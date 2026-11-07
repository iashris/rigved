#!/usr/bin/env python3
"""Concordances for pramana_canon_texts: each Sanskrit block maps to the English blocks that share its number.

Most texts follow the same chapter numbers on both sides, which the converter keeps from Pramāṇa. A minor Upaniṣad is
short and its English is numbered in one run, so its whole English sits beside every section. A text marked `match`
in pramana_canon_texts needs more: "names" goes through the name-matching engine, "near" pairs at low confidence.

Run after build_library.py has written a catalog holding these texts, then run build_library.py again so the pairs are
marked available. Usage: python3 -I scripts/corpus2/pramana_canon_concordance.py [id ...]
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concordance_build as engine  # noqa: E402
import pramana_purana_concordance as by_names  # noqa: E402
from pramana_canon_convert import DATA, english_id  # noqa: E402
from pramana_canon_texts import CANON  # noqa: E402

ROOT = os.path.join(HERE, "..", "..")
OUT = os.path.join(ROOT, "public", "library", "concordance")
CATALOG = os.path.join(ROOT, "public", "library", "catalog.json")
NUMBERING = "Blocks matched by their shared chapter number in Pramāṇa's numbering."
NOTES = {"numbering": "Paired by chapter number; the two sides may divide a chapter differently.",
         "whole": "This short text is shown whole beside each section.",
         "names": "Matched by the names both sides share, so sections may start or end at different verses."}
NEAR = "Chapters paired by number, but the Sanskrit and the translation follow different editions, so a pair may be a chapter or so out."
WEAK = 0.3
WHOLE = "The whole translation beside every section: this short text is numbered in one run in the translation."


ALIAS_BOOK = [False]


def named(cid, en, folder, depth):
    by_names.DATA = os.path.join(DATA, folder)
    with tempfile.TemporaryDirectory() as work:
        sections = by_names.prepare(work, cid, en, depth, None)
        engine.DATA = engine.OUTDIR = work
        out = engine.build(cid, en, engine.build(cid, en, write=False))
    by_names.trust_numbers(out["map"], sections)
    stats = by_names.write(out, cid, en)
    path = os.path.join(OUT, f"{cid}__{en}.json")
    written = json.load(open(path, encoding="utf-8"))
    json.dump({**written, "note": NOTES["names"]}, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return stats


def block_keys(nodes):
    keys = []
    for n in nodes:
        if isinstance(n[2], int):
            keys.append(n[0])
        else:
            keys += block_keys(n[2])
    return keys


def alias(key):
    """Nārada's Sanskrit numbers its titles v1, v2…; Jolly numbers the same titles 1, 2… Bṛhaspati's Sanskrit keeps its
    chapters in a book 1 that Jolly does not have."""
    if key[:1] == "v" and key[1:].isdigit():
        return key[1:]
    return key[2:] if key.startswith("1.") and key[2:].isdigit() and ALIAS_BOOK[0] else key


def matches(key, blocks):
    k = alias(key)
    return [b for b in blocks if b == k or b.startswith(k + ".") or k.startswith(b + ".")]


def main():
    only = set(sys.argv[1:])
    texts = {t["id"]: t for t in json.load(open(CATALOG, encoding="utf-8"))["texts"]}
    for cid, t in CANON.items():
        if not t.get("en") or (only and cid not in only):
            continue
        en = english_id(cid, t)
        if t.get("match") == "names":
            print(f"{cid:32} by names {named(cid, en, t.get('attach') or t['dir'], {k: v['blockDepth'] for k, v in texts.items()})}", flush=True)
            continue
        keys, blocks = block_keys(texts[cid]["toc"]), block_keys(texts[en]["toc"])
        whole = cid.endswith("_upanishad")
        near = t.get("match") == "near"
        ALIAS_BOOK[0] = near
        score = WEAK if near else 1
        mapping = {k: [{"ref": b, "score": score} for b in (blocks if whole else matches(k, blocks))] for k in keys}
        empty = sum(1 for v in mapping.values() if not v)
        hit = {r["ref"] for v in mapping.values() for r in v}
        out = {"source": cid, "translation": en, "method": WHOLE if whole else NEAR if near else NUMBERING,
               "note": NOTES["whole" if whole else "numbering"], "map": mapping,
               "stats": {"blocks": len(keys), "highConfidence": 0 if near else len(keys) - empty, "lowConfidence": len(keys) - empty if near else 0, "unmatched": empty}}
        with open(os.path.join(OUT, f"{cid}__{en}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        print(f"{cid:32} blocks {len(keys):5}  unmatched {empty:5}  English blocks unused {len(set(blocks) - hit):4} of {len(blocks)}", flush=True)


if __name__ == "__main__":
    main()
