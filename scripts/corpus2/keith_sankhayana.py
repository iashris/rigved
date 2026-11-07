"""Add Keith's English (The Śāṅkhāyana Āraṇyaka, RAS 1908) to public/data/aranyakas/sankhayana_aranyaka.json, field `text`.

Input: the ABBYY OCR of https://archive.org/details/sankhayanaaranya00keitrich (research/aranyakas/scans/keith_sankhayana_1908/).
Keith heads each chapter "Adhyāya N." and closes each section with "(n.)", which gives adhyāya.khaṇḍa directly.
Footnotes are dropped by their tighter leading.  Usage: keith_sankhayana.py [--write]
"""
import collections
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abbyy_lines import body_lines, pages  # noqa: E402
from jsonfmt import load, save  # noqa: E402
from oertel_jub import skeleton  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "research/aranyakas/scans/keith_sankhayana_1908/sankhayanaaranya00keitrich_abbyy.gz")
PATH = os.path.join(REPO, "public/data/aranyakas/sankhayana_aranyaka.json")
ADH = re.compile(r"^\s*Ad\S{2,8}\s+[IVXLlF1]+\s*\.?\s*$")  # the word and numeral are often garbled; the headings run in order
# "(7.)", the garbled "(1-i.)" and "(11-)", and in chapter 12 "(5. 1.)" = verse 5, khaṇḍa 1.
END = re.compile(r"\(\s*([0-9IlOoSsH](?:[0-9IlOoSsH]|[-i]{1,2})?)\s*[.,:-]\s*(?:\d\s*\.\s*)?\)i?(?=[\s^'*]|$)")
RUN = re.compile(r"(?:S.NKH.YANA\s+.R.NYAKA\.?(?:\s*\d+)?\s*$|^\s*\d+\s+S.NKH)")
def num(g):
    g = g.replace("H", "11").replace("I", "1").replace("l", "1").replace("O", "0").replace("o", "0").replace("S", "5").replace("s", "5")
    return int(g) if g.isdigit() else None


def parse():
    """{adhyāya: [(n, text)]} in order, n as printed (None when unreadable)."""
    out, adh, buf = collections.OrderedDict(), None, []
    for n, lines in pages(SRC):
        for l in body_lines(lines):
            t = l["text"].strip()
            if RUN.search(t):
                continue
            if t.upper().startswith("APPENDIX") and adh == 15:
                if buf:
                    out[adh].append((None, join(buf)))
                return out
            if ADH.match(t) and l["l"] > 500:
                if adh and buf:
                    out[adh].append((None, join(buf)))
                adh, buf = (adh or 0) + 1, []
                out.setdefault(adh, [])
                continue
            if adh is None:
                continue
            while True:
                e = END.search(t)
                if not e:
                    break
                buf.append(t[:e.start()])
                out[adh].append((num(e.group(1)), join(buf)))
                buf, t = [], t[e.end():].strip()
            if t:
                buf.append(t)
    return out


def join(lines):
    s = ""
    for t in lines:
        t = t.strip()
        s = s[:-1] + t if s.endswith("-") else (s + " " + t if s else t)
    return tidy(s)


TERMS = {"Mahiivrata": "Mahāvrata", "Samhittl": "Saṃhitā", "jDroclaim": "proclaim", "Orn.": "Om.", "JSTow": "Now", "Mahdvrata": "Mahāvrata", "Baliiki": "Bālāki", "BiTlaki": "Bālāki", "Ajiitasatru": "Ajātaśatru", "Ajiitasatrii": "Ajātaśatru", "Prajilpati": "Prajāpati", "Ajatasatrii": "Ajātaśatru", "Samhitiis": "Saṃhitās", "Yedas": "Vedas", "Yisvamitra": "Viśvāmitra", "Mandfikeyas": "Māṇḍūkeyas", "Upanisad": "Upaniṣad", "w ere": "were", "trijale": "triple", "j'oke": "yoke", "\\Aith": "with"}


def tidy(t):
    for a, b in TERMS.items():
        t = t.replace(a, b)
    t = re.sub(r"(?<=[A-Za-z.,;:'’”\"?!)])\s*[\^*]\s*\d?", " ", t)  # note marks
    t = re.sub(r"(?<=[a-z.,;:'’”])\s?['’]?\s?(?<=\s)[\^*]", " ", t)
    t = t.replace("* ", "'") if t.startswith("* ") else t
    t = re.sub(r"\s+([,;:?!.])", r"\1", t)
    t = re.sub(r"(?<=[.,;:'’?!)])\d(?=\s|$)", "", t)  # note numbers
    t = re.sub(r"(^|\s)['‘]\s+(?=\w)", r"\1'", t)
    t = re.sub(r"^[\^*'’\s]+(?=[A-Z'(])", "", t)
    return re.sub(r"\s+", " ", t).strip()


