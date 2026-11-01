#!/usr/bin/env python3
"""K. M. Ganguli's Mahabharata (Vulgate/Calcutta numbering) -> public/data/epics/mahabharata_ganguli.json.

sacred-texts.com is behind a Cloudflare challenge, so the source is the Project Gutenberg edition of the same
sacred-texts transcription (J. B. Hare), 4 volumes: ebooks 15474-15477 (cached in the work dir).
One entry per Ganguli section: reference = parvan.section; `title` = sub-parvan heading.
Sections are headed 'SECTION <roman>' in most books and by a bare arabic numeral in others (Karna, Sauptika...).
Footnote markers [n] are stripped and each book's FOOTNOTES block is dropped.
"""
import json, os, re, sys, time, unicodedata, urllib.request, collections

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/epics/pg'
OUT = '/Users/iashris/Desktop/rigved/public/data/epics/mahabharata_ganguli.json'
VOLS = [15474, 15475, 15476, 15477]

def fetch(n):
    path = f'{WORK}/pg{n}.txt'
    if not os.path.exists(path) or os.path.getsize(path) < 100000:
        os.makedirs(WORK, exist_ok=True)
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(f'https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt', timeout=60).read()
                open(path, 'wb').write(data)
                break
            except Exception as e:
                print('retry', n, e); time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f'failed to fetch {n}')
    return open(path, encoding='utf-8').read().replace('\r', '')

ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
def roman(s):
    t = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        t += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return t

HEAD_SEC = re.compile(r'^\s*(?:SECTION|Section) ([IVXLC]+)(?:\s*[-–]\s*([IVXLC]+))?\.?\s*$')
HEAD_NUM = re.compile(r'^(\d{1,3})$')
TITLE = re.compile(r'^\((.+)\)$')

def clean(paras):
    txt = '\n\n'.join(' '.join(l.strip() for l in p) for p in paras if p)
    txt = re.sub(r'\[\d+\]', '', txt)
    # J. B. Hare's editorial notes: [..--JBH], (???--JBH), [(...--JBH)], ([...--JBH])
    txt = re.sub(r'\(?\[\(?[^\[\]]*?-+ ?JBH\.?\)?\]\)?', '', txt)
    txt = re.sub(r'\([^()]*?-+ ?JBH\.?\)', '', txt)
    txt = re.sub(r'\(\[This where is the Bhagavad Gita.*?Bruno Hare\]\)', '', txt, flags=re.S)
    txt = re.sub(r'\[\(Bhagavad Gita Chapter [IVXL]+\)\]', '', txt)  # Hare's added Gita chapter heads
    txt = re.sub(r'\[sic\]', '', txt)
    txt = re.sub(r' +([,.;])', r'\1', txt)
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    return unicodedata.normalize('NFC', txt.strip())

out, counts, notes = [], collections.Counter(), []
for vol in VOLS:
    raw = fetch(vol)
    raw = raw.split('*** START OF', 1)[1].split('\n', 1)[1]
    raw = raw.split('*** END OF', 1)[0]
    lines = raw.split('\n')
    book_starts = [i for i, l in enumerate(lines) if re.fullmatch(r'BOOK (\d+)', l.strip())]
    for bi, bs in enumerate(book_starts):
        book = int(lines[bs].split()[1])
        be = book_starts[bi + 1] if bi + 1 < len(book_starts) else len(lines)
        blines = lines[bs:be]
        for j, l in enumerate(blines):
            if l.strip() in ('FOOTNOTES', 'Footnotes'):
                blines = blines[:j]; break
        parva = next(l.strip() for l in blines[1:] if l.strip())  # e.g. 'ADI PARVA', 'Karna-parva'
        parva = parva.replace('-parva', ' Parva').title()
        # locate headings
        heads = []
        expect = 1
        for j, l in enumerate(blines):
            s = l.strip()
            m = HEAD_SEC.match(l)
            if m:
                a = roman(m.group(1)); b = roman(m.group(2)) if m.group(2) else a
                heads.append((j, a, b)); expect = b + 1; continue
            m = HEAD_NUM.match(s)
            if m and int(s) == expect and (j == 0 or not blines[j - 1].strip()) and (j + 1 >= len(blines) or not blines[j + 1].strip()):
                heads.append((j, expect, expect)); expect += 1
        # swapped labels (Adi: 'Section CLXXVII' printed before 'SECTION CLXXVI'): renumber by position
        for hi in range(1, len(heads) - 1):
            (j0, a0, b0), (j1, a1, b1), (j2, a2, b2) = heads[hi - 1], heads[hi], heads[hi + 1]
            if a1 == b0 + 2 and a2 == b0 + 1:
                heads[hi], heads[hi + 1] = (j1, a2, a2), (j2, a1, a1)
                notes.append(f'swapped labels {book}.{a2}/{a1} renumbered by position')
        cur_title = parva
        for hi, (j, a, b) in enumerate(heads):
            end = heads[hi + 1][0] if hi + 1 < len(heads) else len(blines)
            body = blines[j + 1:end]
            # trailing book-end boilerplate ('The End of ... Parva') is kept; drop leading blank lines and the title line
            k = 0
            while k < len(body) and not body[k].strip(): k += 1
            title = None
            if k < len(body):
                tm = TITLE.match(body[k].strip())
                if tm:
                    title = tm.group(1).strip(); k += 1
            if title:
                cur_title = re.sub(r'[.,]?(\s+continued)?[.,]?$', '', title, flags=re.I)
            paras, p = [], []
            for l in body[k:]:
                if l.strip():
                    p.append(l)
                elif p:
                    paras.append(p); p = []
            if p: paras.append(p)
            # drop the next book's title-page lines and 'The End of ... Parva' trailers
            if hi + 1 == len(heads):
                while paras and re.fullmatch(r'(The Mahabharata|of|Krishna-Dwaipayana Vyasa|(The )?End of .*|END OF .*|The Eighteen parvas .*)',
                                             ' '.join(x.strip() for x in paras[-1]), flags=re.I):
                    paras.pop()
            text = clean(paras)
            if not text:
                notes.append(f'empty section {book}.{a}')
            t = cur_title if cur_title != parva else parva
            if a != b:
                t = f'{t} (Sections {a}-{b})'
                notes.append(f'combined {book}.{a}-{b}')
            out.append({'reference': f'{book}.{a}', 'sanskrit_iast': '', 'meaning': '', 'text': text, 'title': t,
                        'mandala': book, 'hymn': a, 'vedaId': 'mahabharata_ganguli'})
            counts[book] += 1
        prevn = 0
        for (_, a, b) in heads:
            if a != prevn + 1:
                notes.append(f'gap {book}: {prevn} -> {a}')
            prevn = b

refs = [e['reference'] for e in out]
dups = [r for r, c in collections.Counter(refs).items() if c > 1]
if dups:
    raise SystemExit(f'duplicate refs {dups[:10]}')
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('entries', len(out))
for b in sorted(counts): print(b, counts[b])
for n in notes: print('note', n)
