#!/usr/bin/env python3
"""Convert the cached Pramāṇa texts of pramana_canon_texts into public/data/<dir>/*.json, with the Purāṇa converter.

Prints a line per file, and stops on a file with no entries or a Sanskrit file whose text is not IAST, which the
converter would otherwise store in the wrong field. Set PRAMANA_SA_WORK to the fetch's cache folder.

Usage: python3 -I scripts/corpus2/pramana_canon_convert.py [id ...]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import pramana_purana_convert as engine  # noqa: E402
from pramana_canon_texts import CANON  # noqa: E402
from pramana_sa_common import segments  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


NOTE_MARK = re.compile(r"\[\[?\d+\]\]?")
SITE_NOTE = re.compile(r"https?://|wisdomlib|sacred-texts\.com", re.I)


def english_id(cid, t):
    return f"{cid}_{t['en_name'].lower().replace(' ', '')}"


def clean_english(entries):
    """Drop what the hosting site added: its stub for an absent Sanskrit verse, marks for footnotes the converter leaves
    out, and any entry that is the site's own note."""
    out = []
    for e in entries:
        if SITE_NOTE.search(e["text"]):
            print("  site note dropped:", e["reference"], e["text"][:80].replace("\n", " "), flush=True)
            continue
        e["text"] = NOTE_MARK.sub("", e["text"].replace("[Sanskrit available]", "")).strip()
        if e["text"]:
            out.append(e)
    return out


def write(entries, folder, name):
    if not entries:
        raise SystemExit(f"{name}: no entries")
    engine.OUT = os.path.join(DATA, folder)
    return engine.write(entries, name)


def main():
    only = set(sys.argv[1:])
    for cid, t in CANON.items():
        if only and cid not in only:
            continue
        folder = t.get("attach") or t["dir"]
        if t.get("sa"):
            entries, stats = engine.convert(segments(t["sa"]), False)
            text = "".join(e["sanskrit_iast"] for e in entries)
            share = len(DEVANAGARI.findall(text)) / max(len(text), 1)
            if share > 0.05:
                raise SystemExit(f"{cid}: {share:.0%} Devanagari in the IAST field")
            print(f"{cid}: {len(entries)} entries, {write(entries, folder, cid):.1f} MB, {dict(stats)}", flush=True)
        if t.get("en"):
            name = english_id(cid, t)
            entries, stats = engine.convert(segments(t["en"]), True)
            entries = clean_english(entries)
            print(f"{name}: {len(entries)} entries, {write(entries, folder, name):.1f} MB, {dict(stats)}", flush=True)


if __name__ == "__main__":
    main()
