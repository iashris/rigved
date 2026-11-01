"""Add Max Müller's English (SBE 1, 1879) from Pramāṇa to public/data/aranyakas/aitareya_aranyaka.json.

Pramāṇa doc `in.veda.aranyaka.aitareya~en-muller` is located āraṇyaka.adhyāya.khaṇḍa.paragraph (+ .nN notes),
the same āraṇyaka.adhyāya.khaṇḍa scheme as our file, and covers Āraṇyakas I-III (Müller translated I as well
as the Upaniṣad II-III).  Āraṇyakas IV (Mahānāmnī verses) and V (Āśvalāyana's sūtra part) are not in SBE 1.
Müller's notes are left out.  One place where our (GRETIL) khaṇḍa cuts differ from Müller's was found by
comparing both sides: our 3.1.4 = Müller 3.1.4 + 3.1.5.1-8; our 3.1.5 = Müller 3.1.5.9 + 3.1.6.1-22;
our 3.1.6 = Müller 3.1.6.23 (the closing formula).
"""
import collections
import sys

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import segments, join_paras  # noqa: E402
from jsonfmt import load, save  # noqa: E402

PATH = '/Users/iashris/Desktop/rigved/public/data/aranyakas/aitareya_aranyaka.json'


def remap(loc):
    """Müller paragraph loc (a.b.c.p) -> our khaṇḍa reference."""
    a, b, c, p = loc.split('.')[:4]
    k, p = f'{a}.{b}.{c}', int(p)
    if k == '3.1.5':
        return '3.1.4' if p <= 8 else '3.1.5'
    if k == '3.1.6':
        return '3.1.5' if p <= 22 else '3.1.6'
    return k


def main():
    data, fmt = load(PATH)
    eng = collections.defaultdict(list)
    for s in segments('in.veda.aranyaka.aitareya~en-muller'):
        parts = s['loc'].split('.')
        if s.get('kind') in ('prose', 'verse') and len(parts) == 4 and parts[3].isdigit() and s.get('text'):
            eng[remap(s['loc'])].append(s['text'])
    n = 0
    for e in data:
        e['text'] = join_paras(eng.get(e['reference'], []))
        n += bool(e['text'])
    extra = set(eng) - {e['reference'] for e in data}
    assert not extra, extra
    save(PATH, data, fmt)
    print(f'AA: {len(data)} entries, {n} with English ({100 * n / len(data):.1f}%); without: '
          f'{[e["reference"] for e in data if not e["text"]]}')


if __name__ == '__main__':
    main()
