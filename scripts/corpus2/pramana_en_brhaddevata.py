"""New text public/data/other/brhaddevata.json: Bṛhaddevatā, Sanskrit + Macdonell's English (HOS 5-6, 1904),
both from Pramāṇa.  Reference adhyāya.verse.

Sanskrit: see pramana_en_bd_sanskrit.py (verse re-cutting; numbering follows the printed verse numbers, which
are Macdonell's).

English (`...brhaddevata~en-macdonell`): an OCR of Macdonell's volume 2, where each verse's translation
("57. He then himself roaring ...") is followed by his critical apparatus (variant readings with MS sigla,
"Cp. Nirukta ...", lettered footnotes).  Per chapter the text is cut at the verse numbers, searched in order
(a verse number must be followed by a capital/quote/bracket; the markers kept are the longest chain rising in
both position and number, which skips the varga headings "13. Pusan, Visnu ..." and cross-references); a
combined number "14, 15." is one group.  Each piece is then cut where the apparatus begins (first MS-sigla token such as hm'rbk, or a
"Cp."/"The end of the varga"/footnote start), backing up over the Sanskrit lemma that precedes the sigla.
The English goes on the group's first verse; the other verses of a group, and verses whose number was lost in
the OCR (their translation then sits in the preceding piece), get text "" and text_ref = the carrier verse.
"""
import collections
import json
import re
import sys

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import segments, entry, validate, write_json  # noqa: E402
import pramana_en_bd_sanskrit as bds  # noqa: E402

OUT = '/Users/iashris/Desktop/rigved/public/data/other/brhaddevata.json'
VID = 'brhaddevata'
DICT = set(w.strip().lower() for w in open('/usr/share/dict/words'))
MARK = re.compile(r"(?<![\w.,\-–/])(\d{1,3})((?:\s*,\s*\d{1,3})*)\s*\.\s+(?=[A-Z'‘“(\[])")
SIGLA = re.compile("^[\\[(]?(?=[^A-Za-z]*[hmrbfkdBHl])(?=[^aeou]*[hmrbfk1-4'`˚°ˆ±][^aeou]*[hmrbfk1-4'`˚°ˆ±\x22])[hmrbfkdBHli1-4'`˚°ˆ*±\x22\u201d]{2,12}[\\])]?[,.;:]?$")
APP_START = re.compile(r"\s(?:[-–]{1,2}\s*[a-z°]|Cp\.|The end of the varga|No various reading|omitted in|[a-d]\s(?:Cp\.|That is|Lit\.|\*|See|This|The|In|Here|Text))")
ENGLISH_OK = {'a', 'i', 'o', 'is', 'it', 'he', 'or', 'as', 'by', 'in', 'of', 'to', 'be', 'so', 'we', 'me', 'my', 'no'}


def english(tok):
    w = re.sub(r"[^A-Za-z]", '', tok).lower()
    return bool(w) and (w in DICT or w in ENGLISH_OK) and len(w) > 1 or w in ('a', 'i')


def cut_apparatus(t):
    toks = list(re.finditer(r'\S+', t))
    end = len(t)
    for i, m in enumerate(toks):
        tok = m.group(0)
        if SIGLA.match(tok) and not english(tok):
            j = i
            # back up over the Sanskrit lemma (non-English, unaccented words) before the sigla
            while j > 0 and not english(toks[j - 1].group(0)) and not re.search(r'[.)\]]$', toks[j - 1].group(0)):
                j -= 1
            end = toks[j].start() if j < len(toks) else len(t)
            break
    m = APP_START.search(t[:end])
    if m:
        end = m.start()
    s = t[:end]
    s = re.sub(r'\s+[-–]\s*$', '', s)
    s = re.sub(r'(?<=[\w)’\'])\s+[a-d](?=[\s,.;:)])(?!\s[a-z]{2,})', '', s)   # footnote letters (not the article)
    s = re.sub(r'(?<=[\w)’\'])\s+a(?=[,.;:)])', '', s)
    s = re.sub(r'\s+', ' ', s).strip(' -–•`')
    # a lemma left dangling after the last full stop ("... Agni. namnam tu bfkx, namnam ca") is apparatus
    m = list(re.finditer(r"[.?!)’']\s", s + ' '))
    if m:
        tail = s[m[-1].end():].split()
        if tail and sum(not english(w) for w in tail) >= max(1, len(tail) / 2):
            s = s[:m[-1].end()].strip()
    return s


