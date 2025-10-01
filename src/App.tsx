import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import Controls from './components/Controls';
import ChartVisualization from './components/ChartVisualization';
import ResultsDisplay from './components/ResultsDisplay';
import { loadRigvedaData, searchWord } from './utils/dataProcessor';
import type { Verse, SearchResult, OrderType, DisplayMode } from './types';
import { BookOpen, Share2 } from 'lucide-react';
import './App.css';

function App() {
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [orderType, setOrderType] = useState<OrderType>('sequential');
  const [displayMode, setDisplayMode] = useState<DisplayMode>('absolute');
  const [error, setError] = useState<string>('');
  const [searchTerms, setSearchTerms] = useState<string[]>([]);

  // Load search params from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    const order = params.get('order') as OrderType;
    const mode = params.get('mode') as DisplayMode;

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
    loadRigvedaData().then(data => {
      setVerses(data);
      setLoading(false);
      console.log(`Loaded ${data.length} verses`);
    }).catch(err => {
      setError('Failed to load Rigveda data');
      setLoading(false);
      console.error(err);
    });
  }, []);

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
      const result = searchWord(verses, [term], false);
      if (result) {
        results.push(result);
      }
    });

    if (results.length === 0) {
      setError('No matches found for the given search terms');
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
  }, [orderType, displayMode]);
  
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading Rigveda data...</p>
      </div>
    );
  }
  
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <BookOpen size={32} />
          <h1>Rigveda Analysis Tool</h1>
          <p className="subtitle">Search and visualize word distributions across the 10 Mandalas</p>
        </div>
      </header>
      
      <main className="app-main">
        <section className="search-section">
          <SearchBar onSearch={handleSearch} />
          {error && <div className="error-message">{error}</div>}
        </section>
        
        {searchResults.length > 0 && (
          <>
            <section className="controls-section">
              <div className="controls-wrapper">
                <Controls
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
              />
            </section>
            
            <section className="results-section">
              <ResultsDisplay results={searchResults} />
            </section>
          </>
        )}
        
        <footer className="app-footer">
          <div className="footer-content">
            <p>Data source: Griffith's translation of the Rigveda</p>
            <p>Chronological order based on Talegeri's analysis</p>
            <p className="corpus-info">
              Total corpus: {verses.length} verses across 10 Mandalas
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;