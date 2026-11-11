import { useMemo, useState } from 'react';
import type { Catalog, TextMeta } from './data';
import { blockList } from './data';
import { readHref } from './route';

const fold = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const fmt = (n: number) => n.toLocaleString('en-IN');

/** Human English of its own or a paired translation; a machine translation alone does not count. */
const hasEnglish = (t: TextMeta) => (t.pairs ?? []).length > 0 || t.stats.english > 0;

const era = (y: number) => (y < 0 ? 'BCE' : 'CE');
/** [-900, -725] → "c. 900–725 BCE"; [-200, 200] → "c. 200 BCE–200 CE". */
function dateLabel([a, b]: [number, number]) {
  const n = (y: number) => Math.abs(Math.round(y));
  if (Math.round(a) === Math.round(b)) return `c. ${n(a)} ${era(a)}`;
  return era(a) === era(b) ? `c. ${n(a)}–${n(b)} ${era(b)}` : `c. ${n(a)} ${era(a)}–${n(b)} ${era(b)}`;
}

function TextCard({ t }: { t: TextMeta }) {
  const first = blockList(t)[0]?.key ?? '';
  const translations = (t.pairs ?? []).map((p) => p.label);
  const english = translations.length ? 100 : t.stats.english;
  const unit = t.levels[t.levels.length - 1];
  return (
    <a className="lib-card" href={readHref(t.id, first)} title={t.source ?? ''}>
      <span className="lib-card-name">{t.name}</span>
      {t.date && (
        <span className="lib-card-date" title="Approximate date of composition (Pramāṇa consensus)">
          {dateLabel(t.date)}
        </span>
      )}
      <span className="lib-card-meta">
        {fmt(t.stats.entries)} {unit.toLowerCase()}
        {t.stats.entries === 1 ? '' : 's'}
        {t.later && <span className="lib-tag">later</span>}
      </span>
      <span className="lib-bar" aria-label={`English ${english}%`}>
        <span style={{ width: `${english}%` }} />
      </span>
      <span className="lib-card-en">
        {translations.length
          ? `English: ${translations.join(', ')}`
          : english >= 95
            ? 'English throughout'
            : english > 0
              ? `English ${english}%`
              : t.stats.machine
                ? 'Machine translation only'
                : 'Sanskrit only'}
      </span>
    </a>
  );
}

export default function LibraryHome({ catalog }: { catalog: Catalog }) {
  const [q, setQ] = useState('');
  const [englishOnly, setEnglishOnly] = useState(() => {
    try {
      return localStorage.getItem('lib-english-only') === '1';
    } catch {
      return false;
    }
  });
  const toggleEnglish = () => {
    setEnglishOnly((v) => {
      try {
        localStorage.setItem('lib-english-only', v ? '0' : '1');
      } catch {
        /* storage blocked: the toggle still works for this visit */
      }
      return !v;
    });
  };
  const visible = useMemo(() => {
    const f = fold(q.trim());
    return catalog.texts.filter(
      (t) =>
        !t.translationOf &&
        (!englishOnly || hasEnglish(t)) &&
        (!f || fold(t.name).includes(f) || fold(t.source ?? '').includes(f)),
    );
  }, [catalog, q, englishOnly]);
  const filtering = !!q.trim() || englishOnly;
  const totals = useMemo(() => {
    const prim = catalog.texts.filter((t) => !t.translationOf);
    const entries = catalog.texts.reduce((n, t) => n + t.stats.entries, 0);
    return { texts: prim.length, entries };
  }, [catalog]);

  const cell = (veda: string, layer: string) => visible.filter((t) => t.veda === veda && t.layer === layer);

  return (
    <div className="lib-home">
      <section className="lib-hero">
        <h1>The Vedic corpus, mapped</h1>
        <p>
          {totals.texts} texts · {fmt(totals.entries)} passages. Each Veda reads left to right from its hymns to its
          ritual manuals. Open any text to read it in Sanskrit and English, side by side.
        </p>
        <div className="lib-filters">
          <input className="lib-search" placeholder="Find a text — e.g. Kaṭha, Gopatha, Bhārata" value={q} onChange={(e) => setQ(e.target.value)} />
          <button type="button" className="lib-toggle" aria-pressed={englishOnly} onClick={toggleEnglish}>
            <span className="lib-toggle-dot" aria-hidden="true" />
            With English only
          </button>
        </div>
      </section>

      <section className="lib-grid" style={{ ['--cols' as string]: catalog.layers.length }}>
        <div className="lib-corner" />
        {catalog.layers.map((l) => (
          <div key={l.id} className="lib-colhead">
            <strong>{l.name}</strong>
            <span>{l.blurb}</span>
          </div>
        ))}
        {catalog.vedas.map((v) => {
          const any = catalog.layers.some((l) => cell(v.id, l.id).length);
          if (!any) return null;
          return (
            <div key={v.id} className="lib-row">
              <div className="lib-rowhead">
                <strong>{v.name}</strong>
                <span className="lib-deva">{v.deva}</span>
                <span>{v.blurb}</span>
              </div>
              {catalog.layers.map((l) => {
                const texts = cell(v.id, l.id);
                const absent = !filtering && !texts.length ? v.absent?.[l.id] : undefined;
                return (
                  <div key={l.id} className="lib-cell" data-layer={l.name}>
                    {texts.map((t) => (
                      <TextCard key={t.id} t={t} />
                    ))}
                    {absent && <p className="lib-absent">{absent}</p>}
                  </div>
                );
              })}
            </div>
          );
        })}
      </section>

      {catalog.bands.map((b) => {
        const ts = visible.filter((t) => t.band === b.id);
        if (!ts.length) return null;
        return (
          <section key={b.id} className="lib-band">
            <div className="lib-bandhead">
              <strong>{b.name}</strong>
              <span>{b.blurb}</span>
            </div>
            {b.groups ? (
              <div className="lib-band-groups">
                {b.groups.map((g) => {
                  const members = ts.filter((t) => t.group === g.id);
                  if (!members.length) return null;
                  return (
                    <div key={g.id} className="lib-band-group">
                      <div className="lib-grouphead">
                        <strong>{g.name}</strong>
                        <span>{g.blurb}</span>
                      </div>
                      <div className="lib-band-cards">
                        {members.map((t) => (
                          <TextCard key={t.id} t={t} />
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="lib-band-cards">
                {ts.map((t) => (
                  <TextCard key={t.id} t={t} />
                ))}
              </div>
            )}
          </section>
        );
      })}
      {!visible.length && <p className="lib-empty">{q.trim() ? `No text matches “${q}”${englishOnly ? ' with English' : ''}.` : 'No text matches.'}</p>}
    </div>
  );
}
