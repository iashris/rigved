"""Add Pramāṇa's machine English (Gemini) to the Śāṅkhāyana and Kāṭhaka Āraṇyakas, field `text_mt` (never `text`).

Input: the segments saved under research/aranyakas/pramana/ from /api/segments.  Same method as pramana_mt_jub.py:
each Pramāṇa unit is matched to our entries by comparing the Sanskrit, and a unit that covers several of our entries
puts its English on the first; the others get `text_ref`.  Nothing is split.  Usage: pramana_mt_aranyakas.py [--write]
"""
import difflib
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsonfmt import load, save  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "research/aranyakas/pramana")
JOBS = {"sankhayana_aranyaka": "in.veda.aranyaka.kausitaki", "kathaka_aranyaka": "in.veda.aranyaka.katha"}
MIN = 0.72


def norm(t):
    t = unicodedata.normalize("NFD", t or "").lower()
    t = "".join(c for c in t if not unicodedata.combining(c) or c in "̣̄")
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"śā \d+,\s?\d+", "", t)
    t = re.sub(r"\d+", "", t)
    return re.sub(r"[^a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]", "", t)


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).quick_ratio() and difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def units(path):
    sa = json.load(open(os.path.join(SRC, path + ".json"), encoding="utf-8"))
    mt = json.load(open(os.path.join(SRC, path + "--en-mt.json"), encoding="utf-8"))
    en = {s["loc"]: s["text"] for s in mt["segments"] if s.get("text")}
    en = {k: re.sub(r"^ŚĀ \d+[.,]\s?\d+\s*", "", v) for k, v in en.items()}
    return [(s["loc"], s["text"], en.get(s["loc"], "")) for s in sa["segments"] if s.get("text")], mt.get("title")


def anchored(cid, path, file, data, fmt, ours, us):
    """Pramāṇa cuts the Kāṭhaka every 1,200 characters or so, wherever that falls, so a chunk can begin inside one of our
    entries.  Find each chunk's start by exact text anchors; an entry a chunk begins in takes that chunk's English
    (both chunks' if a boundary falls inside it), and later entries the chunk covers get `text_ref`."""
    whole, starts, pos = "", [], 0
    for x in ours:
        starts.append(len(whole))
        whole += x
    placed, missed = [], []
    for loc, sa, en in us:
        n = norm(sa)
        if len(n) < 25:
            missed.append(loc)
            continue
        at = -1
        for off in range(0, min(400, len(n) - 16), 8):
            i = whole.find(n[off:off + 16], pos)
            if i >= 0 and i - off - pos < 1500:
                at = max(pos, i - off)
                break
        if at < 0:
            missed.append(loc)
            continue
        placed.append((loc, en, at))
        pos = at + len(n) // 2
    entry = lambda c: max(i for i, st in enumerate(starts) if st <= c)
    heads = {}
    for k, (loc, en, at) in enumerate(placed):
        i = entry(at)
        # A chunk starting in the last tenth of an entry really begins with the next one.
        if i + 1 < len(data) and at - starts[i] > 0.9 * max(1, len(ours[i])):
            i += 1
        heads.setdefault(i, []).append(en)
    order = sorted(heads)
    for a, b in zip(order, order[1:] + [len(data)]):
        data[a]["text_mt"] = "\n\n".join(x for x in heads[a] if x)
        data[a]["text_mt_source"] = f"Pramāṇa machine translation (Gemini), {path}~en-mt"
        for i in range(a + 1, b):
            data[i]["text_ref"] = data[a]["reference"]
    first = order[0]
    print(cid, "units", len(us), "placed", len(placed), "missed", missed, "entries with MT", len(order), "covered", sum(bool(e.get("text_mt") or e.get("text_ref")) for e in data), "of", len(data), "before first", [e["reference"] for e in data[:first]])
    for i in order[:2] + order[-3:]:
        print("   ", data[i]["reference"], "|", data[i]["sanskrit_iast"][:60], "=>", data[i]["text_mt"][:80].replace("\n", " "))
    if "--write" in sys.argv:
        save(file, data, fmt)
        print("   written")


def main():
    for cid, path in JOBS.items():
        file = os.path.join(REPO, "public/data/aranyakas", cid + ".json")
        data, fmt = load(file)
        for e in data:
            for k in ("text_mt", "text_mt_source", "text_ref"):
                e.pop(k, None)
        ours = [norm(e["sanskrit_iast"]) for e in data]
        us, _ = units(path)
        if cid == "kathaka_aranyaka":
            anchored(cid, path, file, data, fmt, ours, us)
            continue
        last, cover, skipped = -1, [], []
        for loc, sa, en in us:
            n = norm(sa)
            if len(n) < 25:
                skipped.append(loc)
                continue
            best = None
            for start in range(last + 1, min(last + 6, len(data))):
                acc, j = "", start
                while j < len(data) and len(acc) < len(n) * 1.25:
                    acc += ours[j]
                    r = sim(n, acc)
                    if r >= MIN and (best is None or r > best[0] + 0.01):
                        best = (r, start, j)
                    j += 1
                if best and best[0] > 0.9:
                    break
            if best:
                cover.append((loc, en, best[1], best[2], best[0]))
                last = best[2]
            else:
                skipped.append(loc)
        written = 0
        for loc, en, a, b, r in cover:
            if not en:
                continue
            data[a]["text_mt"] = en
            data[a]["text_mt_source"] = f"Pramāṇa machine translation (Gemini), {path}~en-mt"
            written += 1
            for i in range(a + 1, b + 1):
                data[i]["text_ref"] = data[a]["reference"]
        n_cov = sum(bool(e.get("text_mt") or e.get("text_ref")) for e in data)
        print(cid, "units", len(us), "matched", len(cover), "skipped", skipped[:12], "lowest sim", round(min(c[4] for c in cover), 2),
              "entries with MT", written, "covered incl. refs", n_cov, "of", len(data), "uncovered", [e["reference"] for e in data if not (e.get("text_mt") or e.get("text_ref"))][:12])
        for loc, en, a, b, r in cover[1:4]:
            print("   ", loc, "->", data[a]["reference"], "..", data[b]["reference"], round(r, 2), "|", en[:90].replace("\n", " "))
        if "--write" in sys.argv:
            save(file, data, fmt)
            print("   written")


if __name__ == "__main__":
    main()
