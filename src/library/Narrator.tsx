// The audiobook player bar; the reading logic lives in useNarrator.ts.
import { useState } from 'react';
import { Music, Pause, Play, Settings2, SkipBack, SkipForward, X } from 'lucide-react';
import { voiceScore, type Narrator } from './useNarrator';

export default function NarratorBar({ n, label }: { n: Narrator; label: string }) {
  const [more, setMore] = useState(false);
  if (!n.active) return null;
  return (
    <div className="narrator" role="region" aria-label="Audiobook player">
      {more && (
        <div className="narrator-more">
          <label>
            Voice
            <select value={n.voice?.voiceURI ?? ''} onChange={(e) => n.setSettings({ voice: e.target.value })}>
              {n.voices.map((v) => (
                <option key={v.voiceURI} value={v.voiceURI}>
                  {v.name} ({v.lang})
                </option>
              ))}
            </select>
          </label>
          <label>
            Speed
            <select value={n.settings.rate} onChange={(e) => n.setSettings({ rate: Number(e.target.value) })}>
              {[0.8, 0.9, 1, 1.1, 1.2, 1.35, 1.5].map((r) => (
                <option key={r} value={r}>
                  {r}×
                </option>
              ))}
            </select>
          </label>
          <label className="narrator-vol">
            Music volume
            <input type="range" min={0.05} max={1} step={0.05} value={n.settings.volume} onChange={(e) => n.setSettings({ volume: Number(e.target.value) })} />
          </label>
          {!n.voices.some((v) => voiceScore(v) >= 40) && (
            <p className="narrator-hint">For a more natural voice, add an “Enhanced” or “Premium” English voice in your device’s speech settings.</p>
          )}
        </div>
      )}
      <div className="narrator-main">
        <button onClick={() => n.skip(-1)} aria-label="Previous paragraph">
          <SkipBack size={18} />
        </button>
        <button className="narrator-play" onClick={n.playing ? n.pause : n.play} aria-label={n.playing ? 'Pause' : 'Play'}>
          {n.playing ? <Pause size={20} /> : <Play size={20} />}
        </button>
        <button onClick={() => n.skip(1)} aria-label="Next paragraph">
          <SkipForward size={18} />
        </button>
        <div className="narrator-label">
          <strong>{label}</strong>
          <span>{n.total ? `${Math.min(n.pos.item + 1, n.total)} of ${n.total}` : 'Loading…'}</span>
        </div>
        <button className={n.settings.music ? 'on' : ''} onClick={() => n.setSettings({ music: !n.settings.music })} aria-pressed={n.settings.music} aria-label="Background music" title="Tanpura drone">
          <Music size={17} />
        </button>
        <button className={more ? 'on' : ''} onClick={() => setMore(!more)} aria-expanded={more} aria-label="Voice and speed">
          <Settings2 size={17} />
        </button>
        <button onClick={n.close} aria-label="Stop and close the player">
          <X size={17} />
        </button>
      </div>
    </div>
  );
}
