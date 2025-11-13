#!/usr/bin/env python3
"""
Fast comparative analysis of Black and White Yajurveda texts.
Optimized for performance with sampling and efficient comparisons.
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import hashlib


def normalize_sanskrit(text):
    """Normalize Sanskrit text for comparison"""
    if not text:
        return ""
    # Remove Vedic accent marks
    text = text.replace('॒', '').replace('॑', '').replace('॓', '').replace('॔', '')
    # Remove extra spaces and normalize
    text = ' '.join(text.split())
    return text


def normalize_english(text):
    """Normalize English text for comparison"""
    if not text:
        return ""
    # Convert to lowercase and remove extra whitespace
    text = ' '.join(text.lower().split())
    # Remove punctuation for comparison
    text = re.sub(r'[.,;:!?\'"()\[\]{}]', '', text)
    return text


def get_text_hash(text):
    """Get hash of text for fast comparison"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]


def analyze_basic_stats(black_verses, white_verses):
    """Get basic statistics about both texts"""
    black_stats = {
        'total_verses': len(black_verses),
        'kandas': set(),
        'with_english': 0,
        'sanskrit_only': 0
    }

    white_stats = {
        'total_verses': len(white_verses),
        'books': set(),
        'with_english': 0,
        'sanskrit_only': 0
    }

    # Analyze Black Yajurveda
    for verse in black_verses:
        black_stats['kandas'].add(verse.get('mandala', 0))
        if verse.get('text') != verse.get('meaning'):
            black_stats['with_english'] += 1
        else:
            black_stats['sanskrit_only'] += 1

    # Analyze White Yajurveda
    for verse in white_verses:
        white_stats['books'].add(verse.get('book', verse.get('mandala', 0)))
        if verse.get('text') != verse.get('meaning'):
            white_stats['with_english'] += 1
        else:
            white_stats['sanskrit_only'] += 1

    return black_stats, white_stats


def find_exact_matches_fast(black_verses, white_verses):
    """Find exact matches using hashing for speed"""
    matches = []

    # Create hash maps for fast lookup
    white_hash_map = defaultdict(list)
    for verse in white_verses:
        sanskrit = normalize_sanskrit(verse.get('meaning', ''))
        if sanskrit:
            text_hash = get_text_hash(sanskrit)
            white_hash_map[text_hash].append(verse)

    # Check Black verses
    for black_verse in black_verses:
        black_sanskrit = normalize_sanskrit(black_verse.get('meaning', ''))
        if black_sanskrit:
            text_hash = get_text_hash(black_sanskrit)
            if text_hash in white_hash_map:
                # Verify actual match (not just hash collision)
                for white_verse in white_hash_map[text_hash]:
                    white_sanskrit = normalize_sanskrit(white_verse.get('meaning', ''))
                    if black_sanskrit == white_sanskrit:
                        matches.append({
                            'black_ref': black_verse.get('reference'),
                            'white_ref': white_verse.get('reference'),
                            'type': 'exact_sanskrit'
                        })

    return matches


def sample_similarity_check(black_verses, white_verses, sample_size=100):
    """Check similarity on a sample to estimate overall similarity"""
    import random

    # Sample verses
    black_sample = random.sample(black_verses, min(sample_size, len(black_verses)))
    white_sample = random.sample(white_verses, min(sample_size, len(white_verses)))

    similarities = []

    for black_verse in black_sample[:20]:  # Further limit for speed
        black_sanskrit = normalize_sanskrit(black_verse.get('meaning', ''))[:200]  # First 200 chars

        for white_verse in white_sample[:20]:
            white_sanskrit = normalize_sanskrit(white_verse.get('meaning', ''))[:200]

            if black_sanskrit and white_sanskrit:
                sim = SequenceMatcher(None, black_sanskrit, white_sanskrit).ratio()
                if sim > 0.5:  # Only track significant similarities
                    similarities.append({
                        'black_ref': black_verse.get('reference'),
                        'white_ref': white_verse.get('reference'),
                        'similarity': round(sim, 3)
                    })

    return similarities


def analyze_first_18_books_fast(black_verses, white_verses):
    """Quickly analyze the claim about first 18 books"""
    # Group verses
    black_by_kanda = defaultdict(list)
    white_by_book = defaultdict(list)

    for verse in black_verses:
        kanda = verse.get('mandala', 0)
        black_by_kanda[kanda].append(verse)

    for verse in white_verses:
        book = verse.get('book', verse.get('mandala', 0))
        white_by_book[book].append(verse)

    results = {}

    # Check first 18 books
    for book in range(1, 19):
        if book in white_by_book:
            book_verses = white_by_book[book]

            # Create hash set of first 50 verses from this book
            book_hashes = set()
            for verse in book_verses[:50]:
                sanskrit = normalize_sanskrit(verse.get('meaning', ''))[:100]
                if sanskrit:
                    book_hashes.add(get_text_hash(sanskrit))

            # Check against each Kanda
            matches = defaultdict(int)
            for kanda in black_by_kanda:
                for verse in black_by_kanda[kanda][:50]:  # Sample
                    sanskrit = normalize_sanskrit(verse.get('meaning', ''))[:100]
                    if sanskrit and get_text_hash(sanskrit) in book_hashes:
                        matches[kanda] += 1

            results[book] = {
                'total_verses': len(book_verses),
                'matches_with_kandas': dict(matches),
                'has_matches': len(matches) > 0
            }

    return results


