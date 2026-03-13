#!/usr/bin/env python3
"""
Scrape Indo-European comparative texts from TITUS.
Reuses scraper logic from titus_scraper.py.
"""

import os
import sys

# Add parent to path so we can import
sys.path.insert(0, os.path.dirname(__file__))
from titus_scraper import scrape_html_pages, ensure_output_dir, OUTPUT_DIR

BASE = "https://titus.uni-frankfurt.de/texte"
BASE_AUTH = "https://titus.fkidg1.uni-frankfurt.de/texte"

IE_SOURCES = {
    # === TIER 1: Essential ===
    "avestan_corpus": {
        "base": f"{BASE}/etcs/iran/airan/avesta/avest",
        "max_pages": 500,
    },
    "old_persian": {
        "base": f"{BASE}/etcs/iran/airan/apers/apers",
        "max_pages": 50,
    },
    "poetic_edda": {
        "base": f"{BASE}/etcs/germ/anord/edda/edda",
        "max_pages": 100,
    },
    "gothic_nt": {
        "base": f"{BASE}/etcs/germ/got/gotnt/gotnt",
        "max_pages": 200,
    },
    "bundahisn": {
        "base": f"{BASE}/etcs/iran/miran/mpers/bundahis/bunda",
        "max_pages": 100,
    },
    "ossetic_nart": {
        "base": f"{BASE}/etcs/iran/niran/oss/nart/nart",
        "max_pages": 50,
    },
    "hittite_ritual": {
        "base": f"{BASE}/etcs/anatol/hittite/cthtx/cthtx",
        "max_pages": 200,
    },
    "tocharian_a": {
        "base": f"{BASE}/etcs/toch/tocha/tocha",
        "max_pages": 200,
    },
    "old_prussian": {
        "base": f"{BASE}/etcs/balt/apreuss/apreuss/apreu",
        "max_pages": 50,
    },
}


def main():
    ensure_output_dir()

    names = sys.argv[1:] if len(sys.argv) > 1 else list(IE_SOURCES.keys())

    print("=" * 60)
    print("TITUS IE Comparative Texts Scraper")
    print(f"  Texts: {len(names)}")
    print("=" * 60)

    results = {}
    for name in names:
        if name not in IE_SOURCES:
            print(f"  [skip] Unknown: {name}")
            continue
        results[name] = scrape_html_pages(name, IE_SOURCES[name])

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        print(f"  [{'OK' if ok else 'FAIL'}] {name}")

    succeeded = sum(1 for v in results.values() if v)
    print(f"\n  {succeeded}/{len(results)} downloaded")
    print(f"  Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
