const fs = require('fs');
const path = require('path');

const PUBLIC_DIR = path.join(__dirname, '../public');
const ENGLISH_FILE = path.join(PUBLIC_DIR, 'satapatha_brahmana.json');
const SANSKRIT_FILE = path.join(PUBLIC_DIR, 'satapatha_sanskrit.json');
const OUTPUT_FILE = path.join(PUBLIC_DIR, 'satapatha_brahmana.json');

// IAST to Devanagari converter
function simpleIASTToDevanagari(text) {
  if (!text) return '';

  // Mapping tables
  const consonantMap = {
    'kh': 'ख', 'gh': 'घ', 'ch': 'छ', 'jh': 'झ', 'ṭh': 'ठ',
    'ḍh': 'ढ', 'th': 'थ', 'dh': 'ध', 'ph': 'फ', 'bh': 'भ',
    'k': 'क', 'g': 'ग', 'ṅ': 'ङ', 'c': 'च', 'j': 'ज', 'ñ': 'ञ',
    'ṭ': 'ट', 'ḍ': 'ड', 'ṇ': 'ण', 't': 'त', 'd': 'द', 'n': 'न',
    'p': 'प', 'b': 'ब', 'm': 'म', 'y': 'य', 'r': 'र', 'l': 'ल',
    'v': 'व', 'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह'
  };

  const vowelMap = {
    'ai': 'ऐ', 'au': 'औ', 'ā': 'आ', 'ī': 'ई', 'ū': 'ऊ',
    'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'e': 'ए', 'o': 'ओ',
    'a': 'अ', 'i': 'इ', 'u': 'उ'
  };

  const matraMap = {
    'ai': 'ै', 'au': 'ौ', 'ā': 'ा', 'ī': 'ी', 'ū': 'ू',
    'ṛ': 'ृ', 'ṝ': 'ॄ', 'ḷ': 'ॢ', 'e': 'े', 'o': 'ो',
    'a': '', 'i': 'ि', 'u': 'ु'
  };

  const specialMap = {
    'ṃ': 'ं', 'ḥ': 'ः', "'": 'ऽ', '|': '।'
  };

  let result = '';
  let i = 0;
  const lowerText = text.toLowerCase();

  while (i < lowerText.length) {
    let found = false;

    // Try consonant clusters first (2 char)
    const twoChar = lowerText.substr(i, 2);
    if (consonantMap[twoChar]) {
      result += consonantMap[twoChar];
      i += 2;

      // Look for following vowel
      let vowelFound = false;
      for (const [v, matra] of Object.entries(matraMap).sort((a, b) => b[0].length - a[0].length)) {
        if (lowerText.substr(i).startsWith(v)) {
          result += matra;
          i += v.length;
          vowelFound = true;
          break;
        }
      }

      // Add halant if no vowel and next is consonant
      if (!vowelFound) {
        const next = lowerText[i];
        const nextTwo = lowerText.substr(i, 2);
        if (consonantMap[nextTwo] || consonantMap[next]) {
          result += '्';
        }
      }
      found = true;
      continue;
    }

    // Try single consonant
    const oneChar = lowerText[i];
    if (consonantMap[oneChar]) {
      result += consonantMap[oneChar];
      i += 1;

      // Look for following vowel
      let vowelFound = false;
      for (const [v, matra] of Object.entries(matraMap).sort((a, b) => b[0].length - a[0].length)) {
        if (lowerText.substr(i).startsWith(v)) {
          result += matra;
          i += v.length;
          vowelFound = true;
          break;
        }
      }

      // Add halant if no vowel and next is consonant
      if (!vowelFound) {
        const next = lowerText[i];
        const nextTwo = lowerText.substr(i, 2);
        if (consonantMap[nextTwo] || consonantMap[next]) {
          result += '्';
        }
      }
      found = true;
      continue;
    }

    // Try vowels (standalone)
    for (const [v, dev] of Object.entries(vowelMap).sort((a, b) => b[0].length - a[0].length)) {
      if (lowerText.substr(i).startsWith(v)) {
        result += dev;
        i += v.length;
        found = true;
        break;
      }
    }
    if (found) continue;

    // Special characters
    if (specialMap[oneChar]) {
      result += specialMap[oneChar];
      i++;
      continue;
    }

    // Keep spaces and other characters
    result += text[i];
    i++;
  }

  return result;
}

function main() {
  console.log('Loading English verses...');
  const englishVerses = JSON.parse(fs.readFileSync(ENGLISH_FILE, 'utf-8'));
  console.log(`  Loaded ${englishVerses.length} English verses`);

  console.log('Loading Sanskrit verses...');
  const sanskritVerses = JSON.parse(fs.readFileSync(SANSKRIT_FILE, 'utf-8'));
  console.log(`  Loaded ${sanskritVerses.length} Sanskrit verses`);

  // Create a map of Sanskrit verses by reference
  const sanskritMap = new Map();
  for (const verse of sanskritVerses) {
    sanskritMap.set(verse.reference, verse.text);
  }

  console.log('\nMerging and converting...');
  let matchCount = 0;
  let convertCount = 0;

  for (const verse of englishVerses) {
    const sanskritIAST = sanskritMap.get(verse.reference);

    if (sanskritIAST) {
      matchCount++;
      // Convert IAST to Devanagari
      const devanagari = simpleIASTToDevanagari(sanskritIAST);
      verse.meaning = devanagari;
      verse.sanskrit_iast = sanskritIAST; // Keep IAST version too
      convertCount++;
    }
  }

  console.log(`  Matched ${matchCount} verses`);
  console.log(`  Converted ${convertCount} to Devanagari`);

  // Save merged file
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(englishVerses, null, 2));
  console.log(`\nSaved to: ${OUTPUT_FILE}`);

  // Show sample
  const sampleWithMeaning = englishVerses.find(v => v.meaning);
  if (sampleWithMeaning) {
    console.log('\nSample verse with Sanskrit:');
    console.log('Reference:', sampleWithMeaning.reference);
    console.log('English:', sampleWithMeaning.text.substring(0, 100) + '...');
    console.log('Sanskrit (IAST):', sampleWithMeaning.sanskrit_iast?.substring(0, 80) + '...');
    console.log('Sanskrit (Devanagari):', sampleWithMeaning.meaning?.substring(0, 80) + '...');
  }

  // Stats
  const withMeaning = englishVerses.filter(v => v.meaning).length;
  const withoutMeaning = englishVerses.filter(v => !v.meaning).length;
  console.log(`\nFinal stats:`);
  console.log(`  Total verses: ${englishVerses.length}`);
  console.log(`  With Sanskrit: ${withMeaning}`);
  console.log(`  Without Sanskrit: ${withoutMeaning}`);
}

main();
