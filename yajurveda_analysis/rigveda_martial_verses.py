#!/usr/bin/env python3
"""
Find the most violent and martial verses from Rigveda
about crushing enemies and destroying foes
"""

import json
import re

def load_veda(filepath):
    """Load Veda JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_violent_verses(verses):
    """Search for verses about destroying enemies"""

    martial_patterns = [
        # Direct violence
        r'\bslay\b|\bslaying\b|\bslain\b|\bkill\b|\bkilling\b',
        r'\bdestroy\b|\bdestroying\b|\bdestruction\b',
        r'\bcrush\b|\bcrushing\b|\bcrushed\b',
        r'\bsmite\b|\bsmiting\b|\bsmitten\b|\bsmote\b',
        r'\bstrike\b|\bstriking\b|\bstruck\b',
        r'\bpierce\b|\bpiercing\b|\bpierced\b',
        r'\bshatter\b|\bshattering\b|\bshattered\b',
        r'\bcleave\b|\bcleaving\b|\bcleft\b',
        r'\bburn\b|\bburning\b|\bburnt\b',
        r'\bslaughter\b|\bslaughtering\b',

        # Enemy terms
        r'\benemy\b|\benemies\b|\bfoe\b|\bfoes\b',
        r'\bdasyu\b|\bdasa\b|\brakṣas\b|\bdemon\b',
        r'\bevil\b|\bwicked\b|\bhostile\b',
        r'\badversary\b|\badversaries\b',

        # Weapons and warfare
        r'\bweapon\b|\bthunderbolt\b|\bvajra\b',
        r'\barrow\b|\bspear\b|\bsword\b',
        r'\bbattle\b|\bwarfare\b|\bcombat\b',
        r'\bblood\b|\bbloody\b|\bgore\b',
        r'\bdeath\b|\bdead\b|\bperish\b',

        # Specific violent actions
        r'\btrample\b|\btrampling\b',
        r'\btear\b|\btearing\b|\btorn\b',
        r'\bbreak\b|\bbreaking\b|\bbroke\b',
        r'\bdevour\b|\bdevouring\b',
        r'\bconsume\b|\bconsuming\b',
        r'\bannihilate\b|\bannihilation\b'
    ]

    violent_verses = []
    violence_score = {}

    for verse in verses:
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        meaning = verse.get('meaning', '')

        # Count violence indicators
        score = 0
        matched_patterns = []

        for pattern in martial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
                matched_patterns.append(pattern)

        if score >= 3:  # Only include verses with multiple violence indicators
            violent_verses.append({
                'reference': ref,
                'text': text,
                'meaning': meaning,
                'score': score,
                'patterns': matched_patterns[:5]  # Top 5 patterns
            })
            violence_score[ref] = score

    # Sort by violence score
    violent_verses.sort(key=lambda x: x['score'], reverse=True)

    return violent_verses

def find_specific_martial_hymns(verses):
    """Find specific known martial hymns"""

    # Known martial hymns and verses
    martial_refs = [
        '01.032',  # Indra slaying Vritra
        '01.033',  # Indra's victories
        '01.053',  # Indra crushing enemies
        '01.063',  # Indra's martial deeds
        '01.080',  # Indra destroying foes
        '01.084',  # Indra's thunderbolt
        '01.100',  # Indra crushing Vritra
        '01.103',  # Indra in battle
        '01.130',  # Indra's warfare
        '02.012',  # Indra's violent deeds
        '04.016',  # Indra crushing enemies
        '04.017',  # Indra's battles
        '04.038',  # Dadhikra war horse
        '06.016',  # Agni burning enemies
        '06.022',  # Indra's victories
        '06.026',  # Indra slaying
        '07.018',  # Battle of Ten Kings
        '07.019',  # Indra in battle
        '07.020',  # Indra's warfare
        '07.021',  # Indra crushing
        '07.083',  # Battle hymn
        '07.104',  # Against sorcerers and demons
        '10.083',  # Manyu (Wrath) hymn
        '10.084',  # Manyu battle hymn
        '10.103',  # War drums and battle
        '10.166',  # Against rivals
    ]

    specific_verses = []

    for verse in verses:
        ref = verse.get('reference', '')
        # Check if this verse is from a martial hymn
        for martial_ref in martial_refs:
            if ref.startswith(martial_ref):
                text = verse.get('text', '')
                if any(word in text.lower() for word in
                       ['slay', 'kill', 'destroy', 'crush', 'smite', 'enemy', 'foe',
                        'battle', 'blood', 'death', 'weapon', 'pierce', 'burn']):
                    specific_verses.append({
                        'reference': ref,
                        'text': text,
                        'meaning': verse.get('meaning', ''),
                        'hymn': martial_ref
                    })

    return specific_verses

def main():
    print("="*80)
    print("MOST VIOLENT AND MARTIAL VERSES FROM RIGVEDA")
    print("Verses about Crushing Enemies and Destroying Foes")
    print("="*80)

    # Load Rigveda
    rigveda = load_veda('/Users/ashris/Desktop/rigved/rigveda-web/public/rigveda.json')

    # Find violent verses
    violent_verses = find_violent_verses(rigveda)

    print(f"\nFound {len(violent_verses)} highly martial verses")
    print("\n" + "="*80)
    print("TOP 20 MOST VIOLENT VERSES (by violence indicator score)")
    print("="*80)

    # Display top 20 most violent verses
    for i, verse_data in enumerate(violent_verses[:20], 1):
        print(f"\n{i}. RIGVEDA {verse_data['reference']}")
        print(f"   Violence Score: {verse_data['score']}")
        print(f"   Patterns: {', '.join(verse_data['patterns'])}")
        print(f"\n   English:")
        print(f"   {verse_data['text']}")
        if verse_data['meaning']:
            print(f"\n   Sanskrit:")
            print(f"   {verse_data['meaning'][:300]}...")
        print("-"*60)

    # Find specific martial hymns
    print("\n" + "="*80)
    print("SPECIFIC MARTIAL HYMNS AND BATTLE VERSES")
    print("="*80)

    martial_hymns = find_specific_martial_hymns(rigveda)

    # Group by hymn
    hymn_groups = {}
    for verse in martial_hymns:
        hymn = verse['hymn']
        if hymn not in hymn_groups:
            hymn_groups[hymn] = []
        hymn_groups[hymn].append(verse)

    # Show most violent hymns
    print("\nMost Violent Hymns:")
    for hymn, verses in sorted(hymn_groups.items())[:10]:
        print(f"\nHymn {hymn}: {len(verses)} violent verses")
        # Show most violent verse from this hymn
        if verses:
            print(f"   Example - RV {verses[0]['reference']}:")
            print(f"   {verses[0]['text'][:200]}...")

    # Special focus on specific ultra-violent verses
    print("\n" + "="*80)
    print("SPECIAL SELECTION: MOST BLOOD-CURDLING VERSES")
    print("="*80)

    # Look for specific ultra-violent verses
    for verse in rigveda:
        ref = verse.get('reference', '')
        text = verse.get('text', '')

        # Known ultra-violent verses
        ultra_violent_refs = [
            '01.032.05',  # Vritra's destruction
            '01.080.05',  # Crushing enemies
            '02.012.08',  # Indra smashing
            '04.038.05',  # War horse trampling
            '06.022.09',  # Burning enemies
            '07.104.11',  # Destroying demons
            '10.083.04',  # Manyu's wrath
            '10.084.02',  # Battle fury
            '10.103.12',  # Burning hearts
            '10.166.03',  # Crushing rivals
        ]

        if ref in ultra_violent_refs or (
            ('blood' in text.lower() or 'gore' in text.lower() or
             'slaughter' in text.lower() or 'burn' in text.lower() and 'heart' in text.lower()) and
            ('enemy' in text.lower() or 'foe' in text.lower())
        ):
            print(f"\nRV {ref}:")
            print(f"{text}")
            if verse.get('meaning'):
                print(f"Sanskrit: {verse.get('meaning', '')[:300]}...")
            print("-"*40)

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nThe Rigveda contains numerous verses celebrating violent conquest,")
    print("destruction of enemies, and martial prowess. This reflects the")
    print("warrior culture of the Indo-Aryans during the Bronze Age (1500-1200 BCE).")
    print("\nKey themes include:")
    print("• Indra crushing Vritra and other demons")
    print("• Burning and slaughtering enemies")
    print("• Trampling foes with horses and chariots")
    print("• Piercing enemies with weapons")
    print("• Total annihilation of adversaries")

if __name__ == "__main__":
    main()