const fs = require('fs');
const path = require('path');
const https = require('https');

const OUTPUT_DIR = path.join(__dirname, '../public');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'satapatha_sanskrit.json');
const CACHE_DIR = path.join(__dirname, '../cache/satapatha_sanskrit');

const BASE_URL = 'https://www.wisdomlib.org/hinduism/book/satapatha-brahmana-sanskrit';
const DELAY_MS = 150;

// Doc ID range based on wisdomlib structure
const START_DOC_ID = 1050942;
const END_DOC_ID = 1059014;

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

      if (res.statusCode === 404) {
        reject(new Error('404'));
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
    req.setTimeout(20000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

// Parse a verse page to extract Sanskrit text
function parseVersePage(html) {
  // Extract verse reference
  const refMatch = html.match(/Verse\s+(\d+)\.(\d+)\.(\d+)\.(\d+)/i);
  if (!refMatch) return null;

  const kanda = parseInt(refMatch[1]);
  const adhyaya = parseInt(refMatch[2]);
  const brahmana = parseInt(refMatch[3]);
  const verseNum = parseInt(refMatch[4]);

  // Clean HTML entities
  let content = html
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(code));

  // Extract paragraphs
  const paragraphs = content.match(/<p[^>]*>([\s\S]*?)<\/p>/gi) || [];
  let sanskritText = '';

  for (const p of paragraphs) {
    let text = p.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

    // Skip known non-content paragraphs
    if (text.match(/^(Previous|Next|Contents|Related|Book|Chapter|The Sanskrit text of|One of the largest|Preview of English|For a detailled|Also see the following|Home About|words \||\d+,\d+ words)/i)) {
      continue;
    }

    // Skip short text and metadata
    if (text.length < 30) continue;
    if (text.match(/ISBN|pages|Publisher|Motilal|volumes/i)) continue;

    // Sanskrit text typically contains these patterns:
    // - IAST diacritics: ā, ī, ū, ṛ, ṃ, ḥ, ś, ṣ, ṭ, ḍ, ṇ
    // - Pipe separator | (common in Sanskrit verses)
    // - Common Sanskrit words/endings
    const hasIAST = /[āīūṛṝḷṃḥṅñṭḍṇśṣ]/.test(text);
    const hasPipe = text.includes('|');
    const looksLikeSanskrit = /\b(iti|vai|ha|ca|eva|yat|tat|sa|te|na)\b/.test(text.toLowerCase());

    if ((hasIAST || hasPipe) && text.length >= 30 && (hasIAST || looksLikeSanskrit)) {
      sanskritText = text;
      break;
    }
  }

  if (!sanskritText || sanskritText.length < 20) return null;

  const hymnNumber = (adhyaya - 1) * 100 + brahmana;

  return {
    reference: `${kanda}.${adhyaya}.${brahmana}.${verseNum}`,
    text: sanskritText,
    mandala: kanda,
    hymn: hymnNumber,
    verse: verseNum,
    vedaId: 'satapatha_brahmana'
  };
}

async function main() {
  ensureDir(OUTPUT_DIR);
  ensureDir(CACHE_DIR);

  console.log('========================================');
  console.log('Satapatha Brahmana SANSKRIT Scraper v3');
  console.log('========================================\n');
  console.log(`Scanning doc IDs from ${START_DOC_ID} to ${END_DOC_ID}`);
  console.log(`Total potential pages: ${END_DOC_ID - START_DOC_ID + 1}\n`);

  const allVerses = [];
  let fetchCount = 0;
  let cachedCount = 0;
  let errorCount = 0;
  let verseCount = 0;

  for (let docId = START_DOC_ID; docId <= END_DOC_ID; docId++) {
    const url = `${BASE_URL}/d/doc${docId}.html`;
    const cacheKey = url.replace(/[^a-z0-9]/gi, '_').slice(-150);
    const cachedFile = path.join(CACHE_DIR, cacheKey + '.html');
    const isCached = fs.existsSync(cachedFile);

    try {
      const html = await fetchUrl(url);
      const verse = parseVersePage(html);

      if (verse) {
        allVerses.push(verse);
        verseCount++;
      }

      if (isCached) {
        cachedCount++;
      } else {
        fetchCount++;
        await sleep(DELAY_MS);
      }

      // Progress update every 500 pages
      const processed = docId - START_DOC_ID + 1;
      if (processed % 500 === 0) {
        const pct = Math.round(processed / (END_DOC_ID - START_DOC_ID + 1) * 100);
        console.log(`  [${pct}%] Processed ${processed} pages, found ${verseCount} verses (${fetchCount} fetched, ${cachedCount} cached)`);
      }
    } catch (error) {
      if (!error.message.includes('404')) {
        errorCount++;
      }
      // 404s are expected for non-existent pages
    }
  }

  // Sort and dedupe
  allVerses.sort((a, b) => {
    if (a.mandala !== b.mandala) return a.mandala - b.mandala;
    if (a.hymn !== b.hymn) return a.hymn - b.hymn;
    return a.verse - b.verse;
  });

  const uniqueVerses = [];
  const seen = new Set();
  for (const v of allVerses) {
    if (!seen.has(v.reference)) {
      seen.add(v.reference);
      uniqueVerses.push(v);
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
    const seenKeys = new Set();
    for (const v of verses) {
      const parts = v.reference.split('.');
      const key = `${parts[1]}.${parts[2]}`;
      if (!seenKeys.has(key)) {
        seenKeys.add(key);
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

  // Stats by Kanda
  const kandaCounts = {};
  for (const v of uniqueVerses) {
    kandaCounts[v.mandala] = (kandaCounts[v.mandala] || 0) + 1;
  }

  console.log('\n========================================');
  console.log('RESULTS');
  console.log('========================================');
  console.log(`Pages fetched: ${fetchCount}`);
  console.log(`Pages from cache: ${cachedCount}`);
  console.log(`Errors: ${errorCount}`);
  console.log(`Total verses: ${uniqueVerses.length}`);
  console.log('\nVerses per Kanda:');
  for (const [k, c] of Object.entries(kandaCounts).sort((a, b) => parseInt(a[0]) - parseInt(b[0]))) {
    console.log(`  Kanda ${k}: ${c}`);
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(uniqueVerses, null, 2));
  console.log(`\nSaved to: ${OUTPUT_FILE}`);

  if (uniqueVerses.length > 0) {
    console.log('\nSample:');
    console.log(JSON.stringify(uniqueVerses[0], null, 2));
  }
}

main().catch(console.error);
