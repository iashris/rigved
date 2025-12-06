const fs = require('fs');
const path = require('path');
const https = require('https');

const OUTPUT_DIR = path.join(__dirname, '../public');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'satapatha_brahmana.json');
const CACHE_DIR = path.join(__dirname, '../cache/satapatha');

// Base URL
const BASE_URL = 'https://www.wisdomlib.org/hinduism/book/satapatha-brahmana-english';

// Rate limiting
const DELAY_MS = 300;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const cacheKey = url.replace(/[^a-z0-9]/gi, '_').slice(-150);
    const cachedFile = path.join(CACHE_DIR, cacheKey + '.html');

    if (fs.existsSync(cachedFile)) {
      resolve(fs.readFileSync(cachedFile, 'utf-8'));
      return;
    }

    console.log(`  Fetching: ${url}`);

    const req = https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
      }
    }, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        const redirectUrl = res.headers.location.startsWith('http')
          ? res.headers.location
          : `https://www.wisdomlib.org${res.headers.location}`;
        fetchUrl(redirectUrl).then(resolve).catch(reject);
        return;
      }

      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        ensureDir(CACHE_DIR);
        fs.writeFileSync(cachedFile, data);
        resolve(data);
      });
    });

    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

// Parse index page to get all Brahmana section links
async function parseIndexPage() {
  const html = await fetchUrl(BASE_URL);
  const sections = [];

  // Match links to doc pages with Kanda/Adhyaya/Brahmana info
  // Pattern: href="/hinduism/book/satapatha-brahmana-english/d/doc63xxx.html"
  const linkPattern = /href=["']([^"']*\/d\/doc(\d+)\.html)["'][^>]*>/gi;
  const titlePattern = /K[āa][nṇ][ḍd]a\s+(\d+|[IVX]+)[,\s]+[Aa]dhy[āa]ya\s+(\d+)[,\s]+[Bb]r[āa]hma[nṇ]a\s+(\d+)/i;

  // Get all document links
  const docLinks = new Set();
  let match;
  while ((match = linkPattern.exec(html)) !== null) {
    const href = match[1];
    const docId = parseInt(match[2]);

    // Filter to main content pages (doc63xxx range based on fetch results)
    if (docId >= 63100 && docId <= 63550) {
      const fullUrl = href.startsWith('http') ? href : `https://www.wisdomlib.org${href}`;
      docLinks.add(fullUrl);
    }
  }

  console.log(`Found ${docLinks.size} potential document links`);
  return Array.from(docLinks).sort();
}

// Convert Roman numerals to Arabic
function romanToArabic(roman) {
  if (!roman) return 0;
  if (/^\d+$/.test(roman)) return parseInt(roman);

  const romanMap = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 };
  let result = 0;
  const upper = roman.toUpperCase();

  for (let i = 0; i < upper.length; i++) {
    const current = romanMap[upper[i]] || 0;
    const next = romanMap[upper[i + 1]] || 0;
    if (current < next) {
      result -= current;
    } else {
      result += current;
    }
  }
  return result;
}

