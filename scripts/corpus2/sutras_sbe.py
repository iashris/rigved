#!/usr/bin/env python3
"""Parse Sacred Books of the East English translations of sutra texts into
per-text {reference: english} maps (WORK/english/<id>.json), for
sutras_gretil.py to merge.

Sources (public domain, sacred-texts.com transcriptions).  sacred-texts.com
itself serves a bot challenge, so the copies were fetched from the Internet
Archive's Wayback Machine (web.archive.org/web/2022id_/https://sacred-texts.com/...):
  SBE 2  (Bühler)    Apastamba, Gautama Dharmasutras        -> WORK/sbe/sbe02/*.htm
  SBE 14 (Bühler)    Vasishtha, Baudhayana Dharmasutras     -> WORK/sbe/sbe14/*.htm
  SBE 29 (Oldenberg) Sankhayana, Asvalayana, Paraskara, Khadira GS -> WORK/sbe/sbe29/txt/sbe29.txt
  SBE 30 (Oldenberg) Gobhila, Hiranyakesin, Apastamba GS   -> WORK/sbe/sbe30/txt/sbe30.txt
(see WORK/sbe/fetch.sh).

Run:  python3 -I scripts/corpus2/sutras_sbe.py
"""
import html
import json
import os
import re

SCRATCH = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus'
WORK = os.path.join(SCRATCH, 'work/sutras')
SBE = os.path.join(WORK, 'sbe')
EN = os.path.join(WORK, 'english')

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}


def roman(x):
    x = x.strip().rstrip('.,')
    if x.isdigit():
        return int(x)
    if x in ROMAN:
        return ROMAN[x]
    # longer romans (chapters up to XXX)
    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50}
    tot = 0
    for i, c in enumerate(x):
        v = vals[c]
        if i + 1 < len(x) and vals[x[i + 1]] > v:
            tot -= v
        else:
            tot += v
    return tot


def clean_en(s):
    s = re.sub(r'\[\*[^\]]*\]', '', s)
    s = re.sub(r'\[p\. \d+\]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


START = re.compile(r'^(\d+)(?:\s*(?:,|-|--|–)\s*(\d+))?(?:\s*\[\*[^\]]*\])?\s*\.?\s+(\S.*)$')


class Collector:
    """Collect numbered paragraphs under the current section prefix."""

    def __init__(self):
        self.maps = {}      # vid -> {ref: text}
        self.order = {}     # vid -> [ref]
        self.vid = None
        self.prefix = None
        self.cur = None     # ref of current sutra
        self.last = 0

    def section(self, vid, prefix):
        self.vid, self.prefix, self.cur, self.last = vid, tuple(prefix), None, 0
        self.maps.setdefault(vid, {})
        self.order.setdefault(vid, [])

    def para(self, p):
        p = clean_en(p)
        if not p or self.prefix is None:
            return
        m = START.match(p)
        if m and (m.group(3)[:1].isupper() or m.group(3)[:1] in "('\"[‘“" or self.cur is None):
            n = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else n
            # accept the next number (allow small gaps for sutras the
            # translator merged or skipped)
            if self.last < n <= self.last + 3 and hi >= n:
                ref = '.'.join(str(x) for x in self.prefix + (n,))
                if ref in self.maps[self.vid]:
                    raise SystemExit(f'{self.vid}: duplicate English ref {ref}')
                self.maps[self.vid][ref] = m.group(3)
                self.order[self.vid].append(ref)
                self.cur, self.last = ref, hi
                return
        if self.cur:
            self.maps[self.vid][self.cur] += ' ' + p


# ------------------------------------------------------------ SBE 2 / 14 (HTML)

def html_pages(vol, col):
    d = os.path.join(SBE, vol)
    pages = [l.strip() for l in open(os.path.join(d, 'pages.txt'))]
    for pg in pages:
        t = open(os.path.join(d, pg), encoding='latin-1').read()
        m = re.search(r'<title>\s*(.*?)\s*</title>', t, re.S | re.I)
        title = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1)))) if m else ''
        sec = parse_title(title)
        if not sec:
            continue
        vid, prefix = sec
        b = re.split(r'<H3 ALIGN="CENTER">Footnotes</H3>', t, flags=re.I)[0]
        b = b[b.lower().find('<body'):]
        b = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', ' ', b, flags=re.S | re.I)
        b = re.sub(r'&nbsp;\s*<A NAME="fr_\d+"></A>\s*<A HREF="#fn_\d+"><FONT SIZE="1">[^<]*</FONT></A>', ' ', b, flags=re.I)
        b = re.sub(r'<A NAME="fr_\d+"></A>\s*<A HREF="#fn_\d+">.*?</A>', ' ', b, flags=re.I | re.S)
        b = re.sub(r'<A NAME="page_\d+">.*?</A>', ' ', b, flags=re.I | re.S)
        col.section(vid, prefix)
        for p in re.split(r'<p[^>]*>', b, flags=re.I):
            txt = html.unescape(re.sub(r'<[^>]+>', ' ', p)).replace('\xa0', ' ')
            col.para(txt)


