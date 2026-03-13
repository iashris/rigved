import type { VedaId } from '../types';
import { VEDA_CONFIGS } from '../types';

interface VedaSelectorProps {
  currentVeda: VedaId;
  onChange: (veda: VedaId) => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  samhita: "Samhitas",
  brahmana: "Brahmanas",
  aranyaka: "Aranyakas",
  upanishad: "Upanishads",
  epic: "Epics & Smritis",
};

const CATEGORY_ORDER = ["samhita", "brahmana", "aranyaka", "upanishad", "epic"];

export default function VedaSelector({ currentVeda, onChange }: VedaSelectorProps) {
  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    label: CATEGORY_LABELS[cat],
    texts: Object.values(VEDA_CONFIGS).filter((c) => c.category === cat),
  }));

  return (
    <div className="veda-selector">
      <span className="selector-label">Corpus:</span>
      <select
        className="veda-select"
        value={currentVeda}
        onChange={(e) => onChange(e.target.value as VedaId)}
      >
        {grouped.map((group) => (
          <optgroup key={group.category} label={group.label}>
            {group.texts.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}
