#!/usr/bin/env python3
"""
Comprehensive comparative analysis of Black and White Yajurveda
"""

import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_structure(data, name):
    """Analyze the structural organization of a Yajurveda text"""
    books = defaultdict(lambda: defaultdict(list))

    for verse in data:
        ref = verse['reference']
        parts = ref.split('.')
        book = int(parts[0])
        hymn = int(parts[1]) if len(parts) > 1 else 1
        verse_num = int(parts[2]) if len(parts) > 2 else 1
        books[book][hymn].append(verse)

    print(f"\n{'='*80}")
    print(f"STRUCTURAL ANALYSIS: {name}")
    print(f"{'='*80}")
    print(f"Total verses: {len(data)}")
    print(f"Total books/chapters: {len(books)}")

    for book_num in sorted(books.keys())[:5]:  # First 5 books
        hymns = books[book_num]
        total_verses = sum(len(verses) for verses in hymns.values())
        print(f"  Book {book_num}: {len(hymns)} hymns/sections, {total_verses} verses")

    if len(books) > 5:
        print(f"  ... (showing first 5 books)")

    return books

def clean_text(text):
    """Clean text for comparison"""
    # Remove extra whitespace, newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation for loose comparison
    text = re.sub(r'[,\.!;:]', '', text)
    return text.lower().strip()

def get_similarity(text1, text2):
    """Calculate similarity ratio between two texts"""
    return SequenceMatcher(None, clean_text(text1), clean_text(text2)).ratio()

def find_parallel_mantras(black_books, white_books):
    """Find parallel mantras between Black and White YV"""
    print(f"\n{'='*80}")
    print(f"CONTENT OVERLAP ANALYSIS (Books 1-3)")
    print(f"{'='*80}")

    parallels = []

    # Compare first 3 books
    for book_num in range(1, 4):
        if book_num in black_books and book_num in white_books:
            print(f"\n--- Book/Chapter {book_num} ---")

            black_verses = []
            for hymn_verses in black_books[book_num].values():
                black_verses.extend(hymn_verses)

            white_verses = []
            for hymn_verses in white_books[book_num].values():
                white_verses.extend(hymn_verses)

            print(f"Black YV: {len(black_verses)} verses")
            print(f"White YV: {len(white_verses)} verses")

            # Find similar verses
            matches = []
            for bv in black_verses[:20]:  # Sample first 20 verses
                for wv in white_verses[:20]:
                    similarity = get_similarity(bv['text'], wv['text'])
                    if similarity > 0.4:  # 40% similarity threshold
                        matches.append({
                            'black_ref': bv['reference'],
                            'white_ref': wv['reference'],
                            'black_text': bv['text'],
                            'white_text': wv['text'],
                            'similarity': similarity
                        })

            # Sort by similarity
            matches.sort(key=lambda x: x['similarity'], reverse=True)

            if matches:
                print(f"\nFound {len(matches)} potential parallels in Book {book_num}")
                for i, match in enumerate(matches[:3], 1):  # Show top 3
                    print(f"\n  Match {i} (Similarity: {match['similarity']:.2%}):")
                    print(f"    Black YV {match['black_ref']}")
                    print(f"    White YV {match['white_ref']}")
                    parallels.append(match)

    return parallels

def analyze_language_features(black_books, white_books):
    """Analyze language and expression differences"""
    print(f"\n{'='*80}")
    print(f"LANGUAGE & EXPRESSION DIFFERENCES")
    print(f"{'='*80}")

    # Keywords indicating instructional/explanatory content
    instruction_keywords = [
        'thou art', 'let', 'may', 'i place', 'i grasp', 'i sprinkle',
        'guard', 'protect', 'for thee', 'be thou', 'do thou'
    ]

    black_examples = []
    white_examples = []

    # Sample from Book 1
    if 1 in black_books:
        for hymn_verses in black_books[1].values():
            for verse in hymn_verses[:30]:  # First 30 verses
                text_lower = verse['text'].lower()
                instruction_count = sum(1 for kw in instruction_keywords if kw in text_lower)
                if instruction_count >= 3:
                    black_examples.append({
                        'ref': verse['reference'],
                        'text': verse['text'],
                        'instruction_count': instruction_count,
                        'length': len(verse['text'])
                    })

    if 1 in white_books:
        for hymn_verses in white_books[1].values():
            for verse in hymn_verses[:30]:  # First 30 verses
                text_lower = verse['text'].lower()
                instruction_count = sum(1 for kw in instruction_keywords if kw in text_lower)
                if instruction_count >= 2:
                    white_examples.append({
                        'ref': verse['reference'],
                        'text': verse['text'],
                        'instruction_count': instruction_count,
                        'length': len(verse['text'])
                    })

    # Sort by length (longer = more verbose)
    black_examples.sort(key=lambda x: x['length'], reverse=True)
    white_examples.sort(key=lambda x: x['length'], reverse=True)

    print(f"\nBlack YV - Average verse length: {sum(e['length'] for e in black_examples[:20])/min(20, len(black_examples)):.0f} chars")
    print(f"White YV - Average verse length: {sum(e['length'] for e in white_examples[:20])/min(20, len(white_examples)):.0f} chars")

    return black_examples[:10], white_examples[:10]

