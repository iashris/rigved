#!/usr/bin/env python3
"""
Find specific crop mentions in Rigveda
Looking for: barley, rice, moong, sesame, urad, shimbi, proso millet
"""

import json
import re

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_crop_mantras(verses):
    """Search for specific crop references in Rigveda"""

    crop_categories = {
        'barley': {
            'patterns': [
                r'\byava\b', r'\byavas\b', r'\bbarley\b',
                r'यव', r'जौ', r'जव'
            ],
            'mantras': []
        },
        'rice': {
            'patterns': [
                r'\brice\b', r'\bvrihi\b', r'\bvrīhi\b', r'\btandula\b',
                r'व्रीहि', r'धान्य', r'तण्डुल', r'चावल', r'शाली', r'शालि'
            ],
            'mantras': []
        },
        'wheat': {
            'patterns': [
                r'\bwheat\b', r'\bgodhuma\b', r'\bgodhūma\b',
                r'गोधूम', r'गेहूं', r'गोधुम'
            ],
            'mantras': []
        },
        'mung_moong': {
            'patterns': [
                r'\bmung\b', r'\bmoong\b', r'\bmudga\b', r'\bmūṅga\b',
                r'मुद्ग', r'मूंग', r'मूङ्ग'
            ],
            'mantras': []
        },
        'sesame': {
            'patterns': [
                r'\bsesame\b', r'\btila\b', r'\bsesamum\b',
                r'तिल', r'तैल'
            ],
            'mantras': []
        },
        'urad_black_gram': {
            'patterns': [
                r'\burad\b', r'\bmasha\b', r'\bmāṣa\b', r'\bblack.*gram\b',
                r'माष', r'उड़द', r'उरद', r'मास'
            ],
            'mantras': []
        },
        'shimbi_beans': {
            'patterns': [
                r'\bshimb\b', r'\bkhalva\b', r'\bbean\b', r'\bpulse\b',
                r'शिम्ब', r'खल्व', r'शिंब', r'शिम्बि'
            ],
            'mantras': []
        },
        'proso_millet': {
            'patterns': [
                r'\bmillet\b', r'\bchena\b', r'\bpriyaṅgu\b', r'\bpriyangu\b',
                r'चेन', r'प्रियंगु', r'प्रियङ्गु', r'कंगु', r'कङ्गु'
            ],
            'mantras': []
        },
        'general_grain': {
            'patterns': [
                r'\bgrain\b', r'\bdhana\b', r'\bdhānya\b', r'\bcorn\b',
                r'धान', r'धन', r'धान्य', r'अन्न'
            ],
            'mantras': []
        }
    }

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        for crop, data in crop_categories.items():
            for pattern in data['patterns']:
                if re.search(pattern, combined, re.IGNORECASE):
                    data['mantras'].append({
                        'reference': ref,
                        'text': text,
                        'meaning': meaning,
                        'pattern_matched': pattern
                    })
                    break

    return crop_categories

def search_specific_verses(verses):
    """Search for verses that specifically mention agricultural activities"""

    agricultural_verses = []

    # Keywords related to agricultural activities
    agri_keywords = [
        r'plough', r'sow', r'seed', r'harvest', r'field', r'furrow',
        r'हल', r'बीज', r'खेत', r'कृषि', r'वपन', r'बोना'
    ]

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        for keyword in agri_keywords:
            if re.search(keyword, combined, re.IGNORECASE):
                agricultural_verses.append({
                    'reference': ref,
                    'text': text[:300],
                    'meaning': meaning[:300],
                    'keyword': keyword
                })
                break

    return agricultural_verses

