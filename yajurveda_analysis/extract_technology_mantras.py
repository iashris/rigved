#!/usr/bin/env python3
"""
Extract specific technology-related mantras from Vedic texts
"""

import json
import re

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_technology_mantras(verses, keywords, limit=5):
    """Find specific mantras containing technology keywords"""
    results = []
    for verse in verses:
        text = verse.get('text', '').lower()
        meaning = verse.get('meaning', '').lower()

        for keyword in keywords:
            if keyword.lower() in text or keyword.lower() in meaning:
                results.append({
                    'reference': verse.get('reference', ''),
                    'text': verse.get('text', ''),
                    'meaning': verse.get('meaning', ''),
                    'keyword': keyword
                })
                break

        if len(results) >= limit:
            break

    return results

def main():
    print("="*80)
    print("EXTRACTING SPECIFIC TECHNOLOGY MANTRAS")
    print("="*80)

    # Load texts
    rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')
    atharvaveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/atharvaveda.json')

    # Combined Yajurveda
    yajurveda = yajur_black + yajur_white

    print("\n1. PLOUGH (Sira/Langala) MANTRAS")
    print("-"*40)

    plough_keywords = ['plough', 'plow', 'sira', 'sīra', 'langala', 'lāṅgala', 'furrow']

    print("\nRigveda Plough Mantras:")
    rv_plough = find_technology_mantras(rigveda, plough_keywords, 3)
    for mantra in rv_plough:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nYajurveda Plough Mantras:")
    yv_plough = find_technology_mantras(yajurveda, plough_keywords, 3)
    for mantra in yv_plough:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\n2. WEAPON MANTRAS")
    print("-"*40)

    weapon_keywords = ['sword', 'arrow', 'bow', 'spear', 'vajra', 'thunderbolt', 'weapon']

    print("\nRigveda Weapon Mantras:")
    rv_weapons = find_technology_mantras(rigveda, weapon_keywords, 3)
    for mantra in rv_weapons:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nYajurveda Weapon Mantras:")
    yv_weapons = find_technology_mantras(yajurveda, weapon_keywords, 3)
    for mantra in yv_weapons:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\n3. CHARIOT MANTRAS")
    print("-"*40)

    chariot_keywords = ['chariot', 'ratha', 'car', 'wheel']

    print("\nRigveda Chariot Mantras:")
    rv_chariot = find_technology_mantras(rigveda, chariot_keywords, 3)
    for mantra in rv_chariot:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nYajurveda Chariot Mantras:")
    yv_chariot = find_technology_mantras(yajurveda, chariot_keywords, 2)
    for mantra in yv_chariot:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\n4. AGRICULTURAL TOOL MANTRAS")
    print("-"*40)

    agri_keywords = ['sickle', 'spade', 'axe', 'yoke', 'field', 'harvest', 'grain', 'seed']

    print("\nRigveda Agricultural Mantras:")
    rv_agri = find_technology_mantras(rigveda, agri_keywords, 3)
    for mantra in rv_agri:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nYajurveda Agricultural Mantras:")
    yv_agri = find_technology_mantras(yajurveda, agri_keywords, 3)
    for mantra in yv_agri:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\n5. METAL/SMITH MANTRAS")
    print("-"*40)

    metal_keywords = ['iron', 'copper', 'bronze', 'gold', 'smith', 'forge', 'anvil', 'metal']

    print("\nRigveda Metal/Smith Mantras:")
    rv_metal = find_technology_mantras(rigveda, metal_keywords, 3)
    for mantra in rv_metal:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nYajurveda Metal/Smith Mantras:")
    yv_metal = find_technology_mantras(yajurveda, metal_keywords, 3)
    for mantra in yv_metal:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

    print("\nAtharvaveda Iron Mantras:")
    av_iron = find_technology_mantras(atharvaveda, ['iron', 'syama', 'śyāma', 'black metal'], 3)
    for mantra in av_iron:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        if mantra['meaning']:
            print(f"Sanskrit: {mantra['meaning'][:150]}...")

    print("\n6. TVASHTRI AND RBHU MANTRAS")
    print("-"*40)

    print("\nRigveda Tvashtri Mantras:")
    tv_mantras = find_technology_mantras(rigveda, ['tvashtar', 'tvaṣṭṛ', 'tvastar'], 2)
    for mantra in tv_mantras:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:200]}...")

    print("\nRigveda Rbhu Mantras:")
    rb_mantras = find_technology_mantras(rigveda, ['rbhu', 'ribhu', 'ṛbhu'], 2)
    for mantra in rb_mantras:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:200]}...")

    print("\n7. SETTLEMENT/VILLAGE MANTRAS")
    print("-"*40)

    settlement_keywords = ['village', 'town', 'city', 'settlement', 'house', 'dwelling']

    print("\nYajurveda Settlement Mantras:")
    yv_settle = find_technology_mantras(yajurveda, settlement_keywords, 3)
    for mantra in yv_settle:
        print(f"\nRef: {mantra['reference']}")
        print(f"Text: {mantra['text'][:150]}...")
        print(f"Keyword: {mantra['keyword']}")

if __name__ == "__main__":
    main()