def english_pieces(chapters, counts):
    """chapters: {adhyāya: text}; counts: {adhyāya: number of verses}.  Returns {adhyāya: [(first, group, text)]}.

    Markers are chained over the whole book (Pramāṇa's chapter sections do not always start at verse 1 of the
    adhyāya, so a marker may belong to the neighbouring adhyāya): each candidate is tried as a verse of its own
    section's adhyāya or of the one before/after, and the kept markers are the best chain rising in position and
    in global verse order (step 1; gaps penalised), which skips varga headings and cross-references.
    """
    off, tot = {}, 0
    for a in sorted(counts):
        off[a] = tot
        tot += counts[a] + 3
    text = ''
    flat = []
    for a in sorted(chapters):
        base = len(text)
        t = chapters[a]
        text += t + ' '
        for m in MARK.finditer(t):
            nums = [int(m.group(1))] + [int(x) for x in re.findall(r'\d+', m.group(2))]
            if not all(nums[i + 1] == nums[i] + 1 for i in range(len(nums) - 1)):
                continue
            for b in (a - 1, a, a + 1):
                if b in counts and nums[-1] <= counts[b] + 2:
                    flat.append((base + m.start(), base + m.end(), b, nums, off[b] + nums[0], off[b] + nums[-1]))
    flat.sort()
    best, prev = [0.0] * len(flat), [-1] * len(flat)
    for i, (st, en, b, nums, o0, o1) in enumerate(flat):
        best[i] = 1.0 - 0.3 * min(nums[0] - 1, 10)
        for j in range(i - 1, max(-1, i - 600), -1):
            gap = o0 - flat[j][5]
            if 1 <= gap <= 25 and flat[j][1] <= st:
                sc = best[j] + 1.0 - 0.3 * (gap - 1)
                if sc > best[i] + 1e-9:
                    best[i], prev[i] = sc, j
    i = max(range(len(flat)), key=lambda x: (best[x], flat[x][0]))
    picks = []
    while i >= 0:
        picks.append(flat[i])
        i = prev[i]
    picks.reverse()
    out = collections.defaultdict(list)
    for i, (st, en, b, nums, o0, o1) in enumerate(picks):
        stop = picks[i + 1][0] if i + 1 < len(picks) else len(text)
        out[b].append((nums[0], nums, cut_apparatus(text[en:stop])))
    return out


def main():
    sa, slips = bds.verses()
    chap = collections.defaultdict(list)
    for s in segments('in.vedanga.misc.anukramani.saunaka.brhaddevata~en-macdonell'):
        if s.get('kind') == 'prose' and s.get('text'):
            chap[int(s['loc'].split('.')[0])].append(s['text'].replace('\n', ' '))
    counts = {a: max(v for v, _ in sa[a]) for a in sa}
    allp = english_pieces({a: ' '.join(chap[a]) for a in chap}, counts)
    entries, stats = [], {}
    for a in sorted(sa):
        pieces = allp.get(a, [])
        carrier_of, text_of = {}, {}
        for first, group, txt in pieces:
            text_of[first] = txt
            for v in group:
                carrier_of[v] = first
        cur, n_en = None, 0
        for v, iast in sa[a]:
            ref = f'{a}.{v}'
            e = entry(ref, iast, VID)
            if v in text_of and text_of[v]:
                e['text'] = text_of[v]
                cur = ref
                n_en += 1
            elif v in carrier_of and carrier_of[v] != v:
                e['text_ref'] = f'{a}.{carrier_of[v]}'
            elif cur:
                e['text_ref'] = cur
            entries.append(e)
        stats[a] = (len(sa[a]), n_en, len(pieces))
    validate(entries, 'brhaddevata')
    write_json(entries, OUT)
    for a, (n, ne, npc) in stats.items():
        print(f'adhyaya {a}: {n} verses, {ne} with English, {npc} English pieces; Sanskrit numbering notes {slips[a]}')
    print('total', len(entries), 'with text', sum(1 for e in entries if e['text']),
          'with text_ref', sum(1 for e in entries if e.get('text_ref')),
          'neither', sum(1 for e in entries if not e['text'] and not e.get('text_ref')))


if __name__ == '__main__':
    main()
