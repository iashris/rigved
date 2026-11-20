#!/usr/bin/env python3
"""The Old Testament for the comparative shelf: Hebrew beside the English of the 1917 Jewish Publication Society.

Hebrew: the Westminster Leningrad Codex with vowel points (no cantillation), as tanach.us publishes it; English: The
Holy Scriptures According to the Masoretic Text, A New Translation (JPS, 1917). Both are public domain and both come
from Sefaria's export (storage.googleapis.com/sefaria-export), which holds them in the same Hebrew versification, so
every verse of the English sits beside its own Hebrew; the script stops if a chapter's verse counts disagree.
JPS 1917 is chosen over the King James for that reason: the KJV numbers verses differently in the Psalms' titles,
Joel, Malachi and elsewhere, and would need a verse map.

Books are in the Protestant Old Testament's order, Genesis to Malachi, each its own text in the library, grouped as
Torah, History, Poetry and Wisdom, and Prophets. Writes public/data/bible/<id>.json and adds the books to
library_catalog.json and translation_sources.json. Rerunnable; downloads are cached in cache/sefaria.

Usage: python3 -I scripts/corpus2/bible_old_testament.py
"""
import json
import sys
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "sefaria")
OUT = os.path.join(ROOT, "public", "data", "bible")
CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
GCS = "https://storage.googleapis.com/sefaria-export/json/Tanakh"
HE = "Tanach with Nikkud"
EN = "The Holy Scriptures A New Translation JPS 1917"

# (Sefaria name, Sefaria section, name shown, group)
BOOKS = [
    ("Genesis", "Torah", "Genesis", "torah"),
    ("Exodus", "Torah", "Exodus", "torah"),
    ("Leviticus", "Torah", "Leviticus", "torah"),
    ("Numbers", "Torah", "Numbers", "torah"),
    ("Deuteronomy", "Torah", "Deuteronomy", "torah"),
    ("Joshua", "Prophets", "Joshua", "history"),
    ("Judges", "Prophets", "Judges", "history"),
    ("Ruth", "Writings", "Ruth", "history"),
    ("I Samuel", "Prophets", "1 Samuel", "history"),
    ("II Samuel", "Prophets", "2 Samuel", "history"),
    ("I Kings", "Prophets", "1 Kings", "history"),
    ("II Kings", "Prophets", "2 Kings", "history"),
    ("I Chronicles", "Writings", "1 Chronicles", "history"),
    ("II Chronicles", "Writings", "2 Chronicles", "history"),
    ("Ezra", "Writings", "Ezra", "history"),
    ("Nehemiah", "Writings", "Nehemiah", "history"),
    ("Esther", "Writings", "Esther", "history"),
    ("Job", "Writings", "Job", "wisdom"),
    ("Psalms", "Writings", "Psalms", "wisdom"),
    ("Proverbs", "Writings", "Proverbs", "wisdom"),
    ("Ecclesiastes", "Writings", "Ecclesiastes", "wisdom"),
    ("Song of Songs", "Writings", "Song of Songs", "wisdom"),
    ("Isaiah", "Prophets", "Isaiah", "prophets"),
    ("Jeremiah", "Prophets", "Jeremiah", "prophets"),
    ("Lamentations", "Writings", "Lamentations", "prophets"),
    ("Ezekiel", "Prophets", "Ezekiel", "prophets"),
    ("Daniel", "Writings", "Daniel", "prophets"),
    ("Hosea", "Prophets", "Hosea", "prophets"),
    ("Joel", "Prophets", "Joel", "prophets"),
    ("Amos", "Prophets", "Amos", "prophets"),
    ("Obadiah", "Prophets", "Obadiah", "prophets"),
    ("Jonah", "Prophets", "Jonah", "prophets"),
    ("Micah", "Prophets", "Micah", "prophets"),
    ("Nahum", "Prophets", "Nahum", "prophets"),
    ("Habakkuk", "Prophets", "Habakkuk", "prophets"),
    ("Zephaniah", "Prophets", "Zephaniah", "prophets"),
    ("Haggai", "Prophets", "Haggai", "prophets"),
    ("Zechariah", "Prophets", "Zechariah", "prophets"),
    ("Malachi", "Prophets", "Malachi", "prophets"),
]


