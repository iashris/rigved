#!/usr/bin/env python3
"""Mahabharata critical edition (BORI) from GRETIL mbh_01_u.htm..mbh_18_u.htm -> public/data/epics/mahabharata.json.

Line ids: PP,AAA.SSS<pada-letters>[*star|@appendix]. Lowercase = verse half-lines, uppercase = prose
segments, no suffix = speaker line ("X uvāca") belonging to sloka SSS. Star (*) and appendix (@) lines are
excluded. Half-lines are joined with ' | ', sloka closed with ' ||'.
"""
import json, re, sys, unicodedata, collections, html
sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts')
from titus_to_json import iast_to_devanagari

SRC = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/g/1_sanskr/2_epic/mbh'
OUT = '/Users/iashris/Desktop/rigved/public/data/epics/mahabharata.json'
LINE = re.compile(r'^(\d{2}),(\d{3})\.(\d{2,3})([A-Za-z]*)([*@][^\t<]*|\d+_\d+)?(?:(?:\t|<>)(.*?))?(?:<BR>)?\s*$')
# Two GRETIL ids lack their * / @ marker. 03,062.017010_0000 is the speaker line of 3.62.17 (bṛhadaśva uvāca,
# kept); 03,083.082d013_0001 is the last line of appendix @013 (dropped).
FIX = {'03,062.017010_0000': ''}

entries, order, counts = {}, [], collections.Counter()
skipped = collections.Counter()
for p in range(1, 19):
    for raw in open(f'{SRC}/mbh_{p:02d}_u.htm', encoding='utf-8'):
        m = LINE.match(raw.rstrip('\n'))
        if not m:
            if re.match(r'^\d{2},\d{3}', raw):
                raise SystemExit(f'unparsed id line: {raw!r}')
            continue
        pv, ad, sl, pada, star, txt = m.groups()
        idtok = re.split(r'\t|<>', raw, maxsplit=1)[0]
        if idtok in FIX:
            star = None
        if star:
            skipped[star[0]] += 1
            continue
        assert int(pv) == p, raw
        txt = html.unescape(re.sub(r'<[^>]+>', '', txt or '')).strip()
        if not txt:
            raise SystemExit(f'empty main line: {raw!r}')
        txt = re.sub(r'\s*\[\d+(?:_\d+)?\]', '', txt)  # 12.325.4: numbered epithets of Nārāyaṇa
        txt = unicodedata.normalize('NFC', re.sub(r'\s+', ' ', txt))
        key = (int(pv), int(ad), int(sl))
        if key not in entries:
            entries[key] = []
            order.append(key)
        elif order[-1] != key:
            raise SystemExit(f'non-contiguous sloka {key}: {raw!r}')
        entries[key].append((pada, txt))

out = []
for key in order:
    if key[2] == 0:
        continue  # 1.1.0: unnumbered mangala verse (nārāyaṇaṃ namaskṛtya), not cited as a sloka
    parts = entries[key]
    speaker = [t for pd, t in parts if pd == '']
    body = [(pd, t) for pd, t in parts if pd != '']
    s = ''
    for i, (pd, t) in enumerate(body):
        if i:
            s += ' ' if (pd.isupper() and body[i-1][0].isupper()) else ' | '
        s += t
    if body:
        s += ' ||'
    if speaker:
        s = ' '.join(speaker) + (' | ' + s if s else '')
    counts[key[0]] += 1
    ref = '.'.join(map(str, key))
    out.append({'reference': ref, 'sanskrit_iast': s, 'meaning': iast_to_devanagari(s), 'text': '',
                'mandala': key[0], 'hymn': key[1], 'verse': key[2], 'vedaId': 'mahabharata'})

refs = [e['reference'] for e in out]
assert len(refs) == len(set(refs)), 'duplicate refs'
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('entries', len(out), 'skipped star/app lines', dict(skipped))
for p in range(1, 19):
    print(p, counts[p])
