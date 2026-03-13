#!/usr/bin/env python3
"""
Re-scrape garbled TITUS texts with proper encoding handling.
Produces clean IAST + Devanagari. No English translations.
"""

import json
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "titus_raw")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "data")

BASE = "https://titus.uni-frankfurt.de/texte"
BASE_AUTH = "https://titus.fkidg1.uni-frankfurt.de/texte"
TITUS_USER = "titusstud"
TITUS_PASS = "R2gveda5"
HEADERS = {"User-Agent": "Mozilla/5.0 (academic research; vedic-texts-project)"}

TEXTS = {
    "taittiriya_aranyaka": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvs/ta/ta",
        "max_pages": 200, "category": "aranyakas",
        "verse_boundary": "anuvaka",  # Split at Anuvaka boundaries
    },
    "aitareya_aranyaka": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/aa/aa",
        "max_pages": 100, "category": "aranyakas",
        "verse_boundary": "paragraph",
    },
    "gopatha_brahmana": {
        "base": f"{BASE}/etcs/ind/aind/ved/av/gb/gb",
        "max_pages": 200, "category": "brahmanas",
        "verse_boundary": "paragraph",
    },
    "kausitaki_brahmana": {
        "base": f"{BASE_AUTH}/etcc/ind/aind/ved/rv/kb/kb",
        "max_pages": 150, "needs_auth": True, "category": "brahmanas",
        "verse_boundary": "paragraph",
    },
    "pancavimsa_brahmana": {
        "base": f"{BASE}/etcs/ind/aind/ved/sv/pb/pb",
        "max_pages": 300, "category": "brahmanas",
        "verse_boundary": "paragraph",
    },
    "vajasaneyi_samhita": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvw/vs/vs",
        "max_pages": 200, "category": "vedas",
        "verse_boundary": "verse_num",  # Uses Verse: N structural markers
    },
    "rgveda_khilani": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/rvkh/rvkh",
        "max_pages": 120, "category": "vedas",
        "verse_boundary": "verse_num",
    },
    "manu_smrti": {
        "base": f"{BASE}/etcs/ind/aind/ved/postved/dhs/manu/manu",
        "max_pages": 200, "category": "epics",
        "verse_boundary": "verse_num",  # Uses Verse: N structural markers
    },
    "ramayana": {
        "base": f"{BASE}/etcs/ind/aind/ram/ram",  # files are ram001.htm
        "max_pages": 1000, "category": "epics",
        "verse_boundary": "verse_num",
    },
}


