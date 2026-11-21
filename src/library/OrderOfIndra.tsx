/** The Order of Indra: its vajra, drawn as the Order draws it (orderofindra.com), in the theme's colour, and a line at the foot of the home page. */

export const ORDER_URL = 'https://orderofindra.com/';

export function Vajra({ size = 22 }: { size?: number }) {
  const prong = (
    <>
      <path d="M50 4 L56 72 L44 72 Z" />
      <path d="M43 78 C 24 76, 15 58, 17 30 C 23 52, 33 63, 46 70 Z" />
      <path d="M57 78 C 76 76, 85 58, 83 30 C 77 52, 67 63, 54 70 Z" />
      <rect x="34" y="72" width="32" height="8" rx="2" />
      <rect x="45" y="80" width="10" height="20" />
    </>
  );
  return (
    <svg viewBox="14 0 72 200" height={size} width={size * 0.36} fill="currentColor" aria-hidden="true" focusable="false">
      {prong}
      <g transform="rotate(180 50 100)">{prong}</g>
      <rect x="39" y="96" width="22" height="8" rx="4" />
    </svg>
  );
}

/** At the foot of the home page: one quiet line about the Order, and its link. */
export function OrderNote() {
  return (
    <p className="order-note">
      <Vajra size={14} />
      <span>
        <a href={ORDER_URL} target="_blank" rel="noopener">
          Order of Indra
        </a>{' '}
        · a new order returning to the Vedas and the Upanishads
      </span>
    </p>
  );
}
