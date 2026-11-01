"""Minimal external-sandhi joiner for the Kyoto-style analysed dharmasutra files
(Apastamba, Baudhayana, Vasistha) on GRETIL, where sandhi is undone and marked
with '-' or '^' and compound members are separated by '.'."""

VOWELS = ['ai', 'au', 'a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ', 'ṝ', 'ḷ', 'e', 'o']
VOICED = set('gjḍdbnmṅñṇyrlvh')
LONG = {'a': 'ā', 'i': 'ī', 'u': 'ū', 'ṛ': 'ṝ'}


def first_vowel(w):
    for v in VOWELS:
        if w.startswith(v):
            return v
    return None


def last_vowel(w):
    for v in VOWELS:
        if w.endswith(v):
            return v
    return None


def voiceless_s(b):
    """Form of final s/r before a voiceless consonant (or pause)."""
    if b.startswith('c'):
        return 'ś'
    if b.startswith('ṭ'):
        return 'ṣ'
    if b.startswith('t'):
        return 's'
    return 'ḥ'


def join(a, b, compound=False):
    """Return (left, sep, right) after applying sandhi between a and b."""
    sep = '' if compound else ' '
    if not a or not b:
        return a, sep, b
    if b[0] in '|/':          # before pause
        if a[-1] in 'sr':
            return a[:-1] + 'ḥ', ' ', b
        if a[-1] == 'm':
            return a[:-1] + 'ṃ', ' ', b
        return a, ' ', b
    av = b.startswith("'")
    if av:
        b = b[1:].lstrip()
        if b.startswith('a'):
            b = b[1:]
            # left was e/o (or as->o); keep avagraha
            if a.endswith('as'):
                a = a[:-2] + 'o'
            return a, " '", b
    bv = first_vowel(b)
    lv = last_vowel(a)
    if lv:
        if bv is None:
            return a, sep, b
        stem = a[:-len(lv)]
        if lv in ('a', 'ā'):
            if bv in ('a', 'ā'):
                return stem + 'ā' + b[len(bv):], '', ''
            if bv in ('i', 'ī'):
                return stem + 'e' + b[1:], '', ''
            if bv in ('u', 'ū'):
                return stem + 'o' + b[1:], '', ''
            if bv == 'ṛ':
                return stem + 'ar' + b[1:], '', ''
            if bv in ('e', 'ai'):
                return stem + 'ai' + b[len(bv):], '', ''
            if bv in ('o', 'au'):
                return stem + 'au' + b[len(bv):], '', ''
        if lv in ('i', 'ī'):
            if bv in ('i', 'ī'):
                return stem + 'ī' + b[1:], '', ''
            return stem + 'y', sep, b
        if lv in ('u', 'ū'):
            if bv in ('u', 'ū'):
                return stem + 'ū' + b[1:], '', ''
            return stem + 'v', sep, b
        if lv == 'ṛ':
            return stem + 'r', '', b if compound else b
        if lv in ('e', 'o'):
            if bv == 'a':
                return a, " '", b[1:]
            return stem + 'a', ' ', b
        if lv == 'ai':
            return stem + 'ā', ' ', b
        if lv == 'au':
            return stem + 'āv', ' ', b
        return a, sep, b
    c = a[-1]
    b_voiced = bv is not None or b[0] in VOICED
    if c in 'sr':
        pre = a[-2] if len(a) > 1 else ''
        if c == 's' and a in ('sas', 'eṣas', 'syas') and bv is None:
            return a[:-1], ' ', b
        if c == 's' and pre == 'a':
            if bv == 'a':
                return a[:-2] + 'o', " '", b[1:]
            if bv is not None:
                return a[:-1], ' ', b
            if b_voiced:
                return a[:-2] + 'o', sep, b
            return a[:-1] + voiceless_s(b), sep, b
        if c == 's' and pre == 'ā':
            if b_voiced:
                return a[:-1], ' ', b
            return a[:-1] + voiceless_s(b), sep, b
        # other vowels (i, u, e, ai, o ...) + s, or r
        if b_voiced:
            if b.startswith('r'):
                v = a[-2]
                return a[:-2] + LONG.get(v, v), ' ', b
            return a[:-1] + 'r', sep, b
        return a[:-1] + voiceless_s(b), sep, b
    if c == 't':
        if b[0] in 'nm':
            return a[:-1] + 'n', sep, b
        if b.startswith('c'):
            return a[:-1] + 'c', sep, b
        if b.startswith('j'):
            return a[:-1] + 'j', sep, b
        if b.startswith('l'):
            return a[:-1] + 'l', sep, b
        if b.startswith('ś'):
            return a[:-1] + 'c', sep, 'ch' + b[1:]
        if b_voiced:
            return a[:-1] + 'd', sep, b
        return a, sep, b
    if c in 'kṭp' and b_voiced:
        return a[:-1] + {'k': 'g', 'ṭ': 'ḍ', 'p': 'b'}[c], sep, b
    if c == 'm':
        if bv is None and not compound:
            return a[:-1] + 'ṃ', sep, b
        return a, sep, b
    if c == 'n':
        if b.startswith('c'):
            return a[:-1] + 'ṃś', sep, b
        if b.startswith('t'):
            return a[:-1] + 'ṃs', sep, b
        if b.startswith('j') or b.startswith('ś'):
            return a[:-1] + 'ñ', sep, b
        if bv is not None and len(a) > 2 and a[-2] in 'aiuṛ' and not compound:
            return a + 'n', sep, b
        return a, sep, b
    return a, sep, b


def apply(text, junction_chars='-^', compound_char='.'):
    """Apply sandhi at every junction marker in text."""
    import re
    # tokens: words, junction markers, compound markers, spaces
    toks = re.findall(r"\s+|[%s]|%s|[^\s%s%s]+" % (
        re.escape(junction_chars), re.escape(compound_char),
        re.escape(junction_chars), re.escape(compound_char)), text)
    out = []        # list of words / separators
    pending = None  # 'j' or 'c'
    for t in toks:
        if t.isspace():
            if pending is None:
                out.append(' ')
            continue
        if t in junction_chars:
            pending = 'j'
            continue
        if t == compound_char:
            pending = 'c'
            continue
        if pending and out:
            # find previous word
            while out and out[-1] == ' ':
                out.pop()
            if out:
                prev = out.pop()
                l, sep, r = join(prev, t, compound=(pending == 'c'))
                out.append(l)
                if r:
                    out.append(sep)
                    out.append(r)
                pending = None
                continue
        pending = None
        out.append(t)
    s = ''.join(out)
    # dangling junction before end of string: final s/r -> visarga
    s = re.sub(r"([aāiīuūeo])[sr]$", r"\1ḥ", s.strip())
    return s
