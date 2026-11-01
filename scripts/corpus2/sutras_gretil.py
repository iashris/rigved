#!/usr/bin/env python3
"""Convert GRETIL TEI Srauta/Grhya/Dharma/Sulba sutras to public/data/sutras/*.json.

English (where available) is merged from the per-text maps written by
sutras_sbe.py into WORK/english/<id>.json ({reference: text}).  SBE texts with
no GRETIL Sanskrit (Paraskara, Khadira, Gobhila, Hiranyakesin) are written
English-only.

Run:  python3 -I scripts/corpus2/sutras_gretil.py
"""
import html
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
sys.path.insert(0, HERE)
from titus_to_json import iast_to_devanagari  # noqa: E402
import sutras_sandhi  # noqa: E402

SCRATCH = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus'
TEI = os.path.join(SCRATCH, 'g/1_sanskr/tei')
WORK = os.path.join(SCRATCH, 'work/sutras')
OUT = os.path.join(REPO, 'public/data/sutras')


def body(fname):
    t = open(os.path.join(TEI, fname + '.xml'), encoding='utf-8').read()
    return t[t.index('<body'):t.index('</body>')]


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def rm_parens(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\([^()]*\)', ' ', s)
    return s


def rm_brackets(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\[[^\[\]]*\]', ' ', s)
    return s


def scrub(s):
    """Drop leftover editorial tokens: anything with Latin capitals (sigla,
    text abbreviations), 'cf.', pure reference numbers; stray brackets."""
    s = re.sub(r'\(ed\.:?', ' ', s)
    s = re.sub(r'(?<!\S)cf\.', ' ', s)
    s = re.sub(r'[\[\]()+]', ' ', s)
    out = []
    for tok in s.split():
        if re.search(r'[A-Z]', tok):
            continue
        if re.fullmatch(r'[\d.,;:\-]+', tok):
            continue
        tok = re.sub(r'(?<![^\W\d_])3(?=[^\W\d_])', '\x00', tok)   # keep pluta 3 inside words
        tok = re.sub(r'\d', '', tok).replace('\x00', '3')
        tok = tok.strip(',;:-') or tok
        if tok:
            out.append(tok)
    return ' '.join(out)


def finish(s):
    """Common final normalisation."""
    s = scrub(s)
    s = s.replace('//', ' || ').replace('/', ' | ')
    s = re.sub(r'\|\s*\|', '||', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s+([|])', r' \1', s)
    s = re.sub(r'^(\|+\s*)+', '', s).strip()
    s = re.sub(r'(\|\|?)(\s*\|+)+$', r'\1', s)
    s = re.sub(r'\|\| \|\|', '||', s)
    return unicodedata.normalize('NFC', s)


def clean_dot(s):
    """Texts with '.' between words (Asv, Sankh): strip apparatus, dots->spaces.
    Returns '' for sutras the e-text marks as omitted ('OmIṭṭEḍ' = OMITTED)."""
    s = s.strip()
    s = re.sub(r'\.?OmIṭṭEḍ\.?', ' ', s).strip()
    if s.startswith('(') and s.endswith(')'):         # whole sutra wrapped in (...)?
        depth = 0
        for i, ch in enumerate(s):
            depth += (ch == '(') - (ch == ')')
            if depth == 0:
                break
        if i == len(s) - 1:
            s = s[1:-1]
    prev = None
    while prev != s:                                  # trailing topic annotations
        prev = s
        s = re.sub(r'\s*\([^()]*\)\s*$', '', s)
        s = re.sub(r'(/)\s*[^/()]*\)\s*$', r'\1', s)     # '.../ṣoma: x)' (missing '(')
        s = re.sub(r'(/)\s*[a-zṣ]+:[^/]*$', r'\1', s)     # '.../ soma: x' (no parens)
    if s.startswith('('):                             # a whole sutra in parentheses
        s = s[1:]
        if s.rstrip(' /').endswith(')'):
            s = s.rstrip(' /')[:-1] + ' /'
    s = rm_parens(s)
    s = re.sub(r'\(.*$', ' ', s)                     # unbalanced '(' opens a trailing note
    s = rm_brackets(s)
    s = re.sub(r'/\d+/', '/', s)
    s = re.sub(r'/\d+:', '/', s)
    s = s.replace('/:', '/')
    # numbers not glued to a letter on the left (keep pluta 3 as in o3m)
    s = re.sub(r'(?<![^\W\d_])\d+(?:\.\d+)*\.?', ' ', s)
    s = re.sub(r'[<>:?;)]', ' ', s)
    s = s.replace('.', ' ')
    s = re.sub(r'\S*[A-Z]\S*', ' ', s)              # editorial tokens (e.g. ṛV)
    s = finish(s)
    return '' if not s.strip(' |') else s


class Acc:
    """Ordered accumulator; consecutive repeats of a ref are merged."""

    def __init__(self, vid):
        self.vid = vid
        self.order = []
        self.d = {}
        self.dropped = []

    def add(self, ref, txt):
        txt = txt.replace('#', '')
        ref = tuple(int(x) for x in ref)
        if not txt.strip(' |'):
            self.dropped.append(ref)
            return
        if ref in self.d:
            if self.order[-1] != ref:
                raise SystemExit(f'{self.vid}: non-consecutive duplicate {ref}')
            self.d[ref] = (self.d[ref] + ' ' + txt).strip()
        else:
            self.order.append(ref)
            self.d[ref] = txt.strip()

    def items(self):
        return [(r, self.d[r]) for r in self.order]


# ---------------------------------------------------------------- parsers

def repair(rows, vid):
    """rows: [adhyaya, khanda, sutra, label, text].  Source id typos are
    repaired by sequence: an id that goes backwards, or jumps when the next id
    continues the sequence (or repeats when the next id continues it), is
    renumbered prev+1; a khanda that opens with the continuation of the
    previous khanda's numbering is folded back.  Remaining repeats of the same
    number (sutra split into parts) are merged."""
    fixes = []
    for i, r in enumerate(rows):
        if i == 0:
            continue
        p = rows[i - 1]
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        if (r[0], r[1]) == (p[0], p[1]):
            nxt_cont = nxt and (nxt[0], nxt[1]) == (r[0], r[1]) and nxt[2] == p[2] + 2
            if r[2] == p[2]:
                if nxt_cont and not r[3][-1:].isalpha():
                    fixes.append((tuple(r[:3]), p[2] + 1)); r[2] = p[2] + 1
            elif r[2] < p[2]:
                fixes.append((tuple(r[:3]), p[2] + 1)); r[2] = p[2] + 1
            elif r[2] > p[2] + 1 and nxt_cont:
                fixes.append((tuple(r[:3]), p[2] + 1)); r[2] = p[2] + 1
        elif r[0] == p[0] and r[1] == p[1] + 1 and r[2] == p[2] + 1 and r[2] > 1:
            fixes.append((tuple(r[:3]), 'prev khanda')); r[1] = p[1]
    print(f'  {vid}: id repairs {fixes}')
    return rows


def p_asv(fname, prefix, vid):
    acc = Acc(vid)
    rows = [[int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(3) + m.group(4), m.group(5)]
            for m in re.finditer(r'<p xml:id="%s_(\d+)\.(\d+)-(\d+)([a-z]?)">(.*?)</p>' % prefix,
                                 body(fname), re.S)]
    for r in repair(rows, vid):
        acc.add(r[:3], clean_dot(strip_tags(r[4])))
    return acc


def p_sankh(fname, prefix, vid):
    """Sutra 0 lines (ŚGS x.y.0) are editorial section titles and are dropped."""
    acc = Acc(vid)
    rows = []
    for line in strip_tags(body(fname)).split('\n'):
        m = re.match(r'\s*%s_(\d+)\.(\d+)\.(\d+)((?:-\d+)?[a-z]*):\s*(.*)' % prefix, line)
        if m:
            if m.group(3) == '0':
                continue
            rows.append([int(m.group(1)), int(m.group(2)), int(m.group(3)),
                         m.group(3) + ('p' if m.group(4) else ''), m.group(5).replace('x[', 'ṣṭ')])
        elif line.strip() and not line.strip()[0] in '(%':   # notes / variants
            raise SystemExit(f'{vid}: unparsed line {line[:80]}')
    for r in repair(rows, vid):
        acc.add(r[:3], clean_dot(r[4]))
    return acc


def p_vaitana(fname, vid):
    acc = Acc(vid)
    t = strip_tags(body(fname))
    t = '\n'.join(l for l in t.split('\n') if not l.strip().startswith('%'))
    # '<4.3.4-5> (27.4-5)': a range that cannot be split is kept under its first number
    parts = re.split(r'<(\d+)\.(\d+)\.(\d+)(?:-\d+)?>\s*\((\d+)\.(\d+)(?:-\d+)?\)', t)
    rows = [[0, int(parts[i + 3]), int(parts[i + 4]), '', parts[i + 5]]
            for i in range(1, len(parts), 6)]
    for _, k, s, _, txt in repair(rows, vid):
        txt = rm_brackets(txt).replace('<', ' ').replace('>', ' ').replace('_', ' ')
        txt = re.sub(r'\.\s', ' ', txt)
        acc.add((k, s), finish(txt))
    return acc


def p_sulba(fname, vid):
    acc = Acc(vid)
    for d in re.findall(r'<div>(.*?)</div>', body(fname), re.S):
        if 'ĀpŚus_' not in d:
            continue
        txt = strip_tags(d)
        m = re.search(r'^(.*?)\|\|\s*ĀpŚus_(\d+)\.(\d+)[a-z]?\s*\|\|\s*$', txt.strip(), re.S)
        if not m:
            raise SystemExit(f'sulba: bad div {txt[:100]}')
        acc.add(m.group(2, 3), finish(rm_parens(m.group(1)).replace('|', '/') + ' //'))
    return acc


def p_marker(text, pat, vid, nref, drop=None):
    """Generic: text segments terminated by a marker regex with nref groups."""
    acc = Acc(vid)
    pos = 0
    for m in re.finditer(pat, text):
        seg = text[pos:m.start()]
        pos = m.end()
        if drop:
            seg = drop(seg)
        acc.add(m.groups()[:nref], seg)
    tail = text[pos:].strip()
    return acc, tail


def p_jaim(fname, vid):
    t = strip_tags(body(fname))
    t = re.sub(r'jaiminīyagṛhyasūtram', '', t)
    acc, tail = p_marker(t, r'//\s*JaimGS_(\d+)\.(\d+)\s*//', vid, 2,
                         drop=lambda s: re.sub(r'JaimGS \d+\.\d+:', '', s))
    out = Acc(vid)
    for r, s in acc.items():
        out.add(r, finish(s + ' //'))
    return out, tail


def p_kauth(fname, vid):
    t = strip_tags(body(fname))
    t = t.replace('kauthumagṛhyasūtram', '')
    acc, tail = p_marker(t, r'//\s*KauthGS_(\d+)\s*//', vid, 1,
                         drop=lambda s: re.sub(r'KauthGS \d+:', '', s))
    out = Acc(vid)
    for r, s in acc.items():
        out.add(r, finish(s + ' //'))
    return out, tail


HEAD_RE = re.compile(r'^\s*(?:\S+ḥ (?:khaṇḍaḥ|puruṣaḥ)|śrīmaitrāyaṇīyamānavagṛhyasūtrabhāṣyam|'
                     r'atha mānavagṛhyasūtraprārambhaḥ)\s*/?\s*$', re.M)


def p_manava(fname, vid):
    t = strip_tags(body(fname))
    t = HEAD_RE.sub('', t)
    t = re.sub(r"iti [^/|\n]*?khaṇḍaḥ\s*/*\s*\d*\s*/*", ' ', t)     # khanda colophons
    rows, pos = [], 0
    for m in re.finditer(r'//\s*ManGS_(\d+),\s*(\d+)\.\s*(\d+)\s*//', t):
        rows.append([int(m.group(1)), int(m.group(2)), int(m.group(3)), '', t[pos:m.start()]])
        pos = m.end()
    tail = t[pos:].strip()
    out = Acc(vid)
    for r in repair(rows, vid):
        r, s = r[:3], r[4]
        s = re.sub(r'^\s*oṃ\s+', 'oṃ ', s)
        out.add(r, finish(s.replace('---', ' ').replace('--', ' ') + ' //'))
    return out, tail


def p_varaha(fname, vid):
    t = strip_tags(body(fname))
    t = re.sub(r'Vārāhagṛhyasūtra, \d+', '', t)
    acc, tail = p_marker(t, r'//\s*VGrs_(\d+)\.(\d+)', vid, 2)
    out = Acc(vid)
    for r, s in acc.items():
        out.add(r, finish(s + ' //'))
    return out, tail


def p_kausika(fname, vid):
    acc = Acc(vid)
    for m in re.finditer(r'<p>\(KauśS_(\d+),(\d+)(?:\[(\d+)\])?\.(\d+)\)\s*(.*?)</p>', body(fname), re.S):
        a, k, kk, s, txt = m.groups()
        kand = kk if kk else k
        if not kk and a != '1':
            raise SystemExit(f'kausika: no continuous kandika for {m.group(0)[:40]}')
        txt = strip_tags(txt)
        txt = rm_brackets(txt)
        txt = rm_parens(txt)
        txt = txt.replace('<', ' ').replace('>', ' ').replace('_', ' ')
        acc.add((kand, s), finish(txt))
    return acc


def p_apgs(fname, vid):
    acc = Acc(vid)
    for m in re.finditer(r'rend="bold">([^<]*?)//\s*ĀpGs_(\d+)\.(\d+)\s*/', body(fname)):
        acc.add(m.group(2, 3), finish(rm_parens(html.unescape(m.group(1))) + ' //'))
    return acc


def p_gautama(fname, vid):
    """Stenzler (St) numbering, which Bühler's SBE 2 translation follows.  St
    parts (2.8a, 2.8b) are merged; the six AA-only paragraphs without an St
    number are appended to the preceding sutra.  A few St numbers occur out of
    text order (e.g. 17.13 before 17.12); entries are emitted in St order."""
    acc = Acc(vid)
    rows = []
    for m in re.finditer(r'<p xml:id="Gaut(St|AA)_(\d+)\.(\d+)[^"]*"[^>]*>(.*?)</p>', body(fname), re.S):
        txt = rm_parens(strip_tags(m.group(4))).replace('|', '/')
        if m.group(1) == 'AA':
            rows[-1][1] += ' ' + txt
        elif rows and rows[-1][0] == (int(m.group(2)), int(m.group(3))):
            rows[-1][1] += ' ' + txt
        else:
            rows.append([(int(m.group(2)), int(m.group(3))), txt])
    seen = set()
    for r, t in sorted(rows, key=lambda x: x[0]):
        if r in seen:
            raise SystemExit(f'gautama: duplicate {r}')
        seen.add(r)
        acc.add(r, finish(t))
    return acc


def split_lines(fname, pat):
    """Return [(refgroups, text)] for line-prefixed files with continuations."""
    rows = []
    text = strip_tags(body(fname))
    text = re.sub(r'(?<=\S)\s*(?=(?:Baudh|Ap\.?)\d+\.\d+\.\d+[\d.\-]*[a-z]*\(?/)', '\n', text)  # inline sutra markers
    for line in text.split('\n'):
        m = re.match(pat, line)
        if m:
            rows.append([m.groups()[:-1], m.groups()[-1]])
        elif line.strip() and rows:
            rows[-1][1] += ' ' + line.strip()
    return rows


def ap_clean(t):
    t = re.sub(r'\[\*[^\]]*\]', ' ', t)
    t = re.sub(r'\[[^\[\]]*\\[^\[\]]*\]', '', t)     # grammatical glosses [upa\\nī, opt.]
    t = t.replace('[', '')
    t = rm_parens(t)
    t = re.sub(r'#\d*', '', t)
    t = re.sub(r'[*?!"]', '', t)
    t = re.sub(r'\d+(?:\.\d+)*\.?', ' ', t)          # stray reference numbers
    return t


def p_apdh(fname, vid):
    acc = Acc(vid)
    rows = split_lines(fname, r'\s*Ap\.?(\d+)\.(\d+)\.(\d+)\.(\d+)(?:-(\d+))?[a-z]*/\s*(.*)')
    problems = []
    for g, t in rows:
        if 'samāptaṃ' in t and 'āpastambīya' in t:
            t = t[:t.index('//samāptaṃ')] if '//samāptaṃ' in t else t
        t = ap_clean(t)
        p, pa, k, s, e = g
        s = int(s)
        e = int(e) if e else s
        refs = [(p, pa, k, n) for n in range(s, e + 1)]
        if len(refs) == 1:
            parts = [t]
        else:
            parts = None
            for sp in (r'\s*[/,]\s*', r'\s*/\s*', r'\s*,\s*'):
                cand = [x for x in re.split(sp, t) if x.strip()]
                if len(cand) == len(refs):
                    parts = cand
                    break
            if parts is None and len(refs) == 2:
                cand = [x for x in re.split(r'\s*/\s*', t, maxsplit=1) if x.strip(' /')]
                if len(cand) == 2:
                    parts = cand
            if parts is None:      # cannot split: keep text under the first number only
                problems.append(('/'.join(g), t[:50]))
                refs, parts = refs[:1], [t]
        for r, x in zip(refs, parts):
            x = x.replace(',', ' ')
            x = sutras_sandhi.apply(x.strip(' /') + ' /', junction_chars='-')
            acc.add(r, finish(x))
    return acc, problems


def p_baudh(fname, vid):
    acc = Acc(vid)
    # Prasnas 1-2: prasna.adhyaya.kandika.sutra; Prasnas 3-4: prasna.adhyaya.sutra
    rows = split_lines(fname, r'\s*(?:Baudh[\d.]*(?=Baudh))?Baudh(\d+(?:\.\d+){2,3})(?:-\d+)?[a-z]*\(?/?\s+(.*)')
    for g, t in rows:
        g = g[0].split('.')
        t = re.sub(r'\(cf\.[^)]*\)', ' ', t)
        t = rm_brackets(t)
        t = t.replace('Z', 'ś')
        t = t.replace('^(', '^').replace('(', ' ').replace(')', ' ')
        t = t.replace('-', '')
        t = re.sub(r'[=+:;!]', ' ', t)
        t = re.sub(r'\d+', ' ', t)
        t = sutras_sandhi.apply(t, junction_chars='^')
        acc.add(g, finish(t))
    return acc


def p_vas(fname, vid):
    acc = Acc(vid)
    raw = strip_tags(body(fname))
    raw = re.sub(r'\[\(\d+\.\d+\).*?\]', ' ', raw, flags=re.S)  # bracketed extra passages
    pos_rows = []
    for line in raw.split('\n'):
        m = re.match(r'\s*Va\.(\d+)\.(\d+)[a-z]?\s+(.*)', line)
        if m:
            pos_rows.append([m.group(1, 2), m.group(3)])
        elif line.strip() and pos_rows:
            pos_rows[-1][1] += ' ' + line.strip()
    for g, t in pos_rows:
        t = re.sub(r'\{[^}]*\}', ' ', t)
        t = rm_brackets(t)
        t = rm_parens(t)
        t = t.replace('-', '')
        t = re.sub(r'[;:?&]', ' ', t).replace('End of the Text', ' ')
        t = sutras_sandhi.apply(t, junction_chars='^')
        acc.add(g, finish(t))
    return acc


# ---------------------------------------------------------------- output

def deva(s):
    d = iast_to_devanagari(s)
    return (d.replace('||', '॥').replace('|', '।').replace("'", 'ऽ')
             .replace('3', '३'))


def align_filter(vid, items, english):
    """Keep English for a reference only where the numbering demonstrably
    matches: within each lowest-level group (khanda/chapter) the Sanskrit and
    English sutras are aligned by a length-based dynamic programme
    (Gale-Church style; 1-1, 1-0, 0-1, 2-1, 1-2 beads), and English is kept for
    reference r only if the DP pairs Sanskrit r with English r one-to-one.
    This drops the stretches where the SBE edition numbers differently."""
    import math
    from collections import defaultdict
    if not english:
        return {}, {}
    skt_groups, en_groups = defaultdict(list), defaultdict(list)
    for ref, skt in items:
        skt_groups[ref[:-1]].append((ref[-1], len(skt)))
    for r, t in english.items():
        k = tuple(int(x) for x in r.split('.'))
        en_groups[k[:-1]].append((k[-1], len(t)))
    tot_s = sum(l for g in skt_groups.values() for _, l in g)
    tot_e = sum(len(t) for t in english.values())
    c = tot_e / max(tot_s, 1)

    def cost(ls, le):
        d = math.log((le + 20) / (ls * c + 20))
        return d * d / 0.25

    keep, stats = {}, {'groups': 0, 'shifted_groups': 0}
    for g, S in skt_groups.items():
        E = sorted(en_groups.get(g, []))
        if not E:
            continue
        stats['groups'] += 1
        n, m = len(S), len(E)
        INF = float('inf')
        D = [[INF] * (m + 1) for _ in range(n + 1)]
        B = [[None] * (m + 1) for _ in range(n + 1)]
        D[0][0] = 0
        moves = [(1, 1, 0.0), (1, 0, 3.0), (0, 1, 3.0), (2, 1, 2.0), (1, 2, 2.0)]
        for i in range(n + 1):
            for j in range(m + 1):
                if D[i][j] == INF:
                    continue
                for di, dj, pen in moves:
                    ii, jj = i + di, j + dj
                    if ii > n or jj > m:
                        continue
                    ls = sum(l for _, l in S[i:ii])
                    le = sum(l for _, l in E[j:jj])
                    cc = D[i][j] + pen + (cost(ls, le) if di and dj else 0)
                    if cc < D[ii][jj]:
                        D[ii][jj] = cc
                        B[ii][jj] = (i, j)
        i, j = n, m
        shifted = False
        while i or j:
            pi, pj = B[i][j]
            if i - pi == 1 and j - pj == 1 and S[pi][0] == E[pj][0]:
                keep['.'.join(map(str, g + (S[pi][0],)))] = True
            else:
                shifted = True
            i, j = pi, pj
        stats['shifted_groups'] += shifted
    out = {r: t for r, t in english.items() if r in keep}
    stats['kept'] = len(out)
    stats['offered'] = len(english)
    return out, stats


def entries(vid, items, english, levels_note=None):
    out = []
    for ref, skt in items:
        r = '.'.join(str(x) for x in ref)
        e = {'reference': r, 'sanskrit_iast': skt,
             'meaning': deva(skt) if skt else '',
             'text': english.get(r, ''), 'mandala': ref[0]}
        if len(ref) > 1:
            e['hymn'] = ref[1]
        if len(ref) > 2:
            e['verse'] = ref[2]
        e['vedaId'] = vid
        out.append(e)
    return out


def load_en(vid):
    p = os.path.join(WORK, 'english', vid + '.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    return {}


def write(vid, ents):
    refs = [e['reference'] for e in ents]
    if len(set(refs)) != len(refs):
        raise SystemExit(f'{vid}: duplicate references')
    with open(os.path.join(OUT, vid + '.json'), 'w', encoding='utf-8') as f:
        json.dump(ents, f, ensure_ascii=False, indent=1)


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = {
        'asvalayana_srautasutra': lambda v: p_asv('sa_AzvalAyanazrautasUtra', 'AsvSS', v),
        'sankhayana_srautasutra': lambda v: p_sankh('sa_zAGkhAyanazrautasUtra', 'ŚŚS', v),
        'vaitana_sutra': lambda v: p_vaitana('sa_vaitAnazrautasUtra-vaitAnasUtra', v),
        'apastamba_sulbasutra': lambda v: p_sulba('sa_ApastambazulbasUtra', v),
        'asvalayana_grhyasutra': lambda v: p_asv('sa_AzvalAyanagRhyasUtra', 'AsvGS', v),
        'sankhayana_grhyasutra': lambda v: p_sankh('sa_zAGkhAyanagRhyasUtra', 'ŚGS', v),
        'jaiminiya_grhyasutra': lambda v: p_jaim('sa_jaiminIyagRhyasUtra', v),
        'kauthuma_grhyasutra': lambda v: p_kauth('sa_kauthumagRhyasUtra', v),
        'manava_grhyasutra': lambda v: p_manava('sa_mAnavagRhyasUtra-maitrAyaNIyamAnavagRhyasUtra', v),
        'varaha_grhyasutra': lambda v: p_varaha('sa_vArAhagRhyasUtra', v),
        'kausika_sutra': lambda v: p_kausika('sa_kauzikasUtra', v),
        'apastamba_grhyasutra': lambda v: p_apgs('sa_ApastambagRhyasUtra-comm', v),
        'apastamba_dharmasutra': lambda v: p_apdh('sa_ApastambadharmasUtra', v),
        'gautama_dharmasutra': lambda v: p_gautama('sa_gautama-dharmasUtra', v),
        'baudhayana_dharmasutra': lambda v: p_baudh('sa_baudhAyanadharmasUtra', v),
        'vasistha_dharmasutra': lambda v: p_vas('sa_vAsiSThadharmasUtra', v),
    }
    only = sys.argv[1:]
    for vid, fn in jobs.items():
        if only and vid not in only:
            continue
        res = fn(vid)
        extra = ''
        if isinstance(res, tuple):
            res, extra = res
        items = res.items()
        if res.dropped:
            print(f'  {vid}: dropped empty/omitted {res.dropped}')
        en, st = align_filter(vid, items, load_en(vid))
        if st:
            print(f'  {vid}: English alignment {st}')
        ents = entries(vid, items, en)
        write(vid, ents)
        print(f'{vid}: {len(ents)} entries; extra={str(extra)[:120]!r}')
    # English-only SBE texts
    for vid in ['paraskara_grhyasutra', 'khadira_grhyasutra', 'gobhila_grhyasutra',
                'hiranyakesin_grhyasutra']:
        if only and vid not in only:
            continue
        en = load_en(vid)
        if not en:
            print(f'{vid}: no English map, skipped')
            continue
        order = json.load(open(os.path.join(WORK, 'english', vid + '.order.json')))
        items = [(tuple(int(x) for x in r.split('.')), '') for r in order]
        ents = entries(vid, items, en)
        write(vid, ents)
        print(f'{vid}: {len(ents)} entries (English only)')


if __name__ == '__main__':
    main()
