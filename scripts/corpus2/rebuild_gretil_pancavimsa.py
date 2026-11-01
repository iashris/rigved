#!/usr/bin/env python3
"""Pancavimsa (Tandya Maha) Brahmana from GRETIL TEI sa_paJcaviMzabrAhmaNa.xml
-> public/data/brahmanas/pancavimsa_brahmana.json, reference adhyaya.khanda.sentence.

Text carries inline markers "(PB 1.1.1)". The TEI sentence numbers contain typos
(13.5.90, 14.9.66, a 20.13.8 inside 20.14, ...); affected khandas are renumbered 1..n in
text order (see fix_numbering). Dropped: bracketed editorial notes ("[thus BI; KSS ...]"),
the '' quote marks around cited mantras.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_gretil_common import (body, compare_old, fix_numbering, load_old, make_entry,  # noqa: E402
                                   norm_space, odd_chars, report, validate, write)

REL = 'public/data/brahmanas/pancavimsa_brahmana.json'
VID = 'pancavimsa_brahmana'
MARK = re.compile(r'\(PB (\d+)\.(\d+)\.(\d+)\)')


def clean(t):
    t = re.sub(r'\[[^\]]*\]', ' ', t)
    t = t.replace("''", ' ')
    t = re.sub(r'\(\s*\S*\s*\)', ' ', t)       # "(?)", one-word variant readings "(daprahe)"
    t = t.replace('(', ' ').replace(')', ' ')       # 15.1.8: a bracketed sentence, kept
    t = re.sub(r'[+%:,]', '', t)                    # conjecture marks, typos
    t = re.sub(r'(?<=[^\W\d_])\.(?=[^\W\d_])', '', t)  # "pit.ṛn"
    t = t.replace('.', ' ')
    t = re.sub(r'\s*/\s*', ' | ', t)                # half-verse marks in quoted mantras
    t = t.replace('-', ' ')                         # amredita "kule-kule", "anyo-'nyaḥ", "...- iti"
    return norm_space(t)


def main():
    old = load_old(REL)
    text = ''.join(body('sa_paJcaviMzabrAhmaNa.xml').itertext())
    parts = MARK.split(text)  # [pre, a, k, s, txt, ...]
    assert not parts[0].strip(), parts[0][:200]
    segs = [[int(parts[i]), int(parts[i + 1]), int(parts[i + 2]), parts[i + 3]]
            for i in range(1, len(parts), 4)]
    empty = [f'{a}.{k}.{s}' for a, k, s, t in segs if not clean(t)]
    print('empty TEI sentences skipped:', empty)
    segs = [sg for sg in segs if clean(sg[3])]
    entries = []
    for ref, t in fix_numbering(segs, 'PB'):
        c = clean(t)
        if not c:
            raise SystemExit(f'empty: {ref}')
        entries.append(make_entry(ref, c, VID))
    write(REL, entries)
    report(REL, old, entries)
    validate(os.path.join('/Users/iashris/Desktop/rigved', REL))
    odd_chars(entries)
    compare_old(old, entries)


if __name__ == '__main__':
    main()
