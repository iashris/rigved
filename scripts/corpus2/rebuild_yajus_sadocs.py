"""Rebuild Taittiriya Samhita and Taittiriya Brahmana from sanskritdocuments.org ITRANS.

Sources (accented editions by Muralidhara B A):
  https://sanskritdocuments.org/doc_veda/taittirIyasamhitA.itx
  https://sanskritdocuments.org/doc_veda/taittirIyabrAhmaNam.itx

TS: the file holds the accented text (kandas 1-7) followed by an unaccented
copy; only the accented half is used. Paragraphs (pancasat) are numbered
1..n running within each prasna; the last paragraph of an anuvaka ends with
"|| <anukramani> || K| P| A||". Reference = K.P.A.k, k = position of the
paragraph inside its anuvaka (standard TS citation, e.g. TS 1.1.2.1).
The anukramani (pratika + syllable count) and the end-of-prasna index are
dropped.

TB: every paragraph ends with "|| K| P| A| N||" (N = paragraph within the
anuvaka) -> reference K.P.A.N. The "kAThakam" chapter is TB 3.10-3.12, as its
markers say. Anukramani text after anuvaka-final markers is dropped.

Run with the sadocs venv python (needs indic_transliteration).
"""
import re, sys
sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from sadocs_common import fetch, itx_to_iast, entry, validate, write, header

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/rebuild_yajus'
DATA = '/Users/iashris/Desktop/rigved/public/data/'
SEP = r'\s*\|\|?\s*'
TS_MARK = re.compile(r'\|\|\s*(\d+)' + SEP + r'(\d+)' + SEP + r'(\d+)\s*\|\|')
TB_MARK = re.compile(r'\|\|\s*(\d+)' + SEP + r'(\d+)' + SEP + r'(\d+)' + SEP + r'(\d+)\s*\|\|')
PSTART = re.compile(r'(?m)^[ \t]*(\d+)[ \t]+(?=\S)')


def sections(itx):
    """Yield (prapathaka_no, body) for numbered \\section{}s; unnumbered
    subtitle sections are merged into the preceding numbered one."""
    out = []
    for sec in re.split(r'\\section\{', itx)[1:]:
        title, body = sec.split('}', 1)
        m = re.search(r'(\d+)\s*$', title.strip())
        if m:
            out.append([int(m.group(1)), body])
        else:
            out[-1][1] += '\n' + body
    return out


def paragraphs(body):
    """Split a section body into numbered paragraphs 1..n (sequential)."""
    starts, n = [], 1
    for m in PSTART.finditer(body):
        if int(m.group(1)) == n:
            starts.append(m)
            n += 1
    paras = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(body)
        paras.append((int(m.group(1)), body[m.end():end]))
    return paras


def to_iast(raw):
    """itx_to_iast plus removal of the stray svara/kampa digits 1/2 this
    edition puts next to avagrahas (e.g. "Asante1'nyo'nyasmai")."""
    out = itx_to_iast(raw)
    out = re.sub(r"\s*[12]\s*(?=')", '', out)
    out = re.sub(r"(?<=')\s*[12]\s*(?=')", '', out)
    out = re.sub(r"(?<=')[12]", '', out)
    out = re.sub(r'(?<=\w) [12] (?=\w)', ' ', out)
    return out


def strip_anukramani(chunk, ref, log):
    t = chunk.rstrip().rstrip('|').rstrip()
    i = t.rfind('||')
    if i < 0:
        log.append((ref, 'no || before marker'))
        return chunk
    tail = t[i + 2:]
    if len(tail.split()) > 8:
        log.append((ref, 'long anukramani: ' + tail[:80]))
    return t[:i]


