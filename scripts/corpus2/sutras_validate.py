#!/usr/bin/env python3
"""Validate public/data/sutras/*.json (counts, order, markup, Devanagari)."""
import json
import os
import random
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'public', 'data', 'sutras')
ENGLISH_ONLY = {'paraskara_grhyasutra', 'khadira_grhyasutra', 'gobhila_grhyasutra', 'hiranyakesin_grhyasutra'}


def key(r):
    return tuple(int(x) for x in r.split('.'))


def main():
    files = sorted(f for f in os.listdir(OUT) if f.endswith('.json'))
    if sys.argv[1:]:
        files = [f for f in files if f[:-5] in sys.argv[1:]]
    bad_total = 0
    for f in files:
        vid = f[:-5]
        d = json.load(open(os.path.join(OUT, f), encoding='utf-8'))
        refs = [e['reference'] for e in d]
        errs = []
        if len(set(refs)) != len(refs):
            errs.append('duplicate refs')
        ks = [key(r) for r in refs]
        if ks != sorted(ks):
            errs.append('refs out of order')
        if any(not re.fullmatch(r'[1-9]\d*(\.[1-9]\d*)*', r) for r in refs):
            errs.append('bad ref format')
        sus = []
        for e in d:
            s = e['sanskrit_iast']
            if vid not in ENGLISH_ONLY:
                if not s.strip():
                    errs.append(f'empty sanskrit {e["reference"]}')
                if not re.search(r'[ऀ-ॿ]', e['meaning']):
                    errs.append(f'no devanagari {e["reference"]}')
            if re.search(r'[<>\[\]{}()_^#*=]|//|\d(?<!3)|[A-Z]', s) or re.search(r'[a-zāīūṛṃḥ]\d|\d[a-zāīūṛṃḥ]', s.replace('3', '')):
                sus.append(e['reference'])
        en = sum(1 for e in d if e['text'].strip())
        print(f'{vid}: {len(d)} entries, {refs[0]}..{refs[-1]}, English {en}/{len(d)} '
              f'({100.0 * en / len(d):.1f}%), suspicious {len(sus)} {sus[:8]}')
        for x in errs[:5]:
            print('   ERROR', x)
        bad_total += len(errs)
    sys.exit(1 if bad_total else 0)


if __name__ == '__main__':
    main()
