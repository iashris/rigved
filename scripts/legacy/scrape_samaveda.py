#!/usr/bin/env python3
"""
Scrape Sama Veda from sacred-texts.com (English) and TITUS (Sanskrit)
Creates bilingual JSON with Devanagari Sanskrit and English translation
"""

import urllib.request
import json
import re
import os
from html.parser import HTMLParser
from typing import List, Dict

# URLs
ENGLISH_URL = "https://sacred-texts.com/hin/sv.htm"
TITUS_BASE = "https://titus.uni-frankfurt.de/texte/etcs/ind/aind/ved/sv/svk/"


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract text content"""
    def __init__(self):
        super().__init__()
        self.text_content = []

    def handle_data(self, data):
        self.text_content.append(data)

    def get_text(self):
        return '\n'.join(self.text_content)


def fetch_url(url: str) -> str:
    """Fetch URL and return content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def parse_titus_sanskrit(html_files_dir: str) -> Dict[int, str]:
    """Parse TITUS HTML files to extract Sanskrit verses"""
    sanskrit_verses = {}

    if os.path.exists(html_files_dir):
        files = sorted([f for f in os.listdir(html_files_dir) if f.endswith('.htm')])
    else:
        files = []
        for i in range(1, 20):
            url = f"{TITUS_BASE}svk{i:03d}.htm"
            content = fetch_url(url)
            if content:
                files.append((i, content))

    all_content = ""
    for f in files:
        if isinstance(f, tuple):
            all_content += f[1]
        else:
            filepath = os.path.join(html_files_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                all_content += file.read()

    span_pattern = re.compile(r'<span id=iovml16>(.*?)</span>', re.IGNORECASE | re.DOTALL)
    spans = span_pattern.findall(all_content)
    word_pattern = re.compile(r'>([^<]+)</a>')

    current_verse_words = []
    verse_num = 0

    for span_content in spans:
        words = word_pattern.findall(span_content)
        line_text = ' '.join(words)
        verse_end_match = re.search(r'\\\\?\s*(\d+)\s*$', span_content)

        if verse_end_match:
            verse_num = int(verse_end_match.group(1))
            line_text = re.sub(r'\s*\\\\?\s*$', '', line_text)
            current_verse_words.append(line_text)

            if current_verse_words:
                full_verse = ' '.join(current_verse_words)
                full_verse = re.sub(r'\s+', ' ', full_verse).strip()
                sanskrit_verses[verse_num] = full_verse
                current_verse_words = []
        else:
            line_text = re.sub(r'\s*\\+\s*$', '', line_text)
            if line_text.strip():
                current_verse_words.append(line_text.strip())

    return sanskrit_verses


def roman_to_int(roman: str) -> int:
    """Convert Roman numeral to integer"""
    roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
    return roman_map.get(roman.upper(), 1)


def parse_english_samaveda(html_content: str) -> List[Dict]:
    """Parse the English translation from sacred-texts.com"""
    verses = []

    parser = SimpleHTMLParser()
    parser.feed(html_content)
    text_content = parser.get_text()
    lines = text_content.split('\n')

    current_part = 1
    current_book = 1
    current_chapter = 1
    current_decade = 1  # Default to 1 for Part II which has no decades
    current_hymn = 0

    # Track sequential verse number within each section
    section_verse_counter = 0
    last_section_key = None

    current_verse_text = []
    in_verse = False
    overall_verse = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for Part markers
        if re.match(r'^PART\s+(FIRST|SECOND|I+)\s*$', line, re.I):
            part_text = line.upper()
            if 'FIRST' in part_text or 'PART I' in part_text:
                current_part = 1
            elif 'SECOND' in part_text or 'PART II' in part_text:
                current_part = 2
            continue

        # Check for Book markers
        book_match = re.match(r'^BOOK\s+([IVX]+)\s*\.?\s*$', line, re.I)
        if book_match:
            current_book = roman_to_int(book_match.group(1))
            current_chapter = 1
            current_decade = 1
            continue

        # Check for Chapter markers
        chapter_match = re.match(r'^CHAPTER\s+([IVX]+)\s*\.?\s*$', line, re.I)
        if chapter_match:
            current_chapter = roman_to_int(chapter_match.group(1))
            current_decade = 1
            continue

        # Check for Decade markers (only in Part I)
        # Format: "DECADE I Agni" or "DECADE II Indra and others"
        decade_match = re.match(r'^DECADE\s+([IVX]+)\b', line, re.I)
        if decade_match:
            current_decade = roman_to_int(decade_match.group(1))
            continue

        # Check for hymn number
        hymn_match = re.match(r'^(\d+)\.\s*(.+)$', line)
        if hymn_match:
            # Save previous verse
            if current_verse_text and current_hymn > 0:
                verse_text = ' '.join(current_verse_text).strip()
                if verse_text:
                    overall_verse += 1

                    # Calculate section based on structure
                    if current_part == 1:
                        section = (current_chapter - 1) * 5 + current_decade
                    else:
                        section = current_chapter

                    # Track section changes to reset verse counter
                    section_key = (current_part, current_book, section)
                    if section_key != last_section_key:
                        section_verse_counter = 0
                        last_section_key = section_key
                    section_verse_counter += 1

                    verses.append({
                        'overall': overall_verse,
                        'part': current_part,
                        'book': current_book,
                        'chapter': current_chapter,
                        'decade': current_decade,
                        'section': section,
                        'verse_in_section': section_verse_counter,
                        'original_verse': current_hymn,
                        'text': verse_text
                    })

            current_hymn = int(hymn_match.group(1))
            current_verse_text = [hymn_match.group(2)]
            in_verse = True
            continue

        # Continue verse text
        if in_verse and line and not re.match(r'^(BOOK|CHAPTER|DECADE|PART)\s', line, re.I):
            if len(line) > 3 and not line.isupper():
                current_verse_text.append(line)

    # Last verse
    if current_verse_text and current_hymn > 0:
        verse_text = ' '.join(current_verse_text).strip()
        if verse_text:
            overall_verse += 1
            if current_part == 1:
                section = (current_chapter - 1) * 5 + current_decade
            else:
                section = current_chapter

            section_key = (current_part, current_book, section)
            if section_key != last_section_key:
                section_verse_counter = 0
                last_section_key = section_key
            section_verse_counter += 1

            verses.append({
                'overall': overall_verse,
                'part': current_part,
                'book': current_book,
                'chapter': current_chapter,
                'decade': current_decade,
                'section': section,
                'verse_in_section': section_verse_counter,
                'original_verse': current_hymn,
                'text': verse_text
            })

    return verses


def scrape_samaveda():
    """Main scraping function"""
    print("=" * 60)
    print("Sama Veda Bilingual Scraper")
    print("=" * 60)

    # Step 1: Get English translations
    print("\n[1/4] Fetching English translation from sacred-texts.com...")
    html_content = fetch_url(ENGLISH_URL)
    if not html_content:
        print("Failed to fetch English translation")
        return

    print("[2/4] Parsing English verses...")
    english_verses = parse_english_samaveda(html_content)
    print(f"  Found {len(english_verses)} English verses")

    # Debug: show structure
    print("\n  Structure breakdown:")
    part1 = [v for v in english_verses if v['part'] == 1]
    part2 = [v for v in english_verses if v['part'] == 2]
    print(f"    Part I: {len(part1)} verses")
    print(f"    Part II: {len(part2)} verses")

    # Step 2: Get Sanskrit from TITUS
    print("\n[3/4] Parsing Sanskrit from TITUS files...")
    titus_dir = "/tmp/titus_sv"
    sanskrit_verses = parse_titus_sanskrit(titus_dir)
    print(f"  Found {len(sanskrit_verses)} Sanskrit verses")

    # Step 3: Merge and create final output
    print("\n[4/4] Creating bilingual JSON...")
    final_verses = []

    for v in english_verses:
        overall = v['overall']
        part = v['part']
        book = v['book']
        section = v['section']
        verse_num = v['verse_in_section']

        # Calculate book number (1-6 for Part I, 7-15 for Part II)
        if part == 1:
            mandala = book  # Books 1-6
        else:
            mandala = 6 + book  # Books 7-15

        # Get Sanskrit text
        sanskrit_iast = sanskrit_verses.get(overall, '')

        # Reference format: book.section.verse
        reference = f"{mandala}.{section}.{verse_num}"

        final_verse = {
            'reference': reference,
            'text': v['text'],
            'mandala': mandala,
            'hymn': section,
            'verse': verse_num,
            'meaning': sanskrit_iast,
            'sanskrit_iast': sanskrit_iast,
            'vedaId': 'samaveda'
        }
        final_verses.append(final_verse)

    # Save to JSON
    output_file = 'docs/samaveda.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_verses, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(final_verses)} verses to {output_file}")

    public_output = 'public/samaveda.json'
    with open(public_output, 'w', encoding='utf-8') as f:
        json.dump(final_verses, f, ensure_ascii=False, indent=2)
    print(f"  Also saved to {public_output}")

    # Print sample
    print("\n" + "=" * 60)
    print("Sample verses:")
    print("=" * 60)
    for v in final_verses[:5]:
        print(f"\n{v['reference']}:")
        print(f"  Hymn: {v['hymn']}, Verse: {v['verse']}")
        print(f"  English: {v['text'][:60]}...")

    # Show hymn distribution
    print("\n\nHymn distribution by book:")
    for m in sorted(set(v['mandala'] for v in final_verses)):
        book_verses = [v for v in final_verses if v['mandala'] == m]
        hymns = sorted(set(v['hymn'] for v in book_verses))
        print(f"  Book {m}: {len(book_verses)} verses, Hymns: {hymns[:10]}{'...' if len(hymns) > 10 else ''}")

    return final_verses


if __name__ == '__main__':
    scrape_samaveda()
