"""Maitri (Maitrayaniya) Upanishad from sanskritdocuments.org ITRANS.

Source: https://sanskritdocuments.org/doc_upanishhat/maitri.itx
Reference = prapathaka.khanda exactly as numbered in that file (see notes in
the report: P1-P5 follow the file's own (108-Upanishad / Sama) division, P6-P7
were taken by the encoder from Radhakrishnan and follow Cowell's numbering).
English: Max Mueller, SBE 15 (1884), via Internet Archive snapshots of
sacred-texts.com/hin/sbe15/sbe15112-118.htm, attached only for prapathakas
whose khanda division matches Cowell/Mueller (3, 6, 7).
"""
import re, sys, html, os
sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from sadocs_common import fetch, itx_to_iast, entry, validate, write, header

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/sadocs'
OUT = '/Users/iashris/Desktop/rigved/public/data/upanishads/maitri_upanishad.json'
ENGLISH_PRAPATHAKAS = {3, 6, 7}

MK = re.compile(r'\.\.\s*(\d+)\s*\.\.')


def sanskrit():
    itx = fetch('doc_upanishhat/maitri.itx', WORK + '/dl')
    h = header(itx)
    print('header:', h.get('Text title'), '|', h.get('Transliterated by'), '|', h.get('Latest update'))
    body = itx[itx.index('OM bR^ihadratho'):itx.index('OM ApyAyantviti shAntiH')]
    body = re.sub(r'\\medskip\\hrule\\medskip', '', body)
    parts = re.split(r'(?:iti\s+)?[\w^~]+H\s+prapAThakaH\s*\.\.|\.\s*atha prapAThaka 6\s*\.|prapAThaka\s+7\s*\.', body)
    parts = [p for p in parts if p.strip()]
    assert len(parts) == 7, len(parts)
    out = []
    for P, txt in enumerate(parts, 1):
        if P == 4:   # verses 1..15 inside khanda 4 ("atraite shlokA bhavanti"): verse numbers -> danda
            a = txt.index('atraite shlokA')
            b = txt.index('.. 15..') + len('.. 15..')
            txt = txt[:a] + MK.sub(' || ', txt[a:b]) + txt[b:]
        txt = re.sub(r'(?m)^\s*\d+\s+', ' ', txt)        # line-initial verse numbers (6.34, 7.11)
        pos, k = 0, 1
        for m in MK.finditer(txt):
            n = int(m.group(1))
            assert n == k, (P, n, k, txt[pos:m.start()][-80:])
            out.append((P, k, txt[pos:m.start()]))
            pos, k = m.end(), k + 1
        assert not txt[pos:].strip(), (P, txt[pos:][:100])
    return out


def clean(raw):
    s = raw.replace('\\:', ' ')
    s = re.sub(r'\.\.', ' || ', s)
    s = re.sub(r'\.(?![a-zA-Z])', ' | ', s)
    t = itx_to_iast(s)
    t = re.sub(r'(\|\s*){3,}', '|| ', t)
    t = re.sub(r'\|\|\s*\|(?!\|)', '||', t)
    t = re.sub(r'^\s*\|+\s*', '', t).strip()
    return re.sub(r'\s+', ' ', t)


def english():
    """Mueller SBE 15 khandas: {(P, k): text}."""
    eng = {}
    for P in range(1, 8):
        url = f'https://web.archive.org/web/2025id_/https://sacred-texts.com/hin/sbe15/sbe15{111 + P}.htm'
        path = f'{WORK}/dl/sbe15/sbe15{111 + P}.htm'
        if not os.path.exists(path):
            os.system(f'python3 -I {WORK}/fetch_wb.py "{url}" "{path}"')
        t = open(path, encoding='latin-1').read()
        t = re.split(r'<H3 ALIGN="CENTER">Footnotes</H3>', t, flags=re.I)[0]
        t = re.sub(r'<A NAME="fr_[^>]*>\s*</A>\s*<A HREF="#fn_[^>]*>.*?</A>', '', t, flags=re.S | re.I)  # footnote refs
        t = re.sub(r'<FONT SIZE="1"[^>]*>.*?</FONT>', '', t, flags=re.S | re.I)  # page numbers
        t = t.replace('<p>2 1. And thus', '<p>21. And thus')            # sbe15117 typo
        # every paragraph opening with a number starts a khanda; counted sequentially
        starts = [m for m in re.finditer(r'<p>\s*(\d{1,2})(?:&nbsp;|\s)*\.', t, re.I)]
        for k, m in enumerate(starts, 1):
            n = int(m.group(1))
            assert n == k, (P, k, n)
            end = starts[k].start() if k < len(starts) else len(t)
            seg = t[m.end():end]
            seg = seg.split('Next:')[0]
            seg = re.sub(r'</?(?:I|B|SUP|SUB)>', '', seg, flags=re.I)
            seg = re.sub(r'<[^>]+>', ' ', seg)
            seg = html.unescape(seg).replace('\xa0', ' ')
            seg = re.sub(r'\bp\. \d+\b', ' ', seg)
            seg = re.sub(r'\s+', ' ', seg).strip()
            eng[(P, k)] = re.sub(r'\s+([,.;:!?)])', r'\1', seg)
    return eng


if __name__ == '__main__':
    ks = sanskrit()
    eng = english()
    entries = []
    for P, k, raw in ks:
        e_txt = eng.get((P, k), '') if P in ENGLISH_PRAPATHAKAS else ''
        entries.append(entry(f'{P}.{k}', clean(raw), 'maitri_upanishad', re.sub(r'\s+\d+\s*$', '', e_txt).strip()))
    validate(entries, 'maitri_upanishad')
    write(entries, OUT)
    import collections
    print('sanskrit khandas per P:', dict(collections.Counter(P for P, _, _ in ks)))
    print('mueller khandas per P:', dict(collections.Counter(P for P, _ in eng)))
