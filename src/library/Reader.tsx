import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, Headphones, List, Type, X } from 'lucide-react';
import type { Catalog, Concordance, Entry, SourceLink, TextMeta, TocNode, TranslationCredit } from './data';
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

/** `idPrefix` gives each paragraph an id (prefix-p0, -p1…) for the audiobook to highlight. */
const Paragraphs = ({ text, idPrefix }: { text: string; idPrefix?: string }) => (
  <>
    {paragraphs(text).map((p, i) => (
      <p key={i} id={idPrefix ? `${idPrefix}-p${i}` : undefined}>
        {p}
      </p>
    ))}
  </>
);

function SanskritCell({ e, show, englishOnly }: { e: Entry; show: Show; englishOnly?: boolean }) {
  return (
    <>
      {show.deva && e.d && <div className="v-deva" lang="sa-Deva">{e.d}</div>}
      {show.iast && e.s && <div className="v-iast" lang="sa-Latn">{e.s}</div>}
      {!e.s && !e.d && !englishOnly && <div className="v-missing">No Sanskrit in this edition</div>}
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
  const [conc, setConc] = useState<Concordance | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState('');
  const sync = useScrollSync();

  const blocks = useMemo(() => (t ? blockList(t) : []), [t]);
  const at = blocks.findIndex((b) => b.key === block);
  const key = at >= 0 ? block : (blocks[0]?.key ?? '');
  const pairs = t?.pairs?.filter((p) => p.mode !== 'concordance' || p.available) ?? [];
  // A translation is shown by default when the text has one; ?with=none turns it off.
  const pair = withId === 'none' ? undefined : (pairs.find((p) => p.with === withId) ?? pairs[0]);
  const parent = t?.translationOf ? catalog.texts.find((x) => x.id === t.translationOf) : undefined;
  const inlineEnglish = !!entries?.some((e) => e.e || e.m) && !!entries?.some((e) => e.s || e.d);

  useEffect(() => setOffset(0), [key, pair?.with]);
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

  useEffect(() => {
    let live = true;
    setTr(null);
    if (!t || !pair) return;
    const meta = catalog.texts.find((x) => x.id === pair.with);
    if (!meta) return;
    const trBlocks = blockList(meta);
    let refs: { ref: string; score: number }[] = [];
    if (pair.mode === 'aligned' || pair.mode === 'prefix') refs = [{ ref: key, score: 1 }];
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
    const aligned = pair?.mode === 'aligned' && tr?.key === key ? new Map(tr.entries.map((e) => [e.r, e.e])) : null;
    return [intro, ...entries.flatMap((e) => paras(`v-${e.r}`, (aligned ? aligned.get(e.r) : e.e) ?? e.m ?? ''))];
  }, [t, entries, entriesKey, key, tr, pair?.mode, listenBlockMode]);
  const narrationReady = !!entries && entriesKey === key && (!pair || (!!tr && tr.key === key));
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
  const trByRef = new Map((pair?.mode === 'aligned' ? tr?.entries : [])?.map((e) => [e.r, e]) ?? []);
  // English-only texts (Jātakas, the pilgrims, Kathāsaritsāgara…) have no original to toggle or to flag as missing.
  const englishOnly = t.stats.sanskrit === 0 && !pair;
  // With no English to read, folding the Sanskrit away would leave a blank page: show it regardless.
  const hasEnglish = !!pair || !!entries?.some((e) => e.e || e.m);
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
  const toggles: [keyof Show, string][] = englishOnly
    ? []
    : [
        ['deva', 'देवनागरी'],
        ['iast', 'IAST'],
        ['english', 'English'],
      ];
  // Sanskrit folded: the English runs on as prose, each verse with a button to peek at its Sanskrit.
  const prose = canFold && !sanskritShown;
  const twoCol = show.english && sanskritShown && (inlineEnglish || pair?.mode === 'aligned');
  const lowConfidence = tr && pair?.mode === 'concordance' && tr.refs.every((r) => r.score < 0.5);
  const englishCredit = (pair ? catalog.texts.find((x) => x.id === pair.with) : t)?.translation?.english;
  const machineCredit = blockMode ? undefined : t.translation?.machine;

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
            <button className={`chip sa-chip${sanskritShown ? ' on' : ''}`} onClick={toggleSanskrit} aria-pressed={sanskritShown} title={sanskritShown ? 'Fold the Sanskrit away' : 'Show the Sanskrit'}>
              सं
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
              <select
                className="chip-select"
                value={pair?.with ?? 'none'}
                onChange={(e) => (window.location.hash = readHref(t.id, key, { with: e.target.value }))}
                aria-label="Translation shown alongside"
              >
                {pairs.map((p) => (
                  <option key={p.with} value={p.with}>
                    Beside: {p.label}
                  </option>
                ))}
                <option value="none">No translation pane</option>
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

        {show.english && !narrow && (englishCredit || machineCredit) && (
          <div className="tr-credit">
            {englishCredit && <Credit kind="English" c={englishCredit} />}
            {machineCredit && <Credit kind="Machine translation" c={machineCredit} />}
          </div>
        )}

        {error && <div className="lib-empty">{error}</div>}
        {!entries && !error && <div className="reader-loading">Loading…</div>}

        {entries && !blockMode && (
          <div className={`verses${twoCol ? ' two' : ''}${prose ? ' prose' : ''}`}>
            {entries.map((e) => {
              const en = pair?.mode === 'aligned' ? trByRef.get(e.r)?.e : e.e;
              const machine = !en ? e.m : undefined;
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
                        <button className={`v-peek-btn${open ? ' on' : ''}`} onClick={() => togglePeek(e.r)} aria-expanded={open} title="Sanskrit of this verse">
                          सं
                        </button>
                      )}
                    </span>
                    {e.t && <div className="v-title">{e.t}</div>}
                    {en ? (
                      <div className="v-en">
                        <Paragraphs text={en} />
                      </div>
                    ) : machine ? (
                      <div className="v-en v-mt">
                        <span className="mt-label">Machine translation</span>
                        <Paragraphs text={machine} />
                      </div>
                    ) : null}
                    {open && (
                      <div className="v-peek">
                        <SanskritCell e={e} show={ALL_SANSKRIT} />
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
                  <div className="v-sa">
                    {e.t && <div className="v-title">{e.t}</div>}
                    <SanskritCell e={e} show={show} englishOnly={englishOnly} />
                  </div>
                  {(show.english || englishOnly) &&
                    (en ? (
                      <div className="v-en"><Paragraphs text={en} /></div>
                    ) : machine ? (
                      <div className="v-en v-mt">
                        <span className="mt-label">Machine translation</span>
                        <Paragraphs text={machine} />
                      </div>
                    ) : twoCol ? (
                      <div className="v-en v-missing">—</div>
                    ) : null)}
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
                Sanskrit
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
                      <SanskritCell e={e} show={show} />
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
                  <div className="pane-ref">{tr.meta.levels.map((l, i) => `${l} ${e.r.split('.')[i]}`).join(' · ')}</div>
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
                    <SanskritCell e={e} show={show} />
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
                  <div className="pane-ref">{tr.meta.levels.map((l, i) => `${l} ${e.r.split('.')[i]}`).join(' · ')}</div>
                  {e.e && <Paragraphs text={e.e} idPrefix={`t-${e.r}`} />}
                </section>
              ))}
            </div>
          </div>
        )}

        {/* On a phone the credit would push the text below the fold; it follows the passage instead. */}
        {narrow && entries && (englishCredit || machineCredit) && (
          <div className="tr-credit tr-credit-after">
            {englishCredit && <Credit kind="English" c={englishCredit} />}
            {machineCredit && <Credit kind="Machine translation" c={machineCredit} />}
          </div>
        )}

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
