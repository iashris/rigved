"""Add Oertel's English (JAOS 16, 1896) to public/data/brahmanas/jaiminiya_upanisad_brahmana.json, field `text`.

Input: the ABBYY OCR of https://archive.org/details/jstor-592488 (research/aranyakas/scans/oertel_jub_1896/).
Oertel prints each khaṇḍa twice, Sanskrit then English, both headed "I. 1. 1." with sentence numbers run in.
Footnotes are dropped by their tighter leading.  Sentence numbers are often misread by the OCR ("a." for 2, "s." for 3),
so they are matched in order against the sentence count of our own entries.  When a khaṇḍa's count cannot be
met exactly, its whole English goes on the khaṇḍa's first entry rather than risking a wrong split.
Usage: oertel_jub.py [--write]
"""
import collections
import math
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abbyy_lines import body_lines, pages  # noqa: E402
from jsonfmt import load, save  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "research/aranyakas/scans/oertel_jub_1896/592488_abbyy.gz")
PATH = os.path.join(REPO, "public/data/brahmanas/jaiminiya_upanisad_brahmana.json")
HEAD = re.compile(r"^(I{1,3}V?|IV)\s*\.\s*(\d{1,2})\s*\.\s*([0-9Il\])!j]{1,2})\s*\.\s*")
STOP = set("the of and by he it is in to that this for with they as his be from on him what who verily which are them so when one those not all has was were these their thus if then there have you thou".split())
SANSK = re.compile(r"(?:''|\bv[dā]|dd|[a-z]d[a-z]*d\b|\bcd\b|\bsd\b|\btd\b|\bhd\b)")
CONFUSE = {1: "1Il)]i", 2: "2a?z", 3: "3sa8", 4: "4iJ", 5: "5sa", 6: "6eoG", 7: "7itTrl", 8: "8sa3B", 9: "9og0"}
MARK = re.compile(r"(?:(?<=[.,?!\"”:;\]\)'’]) |^)([0-9a-zA-Z?»«<>^*•■]{1,3}|\))\. (?=[A-Z\"“‘'\[(])")
LOOSE = re.compile(r"^(?:I{1,3}|IV|TV|T|l|1|H|HI|Il|II|n|in|ni|Ill|lll|ni)\s*[.,]\s*\S{1,3}\s*[.,]\s*(?:1|I|l|\)|\]|!|j|i|T)\s*[.,:]\s+")
NOTES_PAGE = 148  # Oertel's notes begin on the next scan page.
COMMON = set("about after again among around because before being between called certainly creatures death divinity divinities earth other others place people should speech their therefore there these thing things thinking those three through truly verily where which while whose world worlds would yonder".split())
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4}
SIGLA = re.compile(r"\b[ABC]\.(?:[ABC]\.)*\s*(?:insert|inserts|om\b|add\b|adds\b)|^['‘\d]+\s*[ABC]\.")
RUNNING = re.compile(r"(Oertel,?\s*$|Upani.ad.?-?\s*Br.hma.?.a\.?\s*\d*\s*$|^VOL\. XVI|^\d{2,3}\s*$)")


def kind(text):
    w = re.findall(r"[A-Za-z]+", text.lower())
    n = sum(x in STOP for x in w)
    if n >= 2 or (n == 1 and len(w) <= 6 and not SANSK.search(text)):
        return "en"
    if n == 0 and (SANSK.search(text) or len(w) >= 4):
        return "sa"
    return None


def skeleton(t):
    """Consonant skeleton for comparing OCR Sanskrit (ā read as d, diacritics lost) with ours."""
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^bcfghjklmnpqrstvwxyz]", "", t.replace("ʰ", ""))


def grams(t, n=5):
    return {t[i:i + n] for i in range(max(0, len(t) - n + 1))}


