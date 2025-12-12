import { useState, useEffect, useMemo, useRef } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import type { Verse, VedaMetadata } from '../types';
import './SuktaNavigator.css';

interface SuktaNavigatorProps {
  verses: Verse[];
  metadata: VedaMetadata;
  onNavigate: (verses: Verse[]) => void;
}

export default function SuktaNavigator({ verses, metadata, onNavigate }: SuktaNavigatorProps) {
  const [selectedMandala, setSelectedMandala] = useState<number | ''>('');
  const [selectedAdhyaya, setSelectedAdhyaya] = useState<number | ''>(''); // For Satapatha only
  const [selectedHymn, setSelectedHymn] = useState<number | ''>('');
  const [selectedVerse, setSelectedVerse] = useState<number | ''>('');
  const [currentVerses, setCurrentVerses] = useState<Verse[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  // Track if we're doing programmatic navigation to prevent reset effects
  const isNavigatingRef = useRef(false);

  const isSatapatha = metadata.id === 'satapatha_brahmana';

  // Get unique mandalas/books
  const mandalas = useMemo(() => {
    const unique = Array.from(new Set(verses.map(v => v.mandala))).sort((a, b) => a - b);
    return unique;
  }, [verses]);

  // Get adhyayas for selected Kanda (Satapatha only)
  const adhyayas = useMemo(() => {
    if (!isSatapatha || selectedMandala === '') return [];
    const filteredVerses = verses.filter(v => v.mandala === selectedMandala);
    const unique = new Set<number>();
    for (const v of filteredVerses) {
      const parts = v.reference.split('.');
      if (parts.length >= 2) {
        unique.add(parseInt(parts[1])); // Adhyaya
      }
    }
    return Array.from(unique).sort((a, b) => a - b);
  }, [verses, selectedMandala, isSatapatha]);

  // Get brahmanas for selected Adhyaya (Satapatha only)
  const brahmanas = useMemo(() => {
    if (!isSatapatha || selectedMandala === '' || selectedAdhyaya === '') return [];
    const filteredVerses = verses.filter(v => {
      if (v.mandala !== selectedMandala) return false;
      const parts = v.reference.split('.');
      return parts.length >= 2 && parseInt(parts[1]) === selectedAdhyaya;
    });
    const unique = new Set<number>();
    for (const v of filteredVerses) {
      const parts = v.reference.split('.');
      if (parts.length >= 3) {
        unique.add(parseInt(parts[2])); // Brahmana
      }
    }
    return Array.from(unique).sort((a, b) => a - b);
  }, [verses, selectedMandala, selectedAdhyaya, isSatapatha]);

  // Get hymns for selected mandala (non-Satapatha)
  const hymns = useMemo(() => {
    if (isSatapatha || selectedMandala === '') return [];
    const filteredVerses = verses.filter(v => v.mandala === selectedMandala);
    const unique = Array.from(
      new Set(filteredVerses.map(v => v.hymn))
    ).sort((a, b) => a - b);
    return unique.map(h => ({ hymn: h, label: String(h) }));
  }, [verses, selectedMandala, isSatapatha]);

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
    if (isSatapatha) {
      setSelectedAdhyaya('');
    }
    setSelectedHymn('');
    if (metadata.hasThirdLevel) {
      setSelectedVerse('');
    }
  }, [selectedMandala, metadata.hasThirdLevel, isSatapatha]);

  // Reset Brahmana when Adhyaya changes (Satapatha only)
  useEffect(() => {
    if (isSatapatha) {
      setSelectedHymn('');
    }
  }, [selectedAdhyaya, isSatapatha]);

  useEffect(() => {
    // Skip reset if we're doing programmatic navigation
    if (isNavigatingRef.current) {
      isNavigatingRef.current = false;
      return;
    }
    if (metadata.hasThirdLevel) {
      setSelectedVerse('');
    } else {
      // For 2-level vedas, automatically set verse to 1
      setSelectedVerse(1);
    }
  }, [selectedHymn, metadata.hasThirdLevel]);

  // Navigate to selected verse(s)
  useEffect(() => {
    let canNavigate = false;
    let foundVerses: Verse[] = [];

    if (isSatapatha) {
      // Satapatha: need Kanda + Adhyaya + Brahmana
      canNavigate = selectedMandala !== '' && selectedAdhyaya !== '' && selectedHymn !== '';
      if (canNavigate) {
        foundVerses = verses.filter(v => {
          if (v.mandala !== selectedMandala) return false;
          const parts = v.reference.split('.');
          return parts.length >= 3 &&
                 parseInt(parts[1]) === selectedAdhyaya &&
                 parseInt(parts[2]) === selectedHymn;
        }).sort((a, b) => a.verse - b.verse);
      }
    } else if (metadata.hasThirdLevel) {
      // 3-level vedas: need all three
      canNavigate = selectedMandala !== '' && selectedHymn !== '' && selectedVerse !== '';
      if (canNavigate) {
        foundVerses = verses.filter(
          v => v.mandala === selectedMandala &&
               v.hymn === selectedHymn &&
               v.verse === selectedVerse
        );
      }
    } else {
      // 2-level vedas
      canNavigate = selectedMandala !== '' && selectedHymn !== '';
      if (canNavigate) {
        foundVerses = verses.filter(
          v => v.mandala === selectedMandala && v.hymn === selectedHymn
        ).sort((a, b) => a.verse - b.verse);
      }
    }

    if (canNavigate && foundVerses.length > 0) {
      setCurrentVerses(foundVerses);
      onNavigate(foundVerses);
    }
  }, [selectedMandala, selectedAdhyaya, selectedHymn, selectedVerse, verses, onNavigate, metadata.hasThirdLevel, isSatapatha]);

  // Get unique sections for navigation
  const uniqueSections = useMemo(() => {
    if (isSatapatha) {
      // For Satapatha: unique Kanda.Adhyaya.Brahmana combinations
      const sections: { mandala: number; adhyaya: number; brahmana: number }[] = [];
      const seen = new Set<string>();
      for (const v of verses) {
        const parts = v.reference.split('.');
        if (parts.length >= 3) {
          const key = `${parts[0]}-${parts[1]}-${parts[2]}`;
          if (!seen.has(key)) {
            seen.add(key);
            sections.push({
              mandala: parseInt(parts[0]),
              adhyaya: parseInt(parts[1]),
              brahmana: parseInt(parts[2])
            });
          }
        }
      }
      return sections.sort((a, b) => {
        if (a.mandala !== b.mandala) return a.mandala - b.mandala;
        if (a.adhyaya !== b.adhyaya) return a.adhyaya - b.adhyaya;
        return a.brahmana - b.brahmana;
      });
    } else {
      // For other vedas: unique mandala.hymn combinations
      const hymns: { mandala: number; hymn: number }[] = [];
      const seen = new Set<string>();
      for (const v of verses) {
        const key = `${v.mandala}-${v.hymn}`;
        if (!seen.has(key)) {
          seen.add(key);
          hymns.push({ mandala: v.mandala, hymn: v.hymn });
        }
      }
      return hymns.sort((a, b) => a.mandala !== b.mandala ? a.mandala - b.mandala : a.hymn - b.hymn);
    }
  }, [verses, isSatapatha]);

  // Get all verses sorted for verse-level navigation (3-level vedas)
  const allVersesSorted = useMemo(() => {
    if (!metadata.hasThirdLevel || isSatapatha) return [];
    return [...verses].sort((a, b) => {
      if (a.mandala !== b.mandala) return a.mandala - b.mandala;
      if (a.hymn !== b.hymn) return a.hymn - b.hymn;
      return a.verse - b.verse;
    });
  }, [verses, metadata.hasThirdLevel, isSatapatha]);

  const handlePrevious = () => {
    if (currentVerses.length === 0) return;

    if (isSatapatha) {
      const parts = currentVerses[0].reference.split('.');
      const currentIdx = (uniqueSections as { mandala: number; adhyaya: number; brahmana: number }[]).findIndex(
        s => s.mandala === parseInt(parts[0]) && s.adhyaya === parseInt(parts[1]) && s.brahmana === parseInt(parts[2])
      );
      if (currentIdx > 0) {
        const prev = (uniqueSections as { mandala: number; adhyaya: number; brahmana: number }[])[currentIdx - 1];
        setSelectedMandala(prev.mandala);
        setSelectedAdhyaya(prev.adhyaya);
        setSelectedHymn(prev.brahmana);
      } else {
        setModalMessage('You are at the first brahmana.');
        setShowModal(true);
      }
    } else if (metadata.hasThirdLevel) {
      // For 3-level vedas: navigate verse by verse
      const currentVerse = currentVerses[0];
      const currentIdx = allVersesSorted.findIndex(
        v => v.mandala === currentVerse.mandala && v.hymn === currentVerse.hymn && v.verse === currentVerse.verse
      );
      if (currentIdx > 0) {
        const prev = allVersesSorted[currentIdx - 1];
        // Set flag to prevent useEffect from resetting verse
        isNavigatingRef.current = true;
        setSelectedMandala(prev.mandala);
        setSelectedHymn(prev.hymn);
        setSelectedVerse(prev.verse);
      } else {
        setModalMessage(`You are at the first ${metadata.verseLabel.toLowerCase()}.`);
        setShowModal(true);
      }
    } else {
      // For 2-level vedas: navigate hymn by hymn
      const currentHymn = currentVerses[0];
      const currentIdx = (uniqueSections as { mandala: number; hymn: number }[]).findIndex(
        h => h.mandala === currentHymn.mandala && h.hymn === currentHymn.hymn
      );
      if (currentIdx > 0) {
        const prev = (uniqueSections as { mandala: number; hymn: number }[])[currentIdx - 1];
        setSelectedMandala(prev.mandala);
        setSelectedHymn(prev.hymn);
      } else {
        setModalMessage(`You are at the first ${metadata.hymnLabel.toLowerCase()}.`);
        setShowModal(true);
      }
    }
  };

  const handleNext = () => {
    if (currentVerses.length === 0) return;

    if (isSatapatha) {
      const parts = currentVerses[0].reference.split('.');
      const currentIdx = (uniqueSections as { mandala: number; adhyaya: number; brahmana: number }[]).findIndex(
        s => s.mandala === parseInt(parts[0]) && s.adhyaya === parseInt(parts[1]) && s.brahmana === parseInt(parts[2])
      );
      if (currentIdx < uniqueSections.length - 1) {
        const next = (uniqueSections as { mandala: number; adhyaya: number; brahmana: number }[])[currentIdx + 1];
        setSelectedMandala(next.mandala);
        setSelectedAdhyaya(next.adhyaya);
        setSelectedHymn(next.brahmana);
      } else {
        setModalMessage('You are at the last brahmana.');
        setShowModal(true);
      }
    } else if (metadata.hasThirdLevel) {
      // For 3-level vedas: navigate verse by verse
      const currentVerse = currentVerses[0];
      const currentIdx = allVersesSorted.findIndex(
        v => v.mandala === currentVerse.mandala && v.hymn === currentVerse.hymn && v.verse === currentVerse.verse
      );
      if (currentIdx < allVersesSorted.length - 1) {
        const next = allVersesSorted[currentIdx + 1];
        // Set flag to prevent useEffect from resetting verse
        isNavigatingRef.current = true;
        setSelectedMandala(next.mandala);
        setSelectedHymn(next.hymn);
        setSelectedVerse(next.verse);
      } else {
        setModalMessage(`You are at the last ${metadata.verseLabel.toLowerCase()}.`);
        setShowModal(true);
      }
    } else {
      // For 2-level vedas: navigate hymn by hymn
      const currentHymn = currentVerses[0];
      const currentIdx = (uniqueSections as { mandala: number; hymn: number }[]).findIndex(
        h => h.mandala === currentHymn.mandala && h.hymn === currentHymn.hymn
      );
      if (currentIdx < uniqueSections.length - 1) {
        const next = (uniqueSections as { mandala: number; hymn: number }[])[currentIdx + 1];
        setSelectedMandala(next.mandala);
        setSelectedHymn(next.hymn);
      } else {
        setModalMessage(`You are at the last ${metadata.hymnLabel.toLowerCase()}.`);
        setShowModal(true);
      }
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
          {/* Kanda/Mandala dropdown - always shown */}
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

          {/* Satapatha: Adhyaya dropdown */}
          {isSatapatha && (
            <select
              value={selectedAdhyaya}
              onChange={(e) => setSelectedAdhyaya(e.target.value ? parseInt(e.target.value) : '')}
              className="navigator-select"
              disabled={selectedMandala === ''}
            >
              <option value="">Adhyaya</option>
              {adhyayas.map(a => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          )}

          {/* Satapatha: Brahmana dropdown */}
          {isSatapatha && (
            <select
              value={selectedHymn}
              onChange={(e) => setSelectedHymn(e.target.value ? parseInt(e.target.value) : '')}
              className="navigator-select"
              disabled={selectedAdhyaya === ''}
            >
              <option value="">{metadata.hymnLabel}</option>
              {brahmanas.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          )}

          {/* Non-Satapatha: Hymn dropdown */}
          {!isSatapatha && (
            <select
              value={selectedHymn}
              onChange={(e) => setSelectedHymn(e.target.value ? parseInt(e.target.value) : '')}
              className="navigator-select"
              disabled={selectedMandala === ''}
            >
              <option value="">{metadata.hymnLabel}</option>
              {hymns.map(h => (
                <option key={h.hymn} value={h.hymn}>{h.label}</option>
              ))}
            </select>
          )}

          {/* Non-Satapatha 3-level: Verse dropdown */}
          {!isSatapatha && metadata.hasThirdLevel && (
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
            disabled={currentVerses.length === 0}
            title={`Previous ${metadata.hymnLabel.toLowerCase()}`}
          >
            <ChevronLeft size={18} />
            Previous
          </button>
          <button
            onClick={handleNext}
            className="nav-button next-button"
            disabled={currentVerses.length === 0}
            title={`Next ${metadata.hymnLabel.toLowerCase()}`}
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
