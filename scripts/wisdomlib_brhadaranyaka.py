#!/usr/bin/env python3
"""
Scrape Brhadaranyaka Upanishad from wisdomlib.org
Extracts: Sanskrit (Devanagari), IAST transliteration, English translation
Source: Swami Madhavananda's translation with Shankaracharya's commentary
"""

import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://www.wisdomlib.org/hinduism/book/the-brihadaranyaka-upanishad"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "public", "data", "upanishads", "brhadaranyaka_upanishad.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (academic research; vedic-texts-project)",
}

# Section pages (skip chapter headers, prefaces, etc.)
SECTION_PAGES = [
    # Chapter I
    ("doc117893", 1, 1),
    ("doc117895", 1, 2),
    ("doc117898", 1, 3),
    ("doc117939", 1, 4),
    ("doc117941", 1, 5),
    ("doc117943", 1, 6),
    # Chapter II
    ("doc117945", 2, 1),
    ("doc117947", 2, 2),
    ("doc117948", 2, 3),
    ("doc117950", 2, 4),
    ("doc117952", 2, 5),
    ("doc117954", 2, 6),
    # Chapter III
    ("doc118302", 3, 1),
    ("doc118304", 3, 2),
    ("doc118354", 3, 3),
    ("doc118355", 3, 4),
    ("doc118356", 3, 5),
    ("doc118357", 3, 6),
    ("doc118358", 3, 7),
    ("doc118359", 3, 8),
    ("doc118360", 3, 9),
    # Chapter IV
    ("doc118991", 4, 1),
    ("doc120048", 4, 2),
    ("doc120049", 4, 3),
    ("doc122058", 4, 4),
    ("doc122154", 4, 5),
    ("doc122184", 4, 6),
    # Chapter V
    ("doc122186", 5, 1),
    ("doc122189", 5, 2),
    ("doc122190", 5, 3),
    ("doc122191", 5, 4),
    ("doc122192", 5, 5),
    ("doc122193", 5, 6),
    ("doc122194", 5, 7),
    ("doc122195", 5, 8),
    ("doc122196", 5, 9),
    ("doc122197", 5, 10),
    ("doc122198", 5, 11),
    ("doc122199", 5, 12),
    ("doc122200", 5, 13),
    ("doc122201", 5, 14),
    ("doc122208", 5, 15),
    # Chapter VI
    ("doc122210", 6, 1),
    ("doc122212", 6, 2),
    ("doc122230", 6, 3),
    ("doc122237", 6, 4),
    ("doc122239", 6, 5),
]


def extract_verses_from_page(html, chapter, section):
    """Extract verses from a wisdomlib section page."""
    soup = BeautifulSoup(html, "html.parser")
    verses = []

    # Find all <strong> tags containing "Verse X.Y.Z"
    verse_markers = []
    for strong in soup.find_all("strong"):
        text = strong.get_text().strip()
        m = re.match(r"Verse\s+(\d+\.\d+\.\d+)", text)
        if m:
            verse_markers.append((strong, m.group(1)))

    for i, (marker, ref) in enumerate(verse_markers):
        # Parse reference
        parts = ref.split(".")
        ch = int(parts[0])
        sec = int(parts[1])
        v_num = int(parts[2])

        # Find the blockquote after this marker (contains Sanskrit)
        parent = marker.parent
        bq = None
        if parent:
            bq = parent.find_next("blockquote")

        # Check if this blockquote belongs to us (not the next verse)
        if bq and i + 1 < len(verse_markers):
            next_marker = verse_markers[i + 1][0]
            # Make sure blockquote comes before next marker
            if bq.sourceline and next_marker.sourceline:
                if bq.sourceline > next_marker.sourceline:
                    bq = None

        sanskrit = ""
        iast = ""
        if bq:
            bq_text = bq.get_text().strip()
            # Split into Devanagari and IAST parts
            # Devanagari uses Unicode range 0900-097F
            lines = bq_text.split("\n")
            dev_lines = []
            iast_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Check if line has Devanagari characters
                has_devanagari = any("\u0900" <= c <= "\u097F" for c in line)
                if has_devanagari:
                    dev_lines.append(line)
                elif line and re.search(r"[a-zA-Zāīūṛṝḷṃḥśṣṭḍṇñṅ]", line):
                    iast_lines.append(line)

            sanskrit = " ".join(dev_lines).strip()
            iast = " ".join(iast_lines).strip()

            # Clean verse numbers from end (॥ 1 ॥ etc)
            sanskrit = re.sub(r"\s*॥\s*\d+\s*॥\s*$", "", sanskrit).strip()

        # Find English translation — it's the paragraph(s) after the blockquote
        # that contain the actual translation (usually starts with explanatory text)
        translation = ""
        if bq:
            # Look for translation text after the blockquote
            next_elem = bq.find_next_sibling()
            while next_elem:
                if next_elem.name == "blockquote":
                    break  # Hit next Sanskrit block
                if next_elem.name == "p":
                    text = next_elem.get_text().strip()
                    # Skip if it's a verse marker for next verse
                    if re.match(r"Verse\s+\d+\.\d+\.\d+", text):
                        break
                    # The translation is typically the first substantial paragraph
                    if text and len(text) > 20:
                        translation = text
                        break
                next_elem = next_elem.find_next_sibling()

        # Clean translation - remove footnote markers
        translation = re.sub(r"\[\d+\]", "", translation).strip()
        # Truncate overly long commentary - keep first 500 chars
        if len(translation) > 500:
            # Try to cut at a sentence boundary
            cut = translation[:500].rfind(".")
            if cut > 200:
                translation = translation[: cut + 1]
            else:
                translation = translation[:500] + "..."

        if sanskrit:  # Only add if we found Sanskrit text
            verses.append(
                {
                    "reference": ref,
                    "sanskrit_iast": iast,
                    "meaning": sanskrit,
                    "text": translation,
                    "mandala": ch,
                    "hymn": sec,
                    "verse": v_num,
                    "vedaId": "brhadaranyaka_upanishad",
                }
            )

    return verses


def main():
    print("=" * 60)
    print("Scraping Brhadaranyaka Upanishad from wisdomlib.org")
    print("=" * 60)

    all_verses = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for doc_id, chapter, section in SECTION_PAGES:
        url = f"{BASE}/d/{doc_id}.html"
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"  [FAIL] {chapter}.{section} — status {resp.status_code}")
                continue

            verses = extract_verses_from_page(resp.text, chapter, section)
            all_verses.extend(verses)
            print(f"  [{chapter}.{section}] {len(verses)} verses")
            time.sleep(0.5)  # Be respectful

        except Exception as e:
            print(f"  [ERROR] {chapter}.{section}: {e}")

    # Write output
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(all_verses)} verses")
    print(f"Output: {OUTPUT}")

    # Show a sample
    if all_verses:
        v = all_verses[0]
        print(f"\nSample (first verse):")
        print(f"  Ref: {v['reference']}")
        print(f"  Sanskrit: {v['meaning'][:80]}...")
        print(f"  IAST: {v['sanskrit_iast'][:80]}...")
        print(f"  English: {v['text'][:80]}...")


if __name__ == "__main__":
    main()