// Parse a Brahmana document page
function parseBrahmanaPage(html, url) {
  const verses = [];

  // Extract Kanda, Adhyaya, Brahmana from page title or content
  const titleMatch = html.match(/K[āa][nṇ][ḍd]a\s+(\d+|[IVX]+)[,\s]+[Aa]dhy[āa]ya\s+(\d+)[,\s]+[Bb]r[āa]hma[nṇ]a\s+(\d+)/i);

  if (!titleMatch) {
    return verses;
  }

  const kanda = romanToArabic(titleMatch[1]);
  const adhyaya = parseInt(titleMatch[2]) || romanToArabic(titleMatch[2]);
  const brahmana = parseInt(titleMatch[3]) || romanToArabic(titleMatch[3]);

  if (!kanda || !adhyaya || !brahmana) {
    return verses;
  }

  // Find the main content area - typically after "Contents of this online book"
  let content = html;

  // Try to extract just the content area
  const contentStart = html.indexOf('<div class="chapter-inner">');
  const contentEnd = html.indexOf('<div class="chapter-footer">');
  if (contentStart > -1 && contentEnd > contentStart) {
    content = html.substring(contentStart, contentEnd);
  }

  // Parse numbered paragraphs
  // Pattern 1: <p><b>X.</b> text</p>
  // Pattern 2: <p><strong>X.</strong> text</p>
  // Pattern 3: Just numbered text like "1. text"

  // First clean up HTML entities
  content = content
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(code));

  // Extract paragraphs
  const paragraphPattern = /<p[^>]*>([\s\S]*?)<\/p>/gi;
  let paragraphMatch;

  while ((paragraphMatch = paragraphPattern.exec(content)) !== null) {
    let paragraphText = paragraphMatch[1];

    // Check if it starts with a number (possibly bold)
    const numMatch = paragraphText.match(/^[\s]*(?:<[^>]+>)*\s*(\d+)\.\s*/);

    if (numMatch) {
      const verseNum = parseInt(numMatch[1]);

      // Extract the text after the number
      let text = paragraphText
        .replace(/^[\s]*(?:<[^>]+>)*\s*\d+\.\s*/, '')  // Remove leading number
        .replace(/<sup[^>]*>.*?<\/sup>/gi, '')  // Remove footnotes
        .replace(/<a[^>]*>(.*?)<\/a>/gi, '$1')  // Keep link text, remove tags
        .replace(/<[^>]+>/g, ' ')  // Remove remaining HTML tags
        .replace(/\s+/g, ' ')  // Normalize whitespace
        .trim();

      // Skip very short entries or navigation text
      if (text.length > 20 && !text.match(/^(Previous|Next|Contents)/i)) {
        // Create hymn number as combination of adhyaya and brahmana
        // This allows navigation: Kanda -> Brahmana (adhyaya.brahmana combined) -> Verse
        const hymnNumber = (adhyaya - 1) * 100 + brahmana;

        verses.push({
          reference: `${kanda}.${adhyaya}.${brahmana}.${verseNum}`,
          text: text,
          mandala: kanda,
          hymn: hymnNumber,
          verse: verseNum,
          vedaId: 'satapatha_brahmana'
        });
      }
    }
  }

  // If no paragraphs found, try alternate patterns
  if (verses.length === 0) {
    // Look for text blocks with numbers
    const altPattern = /(?:^|\n)\s*(\d+)\.\s+([^\n]+)/g;
    let altMatch;

    const plainText = content.replace(/<[^>]+>/g, ' ');

    while ((altMatch = altPattern.exec(plainText)) !== null) {
      const verseNum = parseInt(altMatch[1]);
      const text = altMatch[2].trim();

      if (text.length > 20) {
        const hymnNumber = (adhyaya - 1) * 100 + brahmana;

        verses.push({
          reference: `${kanda}.${adhyaya}.${brahmana}.${verseNum}`,
          text: text,
          mandala: kanda,
          hymn: hymnNumber,
          verse: verseNum,
          vedaId: 'satapatha_brahmana'
        });
      }
    }
  }

  return verses;
}

