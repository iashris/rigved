"""Taittiriya Aranyaka (prapathakas 1-10) from sanskritdocuments.org ITRANS.

Source: https://sanskritdocuments.org/doc_veda/taittirIyaAraNyaka.itx
Each paragraph ends with "|| 0| P| A| N||" where P = prapathaka (prasna),
A = anuvaka, N = running paragraph number within the prapathaka (the leading
0 is a constant book field; the appended Ekagnikanda uses P=0). The reference
is P.A.K with K = position of the paragraph inside its anuvaka (the usual
TA citation, e.g. TA 1.1.3). Opening/closing santi-patha lines (numbered 0)
and the end-of-anuvaka / end-of-prasna anukramani (pratika index lines) are
not included. The Ekagnikanda (two extra prasnas) is excluded.
Optionally writes prasna 10 also as the Mahanarayana Upanishad.
"""
import re, sys
sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from sadocs_common import fetch, itx_to_iast, entry, validate, write, header

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/sadocs'
OUT_TA = WORK + '/out/taittiriya_aranyaka_full.json'
OUT_MNU = '/Users/iashris/Desktop/rigved/public/data/upanishads/mahanarayana_upanishad.json'

MARK = re.compile(r'\|\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\s*\|\|')


def parse():
    itx = fetch('doc_veda/taittirIyaAraNyaka.itx', WORK + '/dl')
    print('header:', header(itx).get('Text title'), '|', header(itx).get('Transliterated by'),
          '|', header(itx).get('Latest update'))
    itx = re.sub(r'^##.*$', '', itx, flags=re.M)          # inline editor notes
    secs = re.split(r'\\section\{', itx)[1:]
    paras = []  # (P, A, N, text)
    for sec in secs:
        title = sec.split('}')[0]
        if 'ekAgni' in title:
            continue
        P = int(re.search(r'(\d+)\s*$', title.strip()).group(1))
        body = sec.split('}', 1)[1]
        # drop santi-patha blocks (lines starting with "0 ", ending "shAntiH.. ||")
        body = re.sub(r'(?m)^0 .*?shAntiH\\?[\'`"]?\s*\|\|', '', body, flags=re.S)
        pos = 0
        n_expected = 1
        for m in MARK.finditer(body):
            z, p, a, n = map(int, m.groups())
            assert z == 0 and p == P, (title, m.groups())
            assert n == n_expected, (title, m.groups(), n_expected)
            chunk = body[pos:m.start()]
            pm = re.search(r'(?:^|\n)\s*%d ' % n, chunk)
            assert pm, (P, a, n, chunk[:200])
            paras.append((P, a, n, chunk[pm.end():]))
            pos = m.end()
            n_expected += 1
    return paras


def build(paras, vid, sel=None, drop_p=False):
    out, k, last = [], 0, None
    for P, A, N, raw in paras:
        if sel and P not in sel:
            continue
        k = k + 1 if (P, A) == last else 1
        last = (P, A)
        ref = f'{A}.{k}' if drop_p else f'{P}.{A}.{k}'
        out.append(entry(ref, itx_to_iast(raw), vid))
    return out


if __name__ == '__main__':
    paras = parse()
    ta = build(paras, 'taittiriya_aranyaka')
    validate(ta, 'taittiriya_aranyaka_full')
    write(ta, OUT_TA)
    mnu = build(paras, 'mahanarayana_upanishad', sel={10}, drop_p=True)
    validate(mnu, 'mahanarayana_upanishad')
    write(mnu, OUT_MNU)
