#!/usr/bin/env python3
"""Kausitaki (Sankhayana) Brahmana from GRETIL TEI sa_kauSItakibrAhmaNa.xml
-> public/data/brahmanas/kausitaki_brahmana.json, reference adhyaya.khanda.sentence.

Each <p xml:id="KB_a.k.s"> is one sentence. The TEI sentence numbers contain typos and
restarts (e.g. 6.9.1-17 twice, 26.2.3 x8); affected khandas are renumbered 1..n in text
order (see fix_numbering). Trailing topic labels "(agnyādhāna)", "(soma: ...)" and inline
editorial parentheses "(.hotā.)", "(?)" are dropped; dots between words become spaces.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_gretil_common import (NS, XID, body, compare_old, dots_slashes, fix_numbering,  # noqa: E402
                                   load_old, make_entry, odd_chars, report, strip_parens, validate, write)

REL = 'public/data/brahmanas/kausitaki_brahmana.json'
VID = 'kausitaki_brahmana'


def clean(t):
    t = re.sub(r'/\s*\([^/]*$', '/', t)  # trailing topic label, also when its ')' is missing
    t = strip_parens(t)
    t = t.replace('&', ' ')
    t = re.sub(r'ṇṇṇ', '', t)  # 30.5.23 keyboard junk after a label
    t = t.replace('?', ' ')
    return dots_slashes(t)


def main():
    old = load_old(REL)
    segs = []
    for p in body('sa_kauSItakibrAhmaNa.xml').iter(f'{NS}p'):
        pid = p.get(XID)
        if not pid:
            continue
        a, k, s = map(int, re.fullmatch(r'KB_(\d+)\.(\d+)\.(\d+)', pid).groups())
        t = ''.join(p.itertext())
        if pid == 'KB_28.6.26':
            # sentence 27 got swallowed by an unclosed topic label: "... iti / (soma: etābhir.jayet /27"
            head, tail = t.split('(soma:')
            segs.append([a, k, s, head])
            segs.append([a, k, 27, tail.replace('/27', '/')])
            continue
        segs.append([a, k, s, t])
    entries = []
    for ref, t in fix_numbering(segs, 'KB'):
        c = clean(t)
        if not c.strip(' |'):
            raise SystemExit(f'empty after cleaning: {ref} {t!r}')
        entries.append(make_entry(ref, c, VID))
    write(REL, entries)
    report(REL, old, entries)
    validate(os.path.join('/Users/iashris/Desktop/rigved', REL))
    odd_chars(entries)
    compare_old(old, entries)


if __name__ == '__main__':
    main()
