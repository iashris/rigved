#!/usr/bin/env python3
"""
Deep Deity Analysis: Vishnu, Rudra, and Prajapati/Brahma
Extracting specific mantras and analyzing their contexts
"""

import json
import re
from collections import defaultdict

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_deity_verses(verses, deity_patterns, limit=10):
    """Extract verses mentioning specific deity"""
    results = []
    for verse in verses:
        text = verse.get('text', '').lower()
        meaning = verse.get('meaning', '').lower()

        for pattern in deity_patterns:
            if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, meaning, re.IGNORECASE):
                results.append({
                    'reference': verse.get('reference', ''),
                    'text': verse.get('text', ''),
                    'meaning': verse.get('meaning', ''),
                    'veda': verse.get('vedaId', '')
                })
                break

        if len(results) >= limit:
            break

    return results

def analyze_deity_context(verses, deity_patterns):
    """Analyze the context in which deity appears"""
    contexts = {
        'ritual': 0,
        'cosmogonic': 0,
        'protective': 0,
        'philosophical': 0,
        'material_grant': 0,
        'praise': 0,
        'power': 0,
        'creation': 0
    }

    context_patterns = {
        'ritual': [r'sacrifice', r'offering', r'oblation', r'soma', r'altar', r'priest'],
        'cosmogonic': [r'created', r'born', r'origin', r'first', r'beginning', r'primordial'],
        'protective': [r'protect', r'guard', r'save', r'defend', r'shelter', r'refuge'],
        'philosophical': [r'truth', r'knowledge', r'eternal', r'consciousness', r'absolute', r'brahman'],
        'material_grant': [r'wealth', r'cattle', r'prosperity', r'offspring', r'victory', r'grant'],
        'praise': [r'praise', r'laud', r'worship', r'honor', r'glory', r'mighty'],
        'power': [r'strength', r'power', r'mighty', r'supreme', r'lord', r'ruler'],
        'creation': [r'create', r'make', r'form', r'fashion', r'generate', r'produce']
    }

    for verse in verses:
        text = (verse.get('text', '') + ' ' + verse.get('meaning', '')).lower()

        # Check if deity is mentioned
        deity_mentioned = False
        for pattern in deity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                deity_mentioned = True
                break

        if deity_mentioned:
            # Analyze context
            for context_type, patterns in context_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text):
                        contexts[context_type] += 1
                        break

    return contexts

