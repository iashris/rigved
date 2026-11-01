"""Maitrayani Samhita (GRETIL 1_veda/1_sam/maitrs_pu.htm, plain/unaccented) -> JSON.

Native unit numbered in the source: MS_kanda,prapathaka.anuvaka (the "khanda").
Mantras inside an anuvaka are not numbered in the source, so one entry per anuvaka.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vedic_common import GRETIL, make_entry, slashes_to_dandas, validate, write  # noqa: E402

SRC = os.path.join(GRETIL, '1_veda/1_sam/maitrs_pu.htm')
OUT = 'public/data/vedas/maitrayani_samhita.json'
VID = 'maitrayani_samhita'


def main():
    raw = open(SRC, encoding='utf-8').read().replace('\r\n', '\n')
    start = raw.index('Maitrāyaṇī-Saṃhitā<br>')
    body = raw[start + len('Maitrāyaṇī-Saṃhitā<br>'):]
    body = body[:body.index('</body>')]
    body = re.sub(r'<span class="(red|blue)">.*?</span>', ' ', body, flags=re.S)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = html.unescape(body)
    # mis-encoded characters in the GRETIL file: 'π' stands for ṝ (pitṝṇām,
    # caturhotṝn) and '·' for ū (vyūhet, ūrdhva, abhyūhati)
    body = body.replace('π', 'ṝ').replace('·', 'ū')

    # source glitch: 2,1.1 ends with stacked markers //MS_2,1.1//MS_2,1.2//MS_2,1.3//
    # while the real 2,1.2 and 2,1.3 follow later; keep only the first marker.
    body = re.sub(r'(//\s*MS_\d+,\d+\.\d+\s*//)(?:MS_\d+,\d+\.\d+//)+', r'\1', body)
    parts = re.split(r'//\s*MS_(\d+),(\d+)\.(\d+)\s*//', body)
    tail = parts[-1].strip()
    if tail:
        raise SystemExit(f'unreferenced trailing text: {tail[:200]}')
    entries = []
    for i in range(0, len(parts) - 1, 4):
        txt, k, p, a = parts[i], parts[i + 1], parts[i + 2], parts[i + 3]
        txt = slashes_to_dandas(txt + ' //')
        entries.append(make_entry([k, p, a], txt, VID))
    path = write(OUT, entries)
    validate(path, '(Schroeder: 4 kandas, 54 prapathakas; source markers run consecutively)')


if __name__ == '__main__':
    main()
