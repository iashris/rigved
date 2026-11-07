"""Add Pramāṇa's machine English (Gemini) of the Jaiminīya Upaniṣad Brāhmaṇa to
public/data/brahmanas/jaiminiya_upanisad_brahmana.json, in the field `text_mt` (never `text`).

Source: `in.veda.brahmana.jaiminiya_upanisad~en-mt` (loc_scheme "parent"), aligned to Pramāṇa's own Sanskrit
`in.veda.brahmana.jaiminiya_upanisad` (TITUS jub.htm, Oertel 1896), read with /api/segments?aligned=true.

Mapping: every Pramāṇa prose unit is matched to one of our entries by comparing the Sanskrit (normalised:
dandas, punctuation, whitespace and avagraha dropped).  First choice is the entry with the same location
whose Sanskrit agrees (similarity >= 0.9); otherwise a monotone difflib alignment of the two Sanskrit
sequences pairs the units.  A Pramāṇa unit that covers several of our entries (its Sanskrit = their
concatenation) puts its English on the first of them; the others get `text_ref` = that entry's reference.
Nothing is ever split.  Oertel's bracketed insertions and anuvāka colophons, present
only in Pramāṇa's Sanskrit, are ignored when comparing.  Units whose Sanskrit agrees with none of ours are reported and not written.
Each entry with English also gets `text_mt_source` naming the machine translation.
"""
import difflib
import re
import sys
import unicodedata

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import get  # noqa: E402
from jsonfmt import load, save  # noqa: E402

PATH = '/Users/iashris/Desktop/rigved/public/data/brahmanas/jaiminiya_upanisad_brahmana.json'
WORK = 'in.veda.brahmana.jaiminiya_upanisad'
MT = WORK + '~en-mt'
SOURCE = 'Pramāṇa machine translation (Gemini 3.8 Flash), in.veda.brahmana.jaiminiya_upanisad~en-mt'
MIN_SIM = 0.9


def norm(t):
    t = unicodedata.normalize('NFC', t or '').lower()
    return re.sub(r"[\s/|।॥'’ऽ.,;:!?()\[\]\-–—0-9]+", '', t)


def strip_apparatus(t):
    """Pramāṇa keeps Oertel's bracketed insertions and anuvāka colophons ('daśame 'nuvāke ... khaṇḍaḥ //'),
    which our TITUS file omits; drop them before comparing (the English is kept whole)."""
    t = re.sub(r'\[[^\]]*\]', ' ', t or '')
    return '\n'.join(ln for ln in t.split('\n') if not re.search(r"khaṇḍaḥ\s*//", ln))


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def fetch():
    """[(loc, sanskrit, english)] for every Pramāṇa prose/verse unit, in order."""
    out, after = [], None
    while True:
        d = get(f'segments/{WORK}', limit=300, aligned='true', lang='en', after=after)
        al = d.get('aligned') or {}
        for s in d['segments']:
            if not s.get('text'):
                continue
            en = [a['text'] for a in al.get(s['loc'], [])
                  if a['doc']['path'] == MT and a.get('rel') == 'translation' and a.get('text')]
            out.append((s['loc'], s['text'], '\n'.join(en).strip()))
        after = d.get('next')
        if not after:
            return out


def main():
    data, fmt = load(PATH)
    for e in data:
        for k in ('text_mt', 'text_mt_source', 'text_ref'):
            e.pop(k, None)
    units = fetch()
    ours = [norm(e['sanskrit_iast']) for e in data]
    idx = {e['reference']: i for i, e in enumerate(data)}

    # unit index -> list of our entry indices it covers
    cover, unmatched = {}, []
    used = set()
    for u, (loc, sa, en) in enumerate(units):
        i = idx.get(loc)
        if i is not None and max(sim(norm(sa), ours[i]), sim(norm(strip_apparatus(sa)), ours[i])) >= MIN_SIM:
            cover[u] = [i]
            used.add(i)
    # Fallback for the rest: grow a run of our consecutive unused entries starting after the previous match.
    last = -1
    for u, (loc, sa, en) in enumerate(units):
        if u in cover:
            last = cover[u][-1]
            continue
        n, best = norm(strip_apparatus(sa)), None
        j, acc = last + 1, ''
        while j < len(data) and j not in used and len(acc) < len(n) * 1.3:
            acc += ours[j]
            s = sim(n, acc)
            if s >= MIN_SIM and (best is None or s > best[0]):
                best = (s, list(range(last + 1, j + 1)))
            j += 1
        if best:
            cover[u] = best[1]
            used.update(best[1])
            last = best[1][-1]
        else:
            unmatched.append(loc)

    written = 0
    for u, ii in cover.items():
        en = units[u][2]
        if not en:
            continue
        head = data[ii[0]]
        head['text_mt'] = en
        head['text_mt_source'] = SOURCE
        written += 1
        for i in ii[1:]:
            data[i]['text_ref'] = head['reference']
    save(PATH, data, fmt)

    n_mt = sum(1 for e in data if e.get('text_mt'))
    n_cov = sum(1 for e in data if e.get('text_mt') or e.get('text_ref'))
    multi = sum(1 for ii in cover.values() if len(ii) > 1)
    by_loc = sum(1 for u, ii in cover.items() if len(ii) == 1 and data[ii[0]]['reference'] == units[u][0])
    print(f'Pramāṇa units: {len(units)}, with English: {sum(1 for x in units if x[2])}')
    print(f'matched: {len(cover)} (same loc: {by_loc}, multi-entry: {multi}); unmatched: {unmatched[:20]}')
    print(f'our entries: {len(data)}, text_mt: {n_mt}, text_ref: {n_cov - n_mt}, '
          f'covered: {n_cov} ({100 * n_cov / len(data):.1f}%)')
    missing = [e['reference'] for e in data if not (e.get('text_mt') or e.get('text_ref'))]
    print('entries without English:', missing[:30])


if __name__ == '__main__':
    main()
