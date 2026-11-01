#!/usr/bin/env python3
"""Valmiki Ramayana, critical edition (Baroda), from GRETIL TEI sa_rAmAyaNa.xml
-> public/data/epics/ramayana.json, reference kanda.sarga.sloka.

One <lg xml:id="R_k.sss.vvv"> per sloka; its <l> half-lines (ab, cd, ef, gh) are joined with
' | ' and the sloka is closed with ' ||'. The GRETIL file holds only the constituted text: it
has no star passages or appendices to exclude (checked: every lg id is R_k.sss.vvv).
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_gretil_common import (NS, XID, body, compare_old, load_old, make_entry,  # noqa: E402
                                   norm_space, odd_chars, report, validate, write)

REL = 'public/data/epics/ramayana.json'
VID = 'ramayana'
# CE sarga counts per kanda (Bala .. Uttara)
CE_SARGAS = {1: 76, 2: 111, 3: 71, 4: 66, 5: 66, 6: 116, 7: 100}


def main():
    old = load_old(REL)
    entries, sargas, slokas = [], collections.defaultdict(set), collections.Counter()
    for lg in body('sa_rAmAyaNa.xml').iter(f'{NS}lg'):
        m = re.fullmatch(r'R_(\d)\.(\d{3})\.(\d{3})', lg.get(XID) or '')
        if not m:
            raise SystemExit(f'unexpected lg id {lg.get(XID)!r}')
        ref = tuple(int(x) for x in m.groups())
        halves = [norm_space(''.join(l.itertext())) for l in lg.iter(f'{NS}l')]
        if not halves or not all(halves):
            raise SystemExit(f'empty half-line in {ref}')
        entries.append(make_entry(ref, ' | '.join(halves) + ' ||', VID))
        sargas[ref[0]].add(ref[1])
        slokas[ref[0]] += 1
    for k in range(1, 8):
        s = sorted(sargas[k])
        assert s == list(range(1, CE_SARGAS[k] + 1)), (k, len(s))
    print('slokas per kanda:', dict(slokas), 'total', sum(slokas.values()),
          '| sargas:', {k: len(v) for k, v in sargas.items()})
    write(REL, entries)
    report(REL, old, entries)
    validate(os.path.join('/Users/iashris/Desktop/rigved', REL))
    odd_chars(entries)
    compare_old(old, entries)


if __name__ == '__main__':
    main()