def clean_titus_iast(text):
    """Clean TITUS IAST to standard IAST."""
    # Strip editorial apparatus {M: ...} {P: ...}
    text = re.sub(r'\{[^}]*\}', '', text)
    # Strip stray braces
    text = text.replace('{', '').replace('}', '')

    # Aspirated consonants: Xʰ → Xh
    for c in 'kgcjṭḍtdpbKGCJṬḌTDPB':
        text = text.replace(c + 'ʰ', c + 'h')
    text = text.replace('ʰ', 'h')  # stray

    # r̥ → ṛ, l̥ → ḷ
    text = text.replace('r̥', 'ṛ').replace('R̥', 'Ṛ')
    text = text.replace('l̥', 'ḷ')

    # Strip Vedic accent marks from vowels (acute/grave accents)
    # These are precomposed accented vowels used for svarita/udātta marking
    accent_map = {
        'á': 'a', 'à': 'a', 'é': 'e', 'è': 'e',
        'í': 'i', 'ì': 'i', 'ó': 'o', 'ò': 'o',
        'ú': 'u', 'ù': 'u',
        'Á': 'A', 'À': 'A', 'É': 'E', 'È': 'E',
        'Í': 'I', 'Ì': 'I', 'Ó': 'O', 'Ò': 'O',
        'Ú': 'U', 'Ù': 'U',
    }
    for accented, plain in accent_map.items():
        text = text.replace(accented, plain)

    # Strip combining accent marks on remaining chars (but NOT on ś/ṣ/ṭ etc)
    # Only strip combining grave (U+0300) and combining acute (U+0301)
    # when they follow a vowel
    text = re.sub(r'([aeiouāīūṛṝḷ])[\u0300\u0301]', r'\1', text, flags=re.I)

    text = text.replace('´', '').replace('`', '')

    # m̐ → ṃ, ṁ → ṃ
    text = text.replace('m̐', 'ṃ').replace('ṁ', 'ṃ')

    # Strip the /  that TITUS uses for word separation annotation
    text = text.replace('/', '')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def iast_to_devanagari(text):
    """Convert clean IAST to Devanagari."""
    # We'll use the converter from titus_to_json.py approach
    # but simplified — just map character by character

    cons = [
        ('kh', 'ख'), ('gh', 'घ'), ('ṅ', 'ङ'),
        ('ch', 'छ'), ('jh', 'झ'), ('ñ', 'ञ'),
        ('ṭh', 'ठ'), ('ḍh', 'ढ'), ('ṇ', 'ण'),
        ('th', 'थ'), ('dh', 'ध'), ('n', 'न'),
        ('ph', 'फ'), ('bh', 'भ'), ('m', 'म'),
        ('k', 'क'), ('g', 'ग'), ('c', 'च'), ('j', 'ज'),
        ('ṭ', 'ट'), ('ḍ', 'ड'), ('t', 'त'), ('d', 'द'),
        ('p', 'प'), ('b', 'ब'),
        ('y', 'य'), ('r', 'र'), ('l', 'ल'), ('v', 'व'),
        ('ś', 'श'), ('ṣ', 'ष'), ('s', 'स'), ('h', 'ह'),
    ]
    vowels_indep = [
        ('ai', 'ऐ'), ('au', 'औ'),
        ('ā', 'आ'), ('ī', 'ई'), ('ū', 'ऊ'),
        ('ṛ', 'ऋ'), ('ṝ', 'ॠ'), ('ḷ', 'ऌ'),
        ('e', 'ए'), ('o', 'ओ'),
        ('a', 'अ'), ('i', 'इ'), ('u', 'उ'),
    ]
    vowels_dep = [
        ('ai', 'ै'), ('au', 'ौ'),
        ('ā', 'ा'), ('ī', 'ी'), ('ū', 'ू'),
        ('ṛ', 'ृ'), ('ṝ', 'ॄ'), ('ḷ', 'ॢ'),
        ('e', 'े'), ('o', 'ो'),
        ('a', ''), ('i', 'ि'), ('u', 'ु'),
    ]
    virama = '्'

    result = []
    t = text.lower()
    i = 0

    while i < len(t):
        c = t[i]

        if c in ' \t\n':
            result.append(c); i += 1; continue
        if c == 'ṃ':
            result.append('ं'); i += 1; continue
        if c == 'ḥ':
            result.append('ः'); i += 1; continue
        if t[i:i+2] == '||':
            result.append('॥'); i += 2; continue
        if c == '|':
            result.append('।'); i += 1; continue

        # Try consonants
        matched = False
        for lat, dev in cons:
            if t[i:i+len(lat)] == lat:
                result.append(dev)
                i += len(lat)
                # Check for vowel matra
                found_v = False
                for vlat, vmatra in vowels_dep:
                    if t[i:i+len(vlat)] == vlat:
                        if vmatra: result.append(vmatra)
                        i += len(vlat)
                        found_v = True
                        break
                if not found_v:
                    result.append(virama)
                matched = True
                break
        if matched: continue

        # Try independent vowels
        for vlat, vdev in vowels_indep:
            if t[i:i+len(vlat)] == vlat:
                result.append(vdev)
                i += len(vlat)
                matched = True
                break
        if matched: continue

        # Pass through
        result.append(text[i])
        i += 1

    return ''.join(result)


