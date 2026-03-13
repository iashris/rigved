import type { Verse, SearchResult, VedaId, VedaMetadata } from "../types";
import { VEDA_CONFIGS } from "../types";

// Normalize text by removing diacritics and special characters
function normalizeText(text: string): string {
  const replacements: Record<string, string> = {
    ā: "a", Ā: "A", ī: "i", Ī: "I", ū: "u", Ū: "U",
    ṛ: "r", Ṛ: "R", ṝ: "r", Ṝ: "R", ḷ: "l", Ḷ: "L", ḹ: "l", Ḹ: "L",
    ṃ: "m", Ṃ: "M", ḥ: "h", Ḥ: "H",
    ṅ: "n", Ṅ: "N", ñ: "n", Ñ: "N",
    ṭ: "t", Ṭ: "T", ḍ: "d", Ḍ: "D", ṇ: "n", Ṇ: "N",
    ś: "s", Ś: "S", ṣ: "s", Ṣ: "S",
    ẓ: "z", Ẓ: "Z", ḻ: "l", Ḻ: "L",
    â: "a", Â: "A", î: "i", Î: "I", û: "u", Û: "U",
    ê: "e", Ê: "E", ô: "o", Ô: "O",
    ṁ: "m", ḿ: "m", Ḿ: "M",
  };

  let normalized = text;
  for (const [diacritic, replacement] of Object.entries(replacements)) {
    normalized = normalized.replace(new RegExp(diacritic, "g"), replacement);
  }

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

// ==========================================
// Generic JSON loader for all texts
// ==========================================

async function loadGenericJson(vedaId: VedaId): Promise<Verse[]> {
  const config = VEDA_CONFIGS[vedaId];
  const response = await fetch(`./${config.dataPath}`);
  const rawData = await response.json();

  const verses: Verse[] = rawData.map((item: Record<string, unknown>) => ({
    reference: item.reference as string || '',
    text: (item.text as string) || '',
    mandala: (item.mandala as number) || (item.chapter as number) || 0,
    hymn: (item.hymn as number) || (item.khanda as number) || 0,
    verse: (item.verse as number) || 1,
    iast: (item.sanskrit_iast as string) || (item.iast as string) || '',
    meaning: (item.meaning as string) || '',
    vedaId: vedaId,
  }));

  return verses;
}

// ==========================================
// Legacy fallback parsers
// ==========================================

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

// ==========================================
// Main loader
// ==========================================

export async function loadVedaData(vedaId: VedaId): Promise<Verse[]> {
  try {
    // Try the generic JSON loader first (works for all texts)
    try {
      const verses = await loadGenericJson(vedaId);
      console.log(`Loaded ${verses.length} ${VEDA_CONFIGS[vedaId].name} entries from JSON`);
      return verses;
    } catch (jsonError) {
      console.warn(`Failed to load ${vedaId} JSON, trying fallback...`, jsonError);
    }

    // Legacy fallbacks for Rigveda and Atharvaveda
    if (vedaId === "rigveda") {
      const response = await fetch("./data/other/griffith.csv");
      const text = await response.text();
      return parseRigvedaCSV(text);
    }

    if (vedaId === "atharvaveda") {
      const response = await fetch("./data/other/av.txt");
      const text = await response.text();
      return parseAtharvavedaText(text);
    }

    console.warn(`No fallback available for "${vedaId}"`);
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

  const normalizedSearchTerms = searchTerms.map((term) => normalizeText(term));

  const matches = verses.filter((verse) => {
    const normalizedVerseText = normalizeText(verse.text);
    const normalizedIast = verse.iast ? normalizeText(verse.iast) : '';
    const normalizedMeaning = verse.meaning ? normalizeText(verse.meaning) : '';

    return normalizedSearchTerms.some((term) => {
      const flags = caseSensitive ? "g" : "gi";
      const regex = new RegExp(
        `\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`,
        flags
      );
      return regex.test(normalizedVerseText) || regex.test(normalizedIast) || regex.test(normalizedMeaning);
    });
  });

  if (matches.length === 0) return null;

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
    matches: matches,
  };
}
