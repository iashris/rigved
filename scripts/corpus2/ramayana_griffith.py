#!/usr/bin/env python3
"""Ralph T. H. Griffith's verse Ramayan of Valmiki (1870-74) -> public/data/epics/ramayana_griffith.json.

sacred-texts.com is behind Cloudflare, so every page comes from Wayback Machine snapshots (cached in the work dir).
The 2026 snapshot of hin/rama/index.htm is the new paginated site, so the chapter list is read from the classic
index (snapshot 20240703172801), whose links are ry000.htm .. ry504.htm. Chapter pages come from web/2026id_/.

One entry per canto: reference = book.canto using Griffith's own (Roman) canto numbers, which skip cantos he left
out; `title` = canto heading. Book VII (Uttara) is not part of Griffith's sacred-texts edition. Navigation, page
markers, footnote markers and the footnote block are stripped. Lines consisting only of asterisks (Griffith's
marks for omitted passages / OCR gaps) are dropped.
"""
import html, json, re, sys, unicodedata, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ramayana_fetch_common import wayback

OUT = '/Users/iashris/Desktop/rigved/public/data/epics/ramayana_griffith.json'
ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

def roman(s):
    t = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        t += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return t

def text_of(fragment):
    s = re.sub(r'<A NAME="fr_\d+"></A><A HREF="#fn_\d+"><FONT SIZE="1">[^<]*</FONT></A>', '', fragment, flags=re.I)
    s = re.sub(r'<A NAME="page_[^"]*"><FONT[^>]*>p\. [^<]*</FONT></A>\s*(<BR>)?', '', s, flags=re.I)
    s = re.sub(r'<BR\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</?P[^>]*>', '\n\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('\xa0', ' ')
    return s

def clean(body):
    s = text_of(body)
    lines = [l.strip() for l in s.split('\n')]
    out, blank = [], False
    for l in lines:
        if re.fullmatch(r'[\*\s]+', l) and '*' in l:
            continue
        if not l:
            blank = True; continue
        if blank and out: out.append('')
        out.append(re.sub(r'[ \t]+', ' ', l)); blank = False
    txt = '\n'.join(out).strip()
    txt = re.sub(r' +([,.;:!?])', r'\1', txt)
    return unicodedata.normalize('NFC', txt)

def main():
    idx = wayback('hin/rama/index.htm', ts='20240703172801')
    book, items = None, []
    for m in re.finditer(r'<H3[^>]*>(.*?)</H3>|<A HREF="(ry\d{3})\.htm">(.*?)</A>', idx[idx.find('NAME="contents"'):], re.I | re.S):
        if m.group(1):
            h = html.unescape(m.group(1)).strip()
            bm = re.match(r'BOOK ([IVX]+)$', h, re.I)
            book = roman(bm.group(1).upper()) if bm else None
        elif book:
            title = re.sub(r'\s+', ' ', html.unescape(m.group(3))).strip()
            cm = re.match(r'Canto ([IVXLC]+)\s*[.:]', title + ':')
            if cm:
                items.append((book, roman(cm.group(1)), m.group(2), title))
    print('cantos listed:', len(items), collections.Counter(b for b, *_ in items))
    out, seen = [], set()
    for book, canto, page, idx_title in items:
        t = wayback(f'hin/rama/{page}.htm')
        m = re.search(r'<H3[^>]*>(.*?)</H3>', t, re.I | re.S)
        if not m: raise SystemExit(f'no heading in {page}')
        heading = clean(m.group(1))
        body = t[m.end():]
        cut = re.search(r'<P><A NAME="fn_\d+"></A>|<H\d[^>]*>\s*Footnotes|<P><HR>\s*<CENTER>\s*<A HREF="ry\d+\.htm">Next|<nav ', body, re.I)
        if cut: body = body[:cut.start()]
        txt = clean(body)
        ref = f'{book}.{canto}'
        if out and out[-1]['mandala'] == book and canto <= out[-1]['hymn']:
            # e.g. ry329 'Canto LVI:' (no title) is the rest of IV.54 split onto its own page: append it
            print(f'  {page} ({idx_title!r}) does not advance the canto number: appended to {out[-1]["reference"]}')
            out[-1]['text'] += '\n\n' + txt
            continue
        if ref in seen: raise SystemExit(f'duplicate {ref} ({page})')
        seen.add(ref)
        hm = re.match(r'CANTO ([IVXLC]+)\s*\.?\s*:?\s*(.*)$', heading, re.I)
        if not hm or roman(hm.group(1).upper()) != canto:
            print('  heading/index mismatch', page, repr(heading), idx_title)
        title = (hm.group(2).strip().rstrip('.') if hm else heading) or idx_title
        title = title.title() if title.isupper() else title
        if not txt: print('  EMPTY', page, ref)
        out.append({'reference': ref, 'sanskrit_iast': '', 'meaning': '', 'text': txt, 'title': title,
                    'mandala': book, 'hymn': canto, 'vedaId': 'ramayana_griffith'})
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', OUT, len(out))

if __name__ == '__main__':
    main()