def extract_structured_data(html):
    """Extract structured data from TITUS HTML using span IDs.

    TITUS uses specific span ID prefixes:
      iov* = actual Sanskrit text (iovpl, iovml, etc.)
      ioc* = editorial comments/references (skip)
      h3-h7 = structural markers (Aranyaka, Adhyaya, Paragraph, Sentence)
      h8, h9 = editorial page/line numbers (skip)
      title, subtitle, textdescr, bibliogr, titus = header metadata (skip)
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    body = soup.find("body")
    if not body:
        return []

    events = []  # list of (type, data) tuples

    # Walk through all spans in order
    for span in body.find_all("span", id=True):
        span_id = span.get("id", "")
        text = span.get_text(" ").strip()
        if not text:
            continue

        # Structural markers (h2-h7 = content structure)
        if re.match(r'^h[2-7]$', span_id):
            # Extract level comment like "<!--Level 3-->Aranyaka: 1"
            raw = str(span)
            m = re.search(r'<!--\s*(?:X?Level \d+)\s*-->([^<]+)', raw)
            if m:
                label = m.group(1).strip()
                events.append(("struct", label))
            continue

        # Skip editorial metadata (h8=page, h9=line)
        if re.match(r'^h[89]$', span_id):
            continue

        # Skip header/bibliographic metadata
        if span_id in ('title', 'subtitle', 'textdescr', 'bibliogr', 'titus', 'n16'):
            continue

        # Actual text content (iov* or iosk* spans)
        if span_id.startswith('iov') or span_id.startswith('iosk'):
            # Get text from anchor tags within the span
            parts = []
            for child in span.children:
                if hasattr(child, 'get_text'):
                    parts.append(child.get_text())
                elif isinstance(child, str):
                    t = child.strip()
                    if t:
                        parts.append(t)
            text = " ".join(parts).strip()
            if text:
                events.append(("text", text))
            continue

        # Skip editorial comments (ioc* spans) and other non-text spans
        if span_id.startswith('ioc') or span_id == 'n16':
            continue

    return events


def scrape_and_parse(name, config):
    """Scrape text from TITUS and parse into verses."""
    base = config["base"]
    max_pages = config["max_pages"]
    category = config["category"]

    session = requests.Session()
    session.headers.update(HEADERS)
    if config.get("needs_auth"):
        session.auth = (TITUS_USER, TITUS_PASS)

    all_events = []  # Accumulated (type, data) events from all pages
    page_num = 1
    consecutive_fails = 0
    pages_ok = 0

    print(f"\n  Scraping {name} (up to {max_pages} pages)...")

    while page_num <= max_pages and consecutive_fails < 3:
        url = f"{base}{page_num:03d}.htm"
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 404 or "not (yet) available" in resp.text:
                consecutive_fails += 1
                page_num += 1
                continue

            if resp.status_code == 200 and len(resp.text) > 200:
                resp.encoding = "utf-8"  # TITUS serves UTF-8 but doesn't declare it
                events = extract_structured_data(resp.text)
                text_events = [e for e in events if e[0] == "text"]
                if text_events:
                    all_events.extend(events)
                    consecutive_fails = 0
                    pages_ok += 1
                    if page_num % 50 == 0:
                        print(f"    page {page_num:03d} ok")
                else:
                    consecutive_fails += 1
            else:
                consecutive_fails += 1
        except Exception as e:
            print(f"    page {page_num:03d} error: {e}")
            consecutive_fails += 1

        page_num += 1
        time.sleep(0.3)

    if not all_events:
        print(f"  [FAIL] {name}")
        return 0

    # Save raw events for debugging
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_lines = []
    for etype, data in all_events:
        raw_lines.append(f"[{etype}] {data}")
    with open(os.path.join(OUTPUT_DIR, f"{name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(raw_lines))

    # Parse events into verses
    verse_boundary = config.get("verse_boundary", "paragraph")
    verses = parse_events_into_verses(all_events, name, verse_boundary)

    # Save JSON
    json_dir = os.path.join(DATA_DIR, category)
    json_path = os.path.join(json_dir, f"{name}.json")
    os.makedirs(json_dir, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)

    print(f"  [OK] {name}: {len(verses)} verses from {pages_ok} pages")
    if verses:
        v = verses[0]
        print(f"    IAST: {v['sanskrit_iast'][:80]}")
        print(f"    Dev:  {v['meaning'][:80]}")

    return len(verses)


def parse_events_into_verses(events, text_name, verse_boundary="paragraph"):
    """Parse structured events into verses.

    Events are (type, data) tuples:
      ("struct", "Aranyaka: 1") — structural marker
      ("text", "atʰa mahāvratam") — actual Sanskrit text

    verse_boundary controls how text is split into verses:
      "paragraph" — emit on Paragraph/Kandika change
      "anuvaka" — emit on Anuvaka change (each anuvaka = one verse)
      "verse_marker" — emit on \\ N \\ markers in text
    """
    # Track structural position
    struct = {"kanda": 0, "adhyaya": 0, "prapathaka": 0,
              "anuvaka": 0, "brahmana": 0, "chapter": 0,
              "book": 0, "sarga": 0, "section": 0,
              "paragraph": 0, "aranyaka": 0, "verse_num": 0}

    # Map TITUS structural labels to our keys
    struct_patterns = [
        (r'Prapāṭhaka:\s*(\d+)', 'prapathaka'),
        (r'Prapathaka:\s*(\d+)', 'prapathaka'),
        (r'Adhyāya:\s*(\d+)', 'adhyaya'),
        (r'Adhyaya:\s*(\d+)', 'adhyaya'),
        (r'Anuvāka:\s*(\d+)', 'anuvaka'),
        (r'Anuvaka:\s*(\d+)', 'anuvaka'),
        (r'Kāṇḍa:\s*(\d+)', 'kanda'),
        (r'Kanda:\s*(\d+)', 'kanda'),
        (r'Brāhmaṇa:\s*(\d+)', 'brahmana'),
        (r'Brahmana:\s*(\d+)', 'brahmana'),
        (r'Book:\s*(\d+)', 'book'),
        (r'Chapter:\s*(\d+)', 'chapter'),
        (r'Paṭala:\s*(\d+)', 'chapter'),
        (r'Sarga:\s*(\d+)', 'sarga'),
        (r'Section:\s*(\d+)', 'section'),
        (r'Paragraph:\s*(\d+)', 'paragraph'),
        (r'Aranyaka:\s*(\d+)', 'aranyaka'),
        (r'Āraṇyaka:\s*(\d+)', 'aranyaka'),
        (r'Kaṇḍikā:\s*\(?\s*(\d+)', 'paragraph'),
        (r'Kandika:\s*\(?\s*(\d+)', 'paragraph'),
        (r'Khanda:\s*(\d+)', 'chapter'),
        (r'Khaṇḍa:\s*(\d+)', 'chapter'),
        (r'Hymn:\s*(\d+)', 'section'),
        (r'Verse:\s*(\d+)', 'verse_num'),
        (r'Stanza:\s*(\d+)', 'verse_num'),
    ]

    verses = []
    current_parts = []
    last_boundary_val = 0  # Track the last boundary-level value

    def emit_verse(vnum=None):
        """Emit current accumulated text as a verse."""
        nonlocal current_parts
        if not current_parts:
            return
        raw = " ".join(current_parts)
        # Clean: remove verse markers, stray backslashes
        raw = re.sub(r'(?:\\\\|//|--)\s*\d+\s*(?:\\\\|//|--)', '', raw)
        raw = re.sub(r'\\\\', ' ', raw)
        raw = re.sub(r'\\', '', raw)
        raw = re.sub(r'\s+', ' ', raw).strip()

        if not raw or len(raw) < 5:
            current_parts = []
            return

        iast = clean_titus_iast(raw)
        if not iast or len(iast) < 5:
            current_parts = []
            return

        if vnum is None:
            if verse_boundary == "anuvaka":
                vnum = struct["anuvaka"] or len(verses) + 1
            elif verse_boundary == "verse_num":
                vnum = struct["verse_num"] or len(verses) + 1
            else:
                vnum = struct["paragraph"] if struct["paragraph"] else len(verses) + 1

        ref = make_ref(struct, vnum, text_name)
        devanagari = iast_to_devanagari(iast)

        verses.append({
            "reference": ref,
            "sanskrit_iast": iast,
            "meaning": devanagari,
            "text": "",
            "mandala": get_book(struct, text_name),
            "hymn": get_section(struct, text_name),
            "verse": vnum,
            "vedaId": text_name,
        })
        current_parts = []

    # Determine which structural key triggers verse emission
    boundary_key = {
        "paragraph": "paragraph",
        "anuvaka": "anuvaka",
        "verse_num": "verse_num",
        "verse_marker": None,  # Uses \\ N \\ in text, not struct events
    }.get(verse_boundary, "paragraph")

    for etype, data in events:
        if etype == "struct":
            # Parse structural marker
            for pat, key in struct_patterns:
                m = re.match(pat, data, re.I)
                if m:
                    new_val = int(m.group(1))
                    # Emit on boundary change
                    if boundary_key and key == boundary_key and new_val != last_boundary_val:
                        emit_verse()
                        last_boundary_val = new_val
                    struct[key] = new_val
                    break

        elif etype == "text":
            # Check for verse-end markers like \\ N \\
            verse_ends = re.findall(r'(?:\\\\|//|--)\s*(\d+)\s*(?:\\\\|//|--)', data)
            current_parts.append(data)

            if verse_ends and verse_boundary == "verse_marker":
                struct["paragraph"] = int(verse_ends[-1])
                emit_verse(vnum=int(verse_ends[-1]))
            elif verse_ends and verse_boundary == "paragraph":
                # Also emit on verse markers for paragraph mode
                struct["paragraph"] = int(verse_ends[-1])
                emit_verse(vnum=int(verse_ends[-1]))

    # Emit any remaining text
    emit_verse()

    return verses


def make_ref(s, vnum, name):
    """Build reference string."""
    if name in ("taittiriya_aranyaka",):
        return f"{s['prapathaka'] or 1}.{vnum}"  # prapathaka.anuvaka
    if name in ("aitareya_aranyaka",):
        return f"{s['aranyaka'] or 1}.{s['adhyaya'] or 1}.{vnum}"
    if name in ("gopatha_brahmana",):
        return f"{s['prapathaka'] or 1}.{vnum}"
    if name in ("kausitaki_brahmana",):
        return f"{s['book'] or 1}.{s['chapter'] or 1}.{vnum}"
    if name in ("pancavimsa_brahmana",):
        return f"{s['chapter'] or 1}.{vnum}"
    if name in ("vajasaneyi_samhita",):
        return f"{s['paragraph'] or 1}.{vnum}"
    if name in ("rgveda_khilani",):
        return f"{s['adhyaya'] or 1}.{s['section'] or 1}.{vnum}"
    if name in ("manu_smrti",):
        return f"{s['book'] or 1}.{vnum}"
    if name in ("ramayana",):
        return f"{s['book'] or 1}.{s['chapter'] or 1}.{vnum}"
    return str(vnum)


def get_book(s, name):
    if name == "taittiriya_aranyaka": return s["prapathaka"] or 1
    if name == "aitareya_aranyaka": return s["aranyaka"] or 1
    if name == "gopatha_brahmana": return s["prapathaka"] or 1
    if name == "kausitaki_brahmana": return s["book"] or 1
    if name == "pancavimsa_brahmana": return s["chapter"] or 1
    if name == "vajasaneyi_samhita": return s["paragraph"] or 1
    if name == "manu_smrti": return s["book"] or 1
    if name == "ramayana": return s["book"] or 1
    return s.get("adhyaya") or s.get("kanda") or s.get("book") or 1


def get_section(s, name):
    if name == "taittiriya_aranyaka": return s["anuvaka"] or 1
    if name == "aitareya_aranyaka": return s["adhyaya"] or 1
    if name == "kausitaki_brahmana": return s["chapter"] or 1
    if name == "ramayana": return s["chapter"] or 1
    return s.get("chapter") or s.get("brahmana") or s.get("section") or s.get("anuvaka") or 1


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    names = sys.argv[1:] if len(sys.argv) > 1 else list(TEXTS.keys())

    print("=" * 60)
    print("TITUS Re-scraper — Clean Encoding")
    print(f"  Texts: {', '.join(names)}")
    print("=" * 60)

    results = {}
    for name in names:
        if name not in TEXTS:
            print(f"  [skip] Unknown: {name}")
            continue
        results[name] = scrape_and_parse(name, TEXTS[name])

    print("\n" + "=" * 60)
    print("SUMMARY")
    for name, count in results.items():
        print(f"  {name}: {count} verses")
    print(f"\n  Total: {sum(results.values())} verses")


if __name__ == "__main__":
    main()
