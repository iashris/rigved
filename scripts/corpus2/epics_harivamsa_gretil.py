#!/usr/bin/env python3
"""Harivamsa critical edition (Vaidya, BORI 1969) from GRETIL tei/sa_harivaMza.xml -> public/data/epics/harivamsa.json.

Main text = <lg xml:id="HV_a.s">; star passages (<l xml:id="xHV_..."> with n="*HV...") and notes are skipped; the
appendix file sa_harivaMza-app1.xml is not read. A preceding <milestone unit="speaker"> is prefixed to the verse.
Pādas: '|' after each half-line, '||' at verse end ('//' in the source).
"""
import json, re, sys, unicodedata, collections
import xml.etree.ElementTree as ET
sys.path.insert(0, '/Users/iashris/Desktop/rigved/scripts')
from titus_to_json import iast_to_devanagari

SRC = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/g/1_sanskr/tei/sa_harivaMza.xml'
OUT = '/Users/iashris/Desktop/rigved/public/data/epics/harivamsa.json'
NS = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'

def tag(e):
    return e.tag.replace(NS, '')

def text_of(el):
    # all text except <note>
    parts = []
    def walk(e):
        if tag(e) == 'note':
            return
        if e.text: parts.append(e.text)
        for c in e:
            walk(c)
            if c.tail: parts.append(c.tail)
    walk(el)
    return ''.join(parts)

root = ET.parse(SRC).getroot()
body = next(e for e in root.iter() if tag(e) == 'body')

out, seen = [], set()
prev = (0, -1)
speaker = None
anomalies = []
for el in body.iter():
    t = tag(el)
    if t == 'milestone' and el.get('unit') == 'speaker':
        speaker = el.get('n').strip()
    elif t == 'lg':
        xid = el.get(XID) or ''
        m = re.fullmatch(r'HV_(\d+)[.-](\d+)', xid)
        given = (int(m.group(1)), int(m.group(2))) if m else None
        nxt, newch = (prev[0], prev[1] + 1), (prev[0] + 1, 1)
        if given and ((given[0] == prev[0] and given[1] > prev[1]) or (given[0] == prev[0] + 1 and given[1] == 1)):
            ref = given
            if given != nxt and given != newch:
                anomalies.append(('gap-before', xid))
        else:
            # malformed/mistyped id in GRETIL (HV_58, HV_24, HV_70-18, dup HV_105.6, HV_108.4, HV_09.29): neighbours fix it
            ref = nxt
            anomalies.append((xid, ref))
        if ref == (0, 0):
            continue  # unnumbered mangala verse (nārāyaṇaṃ namaskṛtya), not part of the CE numbering
        lines = []
        for l in el:
            if tag(l) != 'l':
                continue
            if (l.get(XID) or '').startswith('x') or (l.get('n') or '').startswith('*'):
                continue
            s = re.sub(r'\s+', ' ', text_of(l)).strip()
            s = s.replace('//', '||')
            s = re.sub(r'\s+', ' ', s.replace('*', ' ')).strip()  # ch. 63: stray editorial asterisks
            if not s.endswith(('|', '||')):
                s += ' |'
            lines.append(s)
        s = ' '.join(lines)
        s = re.sub(r'\s+([|])', r' \1', s).strip()
        if speaker:
            s = speaker + ' | ' + s
            speaker = None
        s = unicodedata.normalize('NFC', s)
        if not s.endswith('||'):
            anomalies.append(('no-final-danda', ref))
        prev = ref
        if ref in seen:
            raise SystemExit(f'duplicate {ref}')
        seen.add(ref)
        r = f'{ref[0]}.{ref[1]}'
        out.append({'reference': r, 'sanskrit_iast': s, 'meaning': iast_to_devanagari(s), 'text': '',
                    'mandala': ref[0], 'hymn': ref[1], 'vedaId': 'harivamsa'})

json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('entries', len(out), 'adhyayas', len({e['mandala'] for e in out}))
for a in anomalies:
    print('anomaly', a)
