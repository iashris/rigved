#!/usr/bin/env python3
"""Block concordance between a Sanskrit critical-edition text and an English translation with vulgate numbering.

Usage:  python3 -I scripts/corpus2/concordance_build.py mahabharata mahabharata_ganguli
        python3 -I scripts/corpus2/concordance_build.py harivamsa harivamsa_dutt
        python3 -I scripts/corpus2/concordance_build.py ramayana ramayana_dutt

Deterministic, no LLM:
 1. English proper names (capitalised words that are rarely seen lower-case) are folded to a phonetic key
    (diacritics stripped, aspirates/sibilants collapsed, ri/r, w/v, final -a dropped).
 2. Every Sanskrit word is folded the same way and mapped to the longest English name key that is a prefix of it
    (this absorbs inflection and the first member of compounds).
 3. Blocks (CE adhyaya) and sections are TF-IDF vectors over name keys; similarity = cosine.
 4. A monotone dynamic programme per parvan gives each Sanskrit block a contiguous run of 1-3 sections,
    allowing shared sections (many-to-one), skipped sections (vulgate extras) and unmatched blocks.
"""
import json, math, os, re, sys, unicodedata, collections

ROOT = '/Users/iashris/Desktop/rigved'
DATA = f'{ROOT}/public/data/epics'
OUTDIR = f'{ROOT}/public/library/concordance'

MAXL = 3            # sections per block
SKIP_PEN = 0.03     # per skipped translation section
SHARE_PEN = 0.10    # block starts on the previous block's last section
EXTRA_PEN = 0.06    # per extra section in a block's run
UNMATCH_PEN = 0.10  # block left unmatched (on top of losing its similarity)
ATTACH_MIN = 0.2     # attach an unclaimed neighbouring section at this cosine...
ATTACH_REL = 0.6    # ...and at this fraction of the block's best section
FILL_MIN = 0.15     # cosine needed to place a DP-unmatched block between its neighbours
EDGE_W = 0.12       # weight of opening/closing name overlap
EDGE_SLOKAS = 3
EDGE_CHARS = 700
LEN_W = 0.25        # weight of the length-compatibility term
LEN_SD = 0.3        # sd of log(English chars per sloka) when the English is shorter than the norm
LEN_SD_HI = 0.6     # ... and when longer (shared sections, vulgate expansions)


# ---------------------------------------------------------------- folding
def strip_diac(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def fold_common(s):
    s = s.replace('b', 'v')                 # Ganguli/Dutt often write V for B
    s = s.replace('chh', 'c').replace('ch', 'c').replace('sh', 's').replace('w', 'v')
    s = re.sub(r'([kgcjtdpb])h', r'\1', s)
    s = s.replace('ee', 'i').replace('oo', 'u')
    s = re.sub(r'(.)\1', r'\1', s)          # geminates
    return s

def fold_sa(w):
    """IAST word -> key space."""
    w = w.lower()
    w = w.replace('ṛ', 'ri').replace('ṝ', 'ri').replace('ḷ', 'li')
    w = w.replace('ṃ', 'n').replace('ṁ', 'n').replace('ṅ', 'n').replace('ñ', 'n').replace('ḥ', '')
    w = w.replace('ch', 'c')                # IAST aspirated c
    w = strip_diac(w)
    w = re.sub(r'[^a-z]', '', w)
    return fold_common(w)

def fold_en(w):
    w = strip_diac(w.lower())
    w = re.sub(r"['’]s$", '', w)
    w = re.sub(r'[^a-z]', '', w)
    w = fold_common(w)
    if len(w) > 4 and w.endswith('as'):     # English plural of an -a stem
        w = w[:-1]
    if len(w) > 3 and w.endswith('a'):
        w = w[:-1]
    return w


# ---------------------------------------------------------------- loading
def load_blocks(src):
    d = json.load(open(f'{DATA}/{src}.json'))
    blocks = collections.OrderedDict()
    for e in d:
        parts = e['reference'].split('.')
        key = '.'.join(parts[:-1])
        blocks.setdefault(key, []).append(e['sanskrit_iast'])
    level = len(next(iter(blocks)).split('.'))
    return blocks, level

def load_sections(tr):
    d = json.load(open(f'{DATA}/{tr}.json'))
    secs = collections.OrderedDict()
    for e in d:
        title = e.get('title', '') or ''
        secs[e['reference']] = (title, e['text'])
    return secs

def group_of(ref, src):
    # alignment groups: parvan/kanda for the Mahabharata and Ramayana, the whole text for the Harivamsa
    return ref.split('.')[0] if src in ('mahabharata', 'ramayana') else 'all'


# ---------------------------------------------------------------- names
CAPWORD = re.compile(r"[A-Za-zĀ-ſḀ-ỿ’'\-]+")

def english_names(secs, use_titles):
    cap, low = collections.Counter(), collections.Counter()
    for title, text in secs.values():
        body = text + ('\n' + title if use_titles else '')
        for m in CAPWORD.finditer(body):
            w = m.group(0).strip("-'’")
            if not w:
                continue
            for part in [w.replace('-', '')]:
                if part[:1].isupper():
                    cap[part.lower()] += 1
                else:
                    low[part.lower()] += 1
    names = {}
    for w, c in cap.items():
        if c >= 2 and low[w] <= 0.15 * c:
            k = fold_en(w)
            if len(k) >= 3:
                names[w] = k
    return names

class KeyMatcher:
    def __init__(self, keys):
        self.keys = set(keys)
        self.maxlen = max(len(k) for k in keys)
        self.cache = {}

    def match(self, tok):
        if tok in self.cache:
            return self.cache[tok]
        best = None
        for start in (0, 1, 2):          # initial vowel sandhi (ca+arjunah -> carjunah)
            t = tok[start:]
            minlen = 3 if start == 0 else 5
            for L in range(min(len(t), self.maxlen), minlen - 1, -1):
                if t[:L] in self.keys and len(t) - L <= (4 if L == 3 else 6 if L == 4 else 99):
                    best = t[:L]
                    break
            if best:
                break
        self.cache[tok] = best
        return best


# ---------------------------------------------------------------- vectors
def tfidf(counts_list, idf):
    vecs = []
    for c in counts_list:
        v = {k: (1 + math.log(n)) * idf[k] for k, n in c.items() if k in idf}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({k: x / norm for k, x in v.items()})
    return vecs

def cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(k, 0.0) for k, x in a.items())

