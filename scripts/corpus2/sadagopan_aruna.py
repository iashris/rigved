"""Add Sadagopan's English on Taittirīya Āraṇyaka Book 1 (Aruṇa Praśnam, 3 vols.) to public/data/aranyakas/taittiriya_aranyaka.json, field `text`.

Input: the PDFs from sadagopan.org/ebook/pdf/ (research/aranyakas/scans/sadagopan_aruna/), read with pdftotext.
He numbers Book 1's mantras in one running series ("MANTRAM # 4", "20TH MANTRAM", "90th Mantram"), which follow the order of our
entries; each block is checked against our Sanskrit through his own transliteration.  This is a devotional commentary with
word-by-word glosses after Sāyaṇa, not a literal translation; every entry it fills is labelled in `text_source`.
Usage: sadagopan_aruna.py [--write]
"""
import collections
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsonfmt import load, save  # noqa: E402
from oertel_jub import skeleton  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "research/aranyakas/scans/sadagopan_aruna")
PATH = os.path.join(REPO, "public/data/aranyakas/taittiriya_aranyaka.json")
SOURCE = "Oppiliappan Koil V. Sadagopan, Aruṇa Praśnam (sadagopan.org e-books): commentary with word-by-word meanings"
WORDS = {"FIRST": 1, "SECOND": 2, "THIRD": 3}
HEAD = re.compile(r"^\s*(?:(FIRST|SECOND|THIRD) MANTRAM?\s*:?|MANTRAM\s*#\s*(\d+)\s*:?|(\d+)(?:ST|ND|RD|TH|st|nd|rd|th)(?:\s+(?:and|AND)\s+(\d+)(?:ST|ND|RD|TH|st|nd|rd|th))?\s+[Mm](?:ANTRAMS?|antrams?)\s*:?)\s*$")
DROP = re.compile(r"^(sadagopan\.org|\d{1,3}|.*Thanks:.*|.*www\..*)$")


CAPTION = re.compile(r"(?i)(vAhanam on|^SrI Malayappa|^Sri Malayappa|-\s*(SrI|Sri) M[Aa]l[Oo]lan|Thanks to|^Image|^\"?.{0,60}\"\s*-\s*S[rR][iI]\b)")


def legacy(t):
    """A line in the books' non-Unicode Devanagari font, or in Unicode Devanagari; or a picture caption."""
    if CAPTION.search(t) or re.search(r"[a-zA-Z][vkstpmnyd]R[a-zA-Z]*\b|\b[a-zA-Z]*[bcdfghjklmnpqstvwyz]E\b|[a-z]\.\s*$(?<=[bcdfghjklmnpqstvwxz]\.)", t) and not re.search(r"\b(the|of|and|to|is|in|for|with)\b", t):
        return True
    if re.search(r"[\u0080-\u024f\u0900-\u097f]", t.replace("“", "").replace("”", "").replace("’", "")):
        return True
    letters = re.findall(r"[A-Za-z]", t)
    if letters and sum(c in "aeiouAEIOU" for c in letters) / len(letters) < 0.3:
        return True
    return bool(re.search(r"[>\[\]\\^@#$%&*=~]|;[a-zA-Z]|[a-z]![a-z ]", t)) and not re.search(r"\b(the|of|and|to|is|in|for|with)\b", t)


def stream():
    """All kept lines of the three volumes, in order."""
    out = []
    for v in (1, 2, 3):
        txt = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", os.path.join(SRC, f"aruna_prasnam_v{v}.pdf"), "-"],
                             capture_output=True, text=True, errors="replace").stdout
        for raw in txt.replace("\f", "\n").split("\n"):
            t = raw.strip()
            if t and (HEAD.match(t) or (not DROP.match(t) and not legacy(t))):
                out.append(t)
    return out


def anchor(entry):
    """The start of an entry's Sanskrit as it would look in Sadagopan's transliteration, reduced to consonants."""
    return skeleton(entry["sanskrit_iast"]).replace("h", "")


def blocks(ents):
    """{mantra number: lines}.  Numbers come from his headings; mantras without a usable heading are found by their
    transliterated opening, searched between the neighbouring headings.  Returns also the numbers a block shares."""
    L = stream()
    heads, also = {}, {}
    last = 0
    for i, t in enumerate(L):
        m = HEAD.match(t)
        if not m:
            continue
        n = WORDS.get(m.group(1)) or int(m.group(2) or m.group(3))
        if n == 1 and last >= 19:  # "1ST MANTRAM" for 21st: a dropped digit
            n = last + 1
        if n <= last or n > last + 25:
            continue
        heads[n] = i
        last = n
        if m.group(4):
            also[n] = int(m.group(4))
            last = also[n]
    sk = [skeleton(t).replace("h", "") for t in L]
    anchored = []
    known = sorted(heads)
    for n in range(1, 132):
        if n in heads or n in also.values() or (n - 1) >= len(ents):
            continue
        lo = max([heads[k] for k in known if k < n], default=0)
        hi = min([heads[k] for k in known if k > n], default=len(L))
        a = anchor(ents[n - 1])[:14]
        if len(a) < 8:
            continue
        for i in range(lo + 1, hi):
            if (sk[i] + (sk[i + 1] if i + 1 < len(sk) else "")).startswith(a):
                heads[n] = i
                anchored.append(n)
                known = sorted(heads)
                break
    order = sorted(heads, key=lambda k: heads[k])
    out = collections.OrderedDict()
    for k, n in enumerate(order):
        end = heads[order[k + 1]] if k + 1 < len(order) else len(L)
        start = heads[n] + (0 if n in anchored else 1)
        out[n] = L[start:end]
    return out, also, anchored


