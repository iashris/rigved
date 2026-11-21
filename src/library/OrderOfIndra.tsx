/** The Order of Indra: its vajra, drawn as the Order draws it (orderofindra.com), in the theme's colour, and its word. */

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

const TENETS = [
  'Every person has the right to author their own life.',
  'Sincerity over performance.',
  'Question everything, as the Upanishads did.',
  'Joy carries no guilt. Celebration is sacred.',
];

/** On the home page: what the Order is, in its own words, and where to find it. */
export function OrderCard() {
  return (
    <aside className="order-card">
      <div className="order-card-mark">
        <Vajra size={56} />
      </div>
      <div>
        <h2>The Order of Indra</h2>
        <p>
          A new order within the Hindu tradition, going back to its oldest source: the Vedas and the Upanishads. Not to replace what
          came after. To remember what came first. Every text it draws from is open to read here.
        </p>
        <ul>
          {TENETS.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
        <p className="order-card-links">
          <a href={ORDER_URL} target="_blank" rel="noopener">
            orderofindra.com ↗
          </a>
          <span>For the one.</span>
        </p>
      </div>
    </aside>
  );
}
