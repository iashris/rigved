#!/usr/bin/env python3
"""
Convert TITUS raw text files to structured JSON with IAST and Devanagari.

Handles two formats:
  1. TITUS pipe-markup (|b, |c, |p lines) — Aitareya Br., Taittiriya Br./Sam.
  2. HTML-scraped "Level N" structure — Upanishads, Gopatha, Ramayana, etc.

Output JSON matches existing repo format:
  { reference, text (IAST), meaning (Devanagari), vedaId, mandala, hymn, verse,
    sanskrit_iast }
"""

import json
import os
import re
import sys
import unicodedata

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
RAW_DIR = os.path.join(os.path.dirname(__file__), "titus_raw")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "data")

# Output directories by category
OUT_DIRS = {
    "vedas": os.path.join(DATA_DIR, "vedas"),
    "brahmanas": os.path.join(DATA_DIR, "brahmanas"),
    "aranyakas": os.path.join(DATA_DIR, "aranyakas"),
    "upanishads": os.path.join(DATA_DIR, "upanishads"),
    "epics": os.path.join(DATA_DIR, "epics"),
}

# ============================================================
# TITUS transliteration → IAST conversion
# ============================================================

# TITUS Harvard-Kyoto style encoding used in pipe-markup files
TITUS_TO_IAST = {
    # Vowels
    "A": "ā", "I": "ī", "U": "ū",
    "E": "e", "O": "o",
    ".r": "ṛ", ".R": "ṝ", ".l": "ḷ", ".L": "ḹ",
    # Nasals/Anusvara
    "~N": "ṅ", "## old ~n": "", "~n": "ñ",
    "N": "ṇ", "M": "ṃ",
    "H": "ḥ",  # Visarga — but only at end of word/before space
    # Retroflex
    "T": "ṭ", "D": "ḍ",
    # Sibilants
    "S": "ṣ", "/S": "ś",  # /S = palatal
    "z": "ś",
    # Special
    "~m": "ṃ", "~": "ṃ",  # anusvara
    ".": "",  # often a separator
}