def clean(lines):
    s = ""
    for t in lines:
        if s.endswith("-") and not s.endswith(" -"):
            s = s[:-1] + t
        else:
            s += ("\n" if re.search(r"[.:!?)|]$", s) or re.match(r"\(|Meaning", t) else " ") + t if s else t
    s = re.sub(r"(?im)^.*\b(anuvAkam|anuvAka)\s*$", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def main():
    data, fmt = load(PATH)
    ents = [e for e in data if e["reference"].startswith("1.")]
    bl, also, anchored = blocks(ents)
    print("blocks", len(bl), "found by Sanskrit anchor", anchored, "\nstill missing", [n for n in range(1, 133) if n not in bl and n not in also.values()], "shared", also)
    sks = [skeleton(e["sanskrit_iast"]) for e in ents]

    def grams(t):
        return {t[i:i + 6] for i in range(max(0, len(t) - 5))}

    G = [grams(s) for s in sks]
    texts = {n: clean(v) for n, v in bl.items()}
    # Each block is compared with our entries around its own number.
    place, weak = {}, []
    off = 0
    for n in bl:
        # Only the transliteration before the first "Meaning:" is reliable Sanskrit; fall back to the block's opening.
        head = texts[n].split("Meaning:")[0][:1500] if "Meaning:" in texts[n] else texts[n][:800]
        g = grams(skeleton(head))
        scores = {j: len(g & G[j]) / max(1, min(len(g), len(G[j]))) for j in range(max(0, n - 4), min(len(ents), n + 3))}
        best = max(scores, key=scores.get) if scores else None
        exp = n - 1 + off
        if best is not None and scores[best] > scores.get(exp, 0) + 0.12 and scores[best] > 0.25:
            off = best - (n - 1)
            exp = best
        place[n] = exp
        if scores.get(exp, 0) < 0.2:
            weak.append((n, ents[exp]["reference"] if exp < len(ents) else None, round(scores.get(exp, 0), 2)))
    print("offsets used", sorted(set(j - (n - 1) for n, j in place.items())), "first shift at", next((n for n, j in place.items() if j != n - 1), None))
    print("weak Sanskrit match:", len(weak), weak[:24])
    show = "--write" not in sys.argv
    filled = 0
    for n, j in place.items():
        if 0 <= j < len(ents) and texts[n]:
            ents[j]["text"] = texts[n]
            ents[j]["text_source"] = SOURCE
            filled += 1
    # Anuvāka 22, the Mantra Puṣpam, is treated in a separate e-book.
    mp = next(e for e in ents if e["reference"] == "1.22.1")
    txt = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", os.path.join(SRC, "manthra_pushpam.pdf"), "-"], capture_output=True, text=True, errors="replace").stdout
    lines = [r.strip() for r in txt.replace("\f", "\n").split("\n")]
    lines = [t for t in lines if t and not DROP.match(t) and not legacy(t)]
    start = next(i for i, t in enumerate(lines) if re.search(r"(?i)mantra pushpam\s*$|^THE MANTRA|yO ?a?p[aA]+m ?pushpam|yOpAm pushpam", t) and i > 30)
    mp["text"] = clean(lines[start:])
    mp["text_source"] = SOURCE.replace("Aruṇa Praśnam", "Mantra Puṣpam")
    print("1.22.1 from Mantra Pushpam, starts:", mp["text"][:200].replace("\n", " / "), "| chars", len(mp["text"]))
    # A block that covers two mantras ("93rd and 94th"), or a mantra Sadagopan treats with its neighbour, points back to it.
    last = None
    for e in ents:
        if e.get("text"):
            last = e["reference"]
        elif last:
            e["text_ref"] = last
    print("filled", filled, "of", len(ents), "chars", sum(len(e.get("text") or "") for e in ents), "empty", [e["reference"] for e in ents if not e.get("text")][:30])
    if show:
        for n in (1, 4, 20, 93, 110, 131):
            if n in place:
                e = ents[place[n]]
                print(n, e["reference"], "|", e["sanskrit_iast"][:58], "\n   =>", texts[n][:230].replace("\n", " / "))
    else:
        save(PATH, data, fmt)
        print("written")


if __name__ == "__main__":
    main()
