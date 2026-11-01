#!/usr/bin/env python3
"""Convert TITUS HTML pages (downloaded by titus_fetch.py) to repo JSON.

Usage: python3 -I titus_convert.py [ks] [jub] [kathar] [kathbr]

  ks      Kathaka Samhita, sthanakas 1-40 (sthanaka.anuvaka)
  ksa     Kathaka Samhita Asvamedha grantha (TITUS "KS-V"), KSA 1-13 (sthanaka.anuvaka)
  manb    Mantra-Brahmana (prapathaka.khanda.mantra)
  dab     Devatadhyaya-Brahmana (khanda.verse)
  vb      Vamsa-Brahmana (khanda.paragraph)
  jub     Jaiminiya Upanisad Brahmana (adhyaya.khanda.section, = Oertel's numbering)
  kathar  Kathaka Aranyaka, Brahmana sections, Witzel ed. (chapter.mantra, e.g. 2.1, 3.240)
  kathbr  Kathaka Brahmana remnants (Caland), brahmana.chapter.paragraph

Only text spans of the main font size (iov*16) are used; size-12 spans are the
edition's footnote readings and are skipped, as are ioc* comments and h8/h9 page/line
markers.
"""
import json
import os
import re
import sys
import unicodedata

from bs4 import BeautifulSoup

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts')
from titus_to_json import iast_to_devanagari  # noqa: E402

REPO = '/Users/iashris/Desktop/rigved'
WORK = os.environ.get("TITUS_WORK", "/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/"
       "c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/titus")

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6}

ACCENTED = {
    'á': 'a', 'à': 'a', 'é': 'e', 'è': 'e', 'í': 'i', 'ì': 'i', 'ó': 'o', 'ò': 'o',
    'ú': 'u', 'ù': 'u', 'ŕ': 'r', 'ĺ': 'l', 'ǘ': 'ü',
    'Á': 'A', 'À': 'A', 'É': 'E', 'È': 'E', 'Í': 'I', 'Ì': 'I', 'Ó': 'O', 'Ò': 'O',
    'Ú': 'U', 'Ù': 'U',
}


def clean_iast(s):
    s = unicodedata.normalize('NFC', s)
    s = s.replace(' ', ' ')
    s = re.sub(r'\{[^}]*\}', '', s)
    for k, v in ACCENTED.items():
        s = s.replace(k, v)
    # remaining combining accents (acute, grave, double acute, vertical line above)
    s = re.sub('[̀́̋̍̎́̀]', '', s)
    # aspirates
    s = s.replace('ʰ', 'h')
    # vocalic r/l (with optional macron)
    s = s.replace('r̥̄', 'ṝ').replace('r̥̄', 'ṝ')
    s = s.replace('r̥', 'ṛ').replace('l̥', 'ḷ').replace('ŀ̥', 'ḷ').replace('ŀ', 'ḷ')
    s = s.replace('ghṛtenānaktI', 'ghṛtenānakti')  # KS 21.8 typo in TITUS
    s = s.replace('žHhutir', 'āhutir')  # KS 27.1 encoding garble (= āhutir)
    s = s.replace('R̥', 'Ṛ')
    # nasalisation, jihvamuliya/upadhmaniya
    s = s.replace('m̐', 'ṃ').replace('ṁ', 'ṃ')
    s = s.replace('ẖ', 'ḥ').replace('ḫ', 'ḥ').replace('ẖ', 'ḥ').replace('ḫ', 'ḥ')
    # avagraha
    s = s.replace('ʼ', "'").replace('’', "'").replace('‘', "'")
    # TITUS sandhi-break marker, footnote stars, parenthesised editorial additions
    s = s.replace('_', '')
    s = s.replace('*', '')
    s = re.sub(r'\(\s*[^)]*\)', '', s)  # e.g. "juṣṭam (ṃ)" - editorial alternative
    # JUB editorial brackets: keep the supplied letters inside a word ("e[va]" -> "eva"),
    # drop free-standing bracketed insertions/deletions ("[sa] sa" -> "sa")
    s = re.sub(r'(?<=\w)\[([^\]\s]*)\]|\[([^\]\s]*)\](?=\w)', lambda m: m.group(1) or m.group(2) or '', s)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = s.replace('{', '').replace('}', '')
    s = re.sub(r'\.{2,}|…', ' ', s)       # ellipses marking omitted/illegible text
    s = re.sub(r'(?<!\w)-+|-+(?!\w)', ' ', s)  # free-standing dashes (keep "dve-dve")
    s = re.sub(r'\s[:!](?=\s|$)', ' ', s)  # free-standing colon / exclamation separators
    # punctuation -> dandas
    s = s.replace('\\\\', ' || ').replace('\\', ' | ')
    s = re.sub(r'//', ' || ', s)
    s = s.replace('/', ' | ')
    s = re.sub(r'\s\.(?=\s|$)', ' | ', s)  # KathAr sentence stops " ."
    s = re.sub(r'\s,(?=\s|$)', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\|\s*\|', '||', s)
    s = re.sub(r'(\|\|?)(\s*\|+)+', r'\1', s)  # collapse runs of dandas
    s = re.sub(r'\|+\s*\d+\s*\|+', ' || ', s)  # anuvaka numbers "| 1 |"
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'(\|\|?)(\s*\|+)+', r'\1', s)
    s = re.sub(r'^\|+\s*', '', s)
    return unicodedata.normalize('NFC', s.strip())


