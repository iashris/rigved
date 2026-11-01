#!/usr/bin/env python3
"""Manmatha Nath Dutt's prose Ramayana (Calcutta 1891-94) -> public/data/epics/ramayana_dutt.json.

Source: Project Gutenberg ebooks 57265 (Bala, Ayodhya), 57826 (Aranya, Kishkindha, Sundara), 60188 (Yuddha),
62496 (Uttara), cached in the work dir.

One entry per section: reference = kanda.N where N is the section's ORDINAL position within the kanda in Dutt's
text. Dutt's printed section numerals contain many printer's errors (skips such as Bala XLII -> XLIV, repeats such
as Yuddha LXXI twice, misprints such as 'LXL' for XC); the ordinal is unique and in the cases checked tracks the
sarga sequence better than the printed numeral. `title` keeps the printed heading verbatim (e.g. 'Section XLIV').
Footnote paragraphs ('[n] ...', or superscript '¹ ...' in vol. 4) and their inline markers are dropped; _italic_ underscores are removed.
"""
import json, os, re, sys, time, unicodedata, urllib.request, collections

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/ramayana/pg'
OUT = '/Users/iashris/Desktop/rigved/public/data/epics/ramayana_dutt.json'
VOLS = [57265, 57826, 60188, 62496]
KANDAS = {'BALAKANDAM': 1, 'AYODHYAKANDAM': 2, 'ARANYA KANDAM': 3, 'KISHKINDHA KANDAM': 4,
          'SUNDARA KANDAM': 5, 'YUDDHAKANDAM': 6, 'UTTARAKĀNDAM': 7}
KHEAD = re.compile(r'^(' + '|'.join(KANDAS) + r')\.?\s*$')
SHEAD = re.compile(r'^\s*SECTI[O0]N ([IVXLCN]+)\.?(?:\[\d+\])?\s*$')
END = re.compile(r'^\s*(THE )?END OF ')
ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}

def roman(s):
    t = 0
    for i, ch in enumerate(s):
        v = ROMAN.get(ch, 0)
        t += -v if i + 1 < len(s) and ROMAN.get(s[i + 1], 0) > v else v
    return t

def fetch(n):
    path = f'{WORK}/pg{n}.txt'
    if not os.path.exists(path) or os.path.getsize(path) < 100000:
        os.makedirs(WORK, exist_ok=True)
        for attempt in range(4):
            try:
                open(path, 'wb').write(urllib.request.urlopen(
                    f'https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt', timeout=90).read())
                break
            except Exception as e:
                print('retry', n, e); time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f'failed to fetch {n}')
    return open(path, encoding='utf-8').read().replace('\r', '')

def clean(lines):
    paras, cur = [], []
    for l in lines + ['']:
        if l.strip(): cur.append(l)
        elif cur: paras.append(cur); cur = []
    keep = []
    for p in paras:
        if re.match(r'^\s*(\[\d+\]|[⁰¹²³⁴⁵⁶⁷⁸⁹]+\s)', p[0]): continue   # footnote paragraph ([n] or superscript n)
        if re.fullmatch(r'\s*(THE )?END\.?\s*', ' '.join(p)): continue
        keep.append(' '.join(l.strip() for l in p))
    txt = '\n\n'.join(keep)
    txt = re.sub(r'\[\d+\]|[⁰¹²³⁴⁵⁶⁷⁸⁹]+', '', txt)
    txt = re.sub(r'(?<=[a-z])1(?=[a-z])', 'l', txt)  # OCR: shou1d, 1ike
    txt = re.sub(r'(?<![A-Za-z0-9])_([^_]+)_(?![A-Za-z0-9])', r'\1', txt)
    txt = txt.replace('_', '')
    txt = re.sub(r' +([,.;:!?])', r'\1', txt)
    txt = re.sub(r'[ \t]+', ' ', txt)
    return unicodedata.normalize('NFC', txt.strip())

def main():
    out, seen, notes = [], set(), []
    for vol in VOLS:
        raw = fetch(vol)
        raw = raw.split('*** START OF', 1)[1].split('\n', 1)[1].split('*** END OF', 1)[0]
        lines = raw.split('\n')
        kanda, sec, printed, buf = None, 0, None, []
        def flush():
            if kanda and sec:
                ref = f'{kanda}.{sec}'
                if ref in seen: raise SystemExit(f'duplicate {ref}')
                seen.add(ref)
                txt = clean(buf)
                if not txt: raise SystemExit(f'empty {ref}')
                out.append({'reference': ref, 'sanskrit_iast': '', 'meaning': '', 'text': txt,
                            'title': f'Section {printed}', 'mandala': kanda, 'hymn': sec, 'vedaId': 'ramayana_dutt'})
        started = False
        for l in lines:
            m = KHEAD.match(l)
            if m and not '....' in l and (started or not l.startswith(' ')):
                # body kanda heading (unindented); TOC/title-page headings are indented or dotted
                flush(); kanda, sec, buf, started = KANDAS[m.group(1)], 0, [], True
                continue
            if not started: continue
            m = SHEAD.match(l)
            if m:
                flush(); sec += 1; buf = []
                printed = m.group(1).replace('0', 'O')
                if roman(printed) != sec: notes.append(f'{kanda}.{sec} printed {printed}')
                continue
            if END.match(l):
                flush(); buf = []; sec_end = True
                kanda_done = kanda; sec = 0
                continue
            buf.append(l)
        flush()
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = collections.Counter(e['mandala'] for e in out)
    print('wrote', OUT, len(out), dict(c))
    print(len(notes), 'printed numerals differ from ordinal; first:', notes[:8])

if __name__ == '__main__':
    main()
