import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, Headphones, List, Type, X } from 'lucide-react';
import type { Catalog, Concordance, Entry, HymnAbout, Original, Pair, SourceLink, TextMeta, TocNode, TranslationCredit } from './data';
import { blockLabel, blockList, isBlock, loadBlock, loadConcordance, localRef, paragraphs } from './data';
import { readHref } from './route';
import NarratorBar from './Narrator';
import { speechSupported, useNarrator, type NarrationItem } from './useNarrator';

type Show = { iast: boolean; deva: boolean; english: boolean };

function usePersisted<T>(key: string, initial: T): [T, (v: T) => void] {
  const [v, setV] = useState<T>(() => {
    try {
      const s = localStorage.getItem(key);
      return s ? { ...initial, ...JSON.parse(s) } : initial;
    } catch {
      return initial;
    }
  });
  const set = (x: T) => {
    setV(x);
    try {
      localStorage.setItem(key, JSON.stringify(x));
    } catch {
      /* storage unavailable: keep the in-memory value */
    }
  };
  return [v, set];
}

/** Phones and narrow tablets, where the reader drops its side-by-side panes for one column on the page's own scroll. */
const NARROW = '(max-width: 900px)';

function useNarrow() {
  const [narrow, setNarrow] = useState(() => window.matchMedia(NARROW).matches);
  useEffect(() => {
    const mq = window.matchMedia(NARROW);
    const on = () => setNarrow(mq.matches);
    mq.addEventListener('change', on);
    return () => mq.removeEventListener('change', on);
  }, []);
  return narrow;
}

const ALL_SANSKRIT: Show = { deva: true, iast: true, english: true };

function Toc({ t, nodes, current, withId, depth = 1 }: { t: TextMeta; nodes: TocNode[]; current: string; withId?: string; depth?: number }) {
  return (
    <ul className="toc-list">
      {nodes.map((n) => {
        const key = n[0];
        const label = `${t.levels[depth - 1] ?? ''} ${key.split('.').pop()}`;
        if (isBlock(n)) {
          return (
            <li key={key}>
              <a className={`toc-leaf${key === current ? ' active' : ''}`} href={readHref(t.id, key, { with: withId })}>
                {label}
                {n[3] && <span className="toc-heading">{n[3]}</span>}
              </a>
            </li>
          );
        }
        return <TocBranch key={key} t={t} node={n} label={label} current={current} withId={withId} depth={depth} />;
      })}
    </ul>
  );
}

function TocBranch({ t, node, label, current, withId, depth }: { t: TextMeta; node: [string, number, TocNode[]]; label: string; current: string; withId?: string; depth: number }) {
  const inside = current === node[0] || current.startsWith(`${node[0]}.`);
  const [open, setOpen] = useState(inside);
  useEffect(() => {
    if (inside) setOpen(true);
  }, [inside]);
  return (
    <li>
      <button className={`toc-branch${inside ? ' inside' : ''}`} onClick={() => setOpen(!open)} aria-expanded={open}>
        <ChevronDown size={14} className={open ? '' : 'rot'} />
        {label}
        <span className="toc-count">{node[2].length}</span>
      </button>
      {open && <Toc t={t} nodes={node[2]} current={current} withId={withId} depth={depth + 1} />}
    </li>
  );
}

/** `idPrefix` gives each paragraph an id (prefix-p0, -p1…) for the audiobook to highlight. `lines` keeps a verse
 * translation's half-verse breaks; other English carries hard line wraps from its source that should run on. */
const Paragraphs = ({ text, idPrefix, lines }: { text: string; idPrefix?: string; lines?: boolean }) => (
  <>
    {paragraphs(text).map((p, i) => (
      <p key={i} id={idPrefix ? `${idPrefix}-p${i}` : undefined} className={lines ? 'lines' : undefined}>
        {p}
      </p>
    ))}
  </>
);

/** "R. T. H. Griffith" + 1896 → "Griffith (1896)", for naming a text's own English beside its paired translations. */
function creditLabel(c?: TranslationCredit): string | undefined {
  if (!c) return undefined;
  const surname = c.by.split(/\s+and\s+|,/)[0].trim().split(/\s+/).pop();
  return c.year ? `${surname} (${c.year})` : surname;
}

/** One translation of one verse, as the reader shows it. */
interface Version {
  id: string;
  label: string;
  text?: string;
  lines?: boolean;
}

/** A hymn's notes from its translators: poet, meter, who translated it, and their introduction. Open or shut, it stays
 * that way from hymn to hymn. */
