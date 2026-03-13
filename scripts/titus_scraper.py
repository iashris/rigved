#!/usr/bin/env python3
"""
TITUS Text Scraper — Download Vedic texts from TITUS database.

Tier 1: Aitareya Brahmana, Taittiriya Brahmana, Taittiriya Samhita,
        Kausitaki Brahmana, Brhadaranyaka Upanishad, Rgveda Khilani,
        Pancavimsa Brahmana
Tier 2: Taittiriya Aranyaka, Taittiriya Upanishad, Katha Upanishad,
        Svetasvatara Upanishad, Gopatha Brahmana, Aitareya Aranyaka,
        Aitareya Upanishad, Kena Upanishad, Kausitaki Upanishad
Tier 3: Mahabharata, Ramayana, Manu Smrti, Vajasaneyi Samhita
"""

import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "titus_raw")

# TITUS credentials
TITUS_USER = "titusstud"
TITUS_PASS = "R2gveda5"

BASE = "https://titus.uni-frankfurt.de/texte"
BASE_AUTH = "https://titus.fkidg1.uni-frankfurt.de/texte"
PRIVATE = "https://titus.fkidg1.uni-frankfurt.de/private/texte/indica/vedica"

# --- Plain text downloads (single file) ---
TXT_SOURCES = {
    "aitareya_brahmana": f"{PRIVATE}/rv/ab/ab.txt",
    "taittiriya_brahmana": f"{PRIVATE}/yvs/tb/tb.txt",
    "taittiriya_samhita": f"{PRIVATE}/yvs/ts/ts.txt",
}

# --- HTML page sources (need pagination scraping) ---
HTML_SOURCES = {
    # === TIER 1 ===
    "brhadaranyaka_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvw/upanisad/bau/bau",
        "max_pages": 200,
    },
    "rgveda_khilani": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/rvkh/rvkh",
        "max_pages": 120,
    },
    "pancavimsa_brahmana": {
        "base": f"{BASE}/etcs/ind/aind/ved/sv/pb/pb",
        "max_pages": 300,
    },
    "kausitaki_brahmana": {
        "base": f"{BASE_AUTH}/etcc/ind/aind/ved/rv/kb/kb",
        "max_pages": 150,
        "needs_auth": True,
    },
    # === TIER 2 ===
    "taittiriya_aranyaka": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvs/ta/ta",
        "max_pages": 200,
    },
    "taittiriya_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvs/upanisad/taittup/taitt",
        "max_pages": 50,
    },
    "katha_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvs/upanisad/kathup/kathu",
        "max_pages": 50,
    },
    "svetasvatara_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvs/upanisad/svetup/svetu",
        "max_pages": 50,
    },
    "gopatha_brahmana": {
        "base": f"{BASE}/etcs/ind/aind/ved/av/gb/gb",
        "max_pages": 200,
    },
    "aitareya_aranyaka": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/aa/aa",
        "max_pages": 100,
    },
    "aitareya_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/upanisad/aitup/aitup",
        "max_pages": 30,
    },
    "kena_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/sv/upanisad/kenup/kenup",
        "max_pages": 30,
    },
    "kausitaki_upanishad": {
        "base": f"{BASE}/etcs/ind/aind/ved/rv/upanisad/kausup/kausu",
        "max_pages": 50,
    },
    # === TIER 3 ===
    "mahabharata": {
        "base": f"{BASE}/etcs/ind/aind/mbh/mbh",
        "max_pages": 2500,
    },
    "ramayana": {
        "base": f"{BASE}/etcs/ind/aind/ram/ram",
        "max_pages": 1000,
    },
    "manu_smrti": {
        "base": f"{BASE}/etcs/ind/aind/ved/postved/dhs/manu/manu",
        "max_pages": 200,
    },
    "vajasaneyi_samhita": {
        "base": f"{BASE}/etcs/ind/aind/ved/yvw/vs/vs",
        "max_pages": 200,
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (academic research; vedic-texts-project)",
}


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_txt(name, url):
    """Download a plain text file from TITUS private server."""
    outpath = os.path.join(OUTPUT_DIR, f"{name}.txt")
    if os.path.exists(outpath):
        print(f"  [skip] {name}.txt already exists")
        return True

    print(f"  Downloading {name} ...")
    try:
        resp = requests.get(url, headers=HEADERS, auth=(TITUS_USER, TITUS_PASS), timeout=60)
        if resp.status_code == 200 and len(resp.text) > 500:
            with open(outpath, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"  [ok] {name}.txt — {len(resp.text):,} chars")
            return True
        else:
            # Try without auth
            resp2 = requests.get(url, headers=HEADERS, timeout=60)
            if resp2.status_code == 200 and len(resp2.text) > 500:
                with open(outpath, "w", encoding="utf-8") as f:
                    f.write(resp2.text)
                print(f"  [ok] {name}.txt — {len(resp2.text):,} chars (no auth)")
                return True
            print(f"  [FAIL] {name} — status {resp.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def extract_text_from_html(html_content):
    """Extract Sanskrit text from a TITUS HTML page."""
    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup.find_all("script"):
        script.decompose()
    for img in soup.find_all("img"):
        img.decompose()

    body = soup.find("body")
    if not body:
        return ""

    text_parts = []
    for element in body.descendants:
        if isinstance(element, str):
            cleaned = element.strip()
            if cleaned and not cleaned.startswith("{") and not cleaned.startswith("©"):
                text_parts.append(cleaned)
        elif element.name == "br":
            text_parts.append("\n")
        elif element.name in ("p", "div", "hr"):
            text_parts.append("\n")

    raw_text = " ".join(text_parts)
    raw_text = re.sub(r" +", " ", raw_text)
    raw_text = re.sub(r"\n +", "\n", raw_text)
    raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)

    return raw_text.strip()


