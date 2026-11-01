"""Shared helpers for the `rebuild_gretil` converters.

These rebuild five existing repo files (built by an older converter that lost the upper
numbering levels) from GRETIL TEI. Each script refuses to overwrite a file that has English.
"""
import collections
import json
import os
import re
import shutil
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vedic_common import GRETIL, REPO, make_entry, norm_space, validate, write  # noqa: E402,F401

TEI = os.path.join(GRETIL, 'tei')
WORK = os.path.join(os.path.dirname(GRETIL.rstrip('/')).rsplit('/g', 1)[0], 'work', 'rebuild_gretil')
NS = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'


def body(fname):
    return ET.parse(os.path.join(TEI, fname)).getroot().find(f'.//{NS}body')


def tag(el):
    return el.tag.replace(NS, '')


def load_old(rel_path):
    """Old file contents; abort if any entry carries English."""
    path = os.path.join(REPO, rel_path)
    # keep a copy of the pre-rebuild file so reruns still compare against the old converter's output
    bak = os.path.join(WORK, 'old_' + os.path.basename(rel_path))
    if not os.path.exists(bak):
        os.makedirs(WORK, exist_ok=True)
        shutil.copyfile(path, bak)
    old = json.load(open(bak, encoding='utf-8'))
    eng = [e['reference'] for e in old if (e.get('text') or '').strip()]
    if eng:
        raise SystemExit(f'{rel_path} has English in {len(eng)} entries (e.g. {eng[:3]}); not overwriting')
    return old


def dup_count(entries):
    c = collections.Counter(e['reference'] for e in entries)
    return sum(v - 1 for v in c.values() if v > 1)


def strip_parens(s):
    """Remove (possibly nested) parenthesised groups; drop stray brackets left behind."""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\([^()]*\)', ' ', s)
    return s.replace('(', ' ').replace(')', ' ')


def dots_slashes(s):
    """Dot-separated word style (KB, Khila): // -> ||, / -> |, dots -> spaces."""
    s = re.sub(r'/\s*/', ' || ', s)
    s = s.replace('/', ' | ')
    s = s.replace('.', ' ')
    s = re.sub(r'\|(\s*\|)+', '||', s)       # collapse "| |" runs
    s = re.sub(r'\|\|\s*\|', '||', s)
    return norm_space(s)


def fix_numbering(segs, label):
    """segs: list of [a, k, s, text] in text order (TEI numbering, which has typos).
    1. A segment whose (a,k) goes backwards, or jumps forward with s != 1 while the next
       segment restarts that new khanda at 1, belongs to the current khanda.
    2. Within each khanda, keep the TEI sentence numbers where they increase; fix single bad
       numbers (see repair); if that fails, renumber the khanda 1..n in text order. Returns new list of ((a,k,s), text) and prints what changed."""
    cur = None
    moved = []
    for i, sg in enumerate(segs):
        ak = (sg[0], sg[1])
        if cur is not None and ak != cur:
            nxt = segs[i + 1] if i + 1 < len(segs) else None
            if ak < cur or (sg[2] != 1 and nxt and (nxt[0], nxt[1]) == ak and nxt[2] == 1):
                moved.append(f'{sg[0]}.{sg[1]}.{sg[2]}->{cur[0]}.{cur[1]}')
                sg[0], sg[1] = cur
                ak = cur
        cur = ak
    groups = collections.OrderedDict()
    for a, k, s, t in segs:
        groups.setdefault((a, k), []).append((s, t))
    out, local, renum = [], [], []
    for (a, k), items in groups.items():
        nums = [s for s, _ in items]
        fixed = repair(nums)
        if fixed is None:
            renum.append(f'{a}.{k}(n={len(nums)},TEI max={max(nums)})')
            fixed = list(range(1, len(nums) + 1))
        elif fixed != nums:
            local += [f'{a}.{k}.{x}->{y}' for x, y in zip(nums, fixed) if x != y]
        for n, (_, t) in zip(fixed, items):
            out.append(((a, k, n), t))
    print(f'[{label}] khanda fixes: {moved}')
    print(f'[{label}] single-number fixes ({len(local)}): {", ".join(local)}')
    print(f'[{label}] khandas renumbered 1..n ({len(renum)}): {", ".join(renum)}')
    return out


def repair(nums):
    """Keep TEI numbers (gaps allowed, they are real lacunae) while strictly increasing.
    A number that breaks the order is replaced by prev+1 when that fits before the next
    number; returns None if the khanda cannot be fixed this way (e.g. a restart)."""
    out = []
    for i, x in enumerate(nums):
        prev = out[-1] if out else 0
        nxt = nums[i + 1] if i + 1 < len(nums) else None
        if x > prev and (nxt is None or x < nxt):
            out.append(x)
        elif x > prev and nxt <= prev and x <= prev + 3:   # it is the next number that is wrong
            out.append(x)
        elif nxt is None or prev + 1 < nxt:
            out.append(prev + 1)
        elif x > prev and x == nxt:                        # doubled number; the next gets fixed
            out.append(x)
        else:
            return None
    if any(b <= a for a, b in zip(out, out[1:])):
        return None
    return out


def skel(s):
    """Letters only, for content comparison."""
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'[^a-zāīūṛṝḷḹṅñṭḍṇśṣḥṃṁ]', '', s.lower())


def compare_old(old, new, n=5, thresh=0.5):
    """Report old entries whose content is largely absent from the new file: share of the old
    entry's letter 5-grams found anywhere in the new file < thresh (tolerates sandhi/spacing
    differences between editions)."""
    grams = set()
    for e in new:
        k = skel(e['sanskrit_iast'])
        grams.update(k[i:i + n] for i in range(len(k) - n + 1))
    miss = []
    for e in old:
        k = skel(e['sanskrit_iast'])
        g = [k[i:i + n] for i in range(len(k) - n + 1)]
        if len(g) < 3:
            continue
        cov = sum(x in grams for x in g) / len(g)
        if cov < thresh:
            miss.append((e, cov))
    print(f'old entries with <{thresh:.0%} of their 5-grams in new: {len(miss)} of {len(old)}')
    # isolated misses are mostly short sentences whose readings differ; runs of >=3 adjacent
    # misses point at passages genuinely absent from the new file
    idx = {id(e): i for i, e in enumerate(old)}
    pos = [idx[id(e)] for e, _ in miss]
    runs, start = [], None
    for j, q in enumerate(pos):
        if start is None:
            start = j
        if j + 1 == len(pos) or pos[j + 1] != q + 1:
            if j - start + 1 >= 3:
                runs.append((pos[start], q))
            start = None
    print(f'runs of >=3 adjacent missing old entries: {len(runs)}')
    for a, b in runs[:20]:
        print(f'   RUN old[{a}..{b}] {old[a]["reference"]}..{old[b]["reference"]}: {old[a]["sanskrit_iast"][:90]}')
    return miss


def report(rel_path, old, entries):
    refs = [e['reference'] for e in entries]
    print(f'== {rel_path}: old {len(old)} entries ({dup_count(old)} dup refs) -> new {len(entries)} '
          f'({refs[0]} .. {refs[-1]}, {dup_count(entries)} dup refs)')


def odd_chars(entries):
    ok = set('abcdeghijklmnoprstuvyāīūṛṝḷḹṅñṭḍṇśṣḥṃṁ \'|')
    c = collections.Counter(ch for e in entries for ch in e['sanskrit_iast'] if ch not in ok)
    print('non-IAST characters:', dict(c.most_common(30)))
    return c