def build_ts():
    itx = fetch('doc_veda/taittirIyasamhitA.itx', WORK + '/dl')
    h = header(itx)
    print('TS header:', h.get('Text title'), '|', h.get('Transliterated by'), '|', h.get('Latest update'))
    itx = itx.split('\\chapter{|| (niHsvaraH)')[0]
    chapters = re.split(r'\\chapter\{', itx)[1:]
    out, log = [], []
    for K, ch in enumerate(chapters, 1):
        for P, body in sections(ch):
            A, k = 1, 0
            for n, chunk in paragraphs(body):
                m = TS_MARK.search(chunk)
                k += 1
                ref = f'{K}.{P}.{A}.{k}'
                if m:
                    mk, mp, ma = map(int, m.groups())
                    if (mk, mp, ma) != (K, P, A):
                        log.append((ref, 'marker', m.groups()))
                    m2 = TS_MARK.search(chunk, m.end())
                    if m2 and m2.groups() == m.groups():
                        # kandas 2-7: "text || K| P| A|| anukramani || K| P| A||"
                        text = chunk[:m.start()]
                    else:
                        text = strip_anukramani(chunk[:m.start()], ref, log)
                else:
                    text = chunk
                out.append(entry(ref, to_iast(text), 'taittiriya_samhita'))
                if m:
                    A, k = A + 1, 0
            if k:
                log.append((f'{K}.{P}', 'trailing paragraphs without marker', k))
    for l in log:
        print('  TS note:', l)
    return out


def build_tb():
    itx = fetch('doc_veda/taittirIyabrAhmaNam.itx', WORK + '/dl')
    h = header(itx)
    print('TB header:', h.get('Text title'), '|', h.get('Transliterated by'), '|', h.get('Latest update'))
    chapters = re.split(r'\\chapter\{', itx)[1:]
    items, log = [], []          # [K, P, A, N or None, raw]
    for ci, ch in enumerate(chapters):
        for P, body in sections(ch):
            for n, chunk in paragraphs(body):
                m = TB_MARK.search(chunk)
                if m:
                    items.append(list(map(int, m.groups())) + [chunk[:m.start()]])
                else:
                    # unmarked (or truncated marker such as "|| 1||" at 2.3.7.1)
                    items.append([None, None, None, None,
                                  re.sub(r'\|\|\s*\d+\s*\|\|\s*$', '', chunk)])
    # A few paragraphs lack their marker and a few markers have a typo in N
    # (e.g. 3.1.4: 1, 2, 1, 4 ...). K.P.A come from the markers (unmarked
    # paragraphs take the anuvaka of the next marked paragraph unless that one
    # opens a new anuvaka); N is recomputed as the position in the anuvaka.
    for i, it in enumerate(items):
        if it[0] is None:
            j = next(j for j in range(i + 1, len(items)) if items[j][0] is not None)
            nxt = items[j]
            it[:3] = nxt[:3] if nxt[3] > j - i else items[i - 1][:3]
            log.append(('unmarked paragraph assigned to anuvaka', '.'.join(map(str, it[:3]))))
    last, k = None, 0
    for it in items:
        k = k + 1 if tuple(it[:3]) == last else 1
        last = tuple(it[:3])
        if it[3] is not None and it[3] != k:
            log.append(('marker N differs from position', '.'.join(map(str, it[:4])), '->', k))
        it[3] = k
    out = [entry('.'.join(map(str, it[:4])), to_iast(it[4]), 'taittiriya_brahmana') for it in items]
    for l in log:
        print('  TB note:', l)
    return out


def dandas(entries):
    """Devanagari dandas in `meaning` (as in the TITUS-based rebuilds)."""
    for e in entries:
        e['meaning'] = e['meaning'].replace('||', '॥').replace('|', '।')
    return entries


if __name__ == '__main__':
    which = sys.argv[1:] or ['ts', 'tb']
    if 'ts' in which:
        ts = dandas(build_ts())
        validate(ts, 'taittiriya_samhita')
        write(ts, DATA + 'vedas/taittiriya_samhita.json')
    if 'tb' in which:
        tb = dandas(build_tb())
        validate(tb, 'taittiriya_brahmana')
        write(tb, DATA + 'brahmanas/taittiriya_brahmana.json')
