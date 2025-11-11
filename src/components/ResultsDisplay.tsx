import React, { useState } from "react";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import type { SearchResult, VedaMetadata } from "../types";

interface ResultsDisplayProps {
  results: SearchResult[];
  metadata: VedaMetadata;
}

function highlightMatches(
  text: string,
  searchWord: string
): React.ReactElement {
  // Normalize the search word for matching
  const normalizeText = (str: string) =>
    str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const normalizedSearchWord = normalizeText(searchWord);

  // Split text but preserve the original characters
  const parts: React.ReactElement[] = [];
  let lastIndex = 0;
  let match;

  // Find matches in normalized text but extract from original text
  const normalizedText = normalizeText(text);
  const matchRegex = new RegExp(
    `\\b${normalizedSearchWord.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`,
    "gi"
  );

  while ((match = matchRegex.exec(normalizedText)) !== null) {
    // Add text before match
    if (match.index > lastIndex) {
      parts.push(
        <span key={`text-${lastIndex}`}>
          {text.substring(lastIndex, match.index)}
        </span>
      );
    }

    // Add highlighted match (using original text)
    const matchedText = text.substring(
      match.index,
      match.index + match[0].length
    );
    parts.push(<mark key={`mark-${match.index}`}>{matchedText}</mark>);

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(
      <span key={`text-${lastIndex}`}>{text.substring(lastIndex)}</span>
    );
  }

  return <>{parts}</>;
}

export default function ResultsDisplay({ results, metadata }: ResultsDisplayProps) {
  const [expandedResults, setExpandedResults] = useState<Set<string>>(
    new Set()
  );
  const [copiedVerse, setCopiedVerse] = useState<string | null>(null);

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

  const copyVerseToClipboard = async (verse: { reference: string; text: string; meaning?: string; vedaId: string }, verseKey: string) => {
    const vedaPrefix = verse.vedaId === 'rigveda' ? 'RV' : 'AV';
    const formattedText = `${vedaPrefix} ${verse.reference}\n\n${verse.meaning || ''}\n\n${verse.text}`;

    try {
      await navigator.clipboard.writeText(formattedText);
      setCopiedVerse(verseKey);
      setTimeout(() => setCopiedVerse(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const buildVerseLink = (reference: string) => {
    if (metadata.id !== "rigveda") {
      return null;
    }
    const formattedRef = reference
      .split(".")
      .map((num) => parseInt(num, 10))
      .join(".");
    return `https://vedaweb.uni-koeln.de/rigveda/view/id/${formattedRef}`;
  };

  return (
    <div className="results-display">
      <h3>Search Results</h3>

      {results.map((result) => (
        <div key={result.word} className="result-item">
          <div className="result-header">
            <h4>{result.word}</h4>
            <div className="result-stats">
              <span className="stat-badge">{result.totalMatches} matches</span>
              <span className="stat-badge">
                {(
                  (result.totalMatches /
                    result.mandalaSizes.reduce((a, b) => a + b, 0)) *
                  100
                ).toFixed(2)}
                % of corpus
              </span>
              <button
                className="expand-btn"
                onClick={() => toggleExpanded(result.word)}
              >
                {expandedResults.has(result.word) ? (
                  <ChevronUp size={20} />
                ) : (
                  <ChevronDown size={20} />
                )}
              </button>
            </div>
          </div>

          {expandedResults.has(result.word) && (
            <div className="result-details">
              <div className="mandala-breakdown">
                <h5>Distribution by {metadata.bookLabel}:</h5>
                <div className="mandala-grid">
                  {result.mandalaCounts.map((count, idx) => (
                    <div key={idx} className="mandala-item">
                      <strong>
                        {metadata.shortLabel}
                        {idx + 1}:
                      </strong>
                      <span>
                        {count} ({result.mandalaPercentages[idx].toFixed(1)}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="all-matches">
                <h5>All Matches ({result.matches.length}):</h5>
                <div className="verses-list">
                  {result.matches.map((verse, idx) => {
                    const verseLink = buildVerseLink(verse.reference);
                    const verseKey = `${result.word}-${verse.reference}`;
                    const isCopied = copiedVerse === verseKey;
                    return (
                      <div key={idx} className="verse-item">
                        <div className="verse-header-row">
                          {verseLink ? (
                            <a
                              href={verseLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="verse-ref"
                            >
                              {verse.reference}
                            </a>
                          ) : (
                            <span className="verse-ref">{verse.reference}</span>
                          )}
                          <button
                            className="copy-verse-btn"
                            onClick={() => copyVerseToClipboard(verse, verseKey)}
                            title="Copy verse"
                          >
                            {isCopied ? <Check size={16} /> : <Copy size={16} />}
                          </button>
                        </div>
                        <div className="verse-content">
                        <div className="verse-original">
                          <strong>Original: </strong>
                          {highlightMatches(verse.text, result.word)}
                        </div>
                        {verse.meaning && (
                          <div className="verse-meaning">
                            <strong>Meaning: </strong>
                            {verse.meaning}
                          </div>
                        )}
                      </div>
                    </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
