#!/usr/bin/env python3
"""Gopatha Brahmana from GRETIL TEI sa_gopathabrAhmaNa.xml
-> public/data/brahmanas/gopatha_brahmana.json, reference bhaga.prapathaka.kandika
(Purvabhaga = 1, Uttarabhaga = 2), one entry per kandika.

Text carries inline sentence markers "(GBr_1,1.1a)"; all sentences of a kandika are joined.
Dropped: the invocation (GBr_0.0.0a), prapathaka/bhaga colophons (...col), bracketed editorial
notes ("[ed.: yāc]", "[ṚV 3.48.1]"), the "_" sandhi-break marks, and kandika numbers "|| 1 ||".
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_gretil_common import (body, compare_old, load_old, make_entry, norm_space,  # noqa: E402
                                   odd_chars, report, validate, write)

REL = 'public/data/brahmanas/gopatha_brahmana.json'
VID = 'gopatha_brahmana'
MARK = re.compile(r'\(GBr_([^)]*)\)')


def clean(t):
    t = re.sub(r'\[[^\]]*\]', ' ', t)
    t = t.replace('_', ' ')
    t = t.replace('<', ' ').replace('>', ' ')      # <...> marks quoted mantras
    t = re.sub(r'(?<=[^\W\d_])[."](?=[^\W\d_])', '', t)   # typos: "viris.yate", "pra"ugaṃ"
    t = t.replace('.', ' ')
    t = re.sub(r'\|\|\s*\d+\s*\|\|', '||', t)
    t = re.sub(r'\s*\|\|\s*$', '', norm_space(t)) + ' ||'
    return norm_space(t)


def main():
    old = load_old(REL)
    text = ''.join(body('sa_gopathabrAhmaNa.xml').itertext())
    parts = MARK.split(text)  # [pre, id, txt, id, txt, ...]
    kand, order, skipped = {}, [], []
    for mid, txt in zip(parts[1::2], parts[2::2]):
        m = re.fullmatch(r'(\d+),(\d+)\.(\d+)([a-z]+)', mid)
        if not m:
            skipped.append(mid)
            continue
        key = tuple(int(x) for x in m.groups()[:3])
        if key not in kand:
            if order and key <= order[-1]:
                raise SystemExit(f'out of order kandika {key} after {order[-1]}')
            kand[key] = []
            order.append(key)
        kand[key].append(txt)
    print('skipped markers:', skipped)
    entries = [make_entry(k, clean(' '.join(kand[k])), VID) for k in order]
    write(REL, entries)
    report(REL, old, entries)
    validate(os.path.join('/Users/iashris/Desktop/rigved', REL))
    odd_chars(entries)
    compare_old(old, entries)
    import collections
    print('kandikas per prapathaka:', dict(collections.Counter((k[0], k[1]) for k in order)))


if __name__ == '__main__':
    main()
