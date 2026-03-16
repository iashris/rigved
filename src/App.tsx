import { useState, useEffect, useMemo, useCallback } from 'react';
import SearchBar from './components/SearchBar';
import Controls from './components/Controls';
import ChartVisualization from './components/ChartVisualization';
import ResultsDisplay from './components/ResultsDisplay';
import VedaSelector from './components/VedaSelector';
import SuktaNavigator from './components/SuktaNavigator';
import type { NavMode } from './components/SuktaNavigator';
import { loadVedaData, searchWord } from './utils/dataProcessor';
import type { Verse, SearchResult, OrderType, DisplayMode, VedaId } from './types';
import { VEDA_CONFIGS } from './types';
import { BookOpen, Share2, Moon, Sun, Copy, Check } from 'lucide-react';
import './App.css';

function isVedaId(value: string | null): value is VedaId {
  return value === 'rigveda' || value === 'samaveda' || value === 'atharvaveda' || value === 'yajurveda_black' || value === 'yajurveda_white' || value === 'satapatha_brahmana' || value === 'jaiminiya_brahmana' || value === 'chandogya_upanishad';
}

function App() {
  const [currentVeda, setCurrentVeda] = useState<VedaId>('rigveda');
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [orderType, setOrderType] = useState<OrderType>('sequential');
  const [displayMode, setDisplayMode] = useState<DisplayMode>('absolute');
  const [error, setError] = useState<string>('');
  const [searchTerms, setSearchTerms] = useState<string[]>([]);
  const [navigatedVerses, setNavigatedVerses] = useState<Verse[]>([]);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [copyToast, setCopyToast] = useState<string | null>(null);
  const [copiedVerseKey, setCopiedVerseKey] = useState<string | null>(null);
  const metadata = useMemo(() => VEDA_CONFIGS[currentVeda], [currentVeda]);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // Load search params from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    const order = params.get('order') as OrderType;
    const mode = params.get('mode') as DisplayMode;
    const vedaParam = params.get('veda');

    if (isVedaId(vedaParam)) {
      setCurrentVeda(vedaParam);
    }
    if (order && (order === 'sequential' || order === 'chronological')) {
      setOrderType(order);
    }
    if (mode && (mode === 'absolute' || mode === 'percentage')) {
      setDisplayMode(mode);
    }
    if (query) {
      const terms = query.split(',').map(t => t.trim());
      setSearchTerms(terms);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    setLoading(true);
    setError('');

    loadVedaData(currentVeda)
      .then(data => {
        if (isCancelled) return;
        setVerses(data);
        setLoading(false);
        console.log(`Loaded ${data.length} verses for ${currentVeda}`);
      })
      .catch(err => {
        if (isCancelled) return;
        setError(`Failed to load ${metadata.name} data`);
        setVerses([]);
        setLoading(false);
        console.error(err);
      });

    return () => {
      isCancelled = true;
    };
  }, [currentVeda, metadata.name]);

  useEffect(() => {
    if (!metadata.chronologicalOrder && orderType === 'chronological') {
      setOrderType('sequential');
    }
  }, [metadata, orderType]);

  const updateURL = useCallback((terms: string[]) => {
    const params = new URLSearchParams();
    if (terms.length > 0) {
      params.set('q', terms.join(','));
    }
    params.set('order', orderType);
    params.set('mode', displayMode);
    params.set('veda', currentVeda);

    const newURL = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newURL);
  }, [orderType, displayMode, currentVeda]);

  const handleSearch = useCallback((terms: string[]) => {
    if (!verses.length) {
      setError('Data not loaded yet');
      return;
    }

    setError('');
    const results: SearchResult[] = [];

    terms.forEach(term => {
      const result = searchWord(verses, [term], metadata, false);
      if (result) {
        results.push(result);
      }
    });

    if (results.length === 0) {
      setError('No matches found for the given search terms');
      setSearchResults([]);
    } else {
      setSearchResults(results);
      setSearchTerms(prevTerms => {
        const termsChanged = JSON.stringify(prevTerms) !== JSON.stringify(terms);
        return termsChanged ? terms : prevTerms;
      });
      updateURL(terms);
    }
  }, [verses, metadata, updateURL]);

  useEffect(() => {
    if (verses.length > 0 && searchTerms.length > 0) {
      handleSearch(searchTerms);
    }
  }, [verses, searchTerms, handleSearch]);

  const copyShareLink = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      showToast('Link copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy link:', err);
    });
  };

  const showToast = (message: string) => {
    setCopyToast(message);
    setTimeout(() => setCopyToast(null), 2000);
  };

  useEffect(() => {
    if (searchTerms.length > 0) {
      updateURL(searchTerms);
    }
  }, [orderType, displayMode, currentVeda, searchTerms, updateURL]);

  const handleVedaChange = (veda: VedaId) => {
    if (veda === currentVeda) return;
    setCurrentVeda(veda);
    setSearchResults([]);
    setVerses([]);
    setNavigatedVerses([]);
  };

  const handleNavigateToVerse = useCallback((navVerses: Verse[], _navMode: NavMode) => {
    setNavigatedVerses(navVerses);
    setSearchResults([]);
    setSearchTerms([]);
    setError('');

    setTimeout(() => {
      const element = document.querySelector('.navigated-verse-section');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  }, []);

  const copyVerseBlock = async (verse: Verse) => {
    const vedaName = metadata.name;
    const parts = [`${vedaName} ${verse.reference}`];
    if (verse.iast) parts.push(verse.iast);
    if (verse.meaning) parts.push(verse.meaning);
    parts.push(verse.text);
    const formatted = parts.join('\n\n');

    try {
      await navigator.clipboard.writeText(formatted);
      setCopiedVerseKey(verse.reference);
      showToast('Verse copied!');
      setTimeout(() => setCopiedVerseKey(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const copyAllNavigatedVerses = async () => {
    if (navigatedVerses.length === 0) return;
    const vedaName = metadata.name;

    let header: string;
    if (metadata.id === 'satapatha_brahmana') {
      header = `${vedaName}, ${metadata.bookLabel} ${navigatedVerses[0].reference.split('.')[0]}, Adhyaya ${navigatedVerses[0].reference.split('.')[1]}, ${metadata.hymnLabel} ${navigatedVerses[0].reference.split('.')[2]}`;
    } else {
      header = `${vedaName}, ${metadata.bookLabel} ${navigatedVerses[0].mandala}, ${metadata.hymnLabel} ${navigatedVerses[0].hymn}`;
    }

    const verseTexts = navigatedVerses.map(v => {
      const parts = [`[${v.reference}]`];
      if (v.iast) parts.push(v.iast);
      if (v.meaning) parts.push(v.meaning);
      parts.push(v.text);
      return parts.join('\n');
    });

    const fullText = `${header}\n\n${verseTexts.join('\n\n')}`;

    try {
      await navigator.clipboard.writeText(fullText);
      showToast(`Copied ${navigatedVerses.length} verse${navigatedVerses.length > 1 ? 's' : ''}!`);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading {metadata.name} data...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <BookOpen size={32} />
          <h1>{metadata.name} Analysis Tool</h1>
          <p className="subtitle">
            Search and visualize word distributions across the {metadata.totalBooks} {metadata.pluralBookLabel}
          </p>
          <div className="header-buttons">
            <button
              className="theme-toggle-btn"
              onClick={() => setDarkMode(d => !d)}
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
              {darkMode ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="search-section">
          <VedaSelector currentVeda={currentVeda} onChange={handleVedaChange} />
          <div className="search-nav-row">
            <SearchBar onSearch={handleSearch} />
            <SuktaNavigator
              verses={verses}
              metadata={metadata}
              onNavigate={handleNavigateToVerse}
            />
          </div>
          {error && <div className="error-message">{error}</div>}
        </section>

        {navigatedVerses.length > 0 && (
          <section className="navigated-verse-section">
            <div className="navigated-verse-content">
              <div className="navigated-verse-header">
                <h2>
                  {metadata.id === 'satapatha_brahmana' ? (
                    <>
                      {metadata.bookLabel} {navigatedVerses[0].reference.split('.')[0]},
                      {' '}Adhyaya {navigatedVerses[0].reference.split('.')[1]},
                      {' '}{metadata.hymnLabel} {navigatedVerses[0].reference.split('.')[2]}
                      {navigatedVerses.length > 1 && ` (${navigatedVerses.length} verses)`}
                    </>
                  ) : navigatedVerses.length > 1 && !metadata.hasThirdLevel && new Set(navigatedVerses.map(v => v.hymn)).size > 1 ? (
                    <>
                      {metadata.bookLabel} {navigatedVerses[0].mandala} ({navigatedVerses.length} verses)
                    </>
                  ) : (
                    <>
                      {metadata.bookLabel} {navigatedVerses[0].mandala}, {metadata.hymnLabel} {navigatedVerses[0].hymn}
                      {navigatedVerses.length > 1 && ` (${navigatedVerses.length} verses)`}
                    </>
                  )}
                </h2>
                <button
                  className="copy-chapter-btn"
                  onClick={copyAllNavigatedVerses}
                  title="Copy all displayed verses"
                >
                  <Copy size={16} />
                  Copy All
                </button>
              </div>
              {navigatedVerses.map((verse) => (
                <div className="verse-card" key={verse.reference}>
                  <div className="verse-header">
                    <span className="verse-reference">
                      {metadata.hasThirdLevel || navigatedVerses.length === 1
                        ? verse.reference
                        : `${metadata.hymnLabel} ${verse.hymn}`}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {metadata.hasThirdLevel && (
                        <span className="verse-location">
                          {metadata.bookLabel} {verse.mandala}, {metadata.hymnLabel} {verse.hymn}, {metadata.verseLabel} {verse.verse}
                        </span>
                      )}
                      <button
                        className={`verse-copy-btn ${copiedVerseKey === verse.reference ? 'copied' : ''}`}
                        onClick={() => copyVerseBlock(verse)}
                        title="Copy this verse"
                      >
                        {copiedVerseKey === verse.reference ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                    </div>
                  </div>
                  {verse.meaning && (
                    <div className="verse-sanskrit">
                      <div className="verse-label">Sanskrit:</div>
                      <div className="verse-content-text">{verse.meaning}</div>
                    </div>
                  )}
                  <div className="verse-translation">
                    {verse.meaning && <div className="verse-label">English:</div>}
                    <div className="verse-content-text">{verse.text}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {searchResults.length > 0 && (
          <>
            <section className="controls-section">
              <div className="controls-wrapper">
                <Controls
                  metadata={metadata}
                  orderType={orderType}
                  displayMode={displayMode}
                  onOrderChange={setOrderType}
                  onDisplayModeChange={setDisplayMode}
                />
                <button className="share-button" onClick={copyShareLink} title="Copy share link">
                  <Share2 size={20} />
                  Share
                </button>
              </div>
            </section>

            <section className="visualization-section">
              <ChartVisualization
                results={searchResults}
                orderType={orderType}
                displayMode={displayMode}
                metadata={metadata}
              />
            </section>

            <section className="results-section">
              <ResultsDisplay results={searchResults} metadata={metadata} />
            </section>
          </>
        )}

        <footer className="app-footer">
          <div className="footer-content">
            <p>Data source: {metadata.dataSource}</p>
            {metadata.chronologyAttribution && (
              <p>{metadata.chronologyAttribution}</p>
            )}
            <p className="corpus-info">
              Total corpus: {verses.length} verses across {metadata.totalBooks} {metadata.pluralBookLabel}
            </p>
          </div>
        </footer>
      </main>

      {copyToast && <div className="copy-toast">{copyToast}</div>}
    </div>
  );
}

export default App;
