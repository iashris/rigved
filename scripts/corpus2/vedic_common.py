"""Shared helpers for the `vedic` corpus2 converters (GRETIL sources).

Builds entries in the repo schema, writes JSON, and runs the validation pass.
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts')
from titus_to_json import iast_to_devanagari  # noqa: E402

REPO = '/Users/iashris/Desktop/rigved'
GRETIL = ('/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/'
          'c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/g/1_sanskr')


def norm_space(s):
    s = s.replace(' ', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    # no space before dandas, single space after
    s = re.sub(r'\s+(\|)', r' \1', s)
    return unicodedata.normalize('NFC', s)


def slashes_to_dandas(s):
    s = re.sub(r'\s*//\s*', ' || ', s)
    s = re.sub(r'\s*/\s*', ' | ', s)
    return norm_space(s)


def make_entry(ref_parts, iast, veda_id, text=''):
    ref_parts = [int(x) for x in ref_parts]
    iast = norm_space(iast)
    e = {
        'reference': '.'.join(str(x) for x in ref_parts),
        'sanskrit_iast': iast,
        # IAST m̐ (anunasika) comes out as "म्" + U+0310; render as candrabindu
        'meaning': unicodedata.normalize('NFC', iast_to_devanagari(iast).replace('म्\u0310', 'ँ')),
        'text': text,
        'mandala': ref_parts[0],
        'hymn': ref_parts[1] if len(ref_parts) > 1 else ref_parts[0],
    }
    if len(ref_parts) > 2:
        e['verse'] = ref_parts[2]
    elif len(ref_parts) == 1:
        # repo precedent (isha/mandukya): single-level ref -> mandala 1, hymn=verse=n
        e['mandala'] = 1
        e['hymn'] = ref_parts[0]
        e['verse'] = ref_parts[0]
    e['vedaId'] = veda_id
    return e


GLUED_DIGIT = re.compile(r'(?:[^\W\d_][0-24-9]|[^\W\d_]3\d|[0-24-9][^\W\d_])')


def validate(path, expected_note=''):
    data = json.load(open(path, encoding='utf-8'))
    refs = [d['reference'] for d in data]
    problems = []
    if len(set(refs)) != len(refs):
        dups = sorted({r for r in refs if refs.count(r) > 1})
        problems.append(f'duplicate refs: {dups[:10]}')
    keys = [tuple(int(x) for x in r.split('.')) for r in refs]
    for a, b, ra, rb in zip(keys, keys[1:], refs, refs[1:]):
        if b <= a:
            problems.append(f'out of order: {ra} -> {rb}')
            break
    for d in data:
        s = d['sanskrit_iast']
        if not s.strip():
            problems.append(f"empty: {d['reference']}")
        for bad in ('<', '>', '[', ']', '{', '}', '//', '(', ')', '`', '$', '*', '+'):
            if bad in s:
                problems.append(f"markup {bad!r} in {d['reference']}: {s[:80]}")
                break
        # letters glued to digits; a pluta "3" after a vowel letter is legitimate
        m = GLUED_DIGIT.search(s)
        if m:
            problems.append(f"glued digit {m.group()!r} in {d['reference']}")
        if not re.search('[ऀ-ॿ]', d['meaning']):
            problems.append(f"no devanagari: {d['reference']}")
        if s != unicodedata.normalize('NFC', s):
            problems.append(f"not NFC: {d['reference']}")
    print(f'--- {os.path.relpath(path, REPO)}: {len(data)} entries, '
          f'{refs[0]} .. {refs[-1]} {expected_note}')
    for p in problems[:25]:
        print('   PROBLEM', p)
    if len(problems) > 25:
        print(f'   ... {len(problems)} problems total')
    if not problems:
        print('   OK')
    return problems


def write(rel_path, entries):
    refs = [e['reference'] for e in entries]
    seen = set()
    for r in refs:
        if r in seen:
            raise SystemExit(f'DUPLICATE reference {r} in {rel_path}')
        seen.add(r)
    path = os.path.join(REPO, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return path
