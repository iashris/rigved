#!/usr/bin/env python3
"""
Comprehensive comparison and analysis of Black and White Yajurveda texts.
This script performs deep textual analysis to find similarities, differences,
and patterns between the two versions.
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import unicodedata


def normalize_sanskrit(text):
    """Normalize Sanskrit text for comparison by removing accent marks"""
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


def calculate_similarity(text1, text2, normalize_func=None):
    """Calculate similarity ratio between two texts"""
    if normalize_func:
        text1 = normalize_func(text1)
        text2 = normalize_func(text2)

    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(None, text1, text2).ratio()


def extract_words(text, is_sanskrit=False):
    """Extract individual words from text for frequency analysis"""
    if not text:
        return []

    if is_sanskrit:
        # Split on spaces and common Sanskrit delimiters
        words = re.findall(r'[^\s॥।]+', text)
    else:
        # Split English text on word boundaries
        words = re.findall(r'\b\w+\b', text.lower())

    return [w for w in words if len(w) > 1]


def analyze_structure(verses):
    """Analyze the structural organization of verses"""
    structure = defaultdict(lambda: defaultdict(set))

    for verse in verses:
        mandala = verse.get('mandala', verse.get('book', 0))
        hymn = verse.get('hymn', verse.get('chapter', 0))
        verse_num = verse.get('verse', 0)

        structure[mandala]['hymns'].add(hymn)
        structure[mandala]['verses'].add((hymn, verse_num))

    return structure


def find_exact_matches(black_verses, white_verses):
    """Find verses with exact or near-exact matches in Sanskrit"""
    matches = []

    # Create normalized lookup for White verses
    white_sanskrit_map = {}
    for verse in white_verses:
        normalized = normalize_sanskrit(verse.get('meaning', ''))
        if normalized:
            if normalized not in white_sanskrit_map:
                white_sanskrit_map[normalized] = []
            white_sanskrit_map[normalized].append(verse)

    # Check each Black verse against White
    for black_verse in black_verses:
        black_sanskrit = normalize_sanskrit(black_verse.get('meaning', ''))
        if black_sanskrit in white_sanskrit_map:
            for white_verse in white_sanskrit_map[black_sanskrit]:
                matches.append({
                    'black_ref': black_verse.get('reference'),
                    'white_ref': white_verse.get('reference'),
                    'similarity': 1.0,
                    'type': 'exact'
                })

    return matches


def find_similar_verses(black_verses, white_verses, threshold=0.7):
    """Find verses with high similarity but not exact matches"""
    similar = []

    # Sample for performance - compare first 100 from each Kanda/Book
    black_sample = {}
    white_sample = {}

    # Group Black verses by Kanda
    for verse in black_verses:
        kanda = verse.get('mandala', 0)
        if kanda not in black_sample:
            black_sample[kanda] = []
        if len(black_sample[kanda]) < 50:
            black_sample[kanda].append(verse)

    # Group White verses by Book
    for verse in white_verses:
        book = verse.get('book', verse.get('mandala', 0))
        if book not in white_sample:
            white_sample[book] = []
        if len(white_sample[book]) < 50:
            white_sample[book].append(verse)

    # Compare samples
    for kanda, black_list in black_sample.items():
        # Focus on books that might correspond (first 18 books claim)
        for book in range(1, min(19, max(white_sample.keys()) + 1)):
            if book in white_sample:
                for black_verse in black_list:
                    black_sanskrit = normalize_sanskrit(black_verse.get('meaning', ''))
                    black_english = normalize_english(black_verse.get('text', ''))

                    for white_verse in white_sample[book]:
                        white_sanskrit = normalize_sanskrit(white_verse.get('meaning', ''))
                        white_english = normalize_english(white_verse.get('text', ''))

                        # Calculate similarities
                        sanskrit_sim = calculate_similarity(black_sanskrit, white_sanskrit)
                        english_sim = calculate_similarity(black_english, white_english)

                        if sanskrit_sim >= threshold or english_sim >= threshold:
                            similar.append({
                                'black_ref': black_verse.get('reference'),
                                'white_ref': white_verse.get('reference'),
                                'sanskrit_similarity': round(sanskrit_sim, 3),
                                'english_similarity': round(english_sim, 3),
                                'black_kanda': kanda,
                                'white_book': book
                            })

    return similar


def analyze_vocabulary(verses, text_field='meaning'):
    """Analyze vocabulary frequency and unique words"""
    word_freq = Counter()
    total_words = 0

    for verse in verses:
        text = verse.get(text_field, '')
        words = extract_words(text, is_sanskrit=(text_field == 'meaning'))
        word_freq.update(words)
        total_words += len(words)

    return {
        'total_words': total_words,
        'unique_words': len(word_freq),
        'top_words': word_freq.most_common(50),
        'word_frequency': word_freq
    }


def compare_first_18_books(black_verses, white_verses):
    """Specifically analyze the claim about first 18 books of White matching Black"""
    # Group verses by book/kanda
    black_by_kanda = defaultdict(list)
    white_by_book = defaultdict(list)

    for verse in black_verses:
        kanda = verse.get('mandala', 0)
        black_by_kanda[kanda].append(verse)

    for verse in white_verses:
        book = verse.get('book', verse.get('mandala', 0))
        white_by_book[book].append(verse)

    comparison = {}

    # Compare first 18 books of White with all Black Kandas
    for book in range(1, 19):
        if book in white_by_book:
            book_data = {
                'white_verses': len(white_by_book[book]),
                'matches_with_black': defaultdict(int),
                'similarity_scores': []
            }

            # Sample comparison with each Kanda
            for kanda in black_by_kanda:
                # Compare first 10 verses from each for efficiency
                sample_size = min(10, len(white_by_book[book]), len(black_by_kanda[kanda]))

                for i in range(sample_size):
                    white_verse = white_by_book[book][i]
                    black_verse = black_by_kanda[kanda][i % len(black_by_kanda[kanda])]

                    sanskrit_sim = calculate_similarity(
                        normalize_sanskrit(white_verse.get('meaning', '')),
                        normalize_sanskrit(black_verse.get('meaning', ''))
                    )

                    if sanskrit_sim > 0.5:
                        book_data['matches_with_black'][f'Kanda_{kanda}'] += 1
                        book_data['similarity_scores'].append(sanskrit_sim)

            if book_data['similarity_scores']:
                book_data['avg_similarity'] = sum(book_data['similarity_scores']) / len(book_data['similarity_scores'])
            else:
                book_data['avg_similarity'] = 0

            comparison[f'Book_{book}'] = book_data

    return comparison


def main():
    # Load data
    black_file = Path('public/yajurveda_black.json')
    white_file = Path('public/yajurveda_white.json')

    print("Loading Yajurveda texts...")
    with open(black_file, 'r', encoding='utf-8') as f:
        black_verses = json.load(f)

    with open(white_file, 'r', encoding='utf-8') as f:
        white_verses = json.load(f)

    print(f"Loaded {len(black_verses)} Black Yajurveda verses")
    print(f"Loaded {len(white_verses)} White Yajurveda verses")

    # Basic statistics
    print("\n=== BASIC STATISTICS ===")

    # Structure analysis
    black_structure = analyze_structure(black_verses)
    white_structure = analyze_structure(white_verses)

    print(f"\nBlack Yajurveda Structure:")
    for kanda in sorted(black_structure.keys()):
        print(f"  Kanda {kanda}: {len(black_structure[kanda]['hymns'])} Prapathakas, "
              f"{len(black_structure[kanda]['verses'])} verses")

    print(f"\nWhite Yajurveda Structure:")
    books_count = len(white_structure)
    total_white_verses = sum(len(data['verses']) for data in white_structure.values())
    print(f"  Total: {books_count} Books/Adhyayas, {total_white_verses} verses")

    # Find exact matches
    print("\n=== FINDING EXACT MATCHES ===")
    exact_matches = find_exact_matches(black_verses, white_verses)
    print(f"Found {len(exact_matches)} exact Sanskrit matches")

    # Find similar verses
    print("\n=== FINDING SIMILAR VERSES ===")
    similar_verses = find_similar_verses(black_verses, white_verses, threshold=0.6)
    print(f"Found {len(similar_verses)} similar verses (>60% similarity)")

    # Analyze first 18 books claim
    print("\n=== ANALYZING FIRST 18 BOOKS CLAIM ===")
    first_18_analysis = compare_first_18_books(black_verses, white_verses)

    # Vocabulary analysis
    print("\n=== VOCABULARY ANALYSIS ===")
    black_vocab = analyze_vocabulary(black_verses, 'meaning')
    white_vocab = analyze_vocabulary(white_verses, 'meaning')

    print(f"Black Yajurveda: {black_vocab['unique_words']:,} unique words")
    print(f"White Yajurveda: {white_vocab['unique_words']:,} unique words")

    # Find common vocabulary
    black_words = set(w for w, _ in black_vocab['top_words'])
    white_words = set(w for w, _ in white_vocab['top_words'])
    common_words = black_words & white_words
    print(f"Common top words: {len(common_words)}")

    # Save detailed analysis
    analysis_dir = Path('yajurveda_analysis')
    analysis_dir.mkdir(exist_ok=True)

    # Save results
    results = {
        'statistics': {
            'black_verses': len(black_verses),
            'white_verses': len(white_verses),
            'exact_matches': len(exact_matches),
            'similar_verses': len(similar_verses),
            'black_unique_words': black_vocab['unique_words'],
            'white_unique_words': white_vocab['unique_words']
        },
        'exact_matches': exact_matches[:100],  # First 100 for review
        'similar_verses': similar_verses[:200],  # First 200 for review
        'first_18_books_analysis': first_18_analysis,
        'black_structure': {str(k): {'prapathakas': len(v['hymns']),
                                     'verses': len(v['verses'])}
                           for k, v in black_structure.items()},
        'vocabulary': {
            'black_top_words': black_vocab['top_words'][:30],
            'white_top_words': white_vocab['top_words'][:30],
            'common_top_words': list(common_words)[:30]
        }
    }

    with open(analysis_dir / 'comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nAnalysis complete! Results saved to {analysis_dir}/")

    return results


if __name__ == '__main__':
    results = main()