def main():
    print("="*80)
    print("DEEP DEITY ANALYSIS: Vishnu, Rudra, and Prajapati/Brahma")
    print("="*80)

    # Load all Vedas
    rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')
    atharvaveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/atharvaveda.json')

    # Define deity patterns
    vishnu_patterns = [r'\bvishnu\b', r'\bviṣṇu\b', r'विष्णु', r'वैष्णव']
    rudra_patterns = [r'\brudra\b', r'रुद्र', r'\bshiva\b', r'शिव', r'\bśiva\b']
    prajapati_patterns = [r'\bprajapati\b', r'प्रजापति', r'\bbrahma\b', r'ब्रह्मा', r'\bbrahmā\b']

    print("\n" + "="*80)
    print("1. VISHNU ANALYSIS")
    print("="*80)

    # Extract Vishnu verses from each Veda
    print("\n--- Vishnu in Rigveda ---")
    vishnu_rv = extract_deity_verses(rigveda, vishnu_patterns, limit=5)
    for i, verse in enumerate(vishnu_rv, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Vishnu in Yajurveda (Black) ---")
    vishnu_yv_black = extract_deity_verses(yajur_black, vishnu_patterns, limit=5)
    for i, verse in enumerate(vishnu_yv_black, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Vishnu in Yajurveda (White) ---")
    vishnu_yv_white = extract_deity_verses(yajur_white, vishnu_patterns, limit=5)
    for i, verse in enumerate(vishnu_yv_white, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    # Analyze Vishnu's context
    print("\n--- Vishnu Context Analysis ---")
    vishnu_rv_context = analyze_deity_context(rigveda, vishnu_patterns)
    vishnu_yv_context = analyze_deity_context(yajur_black + yajur_white, vishnu_patterns)

    print("Rigveda context:")
    for context, count in sorted(vishnu_rv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\nYajurveda context:")
    for context, count in sorted(vishnu_yv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\n" + "="*80)
    print("2. RUDRA ANALYSIS")
    print("="*80)

    # Extract Rudra verses
    print("\n--- Rudra in Rigveda ---")
    rudra_rv = extract_deity_verses(rigveda, rudra_patterns, limit=5)
    for i, verse in enumerate(rudra_rv, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Rudra in Yajurveda (Black) ---")
    rudra_yv_black = extract_deity_verses(yajur_black, rudra_patterns, limit=5)
    for i, verse in enumerate(rudra_yv_black, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Rudra in Atharvaveda ---")
    rudra_av = extract_deity_verses(atharvaveda, rudra_patterns, limit=5)
    for i, verse in enumerate(rudra_av, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    # Analyze Rudra's context
    print("\n--- Rudra Context Analysis ---")
    rudra_rv_context = analyze_deity_context(rigveda, rudra_patterns)
    rudra_yv_context = analyze_deity_context(yajur_black + yajur_white, rudra_patterns)
    rudra_av_context = analyze_deity_context(atharvaveda, rudra_patterns)

    print("Rigveda context:")
    for context, count in sorted(rudra_rv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\nYajurveda context:")
    for context, count in sorted(rudra_yv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\nAtharvaveda context:")
    for context, count in sorted(rudra_av_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\n" + "="*80)
    print("3. PRAJAPATI/BRAHMA ANALYSIS")
    print("="*80)

    # Extract Prajapati verses
    print("\n--- Prajapati in Rigveda ---")
    prajapati_rv = extract_deity_verses(rigveda, prajapati_patterns, limit=5)
    for i, verse in enumerate(prajapati_rv, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Prajapati in Yajurveda (Black) ---")
    prajapati_yv_black = extract_deity_verses(yajur_black, prajapati_patterns, limit=7)
    for i, verse in enumerate(prajapati_yv_black, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    print("\n--- Prajapati in Yajurveda (White) ---")
    prajapati_yv_white = extract_deity_verses(yajur_white, prajapati_patterns, limit=7)
    for i, verse in enumerate(prajapati_yv_white, 1):
        print(f"\n{i}. Reference: {verse['reference']}")
        print(f"Text: {verse['text'][:200]}...")

    # Analyze Prajapati's context
    print("\n--- Prajapati Context Analysis ---")
    prajapati_rv_context = analyze_deity_context(rigveda, prajapati_patterns)
    prajapati_yv_context = analyze_deity_context(yajur_black + yajur_white, prajapati_patterns)

    print("Rigveda context:")
    for context, count in sorted(prajapati_rv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    print("\nYajurveda context:")
    for context, count in sorted(prajapati_yv_context.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {context}: {count}")

    # Summary statistics
    print("\n" + "="*80)
    print("4. COMPARATIVE SUMMARY")
    print("="*80)

    # Count total mentions
    def count_deity_mentions(verses, patterns):
        count = 0
        for verse in verses:
            text = (verse.get('text', '') + ' ' + verse.get('meaning', '')).lower()
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    count += 1
                    break
        return count

    print("\n--- Total Mentions ---")
    print("Vishnu:")
    print(f"  Rigveda: {count_deity_mentions(rigveda, vishnu_patterns)}")
    print(f"  Yajurveda: {count_deity_mentions(yajur_black + yajur_white, vishnu_patterns)}")
    print(f"  Atharvaveda: {count_deity_mentions(atharvaveda, vishnu_patterns)}")

    print("\nRudra:")
    print(f"  Rigveda: {count_deity_mentions(rigveda, rudra_patterns)}")
    print(f"  Yajurveda: {count_deity_mentions(yajur_black + yajur_white, rudra_patterns)}")
    print(f"  Atharvaveda: {count_deity_mentions(atharvaveda, rudra_patterns)}")

    print("\nPrajapati:")
    print(f"  Rigveda: {count_deity_mentions(rigveda, prajapati_patterns)}")
    print(f"  Yajurveda: {count_deity_mentions(yajur_black + yajur_white, prajapati_patterns)}")
    print(f"  Atharvaveda: {count_deity_mentions(atharvaveda, prajapati_patterns)}")

    print("\n" + "="*80)
    print("Analysis complete!")

if __name__ == "__main__":
    main()