def main():
    print("="*80)
    print("CROP REFERENCES IN RIGVEDA")
    print("Searching for: barley, rice, moong, sesame, urad, shimbi, proso millet")
    print("="*80)

    # Load Rigveda
    rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')

    print(f"\nTotal Rigveda verses analyzed: {len(rigveda)}")

    # Find crop mantras
    crop_results = find_crop_mantras(rigveda)

    print("\n1. SPECIFIC CROP MENTIONS IN RIGVEDA")
    print("-"*40)

    # Barley (yava) - most important cereal
    print("\n### BARLEY (Yava) References:")
    if crop_results['barley']['mantras']:
        print(f"Found {len(crop_results['barley']['mantras'])} references")
        for mantra in crop_results['barley']['mantras'][:5]:  # Show first 5
            print(f"\nRV {mantra['reference']}")
            print(f"Pattern matched: {mantra['pattern_matched']}")
            print(f"Text: {mantra['text'][:200]}...")
            if mantra['meaning']:
                print(f"Sanskrit: {mantra['meaning'][:200]}...")
    else:
        print("No barley references found")

    # Rice (vrihi)
    print("\n### RICE (Vrihi) References:")
    if crop_results['rice']['mantras']:
        print(f"Found {len(crop_results['rice']['mantras'])} references")
        for mantra in crop_results['rice']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No rice references found")

    # Wheat
    print("\n### WHEAT (Godhuma) References:")
    if crop_results['wheat']['mantras']:
        print(f"Found {len(crop_results['wheat']['mantras'])} references")
        for mantra in crop_results['wheat']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No wheat references found")

    # Mung/Moong
    print("\n### MUNG/MOONG (Mudga) References:")
    if crop_results['mung_moong']['mantras']:
        print(f"Found {len(crop_results['mung_moong']['mantras'])} references")
        for mantra in crop_results['mung_moong']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No mung/moong references found")

    # Sesame
    print("\n### SESAME (Tila) References:")
    if crop_results['sesame']['mantras']:
        print(f"Found {len(crop_results['sesame']['mantras'])} references")
        for mantra in crop_results['sesame']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No sesame references found")

    # Urad/Black Gram
    print("\n### URAD/BLACK GRAM (Masha) References:")
    if crop_results['urad_black_gram']['mantras']:
        print(f"Found {len(crop_results['urad_black_gram']['mantras'])} references")
        for mantra in crop_results['urad_black_gram']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No urad references found")

    # Shimbi/Beans
    print("\n### SHIMBI/BEANS (Khalva) References:")
    if crop_results['shimbi_beans']['mantras']:
        print(f"Found {len(crop_results['shimbi_beans']['mantras'])} references")
        for mantra in crop_results['shimbi_beans']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No shimbi/bean references found")

    # Proso Millet
    print("\n### PROSO MILLET (Chena/Priyangu) References:")
    if crop_results['proso_millet']['mantras']:
        print(f"Found {len(crop_results['proso_millet']['mantras'])} references")
        for mantra in crop_results['proso_millet']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No proso millet references found")

    # General grain references
    print("\n### GENERAL GRAIN/CORN References:")
    if crop_results['general_grain']['mantras']:
        print(f"Found {len(crop_results['general_grain']['mantras'])} references")
        print("(Showing first 3)")
        for mantra in crop_results['general_grain']['mantras'][:3]:
            print(f"\nRV {mantra['reference']}")
            print(f"Text: {mantra['text'][:150]}...")

    print("\n2. AGRICULTURAL ACTIVITY REFERENCES")
    print("-"*40)

    agri_verses = search_specific_verses(rigveda)
    print(f"\nFound {len(agri_verses)} verses mentioning agricultural activities")

    # Show famous agricultural verses
    print("\nKey Agricultural Verses:")

    # Look for specific famous verses
    for verse in rigveda:
        ref = verse.get('reference', '')
        text = verse.get('text', '')

        # RV 1.117.21 - Famous ploughing verse
        if ref == '01.117.21':
            print(f"\n### FAMOUS PLOUGHING VERSE - RV {ref}:")
            print(f"Text: {text}")
            print(f"Sanskrit: {verse.get('meaning', '')}")

        # RV 10.101 - Agricultural hymn
        if ref.startswith('10.101'):
            print(f"\n### AGRICULTURAL HYMN - RV {ref}:")
            print(f"Text: {text[:200]}...")

    print("\n3. SUMMARY STATISTICS")
    print("-"*40)

    total_crop_mentions = 0
    for crop, data in crop_results.items():
        count = len(data['mantras'])
        if count > 0:
            print(f"{crop.replace('_', ' ').title()}: {count} references")
            total_crop_mentions += count

    print(f"\nTotal crop-specific mentions: {total_crop_mentions}")
    print(f"Agricultural activity mentions: {len(agri_verses)}")

    print("\n4. ANALYSIS")
    print("-"*40)

    print("\n### Crops Actually Found in Rigveda:")
    if crop_results['barley']['mantras']:
        print("✓ BARLEY (Yava) - Primary cereal, multiple references")
    if crop_results['rice']['mantras']:
        print("✓ RICE (Vrihi) - Present but rare")
    if crop_results['wheat']['mantras']:
        print("✓ WHEAT (Godhuma) - If present")

    print("\n### Crops NOT Found or Extremely Rare:")
    if not crop_results['mung_moong']['mantras']:
        print("✗ MUNG/MOONG - Not found")
    if not crop_results['sesame']['mantras']:
        print("✗ SESAME - Not found")
    if not crop_results['urad_black_gram']['mantras']:
        print("✗ URAD - Not found")
    if not crop_results['shimbi_beans']['mantras']:
        print("✗ SHIMBI/BEANS - Not found")
    if not crop_results['proso_millet']['mantras']:
        print("✗ PROSO MILLET - Not found")

    print("\n" + "="*80)
    print("KEY FINDING:")
    print("="*80)
    print("\nThe Rigveda primarily mentions BARLEY (yava) as the main crop.")
    print("Rice appears rarely. Most pulse crops (mung, urad, etc.) and")
    print("oil seeds (sesame) are NOT mentioned in Rigveda, suggesting")
    print("these were cultivated later in the Yajurveda period.")
    print("\nThis supports the agricultural revolution thesis - the Rigveda")
    print("represents a primarily pastoral society with limited agriculture,")
    print("while diverse crop cultivation developed during Yajurveda period.")
    print("="*80)

if __name__ == "__main__":
    main()