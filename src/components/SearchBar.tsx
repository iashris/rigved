import { useState } from 'react';
import { Search, Plus, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (terms: string[]) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [searchTerms, setSearchTerms] = useState<string[]>(['']);
  
  const handleTermChange = (index: number, value: string) => {
    const newTerms = [...searchTerms];
    newTerms[index] = value;
    setSearchTerms(newTerms);
  };
  
  const addSearchTerm = () => {
    setSearchTerms([...searchTerms, '']);
  };
  
  const removeSearchTerm = (index: number) => {
    const newTerms = searchTerms.filter((_, i) => i !== index);
    setSearchTerms(newTerms.length > 0 ? newTerms : ['']);
  };
  
  const handleSearch = () => {
    const validTerms = searchTerms.filter(term => term.trim());
    if (validTerms.length > 0) {
      onSearch(validTerms);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };
  
  return (
    <div className="search-container">
      <div className="search-help">
        <p>💡 Tip: You can search without diacritics! Try "varuna" instead of "varuṇa", or "agni" for "agnī"</p>
      </div>
      <div className="search-terms">
        {searchTerms.map((term, index) => (
          <div key={index} className="search-term-row">
            <input
              type="text"
              value={term}
              onChange={(e) => handleTermChange(index, e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Enter search term ${index + 1}...`}
              className="search-input"
            />
            {searchTerms.length > 1 && (
              <button
                onClick={() => removeSearchTerm(index)}
                className="btn-remove"
                title="Remove term"
              >
                <X size={20} />
              </button>
            )}
          </div>
        ))}
      </div>
      
      <div className="search-actions">
        <button
          onClick={addSearchTerm}
          className="btn-add"
          title="Add another search term"
        >
          <Plus size={20} />
          Add Term
        </button>
        
        <button
          onClick={handleSearch}
          className="btn-search"
          disabled={!searchTerms.some(term => term.trim())}
        >
          <Search size={20} />
          Search
        </button>
      </div>
    </div>
  );
}