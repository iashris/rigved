import { useState, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import type { Verse, VedaMetadata } from '../types';
import './SuktaNavigator.css';

interface SuktaNavigatorProps {
  verses: Verse[];
  metadata: VedaMetadata;
  onNavigate: (verse: Verse) => void;
}

export default function SuktaNavigator({ verses, metadata, onNavigate }: SuktaNavigatorProps) {
  const [selectedMandala, setSelectedMandala] = useState<number | ''>('');
  const [selectedHymn, setSelectedHymn] = useState<number | ''>('');
  const [selectedVerse, setSelectedVerse] = useState<number | ''>('');
  const [currentVerse, setCurrentVerse] = useState<Verse | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  // Get unique mandalas/books
  const mandalas = useMemo(() => {
    const unique = Array.from(new Set(verses.map(v => v.mandala))).sort((a, b) => a - b);
    return unique;
  }, [verses]);

  // Get hymns for selected mandala
  const hymns = useMemo(() => {
    if (selectedMandala === '') return [];
    const unique = Array.from(
      new Set(verses.filter(v => v.mandala === selectedMandala).map(v => v.hymn))
    ).sort((a, b) => a - b);
    return unique;
  }, [verses, selectedMandala]);

  // Get verses for selected mandala and hymn
  const versesInHymn = useMemo(() => {
    if (selectedMandala === '' || selectedHymn === '') return [];
    const unique = Array.from(
      new Set(
        verses
          .filter(v => v.mandala === selectedMandala && v.hymn === selectedHymn)
          .map(v => v.verse)
      )
    ).sort((a, b) => a - b);
    return unique;
  }, [verses, selectedMandala, selectedHymn]);

  // Reset dependent dropdowns when parent changes
  useEffect(() => {
    setSelectedHymn('');
    if (metadata.hasThirdLevel) {
      setSelectedVerse('');
    }
  }, [selectedMandala, metadata.hasThirdLevel]);

  useEffect(() => {
    if (metadata.hasThirdLevel) {
      setSelectedVerse('');
    } else {
      // For 2-level vedas, automatically set verse to 1
      setSelectedVerse(1);
    }
  }, [selectedHymn, metadata.hasThirdLevel]);

  // Navigate to selected verse
  useEffect(() => {
    // For 2-level vedas (like white Yajurveda), navigate when mandala and hymn are selected
    // For 3-level vedas, require all three selections
    const canNavigate = metadata.hasThirdLevel
      ? selectedMandala !== '' && selectedHymn !== '' && selectedVerse !== ''
      : selectedMandala !== '' && selectedHymn !== '';

    if (canNavigate) {
      const foundVerse = verses.find(
        v => v.mandala === selectedMandala &&
             v.hymn === selectedHymn &&
             (metadata.hasThirdLevel ? v.verse === selectedVerse : true)
      );

      if (foundVerse) {
        setCurrentVerse(foundVerse);
        onNavigate(foundVerse);
      }
    }
  }, [selectedMandala, selectedHymn, selectedVerse, verses, onNavigate, metadata.hasThirdLevel]);

  const handlePrevious = () => {
    if (!currentVerse) return;

    const currentIndex = verses.findIndex(
      v => v.mandala === currentVerse.mandala &&
           v.hymn === currentVerse.hymn &&
           (metadata.hasThirdLevel ? v.verse === currentVerse.verse : true)
    );

    if (currentIndex > 0) {
      const prevVerse = verses[currentIndex - 1];
      setSelectedMandala(prevVerse.mandala);
      setSelectedHymn(prevVerse.hymn);
      if (metadata.hasThirdLevel) {
        setSelectedVerse(prevVerse.verse);
      } else {
        setSelectedVerse(1);
      }
      setCurrentVerse(prevVerse);
      onNavigate(prevVerse);
    } else {
      setModalMessage('You are at the first verse.');
      setShowModal(true);
    }
  };

  const handleNext = () => {
    if (!currentVerse) return;

    const currentIndex = verses.findIndex(
      v => v.mandala === currentVerse.mandala &&
           v.hymn === currentVerse.hymn &&
           (metadata.hasThirdLevel ? v.verse === currentVerse.verse : true)
    );

    if (currentIndex < verses.length - 1) {
      const nextVerse = verses[currentIndex + 1];
      setSelectedMandala(nextVerse.mandala);
      setSelectedHymn(nextVerse.hymn);
      if (metadata.hasThirdLevel) {
        setSelectedVerse(nextVerse.verse);
      } else {
        setSelectedVerse(1);
      }
      setCurrentVerse(nextVerse);
      onNavigate(nextVerse);
    } else {
      setModalMessage('You are at the last verse.');
      setShowModal(true);
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setModalMessage('');
  };

  return (
    <>
      <div className="sukta-navigator">
        <div className="navigator-dropdowns">
          <select
            value={selectedMandala}
            onChange={(e) => setSelectedMandala(e.target.value ? parseInt(e.target.value) : '')}
            className="navigator-select"
          >
            <option value="">{metadata.bookLabel}</option>
            {mandalas.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>

          <select
            value={selectedHymn}
            onChange={(e) => setSelectedHymn(e.target.value ? parseInt(e.target.value) : '')}
            className="navigator-select"
            disabled={selectedMandala === ''}
          >
            <option value="">{metadata.hymnLabel}</option>
            {hymns.map(h => (
              <option key={h} value={h}>{h}</option>
            ))}
          </select>

          {metadata.hasThirdLevel && (
            <select
              value={selectedVerse}
              onChange={(e) => setSelectedVerse(e.target.value ? parseInt(e.target.value) : '')}
              className="navigator-select"
              disabled={selectedHymn === ''}
            >
              <option value="">{metadata.verseLabel}</option>
              {versesInHymn.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          )}
        </div>

        <div className="navigator-buttons">
          <button
            onClick={handlePrevious}
            className="nav-button prev-button"
            disabled={!currentVerse}
            title="Previous verse"
          >
            <ChevronLeft size={18} />
            Previous
          </button>
          <button
            onClick={handleNext}
            className="nav-button next-button"
            disabled={!currentVerse}
            title="Next verse"
          >
            Next
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Notice</h3>
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
