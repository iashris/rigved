#!/usr/bin/env python3
"""M. N. Dutt, A Prose English Translation of Harivamsha (1897), Project Gutenberg #61937
-> public/data/epics/harivamsa_dutt.json. Vulgate numbering, NOT the critical edition.

Dutt numbers chapters continuously through Harivamsa + Vishnu parvan (part 1) and restarts in the
'BHAVISHYA PARVA' (part 2). reference = part.chapter = Dutt's printed numeral, with misprints corrected from
the sequence (LVIII for 63, CCXVIII.. for CXXVIII..); XCI does not exist in Dutt. Part 2 prints XLII twice
(two different chapters), so its last seven chapters are numbered 43-49. Every correction is logged.
The Prelude (before chapter I) has no number, so it is prepended to 1.1.
Footnotes (indented blocks), superscript markers, '(n)' verse numbers and _italic_ underscores are stripped.
"""
import json, os, re, time, unicodedata, urllib.request

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/epics/pg'
OUT = '/Users/iashris/Desktop/rigved/public/data/epics/harivamsa_dutt.json'
N = 61937

path = f'{WORK}/pg{N}.txt'
if not os.path.exists(path) or os.path.getsize(path) < 100000:
    for attempt in range(4):
        try:
            open(path, 'wb').write(urllib.request.urlopen(f'https://www.gutenberg.org/cache/epub/{N}/pg{N}.txt', timeout=60).read())
            break
        except Exception as e:
            print('retry', e); time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit('fetch failed')
raw = open(path, encoding='utf-8').read().replace('\r', '')
raw = raw.split('*** START OF', 1)[1].split('\n', 1)[1].split('*** END OF', 1)[0]
lines = raw.split('\n')

ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
def roman(s):
    s = s.replace('.', '')
    t = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        t += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return t

HEAD = re.compile(r'^CHAPTER[ .]*([IVXLC][IVXLC.]*?)\.?[⁰¹²³⁴⁵⁶⁷⁸⁹]*(?:\s+(.*))?$')
SUP = re.compile(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+')

prelude_start = next(i for i, l in enumerate(lines) if l.strip() == 'THE PRELUDE.')
bhav = next(i for i, l in enumerate(lines) if i > prelude_start and l.startswith('BHAVISHYA PARVA'))
heads = []  # (line, part, printed, title, body_start)
for i, l in enumerate(lines):
    if i < prelude_start:
        continue
    m = HEAD.match(l)
    if m:
        title = [m.group(2) or '']
        j = i + 1
        while j < len(lines) and lines[j].strip() and lines[j].strip().isupper():
            title.append(lines[j].strip()); j += 1
        heads.append([i, 2 if i > bhav else 1, m.group(1), ' '.join(t for t in title if t), j])

def clean(block):
    paras, p = [], []
    for l in block:
        if l.strip():
            p.append(l)
        elif p:
            paras.append(p); p = []
    if p: paras.append(p)
    keep = []
    for p in paras:
        if p[0].startswith('  '):          # indented footnote block
            continue
        if p[0].strip() in ('THE END.',) or p[0].startswith('BHAVISHYA PARVA'):
            continue
        keep.append(' '.join(x.strip() for x in p))
    txt = '\n\n'.join(keep)
    txt = SUP.sub('', txt)
    txt = re.sub(r'\s*\((?:\d+(?:\s*[-–—,]\s*\d+)*)\.?\)', '', txt)  # Dutt's sloka numbers (1), (21-41)
    txt = re.sub(r'\s*\[\d+\]', '', txt)  # stray footnote marker
    txt = re.sub(r'_([^_]+)_', r'\1', txt)
    txt = re.sub(r'[ \t]+', ' ', txt)
    return unicodedata.normalize('NFC', txt.strip())

def tidy_title(t):
    t = SUP.sub('', t).strip().rstrip('.').strip()
    return unicodedata.normalize('NFC', t.title().replace("’S", "’s").replace("'S", "'s"))

out, notes, pos = [], [], {1: 0, 2: 0}
prelude = clean(lines[prelude_start + 1:heads[0][0]])
for k, (i, part, printed, title, bstart) in enumerate(heads):
    prev = pos[part]
    c = roman(printed)
    if c in (prev + 1, prev + 2):      # +2: Dutt skips XCI (ch. XC runs on to sloka 111, nothing lost)
        n = c
    elif c - 100 == prev + 1:          # CCXVIII..CCLXXVII misprinted for CXXVIII..CLXXVII
        n = c - 100
    else:                              # LVIII for 63, CXVVI, CXIVII, CCLXIV for 178, second XLII in part 2
        n = prev + 1
    if n != c:
        notes.append(f'{part}.{n}: printed {printed}')
    if n == prev + 2:
        notes.append(f'{part}.{prev + 1}: no chapter with this number in Dutt')
    pos[part] = n
    end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
    text = clean(lines[bstart:end])
    if part == 1 and n == 1:
        text = 'The Prelude.\n\n' + prelude + '\n\n' + text
    if not text:
        raise SystemExit(f'empty chapter {part}.{n}')
    out.append({'reference': f'{part}.{n}', 'sanskrit_iast': '', 'meaning': '', 'text': text,
                'title': ('Bhavishya Parva: ' if part == 2 else '') + tidy_title(title),
                'mandala': part, 'hymn': n, 'vedaId': 'harivamsa_dutt'})

refs = [e['reference'] for e in out]
assert len(refs) == len(set(refs))
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('entries', len(out), 'part1', pos[1], 'part2', pos[2])
for x in notes: print('note', x)
