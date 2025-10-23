const fs = require('fs');
const path = require('path');

const JSON_FILE = path.join(__dirname, '../public/atharvaveda.json');

function countWords(text) {
  if (!text) return 0;
  // Remove common punctuation and split by whitespace
  const cleaned = text
    .replace(/[।॥॰\u0901-\u0903\u093A-\u094F\u0951-\u0954\u0962-\u0963]/g, '') // Remove diacritics
    .replace(/[.,;:!?()[\]{}'"]/g, '')
    .trim();

  const words = cleaned.split(/\s+/).filter(w => w.length > 0);
  return words.length;
}

function main() {
  console.log('Loading Atharvaveda data...');

  const data = JSON.parse(fs.readFileSync(JSON_FILE, 'utf-8'));
  console.log(`Loaded ${data.length} verses\n`);

  // Group verses by hymn (book.hymn)
  const hymnMap = new Map();

  data.forEach(verse => {
    const hymnKey = `${verse.mandala}.${verse.hymn}`;

    if (!hymnMap.has(hymnKey)) {
      hymnMap.set(hymnKey, []);
    }

    hymnMap.get(hymnKey).push(verse);
  });

  console.log(`Total hymns: ${hymnMap.size}\n`);
  console.log('Searching for hymns where ALL verses have exactly 2 words in Sanskrit...\n');

  const twoWordHymns = [];

  for (const [hymnKey, verses] of hymnMap.entries()) {
    // Check if all verses in this hymn have Sanskrit text
    const allHaveSanskrit = verses.every(v => v.meaning && v.meaning.trim().length > 0);

    if (!allHaveSanskrit) continue;

    // Check if all verses have exactly 2 words
    const allTwoWords = verses.every(v => {
      const wordCount = countWords(v.meaning);
      return wordCount === 2;
    });

    if (allTwoWords) {
      twoWordHymns.push({
        hymn: hymnKey,
        verseCount: verses.length,
        verses: verses
      });
    }
  }

  console.log(`Found ${twoWordHymns.length} hymns where all verses have exactly 2 Sanskrit words:\n`);

  twoWordHymns.forEach(hymn => {
    const [book, hymnNum] = hymn.hymn.split('.');
    console.log(`\n${'='.repeat(70)}`);
    console.log(`Hymn ${hymn.hymn} (Book ${book}, Hymn ${hymnNum}) - ${hymn.verseCount} verses`);
    console.log('='.repeat(70));

    hymn.verses.forEach((verse, idx) => {
      console.log(`\nVerse ${idx + 1} (${verse.reference}):`);
      console.log(`Sanskrit: ${verse.meaning}`);
      console.log(`English: ${verse.text}`);
    });
  });

  if (twoWordHymns.length === 0) {
    console.log('No hymns found with all verses having exactly 2 Sanskrit words.');
    console.log('\nLet me search for short hymns and analyze word counts...\n');

    // Find hymns with short verses
    const shortHymns = [];

    for (const [hymnKey, verses] of hymnMap.entries()) {
      const allHaveSanskrit = verses.every(v => v.meaning && v.meaning.trim().length > 0);
      if (!allHaveSanskrit) continue;

      // Calculate word count statistics for this hymn
      const wordCounts = verses.map(v => countWords(v.meaning));
      const avgWords = wordCounts.reduce((a, b) => a + b, 0) / wordCounts.length;
      const maxWords = Math.max(...wordCounts);
      const minWords = Math.min(...wordCounts);

      if (avgWords <= 4 && maxWords <= 6) {
        shortHymns.push({
          hymn: hymnKey,
          verseCount: verses.length,
          avgWords: avgWords.toFixed(1),
          minWords: minWords,
          maxWords: maxWords,
          wordCounts: wordCounts,
          verses: verses
        });
      }
    }

    shortHymns.sort((a, b) => parseFloat(a.avgWords) - parseFloat(b.avgWords));

    console.log(`Found ${shortHymns.length} hymns with very short verses (avg ≤ 4 words, max ≤ 6 words):\n`);

    shortHymns.slice(0, 10).forEach(hymn => {
      console.log(`Hymn ${hymn.hymn}: ${hymn.verseCount} verses, avg ${hymn.avgWords} words (range: ${hymn.minWords}-${hymn.maxWords})`);
    });

    // Show details of the shortest hymn
    if (shortHymns.length > 0) {
      const shortest = shortHymns[0];
      console.log(`\n${'='.repeat(70)}`);
      console.log(`SHORTEST HYMN: ${shortest.hymn} - ${shortest.verseCount} verses`);
      console.log(`Average: ${shortest.avgWords} words per verse (range: ${shortest.minWords}-${shortest.maxWords})`);
      console.log('='.repeat(70));

      shortest.verses.forEach((verse, idx) => {
        const wordCount = countWords(verse.meaning);
        console.log(`\nVerse ${idx + 1} (${verse.reference}) - ${wordCount} words:`);
        console.log(`Sanskrit: ${verse.meaning}`);
        console.log(`English: ${verse.text}`);
      });
    }
  }
}

main();
