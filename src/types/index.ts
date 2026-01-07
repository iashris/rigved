export type VedaId =
  | "rigveda"
  | "atharvaveda"
  | "yajurveda_black"
  | "yajurveda_white"
  | "satapatha_brahmana"
  | "jaiminiya_brahmana";

export interface Verse {
  reference: string;
  text: string;
  mandala: number; // Mandala for Rigveda, Book for Atharvaveda
  hymn: number;
  verse: number;
  chronologicalPosition?: number;
  meaning?: string;
  iast?: string;
  vedaId: VedaId;
}

export interface SearchResult {
  word: string;
  totalMatches: number;
  mandalaCounts: number[];
  mandalaPercentages: number[];
  mandalaSizes: number[];
  matches: Verse[];
}

export type OrderType = "sequential" | "chronological";
export type DisplayMode = "absolute" | "percentage";

export interface VedaMetadata {
  id: VedaId;
  name: string;
  bookLabel: string;
  pluralBookLabel: string;
  shortLabel: string;
  hymnLabel: string;
  verseLabel: string;
  hasThirdLevel: boolean; // Whether this Veda uses all three levels (mandala/hymn/verse)
  totalBooks: number;
  sequentialOrder: number[];
  chronologicalOrder?: number[];
  chronologicalDescription?: string;
  dataSource: string;
  chronologyAttribution?: string;
}

const range = (count: number) =>
  Array.from({ length: count }, (_, idx) => idx + 1);

export const VEDA_CONFIGS: Record<VedaId, VedaMetadata> = {
  rigveda: {
    id: "rigveda",
    name: "Rigveda",
    bookLabel: "Mandala",
    pluralBookLabel: "Mandalas",
    shortLabel: "M",
    hymnLabel: "Hymn",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 10,
    sequentialOrder: range(10),
    chronologicalOrder: [6, 3, 7, 4, 2, 5, 8, 9, 1, 10],
    chronologicalDescription: "Chronological (Talegeri)",
    dataSource: "Griffith's translation of the Rigveda",
    chronologyAttribution: "Chronological order based on Talegeri's analysis",
  },
  atharvaveda: {
    id: "atharvaveda",
    name: "Atharvaveda",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "B",
    hymnLabel: "Hymn",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 20,
    sequentialOrder: range(20),
    dataSource: "Griffith's translation of the Atharvaveda",
  },
  yajurveda_black: {
    id: "yajurveda_black",
    name: "Yajurveda (Krishna)",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Prapathaka",
    verseLabel: "Anuvaka",
    hasThirdLevel: true,
    totalBooks: 7,
    sequentialOrder: range(7),
    dataSource: "Krishna Yajurveda (Taittiriya Samhita)",
  },
  yajurveda_white: {
    id: "yajurveda_white",
    name: "Yajurveda (Shukla)",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Mantra",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 40,
    sequentialOrder: range(40),
    dataSource: "Shukla Yajurveda (Vajasaneyi Samhita)",
  },
  satapatha_brahmana: {
    id: "satapatha_brahmana",
    name: "Satapatha Brahmana",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Brahmana",
    verseLabel: "Verse",
    hasThirdLevel: false,
    totalBooks: 14,
    sequentialOrder: range(14),
    dataSource: "Julius Eggeling's translation of the Satapatha Brahmana",
  },
  jaiminiya_brahmana: {
    id: "jaiminiya_brahmana",
    name: "Jaiminiya Brahmana",
    bookLabel: "Book",
    pluralBookLabel: "Books",
    shortLabel: "B",
    hymnLabel: "Khanda",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 3,
    sequentialOrder: [1, 2, 3],
    dataSource: "Jaiminiya Brāhmaṇa (TITUS Project)",
  },
};
