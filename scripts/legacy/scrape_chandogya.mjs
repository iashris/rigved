#!/usr/bin/env node
/**
 * Scrape Chandogya Upanishad from wisdomlib.org
 */

import { JSDOM } from 'jsdom';
import fs from 'fs/promises';

const BASE_URL = 'https://www.wisdomlib.org/hinduism/book/chandogya-upanishad-english/d/doc';

async function fetchPage(url) {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      },
    });
    if (!response.ok) {
      return null;
    }
    const html = await response.text();
    return new JSDOM(html);
  } catch (error) {
    console.error(`Error fetching ${url}:`, error.message);
    return null;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function extractVerseContent(dom) {
  const document = dom.window.document;
  const result = {
    sanskrit_devanagari: '',
    sanskrit_iast: '',
    english: '',
    reference: '',
  };

  // Get the title which usually has the verse reference
  const title = document.querySelector('h1');
  const pageTitle = document.querySelector('title');

  let titleText = title ? title.textContent : (pageTitle ? pageTitle.textContent : '');

  const match = titleText.match(/(\d+)\.(\d+)\.(\d+)/);
  if (match) {
    result.reference = match[0];
  }

  // Find main content - use chapter-content div
  const content = document.querySelector('.chapter-content') || document.querySelector('article') || document.body;

  // Get all paragraphs in order
  const paragraphs = content.querySelectorAll('p');

  let foundIAST = false;

  for (const p of paragraphs) {
    const text = p.textContent.trim();
    if (text.length < 10) continue;

    // Check if contains Devanagari characters
    const hasDevanagari = /[\u0900-\u097F]/.test(text);
    // Check if it's IAST (has diacritics and verse markers ||)
    const hasIAST = /\|\|/.test(text) && /[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]/i.test(text) && !hasDevanagari;

    if (hasDevanagari && !result.sanskrit_devanagari) {
      // Clean up the Devanagari text
      result.sanskrit_devanagari = text.replace(/\n+/g, ' ').trim();
      continue;
    }

    if (hasIAST && !result.sanskrit_iast) {
      result.sanskrit_iast = text.replace(/\n+/g, ' ').trim();
      foundIAST = true;
      continue;
    }

    // After finding IAST, the next meaningful paragraph is usually the English translation
    // It often starts with a number like "1. Om is..."
    if (foundIAST && !result.english) {
      // Skip metadata and boilerplate
      if (text.includes('Like what you read?') ||
          text.includes('Click here') ||
          text.includes('share this') ||
          text.includes('humbly request') ||
          text.includes('ISBN') ||
          text.includes('Swami Lokeswarananda |') ||
          text.startsWith('This is the English translation')) {
        continue;
      }

      // The translation paragraph - accept it
      // Clean it up a bit
      let cleaned = text.replace(/\n+/g, ' ').trim();
      // Remove leading verse number if present (e.g., "1. ")
      cleaned = cleaned.replace(/^\d+\.\s*/, '');
      result.english = cleaned;
      break;  // Found the translation, stop looking
    }
  }

  return result;
}

function isVersePage(dom) {
  const document = dom.window.document;
  const title = document.querySelector('title, h1');
  if (title) {
    const text = title.textContent;
    return /Verse\s+\d+\.\d+\.\d+/.test(text);
  }
  return false;
}

function parseReference(reference) {
  const match = reference.match(/(\d+)\.(\d+)\.(\d+)/);
  if (match) {
    return {
      chapter: parseInt(match[1]),
      section: parseInt(match[2]),
      verse: parseInt(match[3]),
    };
  }
  return null;
}

async function scrapeRange(startDoc, endDoc) {
  const verses = [];
  let lastProgress = Date.now();

  console.log(`Scraping doc IDs ${startDoc} to ${endDoc}...`);

  for (let docId = startDoc; docId <= endDoc; docId++) {
    const url = `${BASE_URL}${docId}.html`;

    // Progress update every 50 docs or 10 seconds
    if (docId % 50 === 0 || (Date.now() - lastProgress > 10000)) {
      console.log(`  Progress: doc ${docId} (${verses.length} verses so far)...`);
      lastProgress = Date.now();
    }

    const dom = await fetchPage(url);
    if (!dom) {
      continue;
    }

    if (!isVersePage(dom)) {
      continue; // Skip section index pages
    }

    const content = extractVerseContent(dom);

    if (!content.reference) {
      continue;
    }

    const parsed = parseReference(content.reference);
    if (!parsed) {
      continue;
    }

    const verseData = {
      reference: content.reference,
      text: content.english || '',
      mandala: parsed.chapter,  // prapathaka
      hymn: parsed.section,     // khanda
      verse: parsed.verse,
      vedaId: 'chandogya_upanishad',
      meaning: content.sanskrit_devanagari || '',
      sanskrit_iast: content.sanskrit_iast || '',
    };

    verses.push(verseData);

    // Be polite to the server - 300ms between requests
    await sleep(300);
  }

  return verses;
}

async function main() {
  console.log('Starting Chandogya Upanishad scraper...\n');
  console.log('This will take approximately 5-10 minutes...\n');

  // Based on analysis: doc238710 (1.1.1) to approximately doc239500
  const startDoc = 238710;
  const endDoc = 239500;

  const verses = await scrapeRange(startDoc, endDoc);

  // Sort verses by chapter, section, verse
  verses.sort((a, b) => {
    if (a.mandala !== b.mandala) return a.mandala - b.mandala;
    if (a.hymn !== b.hymn) return a.hymn - b.hymn;
    return a.verse - b.verse;
  });

  // Save to JSON
  const outputPath = 'public/chandogya_upanishad.json';
  await fs.writeFile(outputPath, JSON.stringify(verses, null, 2), 'utf-8');

  console.log(`\n\nDone! Saved ${verses.length} verses to ${outputPath}`);

  // Print summary
  const summary = {};
  for (const verse of verses) {
    const key = verse.mandala;
    summary[key] = (summary[key] || 0) + 1;
  }
  console.log('\nVerses per chapter:');
  for (const [chapter, count] of Object.entries(summary)) {
    console.log(`  Chapter ${chapter}: ${count} verses`);
  }
}

main().catch(console.error);
