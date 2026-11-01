"""Add Keith's English (HOS 25, 1920) from Pramāṇa to public/data/brahmanas/kausitaki_brahmana.json.

Our file (GRETIL) is adhyāya.khaṇḍa.sentence, but its khaṇḍa division is NOT Keith's (Lindner's): e.g. adhyāya 4
has 10 khaṇḍas here and 14 in Keith, adhyāya 1 has 5 in both but with different cuts.  So the English cannot be
keyed by khaṇḍa number.  Instead each Keith khaṇḍa (text from one "<adhyāya>. <khaṇḍa>." marker to the next,
headings dropped) is anchored to the sentence where it begins in our file, using Pramāṇa's own paragraph-to-
sentence alignment (`/api/segments/in.veda.brahmana.kausitaki?aligned=true`): the anchor is the earliest of
our sentences that Pramāṇa links to the khaṇḍa's first paragraph.  The khaṇḍa's English goes on that sentence
(with `keith_ref` = Keith's adhyāya.khaṇḍa); every following sentence up to the next anchor gets text "" and
`text_ref` = the reference of the sentence holding the English.  Nothing is split below Keith's khaṇḍa.
"""
import collections
import re
import sys
import unicodedata

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import get, segments, rom, heading_flags, join_paras  # noqa: E402
from jsonfmt import load, save  # noqa: E402

PATH = '/Users/iashris/Desktop/rigved/public/data/brahmanas/kausitaki_brahmana.json'
# Read by hand where neither Pramāṇa's alignment nor the MT overlap places a khaṇḍa (MT overlap < 0.25).
MANUAL = {'6.15': '6.9.24',   # prajāpatir ha yajñam sasṛje = 'Prajāpati is the creator of the sacrifice'
          '26.3': '26.2.20',  # atha kaścit śastre vā anuvacane vā pramatta = 'Supposing some one in carelessness'
          '26.4': '26.2.28',  # atha yady ūrdhvam paridhānāt praṇava-vaṣaṭkārayor = 'Now if after the conclusion'
          '26.5': '26.2.33',  # daivodāsiḥ pratardano naimiṣīyāṇām = 'Daivodāsi Pratardana ... Naimiṣīyas'
          '26.6': '26.2.38',  # yat pākatrā manasā dīnadakṣā = 'If that in poverty of mind'
          # Pramāṇa gives no alignment for these; MT overlap proposed, each confirmed by reading:
          '4.6': '4.5.7',     # atha ataḥ sārvasenīyajñaḥ = 'Next as to the Sārvaseni sacrifice'
          '6.12': '6.5.27',   # atha yatra enam brūyuḥ = 'When they say to him'
          '6.13': '6.7.6',    # blade of grass from the Brahman's seat
          '6.14': '6.9.1',    # 'Indra is the most forcible ... of the gods'
          '7.1': '7.1.1', '7.2': '7.2.7', '7.3': '7.3.9', '7.4': '7.5.1', '7.5': '7.7.1', '7.6': '7.7.6',
          '7.7': '7.8.10', '7.8': '7.9.2', '7.9': '7.10.4', '7.10': '7.11.13',
          '22.6': '23.1.1',   # antas tṛtīyam ahaḥ = 'The third day is the end' (our adhyāya cut differs)
          '22.7': '23.1.22', '22.8': '23.2.18', '22.9': '23.3.1',
          '23.3': '23.6.1'}   # tat savitur vareṇyam iti vaiśvāmitro anucaraḥ
# Keith's bracketed (interpolated) khaṇḍa on the Sautrāmaṇī; its Sanskrit is not in our (GRETIL) text.
DROP = {'16.10'}
MARK = re.compile(r'^\s*\[?\s*([ivxl]+)\s*[.,]\s*(\d+)\s*\.\s*')


STOP = set("""the a an of and to in is are was were be by for on with as that this it he she they them his her
its their thus verily who which what so or not but at from have has had there these those him then when one
o thou thee thy ye you your we us our i me my do does did said say says let shall should will would may might
all also into than therefore here yonder if being been whereby""".split())


def words(t):
    t = unicodedata.normalize('NFKD', t.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c)).replace('ç', 's')
    return [w[:6] for w in re.findall(r'[a-z]{3,}', t) if w not in STOP]


def alignment():
    """Keith paragraph loc -> Sanskrit sentence locs Pramāṇa links to it; and the per-sentence machine
    translation, used ONLY as an alignment aid (never written to our file)."""
    k2s, mt, after = collections.defaultdict(list), {}, None
    while True:
        d = get('segments/in.veda.brahmana.kausitaki', limit=300, aligned='true', lang='en', after=after)
        for loc, lst in (d.get('aligned') or {}).items():
            for a in lst:
                if a['doc']['path'].endswith('~en-keith'):
                    k2s[a['loc']].append(loc)
                elif a['doc']['path'].endswith('~en-mt'):
                    mt[loc] = a.get('text') or ''
        after = d.get('next')
        if not after:
            return k2s, mt


