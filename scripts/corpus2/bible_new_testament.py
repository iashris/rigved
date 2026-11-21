#!/usr/bin/env python3
"""The New Testament for the comparative shelf: the Greek Textus Receptus beside the King James English.

Greek: the Textus Receptus, the printed Greek the King James translators worked from; English: the King James Version
(1611). Both are public domain (the KJV's Crown patent binds printers in the United Kingdom only) and both come from
eBible.org's verse-per-line exports (grctr, eng-kjv), in the same versification, so every English verse sits beside
the Greek it translates; the script stops if the two disagree on a single verse. The KJV is chosen over the ASV (1901)
for that reason: the ASV follows a different Greek, and would sit beside the Textus Receptus as a translation of
something else.

The KJV prints words its translators supplied in italics; eBible marks them with brackets, which are dropped here, as
are its ¶ paragraph marks.

Books are in the usual order, Matthew to Revelation, each its own text in the library, grouped as Gospels and Acts,
Letters of Paul, Hebrews and the General Letters, and Revelation. Writes public/data/bible/<id>.json and adds the books
to library_catalog.json and translation_sources.json. Rerunnable; downloads are cached in cache/ebible.

Usage: python3 -I scripts/corpus2/bible_new_testament.py
"""
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "ebible")
OUT = os.path.join(ROOT, "public", "data", "bible")
GREEK, ENGLISH = "grctr", "eng-kjv"

# (eBible VPL code, name shown, group)
BOOKS = [
    ("MAT", "Matthew", "gospels"),
    ("MAR", "Mark", "gospels"),
    ("LUK", "Luke", "gospels"),
    ("JOH", "John", "gospels"),
    ("ACT", "Acts", "gospels"),
    ("ROM", "Romans", "paul"),
    ("1CO", "1 Corinthians", "paul"),
    ("2CO", "2 Corinthians", "paul"),
    ("GAL", "Galatians", "paul"),
    ("EPH", "Ephesians", "paul"),
    ("PHI", "Philippians", "paul"),
    ("COL", "Colossians", "paul"),
    ("1TH", "1 Thessalonians", "paul"),
    ("2TH", "2 Thessalonians", "paul"),
    ("1TI", "1 Timothy", "paul"),
    ("2TI", "2 Timothy", "paul"),
    ("TIT", "Titus", "paul"),
    ("PHM", "Philemon", "paul"),
    ("HEB", "Hebrews", "general"),
    ("JAM", "James", "general"),
    ("1PE", "1 Peter", "general"),
    ("2PE", "2 Peter", "general"),
    ("1JO", "1 John", "general"),
    ("2JO", "2 John", "general"),
    ("3JO", "3 John", "general"),
    ("JUD", "Jude", "general"),
    ("REV", "Revelation", "revelation"),
]

sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

BAND = {"id": "new_testament", "after": ["old_testament", "avesta", "travel"], "name": "New Testament",
        "blurb": "not Indic: the Christian scriptures, for comparison — John's Word that was in the beginning beside Vāc, the Ṛgveda's Speech (10.125). "
                 "Greek with the King James English",
        "groups": [{"id": "gospels", "name": "Gospels and Acts", "blurb": "the life of Jesus four times told, and the first church"},
                   {"id": "paul", "name": "Letters of Paul", "blurb": "Romans to Philemon"},
                   {"id": "general", "name": "Hebrews and the General Letters", "blurb": "Hebrews, James, Peter, John and Jude"},
                   {"id": "revelation", "name": "Revelation", "blurb": "John's vision of the end: the dragon cast down, the new Jerusalem"}]}
ORIGINAL = {"name": "Greek", "lang": "grc", "label": "Ἑλληνικά", "short": "Ἑλ"}
SOURCE = "Greek: Textus Receptus (eBible.org); English: King James Version (1611)"
CREDIT = {"english": {"by": "the King James translators", "work": "The Holy Bible, Conteyning the Old Testament, and the New, London: Robert Barker",
                      "year": "1611", "links": [{"label": "eBible.org", "url": "https://ebible.org/find/details.php?id=eng-kjv"}],
                      "via": {"label": "eBible.org", "url": "https://ebible.org/Scriptures/"},
                      "note": "Greek: the Textus Receptus, the text the King James translators worked from (eBible.org, grctr), in the same verse numbering. "
                              "Words the translators supplied, printed in italics in the KJV, are set in roman here."}}
LINE = re.compile(r"^(\S+) (\d+):(\d+) (.*)$")


def fetch(edition):
    """eBible's verse-per-line text: {(book, chapter, verse): text}, in file order."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"{edition}_vpl.zip")
    if not os.path.exists(f):
        url = f"https://ebible.org/Scriptures/{edition}_vpl.zip"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rigved-corpus-research/1.0"}), timeout=120) as r:
            open(f, "wb").write(r.read())
        time.sleep(0.5)
    z = zipfile.ZipFile(f)
    about = z.read(f"{edition}_about.htm").decode("utf-8")
    if "Public Domain" not in about:
        raise SystemExit(f"{edition} is not marked public domain on its about page")
    verses = {}
    for ln in io.TextIOWrapper(z.open(f"{edition}_vpl.txt"), encoding="utf-8-sig"):
        m = LINE.match(ln.rstrip("\n"))
        if m:
            verses[(m[1], int(m[2]), int(m[3]))] = m[4]
    return verses


def clean(v):
    v = re.sub(r"\s+", " ", v.replace("¶", "").replace("[", "").replace("]", "")).strip()
    if re.search(r"[<>{}\\]", v) or not v:
        raise SystemExit(f"markup or nothing left in verse: {v[:120]!r}")
    return v


def slug(name):
    return "nt_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    os.makedirs(OUT, exist_ok=True)
    gr, en = fetch(GREEK), fetch(ENGLISH)
    codes = {b[0] for b in BOOKS}
    if {k[0] for k in gr} != codes:
        raise SystemExit(f"{GREEK}: books {sorted({k[0] for k in gr} ^ codes)} differ from the list here")
    texts, records = [], {}
    for code, name, group in BOOKS:
        g = [k for k in gr if k[0] == code]
        e = [k for k in en if k[0] == code]
        if g != e:
            raise SystemExit(f"{name}: Greek and English number the verses differently: {sorted(set(g) ^ set(e))[:10]}")
        rows = [{"reference": f"{c}.{v}", "original": clean(gr[k]), "text": clean(en[k])} for k in g for (_, c, v) in [k]]
        tid = slug(name)
        with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        texts.append({"id": tid, "file": f"bible/{tid}.json", "name": name, "band": "new_testament", "group": group,
                      "levels": ["Chapter", "Verse"], "original": ORIGINAL, "source": SOURCE})
        records[tid] = CREDIT
        print(f"{tid:22s} {g[-1][1]:4d} chapters {len(rows):5d} verses")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