def fetch(section, book, lang, version):
    d = os.path.join(CACHE, book)
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{lang}.json")
    if not os.path.exists(f):
        url = f"{GCS}/{section}/{urllib.parse.quote(book)}/{'Hebrew' if lang == 'he' else 'English'}/{urllib.parse.quote(version)}.json"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rigved-corpus-research/1.0"}), timeout=120) as r:
            data = r.read()
        open(f, "wb").write(data)
        time.sleep(0.5)
    return json.load(open(f, encoding="utf-8"))


sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

BAND = {"id": "old_testament", "after": ["avesta", "travel"], "name": "Old Testament",
        "blurb": "not Indic: the Hebrew scriptures, for comparison — Yahweh's war with the sea-dragon beside Indra's with Vṛtra. Hebrew with the 1917 JPS English",
        "groups": [{"id": "torah", "name": "Torah", "blurb": "the five books of Moses: creation, the patriarchs, the Exodus, the Law"},
                   {"id": "history", "name": "History", "blurb": "Israel from the conquest of Canaan to the return from Babylon"},
                   {"id": "wisdom", "name": "Poetry and Wisdom", "blurb": "Job, the Psalms, Proverbs, Ecclesiastes, the Song of Songs"},
                   {"id": "prophets", "name": "Prophets", "blurb": "Isaiah to Malachi"}]}
ORIGINAL = {"name": "Hebrew", "lang": "he", "dir": "rtl", "label": "עברית", "short": "א"}
CREDIT = {"english": {"by": "Jewish Publication Society", "work": "The Holy Scriptures According to the Masoretic Text: A New Translation, Philadelphia",
                      "year": "1917", "links": [{"label": "Open Siddur", "url": "https://opensiddur.org/2010/08/%D7%AA%D7%A0%D7%B4%D7%9A-the-holy-scriptures-a-new-translation-jps-1917/"}],
                      "via": {"label": "Sefaria", "url": "https://www.sefaria.org/texts/Tanakh"},
                      "note": "Hebrew: the Westminster Leningrad Codex with vowel points (tanach.us), in the same verse numbering."}}
SMALL = re.compile(r"<br>\s*<small>(.*?)</small>")


def clean(v):
    """Four books end by repeating a kinder verse in the synagogue reading; the editions keep it, bracketed, after a break."""
    v = SMALL.sub(lambda m: "\n\n" + m.group(1), v)
    if "<" in v:
        raise SystemExit(f"markup left in verse: {v[:120]}")
    return v.strip()


def slug(name):
    return "ot_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for book, section, name, group in BOOKS:
        he, en = fetch(section, book, "he", HE), fetch(section, book, "en", EN)
        for d in (he, en):
            if d.get("license") != "Public Domain":
                raise SystemExit(f"{book}: {d.get('versionTitle')} is not marked public domain ({d.get('license')})")
        if [len(c) for c in he["text"]] != [len(c) for c in en["text"]]:
            raise SystemExit(f"{book}: Hebrew and English number the verses differently")
        rows = [{"reference": f"{c}.{v}", "original": clean(h), "text": clean(e)}
                for c, (hc, ec) in enumerate(zip(he["text"], en["text"]), 1) for v, (h, e) in enumerate(zip(hc, ec), 1)]
        tid = slug(name)
        with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        texts.append({"id": tid, "file": f"bible/{tid}.json", "name": name, "band": "old_testament", "group": group,
                      "levels": ["Psalm" if book == "Psalms" else "Chapter", "Verse"], "original": ORIGINAL,
                      "source": "Hebrew: Westminster Leningrad Codex (tanach.us); English: Jewish Publication Society (1917)"})
        records[tid] = CREDIT
        print(f"{tid:22s} {len(he['text']):4d} chapters {len(rows):5d} verses")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