function HymnNotes({ about, deity, credit, preface, open, onToggle }: { about: HymnAbout; deity?: string; credit?: string; preface: string; open: boolean; onToggle: (o: boolean) => void }) {
  // The deity column also holds subjects ("Creation", "Praise of Ghee"), so it stands without a "To".
  const facts = [deity, about.poet && `by ${about.poet}`, about.meter].filter(Boolean).join(' · ');
  return (
    <details className="hymn-about" open={open} onToggle={(e) => onToggle(e.currentTarget.open)}>
      <summary>
        <ChevronDown size={15} className="hymn-about-chev" />
        <span className="hymn-about-title">About this hymn</span>
        <span className="hymn-about-facts">{facts}</span>
      </summary>
      <div className="hymn-about-body">
        {about.intro && <Paragraphs text={about.intro} />}
        {about.preface && (
          <details className="hymn-about-preface">
            <summary>{preface}</summary>
            <Paragraphs text={about.preface} />
          </details>
        )}
        <p className="hymn-about-credit">
          {about.by ? `Translated by ${about.by}` : ''}
          {about.by && credit ? '; notes from ' : credit ? 'Notes from ' : ''}
          {credit}
        </p>
      </div>
    </details>
  );
}

function EnglishCell({ versions, compare, machine, missing }: { versions: Version[]; compare: boolean; machine?: string; missing: boolean }): ReactNode {
  if (compare) {
    return (
      <div className="v-en v-compare">
        {versions.map((v) => (
          <div key={v.id} className="v-version">
            <span className="v-version-label">{v.label}</span>
            {v.text ? <Paragraphs text={v.text} lines={v.lines} /> : <span className="v-missing">No verse with this number in this translation</span>}
          </div>
        ))}
      </div>
    );
  }
  const v = versions[0];
  if (v?.text)
    return (
      <div className="v-en">
        <Paragraphs text={v.text} lines={v.lines} />
      </div>
    );
  if (machine)
    return (
      <div className="v-en v-mt">
        <span className="mt-label">Machine translation</span>
        <Paragraphs text={machine} />
      </div>
    );
  return missing ? <div className="v-en v-missing">—</div> : null;
}

/** The original of one verse: Sanskrit in Devanagari and IAST, or a comparative text's own language (`orig`). */
function SanskritCell({ e, show, englishOnly, renumbered, orig }: { e: Entry; show: Show; englishOnly?: boolean; renumbered?: boolean; orig?: Original }) {
  const lang = orig?.name ?? 'Sanskrit';
  return (
    <>
      {show.deva && e.d && <div className="v-deva" lang="sa-Deva">{e.d}</div>}
      {show.iast && e.s && (
        <div className={orig?.dir ? 'v-orig' : 'v-iast'} lang={orig?.lang ?? 'sa-Latn'} dir={orig?.dir}>
          {e.s}
        </div>
      )}
      {!e.s && !e.d && !englishOnly && (
        <div className="v-missing">{renumbered ? `This edition numbers the verses of this hymn differently; its ${lang} is above` : `No ${lang} in this edition`}</div>
      )}
    </>
  );
}

const OutLink = ({ link }: { link: SourceLink }) => (
  <a href={link.url} target="_blank" rel="noopener noreferrer">
    {link.label} ↗
  </a>
);

function Credit({ kind, c }: { kind: string; c: TranslationCredit }) {
  return (
    <p className="tr-credit-line">
      <strong>{kind}:</strong> {c.by}
      {c.work && (
        <>
          , <cite>{c.work}</cite>
        </>
      )}
      {c.year && ` (${c.year})`}
      {c.links?.map((l) => (
        <span key={l.url}>
          {' · '}
          <OutLink link={l} />
        </span>
      ))}
      {c.via && (
        <span>
          {' · via '}
          <OutLink link={c.via} />
        </span>
      )}
      {c.note && <span className="tr-credit-note"> {c.note}</span>}
    </p>
  );
}

/** Two panes that scroll together by proportion, for block-against-block reading. */
function useScrollSync() {
  const left = useRef<HTMLDivElement>(null);
  const right = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const a = left.current;
    const b = right.current;
    if (!a || !b) return;
    let lock: HTMLElement | null = null;
    const sync = (from: HTMLElement, to: HTMLElement) => () => {
      if (lock && lock !== from) return;
      lock = from;
      const f = from.scrollTop / Math.max(1, from.scrollHeight - from.clientHeight);
      to.scrollTop = f * (to.scrollHeight - to.clientHeight);
      requestAnimationFrame(() => (lock = null));
    };
    const ab = sync(a, b);
    const ba = sync(b, a);
    a.addEventListener('scroll', ab);
    b.addEventListener('scroll', ba);
    return () => {
      a.removeEventListener('scroll', ab);
      b.removeEventListener('scroll', ba);
    };
  });
  return { left, right };
}

