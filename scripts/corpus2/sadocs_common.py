"""Shared helpers for sanskritdocuments.org (.itx ITRANS) conversions.

Run with a Python that has `indic_transliteration` installed (e.g. the venv in
scratchpad/corpus/work/sadocs/venv).
"""
import re, sys, json, time, unicodedata, urllib.request, os
from indic_transliteration import sanscript

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts')
from titus_to_json import iast_to_devanagari  # noqa: E402

UA = 'rigved-corpus-research/1.0 (+https://github.com/iashris/rigved)'
BASE = 'https://sanskritdocuments.org/'


def fetch(path, dest_dir):
    """Download sanskritdocuments.org/<path> into dest_dir (cached)."""
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(path))
    if not os.path.exists(dest):
        req = urllib.request.Request(BASE + path, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        open(dest, 'wb').write(data)
        time.sleep(2)
    return open(dest, encoding='utf-8').read()


def header(itx):
    return {m.group(1).strip(): m.group(2).strip()
            for m in re.finditer(r'^%\s*([A-Za-z -]+?)\s*:\s*(.*)$', itx, re.M)}


VOW = 'aāiīuūṛṝḷeo'


def itx_to_iast(s):
    s = s.replace('\\-', '')
    s = re.sub(r'2?\{\\m\+\}', 'M', s)           # Taittiriya anusvara sign (ꣳ) -> M
    s = re.sub(r'\\[`\'"]', '', s)                # svara marks
    s = re.sub(r'\\.', '', s)                      # any other stray TeX escape
    s = s.replace('{}', '').replace('{', '').replace('}', '')
    s = re.sub(r'\([^)]*\)', ' ', s)              # editorial parentheses, e.g. "(ityupaniShat)", "o(4)m"
    s = re.sub(r'\.a 3o ', ' .a', s)               # "annAdo.a 3o ham" -> "annAdo .aham"
    # "2" after a nasalised vowel = anunasika sign; ".a 2.a" = avagraha
    s = re.sub(r'\.a\s+2(?:\.a)?\s*', '.a', s)
    s = re.sub(r'\s+2(?:\.a)?\s+', ' ', s)
    # pluta numerals 3/4
    s = re.sub(r'(?<=[aAiIuUeoM])\s+[34]\s+(?=[a-zA-Z])', '', s)
    s = re.sub(r'(?<=[aAiIuUeoM])\s?[34](?=[\s|])', '', s)
    s = re.sub(r'(?<=[aAiIuUeoM]) ?[34](?=[a-zA-Z])', '', s)
    s = s.replace(',', ' ')                        # ITRANS ligature breakers
    out = sanscript.transliterate(s, sanscript.ITRANS, sanscript.IAST)
    # Taittiriya orthography of anusvara before sibilants: -gś- / -ggs- / "ā g s" -> ṃ
    out = re.sub(r'([%s]) gg? (?=[sś])' % VOW, r'\1ṃ ', out)
    out = re.sub(r'([%s])gg(?=\s?[sś])' % VOW, r'\1ṃ', out)
    out = re.sub(r'([%s])g(?=[sś])' % VOW, r'\1ṃ', out)
    out = out.replace('ḻ', 'ḷ').replace('ṟ', 'r')
    out = re.sub(r'\s+', ' ', out).strip()
    out = re.sub(r'\s*(\|+)', r' \1', out)
    return unicodedata.normalize('NFC', out)


def entry(ref, iast, vid, text=''):
    parts = [int(x) for x in ref.split('.')]
    e = {'reference': ref, 'sanskrit_iast': iast, 'meaning': iast_to_devanagari(iast),
         'text': text, 'mandala': parts[0], 'hymn': parts[1]}
    if len(parts) > 2:
        e['verse'] = parts[2]
    e['vedaId'] = vid
    return e


def validate(entries, name):
    refs = [e['reference'] for e in entries]
    dup = {r for r in refs if refs.count(r) > 1}
    if dup:
        raise SystemExit(f'{name}: duplicate refs {sorted(dup)[:10]}')
    keys = [tuple(int(x) for x in r.split('.')) for r in refs]
    if keys != sorted(keys):
        bad = [refs[i] for i in range(1, len(keys)) if keys[i] < keys[i - 1]]
        raise SystemExit(f'{name}: out of order at {bad[:5]}')
    probs = []
    for e in entries:
        t = e['sanskrit_iast']
        if not t.strip():
            probs.append((e['reference'], 'empty'))
        if re.search(r'[<\[{\\#()]|//|\d|\^|~|ḻ|ṟ', t):
            probs.append((e['reference'], re.findall(r'.{0,10}(?:[<\[{\\#^~()]|//|\d).{0,10}', t)[:3]))
        if not re.search(r'[\u0900-\u097F]', e['meaning']):
            probs.append((e['reference'], 'no devanagari'))
    if probs:
        raise SystemExit(f'{name}: problems {probs[:10]}')
    print(f'{name}: {len(entries)} entries, {refs[0]} .. {refs[-1]}, '
          f'{sum(1 for e in entries if e["text"])} with English; OK')


def write(entries, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