async function main() {
  ensureDir(OUTPUT_DIR);
  ensureDir(CACHE_DIR);

  console.log('========================================');
  console.log('Satapatha Brahmana Scraper');
  console.log('========================================\n');

  // Get all document URLs from index
  console.log('Step 1: Parsing index page...');
  const docUrls = await parseIndexPage();
  console.log(`Found ${docUrls.length} documents to process\n`);

  // Process each document
  console.log('Step 2: Processing documents...\n');
  const allVerses = [];
  let processedCount = 0;
  let skippedCount = 0;

  for (let i = 0; i < docUrls.length; i++) {
    const url = docUrls[i];

    try {
      const html = await fetchUrl(url);
      const verses = parseBrahmanaPage(html, url);

      if (verses.length > 0) {
        console.log(`  [${i + 1}/${docUrls.length}] ${verses[0].reference.split('.').slice(0, 3).join('.')}: ${verses.length} verses`);
        allVerses.push(...verses);
        processedCount++;
      } else {
        skippedCount++;
      }

      await sleep(DELAY_MS);
    } catch (error) {
      console.error(`  Error processing ${url}: ${error.message}`);
      skippedCount++;
    }
  }

  // Also try sequential document IDs in case we missed any
  console.log('\nStep 3: Checking for additional documents...');
  const existingRefs = new Set(allVerses.map(v => v.reference.split('.').slice(0, 3).join('.')));

  for (let docId = 63100; docId <= 63550; docId++) {
    const url = `${BASE_URL}/d/doc${docId}.html`;

    try {
      const html = await fetchUrl(url);
      const verses = parseBrahmanaPage(html, url);

      if (verses.length > 0) {
        const ref = verses[0].reference.split('.').slice(0, 3).join('.');
        if (!existingRefs.has(ref)) {
          console.log(`  Found additional: ${ref} (${verses.length} verses)`);
          allVerses.push(...verses);
          existingRefs.add(ref);
        }
      }

      await sleep(DELAY_MS / 2);  // Faster since mostly cached
    } catch (error) {
      // Skip silently
    }
  }

  // Sort verses
  allVerses.sort((a, b) => {
    if (a.mandala !== b.mandala) return a.mandala - b.mandala;
    if (a.hymn !== b.hymn) return a.hymn - b.hymn;
    return a.verse - b.verse;
  });

  // Remove duplicates
  const uniqueVerses = [];
  const seenRefs = new Set();
  for (const verse of allVerses) {
    if (!seenRefs.has(verse.reference)) {
      seenRefs.add(verse.reference);
      uniqueVerses.push(verse);
    }
  }

  // Reassign sequential hymn numbers per Kanda
  const versesByKanda = {};
  for (const v of uniqueVerses) {
    if (!versesByKanda[v.mandala]) versesByKanda[v.mandala] = [];
    versesByKanda[v.mandala].push(v);
  }

  for (const kanda of Object.keys(versesByKanda)) {
    const verses = versesByKanda[kanda];
    // Get unique adhyaya.brahmana combinations in order
    const brahmanaKeys = [];
    const seen = new Set();
    for (const v of verses) {
      const parts = v.reference.split('.');
      const key = `${parts[1]}.${parts[2]}`;
      if (!seen.has(key)) {
        seen.add(key);
        brahmanaKeys.push(key);
      }
    }
    // Create mapping from adhyaya.brahmana to sequential hymn number
    const hymnMap = {};
    brahmanaKeys.forEach((key, idx) => {
      hymnMap[key] = idx + 1;
    });
    // Update verses
    for (const v of verses) {
      const parts = v.reference.split('.');
      const key = `${parts[1]}.${parts[2]}`;
      v.hymn = hymnMap[key];
    }
  }

  console.log('\n========================================');
  console.log('RESULTS');
  console.log('========================================');
  console.log(`Documents processed: ${processedCount}`);
  console.log(`Documents skipped: ${skippedCount}`);
  console.log(`Total verses: ${uniqueVerses.length}`);

  // Statistics by Kanda
  const kandaCounts = {};
  for (const verse of uniqueVerses) {
    kandaCounts[verse.mandala] = (kandaCounts[verse.mandala] || 0) + 1;
  }
  console.log('\nVerses per Kanda:');
  for (const [kanda, count] of Object.entries(kandaCounts).sort((a, b) => parseInt(a[0]) - parseInt(b[0]))) {
    console.log(`  Kanda ${kanda}: ${count} verses`);
  }

  // Save to file
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(uniqueVerses, null, 2));
  console.log(`\nSaved to: ${OUTPUT_FILE}`);

  // Sample output
  if (uniqueVerses.length > 0) {
    console.log('\nSample verse:');
    console.log(JSON.stringify(uniqueVerses[0], null, 2));
  }
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
