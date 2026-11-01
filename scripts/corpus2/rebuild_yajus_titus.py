#!/usr/bin/env python3
"""Rebuild Aitareya Brahmana, Aitareya Aranyaka and Vajasaneyi Samhita from TITUS HTML.

Pages are downloaded by rebuild_yajus_titus_fetch.py into WORK/titus/<ab|aa|vs>/NNN.htm.

  ab  Aitareya Brahmana (Aufrecht 1879). TITUS: Chapter = pancika, Paragraph =
      khanda numbered within the pancika, and an inline label
      "adhyaya N, khandah 1-M" (N = 1..40) at each adhyaya start.
      Reference = adhyaya.khanda (40 adhyayas, khanda within adhyaya),
      e.g. the Sunahsepa story (pancika 7, khanda 13) = 33.1.
  aa  Aitareya Aranyaka (Aufrecht). Aranyaka.Adhyaya.Paragraph(khanda) -> a.a.k.
  vs  Vajasaneyi Samhita, Madhyandina (Weber). Paragraph (= adhyaya).Verse -> a.v.

One entry per khanda (AB, AA) or verse (VS). Text spans of the main font size
(iov*16) only; ioc* comments, size-12 footnote readings and h8/h9 page/line
markers are skipped.
"""
import os, re, sys, json, unicodedata
from bs4 import BeautifulSoup

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts/corpus2')
from titus_convert import clean_iast, to_deva  # noqa: E402

WORK = ('/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/'
        'c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/rebuild_yajus/titus')
DATA = '/Users/iashris/Desktop/rigved/public/data/'


def events(name):
    """Yield ('struct', key, value) / ('label', text) / ('sent',) / ('text', s)."""
    d = os.path.join(WORK, name)
    for f in sorted(os.listdir(d)):
        soup = BeautifulSoup(open(os.path.join(d, f), encoding='utf-8').read(), 'html.parser')
        for sp in soup.find_all('span', id=True):
            i = sp['id']
            if re.fullmatch(r'h[2-7]', i):
                t = sp.get_text(' ', strip=True)
                if ':' in t:
                    k, v = (x.strip() for x in t.split(':', 1))
                    yield ('struct', k, v)
            elif i.startswith('iovcs'):
                yield ('label', sp.get_text(' ', strip=True))
            elif i.startswith('iov') and i.endswith('16') and not i.startswith('iovc'):
                parts = [c.get_text() if hasattr(c, 'get_text') else str(c) for c in sp.children]
                t = ' '.join(p.strip() for p in parts if p.strip())
                t = re.sub(r'\{FN[^}]*\}', '', t)
                if t.strip():
                    yield ('text', t)


def clean(raw, prose, pre=None):
    s = unicodedata.normalize('NFC', raw)
    if pre:
        s = pre(s)
    s = re.sub(r'՚\s*[\d,]*', ' ', s)               # TITUS placeholder tokens ("purogavam ՚1 akaḥ", "՚0,1")
    s = re.sub(r'(?<![\w/])[,\s]*\d+(?![\w/])', ' ', s)  # free-standing numerals
    s = re.sub(r'<(\w*)>', r'\1', s)              # editorial supplement "mā<m>" -> "mām"
    # a TITUS sentence boundary falling inside a sandhi is written "vedā/hūtayo":
    # join the word and drop that boundary's danda; other boundaries become "|"
    s = re.sub(r'(\S*/\S*)\s*§', r'\1', s)
    s = re.sub(r'(?<=\w)/(?=\w)', '', s)
    s = s.replace('§', ' | ')
    if prose:                                   # AB/AA punctuation -> dandas
        s = re.sub(r'\s*[.;:?!]\s*', ' | ', s)
        s = s.replace(',', ' ')
    s = clean_iast(s).lower()
    s = re.sub(r'(?<=[aāiīuūeoṛ])3', '', s)        # pluti numeral ("saṃśaṃsatī3ṃ", "agnā3i")
    s = s.replace('(', ' ').replace(')', ' ')      # stray bracket (AA 5.2.1 "rajao)")
    s = re.sub(r'\s*(\|+)', r' \1', s)
    s = re.sub(r'(\|\|?)(\s*\|+)+', r'\1', s).strip()
    s = re.sub(r'^\|+\s*', '', s)
    return unicodedata.normalize('NFC', s)


def mk(ref, iast, vid):
    e = {'reference': '.'.join(map(str, ref)), 'sanskrit_iast': iast, 'meaning': to_deva(iast),
         'text': '', 'mandala': ref[0], 'hymn': ref[1]}
    if len(ref) > 2:
        e['verse'] = ref[2]
    e['vedaId'] = vid
    return e


def num(v):
    return int(re.match(r'\d+', v).group())


LEVELS = ['Chapter', 'Aranyaka', 'Adhyaya', 'Paragraph', 'Verse', 'Sentence']


