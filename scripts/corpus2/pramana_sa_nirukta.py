#!/usr/bin/env python3
"""Compare Pramāṇa's Nirukta (in.vedanga.nirukta.yaska) with our public/data/other/nirukta.json on 10 random
khaṇḍas and count known e-text faults. Read-only: prints the evidence for keeping or replacing our file."""
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_sa_common import page, segments  # noqa: E402

P = {s["loc"]: s["text"] for s in segments("in.vedanga.nirukta.yaska") if s["text"]}
O = {e["reference"]: e["sanskrit_iast"] for e in json.load(open(os.path.join(HERE, "..", "..", "public", "data", "other", "nirukta.json"), encoding="utf-8"))}
print("khaṇḍas: Pramāṇa", len(P), "ours", len(O), "same refs:", set(P) == set(O))
random.seed(7)
for r in random.sample(sorted(O), 10):
    print(f"== {r}\n OURS: {O[r][:160]}\n PRAM: {P.get(r, '')[:160]!r}")
for name, d in (("ours", O), ("pramana", P)):
    t = " ".join(d.values())
    print(name, {"'caste' (for caṣṭe)": len(re.findall(r"\bcaste\b", t)), "word-final -ah/-ih/-uh (h for ḥ)": len(re.findall(r"[aiu]h\b", t)),
                 "digits glued to words": len(re.findall(r"[a-zāīūṛṃḥ]\d|\d[a-zāīūṛṃḥ]", t)), "[apparatus]": t.count("[")})
print("Pramāṇa source:", [(p["repo"], p["edition"]) for p in page("in.vedanga.nirukta.yaska")["provenance"]])
