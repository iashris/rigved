#!/usr/bin/env python3
"""
Scrape Manu Smrti English translations from wisdomlib.org
and merge them into the existing manu_smrti.json
"""

import json
import re
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d"
DISCOURSE_DOC_IDS = [
    145369,  # Discourse I
    145570,  # Discourse II
    199769,  # Discourse III
    200093,  # Discourse IV
    200373,  # Discourse V
    200554,  # Discourse VI
    200659,  # Discourse VII
    200893,  # Discourse VIII
    201357,  # Discourse IX
    201731,  # Discourse X
    201875,  # Discourse XI
    202173,  # Discourse XII
]

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
})


def fetch_page(url: str, retries: int = 3) -> BeautifulSoup | None:
    for attempt in range(retries):
        try:
            resp = SESSION.get(url, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)
            else:
                print(f"  FAILED {url}: {e}", file=sys.stderr)
                return None


def get_verse_doc_ids_from_discourse(doc_id: int) -> dict[str, int]:
    """Scrape a discourse index page to find all verse links and their doc IDs."""
    url = f"{BASE_URL}/doc{doc_id}.html"
    soup = fetch_page(url)
    if not soup:
        return {}

    verse_map = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)

        m = re.search(r"doc(\d+)\.html", href)
        if not m:
            continue
        child_doc_id = int(m.group(1))
        if child_doc_id == doc_id:
            continue

        # Extract verse number from link text
        verse_match = re.search(r"(\d+\.\d+(?:-\d+)?)", text)
        if verse_match:
            verse_ref = verse_match.group(1)
            if "-" in verse_ref:
                base, end = verse_ref.rsplit("-", 1)
                chapter = base.split(".")[0]
                start_v = int(base.split(".")[1])
                end_v = int(end)
                for v in range(start_v, end_v + 1):
                    ref = f"{chapter}.{v}"
                    if ref not in verse_map:
                        verse_map[ref] = child_doc_id
            else:
                if verse_ref not in verse_map:
                    verse_map[verse_ref] = child_doc_id

    return verse_map


def extract_translation(doc_id: int, expected_ref: str) -> str | None:
    """Fetch a verse page and extract the English translation from the blockquote."""
    url = f"{BASE_URL}/doc{doc_id}.html"
    soup = fetch_page(url)
    if not soup:
        return None

    content = soup.find("div", class_="col-lg-8") or soup
    bq = content.find("blockquote")
    if not bq:
        return None

    paras = bq.find_all("p")
    # Translation is the last <p> in the blockquote that isn't:
    # - a header (<strong>)
    # - IAST transliteration (<em>)
    # - Devanagari text
    for p in reversed(paras):
        if p.find("strong") or p.find("em"):
            continue
        text = p.get_text(strip=True)
        # Skip Devanagari-only lines
        if re.match(r'^[\u0900-\u097F\s।॥०-९\d\.]+$', text):
            continue
        if len(text) > 5:
            # Clean trailing verse number markers like —(1). or —(14-15)
            text = re.sub(r'\s*—?\s*\(\d+(?:-\d+)?\)\s*\.?\s*$', '', text)
            return text.strip()

    return None


def main():
    data_path = Path(__file__).parent.parent / "public" / "data" / "epics" / "manu_smrti.json"
    with open(data_path) as f:
        verses = json.load(f)

    print(f"Loaded {len(verses)} existing verses")

    # Phase 1: Build verse -> doc_id mapping
    print("\n=== Phase 1: Scraping discourse index pages ===")
    verse_to_doc: dict[str, int] = {}

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(get_verse_doc_ids_from_discourse, did): i
            for i, did in enumerate(DISCOURSE_DOC_IDS, 1)
        }
        for fut in as_completed(futures):
            disc_num = futures[fut]
            result = fut.result()
            print(f"  Discourse {disc_num}: found {len(result)} verse links")
            verse_to_doc.update(result)

    print(f"\nTotal verse->docID mappings: {len(verse_to_doc)}")

    existing_refs = {v["reference"] for v in verses}
    mapped_refs = set(verse_to_doc.keys())
    missing = existing_refs - mapped_refs
    extra = mapped_refs - existing_refs
    print(f"  Mapped refs matching existing JSON: {len(existing_refs & mapped_refs)}")
    if missing:
        print(f"  Verses in JSON without mapping: {len(missing)}")
    if extra:
        print(f"  Extra refs from web not in JSON: {len(extra)}")

    # Phase 2: Fetch translations (20 concurrent workers)
    print("\n=== Phase 2: Fetching translations (20 workers) ===")
    translations: dict[str, str] = {}
    refs_to_fetch = [(ref, doc_id) for ref, doc_id in verse_to_doc.items() if ref in existing_refs]
    total = len(refs_to_fetch)
    print(f"  Fetching {total} verse pages...")

    completed = 0
    failed = 0
    lock_print = __import__("threading").Lock()

    def fetch_one(item):
        ref, doc_id = item
        trans = extract_translation(doc_id, ref)
        return ref, trans

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(fetch_one, item): item for item in refs_to_fetch}
        for fut in as_completed(futures):
            ref, trans = fut.result()
            completed += 1
            if trans:
                translations[ref] = trans
            else:
                failed += 1

            if completed % 50 == 0 or completed == total:
                with lock_print:
                    print(f"  [{completed}/{total}] {len(translations)} ok, {failed} failed")

    print(f"\n  Done: {len(translations)} translations, {failed} failures")

    # Phase 3: Merge
    print("\n=== Phase 3: Merging ===")
    updated = 0
    for verse in verses:
        ref = verse["reference"]
        if ref in translations:
            verse["text"] = translations[ref]
            updated += 1
        # Promote sanskrit_iast -> iast if needed
        if "sanskrit_iast" in verse and not verse.get("iast"):
            verse["iast"] = verse["sanskrit_iast"]

    print(f"  Updated {updated} verses")

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {data_path}")

    still_empty = sum(1 for v in verses if not v.get("text"))
    print(f"\n  Verses still without translation: {still_empty}/{len(verses)}")

    # Save mapping for debugging
    map_path = Path(__file__).parent / "manu_verse_map.json"
    with open(map_path, "w") as f:
        json.dump(verse_to_doc, f, indent=2, sort_keys=True)
    print(f"  Saved verse map to {map_path}")


if __name__ == "__main__":
    main()