def merge(counts):
    c = collections.Counter()
    for x in counts:
        c.update(x)
    return c


# ---------------------------------------------------------------- DP
def align(S, R):
    """S[i][j]: sim of block i with section j. R[L][i][j]: sim of block i with run ending at j of length L.
    Returns list of (start, end) or None per block."""
    n, m = len(S), len(S[0])
    NEG = -1e18
    F = [[NEG] * m for _ in range(n)]
    back = [[None] * m for _ in range(n)]
    # unmatched option tracked separately: U[i][j] = best with block i unmatched and last used section j
    U = [[NEG] * (m + 1) for _ in range(n)]   # index j+1, j=-1 -> 0 (nothing used yet)
    Uback = [[None] * (m + 1) for _ in range(n)]

    def prev_best(i):
        """best[p] over states of block i-1 ending at section p (p=-1 allowed for i==0)."""
        if i == 0:
            return {-1: (0.0, ('start',))}
        best = {}
        for p in range(m):
            a = F[i - 1][p]
            b = U[i - 1][p + 1]
            if a >= b:
                best[p] = (a, ('F', p))
            else:
                best[p] = (b, ('U', p))
        if U[i - 1][0] > NEG:
            best[-1] = (U[i - 1][0], ('U', -1))
        return best

    for i in range(n):
        pb = prev_best(i)
        # G[k]: best entry into a run starting at k
        G = [NEG] * m
        Gb = [None] * m
        run, runb = NEG, None      # max over p<k of val + SKIP_PEN*p
        ps = sorted(pb)
        pi = 0
        for k in range(m):
            while pi < len(ps) and ps[pi] < k:
                p = ps[pi]
                v = pb[p][0] + SKIP_PEN * p
                if v > run:
                    run, runb = v, pb[p][1]
                pi += 1
            cand = run - SKIP_PEN * (k - 1) if run > NEG else NEG
            G[k], Gb[k] = cand, runb
            if k in pb and pb[k][0] - SHARE_PEN > G[k]:
                G[k], Gb[k] = pb[k][0] - SHARE_PEN, pb[k][1]
        for j in range(m):
            for L in range(1, MAXL + 1):
                k = j - L + 1
                if k < 0 or G[k] <= NEG:
                    continue
                v = G[k] + R[L][i][j] - EXTRA_PEN * (L - 1)
                if v > F[i][j]:
                    F[i][j] = v
                    back[i][j] = (k, Gb[k])
        for p, (v, b) in pb.items():
            vv = v - UNMATCH_PEN
            if vv > U[i][p + 1]:
                U[i][p + 1] = vv
                Uback[i][p + 1] = b
    # termination with trailing skip penalty
    best, state = NEG, None
    for j in range(m):
        v = F[n - 1][j] - SKIP_PEN * (m - 1 - j)
        if v > best:
            best, state = v, ('F', j)
        v = U[n - 1][j + 1] - SKIP_PEN * (m - 1 - j)
        if v > best:
            best, state = v, ('U', j)
    out = [None] * n
    i = n - 1
    while i >= 0:
        kind, j = state
        if kind == 'F':
            k, pstate = back[i][j]
            out[i] = (k, j)
        else:
            pstate = Uback[i][j + 1]
        state = pstate
        i -= 1
    return out