def collect(name, ref_fn, prose, pre=None):
    """Group text by ref_fn(state); sentences joined with a danda (prose)."""
    state, order, buf = {}, [], {}
    for ev in events(name):
        if ev[0] == 'struct':
            if ev[1] in LEVELS:
                for lower in LEVELS[LEVELS.index(ev[1]) + 1:]:
                    state.pop(lower, None)
            if ev[1] == 'Chapter':
                state['_pn'] = 0
            if ev[1] == 'Paragraph':               # running count (TITUS AB repeats "Paragraph: 15" for 3.16)
                state['_pn'] = state.get('_pn', 0) + 1
                if name == 'ab' and ev[2].isdigit() and int(ev[2]) != state['_pn']:
                    print(f'  {name}: label Paragraph {ev[2]} is paragraph no. {state["_pn"]} of its chapter')
            state[ev[1]] = ev[2]
            if ev[1] == 'Sentence' and prose:
                r = ref_fn(state)
                if r in buf and buf[r]:
                    buf[r].append(' § ')
            continue
        if ev[0] == 'label':
            state['_label'] = ev[1]
            ref_fn(state, label=True)
            continue
        r = ref_fn(state)
        if r is None:
            continue
        if r not in buf:
            order.append(r)
            buf[r] = []
        buf[r].append(ev[1])
    return [(r, clean(' '.join(buf[r]), prose, pre)) for r in order]


def ab():
    st = {'adh': 0, 'k0': None}

    def ref(state, label=False):
        if label:
            m = re.search(r'ad.*?y[āa]ya\s+(\d+)', state['_label'])
            if m:
                a = int(m.group(1))
                assert a == st['adh'] + 1, state['_label']
                st['adh'], st['k0'] = a, (state['Chapter'], state['_pn'])
            return
        if 'Paragraph' not in state:
            return None
        ch, p = state['Chapter'], state['_pn']
        assert st['k0'][0] == ch, (ch, p)
        return (st['adh'], p - st['k0'][1] + 1)
    def pre(s):
        # "=(W)" variant flag; Aufrecht's round brackets (e.g. the whole of khandas
        # 7.10-7.11 = 32.9-32.10) mark later additions: keep the text, drop brackets
        return s.replace('=(W)', '').replace('(', ' ').replace(')', ' ')
    return [mk(r, s, 'aitareya_brahmana') for r, s in collect('ab', ref, True, pre)]


def aa():
    def ref(state, label=False):
        if label or 'Aranyaka' not in state:
            return None
        if state['Aranyaka'] == 'IV':           # Mahanamni verses: one unnumbered unit
            return (4, 1, 1)
        if 'Adhyaya' not in state:              # aranyaka title line
            return None
        # AA 2.5-2.7 are single khandas without a Paragraph level
        return (num(state['Aranyaka']), num(state['Adhyaya']), num(state.get('Paragraph', '1')))
    return [mk(r, s, 'aitareya_aranyaka') for r, s in collect('aa', ref, True)]


def vs():
    def ref(state, label=False):
        if label or 'Verse' not in state:
            return None
        return (num(state['Paragraph']), num(state['Verse']))
    def pre(s):                                 # TITUS VS writes avagraha as "(": "yò (smā́n"
        s = re.sub(r'=c5(?=ṣ)', '', s, flags=re.I)   # TITUS escape garble: =C5 = ṣ, =E6 = ḷ
        s = re.sub(r'=c5', 'ṣ', s, flags=re.I)
        s = re.sub(r'=e6', 'ḷ', s, flags=re.I)
        return re.sub(r'\((?=\w)', "'", s)
    return [mk(r, s, 'vajasaneyi_samhita') for r, s in collect('vs', ref, False, pre)]


def validate(entries, name):
    refs = [e['reference'] for e in entries]
    if len(set(refs)) != len(refs):
        raise SystemExit(f'{name}: duplicates')
    keys = [tuple(map(int, r.split('.'))) for r in refs]
    if keys != sorted(keys):
        raise SystemExit(f'{name}: out of order')
    probs = [(e['reference'], re.findall(r'.{0,12}(?:[<\[{\\#^~()*_/]|\d).{0,12}', e['sanskrit_iast'])[:2])
             for e in entries
             if not e['sanskrit_iast'].strip() or re.search(r'[<\[{\\#^~()*_/]|\d', e['sanskrit_iast'])
             or not re.search(r'[ऀ-ॿ]', e['meaning'])]
    if probs:
        raise SystemExit(f'{name}: problems {probs[:10]}')
    print(f'{name}: {len(entries)} entries, {refs[0]} .. {refs[-1]}; OK')


def write(entries, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)


TARGETS = {'ab': (ab, 'brahmanas/aitareya_brahmana.json'),
           'aa': (aa, 'aranyakas/aitareya_aranyaka.json'),
           'vs': (vs, 'vedas/vajasaneyi_samhita.json')}

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    for nm in [a for a in sys.argv[1:] if not a.startswith('--')] or TARGETS:
        fn, path = TARGETS[nm]
        ents = fn()
        validate(ents, nm)
        if not dry:
            write(ents, DATA + path)
