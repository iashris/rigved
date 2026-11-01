import { useMemo, useState } from 'react';
import type { Catalog, TextMeta } from './data';
import { blockList } from './data';
import { readHref } from './route';

const fold = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const fmt = (n: number) => n.toLocaleString('en-IN');

function TextCard({ t }: { t: TextMeta }) {
  const first = blockList(t)[0]?.key ?? '';
  const translations = (t.pairs ?? []).map((p) => p.label);
  const english = translations.length ? 100 : t.stats.english;
  const unit = t.levels[t.levels.length - 1];
  return (
    <a className="lib-card" href={readHref(t.id, first)} title={t.source ?? ''}>
      <span className="lib-card-name">{t.name}</span>
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
  const visible = useMemo(() => {
    const f = fold(q.trim());
    return catalog.texts.filter((t) => !t.translationOf && (!f || fold(t.name).includes(f) || fold(t.source ?? '').includes(f)));
  }, [catalog, q]);
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
        <input className="lib-search" placeholder="Find a text — e.g. Kaṭha, Gopatha, Bhārata" value={q} onChange={(e) => setQ(e.target.value)} />
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
              {catalog.layers.map((l) => (
                <div key={l.id} className="lib-cell" data-layer={l.name}>
                  {cell(v.id, l.id).map((t) => (
                    <TextCard key={t.id} t={t} />
                  ))}
                </div>
              ))}
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
            <div className="lib-band-cards">
              {ts.map((t) => (
                <TextCard key={t.id} t={t} />
              ))}
            </div>
          </section>
        );
      })}
      {!visible.length && <p className="lib-empty">No text matches “{q}”.</p>}
    </div>
  );
}
