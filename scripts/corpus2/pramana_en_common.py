"""Shared Pramāṇa (indike.org/pramana) fetch helper: polite (1 req/s, one at a time), disk-cached, retrying."""

import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://indike.org/pramana/api"
UA = "rigved-corpus-research/1.0 (+https://github.com/iashris/rigved)"
WORK = "/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/pramana_en"
CACHE = os.path.join(WORK, "cache")
os.makedirs(CACHE, exist_ok=True)
REPO = "/Users/iashris/Desktop/rigved"
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "scripts", "corpus2"))


def get(path, **params):
    params = {k: v for k, v in params.items() if v is not None}
    url = f"{API}/{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    f = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json")
    if os.path.exists(f):
        return json.load(open(f))
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.load(r)
            json.dump(data, open(f, "w"))
            time.sleep(1.1)
            return data
        except Exception as e:  # noqa: BLE001
            print("retry", url, e, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"failed: {url}")


def segments(path, **kw):
    """All segments of a path, following the `next` cursor."""
    out, after = [], None
    while True:
        d = get(f"segments/{path}", limit=kw.pop("limit", 1000) if not kw.get("aligned") else 300, after=after, **kw)
        out += d.get("segments") or d.get("items") or []
        after = d.get("next")
        if not after:
            return out

import re  # noqa: E402

ROMAN = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}


def rom(r):
    t = 0
    for i, c in enumerate(r):
        t += -ROMAN[c] if i + 1 < len(r) and ROMAN[r[i + 1]] > ROMAN[c] else ROMAN[c]
    return t


def clean_en(t):
    """Strip OCR/markdown residue from an English paragraph, keep verse line breaks."""
    t = t.replace('[*]', '')
    t = re.sub(r'(?<!\w)[_*]+|[_*]+(?!\w)', '', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r' *\n *', '\n', t)
    t = re.sub(r' ([,;:.!?])', r'\1', t)
    return t.strip()


def is_heading(seg, nxt_is_marker):
    """Keith prints section headings ('The Āçvina Çastra.') as their own short paragraphs before a khaṇḍa."""
    t = (seg.get('text') or '').strip()
    if seg.get('kind') != 'prose' or not t:
        return False
    w = t.split()
    return (len(w) <= 9 and nxt_is_marker and not re.search(r"[,;:'’‘“”]$", t)
            and re.match(r"^[_*(]*[A-Z]", t) is not None)


def join_paras(paras):
    return '\n'.join(p for p in (clean_en(x) for x in paras) if p)


def write_json(entries, path, indent=1):
    import json as _j
    with open(path, 'w', encoding='utf-8') as f:
        _j.dump(entries, f, ensure_ascii=False, indent=indent)


def heading_flags(items):
    """items: list of (kind, text, is_marker). A short title-like paragraph is a heading when the next
    paragraph opens a khaṇḍa or is itself a heading (chapter-end runs like 'THE SOMA SACRIFICE' + subtitle)."""
    flags = [False] * len(items)
    for i in range(len(items) - 1, -1, -1):
        kind, text, mk = items[i]
        if mk:
            continue
        nxt = i + 1 >= len(items) or items[i + 1][2] or flags[i + 1]
        flags[i] = is_heading({'kind': kind, 'text': text}, nxt)
    return flags


def entry(ref, iast, vid, text=''):
    from titus_to_json import iast_to_devanagari
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
        raise SystemExit(f'{name}: out of order')
    probs = []
    for e in entries:
        t = e['sanskrit_iast']
        if not t.strip():
            probs.append((e['reference'], 'empty'))
        if re.search(r'[<\[{\\#()]|//|\d|\^|~', t):
            probs.append((e['reference'], re.findall(r'.{0,10}(?:[<\[{\\#^~()]|//|\d).{0,10}', t)[:3]))
        if not re.search(r'[ऀ-ॿ]', e['meaning']):
            probs.append((e['reference'], 'no devanagari'))
    if probs:
        raise SystemExit(f'{name}: problems {probs[:10]}')
    print(f'{name}: {len(entries)} entries, {refs[0]} .. {refs[-1]}, '
          f'{sum(1 for e in entries if e["text"])} with English; validation OK')
