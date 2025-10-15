import type { VedaId } from '../types';
import { VEDA_CONFIGS } from '../types';

interface VedaSelectorProps {
  currentVeda: VedaId;
  onChange: (veda: VedaId) => void;
}

export default function VedaSelector({ currentVeda, onChange }: VedaSelectorProps) {
  const options = Object.values(VEDA_CONFIGS);

  return (
    <div className="veda-selector">
      <span className="selector-label">Corpus:</span>
      <div className="button-group">
        {options.map((option) => (
          <button
            key={option.id}
            type="button"
            className={`control-btn ${currentVeda === option.id ? 'active' : ''}`}
            onClick={() => onChange(option.id)}
          >
            {option.name}
          </button>
        ))}
      </div>
    </div>
  );
}
