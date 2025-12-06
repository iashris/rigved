#!/usr/bin/env python3
"""
Extract specific Śulba-related geometric principles from Yajurveda
Focus on area doubling, squaring the circle, and mathematical theorems
"""

import json
import re

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_sulba_principles(verses, veda_name=""):
    """Search for Śulba Sūtra related geometric principles"""

    findings = {
        'area_doubling': [],
        'squaring_circle': [],
        'diagonal_theorems': [],
        'altar_dimensions': [],
        'cord_geometry': [],
        'mathematical_operations': []
    }

    # Specific search patterns for mathematical concepts
    patterns = {
        'area_doubling': [
            r'double.*area', r'twice.*space', r'two.*times.*size',
            r'द्विगुण.*क्षेत्र', r'दुगुन', r'dviguṇa', r'duguna',
            r'enlarge.*altar', r'increase.*size'
        ],
        'squaring_circle': [
            r'square.*equal.*circle', r'circle.*equal.*square',
            r'round.*square', r'circular.*quadrilateral',
            r'वृत्त.*चतुरस्र', r'वर्तुल.*चतुर',
            r'transform.*shape'
        ],
        'diagonal_theorems': [
            r'diagonal', r'hypotenuse', r'कर्ण', r'karṇa',
            r'side.*produce.*area', r'side.*combine.*equal'
        ],
        'altar_dimensions': [
            r'\d+.*cubit', r'\d+.*aṅgula', r'\d+.*pradesa',
            r'length.*\d+', r'breadth.*\d+', r'height.*\d+',
            r'हस्त', r'अंगुल', r'प्रदेश',
            r'hasta', r'aṅgula', r'pradeśa',
            r'measure', r'dimension', r'size.*altar'
        ],
        'cord_geometry': [
            r'cord.*measure', r'rope.*stretch', r'string.*mark',
            r'रज्जु', r'शुल्ब', r'सूत्र', r'rajju', r'śulba', r'sūtra',
            r'stretch.*east.*west', r'stake', r'peg'
        ],
        'mathematical_operations': [
            r'add.*subtract', r'multiply', r'divide',
            r'sum', r'difference', r'product',
            r'combine.*area', r'join.*space'
        ]
    }

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        # Check for mathematical/geometric content
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, combined, re.IGNORECASE):
                    findings[category].append({
                        'reference': f"{veda_name} {ref}",
                        'text': text,
                        'meaning': meaning,
                        'pattern_found': pattern
                    })
                    break

    return findings

def extract_specific_mantras(verses, veda_name=""):
    """Extract mantras with specific mathematical instructions"""

    specific_mantras = []

    # Look for mantras with specific numerical instructions
    numerical_patterns = [
        r'(\d+).*long.*(\d+).*wide',
        r'(\d+).*cubit.*(\d+).*cubit',
        r'length.*(\d+).*breadth.*(\d+)',
        r'east.*(\d+).*west.*(\d+)',
        r'(\d+).*times.*(\d+)',
        r'square.*(\d+)',
        r'equal.*(\d+)'
    ]

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')
        combined = (text + ' ' + meaning).lower()

        for pattern in numerical_patterns:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                specific_mantras.append({
                    'reference': f"{veda_name} {ref}",
                    'text': text[:500],
                    'meaning': meaning[:500],
                    'numbers_found': match.groups()
                })
                break

    return specific_mantras

