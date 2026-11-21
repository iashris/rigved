#!/usr/bin/env python3
"""The Apocrypha for the comparative shelf: the Septuagint's Greek books beside Brenton's English.

The books the Greek Old Testament holds and the Hebrew does not: Tobit, Judith, Wisdom, Sirach, Baruch, the
Maccabees and the rest, with Esther and Daniel in their longer Greek forms (Susanna, and Bel and the Dragon, are
also given apart, as the English Bibles print them). Greek: the Septuagint as Sir Lancelot Brenton printed it;
English: Brenton's translation (1844–51). Both public domain, from eBible.org's verse-per-line exports (grcbrent,
eng-Brenton), in the same verse numbering; the script stops if they disagree on a single verse. Brenton's supplied
words, bracketed in the export, are set in roman like the rest.

Writes public/data/bible/<id>.json and adds the books to library_catalog.json and translation_sources.json.
Rerunnable; downloads are cached in cache/ebible.

Usage: python3 -I scripts/corpus2/bible_apocrypha.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "data", "bible")
sys.path.insert(0, HERE)
from bible_new_testament import clean, fetch  # noqa: E402
from comparative_catalog import write  # noqa: E402

# (eBible code, name shown, group)
BOOKS = [
    ("TOB", "Tobit", "stories"),
    ("JDT", "Judith", "stories"),
    ("ESG", "Esther (Greek)", "stories"),
    ("DNG", "Daniel (Greek)", "stories"),
    ("SUS", "Susanna", "stories"),
    ("BEL", "Bel and the Dragon", "stories"),
    ("WIS", "Wisdom of Solomon", "wisdom"),
    ("SIR", "Sirach (Ecclesiasticus)", "wisdom"),
    ("BAR", "Baruch", "wisdom"),
    ("EPJ", "Letter of Jeremiah", "wisdom"),
    ("PRM", "Prayer of Manasseh", "wisdom"),
    ("1MA", "1 Maccabees", "history"),
    ("2MA", "2 Maccabees", "history"),
    ("3MA", "3 Maccabees", "history"),
    ("4MA", "4 Maccabees", "history"),
    ("1ES", "1 Esdras", "history"),
]
BAND = {"id": "apocrypha", "after": ["old_testament"], "name": "Apocrypha",
        "blurb": "not Indic: the books of the Greek Old Testament that the Hebrew lacks — Bel and the Dragon, Daniel slaying the serpent the "
                 "Babylonians worshipped. Septuagint Greek with Brenton's English",
        "groups": [{"id": "stories", "name": "Stories", "blurb": "Tobit, Judith, and Esther and Daniel as the Greek tells them"},
                   {"id": "wisdom", "name": "Wisdom and Prayer", "blurb": "Wisdom of Solomon, Sirach, Baruch, the Prayer of Manasseh"},
                   {"id": "history", "name": "History", "blurb": "the Maccabees' revolt and 1 Esdras"}]}
ORIGINAL = {"name": "Greek", "lang": "grc", "label": "Ἑλληνικά", "short": "Ἑλ"}
SOURCE = "Greek: Septuagint, ed. Brenton (eBible.org); English: L. C. L. Brenton (1844–51)"
CREDIT = {"english": {"by": "Sir Lancelot C. L. Brenton", "work": "The Septuagint Version of the Old Testament, with an English Translation, London: Samuel Bagster",
                      "year": "1844–51", "links": [{"label": "eBible.org", "url": "https://ebible.org/find/details.php?id=eng-Brenton"}],
                      "via": {"label": "eBible.org", "url": "https://ebible.org/Scriptures/"},
                      "note": "Greek: the Septuagint as Brenton printed it (eBible.org, grcbrent), in the same verse numbering."}}


def slug(name):
    return "ap_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    os.makedirs(OUT, exist_ok=True)
    gr, en = fetch("grcbrent"), fetch("eng-Brenton")
    texts, records = [], {}
    for code, name, group in BOOKS:
        g = [k for k in gr if k[0] == code]
        e = [k for k in en if k[0] == code]
        if not g or g != e:
            raise SystemExit(f"{name}: Greek and English number the verses differently: {sorted(set(g) ^ set(e))[:10]}")
        rows = [{"reference": f"{c}.{v}", "original": clean(gr[k]), "text": clean(en[k])} for k in g for (_, c, v) in [k]]
        tid = slug(name)
        with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        texts.append({"id": tid, "file": f"bible/{tid}.json", "name": name, "band": "apocrypha", "group": group,
                      "levels": ["Chapter", "Verse"], "original": ORIGINAL, "source": SOURCE})
        records[tid] = CREDIT
        print(f"{tid:28s} {g[-1][1]:4d} chapters {len(rows):5d} verses")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
