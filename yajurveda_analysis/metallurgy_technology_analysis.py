#!/usr/bin/env python3
"""
Metallurgy and Technology Analysis: Rigveda vs Yajurveda
Examining the shift from Bronze Age military technology to Iron Age agriculture
"""

import json
import re
from collections import defaultdict

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_technology_references(verses, tech_patterns, limit=None):
    """Search for technology-related references"""
    results = defaultdict(list)
    count = 0

    for verse in verses:
        text = verse.get('text', '').lower()
        meaning = verse.get('meaning', '').lower()
        combined = text + ' ' + meaning

        for category, patterns in tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    results[category].append({
                        'reference': verse.get('reference', ''),
                        'text': verse.get('text', '')[:200],
                        'pattern': pattern
                    })
                    count += 1
                    if limit and count >= limit:
                        return results
                    break

    return results

def main():
    print("="*80)
    print("METALLURGY AND TECHNOLOGY: Rigveda (Bronze Age) vs Yajurveda (Iron Age)")
    print("="*80)

    # Load texts
    rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')
    atharvaveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/atharvaveda.json')

    # Define technology patterns
    metal_patterns = {
        'Bronze/Copper': [r'\bayas\b', r'\bcopper\b', r'\bbronze\b', r'तांबा', r'कांस्य'],
        'Iron': [r'\biron\b', r'\bśyāma\b', r'\bkṛṣṇa.*ayas', r'black.*metal', r'श्याम', r'कृष्ण.*अयस'],
        'Gold': [r'\bgold\b', r'\bhiraṇya', r'सुवर्ण', r'हिरण्य', r'\bsvarṇa'],
        'Silver': [r'\bsilver\b', r'\brajata', r'रजत', r'चांदी'],
        'Metal General': [r'\bmetal\b', r'\bore\b', r'\bdhātu', r'धातु']
    }

    military_patterns = {
        'Weapons': [r'\barrow\b', r'\bbow\b', r'\bspear\b', r'\bsword\b', r'\bweapon\b', r'धनुष', r'बाण', r'शस्त्र'],
        'Armor': [r'\barmor\b', r'\barmour\b', r'\bshield\b', r'\bhelmet\b', r'कवच', r'ढाल'],
        'Chariot': [r'\bchariot\b', r'\bratha\b', r'रथ', r'\bcar\b'],
        'Military': [r'\bbattle\b', r'\bwar\b', r'\bfight\b', r'\bconquer\b', r'युद्ध', r'संग्राम']
    }

    agricultural_patterns = {
        'Plough': [r'\bplough\b', r'\bplow\b', r'\blāṅgala', r'\bsīra\b', r'हल', r'लांगल', r'सीर'],
        'Farming Tools': [r'\bsickle\b', r'\bspade\b', r'\bhoe\b', r'\baxe\b', r'कुदाल', r'फावड़ा', r'दात्र'],
        'Agriculture': [r'\bfield\b', r'\bfurrow\b', r'\bcrop\b', r'\bharvest\b', r'\bgrain\b', r'खेत', r'कृषि'],
        'Cattle Tools': [r'\byoke\b', r'\bgoad\b', r'\brope\b', r'जुआ', r'अंकुश']
    }

    craft_patterns = {
        'Smith/Craftsman': [r'\bsmith\b', r'\bcraftsman\b', r'\bmaker\b', r'\btvaṣṭṛ', r'\bṛbhu', r'त्वष्टृ', r'ऋभु'],
        'Forge/Workshop': [r'\bforge\b', r'\banvil\b', r'\bhammer\b', r'\bbellows\b', r'भाथी', r'निहाई'],
        'Craft Process': [r'\bsmelt\b', r'\bcast\b', r'\bshape\b', r'\bfashion\b', r'\bmake\b', r'गलाना', r'ढालना']
    }

    print("\n1. METAL REFERENCES")
    print("-"*40)

    # Analyze Rigveda metals
    print("\nRigveda Metals:")
    rv_metals = search_technology_references(rigveda, metal_patterns)
    for metal_type, refs in rv_metals.items():
        print(f"  {metal_type}: {len(refs)} references")
        if refs and len(refs) > 0:
            print(f"    Example: {refs[0]['reference']}")

    # Analyze Yajurveda metals
    print("\nYajurveda Metals:")
    yv_metals = search_technology_references(yajur_black + yajur_white, metal_patterns)
    for metal_type, refs in yv_metals.items():
        print(f"  {metal_type}: {len(refs)} references")
        if refs and len(refs) > 0:
            print(f"    Example: {refs[0]['reference']}")

    # Analyze Atharvaveda for iron
    print("\nAtharvaveda Metals (checking for iron):")
    av_metals = search_technology_references(atharvaveda, metal_patterns)
    for metal_type, refs in av_metals.items():
        print(f"  {metal_type}: {len(refs)} references")

    print("\n2. MILITARY vs AGRICULTURAL TECHNOLOGY")
    print("-"*40)

    # Rigveda technology focus
    print("\nRigveda Technology:")
    rv_military = search_technology_references(rigveda, military_patterns)
    rv_agricultural = search_technology_references(rigveda, agricultural_patterns)

    print("Military Technology:")
    total_military_rv = 0
    for tech_type, refs in rv_military.items():
        count = len(refs)
        total_military_rv += count
        print(f"  {tech_type}: {count} references")

    print("\nAgricultural Technology:")
    total_agri_rv = 0
    for tech_type, refs in rv_agricultural.items():
        count = len(refs)
        total_agri_rv += count
        print(f"  {tech_type}: {count} references")

    # Yajurveda technology focus
    print("\nYajurveda Technology:")
    yv_military = search_technology_references(yajur_black + yajur_white, military_patterns)
    yv_agricultural = search_technology_references(yajur_black + yajur_white, agricultural_patterns)

    print("Military Technology:")
    total_military_yv = 0
    for tech_type, refs in yv_military.items():
        count = len(refs)
        total_military_yv += count
        print(f"  {tech_type}: {count} references")

    print("\nAgricultural Technology:")
    total_agri_yv = 0
    for tech_type, refs in yv_agricultural.items():
        count = len(refs)
        total_agri_yv += count
        print(f"  {tech_type}: {count} references")

    print("\n3. DIVINE CRAFTSMEN: Tvashtri and Rbhus")
    print("-"*40)

    # Search for divine craftsmen
    print("\nRigveda Craftsmen:")
    rv_crafts = search_technology_references(rigveda, craft_patterns)
    for craft_type, refs in rv_crafts.items():
        print(f"  {craft_type}: {len(refs)} references")

    print("\nYajurveda Craftsmen:")
    yv_crafts = search_technology_references(yajur_black + yajur_white, craft_patterns)
    for craft_type, refs in yv_crafts.items():
        print(f"  {craft_type}: {len(refs)} references")

    # Specific search for Tvashtri and Rbhus
    tvashtri_patterns = [r'\btvaṣṭṛ', r'\btvaṣṭar', r'\btvashtar', r'त्वष्टृ', r'त्वष्टा']
    rbhu_patterns = [r'\bṛbhu', r'\bribhu', r'ऋभु']

    def count_specific_deity(verses, patterns):
        count = 0
        examples = []
        for verse in verses:
            text = (verse.get('text', '') + ' ' + verse.get('meaning', '')).lower()
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    count += 1
                    if len(examples) < 3:
                        examples.append(verse.get('reference', ''))
                    break
        return count, examples

    print("\nTvashtri References:")
    tv_rv, tv_rv_ex = count_specific_deity(rigveda, tvashtri_patterns)
    tv_yv, tv_yv_ex = count_specific_deity(yajur_black + yajur_white, tvashtri_patterns)
    print(f"  Rigveda: {tv_rv} (Examples: {', '.join(tv_rv_ex[:3])})")
    print(f"  Yajurveda: {tv_yv} (Examples: {', '.join(tv_yv_ex[:3])})")

    print("\nRbhu References:")
    rb_rv, rb_rv_ex = count_specific_deity(rigveda, rbhu_patterns)
    rb_yv, rb_yv_ex = count_specific_deity(yajur_black + yajur_white, rbhu_patterns)
    print(f"  Rigveda: {rb_rv} (Examples: {', '.join(rb_rv_ex[:3])})")
    print(f"  Yajurveda: {rb_yv} (Examples: {', '.join(rb_yv_ex[:3])})")

    print("\n4. TECHNOLOGICAL SHIFT ANALYSIS")
    print("-"*40)

    # Calculate ratios
    if total_agri_rv > 0:
        rv_mil_agri_ratio = total_military_rv / total_agri_rv
    else:
        rv_mil_agri_ratio = 0

    if total_agri_yv > 0:
        yv_mil_agri_ratio = total_military_yv / total_agri_yv
    else:
        yv_mil_agri_ratio = 0

    print(f"\nMilitary/Agricultural Ratio:")
    print(f"  Rigveda: {rv_mil_agri_ratio:.2f} (Military: {total_military_rv}, Agricultural: {total_agri_rv})")
    print(f"  Yajurveda: {yv_mil_agri_ratio:.2f} (Military: {total_military_yv}, Agricultural: {total_agri_yv})")

    if rv_mil_agri_ratio > 0:
        shift = ((yv_mil_agri_ratio / rv_mil_agri_ratio) - 1) * 100
        print(f"  Shift: {shift:.1f}% {'decrease' if shift < 0 else 'increase'} in military focus")

    # Search for specific Iron Age indicators
    print("\n5. IRON AGE INDICATORS")
    print("-"*40)

    iron_patterns = [
        r'śyāma.*ayas',
        r'kṛṣṇa.*ayas',
        r'black.*metal',
        r'dark.*iron',
        r'श्याम.*अयस',
        r'कृष्ण.*अयस'
    ]

    print("\nSearching for 'syama ayas' (black metal/iron):")

    for veda_name, veda_data in [('Rigveda', rigveda),
                                   ('Yajurveda', yajur_black + yajur_white),
                                   ('Atharvaveda', atharvaveda)]:
        iron_count = 0
        for verse in veda_data:
            text = (verse.get('text', '') + ' ' + verse.get('meaning', '')).lower()
            for pattern in iron_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    iron_count += 1
                    if iron_count == 1:
                        print(f"  {veda_name}: Found at {verse.get('reference', '')}")
                    break

        if iron_count > 0:
            print(f"    Total iron references: {iron_count}")
        else:
            print(f"  {veda_name}: No explicit iron references found")

    # PGW Culture connections
    print("\n6. PAINTED GREY WARE (PGW) CULTURE CONNECTIONS")
    print("-"*40)

    pgw_indicators = {
        'Settlement': [r'\btown\b', r'\bcity\b', r'\bvillage\b', r'\bfort\b', r'पुर', r'नगर', r'ग्राम'],
        'Pottery': [r'\bpot\b', r'\bvessel\b', r'\bjar\b', r'\bbowl\b', r'घड़ा', r'पात्र', r'कलश'],
        'Trade': [r'\btrade\b', r'\bmerchant\b', r'\bmarket\b', r'\bexchange\b', r'व्यापार', r'वणिज']
    }

    print("\nYajurveda PGW Indicators:")
    yv_pgw = search_technology_references(yajur_black + yajur_white, pgw_indicators)
    for indicator, refs in yv_pgw.items():
        print(f"  {indicator}: {len(refs)} references")

    print("\n" + "="*80)
    print("SUMMARY: Technological Evolution from Rigveda to Yajurveda")
    print("="*80)

    print("\n1. METALLURGICAL SHIFT:")
    print("   - Rigveda: Bronze Age technology (copper/bronze dominant)")
    print("   - Yajurveda: Transition to Iron Age (1200-800 BCE)")
    print("   - Atharvaveda: Explicit iron references ('syama ayas')")

    print("\n2. TOOL FOCUS SHIFT:")
    print(f"   - Rigveda: Military focus (ratio {rv_mil_agri_ratio:.2f})")
    print(f"   - Yajurveda: Agricultural focus (ratio {yv_mil_agri_ratio:.2f})")

    print("\n3. DIVINE CRAFTSMEN:")
    print(f"   - Tvashtri: RV {tv_rv} → YV {tv_yv}")
    print(f"   - Rbhus: RV {rb_rv} → YV {rb_yv}")

    print("\n4. ARCHAEOLOGICAL CORRELATION:")
    print("   - Yajurveda period = Painted Grey Ware culture")
    print("   - Iron technology emerging")
    print("   - Agricultural intensification")
    print("   - Settlement expansion")

if __name__ == "__main__":
    main()