# For the pipe-markup files, we need a more careful approach
def titus_markup_to_iast(text):
    """Convert TITUS Harvard-Kyoto-like encoding to IAST.

    This handles the pipe-markup format where:
      A=ā, I=ī, U=ū, /S=ś, S=ṣ, T=ṭ, D=ḍ, N=ṇ, M=ṃ, H=ḥ,
      .r=ṛ, ~n=ñ, ~N=ṅ, ~m=ṃ, pa~Nc=pañc
      Accents: /a = á (acute), \a = à (grave) — we strip accents
    """
    # Remove TITUS comment markers
    text = re.sub(r'#', '', text)

    # Handle special sequences first (order matters)
    replacements = [
        # Multi-char sequences first
        (".rr", "ṝ"), (".RR", "ṝ"), (".R", "ṝ"),
        (".r", "ṛ"), (".ll", "ḹ"), (".l", "ḷ"),
        ("~N", "ṅ"), ("## ~n", ""), ("~n", "ñ"),
        ("~m", "ṃ"),
        ("/S", "ś"), # palatal sibilant — must come before /X accent removal
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Remove Vedic accent markers: /X → X, \X → X
    # But careful: /S already handled above, / at end of line is daṇḍa
    # /a means accented a — just strip the /
    text = re.sub(r'/([a-zāīūṛṝḷḹṅñṇṃḥṭḍśṣ])', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\\([a-zāīūṛṝḷḹṅñṇṃḥṭḍśṣ])', r'\1', text, flags=re.IGNORECASE)

    # Now handle single-char uppercase mappings
    # Must be careful: only map uppercase that are TITUS encoding, not start of words
    # In TITUS, uppercase in middle/end = special char
    result = []
    i = 0
    chars = list(text)
    while i < len(chars):
        c = chars[i]

        # Handle tilde-vowel combos like ~a
        if c == '~' and i + 1 < len(chars):
            next_c = chars[i + 1]
            if next_c in 'aeiou':
                # nasalized vowel — just use anusvara + vowel
                result.append('ṃ')
                i += 1
                continue

        # Single uppercase mappings
        if c == 'A' and (i > 0 or not text[max(0,i-1):i+1].strip().startswith('A')):
            result.append('ā')
        elif c == 'I':
            result.append('ī')
        elif c == 'U':
            result.append('ū')
        elif c == 'T':
            result.append('ṭ')
        elif c == 'D':
            result.append('ḍ')
        elif c == 'N':
            result.append('ṇ')
        elif c == 'M':
            result.append('ṃ')
        elif c == 'S':
            result.append('ṣ')
        elif c == 'H':
            result.append('ḥ')
        elif c == '/':
            # Remaining / at end of line = daṇḍa or separator
            if i == len(chars) - 1 or chars[i + 1] in ' \n\t/':
                result.append('/')
            else:
                # accent marker we missed — skip
                pass
        elif c == '\\':
            pass  # accent marker
        elif c == '.':
            # Sentence separator in some texts, or already handled
            if i + 1 < len(chars) and chars[i + 1] in 'rRlL':
                pass  # already handled above
            else:
                result.append('.')
        else:
            result.append(c)
        i += 1

    return ''.join(result)


# ============================================================
# IAST → Devanagari conversion
# ============================================================

IAST_TO_DEVANAGARI = {
    # Independent vowels
    'a': 'अ', 'ā': 'आ', 'i': 'इ', 'ī': 'ई', 'u': 'उ', 'ū': 'ऊ',
    'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'ḹ': 'ॡ',
    'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ',
    # Consonants
    'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ṅ': 'ङ',
    'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ñ': 'ञ',
    'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
    't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
    'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
    'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व',
    'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह',
    # Anusvara, visarga, avagraha
    'ṃ': 'ं', 'ḥ': 'ः',
}

# Vowel matras (dependent forms)
VOWEL_MATRAS = {
    'a': '',  # Inherent vowel, no matra
    'ā': 'ा', 'i': 'ि', 'ī': 'ी', 'u': 'ु', 'ū': 'ू',
    'ṛ': 'ृ', 'ṝ': 'ॄ', 'ḷ': 'ॢ', 'ḹ': 'ॣ',
    'e': 'े', 'ai': 'ै', 'o': 'ो', 'au': 'ौ',
}

CONSONANTS = set([
    'k', 'kh', 'g', 'gh', 'ṅ',
    'c', 'ch', 'j', 'jh', 'ñ',
    'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
    't', 'th', 'd', 'dh', 'n',
    'p', 'ph', 'b', 'bh', 'm',
    'y', 'r', 'l', 'v',
    'ś', 'ṣ', 's', 'h',
])

VOWELS = set(['a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'e', 'ai', 'o', 'au'])

VIRAMA = '्'


def iast_to_devanagari(text):
    """Convert IAST transliteration to Devanagari script."""
    if not text or not text.strip():
        return text

    result = []
    i = 0
    text_lower = text.lower()
    prev_was_consonant = False

    while i < len(text_lower):
        # Skip non-alphabetic characters
        if text_lower[i] in ' \t\n.,;:!?/\\|()[]{}0123456789\'"—–-_=+@#$%^&*~`<>':
            if prev_was_consonant:
                result.append(VIRAMA)
                prev_was_consonant = False
            result.append(text[i])
            i += 1
            continue

        # Try matching longer sequences first
        matched = False

        # Try 3-char
        if i + 2 < len(text_lower):
            tri = text_lower[i:i+3]
            if tri in CONSONANTS:
                if prev_was_consonant:
                    result.append(VIRAMA)
                result.append(IAST_TO_DEVANAGARI[tri])
                prev_was_consonant = True
                i += 3
                matched = True
                continue

        # Try 2-char
        if not matched and i + 1 < len(text_lower):
            di = text_lower[i:i+2]
            if di in CONSONANTS:
                if prev_was_consonant:
                    result.append(VIRAMA)
                result.append(IAST_TO_DEVANAGARI[di])
                prev_was_consonant = True
                i += 2
                matched = True
                continue
            elif di in VOWELS:
                if prev_was_consonant:
                    result.append(VOWEL_MATRAS.get(di, ''))
                    prev_was_consonant = False
                else:
                    result.append(IAST_TO_DEVANAGARI.get(di, di))
                i += 2
                matched = True
                continue

        # Try 1-char
        if not matched:
            ch = text_lower[i]
            if ch in CONSONANTS:
                if prev_was_consonant:
                    result.append(VIRAMA)
                result.append(IAST_TO_DEVANAGARI[ch])
                prev_was_consonant = True
                i += 1
            elif ch in VOWELS:
                if prev_was_consonant:
                    result.append(VOWEL_MATRAS.get(ch, ''))
                    prev_was_consonant = False
                else:
                    result.append(IAST_TO_DEVANAGARI.get(ch, ch))
                i += 1
            elif ch == 'ṃ':
                if prev_was_consonant:
                    result.append(VIRAMA)
                    prev_was_consonant = False
                result.append('ं')
                i += 1
            elif ch == 'ḥ':
                if prev_was_consonant:
                    result.append(VIRAMA)
                    prev_was_consonant = False
                result.append('ः')
                i += 1
            elif ch == "'":
                # Avagraha
                if prev_was_consonant:
                    result.append(VIRAMA)
                    prev_was_consonant = False
                result.append('ऽ')
                i += 1
            elif ch == 'oṃ' or text_lower[i:i+2] == 'oṃ':
                result.append('ॐ')
                i += 2
            else:
                if prev_was_consonant:
                    result.append(VIRAMA)
                    prev_was_consonant = False
                result.append(text[i])
                i += 1

    # Final virama if text ends with consonant
    if prev_was_consonant:
        result.append(VIRAMA)

    return ''.join(result)


# ============================================================
# Fix HTML-scraped encoding artifacts
# ============================================================

def fix_html_encoding(text):
    """Fix mojibake from HTML scraping where UTF-8 IAST got mangled."""
    # Common patterns from double-encoding
    fixes = {
        'Ä': 'ā', 'Ä«': 'ī', 'Å«': 'ū',
        'á¹': 'ṇ', 'á¹£': 'ṣ', 'á¹': 'ṃ',
        'á¸¥': 'ḥ', 'á¸': 'ḍ',
        'Åa': 'śa', 'Å': 'ś',
        'Ã±': 'ñ',
        'á¹\x85': 'ṅ',
        'Ê°': 'h',  # aspiration marker in TITUS IAST
        'Ì¥': '',  # combining accent
        'Ã': 'ñ',
    }
    for bad, good in fixes.items():
        text = text.replace(bad, good)

    # More systematic: try to detect and fix common UTF-8 double-encoding
    # Pattern: Ã¤ → ä, Ã± → ñ, etc (Latin1 misread as UTF-8)
    try:
        # Try to fix by re-encoding
        fixed = text.encode('latin1').decode('utf-8')
        if fixed != text:
            return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    return text


# ============================================================
# Parser for TITUS pipe-markup format
# ============================================================

def parse_pipe_markup(filepath, veda_id):
    """Parse TITUS pipe-markup format (|b, |c, |p lines)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []
    current_book = ""
    current_chapter = ""
    current_ref = ""
    current_paragraph_texts = []

    lines = content.split('\n')
    i = 0

    # Detect book/chapter pattern from first |c line
    ref_pattern = None
    for line in lines:
        if line.startswith('|c'):
            # Could be |c1 {adhyAya 1...} or |c1,1,1 {BS 1.1.1.1}
            m = re.match(r'\|c([\d,]+)', line)
            if m:
                ref_str = m.group(1)
                if ',' in ref_str:
                    ref_pattern = 'dotted'  # like 1,1,1
                else:
                    ref_pattern = 'simple'  # like 1
            break

    book_num = 0
    chapter_parts = []

    for line in lines:
        line = line.rstrip()

        # Book marker
        if line.startswith('|b'):
            m = re.match(r'\|b\w+(\d+)', line)
            if m:
                book_num = int(m.group(1))
            continue

        # Chapter marker
        if line.startswith('|c'):
            # Flush previous chapter paragraphs
            _flush_paragraphs(entries, current_chapter, current_paragraph_texts, veda_id, book_num)
            current_paragraph_texts = []

            m = re.match(r'\|c([\d,]+)', line)
            if m:
                current_chapter = m.group(1).replace(',', '.')
            continue

        # Paragraph
        if line.startswith('|p'):
            m = re.match(r'\|p(\d+)\s+(.*)', line)
            if m:
                p_num = m.group(1)
                p_text = m.group(2).strip()
                current_paragraph_texts.append((p_num, p_text))
            continue

        # Continuation line (indented)
        if line.startswith('     ') and current_paragraph_texts:
            p_num, p_text = current_paragraph_texts[-1]
            current_paragraph_texts[-1] = (p_num, p_text + ' ' + line.strip())

    # Flush remaining
    _flush_paragraphs(entries, current_chapter, current_paragraph_texts, veda_id, book_num)

    return entries


def _flush_paragraphs(entries, chapter, paragraphs, veda_id, book_num):
    """Convert accumulated paragraphs into JSON entries."""
    if not paragraphs or not chapter:
        return

    for p_num, p_text in paragraphs:
        if not p_text.strip():
            continue

        ref = f"{chapter}.{p_num}"
        iast_text = titus_markup_to_iast(p_text)
        iast_text = iast_text.strip()

        # Clean up
        iast_text = re.sub(r'\s+', ' ', iast_text)
        iast_text = iast_text.replace(' /', ' /').replace('/ ', '/ ')

        devanagari = iast_to_devanagari(iast_text)

        # Parse reference parts
        ref_parts = ref.split('.')
        mandala = int(ref_parts[0]) if len(ref_parts) > 0 and ref_parts[0].isdigit() else book_num
        hymn_val = int(ref_parts[1]) if len(ref_parts) > 1 and ref_parts[1].isdigit() else 0
        verse_val = int(ref_parts[-1]) if ref_parts[-1].isdigit() else 0

        entries.append({
            "reference": ref,
            "sanskrit_iast": iast_text,
            "meaning": devanagari,
            "text": "",  # No English translation yet
            "mandala": mandala,
            "hymn": hymn_val,
            "verse": verse_val,
            "vedaId": veda_id,
        })


# ============================================================
# Parser for HTML-scraped "Level" format
# ============================================================

def parse_level_format(filepath, veda_id):
    """Parse HTML-scraped format with 'Level N ...' structural markers."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix encoding artifacts
    content = fix_html_encoding(content)

    entries = []
    # Track hierarchy
    levels = {}  # level_num -> value
    current_text_lines = []

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty, page separators, boilerplate
        if not line:
            continue
        if line.startswith('--- Page'):
            continue
        if line.startswith('TITUS'):
            continue
        if line.startswith('Copyright'):
            continue
        if line.startswith('No parts of this'):
            continue
        if line.startswith('without prior'):
            continue
        if 'TITUS edition' in line:
            continue
        if 'TITUS version' in line:
            continue
        if line.startswith('Edited by') or line.startswith('On the basis'):
            continue
        if line.startswith('electronically edited'):
            continue
        if line.startswith('Machine-readable'):
            continue
        if line.startswith('***'):
            continue
        if line.startswith('The copyright'):
            continue
        if line.startswith('Any (free)'):
            continue
        if line.startswith('If you desire'):
            continue
        if 'Frankfurt a/M' in line or 'Frankfurt a.M' in line:
            continue

        # Level markers
        level_match = re.match(r'Level\s+(\d+)\s+(\w[\w\s]*?):\s*(.*)', line)
        if level_match:
            level_num = int(level_match.group(1))
            level_type = level_match.group(2).strip()
            level_val = level_match.group(3).strip()

            levels[level_num] = {
                'type': level_type,
                'value': level_val,
            }
            # Clear lower levels
            for k in list(levels.keys()):
                if k > level_num:
                    del levels[k]

            # If this level line also contains text content after the value
            # Check if the value contains Sanskrit text
            if level_val and not level_val.isdigit() and level_num >= 4:
                # This level line contains inline text
                _add_entry(entries, levels, level_val, veda_id)

            continue

        # Named section headers (not Level markers)
        if re.match(r'^(Adhyāya|Adhyaya|Prapāṭhaka|Kāṇḍa|Kanda|Sarga|Book|Chapter|Part No|BÄla|Bāla|Ayodhyā|Araṇya|Kiṣkindh|Sundara|Yuddha|Uttara)', line):
            continue

        # Skip short metadata-like lines
        if len(line) < 4:
            continue

        # Skip lines that are just text names
        if re.match(r'^(Sāma-Veda|Rig-Veda|Yajur-Veda|Atharva-Veda|White Yajur|Black Yajur)', line, re.IGNORECASE):
            continue
        if re.match(r'^(Kena|Kaṭha|Aitareya|Taittirīya|Bṛhad|Śvetāśvatara|Kauṣītakī|Gopatha|Pañcaviṃśa|Manu)', line):
            continue

        # Actual text lines — Sanskrit content
        if line and not line.startswith('Level'):
            # Check it's not just metadata
            if any(skip in line for skip in ['edition', 'Edition', 'prepared', 'adapted',
                                              'version', 'Version', 'Erlangen', 'Oxford',
                                              'Baroda', 'Cambridge', 'Leiden', 'Frankfurt',
                                              'Recension', 'recension', 'apparatus',
                                              'manuscripta', 'siglum', 'editio']):
                continue
            _add_entry(entries, levels, line, veda_id)

    return entries


def _add_entry(entries, levels, text, veda_id):
    """Create a JSON entry from current level hierarchy and text."""
    text = text.strip()
    if not text or len(text) < 2:
        return

    # Build reference from levels
    ref_parts = []
    for lnum in sorted(levels.keys()):
        val = levels[lnum]['value']
        # Extract numeric part if present
        num_match = re.match(r'^(\d+)', val)
        if num_match:
            ref_parts.append(num_match.group(1))
        elif val and not val[0].isalpha():
            ref_parts.append(val.split()[0])

    ref = '.'.join(ref_parts) if ref_parts else str(len(entries) + 1)

    # Clean the text
    iast_text = text.strip()

    # Remove trailing verse numbers like /1/ or /23/
    iast_text = re.sub(r'\s*/\d+/\s*$', '', iast_text)

    # Remove word-break markers
    iast_text = iast_text.replace(' ~ ', '').replace('~', '')
    iast_text = iast_text.replace(' _', '').replace('_ ', '')

    # Clean up spacing
    iast_text = re.sub(r'\s+', ' ', iast_text).strip()

    if not iast_text or len(iast_text) < 2:
        return

    devanagari = iast_to_devanagari(iast_text)

    # Parse reference for mandala/hymn/verse
    ref_nums = [int(x) for x in ref.split('.') if x.isdigit()]
    mandala = ref_nums[0] if len(ref_nums) > 0 else 0
    hymn = ref_nums[1] if len(ref_nums) > 1 else 0
    verse = ref_nums[-1] if len(ref_nums) > 0 else 0

    entries.append({
        "reference": ref,
        "sanskrit_iast": iast_text,
        "meaning": devanagari,
        "text": "",
        "mandala": mandala,
        "hymn": hymn,
        "verse": verse,
        "vedaId": veda_id,
    })


# ============================================================
# Main
# ============================================================

# Map filename → (parser_type, vedaId)
TEXT_CONFIG = {
    # Tier 1 — pipe markup
    "aitareya_brahmana": ("pipe", "aitareya_brahmana"),
    "taittiriya_brahmana": ("pipe", "taittiriya_brahmana"),
    "taittiriya_samhita": ("pipe", "taittiriya_samhita"),
    # Tier 1 — level format
    "brhadaranyaka_upanishad": ("level", "brhadaranyaka_upanishad"),
    "rgveda_khilani": ("level", "rgveda_khilani"),
    "pancavimsa_brahmana": ("level", "pancavimsa_brahmana"),
    "kausitaki_brahmana": ("level", "kausitaki_brahmana"),
    # Tier 2
    "taittiriya_aranyaka": ("level", "taittiriya_aranyaka"),
    "taittiriya_upanishad": ("level", "taittiriya_upanishad"),
    "katha_upanishad": ("level", "katha_upanishad"),
    "svetasvatara_upanishad": ("level", "svetasvatara_upanishad"),
    "gopatha_brahmana": ("level", "gopatha_brahmana"),
    "aitareya_aranyaka": ("level", "aitareya_aranyaka"),
    "aitareya_upanishad": ("level", "aitareya_upanishad"),
    "kena_upanishad": ("level", "kena_upanishad"),
    "kausitaki_upanishad": ("level", "kausitaki_upanishad"),
    # Tier 3
    "ramayana": ("level", "ramayana"),
    "manu_smrti": ("level", "manu_smrti"),
    "vajasaneyi_samhita": ("level", "vajasaneyi_samhita"),
}


def convert_one(name):
    """Convert a single raw text to JSON."""
    config = TEXT_CONFIG.get(name)
    if not config:
        print(f"  [ERROR] Unknown text: {name}")
        return False

    parser_type, veda_id = config
    inpath = os.path.join(RAW_DIR, f"{name}.txt")
    outpath = os.path.join(OUT_DIR, f"{veda_id}.json")

    if not os.path.exists(inpath):
        print(f"  [skip] {name}.txt not found")
        return False

    if os.path.exists(outpath):
        print(f"  [skip] {veda_id}.json already exists")
        return True

    print(f"  Converting {name} ({parser_type}) ...")

    try:
        if parser_type == "pipe":
            entries = parse_pipe_markup(inpath, veda_id)
        else:
            entries = parse_level_format(inpath, veda_id)

        if not entries:
            print(f"  [FAIL] {name} — 0 entries parsed")
            return False

        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        print(f"  [ok] {veda_id}.json — {len(entries):,} entries")
        return True

    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    names = sys.argv[1:] if len(sys.argv) > 1 else list(TEXT_CONFIG.keys())

    print("=" * 60)
    print("TITUS Raw → JSON Converter")
    print(f"  Texts: {len(names)}")
    print("=" * 60)

    results = {}
    for name in names:
        results[name] = convert_one(name)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        print(f"  [{'OK' if ok else 'FAIL'}] {name}")

    succeeded = sum(1 for v in results.values() if v)
    print(f"\n  {succeeded}/{len(results)} converted")


if __name__ == "__main__":
    main()
