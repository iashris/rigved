import type { Verse, SearchResult } from '../types';
import { CHRONOLOGICAL_ORDER } from '../types';

// Normalize text by removing diacritics and special characters
function normalizeText(text: string): string {
  // Common Sanskrit diacritics and their replacements
  const replacements: Record<string, string> = {
    'ā': 'a', 'Ā': 'A',
    'ī': 'i', 'Ī': 'I', 
    'ū': 'u', 'Ū': 'U',
    'ṛ': 'r', 'Ṛ': 'R',
    'ṝ': 'r', 'Ṝ': 'R',
    'ḷ': 'l', 'Ḷ': 'L',
    'ḹ': 'l', 'Ḹ': 'L',
    'ṃ': 'm', 'Ṃ': 'M',
    'ḥ': 'h', 'Ḥ': 'H',
    'ṅ': 'n', 'Ṅ': 'N',
    'ñ': 'n', 'Ñ': 'N',
    'ṭ': 't', 'Ṭ': 'T',
    'ḍ': 'd', 'Ḍ': 'D',
    'ṇ': 'n', 'Ṇ': 'N',
    'ś': 's', 'Ś': 'S',
    'ṣ': 's', 'Ṣ': 'S',
    'ẓ': 'z', 'Ẓ': 'Z',
    'ḻ': 'l', 'Ḻ': 'L',
    'â': 'a', 'Â': 'A',
    'î': 'i', 'Î': 'I',
    'û': 'u', 'Û': 'U',
    'ê': 'e', 'Ê': 'E',
    'ô': 'o', 'Ô': 'O',
    'ṁ': 'm',
    'ḿ': 'm', 'Ḿ': 'M'
  };
  
  let normalized = text;
  for (const [diacritic, replacement] of Object.entries(replacements)) {
    normalized = normalized.replace(new RegExp(diacritic, 'g'), replacement);
  }
  
  // Also normalize using built-in normalize method for any remaining unicode
  return normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

export async function loadRigvedaData(): Promise<Verse[]> {
  try {
    const response = await fetch('./griffith.csv');
    const text = await response.text();
    const lines = text.split('\n').filter(line => line.trim());
    
    const verses: Verse[] = lines.map(line => {
      const [reference, ...textParts] = line.split('\t');
      const text = textParts.join('\t');
      
      const match = reference.match(/(\d{2})\.(\d{3})\.(\d{2})/);
      if (!match) return null;
      
      const mandala = parseInt(match[1]);
      const hymn = parseInt(match[2]);
      const verse = parseInt(match[3]);
      
      const chronoPosition = CHRONOLOGICAL_ORDER.indexOf(mandala) + 1;
      
      return {
        reference,
        text,
        mandala,
        hymn,
        verse,
        chronologicalPosition: chronoPosition
      };
    }).filter(Boolean) as Verse[];
    
    return verses;
  } catch (error) {
    console.error('Error loading Rigveda data:', error);
    return [];
  }
}

export function searchWord(
  verses: Verse[],
  searchTerms: string[],
  caseSensitive: boolean = false
): SearchResult | null {
  if (!searchTerms.length || !verses.length) return null;
  
  // Normalize search terms
  const normalizedSearchTerms = searchTerms.map(term => normalizeText(term));
  
  // Find matching verses using normalized comparison
  const matches = verses.filter(verse => {
    const normalizedVerseText = normalizeText(verse.text);
    
    // Check if any of the normalized search terms appear in the normalized verse
    return normalizedSearchTerms.some(term => {
      if (caseSensitive) {
        // For case-sensitive, still use normalization but preserve case
        const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g');
        return regex.test(normalizedVerseText);
      } else {
        // Case-insensitive search with normalization
        const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
        return regex.test(normalizedVerseText);
      }
    });
  });
  
  if (matches.length === 0) return null;
  
  // Count by mandala
  const mandalaCounts = new Array(10).fill(0);
  const mandalaSizes = new Array(10).fill(0);
  
  verses.forEach(verse => {
    mandalaSizes[verse.mandala - 1]++;
  });
  
  matches.forEach(verse => {
    mandalaCounts[verse.mandala - 1]++;
  });
  
  // Calculate percentages
  const mandalaPercentages = mandalaCounts.map((count, idx) => {
    const size = mandalaSizes[idx];
    return size > 0 ? (count / size) * 100 : 0;
  });
  
  return {
    word: searchTerms.join(', '),
    totalMatches: matches.length,
    mandalaCounts,
    mandalaPercentages,
    mandalaSizes,
    matches: matches.slice(0, 100) // Limit to first 100 matches for performance
  };
}