def parse_title(title):
    m = re.match(r'SBE 2: .*?Pra\s*s\s*n\s*a\s+(\w+),\s*Pa\s*t\s*ala\s+(\d+),\s*Kha\s*n\s*d\s*a\s+(\d+)', title)
    if m:
        return 'apastamba_dharmasutra', (roman(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r'SBE 2: Gautama: Chapter (\w+)', title)
    if m:
        return 'gautama_dharmasutra', (roman(m.group(1)),)
    m = re.match(r'SBE 14: Vasishtha: Chapter (\w+)', title)
    if m:
        return 'vasistha_dharmasutra', (roman(m.group(1)),)
    m = re.match(r'SBE 14: Baudh.yana: Prasna (\w+), Adhy.ya (\d+)(?:, Kandik. (\d+))?', title)
    if m:
        pr = (roman(m.group(1)), int(m.group(2)))
        if m.group(3):
            pr += (int(m.group(3)),)
        return 'baudhayana_dharmasutra', pr
    return None


# ------------------------------------------------------------ SBE 29 / 30 (text)

TEXTS = {
    'SANKHAYANA-GRIHYA-SUTRA.': 'sankhayana_grhyasutra',
    'ASVALAYANA-GRIHYA-SUTRA.': 'asvalayana_grhyasutra',
    'PARASKARA-GRIHYA-SUTRA.': 'paraskara_grhyasutra',
    'KHADIRA-GRIHYA-SUTRA.': 'khadira_grhyasutra',
    'GRIHYA-SUTRA OF GOBHILA.': 'gobhila_grhyasutra',
    'GRIHYA-SUTRA OF HIRANYAKESIN.': 'hiranyakesin_grhyasutra',
    'GRIHYA-SUTRA OF APASTAMBA,': 'apastamba_grhyasutra',
    'GRIHYA-SUTRA OF APASTAMBA.': 'apastamba_grhyasutra',
}
UPPER = r'(ADHYAYA|PRAPATHAKA|PRASNA|KANDA|PATALA)'
LOWER = r'(KHANDA|KANDIKA|SECTION)'


def text_volume(path, col):
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    # a translation starts at a title line whose next non-empty line is a heading
    starts = []
    for i, l in enumerate(lines):
        if l.strip() in TEXTS:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and re.match(r'\s*%s|\s*%s' % (UPPER, LOWER), lines[j]):
                starts.append((i, TEXTS[l.strip()]))
    starts.append((len(lines), None))
    for (s, vid), (e, _) in zip(starts, starts[1:]):
        upper = {}
        in_notes = False
        para = []

        def flush():
            if para:
                col.para(' '.join(para))
                para.clear()
        for l in lines[s + 1:e]:
            st = l.strip()
            if (re.match(r'(SYNOPTICAL SURVEY|INDEX|TRANSLITERATION)', st) or
                    (st.startswith('End of the') and not re.search(
                        r'(Adhyaya|Kanda|Patala|Prapathaka|Prasna)\.$', st))):
                flush()
                col.prefix = None
                break
            if st == 'Footnotes':
                flush()
                in_notes = True
                continue
            if st.startswith('End of the'):
                flush()
                continue
            if 'at sacred-texts.com' in st:
                flush()
                in_notes = False
                continue
            if in_notes:
                continue
            h = re.sub(r'\[\*[^\]]*\]', '', st)
            hm = re.fullmatch(r'(?:%s\.?\s+(\w+)[,.]?\s*)?(?:%s\.?\s+(\w+)[,.]?\s*)?(?:%s\.?\s*(\d+)?[.,]?)\s*' % (UPPER, UPPER, LOWER), h)
            if hm:
                flush()
                if hm.group(1):
                    upper[hm.group(1)] = roman(hm.group(2))
                if hm.group(3):
                    upper[hm.group(3)] = roman(hm.group(4))
                low = hm.group(6)
                if low is None:      # 'KHANDA [*1].' -> number was inside [*..]
                    low = re.search(r'\[\*(\d+)', st).group(1)
                low = int(low)
                if vid == 'apastamba_grhyasutra':
                    prefix = (low,)
                elif vid == 'hiranyakesin_grhyasutra':
                    prefix = (upper['PRASNA'], upper['PATALA'], low)
                else:
                    top = [v for k, v in upper.items() if k != 'PATALA' or vid == 'khadira_grhyasutra']
                    prefix = (top[-1], low) if top else (low,)
                col.section(vid, prefix)
                continue
            if not st or re.fullmatch(r'\[p\. \d+\]', st):
                flush()
                continue
            para.append(st)
        flush()


def main():
    os.makedirs(EN, exist_ok=True)
    col = Collector()
    html_pages('sbe02', col)
    html_pages('sbe14', col)
    text_volume(os.path.join(SBE, 'sbe29/txt/sbe29.txt'), col)
    text_volume(os.path.join(SBE, 'sbe30/txt/sbe30.txt'), col)
    for vid, m in col.maps.items():
        m = {k: re.sub(r'\s+', ' ', v).strip() for k, v in m.items()}
        json.dump(m, open(os.path.join(EN, vid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        json.dump(col.order[vid], open(os.path.join(EN, vid + '.order.json'), 'w'), indent=0)
        print(f'{vid}: {len(m)} English sutras, {col.order[vid][0]}..{col.order[vid][-1]}')


if __name__ == '__main__':
    main()
