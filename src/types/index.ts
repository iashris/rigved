export type VedaId =
  // Samhitas
  | "rigveda"
  | "samaveda"
  | "atharvaveda"
  | "yajurveda_black"
  | "yajurveda_white"
  | "taittiriya_samhita"
  | "vajasaneyi_samhita"
  | "rgveda_khilani"
  // Brahmanas
  | "satapatha_brahmana"
  | "jaiminiya_brahmana"
  | "aitareya_brahmana"
  | "taittiriya_brahmana"
  | "kausitaki_brahmana"
  | "pancavimsa_brahmana"
  | "gopatha_brahmana"
  // Aranyakas
  | "aitareya_aranyaka"
  | "taittiriya_aranyaka"
  // Upanishads
  | "isha_upanishad"
  | "kena_upanishad"
  | "katha_upanishad"
  | "mundaka_upanishad"
  | "mandukya_upanishad"
  | "prasna_upanishad"
  | "taittiriya_upanishad"
  | "aitareya_upanishad"
  | "svetasvatara_upanishad"
  | "chandogya_upanishad"
  | "brhadaranyaka_upanishad"
  | "kausitaki_upanishad"
  // Epics & Smritis
  | "ramayana"
  | "manu_smrti";

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
  category: "samhita" | "brahmana" | "aranyaka" | "upanishad" | "epic";
  bookLabel: string;
  pluralBookLabel: string;
  shortLabel: string;
  hymnLabel: string;
  verseLabel: string;
  hasThirdLevel: boolean;
  totalBooks: number;
  sequentialOrder: number[];
  chronologicalOrder?: number[];
  chronologicalDescription?: string;
  dataSource: string;
  chronologyAttribution?: string;
  dataPath: string; // Path relative to public/
}

const range = (count: number) =>
  Array.from({ length: count }, (_, idx) => idx + 1);

