import type { Verse, SearchResult, VedaId, VedaMetadata } from "../types";
import { VEDA_CONFIGS } from "../types";

// Normalize text by removing diacritics and special characters
function normalizeText(text: string): string {
  // Common Sanskrit diacritics and their replacements
  const replacements: Record<string, string> = {
    ā: "a",
    Ā: "A",
    ī: "i",
    Ī: "I",
    ū: "u",
    Ū: "U",
    ṛ: "r",
    Ṛ: "R",
    ṝ: "r",
    Ṝ: "R",
    ḷ: "l",
    Ḷ: "L",
    ḹ: "l",
    Ḹ: "L",
    ṃ: "m",
    Ṃ: "M",
    ḥ: "h",
    Ḥ: "H",
    ṅ: "n",
    Ṅ: "N",
    ñ: "n",
    Ñ: "N",
    ṭ: "t",
    Ṭ: "T",
    ḍ: "d",
    Ḍ: "D",
    ṇ: "n",
    Ṇ: "N",
    ś: "s",
    Ś: "S",
    ṣ: "s",
    Ṣ: "S",
    ẓ: "z",
    Ẓ: "Z",
    ḻ: "l",
    Ḻ: "L",
    â: "a",
    Â: "A",
    î: "i",
    Î: "I",
    û: "u",
    Û: "U",
    ê: "e",
    Ê: "E",
    ô: "o",
    Ô: "O",
    ṁ: "m",
    ḿ: "m",
    Ḿ: "M",
  };

  let normalized = text;
  for (const [diacritic, replacement] of Object.entries(replacements)) {
    normalized = normalized.replace(new RegExp(diacritic, "g"), replacement);
  }

  // Also normalize using built-in normalize method for any remaining unicode
  return normalized.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function createReference(mandala: string, hymn: string, verse: string): string {
  return `${mandala}.${hymn}.${verse}`;
}

function finalizeVerse(
  verse: Verse | null,
  parts: string[],
  collection: Verse[]
) {
  if (!verse) return;

  const text = parts.join(" ").replace(/\s+/g, " ").trim();
  if (!text) return;

  const cleaned = text.replace(/\s*\[p\.[^\]]*\]/gi, "").trim();

  verse.text = cleaned;
  collection.push(verse);
}

function parseRigvedaCSV(text: string): Verse[] {
  const metadata = VEDA_CONFIGS.rigveda;
  const lines = text.split("\n").filter((line) => line.trim());

  const verses: Verse[] = lines
    .map((line) => {
      const [reference, ...textParts] = line.split("\t");
      const text = textParts.join("\t");

      const match = reference.match(/(\d{2})\.(\d{3})\.(\d{2})/);
      if (!match) return null;

      const mandala = parseInt(match[1], 10);
      const hymn = parseInt(match[2], 10);
      const verse = parseInt(match[3], 10);

      const chronoSequence = metadata.chronologicalOrder ?? [];
      const chronoPosition = chronoSequence.indexOf(mandala) + 1 || undefined;

      return {
        reference,
        text,
        mandala,
        hymn,
        verse,
        chronologicalPosition: chronoPosition,
        vedaId: metadata.id,
      } as Verse;
    })
    .filter(Boolean) as Verse[];

  return verses;
}

async function loadAtharvavedaJson(): Promise<Verse[]> {
  const response = await fetch('./atharvaveda.json');
  const verses = await response.json();
  return verses as Verse[];
}

async function loadRigvedaJson(): Promise<Verse[]> {
  const response = await fetch('./rigveda.json');
  const verses = await response.json();
  return verses as Verse[];
}

async function loadYajurvedaBlackJson(): Promise<Verse[]> {
  const response = await fetch('./yajurveda_black.json');
  const verses = await response.json();
  return verses as Verse[];
}

async function loadYajurvedaWhiteJson(): Promise<Verse[]> {
  const response = await fetch('./yajurveda_white.json');
  const verses = await response.json();
  return verses as Verse[];
}

