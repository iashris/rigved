#!/usr/bin/env python3
"""Rgveda Khilani (Scheftelowitz numbering, as in GRETIL) from TEI sa_RgvedakhilAni.xml
-> public/data/vedas/rgveda_khilani.json, reference adhyaya.hymn.verse.

Verse units: <lg xml:id="RvKh_a.h.v">, stray <l xml:id="RvKh_a.h.v"> (4.9, 5.17), prose
<p xml:id="RvKh_5.5.n"> (nivids), and bare <l xml:id="RvKh_a.h"> lines (one-verse hymns
2.15, 3.17, 3.20 -> verse 1). The praisa groups 5.7.1-5 (sub-lettered a-m in the edition)
are one entry each.

Edition quirks handled:
- 2.14.9.1 + 2.14.9.2 (a verse printed in two parts) -> one entry 2.14.9.
- 3.10: the ms verses 1-6 are printed first, then Scheftelowitz's 3.10.1-9, 16-20 with the
  note "10 = vs. 5 des Ms., 11-14 = vss. 1-4 des Ms; 15 = vs. 6 des Ms." -> ms 1-4 = 11-14,
  ms 5 = 10, ms 6 = 15; hymn sorted 1..20.
- 3.17: the bare one-verse hymn (#29, ending in a pratika) is 3.17.1; the five verses the TEI
  also numbers 3.17.1-5 (pativrata verses, no pratika) follow as 3.17.2-6.
- 4.7 and 4.10: a second, variant version of the hymn re-uses the numbers 1..n; only the
  first (the edition's text, ending in the pratika //15, //19) is kept.
Excluded: the Anukramani prose, the "samhita-aranya" [3.1]-[3.4] paragraphs, colophons, the
appended Khila-khila (KhKh_*), placeholder lines ("blank.", "...").
Cleaning: dots between words -> spaces, / and // -> dandas, hymn counters (//14) and page refs
"(.p.95.)" dropped, parenthesised variant readings "(.śatodyāmam.)" dropped (a line that is
wholly parenthesised, 3.10.3b, is kept without the parentheses).
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_gretil_common import (XID, body, compare_old, dots_slashes, load_old, make_entry,  # noqa: E402
                                   odd_chars, report, strip_parens, tag, validate, write)

REL = 'public/data/vedas/rgveda_khilani.json'
VID = 'rgveda_khilani'
MS_3_10 = {1: 11, 2: 12, 3: 13, 4: 14, 5: 10, 6: 15}


def clean_line(t):
    t = re.sub(r'RvKh_[\d.]+[a-z]*:', ' ', t)          # inline id leaked into 5.7.2e
    t = re.sub(r'RvKh_.*$', ' ', t)                      # 5.7.5m: trailing note "RvKh_(Kuntāpa.adhyāya)VIII-XXII:"
    t = re.sub(r'/+\s*\d+', '//', t)                     # hymn counters "//14", "/1"
    t = re.sub(r'[{]|-+', ' ', t)                        # 3.22.4 "{" line marks, "---" lacunae
    inner = t.strip().rstrip('/.| ').strip()
    if inner.startswith('(.') and inner.endswith(')') and inner.count('(') == 1:
        t = inner[1:-1]                                  # wholly parenthesised line
    t = strip_parens(t)
    return t


def clean(lines):
    t = dots_slashes(' / '.join(clean_line(x).strip().rstrip('/|. ').strip() for x in lines) + ' //')
    t = re.sub(r'^[|\s]+', '', t)
    return t


def main():
    old = load_old(REL)
    units = []  # [a, h, v, [lines], tei_id]

    odd_ids = []

    def walk(el, in_lg=False):
        for c in el:
            cid = c.get(XID) or ''
            t = tag(c)
            if cid.startswith('RvKh_') and t != 'lg' and not re.fullmatch(r'RvKh_\d+(\.\d+)*', cid):
                if not (t == 'l' and in_lg):
                    odd_ids.append(cid)
                    continue
            if t == 'lg' and cid.startswith('RvKh_'):
                lines = [''.join(l.itertext()) for l in c if tag(l) == 'l' and '-' not in (l.get(XID) or '')]
                nums = [int(x) for x in cid[5:].split('.')]
                units.append([nums, lines, cid])
            elif t == 'l' and not in_lg and cid.startswith('RvKh_') and '-' not in cid:
                nums = [int(x) for x in cid[5:].split('.')]
                if len(nums) == 2 and units and units[-1][2] == cid:
                    units[-1][1].append(''.join(c.itertext()))   # bare hymn id: continue the verse
                else:
                    units.append([nums, [''.join(c.itertext())], cid])
            elif t == 'p' and cid.startswith('RvKh_'):
                units.append([[int(x) for x in cid[5:].split('.')], [''.join(c.itertext())], cid])
            elif t in ('div',):
                walk(c)
    walk(body('sa_RgvedakhilAni.xml'))
    print('skipped non-numeric ids (alternative verses, notes):', odd_ids)

    verses = collections.OrderedDict()
    seen_block = collections.Counter()
    dropped = []
    prev_v = {}
    for nums, lines, cid in units:
        a, h = nums[0], nums[1]
        v = nums[2] if len(nums) > 2 else 1
        # a restart of the verse numbers inside a hymn = a second block
        if (a, h) in prev_v and v <= prev_v[(a, h)] and len(nums) < 4:
            seen_block[(a, h)] += 1
        prev_v[(a, h)] = v
        blk = seen_block[(a, h)]
        if (a, h) in ((4, 7), (4, 10)) and blk:
            dropped.append(cid)
            continue
        if (a, h) == (3, 10) and blk == 0:
            v = MS_3_10[v]
        if (a, h) == (3, 17) and len(nums) == 3:
            v += 1
        key = (a, h, v)
        if len(nums) == 4:                               # 2.14.9.1 / 2.14.9.2
            verses.setdefault(key, []).extend(lines)
            continue
        if key in verses:
            raise SystemExit(f'duplicate verse {key} from {cid}')
        verses[key] = lines
    print('dropped variant-version verses:', dropped)
    keys = sorted(verses)
    entries = [make_entry(k, clean(verses[k]), VID) for k in keys]
    write(REL, entries)
    report(REL, old, entries)
    validate(os.path.join('/Users/iashris/Desktop/rigved', REL))
    odd_chars(entries)
    compare_old(old, entries)
    c = collections.OrderedDict()
    for k in keys:
        c.setdefault(k[0], set()).add(k[1])
    print('hymns per adhyaya:', {a: len(v) for a, v in c.items()},
          'verses per adhyaya:', dict(collections.Counter(k[0] for k in keys)))


if __name__ == '__main__':
    main()
