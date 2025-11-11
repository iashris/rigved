#!/usr/bin/env python3
"""
Detailed verse-by-verse comparison with actual text examples
"""

import json
import re
from difflib import SequenceMatcher

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_for_comparison(text):
    """Clean text for comparison"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[,\.!;:\[\]\(\)]', '', text)
    return text.lower().strip()

def find_exact_parallels(black_data, white_data):
    """Find exact or near-exact parallels"""
    print("\n" + "="*80)
    print("FINDING EXACT PARALLELS")
    print("="*80)

    parallels = []

    # Focus on first 100 verses of each
    for bv in black_data[:100]:
        for wv in white_data[:100]:
            sim = SequenceMatcher(None,
                                clean_for_comparison(bv['text']),
                                clean_for_comparison(wv['text'])).ratio()

            if sim > 0.5:  # 50% similarity
                parallels.append({
                    'black_ref': bv['reference'],
                    'white_ref': wv['reference'],
                    'black_text': bv['text'],
                    'white_text': wv['text'],
                    'similarity': sim
                })

    # Sort by similarity
    parallels.sort(key=lambda x: x['similarity'], reverse=True)

    print(f"\nFound {len(parallels)} parallel passages with >50% similarity\n")

    # Show top 10
    for i, p in enumerate(parallels[:10], 1):
        print(f"\n{'='*80}")
        print(f"PARALLEL #{i} - Similarity: {p['similarity']:.1%}")
        print(f"{'='*80}")
        print(f"\nBlack YV {p['black_ref']}:")
        print(f"{p['black_text'][:400]}")
        if len(p['black_text']) > 400:
            print("...")
        print(f"\nWhite YV {p['white_ref']}:")
        print(f"{p['white_text'][:400]}")
        if len(p['white_text']) > 400:
            print("...")

    return parallels[:15]

def analyze_verbose_vs_concise(black_data, white_data):
    """Find specific examples of verbose vs concise expression"""
    print("\n" + "="*80)
    print("VERBOSE VS CONCISE EXPRESSION EXAMPLES")
    print("="*80)

    # Find verses with similar opening but different lengths
    examples = []

    for bv in black_data[:50]:
        bv_start = clean_for_comparison(bv['text'][:50])
        for wv in white_data[:50]:
            wv_start = clean_for_comparison(wv['text'][:50])

            # Check if they start similarly
            if SequenceMatcher(None, bv_start, wv_start).ratio() > 0.6:
                black_len = len(bv['text'])
                white_len = len(wv['text'])

                # Black should be significantly longer
                if black_len > white_len * 1.5:
                    examples.append({
                        'black_ref': bv['reference'],
                        'white_ref': wv['reference'],
                        'black_text': bv['text'],
                        'white_text': wv['text'],
                        'black_len': black_len,
                        'white_len': white_len,
                        'ratio': black_len / white_len
                    })

    # Sort by length ratio
    examples.sort(key=lambda x: x['ratio'], reverse=True)

    print(f"\nFound {len(examples)} examples where Black YV is significantly more verbose\n")

    for i, ex in enumerate(examples[:5], 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE #{i} - Length Ratio: {ex['ratio']:.1f}x")
        print(f"Black YV: {ex['black_len']} chars | White YV: {ex['white_len']} chars")
        print(f"{'='*80}")
        print(f"\nBlack YV {ex['black_ref']}:")
        print(ex['black_text'])
        print(f"\nWhite YV {ex['white_ref']}:")
        print(ex['white_text'])

    return examples[:10]

def find_instructional_content(black_data):
    """Find verses with embedded instructions/explanations"""
    print("\n" + "="*80)
    print("BLACK YAJURVEDA: EMBEDDED INSTRUCTIONS/BRAHMANA STYLE")
    print("="*80)

    instructional_keywords = [
        'verily', 'thus', 'in that', 'for support', 'he who knows',
        'the gods', 'the asuras', 'the theologians say', 'this is'
    ]

    examples = []

    for verse in black_data:
        text_lower = verse['text'].lower()
        keyword_count = sum(1 for kw in instructional_keywords if kw in text_lower)

        # Look for explanatory style
        if keyword_count >= 2 and len(verse['text']) > 500:
            examples.append({
                'ref': verse['reference'],
                'text': verse['text'],
                'keywords': keyword_count,
                'length': len(verse['text'])
            })

    # Sort by keyword count
    examples.sort(key=lambda x: x['keywords'], reverse=True)

    print(f"\nFound {len(examples)} verses with strong instructional/explanatory content\n")

    for i, ex in enumerate(examples[:5], 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE #{i} - {ex['ref']}")
        print(f"Keywords: {ex['keywords']} | Length: {ex['length']} chars")
        print(f"{'='*80}")
        print(ex['text'][:800])
        if len(ex['text']) > 800:
            print("\n[...continued...]")

    return examples[:10]

def sample_white_yv_chapters(white_data):
    """Sample specific chapters from White YV"""
    print("\n" + "="*80)
    print("WHITE YAJURVEDA: LATER CHAPTERS CONTENT SAMPLES")
    print("="*80)

    chapters = {}
    for verse in white_data:
        ch = verse['mandala']
        if ch not in chapters:
            chapters[ch] = []
        chapters[ch].append(verse)

    # Sample from chapters 19, 25, 30, 35, 40
    target_chapters = [19, 25, 30, 35, 40]

    samples = {}
    for ch in target_chapters:
        if ch in chapters:
            print(f"\n{'='*80}")
            print(f"CHAPTER {ch} - Sample Verses")
            print(f"Total verses in chapter: {len(chapters[ch])}")
            print(f"{'='*80}")

            samples[ch] = []
            # Show first 3 verses
            for verse in chapters[ch][:3]:
                print(f"\n{verse['reference']}:")
                print(verse['text'])
                samples[ch].append(verse)

    return samples

def compare_ritual_terminology(black_data, white_data):
    """Compare ritual terminology and phrasing"""
    print("\n" + "="*80)
    print("RITUAL TERMINOLOGY COMPARISON")
    print("="*80)

    ritual_terms = [
        'sacrifice', 'offering', 'oblation', 'agni', 'soma', 'altar',
        'priest', 'hotr', 'fire', 'ghee', 'veda', 'mantra'
    ]

    print("\nBlack YV - Ritual Term Usage (first 100 verses):")
    black_counts = {term: 0 for term in ritual_terms}
    for verse in black_data[:100]:
        text_lower = verse['text'].lower()
        for term in ritual_terms:
            if term in text_lower:
                black_counts[term] += 1

    for term, count in sorted(black_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {term}: {count}")

    print("\nWhite YV - Ritual Term Usage (first 100 verses):")
    white_counts = {term: 0 for term in ritual_terms}
    for verse in white_data[:100]:
        text_lower = verse['text'].lower()
        for term in ritual_terms:
            if term in text_lower:
                white_counts[term] += 1

    for term, count in sorted(white_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {term}: {count}")

def main():
    print("Loading Yajurveda texts...")
    black_data = load_json('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    white_data = load_json('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')

    print(f"Black YV: {len(black_data)} verses")
    print(f"White YV: {len(white_data)} verses")

    # 1. Find exact parallels
    parallels = find_exact_parallels(black_data, white_data)

    # 2. Verbose vs concise examples
    verbose_examples = analyze_verbose_vs_concise(black_data, white_data)

    # 3. Instructional content in Black YV
    instructional = find_instructional_content(black_data)

    # 4. White YV later chapters
    later_samples = sample_white_yv_chapters(white_data)

    # 5. Ritual terminology
    compare_ritual_terminology(black_data, white_data)

    # Export for report
    output = {
        'parallels': parallels,
        'verbose_examples': verbose_examples,
        'instructional_black': instructional,
        'white_later_chapters': later_samples
    }

    with open('/Users/ashris/Desktop/rigved/rigveda-web/detailed_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("Detailed comparison saved to: detailed_comparison.json")
    print("="*80)

if __name__ == "__main__":
    main()
