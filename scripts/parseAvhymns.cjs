const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const AVHYMNS_DIR = path.join(__dirname, '../public/avhymns');
const OUTPUT_FILE = path.join(__dirname, '../public/atharvaveda.json');

function parseHtmlFile(filePath) {
  const html = fs.readFileSync(filePath, 'utf-8');

  // Use regex to extract verses directly from HTML
  const verses = [];

  // Match pattern: <a id='avXX.YYY.ZZ'/> followed by paragraphs
  const versePattern = /<a id=['"]av(\d{2})\.(\d{3})\.(\d{2,3})['"]\/?>.*?(?=<a id=['"]av|<div|$)/gs;

  const matches = html.matchAll(versePattern);

  for (const match of matches) {
    const fullMatch = match[0];
    const book = parseInt(match[1], 10);
    const hymn = parseInt(match[2], 10);
    const verse = parseInt(match[3], 10);

    // Extract Sanskrit text (class="sa")
    const saMatch = fullMatch.match(/<p class=["']sa["']>(.*?)<\/p>/s);
    let sanskritText = '';
    if (saMatch) {
      sanskritText = saMatch[1]
        .replace(/<br\s*\/?>/gi, ' ')
        .replace(/<[^>]+>/g, '')
        .replace(/\s+/g, ' ')
        .trim();
    }

    // Extract English text (class="en")
    const enMatch = fullMatch.match(/<p class=["']en["']>(.*?)<\/p>/s);
    let englishText = '';
    if (enMatch) {
      englishText = enMatch[1]
        .replace(/<br\s*\/?>/gi, ' ')
        .replace(/<[^>]+>/g, '')
        .replace(/\s+/g, ' ')
        .trim();
    }

    // Use English text as the main text, with Sanskrit as meaning
    const text = englishText || sanskritText;
    if (!text) continue;

    verses.push({
      reference: `${book.toString().padStart(2, '0')}.${hymn.toString().padStart(3, '0')}.${verse.toString().padStart(2, '0')}`,
      text: text,
      mandala: book,
      hymn: hymn,
      verse: verse,
      meaning: sanskritText && sanskritText !== text ? sanskritText : undefined,
      vedaId: 'atharvaveda'
    });
  }

  return verses;
}

function main() {
  console.log('Starting to parse Atharvaveda HTML files...');

  const allVerses = [];
  const files = fs.readdirSync(AVHYMNS_DIR).filter(f => f.endsWith('.html'));

  console.log(`Found ${files.length} HTML files`);

  files.forEach((file, index) => {
    try {
      const filePath = path.join(AVHYMNS_DIR, file);
      const verses = parseHtmlFile(filePath);
      allVerses.push(...verses);

      if ((index + 1) % 50 === 0) {
        console.log(`Processed ${index + 1}/${files.length} files...`);
      }
    } catch (error) {
      console.error(`Error parsing ${file}:`, error.message);
    }
  });

  // Sort verses by book, hymn, verse
  allVerses.sort((a, b) => {
    if (a.mandala !== b.mandala) return a.mandala - b.mandala;
    if (a.hymn !== b.hymn) return a.hymn - b.hymn;
    return a.verse - b.verse;
  });

  console.log(`\nTotal verses parsed: ${allVerses.length}`);

  // Write to JSON file
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(allVerses, null, 2));

  console.log(`\nSuccessfully wrote ${allVerses.length} verses to ${OUTPUT_FILE}`);

  // Print some statistics
  const books = new Set(allVerses.map(v => v.mandala));
  console.log(`Books: ${books.size}`);
  console.log(`First verse: ${allVerses[0].reference}`);
  console.log(`Last verse: ${allVerses[allVerses.length - 1].reference}`);
}

main();
