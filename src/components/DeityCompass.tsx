import { useState, useEffect, useRef, useCallback } from 'react';

// ── Time periods ──
const ERAS = [
  { id: 'vedic', label: 'Vedic (1500–800 BCE)', year: -1200 },
  { id: 'upanishadic', label: 'Upanishadic (800–400 BCE)', year: -600 },
  { id: 'epic', label: 'Epic Period (400 BCE–400 CE)', year: 0 },
  { id: 'puranic', label: 'Puranic (400–1000 CE)', year: 700 },
  { id: 'modern', label: 'Modern (1000 CE+)', year: 1200 },
] as const;

type EraId = (typeof ERAS)[number]['id'];

// ── Deity data ──
// x: -1 (ORDER) to +1 (DESIRE)
// y: -1 (BLEEDS/vulnerable) to +1 (TRANSCENDS/absolute)
interface DeitySnapshot {
  x: number;
  y: number;
  label?: string; // optional tooltip override per era
}

interface Deity {
  name: string;
  tradition: 'hindu' | 'greek' | 'norse' | 'abrahamic' | 'iranian' | 'vedic_concept';
  color: string;
  positions: Partial<Record<EraId, DeitySnapshot>>;
  note?: string;
}

const DEITIES: Deity[] = [
  // ── Hindu / Vedic ──
  {
    name: 'Indra',
    tradition: 'hindu',
    color: '#f59e0b',
    positions: {
      vedic:      { x: 0.85, y: -0.55, label: 'Supreme warrior-king, wants soma & glory' },
      upanishadic:{ x: 0.70, y: -0.65, label: 'Still powerful but questioned by sages' },
      epic:       { x: 0.55, y: -0.75, label: 'Humiliated by Ravana, cursed (Ahalya)' },
      puranic:    { x: 0.40, y: -0.85, label: 'Demoted to weather god, butt of jokes' },
      modern:     { x: 0.35, y: -0.90, label: 'Forgotten. Nobody builds Indra temples' },
    },
  },
  {
    name: 'Vishnu',
    tradition: 'hindu',
    color: '#3b82f6',
    positions: {
      vedic:      { x: -0.30, y: 0.10, label: 'Minor solar deity, three strides' },
      upanishadic:{ x: -0.20, y: 0.35, label: 'Rising, associated with cosmic order' },
      epic:       { x: 0.10, y: 0.65, label: 'Rama avatar — dharma king' },
      puranic:    { x: -0.15, y: 0.85, label: 'Supreme Brahman, preserver of universe' },
      modern:     { x: -0.20, y: 0.90, label: 'One of the Trinity, transcendent' },
    },
  },
  {
    name: 'Rudra → Shiva',
    tradition: 'hindu',
    color: '#8b5cf6',
    positions: {
      vedic:      { x: -0.20, y: -0.60, label: 'Rudra: feared outsider, sends disease & heals' },
      upanishadic:{ x: -0.10, y: -0.15, label: 'Shvetashvatara: becoming supreme' },
      epic:       { x: 0.15, y: 0.40, label: 'Mahadeva: destroyer + ascetic + lover' },
      puranic:    { x: 0.05, y: 0.80, label: 'Supreme Brahman (Shaiva tradition)' },
      modern:     { x: 0.00, y: 0.85, label: 'Transcends all categories' },
    },
  },
  {
    name: 'Krishna',
    tradition: 'hindu',
    color: '#06b6d4',
    positions: {
      upanishadic:{ x: 0.20, y: -0.30, label: 'Devakiputra: student of Ghora Angirasa (Chandogya)' },
      epic:       { x: 0.05, y: 0.25, label: 'Gita: dharma + desire unified, Vishvarupa' },
      puranic:    { x: 0.15, y: 0.50, label: 'Vrindavan lila + Bhagavata: love as theology' },
      modern:     { x: 0.00, y: 0.60, label: 'Center of everything. All quadrants at once' },
    },
  },
  {
    name: 'Varuna',
    tradition: 'hindu',
    color: '#64748b',
    positions: {
      vedic:      { x: -0.80, y: 0.60, label: 'Cosmic judge, keeper of ṛta, all-seeing' },
      upanishadic:{ x: -0.75, y: 0.30, label: 'Declining, merging into Bhrigu lore' },
      epic:       { x: -0.60, y: -0.10, label: 'Reduced to ocean god' },
      puranic:    { x: -0.55, y: -0.30, label: 'Minor dikpala, forgotten judge' },
    },
  },
  {
    name: 'Prajapati → Brahma',
    tradition: 'hindu',
    color: '#a3a3a3',
    positions: {
      vedic:      { x: -0.15, y: 0.70, label: 'Lord of creatures, cosmic creator' },
      upanishadic:{ x: -0.25, y: 0.80, label: 'Creator principle, father of gods' },
      epic:       { x: -0.35, y: 0.75, label: 'Brahma: creator but losing worship' },
      puranic:    { x: -0.40, y: 0.65, label: 'Cursed by Shiva, no temples, irrelevant' },
    },
  },
  {
    name: 'Kama',
    tradition: 'vedic_concept',
    color: '#f472b6',
    positions: {
      vedic:      { x: 0.70, y: 0.75, label: 'Cosmic desire: "kāma tad agre samavartatādhi"' },
      upanishadic:{ x: 0.50, y: 0.40, label: 'VS 7.48: "Desire is giver, Desire is receiver"' },
      epic:       { x: 0.60, y: -0.20, label: 'Manmatha: cupid figure, burned by Shiva' },
      puranic:    { x: 0.55, y: -0.50, label: 'Reduced to lust, one of six enemies' },
    },
  },
  {
    name: 'Agni',
    tradition: 'hindu',
    color: '#ef4444',
    positions: {
      vedic:      { x: 0.30, y: 0.15, label: 'Messenger between humans & gods, #2 in RV' },
      upanishadic:{ x: 0.10, y: 0.25, label: 'Ritual fire, Angirasa lineage carrier' },
      epic:       { x: -0.05, y: -0.10, label: 'Tired fire god, begs to rest' },
      puranic:    { x: -0.10, y: -0.25, label: 'Minor, ritualistic only' },
    },
  },

  // ── Greek ──
  {
    name: 'Zeus',
    tradition: 'greek',
    color: '#eab308',
    positions: {
      vedic:      { x: 0.80, y: -0.35, label: 'Sky father, thunderer (cognate of Dyaus)' },
      epic:       { x: 0.75, y: -0.25, label: 'King of Olympus, lusty & petty' },
      puranic:    { x: 0.70, y: -0.20, label: 'Never transcends. Stays human-like forever' },
    },
  },
  {
    name: 'Apollo',
    tradition: 'greek',
    color: '#fbbf24',
    positions: {
      vedic:      { x: 0.20, y: 0.30, label: 'Sun, music, order — proto-Krishna?' },
      epic:       { x: 0.15, y: 0.25, label: 'Beautiful, prophetic, but can be cruel' },
    },
  },
  {
    name: 'Prometheus',
    tradition: 'greek',
    color: '#fb923c',
    positions: {
      vedic:      { x: 0.70, y: -0.80, label: 'Stole fire for humans, punished eternally' },
      epic:       { x: 0.65, y: -0.85, label: 'Ultimate desire + ultimate suffering' },
    },
  },

  // ── Norse ──
  {
    name: 'Thor',
    tradition: 'norse',
    color: '#dc2626',
    positions: {
      vedic:      { x: 0.80, y: -0.45, label: 'Thunder warrior, Indra\'s twin (Mjolnir = Vajra)' },
      epic:       { x: 0.75, y: -0.40, label: 'Protector, monster-slayer, still drinks & fights' },
    },
  },
  {
    name: 'Odin',
    tradition: 'norse',
    color: '#991b1b',
    positions: {
      vedic:      { x: 0.40, y: -0.30, label: 'Wisdom-seeker, sacrificed eye, hanged himself' },
      epic:       { x: 0.35, y: 0.10, label: 'King of gods but also sorcerer, trickster' },
    },
  },

  // ── Abrahamic ──
  {
    name: 'Yahweh (early)',
    tradition: 'abrahamic',
    color: '#f5f5f4',
    positions: {
      vedic:      { x: 0.30, y: -0.20, label: 'Walks in Eden, regrets flood, wrestles Jacob' },
      upanishadic:{ x: -0.20, y: 0.30, label: 'Lawgiver at Sinai, "I am who I am"' },
      epic:       { x: -0.60, y: 0.70, label: 'Prophetic God: justice, mercy, judgment' },
      puranic:    { x: -0.80, y: 0.90, label: 'Absolute monotheism: perfect, formless' },
      modern:     { x: -0.85, y: 0.95, label: 'Allah / God: ultimate top-left' },
    },
  },
  {
    name: 'Jesus',
    tradition: 'abrahamic',
    color: '#e2e8f0',
    positions: {
      epic:       { x: 0.15, y: -0.40, label: 'God who bleeds, weeps, dies on cross' },
      puranic:    { x: -0.10, y: 0.50, label: 'Resurrected: human + divine synthesis' },
      modern:     { x: -0.05, y: 0.55, label: 'The Krishna move: God walks among us' },
    },
  },

  // ── Iranian ──
  {
    name: 'Ahura Mazda',
    tradition: 'iranian',
    color: '#22d3ee',
    positions: {
      vedic:      { x: -0.75, y: 0.55, label: 'Asura Medha = Varuna\'s twin across the border' },
      upanishadic:{ x: -0.80, y: 0.75, label: 'Zoroaster: one true God of truth & order' },
      epic:       { x: -0.85, y: 0.85, label: 'Cosmic dualist: pure order vs Angra Mainyu' },
    },
  },
];