def to_deva(iast):
    d = iast_to_devanagari(iast)
    d = d.replace('||', '॥').replace('|', '।')
    d = d.replace("'", 'ऽ')  # avagraha
    return unicodedata.normalize('NFC', d)


def num(v):
    """Leading integer of a TITUS label: "24a", "24a1", "1b" -> 24 / 24 / 1 (sub-units are merged)."""
    return int(re.match(r'\d+', v).group())


def events(name, extra_text_ids=(), only_ids=None, relabel=None):
    """Yield ('struct', label, value) / ('text', s) from all span-id pages of a text.

    relabel: {(key, value, nth_occurrence): new_value} to correct TITUS label typos.
    """
    seen = {}
    d = os.path.join(WORK, 'raw', name)
    for f in sorted(os.listdir(d)):
        html = open(os.path.join(d, f), encoding='utf-8').read()
        if not re.search(r'<span id="?h[1-5]\b', html):
            continue  # stale old-format pages (kathbcal 008-021 duplicate 001)
        soup = BeautifulSoup(html, 'html.parser')
        for sp in soup.find_all('span', id=True):
            i = sp['id']
            if re.fullmatch(r'h[2-7]', i):
                t = sp.get_text(' ', strip=True)
                if ':' in t:
                    k, v = t.split(':', 1)
                    k, v = k.strip(), v.strip()
                    seen[(k, v)] = seen.get((k, v), 0) + 1
                    v = (relabel or {}).get((k, v, seen[(k, v)]), v)
                    yield ('struct', k, v)
            elif (i in only_ids) if only_ids else (
                    (i.startswith('iov') and i.endswith('16') and not i.startswith('iovc')) or i in extra_text_ids):
                parts = []
                for c in sp.children:
                    parts.append(c.get_text() if hasattr(c, 'get_text') else str(c))
                t = ' '.join(p.strip() for p in parts if p.strip())
                # footnote apparatus opened inside a text span ("word{FN emended. Ed.: ")
                t = re.sub(r'\{FN[^}]*\}', '', t)
                t = re.sub(r'\{FN.*$', '', t)
                if t.strip():
                    yield ('text', t)


def build(name, levels, ref_fn, veda_id, extra_text_ids=(), only_ids=None, relabel=None):
    """levels: struct keys tracked; ref_fn(state)->tuple of ints or None (skip)."""
    state = {}
    out, cur_ref, buf = [], None, []

    def flush():
        if cur_ref is not None and buf:
            s = clean_iast(' '.join(buf))
            if s:
                out.append((cur_ref, s))

    for ev in events(name, extra_text_ids, only_ids, relabel):
        if ev[0] == 'struct':
            k, v = ev[1], ev[2]
            if k in levels:
                state[k] = v
                # reset lower levels
                for lower in levels[levels.index(k) + 1:]:
                    state.pop(lower, None)
            continue
        ref = ref_fn(state)
        if ref is None:
            continue
        if ref != cur_ref:
            flush()
            cur_ref, buf = ref, []
        buf.append(ev[1])
    flush()

    entries, seen = [], set()
    for ref, s in out:
        r = '.'.join(map(str, ref))
        if r in seen:
            raise SystemExit(f'{veda_id}: duplicate reference {r}')
        seen.add(r)
        e = {'reference': r, 'sanskrit_iast': s, 'meaning': to_deva(s), 'text': '',
             'mandala': ref[0], 'hymn': ref[1]}
        if len(ref) > 2:
            e['verse'] = ref[2]
        e['vedaId'] = veda_id
        entries.append(e)
    return entries