def main():
    print("="*80)
    print("ŚULBA-RELATED GEOMETRIC PRINCIPLES IN YAJURVEDA")
    print("Mathematical Theorems and Area Calculations")
    print("="*80)

    # Load texts
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')

    # Also load docs folder versions if they have different content
    try:
        yajur_white_docs = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/docs/yajurveda_white.json')
    except:
        yajur_white_docs = []

    print("\n1. SEARCHING FOR AREA DOUBLING PRINCIPLES")
    print("-"*40)

    black_principles = search_sulba_principles(yajur_black, "Black YV")
    white_principles = search_sulba_principles(yajur_white, "White YV")

    # Check for area doubling specifically
    print("\nArea Doubling References:")
    all_doubling = black_principles['area_doubling'] + white_principles['area_doubling']
    if all_doubling:
        for ref in all_doubling[:5]:
            print(f"\n{ref['reference']}")
            print(f"Text: {ref['text'][:200]}...")
            if ref['meaning']:
                print(f"Sanskrit: {ref['meaning'][:200]}...")
    else:
        print("No explicit area doubling references found.")

    print("\n2. DIAGONAL AND PYTHAGOREAN PRINCIPLES")
    print("-"*40)

    all_diagonal = black_principles['diagonal_theorems'] + white_principles['diagonal_theorems']
    if all_diagonal:
        for ref in all_diagonal[:5]:
            print(f"\n{ref['reference']}")
            print(f"Text: {ref['text'][:200]}...")
            if ref['meaning']:
                print(f"Sanskrit: {ref['meaning'][:200]}...")
    else:
        print("No diagonal theorem references found.")

    print("\n3. SPECIFIC ALTAR DIMENSIONS")
    print("-"*40)

    all_dimensions = black_principles['altar_dimensions'] + white_principles['altar_dimensions']
    if all_dimensions:
        for ref in all_dimensions[:10]:
            print(f"\n{ref['reference']}")
            print(f"Pattern: {ref['pattern_found']}")
            print(f"Text: {ref['text'][:200]}...")
    else:
        print("No specific dimensional references found.")

    print("\n4. CORD GEOMETRY (ŚULBA)")
    print("-"*40)

    all_cord = black_principles['cord_geometry'] + white_principles['cord_geometry']
    if all_cord:
        for ref in all_cord[:5]:
            print(f"\n{ref['reference']}")
            print(f"Text: {ref['text'][:200]}...")
            if ref['meaning']:
                print(f"Sanskrit: {ref['meaning'][:200]}...")
    else:
        print("No cord geometry references found.")

    print("\n5. MANTRAS WITH SPECIFIC NUMERICAL INSTRUCTIONS")
    print("-"*40)

    black_numerical = extract_specific_mantras(yajur_black, "Black YV")
    white_numerical = extract_specific_mantras(yajur_white, "White YV")

    all_numerical = black_numerical + white_numerical
    if all_numerical:
        for mantra in all_numerical[:5]:
            print(f"\n{mantra['reference']}")
            print(f"Numbers: {mantra['numbers_found']}")
            print(f"Text: {mantra['text'][:200]}...")
    else:
        print("No mantras with specific numerical instructions found.")

    print("\n6. MATHEMATICAL OPERATIONS")
    print("-"*40)

    all_math = black_principles['mathematical_operations'] + white_principles['mathematical_operations']
    if all_math:
        for ref in all_math[:5]:
            print(f"\n{ref['reference']}")
            print(f"Text: {ref['text'][:200]}...")
    else:
        print("No mathematical operation references found.")

    # Search for specific Taittiriya Samhita references (Black YV)
    print("\n7. TAITTIRIYA SAMHITA SPECIFIC GEOMETRIC REFERENCES")
    print("-"*40)

    # Taittiriya Samhita is Black Yajurveda - search for specific sections
    # that are known to contain geometric content

    geometric_sections = []
    for verse in yajur_black:
        ref = verse.get('reference', '')
        # Look for sections 4, 5, 6 which often contain altar construction
        if any(ref.startswith(f"{i}.") for i in ['4', '5', '6']):
            text = verse.get('text', '').lower()
            meaning = verse.get('meaning', '').lower()

            # Check for altar, fire, construction keywords
            if any(kw in text + meaning for kw in ['altar', 'fire', 'vedi', 'citi', 'agni', 'construct', 'build']):
                geometric_sections.append({
                    'reference': ref,
                    'text': verse.get('text', '')[:300],
                    'meaning': verse.get('meaning', '')[:300]
                })

    if geometric_sections:
        print("\nPotential geometric content in Taittiriya Samhita sections 4-6:")
        for section in geometric_sections[:5]:
            print(f"\nTS {section['reference']}")
            print(f"Text: {section['text']}...")

    print("\n" + "="*80)
    print("SUMMARY OF GEOMETRIC PRINCIPLES FOUND")
    print("="*80)

    total_found = sum(len(v) for v in black_principles.values()) + \
                  sum(len(v) for v in white_principles.values())

    print(f"\nTotal geometric/mathematical references: {total_found}")
    print("\nCategories found:")
    for category in black_principles.keys():
        count = len(black_principles[category]) + len(white_principles[category])
        if count > 0:
            print(f"  - {category.replace('_', ' ').title()}: {count}")

    print("\nKEY FINDING:")
    print("While the Yajurveda contains numerous altar construction references,")
    print("the explicit mathematical theorems (like area doubling formulas)")
    print("are more fully developed in the later Śulba Sūtras, which are")
    print("appendices to the Vedas rather than part of the main text.")
    print("\nThe Yajurveda provides the ritual context and basic geometric")
    print("instructions that led to the mathematical discoveries documented")
    print("in the Śulba Sūtras (c. 800-500 BCE).")

if __name__ == "__main__":
    main()