import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import App from './App';
import LibraryHome from './library/LibraryHome';
import Reader from './library/Reader';
import { loadCatalog, type Catalog } from './library/data';
import { useRoute } from './library/route';
import './library/library.css';

export default function Root() {
  const route = useRoute();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState('');
  const [dark, setDark] = useState(() => {
    try {
      const saved = localStorage.getItem('theme');
      if (saved) return saved === 'dark';
    } catch {
      /* no storage */
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    // Phone browsers tint their toolbar with this, so the page doesn't sit under a bright bar at night.
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#0d0d0d' : '#ffffff');
    document.documentElement.style.background = dark ? '#0d0d0d' : '#ffffff';
    try {
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    } catch {
      /* no storage */
    }
  }, [dark]);

  useEffect(() => {
    loadCatalog().then(setCatalog).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (route.page !== 'read') window.scrollTo(0, 0);
  }, [route.page]);

  // The analysis tool keeps its own header and theme switch.
  if (route.page === 'analysis') {
    return (
      <>
        <nav className="lib-nav analysis">
          <a href="#/">← Library</a>
        </nav>
        <App />
      </>
    );
  }

  return (
    <div className="lib">
      <nav className="lib-nav">
        <a href="#/" className="lib-brand">
          <span className="lib-brand-mark">ॐ</span> Vedic Library
        </a>
        <div className="lib-nav-links">
          <a href="#/" className={route.page === 'home' ? 'on' : ''}>
            Canon
          </a>
          <a href="#/analysis">Word analysis</a>
          <button className="lib-theme" onClick={() => setDark(!dark)} aria-label={dark ? 'Light mode' : 'Dark mode'}>
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </nav>
      {error && <div className="lib-empty">Could not load the library: {error}</div>}
      {!catalog && !error && <div className="reader-loading">Loading the library…</div>}
      {catalog && route.page === 'home' && <LibraryHome catalog={catalog} />}
      {catalog && route.page === 'read' && <Reader catalog={catalog} textId={route.text} block={route.block} withId={route.with} verse={route.v} />}
    </div>
  );
}