// ── Tradition styles ──
const TRADITION_CONFIG: Record<string, { shape: 'circle' | 'diamond' | 'triangle' | 'square' | 'star'; label: string }> = {
  hindu:     { shape: 'circle',   label: 'Hindu / Vedic' },
  greek:     { shape: 'diamond',  label: 'Greek' },
  norse:     { shape: 'triangle', label: 'Norse' },
  abrahamic: { shape: 'square',   label: 'Abrahamic' },
  iranian:   { shape: 'star',     label: 'Iranian' },
  vedic_concept: { shape: 'circle', label: 'Vedic Concept' },
};

// ── Drawing helpers ──
function drawShape(
  ctx: CanvasRenderingContext2D,
  shape: string,
  cx: number,
  cy: number,
  r: number,
  color: string,
  alpha: number
) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.strokeStyle = 'rgba(0,0,0,0.4)';
  ctx.lineWidth = 1.5;

  switch (shape) {
    case 'diamond':
      ctx.beginPath();
      ctx.moveTo(cx, cy - r);
      ctx.lineTo(cx + r, cy);
      ctx.lineTo(cx, cy + r);
      ctx.lineTo(cx - r, cy);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      break;
    case 'triangle':
      ctx.beginPath();
      ctx.moveTo(cx, cy - r);
      ctx.lineTo(cx + r * 0.87, cy + r * 0.5);
      ctx.lineTo(cx - r * 0.87, cy + r * 0.5);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      break;
    case 'square':
      ctx.fillRect(cx - r * 0.75, cy - r * 0.75, r * 1.5, r * 1.5);
      ctx.strokeRect(cx - r * 0.75, cy - r * 0.75, r * 1.5, r * 1.5);
      break;
    case 'star': {
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const angle = (i * 4 * Math.PI) / 5 - Math.PI / 2;
        const method = i === 0 ? 'moveTo' : 'lineTo';
        ctx[method](cx + r * Math.cos(angle), cy + r * Math.sin(angle));
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      break;
    }
    default: // circle
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      break;
  }
  ctx.restore();
}

