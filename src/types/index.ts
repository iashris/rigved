export interface Verse {
  reference: string;
  text: string;
  mandala: number;
  hymn: number;
  verse: number;
  chronologicalPosition?: number;
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

export const CHRONOLOGICAL_ORDER = [6, 3, 7, 4, 2, 5, 8, 9, 1, 10];
export const SEQUENTIAL_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];