"""Bṛhaddevatā Sanskrit from Pramāṇa (`in.vedanga.misc.anukramani.saunaka.brhaddevata`) split into verses.

Pramāṇa's segments are uneven (single verses, or blocks of 10-35 verses) and its verse-end numbers have OCR
slips ("1 2", "2.10", "72" for 75, missing numbers).  Each adhyāya's half-verse lines are re-cut here: a line
ending in a double daṇḍa (with or without a number) closes a verse.  Numbering follows the printed numbers
when they are the expected next number; otherwise:
  - a 1-line fragment is joined to the following verse;
  - a 4-line chunk whose printed number is expected+1 is two verses whose first end-mark was lost (split 2+2);
  - any other mismatch keeps the running count (printed number taken as an OCR slip).
"""
import collections
import re
import sys
import unicodedata

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import segments  # noqa: E402

HEADING = re.compile(r'^\d+\s*[-ḥ]|^ṛgveda\s|ṛgveda\s*\d|\skī\s|\ske\sdevatā|kī kathā')
PATH = 'in.vedanga.misc.anukramani.saunaka.brhaddevata'
END = re.compile(r'(\.\s*\.\s*[\d\s.]*$|\d\s*\.?\s*\.?\s*$)')
NUM = re.compile(r'(\d[\d\s.]*?)\s*\.?\s*\.?\s*$')


def printed(line):
    m = NUM.search(line)
    if not m:
        return None
    digits = m.group(1).strip().split('.')[-1].replace(' ', '')
    return int(digits) if digits.isdigit() else None


def clean(line):
    line = re.sub(r'\.\s*\.\s*[\d\s.]*$|[\d\s.]*\d\s*\.?\s*\.?\s*$', ' ||', line.strip())
    line = re.sub(r'\s*\.\s*$', ' |', line)
    line = re.sub(r"\d+'?", '', line)        # OCR digits inside words ("agra5yā", "na29ṅkuke")
    line = re.sub(r'\s+', ' ', line)
    return unicodedata.normalize('NFC', line.strip())


def verses():
    lines = collections.defaultdict(list)
    for s in segments(PATH):
        if s.get('kind') != 'verse':
            continue
        a = int(s['loc'].split('.')[0])
        for ln in s['text'].split('\n'):
            ln = re.sub(r'(\.\.\s*\d+\s*\.\.).*$', r'\1', ln.strip())
            if HEADING.search(ln):   # Hindi editorial headings of the source ("9-ṛgveda 8.1-21 ke devatā")
                continue
            if ln and 'bṛhaddevatā' not in ln.replace('bṛhaddevatāyāṃ', 'bṛhaddevatā') and 'prārambhaḥ' not in ln:
                lines[a].append(ln)
    out, report = {}, {}
    for a in sorted(lines):
        chunks, cur = [], []
        for ln in lines[a]:
            cur.append(ln)
            if END.search(ln):
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
        # join 1-line fragments to the next chunk
        merged = []
        for i, c in enumerate(chunks):
            if merged and merged[-1][1]:
                merged[-1] = (merged[-1][0] + c, False)
                continue
            merged.append((c, len(c) == 1 and i + 1 < len(chunks)))
        vs, n, slips = [], 0, []
        pr = [printed(c[-1]) for c, _ in merged]
        for idx, (c, _) in enumerate(merged):
            p = pr[idx]
            if p == n + 2 and len(c) == 4:
                vs.append((n + 1, c[:2]))
                vs.append((n + 2, c[2:]))
                n += 2
                continue
            if p is not None and p != n + 1:
                ahead = [q for q in pr[idx + 1:idx + 3] if q is not None]
                consistent = bool(ahead) and all(q == p + 1 + k for k, q in enumerate(pr[idx + 1:idx + 3]) if q is not None)
                if consistent and p > n + 1:      # source skips number(s): follow the printed numbering
                    slips.append(('gap', n + 1, p - 1))
                    n = p
                    vs.append((n, c))
                    continue
                if consistent and p <= n and vs:  # repeated/variant lines: keep with the previous verse
                    slips.append(('extra', n, p))
                    vs[-1] = (vs[-1][0], vs[-1][1] + c)
                    continue
                slips.append((n + 1, p))
            n += 1
            vs.append((n, c))
        out[a] = [(v, ' '.join(clean(x) for x in c)) for v, c in vs]
        report[a] = slips
    return out, report


if __name__ == '__main__':
    out, rep = verses()
    for a in out:
        print(a, len(out[a]), 'slips', len(rep[a]), rep[a][:15])