// ── Component ──
export default function DeityCompass() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [eraIndex, setEraIndex] = useState(0);
  const [showTrails, setShowTrails] = useState(true);
  const [hoveredDeity, setHoveredDeity] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);

  // Lerp helper
  const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

  // Get deity position for a given era index + progress
  const getDeityPos = useCallback((deity: Deity, eIdx: number, progress: number): { x: number; y: number; alpha: number } | null => {
    const eraIds = ERAS.map(e => e.id);

    // Find nearest positions before and after current era
    let beforeIdx = -1;
    let afterIdx = -1;

    for (let i = eIdx; i >= 0; i--) {
      if (deity.positions[eraIds[i]]) { beforeIdx = i; break; }
    }
    // For interpolation target, look at current+1 if we're animating forward
    const targetIdx = progress > 0 ? Math.min(eIdx + 1, ERAS.length - 1) : eIdx;
    for (let i = targetIdx; i < ERAS.length; i++) {
      if (deity.positions[eraIds[i]]) { afterIdx = i; break; }
    }

    if (beforeIdx === -1 && afterIdx === -1) return null;
    if (beforeIdx === -1) {
      const pos = deity.positions[eraIds[afterIdx]]!;
      // Fade in if we're approaching
      const fadeIn = afterIdx === eIdx ? 1 : afterIdx === eIdx + 1 ? progress * 0.5 : 0;
      return fadeIn > 0 ? { x: pos.x, y: pos.y, alpha: fadeIn } : null;
    }
    if (afterIdx === -1 || beforeIdx === afterIdx) {
      const pos = deity.positions[eraIds[beforeIdx]]!;
      return { x: pos.x, y: pos.y, alpha: beforeIdx <= eIdx ? 1 : 0.3 };
    }

    // Interpolate between before and after
    const posBefore = deity.positions[eraIds[beforeIdx]]!;
    const posAfter = deity.positions[eraIds[afterIdx]]!;

    if (beforeIdx === eIdx && afterIdx === eIdx + 1) {
      // We're animating between these two
      return {
        x: lerp(posBefore.x, posAfter.x, progress),
        y: lerp(posBefore.y, posAfter.y, progress),
        alpha: 1,
      };
    }

    // Snap to the nearest known position
    if (beforeIdx <= eIdx) {
      return { x: posBefore.x, y: posBefore.y, alpha: 1 };
    }
    return null;
  }, []);

  // Canvas drawing
  const draw = useCallback((eIdx: number, progress: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth;
    const H = canvas.clientHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Margins
    const margin = { top: 60, right: 30, bottom: 60, left: 30 };
    const plotW = W - margin.left - margin.right;
    const plotH = H - margin.top - margin.bottom;
    const cx = margin.left + plotW / 2;
    const cy = margin.top + plotH / 2;

    // Coordinate transform: data (-1..1) → pixel
    const toX = (v: number) => cx + v * (plotW / 2) * 0.88;
    const toY = (v: number) => cy - v * (plotH / 2) * 0.88; // flip y

    // Background
    ctx.fillStyle = '#0c0a09';
    ctx.fillRect(0, 0, W, H);

    // Quadrant fills
    const quadColors = [
      { x: cx, y: margin.top, w: plotW / 2 + margin.right, h: plotH / 2, color: 'rgba(99,102,241,0.06)', label: '✦ THE VOID', sub: 'Cosmic Desire' },
      { x: margin.left, y: margin.top, w: plotW / 2, h: plotH / 2, color: 'rgba(34,211,238,0.06)', label: '☽ THE JUDGE', sub: 'Abrahamic Zone' },
      { x: margin.left, y: cy, w: plotW / 2, h: plotH / 2 + margin.bottom, color: 'rgba(100,116,139,0.06)', label: '⚖ THE ENFORCER', sub: 'Bureaucrat Gods' },
      { x: cx, y: cy, w: plotW / 2 + margin.right, h: plotH / 2 + margin.bottom, color: 'rgba(245,158,11,0.08)', label: '⚡ THE WANTING GOD', sub: 'Indra Zone' },
    ];

    quadColors.forEach(q => {
      ctx.fillStyle = q.color;
      ctx.fillRect(q.x, q.y, q.w, q.h);
      ctx.fillStyle = 'rgba(255,255,255,0.15)';
      ctx.font = 'bold 13px system-ui, sans-serif';
      ctx.textAlign = 'center';
      const labelX = q.x + q.w / 2;
      const labelY = q.y + (q.y < cy ? 28 : q.h - 28);
      ctx.fillText(q.label, labelX, labelY);
      ctx.font = '11px system-ui, sans-serif';
      ctx.fillStyle = 'rgba(255,255,255,0.10)';
      ctx.fillText(q.sub, labelX, labelY + 16);
    });

    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    for (let v = -0.5; v <= 0.5; v += 0.5) {
      if (v === 0) continue;
      ctx.beginPath(); ctx.moveTo(toX(v), margin.top); ctx.lineTo(toX(v), H - margin.bottom); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(margin.left, toY(v)); ctx.lineTo(W - margin.right, toY(v)); ctx.stroke();
    }
    ctx.setLineDash([]);

    // Axes
    ctx.strokeStyle = 'rgba(255,255,255,0.25)';
    ctx.lineWidth = 1.5;
    // X axis
    ctx.beginPath(); ctx.moveTo(margin.left, cy); ctx.lineTo(W - margin.right, cy); ctx.stroke();
    // Y axis
    ctx.beginPath(); ctx.moveTo(cx, margin.top); ctx.lineTo(cx, H - margin.bottom); ctx.stroke();

    // Axis labels
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    ctx.font = 'bold 12px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('← ORDER / LAW', margin.left + plotW * 0.2, cy - 8);
    ctx.fillText('DESIRE / WILL →', W - margin.right - plotW * 0.2, cy - 8);
    ctx.save();
    ctx.translate(cx + 10, margin.top + plotH * 0.15);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('TRANSCENDS →', 0, 0);
    ctx.restore();
    ctx.save();
    ctx.translate(cx + 10, H - margin.bottom - plotH * 0.15);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('← BLEEDS', 0, 0);
    ctx.restore();

    // Subtitle axis labels
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.font = '10px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Bhrigu / Varuṇa', margin.left + plotW * 0.2, cy + 16);
    ctx.fillText('Aṅgirasa / Indra', W - margin.right - plotW * 0.2, cy + 16);
    ctx.save();
    ctx.translate(cx - 14, margin.top + plotH * 0.15);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Absolute / Formless', 0, 0);
    ctx.restore();
    ctx.save();
    ctx.translate(cx - 14, H - margin.bottom - plotH * 0.15);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Vulnerable / Human', 0, 0);
    ctx.restore();

    // Draw trails
    if (showTrails) {
      DEITIES.forEach(deity => {
        const eraIds = ERAS.map(e => e.id);
        const positions: { px: number; py: number }[] = [];
        for (let i = 0; i <= eIdx; i++) {
          const pos = deity.positions[eraIds[i]];
          if (pos) positions.push({ px: toX(pos.x), py: toY(pos.y) });
        }
        // Add interpolated current position
        if (progress > 0 && eIdx + 1 < ERAS.length) {
          const p = getDeityPos(deity, eIdx, progress);
          if (p && p.alpha > 0.5) positions.push({ px: toX(p.x), py: toY(p.y) });
        }

        if (positions.length >= 2) {
          ctx.strokeStyle = deity.color;
          ctx.globalAlpha = 0.3;
          ctx.lineWidth = 2;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          positions.forEach((p, i) => {
            if (i === 0) ctx.moveTo(p.px, p.py);
            else ctx.lineTo(p.px, p.py);
          });
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.globalAlpha = 1;

          // Arrow at the end
          if (positions.length >= 2) {
            const last = positions[positions.length - 1];
            const prev = positions[positions.length - 2];
            const angle = Math.atan2(last.py - prev.py, last.px - prev.px);
            ctx.save();
            ctx.globalAlpha = 0.4;
            ctx.fillStyle = deity.color;
            ctx.translate(last.px, last.py);
            ctx.rotate(angle);
            ctx.beginPath();
            ctx.moveTo(6, 0);
            ctx.lineTo(-4, -4);
            ctx.lineTo(-4, 4);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
          }
        }
      });
    }

    // Draw deities
    DEITIES.forEach(deity => {
      const pos = getDeityPos(deity, eIdx, progress);
      if (!pos || pos.alpha < 0.05) return;

      const px = toX(pos.x);
      const py = toY(pos.y);
      const r = deity.name === 'Indra' ? 10 : hoveredDeity === deity.name ? 9 : 7;
      const tradition = TRADITION_CONFIG[deity.tradition];

      // Glow for Indra
      if (deity.name === 'Indra') {
        const grad = ctx.createRadialGradient(px, py, 0, px, py, 25);
        grad.addColorStop(0, `rgba(245,158,11,${0.35 * pos.alpha})`);
        grad.addColorStop(1, 'rgba(245,158,11,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(px, py, 25, 0, Math.PI * 2);
        ctx.fill();
      }

      // Glow for Krishna
      if (deity.name === 'Krishna') {
        const grad = ctx.createRadialGradient(px, py, 0, px, py, 20);
        grad.addColorStop(0, `rgba(6,182,212,${0.25 * pos.alpha})`);
        grad.addColorStop(1, 'rgba(6,182,212,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(px, py, 20, 0, Math.PI * 2);
        ctx.fill();
      }

      drawShape(ctx, tradition.shape, px, py, r, deity.color, pos.alpha);

      // Label
      ctx.save();
      ctx.globalAlpha = pos.alpha;
      ctx.fillStyle = deity.color;
      ctx.font = `${deity.name === 'Indra' ? 'bold 12px' : '11px'} system-ui, sans-serif`;
      ctx.textAlign = 'center';
      ctx.shadowColor = 'black';
      ctx.shadowBlur = 4;
      ctx.fillText(deity.name, px, py - r - 6);
      ctx.restore();
    });

    // Era label
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.font = 'bold 16px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(ERAS[eIdx].label, W / 2, H - 20);

    // Title
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.font = 'bold 18px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('The Deity Compass', W / 2, 24);
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '12px system-ui, sans-serif';
    ctx.fillText('Where gods live — and where they migrate', W / 2, 42);

  }, [showTrails, hoveredDeity, getDeityPos]);

  // Redraw on state changes
  useEffect(() => {
    draw(eraIndex, 0);
  }, [eraIndex, showTrails, hoveredDeity, draw]);

  // Handle mouse hover for tooltips
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const W = canvas.clientWidth;
    const H = canvas.clientHeight;
    const margin = { top: 60, right: 30, bottom: 60, left: 30 };
    const plotW = W - margin.left - margin.right;
    const plotH = H - margin.top - margin.bottom;
    const cxPlot = margin.left + plotW / 2;
    const cyPlot = margin.top + plotH / 2;
    const toX = (v: number) => cxPlot + v * (plotW / 2) * 0.88;
    const toY = (v: number) => cyPlot - v * (plotH / 2) * 0.88;

    let found: string | null = null;
    let tooltipInfo: { x: number; y: number; text: string } | null = null;

    for (const deity of DEITIES) {
      const pos = getDeityPos(deity, eraIndex, 0);
      if (!pos || pos.alpha < 0.3) continue;
      const px = toX(pos.x);
      const py = toY(pos.y);
      const dist = Math.sqrt((mx - px) ** 2 + (my - py) ** 2);
      if (dist < 18) {
        found = deity.name;
        const eraId = ERAS[eraIndex].id;
        const snap = deity.positions[eraId];
        tooltipInfo = {
          x: e.clientX,
          y: e.clientY,
          text: snap?.label || deity.name,
        };
        break;
      }
    }

    setHoveredDeity(found);
    setTooltip(tooltipInfo);
  }, [eraIndex, getDeityPos]);

  return (
    <div style={{
      width: '100%',
      maxWidth: 900,
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif',
      color: '#fff',
      background: '#0c0a09',
      borderRadius: 12,
      padding: 16,
      position: 'relative',
    }}>
      {/* Canvas */}
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: 580, borderRadius: 8, cursor: 'crosshair' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => { setHoveredDeity(null); setTooltip(null); }}
      />

      {/* Tooltip */}
      {tooltip && (
        <div style={{
          position: 'fixed',
          left: tooltip.x + 12,
          top: tooltip.y - 10,
          background: 'rgba(0,0,0,0.9)',
          border: '1px solid rgba(255,255,255,0.2)',
          borderRadius: 6,
          padding: '6px 10px',
          fontSize: 12,
          color: '#fff',
          maxWidth: 260,
          pointerEvents: 'none',
          zIndex: 999,
        }}>
          {tooltip.text}
        </div>
      )}

      {/* Era buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
        {ERAS.map((era, i) => (
          <button
            key={era.id}
            onClick={() => setEraIndex(i)}
            style={{
              background: i === eraIndex ? '#f59e0b' : 'rgba(255,255,255,0.08)',
              color: i === eraIndex ? '#000' : '#aaa',
              border: i === eraIndex ? 'none' : '1px solid rgba(255,255,255,0.15)',
              borderRadius: 6,
              padding: '8px 16px',
              fontSize: 13,
              cursor: 'pointer',
              fontWeight: i === eraIndex ? 'bold' : 'normal',
              transition: 'all 0.2s ease',
            }}
          >
            {era.label}
          </button>
        ))}

        <label style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#aaa', marginLeft: 'auto' }}>
          <input
            type="checkbox"
            checked={showTrails}
            onChange={e => setShowTrails(e.target.checked)}
          />
          Show trails
        </label>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        gap: 16,
        marginTop: 12,
        fontSize: 11,
        color: '#888',
        flexWrap: 'wrap',
      }}>
        {Object.entries(TRADITION_CONFIG).filter(([k]) => k !== 'vedic_concept').map(([key, cfg]) => (
          <span key={key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{
              display: 'inline-block',
              width: 10,
              height: 10,
              borderRadius: cfg.shape === 'circle' ? '50%' : cfg.shape === 'square' ? 2 : 0,
              background: key === 'hindu' ? '#8b5cf6' : key === 'greek' ? '#eab308' : key === 'norse' ? '#dc2626' : key === 'abrahamic' ? '#e2e8f0' : '#22d3ee',
              transform: cfg.shape === 'diamond' ? 'rotate(45deg) scale(0.8)' : cfg.shape === 'triangle' ? 'scaleY(0.8)' : 'none',
              clipPath: cfg.shape === 'triangle' ? 'polygon(50% 0%, 0% 100%, 100% 100%)' : undefined,
            }} />
            {cfg.label}
          </span>
        ))}
      </div>

      {/* Key insight */}
      <div style={{
        marginTop: 16,
        padding: '12px 16px',
        background: 'rgba(245,158,11,0.08)',
        borderLeft: '3px solid #f59e0b',
        borderRadius: 4,
        fontSize: 13,
        color: '#ccc',
        lineHeight: 1.5,
      }}>
        <strong style={{ color: '#f59e0b' }}>The thesis:</strong> Every civilization starts bottom-right (gods who want &amp; bleed) and migrates top-left
        (formless cosmic law). India is the only civilization that completed the migration <em>and then</em> created
        Krishna — who reunifies all four quadrants. Indra is India's abandoned prototype: the most human god, punished
        for refusing to transcend.
      </div>
    </div>
  );
}