export const VEDA_CONFIGS: Record<VedaId, VedaMetadata> = {
  // ===================== SAMHITAS =====================
  rigveda: {
    id: "rigveda",
    name: "Rigveda",
    category: "samhita",
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
    dataPath: "data/vedas/rigveda.json",
  },
  samaveda: {
    id: "samaveda",
    name: "Samaveda",
    category: "samhita",
    bookLabel: "Book",
    pluralBookLabel: "Books",
    shortLabel: "B",
    hymnLabel: "Section",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 15,
    sequentialOrder: range(15),
    dataSource: "Griffith's translation with Sanskrit from TITUS",
    dataPath: "data/vedas/samaveda.json",
  },
  atharvaveda: {
    id: "atharvaveda",
    name: "Atharvaveda",
    category: "samhita",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "B",
    hymnLabel: "Hymn",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 20,
    sequentialOrder: range(20),
    dataSource: "Griffith's translation of the Atharvaveda",
    dataPath: "data/vedas/atharvaveda.json",
  },
  yajurveda_black: {
    id: "yajurveda_black",
    name: "Yajurveda (Krishna)",
    category: "samhita",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Prapathaka",
    verseLabel: "Anuvaka",
    hasThirdLevel: true,
    totalBooks: 7,
    sequentialOrder: range(7),
    dataSource: "Krishna Yajurveda (Taittiriya Samhita)",
    dataPath: "data/vedas/yajurveda_black.json",
  },
  yajurveda_white: {
    id: "yajurveda_white",
    name: "Yajurveda (Shukla)",
    category: "samhita",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Mantra",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 40,
    sequentialOrder: range(40),
    dataSource: "Shukla Yajurveda (Vajasaneyi Samhita)",
    dataPath: "data/vedas/yajurveda_white.json",
  },
  taittiriya_samhita: {
    id: "taittiriya_samhita",
    name: "Taittiriya Samhita",
    category: "samhita",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Prapathaka",
    verseLabel: "Anuvaka",
    hasThirdLevel: true,
    totalBooks: 7,
    sequentialOrder: range(7),
    dataSource: "TITUS Project (Weber edition)",
    dataPath: "data/vedas/taittiriya_samhita.json",
  },
  vajasaneyi_samhita: {
    id: "vajasaneyi_samhita",
    name: "Vajasaneyi Samhita",
    category: "samhita",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 40,
    sequentialOrder: range(40),
    dataSource: "TITUS Project (Weber edition)",
    dataPath: "data/vedas/vajasaneyi_samhita.json",
  },
  rgveda_khilani: {
    id: "rgveda_khilani",
    name: "Rigveda Khilani",
    category: "samhita",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Hymn",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 5,
    sequentialOrder: range(5),
    dataSource: "TITUS Project (Scheftelowitz edition)",
    dataPath: "data/vedas/rgveda_khilani.json",
  },

  // ===================== BRAHMANAS =====================
  satapatha_brahmana: {
    id: "satapatha_brahmana",
    name: "Satapatha Brahmana",
    category: "brahmana",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Brahmana",
    verseLabel: "Verse",
    hasThirdLevel: false,
    totalBooks: 14,
    sequentialOrder: range(14),
    dataSource: "Julius Eggeling's translation",
    dataPath: "data/brahmanas/satapatha_brahmana.json",
  },
  jaiminiya_brahmana: {
    id: "jaiminiya_brahmana",
    name: "Jaiminiya Brahmana",
    category: "brahmana",
    bookLabel: "Book",
    pluralBookLabel: "Books",
    shortLabel: "B",
    hymnLabel: "Khanda",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 3,
    sequentialOrder: [1, 2, 3],
    dataSource: "TITUS Project",
    dataPath: "data/brahmanas/jaiminiya_brahmana.json",
  },
  aitareya_brahmana: {
    id: "aitareya_brahmana",
    name: "Aitareya Brahmana",
    category: "brahmana",
    bookLabel: "Panchika",
    pluralBookLabel: "Panchikas",
    shortLabel: "P",
    hymnLabel: "Adhyaya",
    verseLabel: "Paragraph",
    hasThirdLevel: true,
    totalBooks: 8,
    sequentialOrder: range(8),
    dataSource: "TITUS Project (Aufrecht edition)",
    dataPath: "data/brahmanas/aitareya_brahmana.json",
  },
  taittiriya_brahmana: {
    id: "taittiriya_brahmana",
    name: "Taittiriya Brahmana",
    category: "brahmana",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Prapathaka",
    verseLabel: "Anuvaka",
    hasThirdLevel: true,
    totalBooks: 3,
    sequentialOrder: range(3),
    dataSource: "TITUS Project (Fushimi edition)",
    dataPath: "data/brahmanas/taittiriya_brahmana.json",
  },
  kausitaki_brahmana: {
    id: "kausitaki_brahmana",
    name: "Kausitaki Brahmana",
    category: "brahmana",
    bookLabel: "Book",
    pluralBookLabel: "Books",
    shortLabel: "B",
    hymnLabel: "Chapter",
    verseLabel: "Paragraph",
    hasThirdLevel: true,
    totalBooks: 30,
    sequentialOrder: range(30),
    dataSource: "TITUS Project (Sreekrishna Sarma edition)",
    dataPath: "data/brahmanas/kausitaki_brahmana.json",
  },
  pancavimsa_brahmana: {
    id: "pancavimsa_brahmana",
    name: "Pancavimsa Brahmana",
    category: "brahmana",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Khanda",
    verseLabel: "Paragraph",
    hasThirdLevel: true,
    totalBooks: 25,
    sequentialOrder: range(25),
    dataSource: "TITUS Project (Kümmel/Griffiths edition)",
    dataPath: "data/brahmanas/pancavimsa_brahmana.json",
  },
  gopatha_brahmana: {
    id: "gopatha_brahmana",
    name: "Gopatha Brahmana",
    category: "brahmana",
    bookLabel: "Bhaga",
    pluralBookLabel: "Bhagas",
    shortLabel: "B",
    hymnLabel: "Prapathaka",
    verseLabel: "Khanda",
    hasThirdLevel: true,
    totalBooks: 2,
    sequentialOrder: [1, 2],
    dataSource: "TITUS Project (Gaastra edition)",
    dataPath: "data/brahmanas/gopatha_brahmana.json",
  },

  // ===================== ARANYAKAS =====================
  aitareya_aranyaka: {
    id: "aitareya_aranyaka",
    name: "Aitareya Aranyaka",
    category: "aranyaka",
    bookLabel: "Aranyaka",
    pluralBookLabel: "Aranyakas",
    shortLabel: "A",
    hymnLabel: "Adhyaya",
    verseLabel: "Khanda",
    hasThirdLevel: true,
    totalBooks: 5,
    sequentialOrder: range(5),
    dataSource: "TITUS Project (Keith edition)",
    dataPath: "data/aranyakas/aitareya_aranyaka.json",
  },
  taittiriya_aranyaka: {
    id: "taittiriya_aranyaka",
    name: "Taittiriya Aranyaka",
    category: "aranyaka",
    bookLabel: "Prapathaka",
    pluralBookLabel: "Prapathakas",
    shortLabel: "P",
    hymnLabel: "Anuvaka",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 10,
    sequentialOrder: range(10),
    dataSource: "TITUS Project",
    dataPath: "data/aranyakas/taittiriya_aranyaka.json",
  },

  // ===================== UPANISHADS =====================
  isha_upanishad: {
    id: "isha_upanishad",
    name: "Isha Upanishad",
    category: "upanishad",
    bookLabel: "Verse",
    pluralBookLabel: "Verses",
    shortLabel: "V",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 1,
    sequentialOrder: [1],
    dataSource: "upanishads.org.in (Sri Aurobindo translation)",
    dataPath: "data/upanishads/isha_upanishad.json",
  },
  kena_upanishad: {
    id: "kena_upanishad",
    name: "Kena Upanishad",
    category: "upanishad",
    bookLabel: "Khanda",
    pluralBookLabel: "Khandas",
    shortLabel: "K",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 4,
    sequentialOrder: range(4),
    dataSource: "upanishads.org.in (Sri Aurobindo translation)",
    dataPath: "data/upanishads/kena_upanishad.json",
  },
  katha_upanishad: {
    id: "katha_upanishad",
    name: "Katha Upanishad",
    category: "upanishad",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Valli",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 2,
    sequentialOrder: [1, 2],
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/katha_upanishad.json",
  },
  mundaka_upanishad: {
    id: "mundaka_upanishad",
    name: "Mundaka Upanishad",
    category: "upanishad",
    bookLabel: "Mundaka",
    pluralBookLabel: "Mundakas",
    shortLabel: "M",
    hymnLabel: "Khanda",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 3,
    sequentialOrder: range(3),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/mundaka_upanishad.json",
  },
  mandukya_upanishad: {
    id: "mandukya_upanishad",
    name: "Mandukya Upanishad",
    category: "upanishad",
    bookLabel: "Verse",
    pluralBookLabel: "Verses",
    shortLabel: "V",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 1,
    sequentialOrder: [1],
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/mandukya_upanishad.json",
  },
  prasna_upanishad: {
    id: "prasna_upanishad",
    name: "Prasna Upanishad",
    category: "upanishad",
    bookLabel: "Prasna",
    pluralBookLabel: "Prasnas",
    shortLabel: "P",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 6,
    sequentialOrder: range(6),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/prasna_upanishad.json",
  },
  taittiriya_upanishad: {
    id: "taittiriya_upanishad",
    name: "Taittiriya Upanishad",
    category: "upanishad",
    bookLabel: "Valli",
    pluralBookLabel: "Vallis",
    shortLabel: "V",
    hymnLabel: "Anuvaka",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 3,
    sequentialOrder: range(3),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/taittiriya_upanishad.json",
  },
  aitareya_upanishad: {
    id: "aitareya_upanishad",
    name: "Aitareya Upanishad",
    category: "upanishad",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 5,
    sequentialOrder: range(5),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/aitareya_upanishad.json",
  },
  svetasvatara_upanishad: {
    id: "svetasvatara_upanishad",
    name: "Svetasvatara Upanishad",
    category: "upanishad",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 6,
    sequentialOrder: range(6),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/svetasvatara_upanishad.json",
  },
  chandogya_upanishad: {
    id: "chandogya_upanishad",
    name: "Chandogya Upanishad",
    category: "upanishad",
    bookLabel: "Prapathaka",
    pluralBookLabel: "Prapathakas",
    shortLabel: "P",
    hymnLabel: "Khanda",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 8,
    sequentialOrder: range(8),
    dataSource: "upanishads.org.in",
    dataPath: "data/upanishads/chandogya_upanishad.json",
  },
  brhadaranyaka_upanishad: {
    id: "brhadaranyaka_upanishad",
    name: "Brhadaranyaka Upanishad",
    category: "upanishad",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Brahmana",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 6,
    sequentialOrder: range(6),
    dataSource: "TITUS Project (Madhyandina recension)",
    dataPath: "data/upanishads/brhadaranyaka_upanishad.json",
  },
  kausitaki_upanishad: {
    id: "kausitaki_upanishad",
    name: "Kausitaki Upanishad",
    category: "upanishad",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Khanda",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 4,
    sequentialOrder: range(4),
    dataSource: "TITUS Project (Ježić edition)",
    dataPath: "data/upanishads/kausitaki_upanishad.json",
  },

  // ===================== EPICS & SMRITIS =====================
  ramayana: {
    id: "ramayana",
    name: "Ramayana",
    category: "epic",
    bookLabel: "Kanda",
    pluralBookLabel: "Kandas",
    shortLabel: "K",
    hymnLabel: "Sarga",
    verseLabel: "Verse",
    hasThirdLevel: true,
    totalBooks: 7,
    sequentialOrder: range(7),
    dataSource: "TITUS Project (Baroda critical edition)",
    dataPath: "data/epics/ramayana.json",
  },
  manu_smrti: {
    id: "manu_smrti",
    name: "Manu Smrti",
    category: "epic",
    bookLabel: "Adhyaya",
    pluralBookLabel: "Adhyayas",
    shortLabel: "A",
    hymnLabel: "Verse",
    verseLabel: "",
    hasThirdLevel: false,
    totalBooks: 12,
    sequentialOrder: range(12),
    dataSource: "TITUS Project (Yano/Ikari edition)",
    dataPath: "data/epics/manu_smrti.json",
  },
};
