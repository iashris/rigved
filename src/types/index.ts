export type VedaId = 'rigveda' | 'atharvaveda';

export interface Verse {
  reference: string;
  text: string;
  mandala: number; // Mandala for Rigveda, Book for Atharvaveda
  hymn: number;
  verse: number;
  chronologicalPosition?: number;
  meaning?: string;
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

export type OrderType = 'sequential' | 'chronological';
export type DisplayMode = 'absolute' | 'percentage';

export interface VedaMetadata {
  id: VedaId;
  name: string;
  bookLabel: string;
  pluralBookLabel: string;
  shortLabel: string;
  totalBooks: number;
  sequentialOrder: number[];
  chronologicalOrder?: number[];
  chronologicalDescription?: string;
  dataSource: string;
  chronologyAttribution?: string;
}

const range = (count: number) => Array.from({ length: count }, (_, idx) => idx + 1);

export const VEDA_CONFIGS: Record<VedaId, VedaMetadata> = {
  rigveda: {
    id: 'rigveda',
    name: 'Rigveda',
    bookLabel: 'Mandala',
    pluralBookLabel: 'Mandalas',
    shortLabel: 'M',
    totalBooks: 10,
    sequentialOrder: range(10),
    chronologicalOrder: [6, 3, 7, 4, 2, 5, 8, 9, 1, 10],
    chronologicalDescription: 'Chronological (Talegeri)',
    dataSource: "Griffith's translation of the Rigveda",
    chronologyAttribution: "Chronological order based on Talegeri's analysis",
  },
  atharvaveda: {
    id: 'atharvaveda',
    name: 'Atharvaveda',
    bookLabel: 'Book',
    pluralBookLabel: 'Books',
    shortLabel: 'B',
    totalBooks: 20,
    sequentialOrder: range(20),
    dataSource: "Griffith's translation of the Atharvaveda",
  },
};
