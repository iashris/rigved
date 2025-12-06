#!/usr/bin/env python3
"""
Deep Analysis of Yajurveda: Paradoxes, Philosophy, and Problems
Examining both Black and White versions for their relationship to modern Hinduism
"""

import json
import re
from collections import defaultdict

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_themes(text, patterns):
    """Search for thematic patterns in text"""
    results = []
    for pattern, theme in patterns:
        matches = re.findall(pattern, text.lower(), re.IGNORECASE)
        if matches:
            results.append((theme, len(matches), matches[:3]))  # Store first 3 examples
    return results

def extract_relevant_verses(verses, keywords):
    """Extract verses containing specific keywords"""
    relevant = []
    for verse in verses:
        text = verse.get('text', '').lower()
        meaning = verse.get('meaning', '').lower()
        for keyword in keywords:
            if keyword in text or keyword in meaning:
                relevant.append({
                    'reference': verse.get('reference', ''),
                    'text': verse.get('text', ''),
                    'keyword': keyword
                })
                break
    return relevant

def main():
    print("="*80)
    print("YAJURVEDA DEEP ANALYSIS: Paradoxes, Philosophy, and Problems")
    print("="*80)

    # Load both Yajurveda versions
    yajur_black = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_black.json')
    yajur_white = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/yajurveda_white.json')

    # Combine texts for analysis
    all_text_black = ""
    all_text_white = ""

    for verse in yajur_black:
        all_text_black += verse.get('text', '') + " " + verse.get('meaning', '') + " "

    for verse in yajur_white:
        all_text_white += verse.get('text', '') + " " + verse.get('meaning', '') + " "

    # 1. PHILOSOPHICAL PARADOXES
    print("\n1. PHILOSOPHICAL PARADOXES")
    print("-"*40)

    philosophical_patterns = [
        (r'no form|no image|formless|pratima', 'Formlessness/Abstract'),
        (r'one without a second|ekam sat|one truth', 'Monism'),
        (r'neti neti|not this', 'Negative theology'),
        (r'tat tvam asi|thou art that', 'Identity philosophy'),
        (r'brahman|absolute', 'Brahman concept'),
        (r'atman|self|soul', 'Atman/Soul concept'),
        (r'maya|illusion', 'Maya concept'),
        (r'karma|action|deed', 'Karma doctrine'),
        (r'rebirth|reborn|transmigration', 'Rebirth concept'),
        (r'moksha|liberation|freedom', 'Liberation concept')
    ]

    print("\nBlack Yajurveda Philosophical Elements:")
    black_phil = search_themes(all_text_black, philosophical_patterns)
    for theme, count, examples in black_phil:
        print(f"  {theme}: {count} references")

    print("\nWhite Yajurveda Philosophical Elements:")
    white_phil = search_themes(all_text_white, philosophical_patterns)
    for theme, count, examples in white_phil:
        print(f"  {theme}: {count} references")

    # 2. DESIRE AND COMPETITION VS PHILOSOPHY
    print("\n2. DESIRE/COMPETITION VS PHILOSOPHICAL DETACHMENT")
    print("-"*40)

    material_patterns = [
        (r'wealth|riches|prosperity|gold', 'Material wealth'),
        (r'cattle|cows|horses|livestock', 'Animal wealth'),
        (r'victory|conquer|defeat enemy', 'Competition/Victory'),
        (r'desire|wish|want|seek', 'Desires'),
        (r'offspring|sons|children', 'Progeny desires'),
        (r'power|strength|might', 'Power seeking'),
        (r'kingdom|rule|sovereignty', 'Political power'),
        (r'fame|glory|renown', 'Social status')
    ]

    print("\nMaterial/Competitive Elements in Black YV:")
    black_mat = search_themes(all_text_black, material_patterns)
    for theme, count, _ in black_mat:
        print(f"  {theme}: {count} references")

    # 3. PROBLEMATIC RITUALS
    print("\n3. PROBLEMATIC RITUALS AND PRACTICES")
    print("-"*40)

    problematic_patterns = [
        (r'ashvamedha|horse sacrifice', 'Ashvamedha (Horse sacrifice)'),
        (r'purushamedha|human sacrifice|man sacrifice', 'Purushamedha (Human sacrifice)'),
        (r'gomedha|cow sacrifice|bull sacrifice', 'Gomedha (Cattle sacrifice)'),
        (r'animal sacrifice|victim|pashu', 'Animal sacrifice general'),
        (r'blood|slaughter|kill', 'Violence in rituals'),
        (r'soma drink|intoxicat', 'Intoxicants'),
        (r'enemy|foe|rival', 'Cursing enemies'),
        (r'death to|destroy|perish', 'Death wishes')
    ]

    print("\nProblematic Rituals in Black YV:")
    black_prob = search_themes(all_text_black, problematic_patterns)
    for theme, count, _ in black_prob:
        print(f"  {theme}: {count} references")

    print("\nProblematic Rituals in White YV:")
    white_prob = search_themes(all_text_white, problematic_patterns)
    for theme, count, _ in white_prob:
        print(f"  {theme}: {count} references")

    # 4. CASTE AND SOCIAL HIERARCHY
    print("\n4. CASTE AND SOCIAL HIERARCHY SOLIDIFICATION")
    print("-"*40)

    caste_patterns = [
        (r'brahman[a]?\s|brahmin|priest class', 'Brahmin references'),
        (r'kshatriya|warrior|ruler class', 'Kshatriya references'),
        (r'vaishya|merchant|trader', 'Vaishya references'),
        (r'shudra|sudra|servant', 'Shudra references'),
        (r'varna|class|caste', 'Varna system'),
        (r'twice-born|dvija', 'Twice-born concept'),
        (r'untouchable|outcaste|chandala', 'Outcaste references'),
        (r'birth\s+determines|born\s+into', 'Birth-based status'),
        (r'serve the|servants of|subordinate', 'Servitude concepts')
    ]

    print("\nCaste References in Black YV:")
    black_caste = search_themes(all_text_black, caste_patterns)
    for theme, count, _ in black_caste:
        print(f"  {theme}: {count} references")

    print("\nCaste References in White YV:")
    white_caste = search_themes(all_text_white, caste_patterns)
    for theme, count, _ in white_caste:
        print(f"  {theme}: {count} references")

    # 5. WOMEN AND GENDER
    print("\n5. TREATMENT OF WOMEN AND GENDER")
    print("-"*40)

    gender_patterns = [
        (r'wife|wives|woman|women', 'Women references'),
        (r'obedient wife|devoted wife', 'Wife subordination'),
        (r'son\s+not\s+daughter|male\s+offspring', 'Son preference'),
        (r'widow|sati|husband.*death', 'Widow references'),
        (r'menstruat|impure woman|pollut.*woman', 'Ritual impurity'),
        (r'property.*husband|belong.*husband', 'Women as property'),
        (r'goddess|devi|shakti', 'Divine feminine')
    ]

    print("\nGender References in Black YV:")
    black_gender = search_themes(all_text_black, gender_patterns)
    for theme, count, _ in black_gender:
        print(f"  {theme}: {count} references")

    # 6. SEARCH FOR SPECIFIC VERSES
    print("\n6. KEY PHILOSOPHICAL VERSES")
    print("-"*40)

    # Search for Isha Upanishad opening
    isha_search = extract_relevant_verses(yajur_white,
        ['purnam', 'ishavasyam', 'jagat', 'tyakten', 'bhunjitha'])

    if isha_search:
        print("\nIsha Upanishad elements found in White YV:")
        for verse in isha_search[:3]:
            print(f"  Ref: {verse['reference']}")
            print(f"  Text: {verse['text'][:100]}...")

    # Search for "no form" concept
    formless_search = extract_relevant_verses(yajur_white + yajur_black,
        ['pratima', 'form', 'image', 'formless', 'nirakara'])

    if formless_search:
        print("\nFormlessness concepts found:")
        for verse in formless_search[:3]:
            print(f"  Ref: {verse['reference']}")
            print(f"  Keyword: {verse['keyword']}")

    # 7. COMPARISON WITH MODERN HINDUISM
    print("\n7. DISTANCE FROM MODERN HINDUISM")
    print("-"*40)

    modern_hindu_concepts = [
        (r'krishna|rama|vishnu avatar', 'Puranic deities'),
        (r'ganesha|ganesh|vinayak', 'Ganesha'),
        (r'durga|kali|parvati', 'Goddess worship'),
        (r'shiva.*linga|lingam', 'Shiva linga'),
        (r'bhakti|devotion|surrender', 'Bhakti concept'),
        (r'temple|mandir|murti', 'Temple worship'),
        (r'pilgrimage|tirtha|yatra', 'Pilgrimage'),
        (r'guru\s+worship|guru\s+devotion', 'Guru tradition'),
        (r'yoga.*meditation|dhyana', 'Yoga/Meditation'),
        (r'vegetarian|ahimsa|non.*violence', 'Non-violence')
    ]

    print("\nModern Hindu concepts in Yajurveda:")
    combined_text = all_text_black + all_text_white
    modern_concepts = search_themes(combined_text, modern_hindu_concepts)
    for theme, count, _ in modern_concepts:
        print(f"  {theme}: {count} references")

    # 8. EVOLUTION ANALYSIS
    print("\n8. PHILOSOPHICAL EVOLUTION: DESIRE TO KARMA")
    print("-"*40)

    # Track evolution of concepts
    evolution_tracking = {
        'Material desires': len(re.findall(r'wealth|cattle|victory|power', combined_text.lower())),
        'Ritual emphasis': len(re.findall(r'sacrifice|offering|ritual|ceremony', combined_text.lower())),
        'Karma mentions': len(re.findall(r'karma|deed|action.*result', combined_text.lower())),
        'Philosophical abstraction': len(re.findall(r'brahman|atman|absolute|consciousness', combined_text.lower())),
        'Ethical concepts': len(re.findall(r'dharma|righteous|duty|moral', combined_text.lower()))
    }

    print("\nConceptual Balance in Yajurveda:")
    for concept, count in evolution_tracking.items():
        print(f"  {concept}: {count} references")

    # Calculate ratios
    if evolution_tracking['Material desires'] > 0:
        phil_ratio = evolution_tracking['Philosophical abstraction'] / evolution_tracking['Material desires']
        print(f"\n  Philosophy/Desire Ratio: {phil_ratio:.2f}")

    if evolution_tracking['Ritual emphasis'] > 0:
        ethics_ratio = evolution_tracking['Ethical concepts'] / evolution_tracking['Ritual emphasis']
        print(f"  Ethics/Ritual Ratio: {ethics_ratio:.2f}")

    # Save detailed results
    results = {
        'philosophical_elements': {
            'black': [(t, c) for t, c, _ in black_phil],
            'white': [(t, c) for t, c, _ in white_phil]
        },
        'problematic_rituals': {
            'black': [(t, c) for t, c, _ in black_prob],
            'white': [(t, c) for t, c, _ in white_prob]
        },
        'caste_references': {
            'black': [(t, c) for t, c, _ in black_caste],
            'white': [(t, c) for t, c, _ in white_caste]
        },
        'evolution_metrics': evolution_tracking
    }

    with open('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/yajurveda_paradoxes_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*80)
    print("Analysis complete. Results saved to yajurveda_paradoxes_results.json")

if __name__ == "__main__":
    main()