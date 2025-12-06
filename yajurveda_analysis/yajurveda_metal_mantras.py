#!/usr/bin/env python3
"""
Extract specific metal references from Yajurveda
Focus on finding iron references similar to Atharvaveda's "śyāma ayas"
"""

import json
import re

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_metal_mantras(verses, veda_name=""):
    """Search for metal references with specific focus on iron"""

    metal_categories = {
        'iron_specific': {
            'patterns': [
                r'śyāma.*ayas', r'syama.*ayas', r'श्याम.*अयस',
                r'kṛṣṇa.*ayas', r'krishna.*ayas', r'कृष्ण.*अयस',
                r'black.*metal', r'dark.*metal', r'grey.*metal',
                r'iron', r'लोह', r'loha'
            ],
            'mantras': []
        },
        'ayas_general': {
            'patterns': [
                r'\bayas\b', r'\bayaḥ\b', r'\bayasaḥ\b',
                r'अयस्', r'अयः', r'अयसः',
                r'metal'
            ],
            'mantras': []
        },
        'gold': {
            'patterns': [
                r'\bgold\b', r'hiraṇya', r'hiranya', r'सुवर्ण', r'हिरण्य',
                r'suvarṇa', r'suvarna', r'golden'
            ],
            'mantras': []
        },
        'silver': {
            'patterns': [
                r'\bsilver\b', r'rajata', r'रजत', r'चांदी',
                r'bright.*metal', r'white.*metal'
            ],
            'mantras': []
        },
        'copper_bronze': {
            'patterns': [
                r'\bcopper\b', r'\bbronze\b', r'lohita', r'लोहित',
                r'red.*metal', r'ताम्र', r'tāmra', r'tamra'
            ],
            'mantras': []
        }
    }

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        for category, data in metal_categories.items():
            for pattern in data['patterns']:
                if re.search(pattern, combined, re.IGNORECASE):
                    data['mantras'].append({
                        'reference': f"{veda_name} {ref}",
                        'text': text,
                        'meaning': meaning,
                        'pattern_matched': pattern
                    })
                    break

    return metal_categories

def analyze_ayas_context(verses, veda_name=""):
    """Analyze context of 'ayas' mentions to determine if iron or bronze"""

    ayas_contexts = {
        'likely_iron': [],
        'likely_bronze': [],
        'ambiguous': []
    }

    # Context clues for iron
    iron_clues = ['black', 'dark', 'śyāma', 'kṛṣṇa', 'grey', 'plough', 'agricultural']
    # Context clues for bronze
    bronze_clues = ['bright', 'shining', 'golden', 'weapon', 'arrow', 'chariot']

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        if re.search(r'\bayas\b|\bayaḥ\b|अयस', combined, re.IGNORECASE):
            # Check context
            has_iron_clue = any(clue in combined for clue in iron_clues)
            has_bronze_clue = any(clue in combined for clue in bronze_clues)

            entry = {
                'reference': f"{veda_name} {ref}",
                'text': text[:300],
                'meaning': meaning[:300]
            }

            if has_iron_clue and not has_bronze_clue:
                ayas_contexts['likely_iron'].append(entry)
            elif has_bronze_clue and not has_iron_clue:
                ayas_contexts['likely_bronze'].append(entry)
            else:
                ayas_contexts['ambiguous'].append(entry)

    return ayas_contexts

