#!/usr/bin/env python3
"""Validation pass for the corpus2 'titus' outputs. Usage: python3 -I titus_validate.py [files...]"""
import json, re, sys, unicodedata

REPO = '/Users/iashris/Desktop/rigved/public/data'
DEFAULT = [f'{REPO}/vedas/kathaka_samhita.json',
           f'{REPO}/brahmanas/jaiminiya_upanisad_brahmana.json',
           f'{REPO}/aranyakas/kathaka_aranyaka.json']
KEYS = ['reference', 'sanskrit_iast', 'meaning', 'text', 'mandala', 'hymn', 'verse', 'vedaId']
# pluta "3" after a vowel (agnā3i, abhū3n) is legitimate Vedic notation
GLUED = re.compile(r'[^\W\d_][0-24-9]|[0-24-9][^\W\d_]|(?<![aāiīuūṛeo])3[^\W\d_]|[^\W\d_aāiīuūṛeo]3')


def check(path):
    d = json.load(open(path, encoding='utf-8'))
    probs = []
    refs = [e['reference'] for e in d]
    if len(set(refs)) != len(refs):
        probs.append('duplicate refs')
    keys = [tuple(map(int, r.split('.'))) for r in refs]
    probs += [f'order {a}->{b}' for a, b in zip(refs, refs[1:]) if tuple(map(int, b.split('.'))) <= tuple(map(int, a.split('.')))]
    for e in d:
        s, r = e['sanskrit_iast'], e['reference']
        ks = [k for k in KEYS if k in e]
        if list(e.keys()) != ks:
            probs.append(f'{r}: keys {list(e.keys())}')
        p = r.split('.')
        if e['mandala'] != int(p[0]) or e['hymn'] != int(p[1]) or (len(p) > 2 and e['verse'] != int(p[2])):
            probs.append(f'{r}: level fields mismatch')
        if not s.strip():
            probs.append(f'{r}: empty')
        if s != unicodedata.normalize('NFC', s):
            probs.append(f'{r}: not NFC')
        for bad in '<>[]{}()*\\/_`':
            if bad in s:
                probs.append(f'{r}: markup {bad!r}')
        if GLUED.search(s):
            probs.append(f'{r}: glued digit {GLUED.search(s).group()!r}')
        if not re.search('[ऀ-ॿ]', e['meaning']):
            probs.append(f'{r}: no Devanagari')
        if re.search('[a-zāīūṛṃḥśṣṇṭḍ]', e['meaning']):
            probs.append(f'{r}: Latin left in meaning')
    eng = sum(1 for e in d if e['text'])
    print(f'{path}: {len(d)} entries, {refs[0]}..{refs[-1]}, english={eng}, problems={len(probs)}')
    for x in probs[:15]:
        print('   ', x)
    return not probs


if __name__ == '__main__':
    ok = all([check(p) for p in (sys.argv[1:] or DEFAULT)])
    sys.exit(0 if ok else 1)