def scrape_html_pages(name, config):
    """Scrape paginated HTML pages from TITUS."""
    outpath = os.path.join(OUTPUT_DIR, f"{name}.txt")
    if os.path.exists(outpath):
        print(f"  [skip] {name}.txt already exists")
        return True

    base = config["base"]
    max_pages = config["max_pages"]
    all_text = []
    session = requests.Session()
    session.headers.update(HEADERS)
    if config.get("needs_auth"):
        session.auth = (TITUS_USER, TITUS_PASS)

    page_num = 1
    consecutive_fails = 0

    print(f"  Scraping {name} (up to {max_pages} pages) ...")

    while page_num <= max_pages and consecutive_fails < 3:
        url = f"{base}{page_num:03d}.htm"
        try:
            resp = session.get(url, timeout=30)

            if resp.status_code == 404 or "not (yet) available" in resp.text:
                consecutive_fails += 1
                page_num += 1
                continue

            if resp.status_code == 200 and len(resp.text) > 200:
                text = extract_text_from_html(resp.text)
                if text and len(text) > 50:
                    all_text.append(f"\n--- Page {page_num:03d} ---\n")
                    all_text.append(text)
                    consecutive_fails = 0
                    if page_num % 25 == 0:
                        print(f"    page {page_num:03d} ok ({len(text):,} chars)")
                else:
                    consecutive_fails += 1
            else:
                consecutive_fails += 1

        except Exception as e:
            print(f"    page {page_num:03d} error: {e}")
            consecutive_fails += 1

        page_num += 1
        time.sleep(0.3)  # Be respectful to the server

    if all_text:
        full_text = "\n".join(all_text)
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(full_text)
        total_pages = page_num - 1 - consecutive_fails
        print(f"  [ok] {name}.txt — {len(full_text):,} chars from ~{total_pages} pages")
        return True
    else:
        print(f"  [FAIL] {name} — no content scraped")
        return False


def main():
    ensure_output_dir()

    # Allow filtering by tier via command line
    tiers = sys.argv[1:] if len(sys.argv) > 1 else ["txt", "tier1", "tier2", "tier3"]

    print("=" * 60)
    print("TITUS Vedic Text Scraper")
    print(f"  Tiers: {', '.join(tiers)}")
    print("=" * 60)

    results = {}

    tier1_html = ["brhadaranyaka_upanishad", "rgveda_khilani", "pancavimsa_brahmana", "kausitaki_brahmana"]
    tier2_html = ["taittiriya_aranyaka", "taittiriya_upanishad", "katha_upanishad",
                  "svetasvatara_upanishad", "gopatha_brahmana", "aitareya_aranyaka",
                  "aitareya_upanishad", "kena_upanishad", "kausitaki_upanishad"]
    tier3_html = ["mahabharata", "ramayana", "manu_smrti", "vajasaneyi_samhita"]

    # Phase 1: Plain text downloads
    if "txt" in tiers:
        print("\n--- Plain text downloads ---")
        for name, url in TXT_SOURCES.items():
            results[name] = download_txt(name, url)

    # Phase 2: Tier 1 HTML
    if "tier1" in tiers:
        print("\n--- Tier 1: HTML scraping ---")
        for name in tier1_html:
            results[name] = scrape_html_pages(name, HTML_SOURCES[name])

    # Phase 3: Tier 2 HTML
    if "tier2" in tiers:
        print("\n--- Tier 2: HTML scraping ---")
        for name in tier2_html:
            results[name] = scrape_html_pages(name, HTML_SOURCES[name])

    # Phase 4: Tier 3 HTML
    if "tier3" in tiers:
        print("\n--- Tier 3: HTML scraping ---")
        for name in tier3_html:
            results[name] = scrape_html_pages(name, HTML_SOURCES[name])

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {name}")

    succeeded = sum(1 for v in results.values() if v)
    print(f"\n  {succeeded}/{len(results)} texts downloaded")
    print(f"  Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
