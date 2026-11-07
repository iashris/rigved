#!/usr/bin/env python3
"""Chapter concordances between the Sanskrit Purāṇas and their human translations, via concordance_build.

Run after build_library.py has written a catalog holding these texts, then run build_library.py again so the pairs are
marked available. The engine compares one block with one section, so each text is first gathered into reader blocks.

A shared chapter number beats a name match that points elsewhere, at WEAK score so the reader warns: reading the
disagreements showed the numbers right more often, whatever the score. The exception is a match on the same number's
repeat (169 -> 169-r2), where the source printed a number twice and only the names can tell the copies apart.
Some translation blocks hold several chapters because the source lost their headings (Subba Rau 10.47 runs through
10.49), so an unsure block between two neighbours on one section joins that section.
A translation of only part of a text names its books in `en_covers`; the others get no match rather than a false one.

Usage: python3 -I scripts/corpus2/pramana_purana_concordance.py [id ...]
"""
import collections
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concordance_build as engine  # noqa: E402
from build_library import norm_ref  # noqa: E402
from pramana_purana_texts import PURANAS  # noqa: E402

ROOT = os.path.join(HERE, "..", "..")
DATA = os.path.join(ROOT, "public", "data", "puranas")
OUT = os.path.join(ROOT, "public", "library", "concordance")
CATALOG = os.path.join(ROOT, "public", "library", "catalog.json")
TRUST, WEAK = 0.5, 0.3


def blocks_of(text_id, depth):
    blocks = collections.OrderedDict()
    for e in json.load(open(os.path.join(DATA, text_id + ".json"), encoding="utf-8")):
        blocks.setdefault(".".join(norm_ref(e["reference"]).split(".")[:depth]), []).append(e)
    return blocks


def prepare(work, sa, en, depth, covers):
    rows = [{"reference": f"{k}.{i}", "sanskrit_iast": e["sanskrit_iast"]} for k, es in blocks_of(sa, depth[sa]).items()
            if not covers or k.split(".")[0] in covers for i, e in enumerate(es)]
    json.dump(rows, open(os.path.join(work, sa + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    sections = blocks_of(en, depth[en])
    rows = [{"reference": k, "title": " ".join(e["title"] for e in es if e.get("title")), "text": "\n".join(e["text"] for e in es)} for k, es in sections.items()]
    json.dump(rows, open(os.path.join(work, en + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    return set(sections)


def trust_numbers(mapping, sections):
    kept = 0
    for key, runs in mapping.items():
        if key in sections and not any(r["ref"] == key or r["ref"].startswith(key + "-r") for r in runs):
            mapping[key] = [{"ref": key, "score": WEAK}]
            kept += 1
    keys = list(mapping)
    for before, key, after in zip(keys, keys[1:], keys[2:]):
        a, b = mapping[before], mapping[after]
        if key not in sections and a and b and a[-1]["ref"] == b[0]["ref"] and max((r["score"] for r in mapping[key]), default=0) < TRUST:
            mapping[key] = [{"ref": a[-1]["ref"], "score": WEAK}]
    return kept


def write(out, sa, en):
    high = sum(1 for v in out["map"].values() if v and max(r["score"] for r in v) >= 0.6)
    empty = sum(1 for v in out["map"].values() if not v)
    out["stats"] = {"blocks": len(out["map"]), "highConfidence": high, "lowConfidence": len(out["map"]) - high - empty, "unmatched": empty}
    out["method"] += f" A shared chapter number replaces a match elsewhere, at score {WEAK}; so does a section both neighbours share."
    rows = ",\n".join(f"    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v)}" for k, v in out["map"].items())
    head = "".join(f"  {json.dumps(k)}: {json.dumps(out[k], ensure_ascii=False)},\n" for k in ("source", "translation", "sourceLevel", "method"))
    with open(os.path.join(OUT, f"{sa}__{en}.json"), "w", encoding="utf-8") as f:
        f.write("{\n" + head + '  "map": {\n' + rows + '\n  },\n  "stats": ' + json.dumps(out["stats"]) + "\n}\n")
    return out["stats"]


def main():
    only = set(sys.argv[1:])
    depth = {t["id"]: t["blockDepth"] for t in json.load(open(CATALOG, encoding="utf-8"))["texts"]}
    for sa, t in PURANAS.items():
        if not t.get("en") or (only and sa not in only):
            continue
        en = f"{sa}_{t['en_name'].lower().replace(' ', '')}"
        with tempfile.TemporaryDirectory() as work:
            sections = prepare(work, sa, en, depth, t.get("en_covers"))
            engine.DATA = engine.OUTDIR = work
            out = engine.build(sa, en, engine.build(sa, en, write=False))
        kept = trust_numbers(out["map"], sections)
        print(sa, "->", en, write(out, sa, en), f"chapter number kept over the name match for {kept}", flush=True)


if __name__ == "__main__":
    main()