def place(a, got, ents):
    """Keith's sections onto our entries, in order.  Two chapters are not one-to-one with our file:
    7: our 7.3 is a mnemonic line that Keith does not render, so his section n >= 3 is our n + 1.
    12: Keith numbers the verses of the Bilva spell 1-35 in fives, which are our 12.1-12.7; the ritual after them is 12.8."""
    cells = collections.defaultdict(list)
    if a == 9 and len(got) == 7:  # the first "(1.)" is lost: 9.1 is the opening prayer, 9.2 starts here
        head, tail = got[0][1].split("He who knows the highest", 1)
        got = [(1, head.strip()), (2, "He who knows the highest" + tail)] + got[1:]
    for i, (n, t) in enumerate(got):
        if a == 7:
            j = i if i < 2 else i + 1
        elif a == 12:
            j = (i // 5) if i < 35 else i - 29  # after the 35 verses: "(7.)" closes khaṇḍa 7, "(8.)" is the ritual
        else:
            j = i
        cells[j].append(t)
    for j, e in enumerate(ents):
        e["text"] = " ".join(cells.get(j, []))


def main():
    data, fmt = load(PATH)
    by = collections.OrderedDict()
    for e in data:
        by.setdefault(int(e["reference"].split(".")[0]), []).append(e)
    eng = parse()
    show = "--write" not in sys.argv
    for a, ents in by.items():
        got = eng.get(a, [])
        place(a, got, ents)
        for e in ents:
            # A long footnote on verse text (Keith p. 17-18) is set like the body and runs into 3.2.
            e["text"] = re.sub(r"'?Parasodn\..*?ARAN ?YAK ?A\.\s*", "", e["text"], flags=re.S)
            # Footnotes interrupting a sentence across a page, read and cut one by one.
            for a, b in ((r"which > Prana and.*?touch and the skin\. is Brahman", "which is Brahman"),
                         (r"^AVritten in the Madhyadesa.*?on Aitareya Aranyaka, (?=Then follows)", ""),
                         (r"he 'i\.e\. whether he reviles.*?obhaydh \\* ?should say", "he should say"),
                         (r"before See vii, 1\..*?Here it is a survival\. and after", "before and after")):
                e["text"] = re.sub(a, b, e["text"], flags=re.S)
        nums = [n for n, _ in got]
        print(a, "ours", len(ents), "keith", len(got), "empty", [e["reference"] for e in ents if not e["text"]],
              "numbers", "1.." + str(len(got)) if nums == list(range(1, len(got) + 1)) else nums)
    # Rare-word check: an entry should share more rare words with its own Sanskrit than with its neighbours.
    sks = [skeleton(e["sanskrit_iast"]) for e in data]
    tok = [{skeleton(w) for w in re.findall(r"[A-Za-z]{5,}", e["text"]) if len(skeleton(w)) >= 4} for e in data]
    voc = set().union(*tok)
    W = {}
    for w in voc:
        d = sum(w in x for x in sks)
        if 0 < d <= len(data) * 0.15:
            W[w] = math.log(len(data) / d)
    sc = lambda i, j: sum(W.get(w, 0) for w in tok[i] if w in sks[j])
    doubt = [(data[i]["reference"], data[j]["reference"], round(sc(i, i), 1), round(sc(i, j), 1))
             for i in range(len(data)) for j in [i - 1, i + 1] if 0 <= j < len(data) and sc(i, j) > sc(i, i) * 1.5 + 4]
    print("doubts (entry, neighbour, own score, neighbour score):", doubt)
    print("entries with text", sum(bool(e["text"]) for e in data), "of", len(data), "chars", sum(len(e["text"]) for e in data))
    if not show:
        save(PATH, data, fmt)
        print("written")
    else:
        for r in ("1.1", "6.18", "6.19", "7.2", "7.4", "7.15", "7.16", "9.1", "9.2", "12.1", "12.7", "12.8", "14.2"):
            e = next(x for x in data if x["reference"] == r)
            print(r, "|", e["sanskrit_iast"][:60], "=>", e["text"][:110], "...", e["text"][-50:])


if __name__ == "__main__":
    main()
