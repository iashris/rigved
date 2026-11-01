#!/usr/bin/env python3
"""Normalise SBE-style transliteration in English `text` fields.

The SBE volumes print long vowels with a circumflex (â î û) and mark retroflex and palatal consonants with italics.
Once the HTML is stripped, the italic letters become stray single letters ("Brâhma n a", "S ûdra"). This turns
them back into IAST: "Brāhmaṇa", "Śūdra". Runs in place; rerunnable (already-normalised text is unchanged).

Usage: python3 -I normalize_sbe.py public/data/sutras/*.json public/data/upanishads/maitri_upanishad.json
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsonfmt import load, save  # noqa: E402

ITALIC = {"n": "ṇ", "t": "ṭ", "d": "ḍ", "s": "ś", "r": "ṛ", "h": "ḥ", "m": "ṃ", "l": "ḷ"}
INITIAL = {"S": "Ś", "R": "Ṛ"}
VOWELS = str.maketrans({"â": "ā", "î": "ī", "û": "ū", "Â": "Ā", "Î": "Ī", "Û": "Ū"})
LETTER = "A-Za-zâîûÂÎÛāīūṇṭḍśṛḥṃḷ"

inner = re.compile(rf"(?<=[{LETTER}]) ([ntdsrhml]) (?=[a-zâîûāīū])")
initial = re.compile(rf"(?<![{LETTER}])([SR]) (?=[a-zâîûāīū])")


def normalize(s: str) -> str:
    prev = None
    while prev != s:  # italics can be adjacent ("Sapi n d a" → "Sapiṇḍa"), so repeat until stable
        prev = s
        s = inner.sub(lambda m: ITALIC[m.group(1)], s)
    s = initial.sub(lambda m: INITIAL[m.group(1)], s)
    return s.translate(VOWELS)


def main(paths):
    for p in paths:
        data, fmt = load(p)
        changed = 0
        for e in data:
            t = e.get("text") or ""
            n = normalize(t)
            if n != t:
                e["text"] = n
                changed += 1
            if e.get("title"):
                e["title"] = normalize(e["title"])
        save(p, data, fmt)
        print(f"{p}: {changed} entries normalised")


if __name__ == "__main__":
    main(sys.argv[1:])
