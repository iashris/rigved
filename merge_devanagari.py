#!/usr/bin/env python3
"""
Script to merge Devanagari Sanskrit text into Yajurveda JSON files.
This adds the 'meaning' field to each verse with its Sanskrit translation.
"""

import json
import os

def merge_devanagari(veda_file, devanagari_file, output_file):
    """
    Merge Devanagari text into Yajurveda JSON file.

    Args:
        veda_file: Path to the existing Yajurveda JSON file
        devanagari_file: Path to the Devanagari JSON file with Sanskrit text
        output_file: Path to write the merged output
    """
    # Load the Yajurveda verses
    with open(veda_file, 'r', encoding='utf-8') as f:
        verses = json.load(f)

    # Load the Devanagari mappings
    with open(devanagari_file, 'r', encoding='utf-8') as f:
        devanagari = json.load(f)

    # Merge the data
    matched = 0
    unmatched = 0

    for verse in verses:
        reference = verse['reference']

        if reference in devanagari:
            verse['meaning'] = devanagari[reference]
            matched += 1
        else:
            unmatched += 1

    # Write the updated verses
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)

    print(f"Processed {len(verses)} verses:")
    print(f"  - Matched: {matched}")
    print(f"  - Unmatched: {unmatched}")

    return matched, unmatched

def main():
    # Define file paths
    base_dir = 'public'

    # Process Krishna Yajurveda (Black)
    print("Processing Krishna Yajurveda (Black)...")
    merge_devanagari(
        os.path.join(base_dir, 'yajurveda_black.json'),
        os.path.join(base_dir, 'devanagari_black.json'),
        os.path.join(base_dir, 'yajurveda_black.json')
    )
    print()

    # Process Shukla Yajurveda (White)
    print("Processing Shukla Yajurveda (White)...")
    merge_devanagari(
        os.path.join(base_dir, 'yajurveda_white.json'),
        os.path.join(base_dir, 'devanagari_white.json'),
        os.path.join(base_dir, 'yajurveda_white.json')
    )
    print()

    print("Done! Yajurveda JSON files now include Sanskrit text in the 'meaning' field.")

if __name__ == '__main__':
    main()