def sample_later_chapters(white_books):
    """Sample content from later chapters of White YV"""
    print(f"\n{'='*80}")
    print(f"NOVEL CONTENT IN WHITE YV (Chapters 19-40)")
    print(f"{'='*80}")

    samples = []

    for chapter in [19, 20, 25, 30, 35, 40]:
        if chapter in white_books:
            print(f"\n--- Chapter {chapter} ---")
            hymns = white_books[chapter]
            total_verses = sum(len(verses) for verses in hymns.values())
            print(f"  Total verses: {total_verses}")

            # Get first few verses as sample
            for hymn_num in sorted(hymns.keys())[:2]:
                for verse in hymns[hymn_num][:2]:
                    print(f"  Sample verse {verse['reference']}:")
                    print(f"    {verse['text'][:200]}...")
                    samples.append(verse)

    return samples

def analyze_ritual_instructions(black_books, white_books):
    """Analyze ritual instructions and explanations"""
    print(f"\n{'='*80}")
    print(f"RITUAL INSTRUCTIONS ANALYSIS")
    print(f"{'='*80}")

    # Look for verses with ritual instructions
    ritual_keywords = ['sacrifice', 'offering', 'oblation', 'altar', 'fire', 'priest', 'soma']

    black_ritual = []
    white_ritual = []

    for book_num in range(1, 3):
        if book_num in black_books:
            for hymn_verses in black_books[book_num].values():
                for verse in hymn_verses:
                    text_lower = verse['text'].lower()
                    if any(kw in text_lower for kw in ritual_keywords):
                        if len(verse['text']) > 300:  # Longer verses likely have more explanation
                            black_ritual.append(verse)

        if book_num in white_books:
            for hymn_verses in white_books[book_num].values():
                for verse in hymn_verses:
                    text_lower = verse['text'].lower()
                    if any(kw in text_lower for kw in ritual_keywords):
                        white_ritual.append(verse)

    print(f"\nBlack YV verses with ritual content: {len(black_ritual)}")
    print(f"White YV verses with ritual content: {len(white_ritual)}")

    # Show examples
    print("\nBlack YV Ritual Examples (verbose with explanations):")
    for verse in black_ritual[:3]:
        print(f"\n  {verse['reference']}:")
        print(f"    {verse['text'][:300]}...")

    print("\nWhite YV Ritual Examples (concise):")
    for verse in white_ritual[:3]:
        print(f"\n  {verse['reference']}:")
        print(f"    {verse['text'][:200]}...")

    return black_ritual[:5], white_ritual[:5]

def main():
    print("Loading data...")
    black_data = load_json('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    white_data = load_json('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')

    # 1. Structural Analysis
    black_books = analyze_structure(black_data, "Black Yajurveda (Taittiriya Samhita)")
    white_books = analyze_structure(white_data, "White Yajurveda (Vajasaneyi Samhita)")

    # 2. Content Overlap
    parallels = find_parallel_mantras(black_books, white_books)

    # 3. Language Features
    black_verbose, white_concise = analyze_language_features(black_books, white_books)

    # 4. Novel Content in White YV
    later_samples = sample_later_chapters(white_books)

    # 5. Ritual Instructions
    black_ritual, white_ritual = analyze_ritual_instructions(black_books, white_books)

    # Export detailed examples for report
    print(f"\n{'='*80}")
    print("GENERATING DETAILED EXAMPLES FOR REPORT")
    print(f"{'='*80}")

    examples = {
        'parallels': parallels[:10],
        'black_verbose': black_verbose,
        'white_concise': white_concise,
        'later_chapters': later_samples,
        'black_ritual': [{'ref': v['reference'], 'text': v['text']} for v in black_ritual],
        'white_ritual': [{'ref': v['reference'], 'text': v['text']} for v in white_ritual]
    }

    with open('/Users/ashris/Desktop/rigved/rigveda-web/yv_analysis_examples.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print("\nDetailed examples saved to: yv_analysis_examples.json")

if __name__ == "__main__":
    main()