// Keep old parser as fallback
function parseAtharvavedaText(text: string): Verse[] {
  const metadata = VEDA_CONFIGS.atharvaveda;
  const lines = text.split(/\r?\n/);
  const verses: Verse[] = [];
  const verseRegex = /^\s*\[(\d{2})(\d{3})(\d{2,3})\](.*)$/;

  let currentVerse: Verse | null = null;
  let currentParts: string[] = [];

  const resetCurrent = () => {
    finalizeVerse(currentVerse, currentParts, verses);
    currentVerse = null;
    currentParts = [];
  };

  const appendPart = (value: string) => {
    if (!value) return;
    if (currentParts.length > 0) {
      const lastIdx = currentParts.length - 1;
      const previous = currentParts[lastIdx];
      if (previous.endsWith("-")) {
        currentParts[lastIdx] = `${previous.slice(0, -1)}${value.replace(
          /^\s+/,
          ""
        )}`;
        return;
      }
    }
    currentParts.push(value);
  };

  for (const rawLine of lines) {
    const match = rawLine.match(verseRegex);

    if (match) {
      resetCurrent();

      const [, mandalaStr, hymnStr, verseStr, textPart] = match;
      const mandalaNum = parseInt(mandalaStr, 10);
      const hymnNum = parseInt(hymnStr, 10);
      const verseNum = parseInt(verseStr, 10);

      currentVerse = {
        reference: createReference(mandalaStr, hymnStr, verseStr),
        text: "",
        mandala: mandalaNum,
        hymn: hymnNum,
        verse: verseNum,
        vedaId: metadata.id,
      };

      const trimmed = textPart.trim();
      if (trimmed) {
        appendPart(trimmed);
      }
      continue;
    }

    if (!currentVerse) {
      continue;
    }

    const trimmedLine = rawLine.trim();

    if (!trimmedLine) {
      resetCurrent();
      continue;
    }

    if (/^\[p\.\s*/i.test(trimmedLine)) {
      continue;
    }

    if (/^(HYMN|BOOK)\b/i.test(trimmedLine)) {
      resetCurrent();
      continue;
    }

    if (/^Hymns of the Atharva Veda/i.test(trimmedLine)) {
      continue;
    }

    appendPart(trimmedLine);
  }

  resetCurrent();
  return verses;
}

export async function loadVedaData(vedaId: VedaId): Promise<Verse[]> {
  try {
    if (vedaId === "rigveda") {
      // Load pre-processed JSON with bilingual support (fast!)
      try {
        const verses = await loadRigvedaJson();
        console.log(`Loaded ${verses.length} Rigveda verses from JSON`);
        return verses;
      } catch {
        console.warn('Failed to load rigveda.json, falling back to griffith.csv');

        // Fallback to griffith.csv if JSON loading fails
        const response = await fetch("./griffith.csv");
        const text = await response.text();
        return parseRigvedaCSV(text);
      }
    }

    if (vedaId === "atharvaveda") {
      // Load pre-processed JSON (fast!)
      try {
        const verses = await loadAtharvavedaJson();
        console.log(`Loaded ${verses.length} Atharvaveda verses from JSON`);
        return verses;
      } catch {
        console.warn('Failed to load JSON, falling back to av.txt');

        // Fallback to av.txt if JSON loading fails
        const response = await fetch("./av.txt");
        const text = await response.text();
        return parseAtharvavedaText(text);
      }
    }

    if (vedaId === "yajurveda_black") {
      const verses = await loadYajurvedaBlackJson();
      console.log(`Loaded ${verses.length} Krishna Yajurveda verses from JSON`);
      return verses;
    }

    if (vedaId === "yajurveda_white") {
      const verses = await loadYajurvedaWhiteJson();
      console.log(`Loaded ${verses.length} Shukla Yajurveda verses from JSON`);
      return verses;
    }

    console.warn(`Unsupported vedaId "${vedaId}" supplied to loadVedaData`);
    return [];
  } catch (error) {
    console.error(`Error loading ${vedaId} data:`, error);
    return [];
  }
}

export function searchWord(
  verses: Verse[],
  searchTerms: string[],
  metadata: VedaMetadata,
  caseSensitive: boolean = false
): SearchResult | null {
  if (!searchTerms.length || !verses.length) return null;

  // Normalize search terms
  const normalizedSearchTerms = searchTerms.map((term) => normalizeText(term));

  // Find matching verses using normalized comparison
  const matches = verses.filter((verse) => {
    const normalizedVerseText = normalizeText(verse.text);

    // Check if any of the normalized search terms appear in the normalized verse
    return normalizedSearchTerms.some((term) => {
      if (caseSensitive) {
        // For case-sensitive, still use normalization but preserve case
        const regex = new RegExp(
          `\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`,
          "g"
        );
        return regex.test(normalizedVerseText);
      } else {
        // Case-insensitive search with normalization
        const regex = new RegExp(
          `\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`,
          "gi"
        );
        return regex.test(normalizedVerseText);
      }
    });
  });

  if (matches.length === 0) return null;

  // Count by mandala
  const divisionCount = metadata.totalBooks;
  const mandalaCounts = new Array(divisionCount).fill(0);
  const mandalaSizes = new Array(divisionCount).fill(0);

  verses.forEach((verse) => {
    const idx = verse.mandala - 1;
    if (idx >= 0 && idx < divisionCount) {
      mandalaSizes[idx]++;
    }
  });

  matches.forEach((verse) => {
    const idx = verse.mandala - 1;
    if (idx >= 0 && idx < divisionCount) {
      mandalaCounts[idx]++;
    }
  });

  // Calculate percentages
  const mandalaPercentages = mandalaCounts.map((count, idx) => {
    const size = mandalaSizes[idx];
    return size > 0 ? (count / size) * 100 : 0;
  });

  return {
    word: searchTerms.join(", "),
    totalMatches: matches.length,
    mandalaCounts,
    mandalaPercentages,
    mandalaSizes,
    matches: matches, // Return all matches
  };
}