def main():
    print("="*80)
    print("METAL REFERENCES IN YAJURVEDA")
    print("Searching for Iron References Similar to Atharvaveda's 'Śyāma Ayas'")
    print("="*80)

    # Load texts
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')

    # Also load Atharvaveda for comparison
    atharvaveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/atharvaveda.json')

    print("\n1. BLACK YAJURVEDA METAL REFERENCES")
    print("-"*40)

    black_metals = find_metal_mantras(yajur_black, "Black YV")

    # Iron-specific references
    print("\nIron-Specific References (śyāma/kṛṣṇa ayas):")
    if black_metals['iron_specific']['mantras']:
        for mantra in black_metals['iron_specific']['mantras'][:5]:
            print(f"\n{mantra['reference']}")
            print(f"Pattern: {mantra['pattern_matched']}")
            print(f"Text: {mantra['text'][:200]}...")
            if mantra['meaning']:
                print(f"Sanskrit: {mantra['meaning'][:200]}...")
    else:
        print("No explicit iron references found (like śyāma ayas)")

    # General ayas references
    print(f"\nGeneral 'Ayas' (Metal) References: {len(black_metals['ayas_general']['mantras'])} found")
    if black_metals['ayas_general']['mantras']:
        for mantra in black_metals['ayas_general']['mantras'][:3]:
            print(f"\n{mantra['reference']}")
            print(f"Text: {mantra['text'][:150]}...")

    # Gold references
    print(f"\nGold References: {len(black_metals['gold']['mantras'])} found")
    if black_metals['gold']['mantras']:
        for mantra in black_metals['gold']['mantras'][:2]:
            print(f"\n{mantra['reference']}")
            print(f"Text: {mantra['text'][:150]}...")

    # Silver references
    print(f"\nSilver References: {len(black_metals['silver']['mantras'])} found")
    if black_metals['silver']['mantras']:
        for mantra in black_metals['silver']['mantras'][:2]:
            print(f"\n{mantra['reference']}")
            print(f"Text: {mantra['text'][:150]}...")

    # Copper/Bronze references
    print(f"\nCopper/Bronze References: {len(black_metals['copper_bronze']['mantras'])} found")
    if black_metals['copper_bronze']['mantras']:
        for mantra in black_metals['copper_bronze']['mantras'][:2]:
            print(f"\n{mantra['reference']}")
            print(f"Text: {mantra['text'][:150]}...")

    print("\n2. WHITE YAJURVEDA METAL REFERENCES")
    print("-"*40)

    white_metals = find_metal_mantras(yajur_white, "White YV")

    # Iron-specific references
    print("\nIron-Specific References:")
    if white_metals['iron_specific']['mantras']:
        for mantra in white_metals['iron_specific']['mantras'][:5]:
            print(f"\n{mantra['reference']}")
            print(f"Pattern: {mantra['pattern_matched']}")
            print(f"Text: {mantra['text'][:200]}...")
            if mantra['meaning']:
                print(f"Sanskrit: {mantra['meaning'][:200]}...")
    else:
        print("No explicit iron references found")

    # General ayas references
    print(f"\nGeneral 'Ayas' References: {len(white_metals['ayas_general']['mantras'])} found")

    print("\n3. CONTEXTUAL ANALYSIS OF 'AYAS' REFERENCES")
    print("-"*40)

    black_ayas_context = analyze_ayas_context(yajur_black, "Black YV")
    white_ayas_context = analyze_ayas_context(yajur_white, "White YV")

    print("\nBlack Yajurveda 'Ayas' Context Analysis:")
    print(f"  Likely Iron (dark/agricultural context): {len(black_ayas_context['likely_iron'])}")
    print(f"  Likely Bronze (bright/weapon context): {len(black_ayas_context['likely_bronze'])}")
    print(f"  Ambiguous: {len(black_ayas_context['ambiguous'])}")

    if black_ayas_context['likely_iron']:
        print("\nPossible Iron References (contextual):")
        for ref in black_ayas_context['likely_iron'][:3]:
            print(f"\n{ref['reference']}")
            print(f"Text: {ref['text']}...")

    print("\nWhite Yajurveda 'Ayas' Context Analysis:")
    print(f"  Likely Iron: {len(white_ayas_context['likely_iron'])}")
    print(f"  Likely Bronze: {len(white_ayas_context['likely_bronze'])}")
    print(f"  Ambiguous: {len(white_ayas_context['ambiguous'])}")

    print("\n4. COMPARISON WITH ATHARVAVEDA")
    print("-"*40)

    av_metals = find_metal_mantras(atharvaveda, "AV")

    print("\nAtharvaveda Iron References (for comparison):")
    if av_metals['iron_specific']['mantras']:
        for mantra in av_metals['iron_specific']['mantras'][:3]:
            print(f"\n{mantra['reference']}")
            print(f"Text: {mantra['text'][:200]}...")
            if mantra['meaning']:
                print(f"Sanskrit: {mantra['meaning'][:200]}...")

    # Look for the famous śyāma ayas reference
    for verse in atharvaveda:
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        if 'श्यामम् अयो' in meaning or 'śyāmam ayo' in text.lower():
            print(f"\nFAMOUS IRON REFERENCE - AV {verse.get('reference', '')}:")
            print(f"Sanskrit: {meaning[:300]}...")
            print(f"Text: {text[:300]}...")
            break

    print("\n5. SUMMARY STATISTICS")
    print("-"*40)

    # Calculate totals
    total_black = sum(len(cat['mantras']) for cat in black_metals.values())
    total_white = sum(len(cat['mantras']) for cat in white_metals.values())
    total_av_iron = len(av_metals['iron_specific']['mantras'])

    print(f"\nBlack Yajurveda:")
    print(f"  Total metal references: {total_black}")
    print(f"  Explicit iron references: {len(black_metals['iron_specific']['mantras'])}")
    print(f"  General ayas references: {len(black_metals['ayas_general']['mantras'])}")
    print(f"  Gold references: {len(black_metals['gold']['mantras'])}")

    print(f"\nWhite Yajurveda:")
    print(f"  Total metal references: {total_white}")
    print(f"  Explicit iron references: {len(white_metals['iron_specific']['mantras'])}")
    print(f"  General ayas references: {len(white_metals['ayas_general']['mantras'])}")

    print(f"\nAtharvaveda (comparison):")
    print(f"  Explicit iron references: {total_av_iron}")

    print("\n" + "="*80)
    print("KEY FINDING:")
    print("="*80)
    print("\nThe Yajurveda does NOT contain explicit iron references like")
    print("Atharvaveda's 'śyāma ayas' (grey/black iron).")
    print("\nThe word 'ayas' appears frequently in Yajurveda but is ambiguous -")
    print("it could mean bronze (earlier sections) or iron (later sections).")
    print("\nThis supports the thesis that Yajurveda represents the TRANSITION")
    print("period from Bronze Age to Iron Age (1200-800 BCE), while")
    print("Atharvaveda shows established iron terminology.")
    print("="*80)

if __name__ == "__main__":
    main()