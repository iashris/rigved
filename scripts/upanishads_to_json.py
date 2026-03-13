#!/usr/bin/env python3
"""
Convert upanishads.org.in Firebase data to our standard JSON format.

Source: https://upanishad-535c0.firebaseio.com/
Fields available: verse_skt (Devanagari), verse_tl (IAST), meaning_en, glossary, hindi_explain
"""

import json
import os
import re

RAW_DIR = os.path.join(os.path.dirname(__file__), "upanishads_raw")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "data", "upanishads")

# Map Firebase IDs to our vedaId and output filename
UPANISHAD_MAP = {
    1:  {"vedaId": "isha_upanishad",         "file": "isha_upanishad.json"},
    2:  {"vedaId": "kena_upanishad",          "file": "kena_upanishad.json"},
    3:  {"vedaId": "katha_upanishad",         "file": "katha_upanishad.json"},
    4:  {"vedaId": "mundaka_upanishad",       "file": "mundaka_upanishad.json"},
    5:  {"vedaId": "mandukya_upanishad",      "file": "mandukya_upanishad.json"},
    6:  {"vedaId": "prasna_upanishad",        "file": "prasna_upanishad.json"},
    7:  {"vedaId": "taittiriya_upanishad",    "file": "taittiriya_upanishad.json"},
    8:  {"vedaId": "aitareya_upanishad",      "file": "aitareya_upanishad.json"},
    9:  {"vedaId": "svetasvatara_upanishad",  "file": "svetasvatara_upanishad.json"},
    11: {"vedaId": "chandogya_upanishad",     "file": "chandogya_upanishad.json"},
}


def clean_text(s):
    """Clean up text - fix spacing, remove excess whitespace."""
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    # Fix common HTML entities that might have leaked through
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return s


def process_verse(verse, chapter_num, section_num, verse_num, veda_id):
    """Convert a single verse from Firebase format to our format."""
    skt = clean_text(verse.get("verse_skt", ""))
    tl = clean_text(verse.get("verse_tl", ""))
    meaning = clean_text(verse.get("meaning_en", ""))

    # Build reference string
    if section_num > 0:
        ref = f"{chapter_num}.{section_num}.{verse_num}"
    elif chapter_num > 0:
        ref = f"{chapter_num}.{verse_num}"
    else:
        ref = str(verse_num)

    entry = {
        "reference": ref,
        "sanskrit_iast": tl,
        "meaning": skt,  # Devanagari goes in meaning field (matches our UI convention)
        "text": meaning,  # English translation
        "mandala": chapter_num if chapter_num > 0 else 1,
        "hymn": section_num if section_num > 0 else verse_num,
        "verse": verse_num,
        "vedaId": veda_id,
    }
    return entry


def convert_upanishad(firebase_id):
    """Convert one upanishad from Firebase JSON to our format."""
    config = UPANISHAD_MAP[firebase_id]
    veda_id = config["vedaId"]
    outfile = config["file"]

    inpath = os.path.join(RAW_DIR, f"{firebase_id}.json")
    outpath = os.path.join(DATA_DIR, outfile)

    with open(inpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title_tl", "unknown")
    entries = []

    if "verses" in data and not "chapters" in data:
        # Flat structure (Isha, Mandukya)
        for i, verse in enumerate(data["verses"]):
            entry = process_verse(verse, 0, 0, i + 1, veda_id)
            entries.append(entry)

    elif "chapters" in data:
        for ch_idx, chapter in enumerate(data["chapters"]):
            ch_num = ch_idx + 1

            if "sections" in chapter:
                # Chapters with sections (Katha, Mundaka, Taittiriya, Chandogya)
                for sec_idx, section in enumerate(chapter["sections"]):
                    sec_num = sec_idx + 1
                    for v_idx, verse in enumerate(section.get("verses", [])):
                        entry = process_verse(verse, ch_num, sec_num, v_idx + 1, veda_id)
                        entries.append(entry)
            else:
                # Chapters without sections (Kena, Prasna, Aitareya, Svetasvatara)
                for v_idx, verse in enumerate(chapter.get("verses", [])):
                    entry = process_verse(verse, ch_num, 0, v_idx + 1, veda_id)
                    entries.append(entry)

    # Write output
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"  [{veda_id}] {title}: {len(entries)} verses → {outfile}")
    return len(entries)


def main():
    print("=" * 60)
    print("Converting upanishads.org.in data to project JSON")
    print("=" * 60)

    total = 0
    for fid in sorted(UPANISHAD_MAP.keys()):
        raw_path = os.path.join(RAW_DIR, f"{fid}.json")
        if not os.path.exists(raw_path):
            print(f"  [skip] ID {fid} not downloaded")
            continue
        total += convert_upanishad(fid)

    print(f"\nTotal: {total} verses across {len(UPANISHAD_MAP)} upanishads")
    print(f"Output: {DATA_DIR}")


if __name__ == "__main__":
    main()
