#!/usr/bin/env python3
"""
Build Kausitaki Upanishad JSON from two sources:
- Sanskrit (Devanagari): sanskritdocuments.org
- English translation: vedarahasya.net (Dr. A. G. Krishna Warrier)
"""

import json
import os
import re
from bs4 import BeautifulSoup

RAW_DIR = os.path.join(os.path.dirname(__file__), "upanishads_raw")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "public", "data", "upanishads", "kausitaki_upanishad.json")

DEV_TO_INT = str.maketrans("०१२३४५६७८९", "0123456789")


def parse_sanskrit():
    """Parse Sanskrit verses from sanskritdocuments.org HTML."""
    with open(os.path.join(RAW_DIR, "kausitaki_sanskrit.html"), encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Find start of actual text
    start = text.find("चित्रो ह वै")
    if start > 0:
        text = text[start:]

    # Split into 4 chapters using actual chapter end markers
    ch_patterns = [
        r'प्रथमोऽध्यायः\s*॥\s*१\s*॥',
        r'द्वितीयोऽध्यायः\s*॥\s*२\s*॥',
        r'तृतीयोऽध्यायः\s*॥',
        r'चतुर्थोऽध्यायः\s*॥\s*४\s*॥',
    ]

    chapters = []
    remaining = text
    for pat in ch_patterns:
        m = re.search(pat, remaining)
        if m:
            chapters.append(remaining[:m.start()])
            remaining = remaining[m.end():]

    all_verses = {}

    for ch_idx, chapter_text in enumerate(chapters):
        ch_num = ch_idx + 1

        # Split by verse markers ॥ N ॥
        parts = re.split(r'॥\s*(\d+)\s*॥', chapter_text)

        current_text = ""
        for i in range(0, len(parts) - 1, 2):
            verse_text = parts[i].strip()
            verse_num_str = parts[i + 1].strip() if i + 1 < len(parts) else ""

            if not verse_num_str:
                current_text += " " + verse_text
                continue

            verse_num = int(verse_num_str.translate(DEV_TO_INT))
            full_text = (current_text + " " + verse_text).strip()
            current_text = ""

            if full_text:
                full_text = re.sub(r'\s+', ' ', full_text).strip()
                all_verses[(ch_num, verse_num)] = full_text

    return all_verses


def parse_english():
    """Parse English translation from vedarahasya.net."""
    with open(os.path.join(RAW_DIR, "kausitaki_english.html"), encoding="latin-1") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Fix encoding issues
    text = text.replace("\x96", "-").replace("\x93", '"').replace("\x94", '"')
    text = text.replace("\x91", "'").replace("\x92", "'")

    roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4}

    pattern = r'([IV]+)-(\d+)\.\s*'
    parts = re.split(pattern, text)

    all_verses = {}

    i = 1
    while i + 2 < len(parts):
        roman = parts[i]
        verse_num = int(parts[i + 1])
        content = parts[i + 2].strip()
        ch_num = roman_to_int.get(roman, 0)

        content = re.sub(r'\s+', ' ', content).strip()

        if ch_num and content:
            all_verses[(ch_num, verse_num)] = content

        i += 3

    return all_verses


def iast_from_devanagari(text):
    """Basic Devanagari to IAST transliteration."""
    vowel_map = {
        "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
        "ऋ": "ṛ", "ॠ": "ṝ", "ऌ": "ḷ", "ए": "e", "ऐ": "ai",
        "ओ": "o", "औ": "au",
    }
    matra_map = {
        "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
        "ृ": "ṛ", "ॄ": "ṝ", "ॢ": "ḷ", "े": "e", "ै": "ai",
        "ो": "o", "ौ": "au", "ं": "ṃ", "ः": "ḥ", "ँ": "m̐",
    }
    consonant_map = {
        "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
        "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
        "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
        "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
        "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
        "य": "y", "र": "r", "ल": "l", "व": "v",
        "श": "ś", "ष": "ṣ", "स": "s", "ह": "h",
    }
    virama = "्"

    result = []
    i = 0
    chars = list(text)
    while i < len(chars):
        c = chars[i]
        if c == virama:
            i += 1
            continue
        if c in consonant_map:
            result.append(consonant_map[c])
            if i + 1 < len(chars) and chars[i + 1] == virama:
                i += 2
            elif i + 1 < len(chars) and chars[i + 1] in matra_map:
                result.append(matra_map[chars[i + 1]])
                i += 2
            else:
                result.append("a")
                i += 1
        elif c in vowel_map:
            result.append(vowel_map[c])
            i += 1
        elif c in matra_map:
            result.append(matra_map[c])
            i += 1
        elif c == "ॐ":
            result.append("oṃ")
            i += 1
        elif c == "।":
            result.append("|")
            i += 1
        elif c == "॥":
            result.append("||")
            i += 1
        else:
            result.append(c)
            i += 1

    return "".join(result)


def main():
    print("=" * 60)
    print("Building Kausitaki Upanishad from two sources")
    print("=" * 60)

    sanskrit_verses = parse_sanskrit()
    english_verses = parse_english()

    print(f"  Sanskrit verses: {len(sanskrit_verses)}")
    print(f"  English verses: {len(english_verses)}")

    # Use English verse numbering as the canonical structure,
    # and match Sanskrit where available
    # Both sources have same structure: 4 chapters
    # English: Ch1=6, Ch2=15, Ch3=8, Ch4=20 = 49 total
    # Sanskrit: Ch1=7, Ch2=14(missing #2), Ch3=9, Ch4=20 = 50 total

    # Merge using union of keys
    all_keys = sorted(set(list(sanskrit_verses.keys()) + list(english_verses.keys())))

    entries = []
    for ch, v in all_keys:
        skt = sanskrit_verses.get((ch, v), "")
        eng = english_verses.get((ch, v), "")
        iast = iast_from_devanagari(skt) if skt else ""

        entries.append({
            "reference": f"{ch}.{v}",
            "sanskrit_iast": iast,
            "meaning": skt,
            "text": eng,
            "mandala": ch,
            "hymn": v,
            "verse": v,
            "vedaId": "kausitaki_upanishad",
        })

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    both = sum(1 for e in entries if e["meaning"] and e["text"])
    skt_only = sum(1 for e in entries if e["meaning"] and not e["text"])
    eng_only = sum(1 for e in entries if not e["meaning"] and e["text"])

    print(f"\n  Output: {len(entries)} verses → {os.path.basename(OUTPUT)}")
    print(f"  Both Sanskrit+English: {both}")
    print(f"  Sanskrit only: {skt_only}")
    print(f"  English only: {eng_only}")

    # Show samples
    for e in entries[:2]:
        print(f"\n  === {e['reference']} ===")
        print(f"  Dev: {e['meaning'][:80]}...")
        print(f"  IAST: {e['sanskrit_iast'][:80]}...")
        print(f"  Eng: {e['text'][:80]}...")


if __name__ == "__main__":
    main()
