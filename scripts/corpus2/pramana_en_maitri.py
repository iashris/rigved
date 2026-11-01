"""Rebuild public/data/upanishads/maitri_upanishad.json in Cowell's prapāṭhaka.khaṇḍa numbering with Max Müller's
English (SBE 15, 1884), both from Pramāṇa.

Pramāṇa's Sanskrit (`in.veda.upanisad.mukhya.maitri`) is the same sanskritdocuments.org maitri.itx our old file
used: prapāṭhakas 6-7 follow Cowell, but 1-5 are the file's own (108-Upaniṣad recension) cuts, with Cowell's
6.1-6.8 repeated as its "prapāṭhaka 5" and the 6.34 ślokas repeated inside its "prapāṭhaka 4".  Pramāṇa does
not renumber it.  So P1-P5 are regrouped here into Cowell's khaṇḍas by reading them against Müller's
translation (and Hume's section openings, used only as a check of the cuts):
  Cowell 1.2 = sd 1.1 (minus the stray list of Upaniṣad names); 1.3 = sd 1.2-1.3; 1.4 = sd 1.4-1.7
  2.1-2.5 = sd 2.1-2.5; 2.6 = sd 2.6-2.9; 2.7 = sd 2.10-2.11; 3.1-3.5 = sd 3.1-3.5
  4.1 = sd 4.1; 4.2 = sd 4.1.p1 + 4.2; 4.3 = sd 4.2.p1 + 4.3
  5.1 = sd 4.11.p1 + 4.12-4.15 (Kutsāyana's hymn); 5.2 = sd 4.5_2
  dropped as duplicates: sd 4.3.p1 + 4.1_2..4.11 (= ślokas of 6.34), sd 5.1-5.8 (= 6.1-6.8)
  Cowell 1.1 and 4.4-4.6 are not in the source at all, so they are omitted (no empty Sanskrit).
Prapāṭhakas 6-7: loc n + n.pK sub-paragraphs, except that the .pK under 6.23, 6.24, 6.27, 6.29, 6.37, 7.8 and
7.10 open the next Cowell khaṇḍa (e.g. 6.37.p1 'agnihotraṃ juhvāno' = Müller 6.38) and are moved to it.
English: Müller's 2.6 covers Cowell 2.6-2.7 (its 4th paragraph is 2.7); his 6.20 carries 6.21 after a "2 1." mark.
Müller's notes are left out.
"""
import re
import sys
import unicodedata

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from pramana_en_common import segments, clean_en, write_json, entry, validate  # noqa: E402

OUT = '/Users/iashris/Desktop/rigved/public/data/upanishads/maitri_upanishad.json'
VID = 'maitri_upanishad'
GROUPS = {'1.2': ['1.1'], '1.3': ['1.2', '1.3'], '1.4': ['1.4', '1.5', '1.6', '1.7'],
          '2.1': ['2.1'], '2.2': ['2.2'], '2.3': ['2.3'], '2.4': ['2.4'], '2.5': ['2.5'],
          '2.6': ['2.6', '2.7', '2.8', '2.9'], '2.7': ['2.10', '2.11'],
          '3.1': ['3.1'], '3.2': ['3.2'], '3.3': ['3.3'], '3.4': ['3.4'], '3.5': ['3.5'],
          '4.1': ['4.1'], '4.2': ['4.1.p1', '4.2'], '4.3': ['4.2.p1', '4.3'],
          '5.1': ['4.11.p1', '4.12', '4.13', '4.14', '4.15'], '5.2': ['4.5_2']}
# In P6-7 the file numbers its verse blocks, so the prose that OPENS the next Cowell khaṇḍa sits as a .pN
# sub-paragraph under the previous number (checked against Müller): these .pN go to number + 1.
SHIFT_P = {'6.23', '6.24', '6.27', '6.29', '6.37', '7.8', '7.10'}
DUPLICATES = ['4.3.p1'] + [f'4.{i}_2' for i in (1, 2, 3)] + [f'4.{i}' for i in range(4, 12)] + \
             [f'5.{i}' for i in range(1, 9)] + ['1.p1', '1.p2', '1.p3', '1.p4', '1.p5', 'p1', 'p2']


def clean_sa(t):
    t = t.replace('\n', ' ')
    t = re.sub(r'\([^)]*\)', ' ', t)                        # bracketed variant readings
    t = re.sub(r'^\s*maitrāyaṇī kauṣitakī.*?(?=oṃ bṛhadratho)', '', t)
    t = re.sub(r'atha prapāṭhaka \d+\s*\|\s*', '', t)
    t = re.sub(r'(^|\s)\d+(?=\s)', ' ', t)                  # verse numbers inside 6.x/7.x
    t = re.sub(r'\s+', ' ', t).strip()
    return unicodedata.normalize('NFC', t)


def main():
    sa = {s['loc']: s['text'] for s in segments('in.veda.upanisad.mukhya.maitri')
          if s.get('kind') in ('verse', 'prose') and s.get('text')}
    used = set()
    khandas = {}
    for k, locs in GROUPS.items():
        khandas[k] = ' '.join(clean_sa(sa[x]) for x in locs)
        used |= set(locs)
    for loc in sa:
        m = re.match(r'^([67])\.(\d+)(?:\.p\d+)?$', loc)
        if not m:
            continue
        k = f'{m.group(1)}.{m.group(2)}'
        if '.p' in loc and k in SHIFT_P:
            k = f'{m.group(1)}.{int(m.group(2)) + 1}'
        khandas[k] = (khandas.get(k, '') + ' ' + clean_sa(sa[loc])).strip()
        used.add(loc)
    left = set(sa) - used - set(DUPLICATES)
    assert not left, sorted(left)

    en = {}
    for s in segments('in.veda.upanisad.mukhya.maitri~en-muller'):
        if s.get('kind') == 'prose' and s.get('text'):
            en[s['loc']] = s['text']
    p26 = [p for p in en.pop('2.6').split('\n') if p.strip()]
    assert len(p26) == 4, len(p26)
    en['2.6'], en['2.7'] = '\n'.join(p26[:3]), p26[3]
    a, b = re.split(r'\n\s*2\s*1\.\s*', en['6.20'], maxsplit=1)
    en['6.20'], en['6.21'] = a, b

    key = lambda r: tuple(int(x) for x in r.split('.'))  # noqa: E731
    out = [entry(k, khandas[k], VID, clean_en(en.get(k, ''))) for k in sorted(khandas, key=key)]
    validate(out, 'maitri')
    write_json(out, OUT)
    print('no English:', [e['reference'] for e in out if not e['text']],
          '| Müller without Sanskrit here:', sorted(set(en) - set(khandas), key=key))


if __name__ == '__main__':
    main()
