#!/usr/bin/env python3
"""
Deity Comparison Analysis Using Percentages
Analyzes deity mentions as percentage of total text length across Rigveda, Yajurveda, and Atharvaveda
"""

import json
import re
from collections import defaultdict
import os

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_text_content(veda_data):
    """Extract all text content from Veda data structure"""
    all_text = []

    # All Vedas have the same simple structure - array of verse objects
    if isinstance(veda_data, list):
        for verse in veda_data:
            # Get English translation
            if 'text' in verse and verse['text']:
                all_text.append(verse['text'])
            # Get Sanskrit/meaning text
            if 'meaning' in verse and verse['meaning']:
                all_text.append(verse['meaning'])

    return ' '.join(all_text)

def count_deity_mentions(text, deity_patterns):
    """Count mentions of deities using regex patterns"""
    text_lower = text.lower()
    counts = {}

    for deity_name, patterns in deity_patterns.items():
        total = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            total += len(matches)
        counts[deity_name] = total

    return counts

def main():
    # Define deity search patterns
    deity_patterns = {
        'Indra': [r'\bindra\b', r'इन्द्र', r'इंद्र'],
        'Agni': [r'\bagni\b', r'अग्नि'],
        'Rudra/Shiva': [r'\brudra\b', r'रुद्र', r'\bshiva\b', r'शिव', r'\bśiva\b'],
        'Soma': [r'\bsoma\b', r'सोम'],
        'Varuna': [r'\bvaruna\b', r'वरुण'],
        'Vishnu': [r'\bvishnu\b', r'विष्णु', r'\bviṣṇu\b'],
        'Prajapati/Brahma': [r'\bprajapati\b', r'प्रजापति', r'\bbrahma\b', r'ब्रह्म', r'\bbrahmā\b'],
        'Yama': [r'\byama\b', r'यम'],
        'Surya': [r'\bsurya\b', r'सूर्य', r'\bsūrya\b'],
        'Maruts': [r'\bmarut', r'मरुत'],
        'Ashvins': [r'\bashvin', r'अश्विन', r'\baśvin'],
        'Vayu': [r'\bvayu\b', r'वायु', r'\bvāyu\b'],
        'Mitra': [r'\bmitra\b', r'मित्र'],
        'Ushas': [r'\bushas\b', r'उषस', r'\buṣas\b'],
        'Savitr': [r'\bsavitr', r'सवितृ', r'\bsavitṛ\b'],
        'Pushan': [r'\bpushan\b', r'पूषन', r'\bpūṣan\b'],
        'Brihaspati': [r'\bbrihaspati\b', r'बृहस्पति', r'\bbṛhaspati\b'],
        'Dyaus': [r'\bdyaus\b', r'द्यौस'],
        'Prithivi': [r'\bprithivi\b', r'पृथिवी', r'\bpṛthivī\b'],
        'Aditi': [r'\baditi\b', r'अदिति'],
        'Adityas': [r'\baditya', r'आदित्य'],
    }

    # Load all Vedas
    print("Loading Vedic texts...")

    vedas = {}

    # Rigveda
    try:
        rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')
        vedas['Rigveda'] = get_text_content(rigveda)
        print(f"Rigveda loaded: {len(vedas['Rigveda'])} characters")
    except Exception as e:
        print(f"Error loading Rigveda: {e}")

    # Yajurveda (both Black and White)
    try:
        yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
        yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')
        vedas['Yajurveda (Black)'] = get_text_content(yajur_black)
        vedas['Yajurveda (White)'] = get_text_content(yajur_white)
        vedas['Yajurveda (Combined)'] = vedas['Yajurveda (Black)'] + ' ' + vedas['Yajurveda (White)']
        print(f"Yajurveda Black loaded: {len(vedas['Yajurveda (Black)'])} characters")
        print(f"Yajurveda White loaded: {len(vedas['Yajurveda (White)'])} characters")
        print(f"Yajurveda Combined: {len(vedas['Yajurveda (Combined)'])} characters")
    except Exception as e:
        print(f"Error loading Yajurveda: {e}")

    # Atharvaveda
    try:
        atharvaveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/atharvaveda.json')
        vedas['Atharvaveda'] = get_text_content(atharvaveda)
        print(f"Atharvaveda loaded: {len(vedas['Atharvaveda'])} characters")
    except Exception as e:
        print(f"Error loading Atharvaveda: {e}")

    print("\n" + "="*80)

    # Count deity mentions
    results = {}
    for veda_name, veda_text in vedas.items():
        if veda_text:
            results[veda_name] = count_deity_mentions(veda_text, deity_patterns)
            # Calculate percentages
            text_length = len(veda_text)
            for deity in results[veda_name]:
                count = results[veda_name][deity]
                percentage = (count * 100.0) / (text_length / 1000)  # Per 1000 characters
                results[veda_name][deity] = {
                    'count': count,
                    'percentage': percentage,
                    'per_1000_chars': percentage
                }

    # Output results
    print("\nDEITY MENTIONS ANALYSIS (Normalized by Text Length)")
    print("="*80)

    # Create a comparison table
    all_deities = set()
    for veda_results in results.values():
        all_deities.update(veda_results.keys())

    # Sort deities by total mentions across all texts
    deity_totals = {}
    for deity in all_deities:
        total = sum(results[veda].get(deity, {}).get('count', 0) for veda in results)
        deity_totals[deity] = total

    sorted_deities = sorted(deity_totals.keys(), key=lambda x: deity_totals[x], reverse=True)

    # Print header
    print(f"\n{'Deity':<20} | {'Rigveda':<25} | {'Yajurveda (Combined)':<25} | {'Atharvaveda':<25}")
    print(f"{'':20} | {'Count | Per 1000 chars':<25} | {'Count | Per 1000 chars':<25} | {'Count | Per 1000 chars':<25}")
    print("-"*100)

    # Print deity data
    for deity in sorted_deities[:15]:  # Top 15 deities
        row = f"{deity:<20} |"

        for veda in ['Rigveda', 'Yajurveda (Combined)', 'Atharvaveda']:
            if veda in results and deity in results[veda]:
                count = results[veda][deity]['count']
                per_1000 = results[veda][deity]['per_1000_chars']
                row += f" {count:>5} | {per_1000:>6.2f} per 1000 |"
            else:
                row += f" {'N/A':>5} | {'N/A':>6} per 1000 |"

        print(row)

    # Calculate and print key ratios
    print("\n" + "="*80)
    print("KEY FINDINGS (Using Percentage-Based Analysis)")
    print("="*80)

    if 'Rigveda' in results and 'Yajurveda (Combined)' in results:
        print("\nYajurveda vs Rigveda Ratios (based on per 1000 chars):")
        print("-"*50)

        for deity in ['Rudra/Shiva', 'Indra', 'Agni', 'Prajapati/Brahma', 'Vishnu', 'Soma']:
            if deity in results['Rigveda'] and deity in results['Yajurveda (Combined)']:
                rv_per_1000 = results['Rigveda'][deity]['per_1000_chars']
                yv_per_1000 = results['Yajurveda (Combined)'][deity]['per_1000_chars']

                if rv_per_1000 > 0:
                    ratio = yv_per_1000 / rv_per_1000
                    trend = "📈 INCREASE" if ratio > 1.2 else "📉 DECREASE" if ratio < 0.8 else "≈ STABLE"
                    print(f"{deity:<20}: {ratio:.2f}x ({yv_per_1000:.2f} vs {rv_per_1000:.2f} per 1000) {trend}")

    # Save detailed results to JSON
    output_file = '/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/deity_percentage_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    main()