def best_start(k, data, mt, lo, hi):
    """Sentence index in [lo, hi) whose MT best matches the khaṇḍa's opening words (weighted toward the
    first 12 words against sentences i..i+1, so short opening sentences are not skipped; ties -> earliest)."""
    kw = words(' '.join(k['paras']))
    k12, k30 = set(kw[:12]), set(kw[:30])

    def ov(ks, i, n):
        w = set(words(' '.join(mt.get(data[j]['reference'], '') for j in range(i, min(i + n, len(data))))))
        return len(ks & w) / max(1, len(ks))
    best = (-1, None)
    for i in range(lo, hi):
        sc = 0.6 * ov(k12, i, 2) + 0.4 * ov(k30, i, 4)
        if sc > best[0] + 1e-9:
            best = (sc, i)
    return best


def main():
    data, fmt = load(PATH)
    order = {e['reference']: i for i, e in enumerate(data)}
    k2s, mt = alignment()

    segs = [s for s in segments('in.veda.brahmana.kausitaki~en-keith') if s.get('text')]
    khandas = []  # dict(key, paras, locs)
    hf = heading_flags([(s['kind'], s['text'], bool(MARK.match(s['text']))) for s in segs])
    for i, s in enumerate(segs):
        t = s['text']
        m = MARK.match(t)
        if m:
            khandas.append({'key': f'{rom(m.group(1))}.{m.group(2)}', 'key0': f'{rom(m.group(1))}.{m.group(2)}', 'paras': [t[m.end():]], 'locs': [s['loc']]})
            continue
        if hf[i] or not khandas:
            continue
        khandas[-1]['paras'].append(t)
        khandas[-1]['locs'].append(s['loc'])

    # 1) Pramāṇa's alignment; 2) where it has none (e.g. Keith's adhyāya 7, absent as a section on Pramāṇa),
    # place the khaṇḍa between its neighbours by English-English overlap with the per-sentence MT.
    pre = []
    for k in khandas:
        start = None
        for pl in k['locs']:
            ss = [order[x] for x in k2s.get(pl, []) if x in order]
            if ss:
                start = min(ss)
                break
        pre.append(start)
    clean, merged, via_mt, weak = [], [], [], []
    dropped = []
    for idx, k in enumerate(khandas):
        st = pre[idx]
        lo = clean[-1][0] + 1 if clean else 0
        if k['key0'] in DROP:
            dropped.append(k['key0'])
            continue
        if k['key0'] in MANUAL:
            st = order[MANUAL[k['key0']]]
            assert st >= lo, k['key0']
        elif st is None or st < lo:
            nxt = next((p for p in pre[idx + 1:] if p is not None and p > lo), len(data))
            sc, st = best_start(k, data, mt, lo, nxt)
            via_mt.append((k['key'], data[st]['reference'] if st is not None else None, round(sc, 2)))
            if st is None or sc < 0.25:
                weak.append(k['key'])
                clean[-1][1]['paras'] += k['paras']
                clean[-1][1]['key'] += '+' + k['key']
                merged.append(k['key'])
                continue
        clean.append((st, k))
    unanch = [v for v in via_mt]
    for e in data:
        e['text'] = ''
        e.pop('text_ref', None)
        e.pop('keith_ref', None)
    starts = {st: k for st, k in clean}
    carrier = None
    for i, e in enumerate(data):
        if i in starts:
            k = starts[i]
            e['text'] = join_paras(k['paras'])
            e['keith_ref'] = k['key']
            carrier = e['reference']
        elif carrier:
            e['text_ref'] = carrier
    save(PATH, data, fmt)
    at_kh_start = sum(1 for st in starts if data[st]['reference'].endswith('.1'))
    print(f'KB: {len(data)} sentences; Keith khandas {len(khandas)}, anchored {len(clean)} '
          f'({at_kh_start} on a first sentence of our khanda); merged into predecessor {merged}')
    print('placed via MT overlap:', unanch)
    print('manual anchors:', MANUAL, 'dropped (no Sanskrit here):', dropped)
    print('sentences covered (text or text_ref):', sum(1 for e in data if e['text'] or e.get('text_ref')))
    keys = [k['key0'] for k in khandas]
    gaps = [(keys[i], keys[i + 1]) for i in range(len(keys) - 1)
            if not (keys[i + 1].split('.')[0] == keys[i].split('.')[0] and int(keys[i + 1].split('.')[1]) == int(keys[i].split('.')[1]) + 1)
            and not int(keys[i + 1].split('.')[1]) == 1]
    print('Keith marker gaps (OCR-lost markers, text stays with predecessor):', gaps)


if __name__ == '__main__':
    main()
