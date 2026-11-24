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
    return t.get("en_existing") or f"{cid}_{t['en_name'].lower().replace(' ', '')}"


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


# GRETIL's file header, which Pramāṇa keeps as text when a work is split into several GRETIL files (the Rāmcaritmānas,
# one per book): the encoding notes are dropped, and the line naming the book becomes the next entry's title.
GRETIL_HEADER = re.compile(r"^(Text converted to Unicode|set to UTF-8|nasalized a |intervocalic y |Unless indicated otherwise, accents"
                           r"|For a comprehensive list of GRETIL)")
GRETIL_BOOK = re.compile(r"^[^\n]{0,120}\bSopana (\d+): (\w+)$")
KANDA = {"Balakanda": "Bālakāṇḍa", "Ayodhyakanda": "Ayodhyākāṇḍa", "Aranyakanda": "Araṇyakāṇḍa", "Kiskindhakanda": "Kiṣkindhākāṇḍa",
         "Sundarakanda": "Sundarakāṇḍa", "Lankakanda": "Laṅkākāṇḍa", "Uttarakanda": "Uttarakāṇḍa"}


def drop_gretil_header(entries):
    out, title = [], None
    for e in entries:
        t = (e.get("sanskrit_iast") or "").strip()
        m = GRETIL_BOOK.match(t)
        if m:
            title = f"Sopāna {m.group(1)}: {KANDA.get(m.group(2), m.group(2))}"
            continue
        if GRETIL_HEADER.match(t):
            continue
        if title:
            e["title"] = title
            title = None
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
            mt = {x["loc"]: x["text"] or "" for x in segments(t["mt"])} if t.get("mt") else None
            entries, stats = engine.convert(segments(t["sa"]), False, mt)
            entries = drop_gretil_header(entries)
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