def blocks(by):
    """{(book, khanda): english}, plus diagnostics.  Each block of Oertel's Sanskrit is matched to one of our khaṇḍas
    by content, within a short window ahead of the previous match.  Each block of English then takes the oldest
    matched Sanskrit block still waiting for its English, so garbled numbers cannot shift the alignment."""
    order = list(by)
    ours = [grams(skeleton(" ".join(e["sanskrit_iast"] for e in by[k]))) for k in order]
    seq, cur = [], {"sa": None, "en": None}
    for n, lines in pages(SRC):
        if n > NOTES_PAGE:
            break
        wide = [l["l"] for l in lines if len(l["text"]) > 40]
        if not wide:
            continue
        left = sorted(wide)[len(wide) // 2]
        for l in body_lines(lines):
            t = l["text"].strip()
            if RUNNING.search(t) or SIGLA.search(t):
                continue
            lang = "sa" if l["italic"] >= 0.6 else "en"  # Oertel sets the Sanskrit in italic.
            m = LOOSE.match(t)
            if m:
                sm = HEAD.match(t)
                key = None
                if sm and sm.group(1) in ROMAN and sm.group(2).isdigit():
                    key = (ROMAN[sm.group(1)], int(sm.group(2)))
                block = {"lang": lang, "lines": [t[m.end():]], "key": key}
                seq.append(block)
                cur[lang] = block
                continue
            indented = l["l"] > left + 25
            if lang == "en" and indented and cur["sa"] is not None and (cur["en"] is None or seq.index(cur["en"]) < seq.index(cur["sa"])):
                # A new paragraph of English after newer Sanskrit: this block's header was lost.
                cur["en"] = {"lang": "en", "lines": [], "key": None}
                seq.append(cur["en"])
            if cur[lang] is not None:
                cur[lang]["lines"].append(t)
    return align(by, [b for b in seq if b["lang"] == "en"])


def align(by, eng_blocks):
    """Monotone alignment of English blocks to our khaṇḍas.  A pair scores for a legible matching header and for rare
    words of the English (names, chant terms) whose consonant skeleton occurs in that khaṇḍa's Sanskrit.  A block may
    merge into the previous khaṇḍa (a false break) and a khaṇḍa may go unfilled (a lost block)."""
    order = list(by)
    sk = [skeleton(" ".join(e["sanskrit_iast"] for e in by[k])) for k in order]
    texts = [join(b["lines"]) for b in eng_blocks]
    toks = []
    df = collections.Counter()
    vocab = {}
    for t in texts:
        ws = set()
        for w in re.findall(r"[A-Za-z]{5,}", t):
            x = skeleton(w)
            if len(x) >= 4 and w.lower() not in COMMON:
                ws.add(x)
        toks.append(ws)
    for w in set().union(*toks):
        vocab[w] = sum(w in x for x in sk)
    N = len(order)
    weight = {w: math.log(N / d) for w, d in vocab.items() if 0 < d <= N * 0.25}

    def pair(i, j):
        got = sum(weight.get(w, 0) for w in toks[i] if w in sk[j])
        total = sum(weight.get(w, 0) for w in toks[i]) or 1
        return 6 * got / total + (3 if eng_blocks[i]["key"] == order[j] else 0)

    M = len(texts)
    NEG = -1e9
    dp = [[NEG] * (N + 1) for _ in range(M + 1)]
    bk = {}
    dp[0][0] = 0
    for i in range(M + 1):
        for j in range(N + 1):
            if dp[i][j] == NEG:
                continue
            if j < N and dp[i][j] - 0.8 > dp[i][j + 1]:  # khaṇḍa j gets no block
                dp[i][j + 1] = dp[i][j] - 0.8
                bk[(i, j + 1)] = "skip"
            if i < M and j < N and dp[i][j] + pair(i, j) > dp[i + 1][j + 1]:
                dp[i + 1][j + 1] = dp[i][j] + pair(i, j)
                bk[(i + 1, j + 1)] = "take"
            if i < M and j > 0 and dp[i][j] + 0.5 * pair(i, j - 1) - 0.8 > dp[i + 1][j]:  # block i continues khaṇḍa j-1
                dp[i + 1][j] = dp[i][j] + 0.5 * pair(i, j - 1) - 0.8
                bk[(i + 1, j)] = "merge"
    i, j, path = M, N, []
    while i or j:
        op = bk[(i, j)]
        if op == "skip":
            j -= 1
        elif op == "take":
            i, j = i - 1, j - 1
            path.append((i, j))
        else:
            i -= 1
            path.append((i, j - 1))
    path.reverse()
    out = collections.OrderedDict()
    doubt = []
    for i, j in path:
        out.setdefault(order[j], []).append(texts[i])
        near = range(max(0, j - 2), min(N, j + 3))
        best = max(near, key=lambda x: pair(i, x))
        if best != j and pair(i, best) > pair(i, j) + 0.7:
            doubt.append((order[j], order[best], eng_blocks[i]["key"]))
    head_bad = [(order[j], eng_blocks[i]["key"]) for i, j in path if eng_blocks[i]["key"] and eng_blocks[i]["key"] != order[j]]
    print("English blocks", M, "khandas filled", len(out), "of", N)
    print("headers disagreeing with alignment:", head_bad[:30])
    print("doubtful (assigned, better-looking neighbour, header):", doubt[:30])
    return {k: " ".join(v) for k, v in out.items()}


def join(lines):
    s = ""
    for t in lines:
        if s.endswith("-"):
            s = s[:-1] + t
        else:
            s += (" " if s else "") + t
    return re.sub(r"\s+", " ", s).strip()


def score(g, k):
    if g == str(k):
        return 3.0
    if k < 10 and len(g) == 1 and g in CONFUSE.get(k, ""):
        return 2.0
    if k >= 10 and len(g) == len(str(k)) and any(x == y for x, y in zip(g, str(k))):
        return 1.0
    return -0.5 if len(g) <= 2 else -4.0


def split(text, n):
    """Divide a khaṇḍa's English among its n sentences at the run-in numbers.  Each marker is either read as a
    sentence number, in increasing order, or ignored; a misread "3." can stand for 2.  A sentence whose number was
    not found gets no text of its own: its English stays at the end of the sentence before."""
    parts = [""] * n
    if n == 1:
        return [text]
    cand = [(m.start(), m.end(), m.group(1)) for m in MARK.finditer(text)]
    # best[k] = best score with the last accepted marker read as sentence k, and how we got there
    best = {1: (0.0, [])}
    for c in cand:
        new = dict(best)
        for k, (sc, path) in best.items():
            for j in range(k + 1, min(n, k + 3) + 1):
                v = sc + score(c[2], j) - 0.75 * (j - k - 1)
                if v > new.get(j, (-1e9,))[0]:
                    new[j] = (v, path + [(j, c)])
        best = new
    # finishing short of n costs a little for each sentence left unmarked
    k = max(best, key=lambda x: best[x][0] - 0.75 * (n - x))
    path = best[k][1]
    last, cur = 0, 1
    for j, c in path:
        parts[cur - 1] = text[last:c[0]].strip()
        last, cur = c[1], j
    parts[cur - 1] = text[last:].strip()
    return parts


# Sanskrit that the OCR's italic flag let through into the English run, cut by hand after reading each place.
LEAKS = {
    (4, 24): (r"^.*?(?=He chose man)", ""),
    (4, 28): (r"23, athd 'nyatrd 'py uktarh ydl\), gabdaa tad dditya; vdc, prdna\.?", ""),
    (3, 9): (r"— tat j!\)ra<Aa»ia>7i mriyate\.?", ""),
}
TERMS = {"gdyatrl": "gāyatrī", "gdyatrt": "gāyatrī", "gdyatra": "gāyatra", "sdmans": "sāmans", "sdman": "sāman", "sdm.an": "sāman", "mman": "sāman",
         "udgltha": "udgītha", "udgttha": "udgītha", "adgltha": "udgītha", "prastdva": "prastāva", "pratihdra": "pratihāra", "pdda": "pāda",
         "brdhmana": "brāhmaṇa", "vpanisad": "upaniṣad", "upanisad": "upaniṣad", "tlie": "the", "breatli": "breath", "rnnning": "running",
         "Yokgd": "Yoked", "yajuses": "yajuses", "re's": "ṛc's"}


def tidy(t):
    """Conservative repair of recurring OCR damage only: known terms, word-initial ś read as ^, stray note marks, punctuation spacing."""
    for a, b in TERMS.items():
        t = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, t)
    t = re.sub(r"(?<![A-Za-z])\^([a-zA-Z])", lambda m: "Ś" + m.group(1).lower(), t)
    t = re.sub(r"(?<=[a-z])\^(?=[\s.,;:])", "", t)
    t = re.sub(r"\s+([,;:?!])", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    data, fmt = load(PATH)
    by = collections.OrderedDict()
    for e in data:
        a, b = e["reference"].split(".")[:2]
        by.setdefault((int(a), int(b)), []).append(e)
    eng = blocks(by)
    missing = 0
    unmarked = 0
    for k, ents in by.items():
        t = eng.get(k)
        if not t:
            missing += 1
            continue
        if k in LEAKS:
            t = re.sub(LEAKS[k][0], LEAKS[k][1], t, count=1, flags=re.S).strip()
        if k == (4, 28):
            # Oertel's notes begin right after the last sentence; the run-in numbers of this khaṇḍa are unreadable.
            t = re.split(r"[:;.]?\s*:?n?\"?otes\. The MSS", t)[0].rstrip() + "."
            cuts = [r"This is its second", r"This is its third", r"[\"“'^ ]*Bhus\s*,\s*bhuvas\s*;", r"[\"“'^ ]*Svar\s*;\s*who\s*shall", r"[\"“'^ ]*Bhus\s*,\s*bhuvas\s*,\s*svar"]
            pieces, rest = [], t
            for c in cuts:
                m = re.search(c, rest)
                pieces.append(rest[:m.start()])
                rest = rest[m.start():]
            pieces.append(rest)
            for e, p in zip(ents, pieces):
                e["text"] = tidy(re.sub(r"\s*\d\.?\s*$", "", p).strip().lstrip("'^ "))
            continue
        parts = [tidy(p) for p in split(t, len(ents))]
        unmarked += sum(not p for p in parts)
        for e, p in zip(ents, parts):
            e["text"] = p
            e.pop("text_source", None)
    # OCR scrambled the end of 4.23 across a page: its last sentence is rebuilt from the page, and 7 was misread as 1.
    tail = next(e for e in by[(4, 23)] if e["reference"] == "4.23.7")
    prev = next(e for e in by[(4, 23)] if e["reference"] == "4.23.6")
    if "______" in prev["text"]:
        prev["text"], tail["text"] = "", prev["text"].replace("______", "white and black, it snatcheth these two unto itself.\" He considered: \"Where now may these divinities bring tribute to me lying supine?\"")
    extra = sorted(set(eng) - set(by))
    print("khandas in corpus", len(by), "with English", len(eng), "missing", [k for k in by if k not in eng], "extra", extra[:10])
    print("sentences whose English stays with the previous sentence:", unmarked)
    print("entries with text", sum(bool(e.get("text")) for e in data), "of", len(data), "chars", sum(len(e.get("text") or "") for e in data))
    if "--write" in sys.argv:
        save(PATH, data, fmt)
        print("written")
    else:
        for r in ("1.2.3", "1.8.1", "2.9.1", "3.14.5", "3.30.1", "4.18.1", "4.19.1", "4.24.1", "4.28.1"):
            e = next((x for x in data if x["reference"] == r), None)
            if e:
                print(r, "|", e["sanskrit_iast"][:70], "\n   =>", (e.get("text") or "")[:210])


if __name__ == "__main__":
    main()
