"""Add Keith's English (HOS 25, 1920) from Pramāṇa to public/data/brahmanas/aitareya_brahmana.json.

Pramāṇa doc `in.veda.brahmana.aitreya~en-keith` is OCR of Keith, located pañcikā.adhyāya-in-pañcikā.pN.
Keith opens each khaṇḍa with "<pañcikā>. <running khaṇḍa no. in the pañcikā> (<adhyāya>. <khaṇḍa>)." in
roman/arabic, e.g. "iii. 12 (xii. 1).".  The running number is the reliable part (the parenthetical has OCR
slips), so (pañcikā P, running N) -> the N-th of our khaṇḍas in adhyāyas 5P-4..5P; the parenthetical is used
only as a cross-check.  Keith's text runs from one marker to the next; Keith's section headings are dropped.
Khaṇḍas whose marker was lost in the OCR get text "" (+ text_ref to the entry that holds the merged English
when the English is demonstrably merged there).
"""
import collections
import re
import sys

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import segments, rom, heading_flags, join_paras  # noqa: E402
from jsonfmt import load, save  # noqa: E402

PATH = '/Users/iashris/Desktop/rigved/public/data/brahmanas/aitareya_brahmana.json'
START = re.compile(r'^\s*\[?\s*([ivxl]+)\s*[.,]\s*(\d+)\s*\.?\s*(?:\(\s*([ivxl]+)\s*[.,]\s*(\d+)\s*\.?\s*\))?\s*\.?\s*')
MID = re.compile(r'\b([ivxl]+)\s*[.,]\s*(\d+)\s*\.?\s*\(\s*([ivxl]+)\s*[.,]\s*(\d+)\s*\.?\s*\)\s*\.?\s*')
# OCR lost these khaṇḍas' markers; the English of 25.8-25.9 is (partly) run together into 25.7's text,
# while 17.6's English is simply missing (page gap between iv. 11 and iv. 13).
MERGED_INTO = {'25.8': '25.7', '25.9': '25.7'}
LOST = {'17.6'}


def main():
    data, fmt = load(PATH)
    refs = [e['reference'] for e in data]
    by_p = collections.defaultdict(list)
    for r in refs:
        by_p[(int(r.split('.')[0]) - 1) // 5 + 1].append(r)

    segs = [s for s in segments('in.veda.brahmana.aitreya~en-keith') if s.get('text')]
    # split into (marker, text) pieces, a marker may sit mid-paragraph
    pieces = []  # (P, N, adh, kh, text, is_marker_start)
    for s in segs:
        t = s['text']
        P = int(s['loc'].split('.')[0])
        cuts = []
        m = START.match(t)
        if m and rom(m.group(1)) == P:
            cuts.append((0, m))
        for mm in MID.finditer(t):
            if mm.start() > 3 and rom(mm.group(1)) == P:
                cuts.append((mm.start(), mm))
        if not cuts:
            pieces.append((None, t, s))
            continue
        if cuts[0][0] > 0:
            pieces.append((None, t[:cuts[0][0]], s))
        for i, (pos, mm) in enumerate(cuts):
            end = cuts[i + 1][0] if i + 1 < len(cuts) else len(t)
            pieces.append(((P, int(mm.group(2)), mm.group(3), mm.group(4)), t[mm.end():end], s))

    eng, cur, xmis = collections.defaultdict(list), None, []
    hf = heading_flags([(s['kind'], t, mk is not None) for mk, t, s in pieces])
    for i, (mk, t, s) in enumerate(pieces):
        if mk:
            P, N, a, k = mk
            cur = by_p[P][N - 1]
            if a and k and f'{rom(a)}.{k}' != cur:
                xmis.append((P, N, f'{a}.{k}', cur))
            eng[cur].append(t)
            continue
        if hf[i]:
            continue
        if cur:
            eng[cur].append(t)

    n_en = 0
    for e in data:
        r = e['reference']
        e.pop('text_ref', None)
        e['text'] = join_paras(eng[r]) if r in eng else ''
        if r in MERGED_INTO:
            assert not e['text']
            e['text_ref'] = MERGED_INTO[r]
        n_en += bool(e['text'])
    missing = [r for r in refs if r not in eng]
    assert set(missing) == set(MERGED_INTO) | LOST, missing
    save(PATH, data, fmt)
    print(f'AB: {len(data)} khandas, {n_en} with English ({100 * n_en / len(data):.1f}%), '
          f'missing {missing}; parenthetical OCR mismatches {len(xmis)}: {xmis}')


if __name__ == '__main__':
    main()