def write(entries, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f'wrote {path}: {len(entries)} entries')


def _ks(part, veda_id):
    # TITUS text "KS" = sthanakas 1-40; "KS-V" = Asvamedha grantha (KSA 1-13)
    def ref(st):
        if st.get('Text') != part or 'Sthanaka' not in st or 'Anuvaka' not in st:
            return None
        return (num(st['Sthanaka']), num(st['Anuvaka']))
    return build('ks', ['Text', 'Sthanaka', 'Anuvaka'], ref, veda_id)


def ks():
    return _ks('KS', 'kathaka_samhita')


def ksa():
    return _ks('KS-V', 'kathaka_samhita_asvamedha')


def manb():
    # prapathaka.khanda.mantra; only the samhitapatha line (iovpl16): iovps16 is the
    # padapatha, iovpal16/iovpbl16/iovmcl16 are variant readings, ioc16 German headings
    def ref(st):
        try:
            return (num(st['Chapter']), num(st['Paragraph']), num(st['Verse']))
        except (KeyError, ValueError, AttributeError):
            return None
    return build('manb', ['Chapter', 'Paragraph', 'Verse'], ref, 'mantra_brahmana', only_ids=('iovpl16',))


def dab():
    # khanda.verse
    def ref(st):
        try:
            return (num(st['Paragraph']), num(st['Verse']))
        except (KeyError, ValueError, AttributeError):
            return None
    return build('dab', ['Paragraph', 'Verse'], ref, 'devatadhyaya_brahmana', only_ids=('iovpl16', 'iovml16'))


def vb():
    # khanda.paragraph (TITUS labels the numbered paragraphs "Sentence")
    def ref(st):
        try:
            return (num(st['Paragraph']), num(st['Sentence']))
        except (KeyError, ValueError, AttributeError):
            return None
    # TITUS labels 1.8 as a second "9" (1.7 is followed by 9, 9, 10)
    return build('vb', ['Paragraph', 'Sentence'], ref, 'vamsa_brahmana', only_ids=('iovpl16',),
                 relabel={('Sentence', '9', 1): '8'})


def jub():
    def ref(st):
        try:
            return (num(st['Chapter']), num(st['Paragraph']), num(st['Verse']))
        except (KeyError, ValueError, AttributeError):
            return None
    return build('jub', ['Chapter', 'Paragraph', 'Verse'], ref, 'jaiminiya_upanisad_brahmana')


def kathar():
    def ref(st):
        try:
            # sub-mantras "67a", "101b" belong to mantra 67 / 101
            return (ROMAN[st['Chapter']], int(re.match(r'\d+', st['Mantra']).group()))
        except (KeyError, ValueError, AttributeError):
            return None
    return build('katharbr', ['Chapter', 'Paragraph', 'Mantra'], ref, 'kathaka_aranyaka')


def kathbr():
    def ref(st):
        try:
            b = num(st['Brahmana'])
            ch = st.get('Chapter', '1')
            m = re.fullmatch(r'\(?(\d+)\)?(?:\((\d+)\))?', ch)
            c = int(m.group(2) or m.group(1))  # "3(5)": running number in parentheses
            return (b, c, int(st.get('Paragraph', '1')))
        except (KeyError, ValueError, AttributeError):
            return None
    return build('kathbcal', ['Brahmana', 'Chapter', 'Paragraph'], ref, 'kathaka_brahmana',
                 extra_text_ids=('iovpl12',))


JOBS = {
    'ks': (ks, f'{REPO}/public/data/vedas/kathaka_samhita.json'),
    'ksa': (ksa, f'{REPO}/public/data/vedas/kathaka_samhita_asvamedha.json'),
    'manb': (manb, f'{REPO}/public/data/brahmanas/mantra_brahmana.json'),
    'dab': (dab, f'{REPO}/public/data/brahmanas/devatadhyaya_brahmana.json'),
    'vb': (vb, f'{REPO}/public/data/brahmanas/vamsa_brahmana.json'),
    'jub': (jub, f'{REPO}/public/data/brahmanas/jaiminiya_upanisad_brahmana.json'),
    'kathar': (kathar, f'{REPO}/public/data/aranyakas/kathaka_aranyaka.json'),
    'kathbr': (kathbr, f'{REPO}/public/data/brahmanas/kathaka_brahmana.json'),
}

if __name__ == '__main__':
    for job in sys.argv[1:] or list(JOBS):
        fn, path = JOBS[job]
        write(fn(), path)
