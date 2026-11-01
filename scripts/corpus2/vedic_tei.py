"""GRETIL TEI sources -> JSON for the `vedic` task.

Texts: Paippalada Samhita, Sankhayana Aranyaka, Nirukta, Rgvidhana, and six minor
Upanishads (Garbha, Brahmabindu, Nadabindu, Atharvasiras, Kaivalya, Sivasamkalpa).
Run with no args for all, or name any of: paippalada sankhayana nirukta rgvidhana upanishads
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vedic_common import GRETIL, make_entry, norm_space, slashes_to_dandas, validate, write  # noqa: E402

TEI = os.path.join(GRETIL, 'tei')
NS = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
DROP = {'note', 'trailer', 'head', 'orig'}


def tag(el):
    return el.tag.replace(NS, '')


def text_of(el, drop=DROP):
    """Plain text of an element: drops notes/trailers/heads, keeps <reg> of <choice>,
    keeps <sic> and <corr> content (in these files they are standalone markers),
    <lb/> becomes a newline."""
    out = []

    def walk(e):
        if e.text and tag(e) not in drop:
            out.append(e.text)
        for c in e:
            if tag(c) in drop:
                pass
            elif tag(c) == 'lb':
                out.append('\n')
            else:
                walk(c)
            if c.tail:
                out.append(c.tail)
    walk(el)
    return ''.join(out)


def body(fname):
    root = ET.parse(os.path.join(TEI, fname)).getroot()
    return root.find(f'.//{NS}body')


# ---------------------------------------------------------------- Paippalada
def ps_clean_line(t):
    t = norm_space(t)
    t = re.sub(r'\[[^\]]*(\]|$)', ' ', t)               # "[Bhatt. ...]", "[see 1d ...]"
    t = re.sub(r'(^|\|\|)\s*Bhatt\.[^\]]*\]', r'\1', t)  # tail of a note opened on prev line
    t = re.sub(r'\(⟨[^)]*\)', ' ', t)                      # "(⟨ malvaṃ?)" variant notes
    t = re.sub(r'\(\s*·[\s·]*\)', ' ', t)                 # "(· ·)" lacuna
    t = re.sub(r'\|\|\s*anuvāka \d+\s*\|+', '||', t)        # leaked anuvāka trailer
    t = re.sub(r"[+*](?=')", '', t)                       # "+'", "*'": editorial avagraha
    t = t.replace('?', '').replace('ü', 'u')              # doubt marks; "titaünā" diaeresis
    t = t.replace('l̥', 'ḷ').replace('r̥', 'ṛ')
    t = t.replace('((…)', '…').replace('(…)', '…').replace('(...)', '…')
    return norm_space(t)


def paippalada():
    b = body('sa_paippalAdasaMhitA.xml')
    entries = []
    pending = []
    for lg in b.iter(f'{NS}lg'):
        m = re.fullmatch(r'PS_(\d+)\.(\d+)\.(\d+)', lg.get(XID, ''))
        if not m:
            raise SystemExit(f'unexpected lg id {lg.get(XID)}')
        lines = [ps_clean_line(text_of(l)) for l in lg.findall(f'{NS}l')]
        s = ''
        for ln in lines:
            if not ln:
                continue
            if s.endswith('-'):          # word broken across padas: "nama-" + "s..."
                s = s[:-1] + ln
            else:
                s = (s + ' ' + ln) if s else ln
        s = re.sub(r'-\s*\|\s*-', ' | ', s)        # "upa- | -imāṃ" (19.9.5)
        s = s.replace('-', ' ')                      # hiatus hyphens: "svāhā-idaṃ"
        s = re.sub(r'\(([^()]*)\)', r'\1', s)       # editor-supplied words: "(yā)"
        s = s.replace('(', ' ').replace(')', ' ')    # unmatched paren typo (9.21.2e)
        s = re.sub(r'\s+(…)', r' \1', s)
        s = re.sub(r'\|\|(\s*\|\|)+', '||', norm_space(s))   # "… || ||" (16.77.10)
        if s.strip(' |…') == '':
            # whole verse elided as "(…) ||" with a note "PS x.y.z is repeated"
            notes = ' '.join(norm_space(''.join(n.itertext())) for n in lg.iter(f'{NS}note'))
            rm = re.search(r'PS (\d+\.\d+\.\d+) is repeated(.*)', notes)
            if rm and not rm.group(2).strip():
                pending.append((len(entries), rm.group(1)))
            else:
                print(f'   omitted PS {".".join(m.groups())}: elided verse, note: {notes}')
                continue
        entries.append(make_entry(m.groups(), s, 'paippalada_samhita'))
    byref = {e['reference']: e for e in entries}
    for idx, src in pending:
        e = entries[idx]
        e2 = make_entry(e['reference'].split('.'), byref[src]['sanskrit_iast'], 'paippalada_samhita')
        print(f'   PS {e["reference"]}: elided repeat filled from PS {src}')
        entries[idx] = e2
    path = write('public/data/vedas/paippalada_samhita.json', entries)
    validate(path, '(Paippalada: 20 kandas)')


# ---------------------------------------------------------------- Sankhayana Aranyaka
def sankhayana():
    b = body('sa_zaGkhAyana-AraNyaka.xml')
    entries = []
    for p in b.iter(f'{NS}p'):
        t = text_of(p)
        m = re.match(r'\s*ŚĀ\s+(\d+),(\d+)\s*(.*)', t, re.S)
        if not m:
            print('   skip (unnumbered):', norm_space(t)[:90])
            continue
        txt = m.group(3).replace('+', '')   # '+' marks emendations in this file
        txt = re.sub(r'=\s*[A-Z]+\s*\d+(?:,\d+)*', ' ', txt)   # parallels "= KU 1,1"
        txt = re.sub(r'\|\|\s*\d+\s*\|\|', '||', txt)          # inline verse nos (adhy. 12)
        txt = re.sub(r'\([^()]*\)', ' ', txt)                   # variant "(laḥ)"
        txt = txt.replace('...', '…').replace(' - ', ' ').replace('-', '')
        txt = txt.replace('ü', 'u').replace('ṁ', 'ṃ').replace('l̥', 'ḷ').replace('r̥', 'ṛ')
        txt = txt.lower().replace('. ', ' | ')                   # stray caps "Suryasya"; stray period (7.19)
        txt = slashes_to_dandas(txt)
        entries.append(make_entry(m.group(1, 2), txt, 'sankhayana_aranyaka'))
    path = write('public/data/aranyakas/sankhayana_aranyaka.json', entries)
    validate(path, '(SA: 15 adhyayas)')


# ---------------------------------------------------------------- Nirukta
def clean_dotted(s):
    """Nirukta/Rgvidhana style: words joined by dots; strip apparatus."""
    s = re.sub(r'\([^()]*\)', ' ', s)          # sources "(ṛV.X,84,2)", variants "(yugapad.Bh)"
    s = re.sub(r'\[[^\]]*\]', ' ', s)          # page numbers "[177]", variants "[etāni.Bh]"
    s = s.replace('``', ' ').replace("''", ' ').replace('$', ' ')
    s = s.replace('.', ' ')
    return s


# The Tokunaga input encodes some inflected forms as stem + case digit (+ p plural /
# d dual), e.g. "dhātu1p" = dhātavaḥ, "kanyaka1d" = kanyake, "deva5bhyo" = devebhyo.
NIR_CODES = [
    (r'(\w*?)u1p\b', lambda m: m.group(1) + 'avaḥ'),
    (r'(\w*?)i[18]p\b', lambda m: m.group(1) + 'ayaḥ'),
    (r'\btanū1p\b', lambda m: 'tanvaḥ'),
    (r'(\w*?)as[12]p\b', lambda m: m.group(1) + 'āṃsi'),
    (r'(\w*?)is[12]p\b', lambda m: m.group(1) + 'īṃṣi'),
    (r'(\w*?)us[12]p\b', lambda m: m.group(1) + 'ūṃṣi'),
    (r'(\w*?)iṣ1p\b', lambda m: m.group(1) + 'īṃṣi'),
    (r'\bbhāj1p\b', lambda m: 'bhājaḥ'),
    (r'\bpitr1p\b', lambda m: 'pitaraḥ'),
    (r'\bgo1p\b', lambda m: 'gāvaḥ'),
    (r'\bahar6p\b', lambda m: 'ahnām'),
    (r'(\w*?)a1p\b', lambda m: m.group(1) + 'āḥ'),
    (r'(\w*?)[aā]1d\b', lambda m: m.group(1) + 'e'),
    (r'(\w*?)a2d\b', lambda m: m.group(1) + 'au'),
    (r'(\w*?)a2na\b', lambda m: m.group(1) + 'ena'),
    (r'(\w*?)a[45](bhy\w*)', lambda m: m.group(1) + 'e' + m.group(2)),
]


NIR_SG = {
    'a': {1: 'aḥ', 2: 'am', 3: 'ena', 4: 'āya', 5: 'āt', 6: 'asya', 7: 'e', 8: 'a'},
    'ā': {1: 'ā', 2: 'ām', 3: 'ayā', 4: 'āyai', 5: 'āyāḥ', 6: 'āyāḥ', 7: 'āyām', 8: 'e'},
    'ī': {1: 'ī', 2: 'īm', 3: 'yā', 4: 'yai', 5: 'yāḥ', 6: 'yāḥ', 7: 'yām', 8: 'i'},
    'i': {1: 'iḥ', 2: 'im', 3: 'inā', 4: 'aye', 5: 'eḥ', 6: 'eḥ', 7: 'au', 8: 'e'},
    'u': {1: 'uḥ', 2: 'um', 3: 'unā', 4: 'ave', 5: 'oḥ', 6: 'oḥ', 7: 'au', 8: 'o'},
    'ṛ': {1: 'ā', 2: 'āram', 3: 'rā', 4: 're', 5: 'uḥ', 6: 'uḥ', 7: 'ari', 8: 'aḥ'},
}
NIR_RELATION = ('pitṛ', 'mātṛ', 'duhitṛ', 'jāmātṛ', 'bhrātṛ')   # acc. -aram
NIR_NEUT_AS = ('tamas', 'retas', 'śiras', 'yaśas', 'mahas', 'tapas', 'tejas', 'okas',
               'vacas', 'andhas', 'apas', 'havis', 'barhis', 'sarpis', 'barbis', 'āyus',
               'cakṣus', 'jyotis', 'yajus', 'chandas', 'manas')
NIR_IRREG = {'rājan4': 'rājñe', 'rājan6': 'rājñaḥ', 'nāman3': 'nāmnā', 'sarvanāman3': 'sarvanāmnā',
             'mūrdhan2': 'mūrdhānam', 'aryaman1': 'aryamā', 'aryaman6': 'aryamṇaḥ',
             'pūsan1': 'pūṣā', 'pūsan3': 'pūṣṇā', 'mātariśvan1': 'mātariśvā', 'snāvan5': 'snāvnaḥ',
             'keśin1': 'keśī', 'peśin1': 'peśī', 'muñjavat1': 'muñjavān', 'sarasvat1': 'sarasvān',
             'ekapād1': 'ekapāt', 'svar1': 'svaḥ', 'saṃdṛś1': 'saṃdṛk', 'dhī2': 'dhiyam',
             'āśis1': 'āśīḥ', 'ahar5': 'ahnaḥ', 'go7': 'gavi', 'kavir2': 'kavim',
             'katukiman3': 'kaṭukimnā'}


def nir_inflect(stem, case):
    key = f'{stem}{case}'
    if key in NIR_IRREG:
        return NIR_IRREG[key]
    for st in ('as', 'is', 'us'):
        if stem.endswith(st) and case in (1, 2, 3, 8):
            base = stem[:-2]
            neut = stem.endswith(NIR_NEUT_AS)
            v = st[0]
            if case == 3:
                return base + st[0] + 'sā' if v == 'a' else base + v + 'ṣā'
            if neut or v != 'a':
                return base + v + 'ḥ'
            return base + ('āḥ' if case == 1 else 'asam' if case == 2 else 'aḥ')
    last = stem[-1]
    if last == 'ṛ' and case == 2 and stem.endswith(NIR_RELATION):
        return stem[:-1] + 'aram'
    if last in NIR_SG:
        return stem[:-1] + NIR_SG[last][case]
    return None


def nirukta_decode(s, ref):
    for pat, rep in NIR_CODES:
        s = re.sub(pat, rep, s)

    def sg(m):
        out = nir_inflect(m.group(1), int(m.group(2)))
        return out if out else m.group(0)
    s = re.sub(r'([^\W\d_]+)([1-8])\b', sg, s)
    left = re.findall(r'\w*[^\W\d_]\d\w*', s)
    if left:
        print(f'   nirukta {ref}: undecodable digit forms, digit dropped: {left}')
        s = re.sub(r'(?<=[^\W\d_])\d+', '', s)
    return s


def nirukta():
    b = body('sa_yAska-nirukta.xml')
    raw = text_of(b)
    # a few lines carry a second "a,b:" label mid-line ("... iti 1,14:santy ...")
    raw = re.sub(r'[\s.](\d+,\d+:)', r'\n\1', raw)
    units = {}
    order = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'(\d+),(\d+):\s*(.*)', line)
        if not m:
            raise SystemExit(f'unnumbered nirukta line: {line[:100]}')
        key = (int(m.group(1)), int(m.group(2)))
        if key not in units:
            if order and key < order[-1]:
                raise SystemExit(f'nirukta order break at {key}')
            units[key] = []
            order.append(key)
        units[key].append(m.group(3))
    entries = []
    for key in order:
        ref = f'{key[0]}.{key[1]}'
        # join lines with a line-break marker first, so brackets spanning lines are caught
        s = ' / '.join(units[key])
        s = re.sub(r'\(([^()]|\(\w*\))*\)', ' ', s)    # "(ṛV.X,84,2)", "(yugapad.Bh)"
        s = re.sub(r'\[[^\]]*\]', ' ', s)            # "[177]", "[etāni.Bh]", "[ḍ p 726: ...]"
        s = re.sub(r'\b\d+,\d+\b', ' ', s)            # bare refs "(2,5)" leftovers "2,5"
        s = re.sub(r'(^|[\s/.])\d+(?=[\s/.]|$)', r'\1', s)  # lone numbers "| 2 iti"
        s = s.replace('``', ' ').replace("''", ' ')
        for ch in '$`\\@#()[]':
            s = s.replace(ch, ' ')
        s = s.replace('.', ' ')
        s = re.sub(r'\s*/\s*(/\s*)*', ' / ', s)
        s = re.sub(r'\bCf\s+\S+', ' ', s)          # leftover "Cf ṇir", "Cf KB"
        s = s.replace(' - ', ' ').replace('rC', 'ṛk').replace('Vṛkaś', 'vṛkaś').replace(';', ' |')
        s = nirukta_decode(s, ref)
        parts = [norm_space(x).strip(' |,') for x in s.split(' / ')]
        parts = [x for x in parts if x]
        if not parts:
            print('   empty khanda skipped:', key)
            continue
        txt = ' | '.join(parts) + ' ||'
        txt = re.sub(r'\s*\|\s*\|\s*\|\|$', ' ||', txt)
        entries.append(make_entry(key, txt, 'nirukta'))
    path = write('public/data/other/nirukta.json', entries)
    validate(path, '(Nirukta: 12 adhyayas + parisista 13-14)')


# ---------------------------------------------------------------- Rgvidhana
def rgvidhana():
    b = body('sa_RgvidhAna.xml')
    entries = []
    for lg in b.iter(f'{NS}lg'):
        m = re.fullmatch(r'RgV_(\d+)\.(\d+)\.(\d+)', lg.get(XID, ''))
        if lg.get(XID) is None:
            print('   rgvidhana: skip unnumbered (scribal colophon):', norm_space(text_of(lg))[:70])
            continue
        if not m:
            raise SystemExit(f'unexpected lg id {lg.get(XID)}')
        s = ' '.join(text_of(l) for l in lg.findall(f'{NS}l'))
        # source typos: ']' for ṭ ("upatiṣ]hati", "ṣa]"), ';' for ṣ ("paritu;syati")
        s = s.replace('upatiṣ]hati', 'upatiṣṭhati').replace('ṣa].', 'ṣaṭ.')
        s = s.replace('paritu;syati', 'parituṣyati').replace(';', '.')
        s = re.sub(r'\.E\b', '.', s)      # stray end marker "E"
        s = clean_dotted(s)               # also drops the bracketed passage in 3.4.18
        entries.append(make_entry(m.groups(), slashes_to_dandas(s), 'rgvidhana'))
    path = write('public/data/other/rgvidhana.json', entries)
    validate(path, '(Rgvidhana: 4 adhyayas)')


# ---------------------------------------------------------------- minor Upanishads
def split_numbered(text, marker_re):
    """Split running text at verse-number markers; returns [(n, text)]."""
    parts = re.split(marker_re, text)
    tail = norm_space(parts[-1])
    out = [(int(parts[i + 1]), parts[i]) for i in range(0, len(parts) - 1, 2)]
    return out, tail


def upanishad_marked(fname, marker_re, out_name, skip_re=None, keep_tail=False):
    b = body(fname)
    # mark l elements that are inside lg so standalone <l> blocks are also caught
    inlg = set()
    for lg in b.iter(f'{NS}lg'):
        for l in lg.iter(f'{NS}l'):
            inlg.add(l)
    chunks = []
    for el in b.iter():
        t = tag(el)
        if t in ('p', 'lg') or (t == 'l' and el not in inlg):
            txt = norm_space(text_of(el))
            if skip_re and re.fullmatch(skip_re, txt):
                print(f'   {out_name}: skip block: {txt[:70]}')
                continue
            chunks.append(txt)
    text = ' '.join(chunks)
    pairs, tail = split_numbered(text, marker_re)
    if tail:
        if keep_tail:
            print(f'   {out_name}: trailing unnumbered text kept as next unit: {tail[:70]}')
            pairs.append((pairs[-1][0] + 1, tail))
        else:
            raise SystemExit(f'{out_name}: unnumbered trailing text: {tail[:150]}')
    return pairs


def finish_upa(name, pairs):
    vid = f'{name}_upanishad'
    entries = []
    for n, txt in pairs:
        txt = re.sub(r'\[[^\]]*\]', ' ', txt)       # bracketed variant readings
        txt = slashes_to_dandas(txt)
        if not txt.rstrip().endswith('|'):
            txt += ' ||'
        txt = re.sub(r'\|\s*\|\|$', '||', txt)
        txt = re.sub(r'\|\|\s*\|\|$', '||', txt)
        entries.append(make_entry([n], txt, vid))
    path = write(f'public/data/upanishads/{vid}.json', entries)
    validate(path)


def upanishads():
    # Garbha: "... || GarUp_n"
    pairs = upanishad_marked('sa_garbhopaniSad.xml', r'\|\|\s*GarUp_(\d+)', 'garbha',
                             skip_re=r'Garbhopaniṣat', keep_tail=True)
    finish_upa('garbha', pairs)
    # Brahmabindu / Nadabindu: "... // BrbUp_n //"
    pairs = upanishad_marked('sa_brahmabindUpaniSad.xml', r'//\s*BrbUp_(\d+)\s*//', 'brahmabindu')
    finish_upa('brahmabindu', pairs)
    pairs = upanishad_marked('sa_nAdabindUpaniSad.xml', r'//\s*NbiUp_(\d+)\s*//', 'nadabindu',
                             skip_re=r'Nādabindūpaniṣat')
    finish_upa('nadabindu', pairs)
    # Kaivalya: "... ||n||"; the "||23*||" line completes verse 23
    b = body('sa_kaivalyopaniSad.xml')
    inlg = {l for lg in b.iter(f'{NS}lg') for l in lg.iter(f'{NS}l')}
    chunks = []
    skip = re.compile(r'\[Oṃ bhadraṃ.*|\[iti\] prathamaḥ khaṇḍaḥ \|\||'
                      r'ity atharvavede kaivalyopaniṣat samāptā \|\||oṃ tat sat')
    for el in b.iter():
        t = tag(el)
        if t in ('p', 'lg') or (t == 'l' and el not in inlg):
            txt = norm_space(text_of(el))
            if skip.fullmatch(txt):
                print(f'   kaivalya: skip block: {txt[:70]}')
                continue
            chunks.append(txt)
    text = ' '.join(chunks)
    # lines numbered "||14*||" / "||23*||" complete the preceding verse 14 / 23
    text = re.sub(r'\|\|(\d+)\|\|(.*?)\|\|\1\*\|\|', r'|\2||\1||', text)
    text = text.replace('-', '')                      # "śraddhā-bhakti-dhyāna-yogād"
    pairs, tail = split_numbered(text, r'\|\|(\d+)\|\|')
    if tail:
        raise SystemExit(f'kaivalya tail: {tail[:100]}')
    finish_upa('kaivalya', pairs)
    # Atharvasiras: <p xml:id="SirUp_n">
    b = body('sa_zira-upaniSad.xml')
    pairs = []
    for p in b:
        m = re.fullmatch(r'SirUp_(\d+)', p.get(XID, ''))
        if not m:
            print('   atharvasiras: skip unnumbered block:', norm_space(text_of(p))[:70])
            continue
        t = text_of(p).replace('ity atharvavede śiraupaniṣat samāptā', '')
        pairs.append((int(m.group(1)), t))
    finish_upa('atharvasiras', pairs)
    # Sivasamkalpa: <lg xml:id="ŚSU_n">, accents in <orig> dropped, <reg> kept
    b = body('sa_zivasaMkalpopaniSad.xml')
    pairs = []
    for lg in b.iter(f'{NS}lg'):
        m = re.fullmatch(r'ŚSU_(\d+)', lg.get(XID, ''))
        if not m:
            raise SystemExit(f'sivasamkalpa: unexpected lg id {lg.get(XID)}')
        s = ' | '.join(norm_space(text_of(l)).strip(' |') for l in lg.findall(f'{NS}l'))
        pairs.append((int(m.group(1)), s))
    finish_upa('sivasamkalpa', pairs)


JOBS = {'paippalada': paippalada, 'sankhayana': sankhayana, 'nirukta': nirukta,
        'rgvidhana': rgvidhana, 'upanishads': upanishads}

if __name__ == '__main__':
    for name in (sys.argv[1:] or JOBS):
        JOBS[name]()