# ---------------------------------------------------------------- main
def build(src, tr, len_norm=None, write=True):
    blocks, level = load_blocks(src)
    secs = load_sections(tr)
    use_titles = tr not in ('mahabharata_ganguli', 'ramayana_dutt')   # their titles are generic
    names = english_names(secs, use_titles)
    keys = set(names.values())
    matcher = KeyMatcher(keys)

    def en_count(body):
        c = collections.Counter()
        for m_ in CAPWORD.finditer(body):
            w = m_.group(0).strip("-'’").replace('-', '')
            k = names.get(w.lower()) if w[:1].isupper() else None
            if k:
                c[k] += 1
        return c

    def sa_count(lines):
        c = collections.Counter()
        for line in lines:
            for tok in re.split(r"[\s|;,.\-'’]+", line):
                f = fold_sa(tok)
                if len(f) >= 3:
                    k = matcher.match(f)
                    if k:
                        c[k] += 1
        return c

    sec_refs = list(secs)
    sec_counts, sec_head, sec_tail = [], [], []
    for ref in sec_refs:
        title, text = secs[ref]
        sec_counts.append(en_count(text + ('\n' + title if use_titles else '')))
        sec_head.append(en_count(text[:EDGE_CHARS]))
        sec_tail.append(en_count(text[-EDGE_CHARS:]))
    blk_refs = list(blocks)
    blk_counts = [sa_count(blocks[r]) for r in blk_refs]
    blk_head = [sa_count(blocks[r][:EDGE_SLOKAS]) for r in blk_refs]
    blk_tail = [sa_count(blocks[r][-EDGE_SLOKAS:]) for r in blk_refs]
    # idf over translation sections; drop keys present in >25% of sections or never seen in Sanskrit
    N = len(sec_counts)
    df = collections.Counter()
    for c in sec_counts:
        df.update(c.keys())
    sa_df = collections.Counter()
    for c in blk_counts:
        sa_df.update(c.keys())
    NB = len(blk_counts)
    idf = {k: min(math.log(N / d), math.log(NB / sa_df[k]))
           for k, d in df.items() if d <= 0.25 * N and 0 < sa_df[k] <= 0.25 * NB}
    blk_vecs = tfidf(blk_counts, idf)
    bh, bt = tfidf(blk_head, idf), tfidf(blk_tail, idf)
    sh, st = tfidf(sec_head, idf), tfidf(sec_tail, idf)
    blk_len = [len(blocks[r]) for r in blk_refs]
    sec_len = [len(secs[r][1]) for r in sec_refs]
    len_norm = len_norm or {}

    result = {}
    groups = collections.OrderedDict()
    for bi, ref in enumerate(blk_refs):
        groups.setdefault(group_of(ref, src), [[], []])[0].append(bi)
    for sj, ref in enumerate(sec_refs):
        g = group_of(ref, src)
        if g in groups:
            groups[g][1].append(sj)
    allconf = []
    for g, (bis, sjs) in groups.items():
        if not sjs:
            for bi in bis:
                result[blk_refs[bi]] = []
            continue
        sv = tfidf([sec_counts[j] for j in sjs], idf)
        S = [[cos(blk_vecs[bi], sv[jj]) for jj in range(len(sjs))] for bi in bis]
        mu = len_norm.get(g, len_norm.get('*'))
        def lenterm(bi, a, b):
            if mu is None:
                return 0.0
            d = math.log(sum(sec_len[sjs[x]] for x in range(a, b + 1)) / blk_len[bi]) - mu
            return LEN_W * (math.exp(-0.5 * (d / (LEN_SD if d < 0 else LEN_SD_HI)) ** 2) - 0.5)
        def edges(bi, a, b):
            return EDGE_W * (cos(bh[bi], sh[sjs[a]]) + cos(bt[bi], st[sjs[b]]))
        R = {1: [[S[ii][jj] + lenterm(bi, jj, jj) + edges(bi, jj, jj) for jj in range(len(sjs))] for ii, bi in enumerate(bis)]}
        for L in range(2, MAXL + 1):
            runs = []
            for jj in range(len(sjs)):
                if jj - L + 1 < 0:
                    runs.append(None)
                else:
                    runs.append(merge(sec_counts[sjs[x]] for x in range(jj - L + 1, jj + 1)))
            rv = [tfidf([r], idf)[0] if r is not None else None for r in runs]
            R[L] = [[cos(blk_vecs[bi], rv[jj]) + lenterm(bi, jj - L + 1, jj) + edges(bi, jj - L + 1, jj) if rv[jj] is not None else -1e9
                     for jj in range(len(sjs))] for bi in bis]
        path = align(S, R)
        # a translation section left unclaimed right next to a block's run is attached to that block
        # when its names fit (the DP skips it when the vulgate splits one CE adhyaya unevenly)
        claimed = set()
        for seg in path:
            if seg:
                claimed.update(range(seg[0], seg[1] + 1))
        for jj in range(len(sjs)):
            if jj in claimed:
                continue
            cands = []
            for ii, seg in enumerate(path):
                if seg and seg[1] - seg[0] + 1 < MAXL and (seg[1] + 1 == jj or seg[0] - 1 == jj):
                    best_in = max(S[ii][x] for x in range(seg[0], seg[1] + 1))
                    if S[ii][jj] >= ATTACH_MIN and S[ii][jj] >= ATTACH_REL * best_in:
                        cands.append((S[ii][jj], ii))
            if cands:
                _, ii = max(cands)
                a, b = path[ii]
                path[ii] = (min(a, jj), max(b, jj))
                claimed.add(jj)
        # a block the DP left unmatched gets the best section between its neighbours' runs, if any fits
        for ii in range(len(path)):
            if path[ii] is not None:
                continue
            lo = next((path[x][1] for x in range(ii - 1, -1, -1) if path[x]), 0)
            hi = next((path[x][0] for x in range(ii + 1, len(path)) if path[x]), len(sjs) - 1)
            if lo <= hi:
                jj = max(range(lo, hi + 1), key=lambda x: S[ii][x])
                if S[ii][jj] >= FILL_MIN:
                    path[ii] = (jj, jj)
        for ii, bi in enumerate(bis):
            seg = path[ii]
            if seg is None:
                result[blk_refs[bi]] = []
                continue
            row = S[ii]
            srt = sorted(row, reverse=True)
            entries = []
            for jj in range(seg[0], seg[1] + 1):
                s = row[jj]
                # confidence: absolute similarity and margin over the best section outside the run
                outside = max([row[x] for x in range(len(row)) if x < seg[0] - 1 or x > seg[1] + 1] or [0.0])
                margin = s - outside
                conf = 1 / (1 + math.exp(-(6 * (s - 0.25) + 8 * margin)))
                entries.append({'ref': sec_refs[sjs[jj]], 'score': round(conf, 2)})
            # neighbour runs: drop weak tails, keep at least the strongest
            top = max(e['score'] for e in entries)
            entries = [e for e in entries if e['score'] >= min(0.2, top) or e['score'] == top]
            result[blk_refs[bi]] = entries
            allconf.append(top)

    # length norm per group from confident one-to-one matches (used by a second pass)
    bi_of = {r: i for i, r in enumerate(blk_refs)}
    sj_of = {r: j for j, r in enumerate(sec_refs)}
    obs = collections.defaultdict(list)
    for r, v in result.items():
        if len(v) == 1 and v[0]['score'] >= 0.6:
            obs[group_of(r, src)].append(math.log(sec_len[sj_of[v[0]['ref']]] / blk_len[bi_of[r]]))
    allobs = sorted(x for o in obs.values() for x in o)
    new_norm = {'*': allobs[len(allobs) // 2]} if allobs else {}
    for g, o in obs.items():
        if len(o) >= 5:
            o.sort()
            new_norm[g] = o[len(o) // 2]
    if not write:
        return new_norm

    hi = sum(1 for v in result.values() if v and max(e['score'] for e in v) >= 0.6)
    un = sum(1 for v in result.values() if not v)
    out = {
        'source': src, 'translation': tr, 'sourceLevel': level,
        'method': 'Deterministic name concordance: English proper names folded to phonetic keys, Sanskrit words '
                  'prefix-matched to them, TF-IDF cosine per block/section, monotone DP alignment (1-3 sections, '
                  'shared/skipped sections allowed); score = logistic of similarity and margin.',
        'map': result,
        'stats': {'blocks': len(result), 'highConfidence': hi, 'lowConfidence': len(result) - hi - un, 'unmatched': un},
    }
    os.makedirs(OUTDIR, exist_ok=True)
    path = f'{OUTDIR}/{src}__{tr}.json'
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{\n')
        head = {k: out[k] for k in ('source', 'translation', 'sourceLevel', 'method')}
        for k, v in head.items():
            f.write(f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n')
        f.write('  "map": {\n')
        items = list(result.items())
        for n_, (k, v) in enumerate(items):
            f.write(f'    {json.dumps(k)}: {json.dumps(v)}' + (',\n' if n_ < len(items) - 1 else '\n'))
        f.write('  },\n')
        f.write(f'  "stats": {json.dumps(out["stats"])}\n}}\n')
    print(path, out['stats'], f'{len(keys)} name keys, {len(idf)} used')
    return out


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    norm = build(sys.argv[1], sys.argv[2], write=False)
    build(sys.argv[1], sys.argv[2], norm)