export default function Reader({ catalog, textId, block, withId, verse }: { catalog: Catalog; textId: string; block: string; withId?: string; verse?: string }) {
  const t = catalog.texts.find((x) => x.id === textId);
  const narrow = useNarrow();
  // On a phone the English is what's read and the Sanskrit is there for reference, so it starts folded.
  const [showWide, setShowWide] = usePersisted<Show>('reader.show', { iast: true, deva: true, english: true });
  const [showNarrow, setShowNarrow] = usePersisted<Show>('reader.show.narrow', { iast: false, deva: false, english: true });
  const [chosen, setShow] = narrow ? [showNarrow, setShowNarrow] : [showWide, setShowWide];
  const [toolsOpen, setToolsOpen] = useState(false);
  const [peek, setPeek] = useState<Set<string>>(() => new Set());
  const [textSize, setTextSize] = usePersisted<{ step: number }>('reader.textSize', { step: 0 });
  const [tocOpen, setTocOpen] = useState(false);
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [entriesKey, setEntriesKey] = useState('');
  const [tr, setTr] = useState<{ meta: TextMeta; entries: Entry[]; refs: { ref: string; score: number }[]; offset: number; key: string } | null>(null);
  const [al, setAl] = useState<{ key: string; ids: string; byId: Record<string, Entry[]> } | null>(null);
  const [conc, setConc] = useState<Concordance | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState('');
  // The translation last chosen for each text, so the reader's pick holds across passages and visits.
  const [savedWith, setSavedWith] = usePersisted<Record<string, string>>('reader.with', {});
  const [notesOpen, setNotesOpen] = usePersisted<{ open: boolean }>('reader.hymnNotes', { open: false });
  const sync = useScrollSync();

  const blocks = useMemo(() => (t ? blockList(t) : []), [t]);
  const at = blocks.findIndex((b) => b.key === block);
  const key = at >= 0 ? block : (blocks[0]?.key ?? '');
  const pairs = useMemo(() => t?.pairs?.filter((p) => p.mode !== 'concordance' || p.available) ?? [], [t]);
  const aligned = useMemo(() => pairs.filter((p) => p.mode === 'aligned'), [pairs]);
  // A text with English of its own (the Ṛgveda's Griffith) offers it as one choice among its verse-aligned translations.
  const ownLabel = t && t.stats.english >= 50 && aligned.length ? creditLabel(t.translation?.english) : undefined;
  const canCompare = aligned.length + (ownLabel ? 1 : 0) >= 2;
  // ?with= wins, then the reader's last choice for this text. Left alone, a text with its own English shows it;
  // one without shows its first translation. ?with=none turns a translation pane off.
  const want = withId ?? (t ? savedWith[t.id] : undefined);
  const choice =
    want === 'all' && canCompare
      ? 'all'
      : want && pairs.some((p) => p.with === want)
        ? want
        : ownLabel
          ? 'own'
          : want === 'none'
            ? 'none'
            : (pairs[0]?.with ?? 'none');
  const pair = pairs.find((p) => p.with === choice);
  const compare = choice === 'all';
  const shownAligned: Pair[] = useMemo(() => (compare ? aligned : pair?.mode === 'aligned' ? [pair] : []), [compare, aligned, pair]);
  const alIds = shownAligned.map((p) => p.with).join(',');
  const parent = t?.translationOf ? catalog.texts.find((x) => x.id === t.translationOf) : undefined;
  const inlineEnglish = !!entries?.some((e) => e.e || e.m) && !!entries?.some((e) => e.s || e.d);

  useEffect(() => setOffset(0), [key, pair?.with]);
  // A passage this edition lacks but a verse-aligned translation has (Ṛgveda VIII.68–80, 92–103): open it there
  // rather than fall back to the first passage.
  useEffect(() => {
    if (!t || !block || at >= 0) return;
    const holder = aligned.map((p) => catalog.texts.find((x) => x.id === p.with)).find((m) => m && blockList(m).some((b) => b.key === block));
    if (holder) window.location.replace(readHref(holder.id, block, { v: verse }));
  }, [t, block, at, aligned, catalog, verse]);
  // A link to one verse (a search hit) opens that verse's Sanskrit even while the rest is folded.
  useEffect(() => setPeek(new Set(verse ? [verse] : [])), [key, verse]);

  useEffect(() => {
    if (!t) return;
    let live = true;
    setEntries(null);
    setError('');
    loadBlock(t, key)
      .then((es) => {
        if (!live) return;
        if (!es) return setError(`No ${t.levels[0]} ${key} in this text.`);
        setEntries(es);
        setEntriesKey(key);
      })
      .catch((e) => live && setError(String(e)));
    return () => {
      live = false;
    };
  }, [t, key]);

  useEffect(() => {
    setConc(null);
    if (t && pair?.mode === 'concordance') loadConcordance(t.id, pair.with).then(setConc).catch(() => setConc(null));
  }, [t, pair?.with, pair?.mode]);

  // Verse-aligned translations (one, or all of them when comparing) load the same block as the text.
  useEffect(() => {
    let live = true;
    if (!t || !alIds) {
      setAl(null);
      return;
    }
    const ids = alIds.split(',');
    Promise.all(
      ids.map((id) => {
        const meta = catalog.texts.find((x) => x.id === id);
        return meta ? loadBlock(meta, key).then((es) => es ?? []) : Promise.resolve([] as Entry[]);
      }),
    ).then((lists) => {
      if (live) setAl({ key, ids: alIds, byId: Object.fromEntries(ids.map((id, i) => [id, lists[i]])) });
    });
    return () => {
      live = false;
    };
  }, [t, key, alIds, catalog]);
  const alReady = !alIds || (al?.key === key && al.ids === alIds);
  const alMaps = useMemo(() => {
    const out: Record<string, Map<string, Entry>> = {};
    for (const [id, es] of Object.entries(al?.byId ?? {})) out[id] = new Map(es.map((e) => [e.r, e]));
    return out;
  }, [al]);

  useEffect(() => {
    let live = true;
    setTr(null);
    if (!t || !pair || pair.mode === 'aligned') return;
    const meta = catalog.texts.find((x) => x.id === pair.with);
    if (!meta) return;
    const trBlocks = blockList(meta);
    let refs: { ref: string; score: number }[] = [];
    if (pair.mode === 'prefix') refs = [{ ref: key, score: 1 }];
    else if (conc) refs = conc.map[key] ?? [];
    else return;
    if (offset && refs.length) {
      const i = trBlocks.findIndex((b) => b.key === refs[0].ref);
      const j = Math.min(Math.max(i + offset, 0), trBlocks.length - 1);
      refs = i >= 0 ? [{ ref: trBlocks[j].key, score: 0 }] : refs;
    }
    Promise.all(refs.map((r) => loadBlock(meta, r.ref))).then((lists) => {
      if (live) setTr({ meta, entries: lists.flatMap((l) => l ?? []), refs, offset, key });
    });
    return () => {
      live = false;
    };
  }, [t, pair, key, conc, offset, catalog]);

  useEffect(() => {
    if (!verse || !entries) return;
    document.getElementById(`v-${verse}`)?.scrollIntoView({ block: 'center' });
  }, [verse, entries]);

  const go = useCallback(
    (d: number) => {
      const b = blocks[at + d];
      if (b && t) window.location.hash = readHref(t.id, b.key, { with: withId });
    },
    [blocks, at, t, withId],
  );
  // Audiobook: the passage's English, in reading order, each piece tied to the element it highlights.
  const listenBlockMode = !!pair && pair.mode !== 'aligned';
  const narration = useMemo<NarrationItem[]>(() => {
    if (!t || !entries || entriesKey !== key) return [];
    const intro = { anchor: '', text: `${blockLabel(t, key).replace(/\s*·\s*/g, ', ')}.` };
    const paras = (anchor: string, text: string, each = false) => paragraphs(text).map((p, i) => ({ anchor: each ? `${anchor}-p${i}` : anchor, text: p }));
    if (listenBlockMode) {
      if (!tr || tr.key !== key) return [];
      return [intro, ...tr.entries.flatMap((e) => [...(e.t ? [{ anchor: `t-${e.r}`, text: `${e.t}.` }] : []), ...paras(`t-${e.r}`, e.e ?? '', true)])];
    }
    // Comparing, the audiobook reads the first paired translation: one voice, not every version in turn.
    const voice = shownAligned[0] && alReady ? alMaps[shownAligned[0].with] : null;
    return [intro, ...entries.flatMap((e) => paras(`v-${e.r}`, (voice ? voice.get(e.r)?.e : e.e) ?? e.m ?? ''))];
  }, [t, entries, entriesKey, key, tr, listenBlockMode, shownAligned, alReady, alMaps]);
  const narrationReady = !!entries && entriesKey === key && (listenBlockMode ? !!tr && tr.key === key : alReady);
  const narrator = useNarrator({
    items: narration,
    ready: narrationReady,
    title: t ? `${t.name} · ${blockLabel(t, key)}` : '',
    onEnd: () => {
      if (at < 0 || at >= blocks.length - 1) return false;
      go(1);
      return true;
    },
    onPrevBlock: () => go(-1),
  });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.closest('input, textarea, select')) return;
      if (e.key === 'ArrowLeft') go(-1);
      if (e.key === 'ArrowRight') go(1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [go]);

  if (!t) return <div className="lib-empty">No text “{textId}”. <a href="#/">Back to the library</a></div>;

  const veda = catalog.vedas.find((v) => v.id === t.veda);
  const layer = catalog.layers.find((l) => l.id === t.layer) ?? catalog.bands.find((b) => b.id === t.band);
  const blockMode = pair && pair.mode !== 'aligned';
  const metaOf = (id: string) => catalog.texts.find((x) => x.id === id);
  const versionsOf = (e: Entry): Version[] => {
    const paired = shownAligned.map((p) => ({ id: p.with, label: p.label, text: alMaps[p.with]?.get(e.r)?.e, lines: metaOf(p.with)?.verseLines }));
    if (compare) return [...(ownLabel ? [{ id: 'own', label: ownLabel, text: e.e, lines: t.verseLines }] : []), ...paired];
    return paired.length ? paired : [{ id: 'own', label: ownLabel ?? '', text: e.e, lines: t.verseLines }];
  };
  // A translation may number verses past the edition's own (the Ṛgveda's dvipadā hymns I.65–70 count ten verses
  // where this edition counts five): those verses follow the block instead of vanishing.
  const extras: Entry[] = [];
  const renumbered = new Set<string>();
  if (entries && alReady) {
    const have = new Set(entries.map((e) => e.r));
    for (const p of shownAligned)
      for (const x of al?.byId[p.with] ?? [])
        if (!have.has(x.r)) {
          have.add(x.r);
          extras.push({ r: x.r });
          renumbered.add(x.r);
        }
  }
  const rows = entries ? [...entries, ...extras] : null;
  // The translator's notes on this hymn, from whichever shown translation carries them.
  const notesFrom = [...shownAligned.map((p) => ({ id: p.with, e: al?.byId[p.with]?.find((x) => x.a) })), { id: t.id, e: entries?.find((x) => x.a) }].find((x) => x.e);
  const notes = alReady && notesFrom?.e?.a ? { about: notesFrom.e.a, deity: notesFrom.e.t, credit: metaOf(notesFrom.id)?.translation?.english } : undefined;
  const prefaceLabel = /\.1$/.test(key) ? `Introduction to ${t.levels[0]} ${key.split('.')[0]}` : 'Introduction to this group of hymns';
  // English-only texts (Jātakas, the pilgrims, Kathāsaritsāgara…) have no original to toggle or to flag as missing.
  const englishOnly = t.stats.sanskrit === 0 && !pair;
  // With no English to read, folding the Sanskrit away would leave a blank page: show it regardless.
  const hasEnglish = !!pair || shownAligned.length > 0 || !!entries?.some((e) => e.e || e.m);
  const canFold = hasEnglish && !englishOnly;
  const show = canFold || !entries ? chosen : { ...chosen, ...(chosen.deva || chosen.iast ? {} : { deva: true, iast: true }) };
  const sanskritShown = show.deva || show.iast;
  const toggleSanskrit = () => setShow({ ...chosen, deva: !sanskritShown, iast: !sanskritShown });
  const togglePeek = (r: string) =>
    setPeek((p) => {
      const n = new Set(p);
      if (n.has(r)) n.delete(r);
      else n.add(r);
      return n;
    });
  // A comparative text (Hebrew, Avestan) has one original, kept where IAST would be, and no Devanagari.
  const toggles: [keyof Show, string][] = englishOnly
    ? []
    : t.original
      ? [
          ['iast', t.original.label],
          ['english', 'English'],
        ]
      : [
          ['deva', 'देवनागरी'],
          ['iast', 'IAST'],
          ['english', 'English'],
        ];
  const origName = t.original?.name ?? 'Sanskrit';
  const origChip = t.original?.short ?? 'सं';
  // Sanskrit folded: the English runs on as prose, each verse with a button to peek at its Sanskrit.
  const prose = canFold && !sanskritShown;
  const twoCol = show.english && sanskritShown && (inlineEnglish || shownAligned.length > 0);
  const lowConfidence = tr && pair?.mode === 'concordance' && tr.refs.every((r) => r.score < 0.5);
  const englishCredits = (compare ? [t, ...aligned.map((p) => metaOf(p.with))] : [pair ? metaOf(pair.with) : t])
    .map((m) => m?.translation?.english)
    .filter((c): c is TranslationCredit => !!c);
  const machineCredit = blockMode ? undefined : t.translation?.machine;
  const chooseTranslation = (id: string) => {
    setSavedWith({ ...savedWith, [t.id]: id });
    window.location.hash = readHref(t.id, key, { with: id });
  };
  const credits = (
    <>
      {englishCredits.map((c) => (
        <Credit key={c.by} kind={c.kind ?? 'English'} c={c} />
      ))}
      {machineCredit && <Credit kind="Machine translation" c={machineCredit} />}
      {machineCredit && (
        <p className="mt-note">
          Machine English, marked in blue: nobody has checked it, and it can be wrong. Read it as a guide to the original, not as
          a translator&rsquo;s rendering; it is here because some English is better than none.
        </p>
      )}
    </>
  );
  const hymnNotes = notes && (show.english || englishOnly) && (
    <HymnNotes {...notes} credit={notes.credit && `${notes.credit.by}, ${notes.credit.work ?? ''} (${notes.credit.year ?? ''})`} preface={prefaceLabel} open={notesOpen.open} onToggle={(open) => open !== notesOpen.open && setNotesOpen({ open })} />
  );

  const readScale = { '--read-scale': String(1 + textSize.step * 0.1) } as CSSProperties;

  return (
    <div className={`reader${narrator.active ? ' listening' : ''}`} style={readScale}>
      <aside className={`reader-toc${tocOpen ? ' open' : ''}`}>
        <div className="toc-top">
          <a href="#/" className="toc-back">
            ← Library
          </a>
          <button className="toc-close" onClick={() => setTocOpen(false)} aria-label="Close contents">
            <X size={18} />
          </button>
        </div>
        <div className="toc-title">{t.name}</div>
        {t.source && <div className="toc-source">{t.source}</div>}
        {/* On mobile, opening a branch keeps the drawer open; only picking a passage closes it. */}
        <nav onClick={(ev) => (ev.target as HTMLElement).closest('a.toc-leaf') && setTocOpen(false)}>
          <Toc t={t} nodes={t.toc} current={key} withId={withId} />
        </nav>
      </aside>

      <main className="reader-main">
        <div className={`reader-bar${toolsOpen ? ' tools-open' : ''}`}>
          <button className="toc-open" onClick={() => setTocOpen(true)} aria-label="Contents">
            <List size={18} />
          </button>
          <div className="crumbs">
            {veda && <span>{veda.name}</span>}
            {layer && <span>{layer.name}</span>}
            <strong>{t.name}</strong>
          </div>
          {speechSupported && hasEnglish && (
            <button
              className={`chip listen-chip${narrator.active ? ' on' : ''}`}
              onClick={() => (narrator.playing ? narrator.pause() : narrator.play())}
              aria-pressed={narrator.playing}
              title="Listen: read the English aloud and carry on to the next passage"
            >
              <Headphones size={15} />
              {!narrow && <span>{narrator.playing ? 'Pause' : 'Listen'}</span>}
            </button>
          )}
          {narrow && canFold && (
            <button className={`chip sa-chip${sanskritShown ? ' on' : ''}`} onClick={toggleSanskrit} aria-pressed={sanskritShown} title={sanskritShown ? `Fold the ${origName} away` : `Show the ${origName}`}>
              {origChip}
            </button>
          )}
          {narrow && (
            <button className={`chip tools-btn${toolsOpen ? ' on' : ''}`} onClick={() => setToolsOpen(!toolsOpen)} aria-expanded={toolsOpen} aria-label="Reading settings">
              <Type size={15} />
            </button>
          )}
          <div className="reader-tools">
            <span className="text-size" role="group" aria-label="Text size">
              <button className="chip" onClick={() => setTextSize({ step: Math.max(-2, textSize.step - 1) })} disabled={textSize.step <= -2} aria-label="Smaller text">
                A−
              </button>
              <button className="chip" onClick={() => setTextSize({ step: Math.min(4, textSize.step + 1) })} disabled={textSize.step >= 4} aria-label="Larger text">
                A+
              </button>
            </span>
            {toggles.map(([k, label]) => (
              <button key={k} className={`chip${show[k] ? ' on' : ''}`} onClick={() => setShow({ ...show, [k]: !show[k] })} aria-pressed={show[k]}>
                {label}
              </button>
            ))}
            {pairs.length > 0 && (
              <select className="chip-select" value={choice} onChange={(e) => chooseTranslation(e.target.value)} aria-label="Translation">
                {ownLabel && <option value="own">{ownLabel}</option>}
                {pairs.map((p) => (
                  <option key={p.with} value={p.with}>
                    {ownLabel ? p.label : `Beside: ${p.label}`}
                  </option>
                ))}
                {canCompare && <option value="all">{aligned.length + (ownLabel ? 1 : 0) === 2 ? 'Both, verse by verse' : 'All, verse by verse'}</option>}
                {!ownLabel && <option value="none">No translation pane</option>}
              </select>
            )}
          </div>
        </div>

        <header className="block-head">
          <button className="nav-btn" disabled={at <= 0} onClick={() => go(-1)} aria-label="Previous">
            <ChevronLeft size={20} />
          </button>
          <div>
            <h2>{blockLabel(t, key)}</h2>
            <div className="block-sub">
              {entries ? `${entries.length} ${t.levels[t.levels.length - 1].toLowerCase()}${entries.length === 1 ? '' : 's'}` : ''}
              {parent && (
                <>
                  {' · '}translation of <a href={readHref(parent.id, '')}>{parent.name}</a>
                </>
              )}
            </div>
          </div>
          <button className="nav-btn" disabled={at >= blocks.length - 1} onClick={() => go(1)} aria-label="Next">
            <ChevronRight size={20} />
          </button>
        </header>

        {show.english && !narrow && (englishCredits.length > 0 || machineCredit) && <div className="tr-credit">{credits}</div>}

        {error && <div className="lib-empty">{error}</div>}
        {!entries && !error && <div className="reader-loading">Loading…</div>}

        {entries && !blockMode && hymnNotes}

        {rows && !blockMode && (
          <div className={`verses${twoCol ? ' two' : ''}${prose ? ' prose' : ''}${compare ? ' comparing' : ''}`}>
            {rows.map((e) => {
              const versions = versionsOf(e);
              const en = versions.find((v) => v.text)?.text;
              const machine = !en ? e.m : undefined;
              const english = <EnglishCell versions={versions} compare={compare} machine={machine} missing={twoCol} />;
              const lr = localRef(t, e.r);
              if (prose) {
                const hasSa = !!(e.s || e.d);
                // A verse with no English keeps its Sanskrit in view, or it would read as a gap.
                const open = peek.has(e.r) || (!en && !machine);
                return (
                  <div key={e.r} id={`v-${e.r}`} className={`verse${verse === e.r ? ' hit' : ''}`}>
                    <span className="v-mark">
                      <a className="v-ref" href={readHref(t.id, key, { with: withId, v: e.r })} title="Link to this passage">
                        {lr}
                      </a>
                      {hasSa && (en || machine) && (
                        <button className={`v-peek-btn${open ? ' on' : ''}`} onClick={() => togglePeek(e.r)} aria-expanded={open} title={`${origName} of this verse`}>
                          {origChip}
                        </button>
                      )}
                    </span>
                    {e.t && <div className="v-title">{e.t}</div>}
                    {(en || machine) && english}
                    {open && (
                      <div className="v-peek">
                        <SanskritCell orig={t.original} e={e} show={ALL_SANSKRIT} renumbered={renumbered.has(e.r)} />
                      </div>
                    )}
                  </div>
                );
              }
              return (
                <div key={e.r} id={`v-${e.r}`} className={`verse${verse === e.r ? ' hit' : ''}`}>
                  <a className="v-ref" href={readHref(t.id, key, { with: withId, v: e.r })} title="Link to this passage">
                    {lr}
                  </a>
                  {/* An English-only text has nothing for this cell but a heading; empty, it would open a gap above the verse. */}
                  {(!englishOnly || e.t) && (
                    <div className="v-sa">
                      {e.t && <div className="v-title">{e.t}</div>}
                      <SanskritCell orig={t.original} e={e} show={show} englishOnly={englishOnly} renumbered={renumbered.has(e.r)} />
                    </div>
                  )}
                  {(show.english || englishOnly) && english}
                </div>
              );
            })}
          </div>
        )}

        {entries && blockMode && narrow && (
          <div className="flow">
            <section className={`sa-fold${sanskritShown ? ' open' : ''}`}>
              <button className="sa-fold-head" onClick={toggleSanskrit} aria-expanded={sanskritShown}>
                <ChevronDown size={16} className={sanskritShown ? '' : 'rot'} />
                {origName}
                <span className="sa-fold-count">
                  {entries.length} {t.levels[t.levels.length - 1].toLowerCase()}
                  {entries.length === 1 ? '' : 's'}
                </span>
              </button>
              {sanskritShown &&
                entries.map((e) => (
                  <div key={e.r} id={`v-${e.r}`} className={`pane-verse${verse === e.r ? ' hit' : ''}`}>
                    <a className="v-ref" href={readHref(t.id, key, { with: withId, v: e.r })}>
                      {localRef(t, e.r)}
                    </a>
                    <div>
                      <SanskritCell orig={t.original} e={e} show={show} />
                    </div>
                  </div>
                ))}
            </section>
            <section className="flow-en">
              <div className="flow-en-head">
                <strong>{pair?.label}</strong>
                {pair?.mode === 'concordance' && (
                  <span className="pane-nudge">
                    <button onClick={() => setOffset(offset - 1)} aria-label="Earlier section">
                      ◀
                    </button>
                    {tr?.refs.map((r) => r.ref).join(', ') || '—'}
                    {offset !== 0 && ' (moved)'}
                    <button onClick={() => setOffset(offset + 1)} aria-label="Later section">
                      ▶
                    </button>
                  </span>
                )}
              </div>
              {lowConfidence && <p className="pane-note">Weak match: this translation numbers sections differently, so the passage may sit one section earlier or later.</p>}
              {!tr && <div className="reader-loading">Loading translation…</div>}
              {tr && !tr.entries.length && <div className="v-missing">No matching section found. Use ◀ ▶ to look nearby.</div>}
              {tr?.entries.map((e) => (
                <section key={e.r} id={`t-${e.r}`} className="pane-section">
                  {e.t && <h3>{e.t}</h3>}
                  {!e.r.endsWith('.intro') && <div className="pane-ref">{tr.meta.levels.map((l, i) => `${l} ${e.r.split('.')[i]}`).join(' · ')}</div>}
                  {e.e && <Paragraphs text={e.e} idPrefix={`t-${e.r}`} />}
                </section>
              ))}
            </section>
          </div>
        )}

        {entries && blockMode && !narrow && (
          <div className="panes">
            <div className="pane" ref={sync.left}>
              {entries.map((e) => (
                <div key={e.r} id={`v-${e.r}`} className={`pane-verse${verse === e.r ? ' hit' : ''}`}>
                  <a className="v-ref" href={readHref(t.id, key, { with: withId, v: e.r })}>
                    {localRef(t, e.r)}
                  </a>
                  <div>
                    <SanskritCell orig={t.original} e={e} show={show} />
                  </div>
                </div>
              ))}
            </div>
            <div className="pane pane-en" ref={sync.right}>
              <div className="pane-head">
                <strong>{pair?.label}</strong>
                {pair?.mode === 'concordance' && (
                  <span className="pane-nudge">
                    <button onClick={() => setOffset(offset - 1)} aria-label="Earlier section">
                      ◀
                    </button>
                    {tr?.refs.map((r) => r.ref).join(', ') || '—'}
                    {offset !== 0 && ' (moved)'}
                    <button onClick={() => setOffset(offset + 1)} aria-label="Later section">
                      ▶
                    </button>
                  </span>
                )}
              </div>
              {pair?.mode === 'concordance' && (
                <p className="pane-note">
                  {lowConfidence
                    ? 'Weak match: this translation numbers sections differently, so the passage may sit one section earlier or later.'
                    : (conc?.note ?? 'Matched by shared names; the translation follows the vulgate, so sections may start or end at different verses.')}
                </p>
              )}
              {!tr && <div className="reader-loading">Loading translation…</div>}
              {tr && !tr.entries.length && <div className="v-missing">No matching section found. Use ◀ ▶ to look nearby.</div>}
              {tr?.entries.map((e) => (
                <section key={e.r} id={`t-${e.r}`} className="pane-section">
                  {e.t && <h3>{e.t}</h3>}
                  {!e.r.endsWith('.intro') && <div className="pane-ref">{tr.meta.levels.map((l, i) => `${l} ${e.r.split('.')[i]}`).join(' · ')}</div>}
                  {e.e && <Paragraphs text={e.e} idPrefix={`t-${e.r}`} />}
                </section>
              ))}
            </div>
          </div>
        )}

        {/* On a phone the credit would push the text below the fold; it follows the passage instead. */}
        {narrow && entries && (englishCredits.length > 0 || machineCredit) && <div className="tr-credit tr-credit-after">{credits}</div>}

        <footer className="block-foot">
          <button className="nav-btn wide" disabled={at <= 0} onClick={() => go(-1)}>
            <ChevronLeft size={16} /> {at > 0 ? blockLabel(t, blocks[at - 1].key) : ''}
          </button>
          <button className="nav-btn wide" disabled={at >= blocks.length - 1} onClick={() => go(1)}>
            {at < blocks.length - 1 ? blockLabel(t, blocks[at + 1].key) : ''} <ChevronRight size={16} />
          </button>
        </footer>
        <NarratorBar n={narrator} label={blockLabel(t, key)} />
      </main>
    </div>
  );
}
