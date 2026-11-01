#!/usr/bin/env python3
"""Kātyāyana's Sarvānukramaṇī (Ṛgveda) from Pramāṇa -> public/data/other/sarvanukramani.json.

Reference scheme (two parts, no letters):
  1.<section>.<sūtra>  the paribhāṣā (introduction), in Pramāṇa's section.sentence numbering;
  2.<maṇḍala>.<sūkta>  the anukramaṇī proper, keyed by Ṛgveda maṇḍala and sūkta from the sūkta numbers that
                       open each paragraph (they restart at 1 with every maṇḍala: 191, 43, 62, 58, 87, 75, 104, 103,
                       114, 191 = 1,028 sūktas). Lines without a number (maṇḍala intros, closing lines) join a sūkta.
Usage: python3 -I scripts/corpus2/pramana_sa_sarvanukramani.py
"""

import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from pramana_sa_common import segments  # noqa: E402
from titus_to_json import iast_to_devanagari  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data")
REL = "other/sarvanukramani.json"
RV_SUKTAS = [191, 43, 62, 58, 87, 75, 104, 103, 114, 191]


def clean(t):
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)  # [1], [prathamamaṇḍalasya mantrāḥ 2006]: editor's counters
    t = re.sub(r"\([^)]*\)", " ", t)  # (mantrāḥ 159)
    t = t.replace("‘", "").replace("’", "")
    t = re.sub(r"\|\|\s*\d+\s*\|\|", "||", t)  # || 23 ||: running sūtra number
    t = re.sub(r"\d+", " ", t)
    t = re.sub(r"(\|\|?\s*)+\|\|", "||", t)
    t = re.sub(r"\s+", " ", t).strip()
    return unicodedata.normalize("NFC", t)


def deva(s):
    return unicodedata.normalize("NFC", iast_to_devanagari(s).replace("||", "॥").replace("|", "।"))


def main():
    units, order, pending = {}, [], []
    mandala = 0
    for s in segments("in.vedanga.misc.anukramani.katyayana.sarvanukramani"):
        if not s["text"] or s["kind"] in ("colophon", "note"):
            continue
        loc, text = s["loc"], s["text"]
        if loc.startswith("11.13.p"):
            m = re.match(r"\s*(\d+)\.\s", text)
            if m:
                n = int(m.group(1))
                mandala += n == 1
                key, text = (2, mandala, n), text[m.end():]
            else:
                key = None  # unnumbered line: joins the sūkta before it (or the next, at a maṇḍala's start)
                if mandala == 0 or (order and order[-1][:2] != (2, mandala)):
                    key = None
        else:
            parts = loc.split(".")
            key = (1, int(parts[0]), int(parts[1])) if len(parts) == 2 and parts[1].isdigit() else None
        if key is None:
            if order and (not loc.startswith("11.13.p") or mandala == 0 or order[-1][:2] == (2, mandala)):
                units[order[-1]].append(text)
            else:
                pending.append(text)
            continue
        if key in units or (order and key < order[-1]):
            raise SystemExit(f"unexpected numbering at {loc}: {key}")
        units[key] = pending + [text]
        pending = []
        order.append(key)
    if pending:
        units[order[-1]] += pending

    out = []
    for key in order:
        iast = clean(" ".join(units[key]))
        out.append({"reference": ".".join(map(str, key)), "sanskrit_iast": iast, "meaning": deva(iast), "text": "",
                    "mandala": key[0], "hymn": key[1], "verse": key[2], "vedaId": "sarvanukramani"})

    # validation
    counts = [sum(1 for k in order if k[:2] == (2, m)) for m in range(1, 11)]
    assert counts == RV_SUKTAS, counts
    for m in range(1, 11):
        assert [k[2] for k in order if k[:2] == (2, m)] == list(range(1, RV_SUKTAS[m - 1] + 1)), m
    refs = [e["reference"] for e in out]
    assert len(set(refs)) == len(refs)
    for e in out:
        assert e["sanskrit_iast"] and re.search(r"[ऀ-ॿ]", e["meaning"]), e["reference"]
        assert not re.search(r"[<>\[\]{}()_#*=\d]|//", e["sanskrit_iast"]), e
    with open(os.path.join(DATA, REL), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{REL}: {len(out)} entries ({len(out) - sum(counts)} paribhāṣā + {sum(counts)} sūktas), {refs[0]}..{refs[-1]}")


if __name__ == "__main__":
    main()
