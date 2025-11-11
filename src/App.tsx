import { useState, useEffect, useMemo } from 'react';
import SearchBar from './components/SearchBar';
import Controls from './components/Controls';
import ChartVisualization from './components/ChartVisualization';
import ResultsDisplay from './components/ResultsDisplay';
import VedaSelector from './components/VedaSelector';
import SuktaNavigator from './components/SuktaNavigator';
import { loadVedaData, searchWord } from './utils/dataProcessor';
import type { Verse, SearchResult, OrderType, DisplayMode, VedaId } from './types';
import { VEDA_CONFIGS } from './types';
import { BookOpen, Share2 } from 'lucide-react';
import './App.css';

function isVedaId(value: string | null): value is VedaId {
  return value === 'rigveda' || value === 'atharvaveda' || value === 'yajurveda_black' || value === 'yajurveda_white';
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
  const [navigatedVerse, setNavigatedVerse] = useState<Verse | null>(null);
  const metadata = useMemo(() => VEDA_CONFIGS[currentVeda], [currentVeda]);

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

  // Perform search when verses are loaded and search terms exist
  useEffect(() => {
    if (verses.length > 0 && searchTerms.length > 0) {
      handleSearch(searchTerms);
    }
  }, [verses, searchTerms]);
  
  const handleSearch = (terms: string[]) => {
    if (!verses.length) {
      setError('Data not loaded yet');
      return;
    }

    setError('');
    const results: SearchResult[] = [];

    // Search for each term individually
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
      setSearchTerms(terms);
      updateURL(terms);
    }
  };

  const updateURL = (terms: string[]) => {
    const params = new URLSearchParams();
    if (terms.length > 0) {
      params.set('q', terms.join(','));
    }
    params.set('order', orderType);
    params.set('mode', displayMode);
    params.set('veda', currentVeda);

    const newURL = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newURL);
  };

  const copyShareLink = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      alert('Link copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy link:', err);
    });
  };

  // Update URL when order or display mode changes
  useEffect(() => {
    if (searchTerms.length > 0) {
      updateURL(searchTerms);
    }
  }, [orderType, displayMode, currentVeda]);

  const handleVedaChange = (veda: VedaId) => {
    if (veda === currentVeda) return;
    setCurrentVeda(veda);
    setSearchResults([]);
    setVerses([]);
    setNavigatedVerse(null);
  };

  const handleNavigateToVerse = (verse: Verse) => {
    setNavigatedVerse(verse);
    setSearchResults([]);
    setSearchTerms([]);
    setError('');

    // Scroll to the navigated verse section
    setTimeout(() => {
      const element = document.querySelector('.navigated-verse-section');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
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
        
        {navigatedVerse && (
          <section className="navigated-verse-section">
            <div className="navigated-verse-content">
              <h2>Verse: {navigatedVerse.reference}</h2>
              <div className="verse-card">
                <div className="verse-header">
                  <span className="verse-reference">{navigatedVerse.reference}</span>
                  <span className="verse-location">
                    {metadata.bookLabel} {navigatedVerse.mandala}, {metadata.hymnLabel} {navigatedVerse.hymn}
                    {metadata.hasThirdLevel && `, ${metadata.verseLabel} ${navigatedVerse.verse}`}
                  </span>
                </div>
                {navigatedVerse.meaning && (
                  <div className="verse-sanskrit">
                    <div className="verse-label">Sanskrit:</div>
                    <div className="verse-content-text">{navigatedVerse.meaning}</div>
                  </div>
                )}
                <div className="verse-translation">
                  {navigatedVerse.meaning && <div className="verse-label">English:</div>}
                  <div className="verse-content-text">{navigatedVerse.text}</div>
                </div>
              </div>
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
    </div>
  );
}

export default App;
