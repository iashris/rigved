import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { SearchResult } from '../types';

interface ResultsDisplayProps {
  results: SearchResult[];
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  
  if (!results || results.length === 0) {
    return null;
  }
  
  const toggleExpanded = (word: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(word)) {
      newExpanded.delete(word);
    } else {
      newExpanded.add(word);
    }
    setExpandedResults(newExpanded);
  };
  
  return (
    <div className="results-display">
      <h3>Search Results</h3>
      
      {results.map(result => (
        <div key={result.word} className="result-item">
          <div className="result-header">
            <h4>{result.word}</h4>
            <div className="result-stats">
              <span className="stat-badge">{result.totalMatches} matches</span>
              <span className="stat-badge">
                {((result.totalMatches / result.mandalaSizes.reduce((a, b) => a + b, 0)) * 100).toFixed(2)}% of corpus
              </span>
              <button
                className="expand-btn"
                onClick={() => toggleExpanded(result.word)}
              >
                {expandedResults.has(result.word) ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>
            </div>
          </div>
          
          {expandedResults.has(result.word) && (
            <div className="result-details">
              <div className="mandala-breakdown">
                <h5>Distribution by Mandala:</h5>
                <div className="mandala-grid">
                  {result.mandalaCounts.map((count, idx) => (
                    <div key={idx} className="mandala-item">
                      <strong>M{idx + 1}:</strong>
                      <span>{count} ({result.mandalaPercentages[idx].toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="sample-matches">
                <h5>Sample Verses (showing first 10):</h5>
                <div className="verses-list">
                  {result.matches.slice(0, 10).map((verse, idx) => (
                    <div key={idx} className="verse-item">
                      <span className="verse-ref">{verse.reference}:</span>
                      <span className="verse-text">{verse.text.substring(0, 200)}...</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}