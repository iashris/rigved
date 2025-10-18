import { useState } from 'react';
import { Search, X } from 'lucide-react';
import type { Verse, VedaMetadata } from '../types';
import './SuktaNavigator.css';

interface SuktaNavigatorProps {
  verses: Verse[];
  metadata: VedaMetadata;
  onNavigate: (verse: Verse) => void;
}

export default function SuktaNavigator({ verses, metadata, onNavigate }: SuktaNavigatorProps) {
  const [input, setInput] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  const handleNavigate = () => {
    if (!input.trim()) return;

    // Parse the input (e.g., "6.8.1" or "6-8-1")
    const parts = input.trim().split(/[.\-_]/);

    if (parts.length !== 3) {
      setModalMessage('Invalid format. Please use format: mandala.hymn.verse (e.g., 6.8.1)');
      setShowModal(true);
      return;
    }

    const mandala = parseInt(parts[0], 10);
    const hymn = parseInt(parts[1], 10);
    const verse = parseInt(parts[2], 10);

    if (isNaN(mandala) || isNaN(hymn) || isNaN(verse)) {
      setModalMessage('Invalid numbers. Please use format: mandala.hymn.verse (e.g., 6.8.1)');
      setShowModal(true);
      return;
    }

    // Find the verse in the current veda
    const foundVerse = verses.find(
      v => v.mandala === mandala && v.hymn === hymn && v.verse === verse
    );

    if (foundVerse) {
      onNavigate(foundVerse);
      setInput('');
    } else {
      setModalMessage(
        `${metadata.bookLabel} ${mandala}.${hymn}.${verse} does not exist in the ${metadata.name}.`
      );
      setShowModal(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNavigate();
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setModalMessage('');
  };

  return (
    <>
      <div className="sukta-navigator">
        <div className="navigator-input-group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Go to ${metadata.bookLabel.toLowerCase()} (e.g., 6.8.1)`}
            className="navigator-input"
          />
          <button
            onClick={handleNavigate}
            className="navigate-button"
            disabled={!input.trim()}
            title="Navigate to verse"
          >
            <Search size={18} />
          </button>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Not Found</h3>
              <button onClick={closeModal} className="modal-close">
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p>{modalMessage}</p>
            </div>
            <div className="modal-footer">
              <button onClick={closeModal} className="modal-button">
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