def get_common_phrases(black_verses, white_verses, min_length=10):
    """Find common phrases between texts"""
    # Extract phrases from sample
    black_phrases = Counter()
    white_phrases = Counter()

    # Sample for speed
    for verse in black_verses[:200]:
        text = normalize_sanskrit(verse.get('meaning', ''))
        # Extract phrases of min_length words
        words = text.split()
        for i in range(len(words) - min_length + 1):
            phrase = ' '.join(words[i:i + min_length])
            if len(phrase) > 50:  # Meaningful phrase
                black_phrases[phrase] += 1

    for verse in white_verses[:200]:
        text = normalize_sanskrit(verse.get('meaning', ''))
        words = text.split()
        for i in range(len(words) - min_length + 1):
            phrase = ' '.join(words[i:i + min_length])
            if len(phrase) > 50:
                white_phrases[phrase] += 1

    # Find common phrases
    common = []
    for phrase in black_phrases:
        if phrase in white_phrases:
            common.append({
                'phrase': phrase[:100] + '...' if len(phrase) > 100 else phrase,
                'black_count': black_phrases[phrase],
                'white_count': white_phrases[phrase]
            })

    return sorted(common, key=lambda x: x['black_count'] + x['white_count'], reverse=True)[:20]


def main():
    # Load data
    print("Loading Yajurveda texts...")
    with open('public/yajurveda_black.json', 'r', encoding='utf-8') as f:
        black_verses = json.load(f)

    with open('public/yajurveda_white.json', 'r', encoding='utf-8') as f:
        white_verses = json.load(f)

    print(f"Loaded {len(black_verses)} Black Yajurveda verses")
    print(f"Loaded {len(white_verses)} White Yajurveda verses")

    # Get basic statistics
    print("\nAnalyzing basic statistics...")
    black_stats, white_stats = analyze_basic_stats(black_verses, white_verses)

    print(f"\nBlack Yajurveda:")
    print(f"  Total verses: {black_stats['total_verses']}")
    print(f"  Kandas: {sorted(black_stats['kandas'])}")
    print(f"  With English: {black_stats['with_english']} ({black_stats['with_english']*100/black_stats['total_verses']:.1f}%)")

    print(f"\nWhite Yajurveda:")
    print(f"  Total verses: {white_stats['total_verses']}")
    print(f"  Books: {len(white_stats['books'])} books")
    print(f"  With English: {white_stats['with_english']} ({white_stats['with_english']*100/white_stats['total_verses']:.1f}%)")

    # Find exact matches
    print("\n=== FINDING EXACT MATCHES ===")
    exact_matches = find_exact_matches_fast(black_verses, white_verses)
    print(f"Found {len(exact_matches)} exact Sanskrit matches")

    # Sample similarity check
    print("\n=== SAMPLING SIMILARITY ===")
    similarities = sample_similarity_check(black_verses, white_verses, sample_size=100)
    print(f"Found {len(similarities)} similar pairs in sample")

    if similarities:
        avg_sim = sum(s['similarity'] for s in similarities) / len(similarities)
        print(f"Average similarity in sample: {avg_sim:.2%}")

    # Analyze first 18 books claim
    print("\n=== FIRST 18 BOOKS ANALYSIS ===")
    first_18 = analyze_first_18_books_fast(black_verses, white_verses)

    books_with_matches = sum(1 for b in first_18.values() if b['has_matches'])
    print(f"Books 1-18 with matches to Black: {books_with_matches}/18")

    for book, data in list(first_18.items())[:5]:  # Show first 5
        if data['matches_with_kandas']:
            print(f"  Book {book}: {data['total_verses']} verses, matches with Kandas: {data['matches_with_kandas']}")

    # Find common phrases
    print("\n=== COMMON PHRASES ===")
    common_phrases = get_common_phrases(black_verses, white_verses, min_length=5)
    print(f"Found {len(common_phrases)} common phrases")

    if common_phrases:
        print("\nTop 5 common phrases:")
        for i, phrase_data in enumerate(common_phrases[:5], 1):
            print(f"  {i}. Found {phrase_data['black_count']} times in Black, {phrase_data['white_count']} times in White")
            print(f"     '{phrase_data['phrase']}'")

    # Create analysis directory and save results
    analysis_dir = Path('yajurveda_analysis')
    analysis_dir.mkdir(exist_ok=True)

    # Prepare results
    results = {
        'summary': {
            'black_verses': black_stats['total_verses'],
            'white_verses': white_stats['total_verses'],
            'black_kandas': sorted(list(black_stats['kandas'])),
            'white_books': len(white_stats['books']),
            'exact_matches': len(exact_matches),
            'sample_similarities': len(similarities),
            'books_1_18_with_matches': books_with_matches,
            'common_phrases_found': len(common_phrases)
        },
        'black_stats': {
            'total_verses': black_stats['total_verses'],
            'kandas': sorted(list(black_stats['kandas'])),
            'with_english': black_stats['with_english'],
            'sanskrit_only': black_stats['sanskrit_only']
        },
        'white_stats': {
            'total_verses': white_stats['total_verses'],
            'books': sorted(list(white_stats['books'])),
            'with_english': white_stats['with_english'],
            'sanskrit_only': white_stats['sanskrit_only']
        },
        'exact_matches_sample': exact_matches[:50],  # First 50
        'similarities_sample': similarities[:50],  # First 50
        'first_18_books': first_18,
        'common_phrases': common_phrases
    }

    # Save JSON results
    with open(analysis_dir / 'fast_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Analysis complete! Results saved to {analysis_dir}/")

    return results


if __name__ == '__main__':
    results = main()