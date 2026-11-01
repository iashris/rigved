// Reader data: the catalog and per-text chunks produced by scripts/corpus2/build_library.py.

export interface Entry {
  r: string; // reference, e.g. "1.32.5"
  s?: string; // IAST
  d?: string; // Devanagari
  e?: string; // English
  m?: string; // machine translation (labelled as such wherever shown)
  t?: string; // heading (translation sections)
}

/** [key, entries, chunk, heading] at block level; [key, entries, children] above it. */
export type TocNode = [string, number, number, string] | [string, number, TocNode[]];

export interface Pair {
  with: string;
  mode: 'aligned' | 'prefix' | 'concordance';
  label: string;
  available?: boolean;
}

export interface TextMeta {
  id: string;
  name: string;
  veda?: string;
  layer?: string;
  band?: string;
  later?: boolean;
  translationOf?: string;
  levels: string[];
  source?: string;
  pairs?: Pair[];
  blockDepth: number;
  stats: { entries: number; blocks: number; english: number; machine?: number; sanskrit: number; chunks: number };
  toc: TocNode[];
}

export interface Group {
  id: string;
  name: string;
  deva?: string;
  blurb: string;
}

export interface Catalog {
  vedas: Group[];
  layers: Group[];
  bands: Group[];
  texts: TextMeta[];
}

export interface Concordance {
  source: string;
  translation: string;
  map: Record<string, { ref: string; score: number }[]>;
  stats?: Record<string, number>;
  method?: string;
}

const BASE = './library';
const cache = new Map<string, Promise<unknown>>();

function getJson<T>(url: string): Promise<T> {
  if (!cache.has(url)) {
    cache.set(
      url,
      fetch(url).then((r) => {
        if (!r.ok) throw new Error(`${url}: ${r.status}`);
        return r.json();
      }),
    );
  }
  return cache.get(url) as Promise<T>;
}

export const loadCatalog = () => getJson<Catalog>(`${BASE}/catalog.json`);

export const isBlock = (n: TocNode): n is [string, number, number, string] => typeof n[2] === 'number';

/** Every block key in text order, with its chunk. */
export function blockList(t: TextMeta): { key: string; chunk: number; heading: string }[] {
  const out: { key: string; chunk: number; heading: string }[] = [];
  const walk = (nodes: TocNode[]) => {
    for (const n of nodes) {
      if (isBlock(n)) out.push({ key: n[0], chunk: n[2], heading: n[3] });
      else walk(n[2]);
    }
  };
  walk(t.toc);
  return out;
}

const blockIndex = new Map<string, Map<string, number>>();

export async function loadBlock(t: TextMeta, key: string): Promise<Entry[] | null> {
  let idx = blockIndex.get(t.id);
  if (!idx) {
    idx = new Map(blockList(t).map((b) => [b.key, b.chunk]));
    blockIndex.set(t.id, idx);
  }
  const chunk = idx.get(key);
  if (chunk === undefined) return null;
  const data = await getJson<Record<string, Entry[]>>(`${BASE}/texts/${t.id}/${chunk}.json`);
  return data[key] ?? null;
}

export const loadConcordance = (source: string, translation: string) =>
  getJson<Concordance>(`${BASE}/concordance/${source}__${translation}.json`);

/** "Maṇḍala 1 · Sūkta 32" for a block key. */
export function blockLabel(t: TextMeta, key: string): string {
  if (!key) return t.name;
  return key
    .split('.')
    .map((p, i) => `${t.levels[i] ?? ''} ${p}`.trim())
    .join(' · ');
}

/** The ref of an entry shown inside its block: the levels below the block. */
export const localRef = (t: TextMeta, r: string) => r.split('.').slice(t.blockDepth).join('.') || r;
