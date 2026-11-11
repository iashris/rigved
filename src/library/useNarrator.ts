// Audiobook mode: reads a passage's English aloud with the browser's own speech engine, highlights the part being
// read, and moves on to the next passage by itself. An optional tanpura drone, synthesised here, plays underneath.
import { useCallback, useEffect, useRef, useState } from 'react';

/** One stretch of text tied to the element it highlights. */
export interface NarrationItem {
  anchor: string; // element id to highlight and keep in view; '' for a spoken heading with nothing to mark
  text: string;
}

type Settings = { voice: string; rate: number; music: boolean; volume: number };

const SETTINGS_KEY = 'narrator.settings';
const DEFAULTS: Settings = { voice: '', rate: 1, music: false, volume: 0.35 };

function loadSettings(): Settings {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) ?? '{}') };
  } catch {
    return DEFAULTS;
  }
}

/** Higher is more natural. The neural and studio voices shipped by Apple, Google and Microsoft sound far less robotic. */
export function voiceScore(v: SpeechSynthesisVoice) {
  const n = v.name.toLowerCase();
  let s = 0;
  if (/natural|neural|premium|enhanced|siri|studio|wavenet/.test(n)) s += 50;
  if (/^google/.test(n)) s += 25;
  if (!v.localService) s += 5;
  if (/en[-_](gb|in|us|au|ie)/i.test(v.lang)) s += 10;
  // Apple's novelty and retro voices, and the old formant ones, read scripture like a robot or a cartoon.
  if (/compact|novelty|whisper|bad news|bells|boing|bubbles|cellos|zarvox|trinoids|albert|jester|organ|superstar|wobble|hysterical|good news|deranged|bahh|^eddy|^flo\b|grandma|grandpa|^reed|rocko|^sandy|shelley|^fred|^junior|^ralph|^kathy/.test(n)) s -= 100;
  return s;
}

function useVoices() {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  useEffect(() => {
    if (!('speechSynthesis' in window)) return;
    const load = () =>
      setVoices(
        speechSynthesis
          .getVoices()
          .filter((v) => v.lang.toLowerCase().startsWith('en'))
          .sort((a, b) => voiceScore(b) - voiceScore(a) || a.name.localeCompare(b.name)),
      );
    load();
    speechSynthesis.addEventListener('voiceschanged', load);
    return () => speechSynthesis.removeEventListener('voiceschanged', load);
  }, []);
  return voices;
}

/** Sentence-sized pieces: browsers stall or clip long utterances, and short ones let pause and skip land quickly. */
function chunks(text: string): string[] {
  const clean = text
    .replace(/\[\d+\]|\(\d+\)/g, '') // footnote marks
    .replace(/\s+/g, ' ')
    .trim();
  if (!clean) return [];
  const sentences = clean.match(/[^.!?;]+[.!?;]+["'”’)]*\s*|[^.!?;]+$/g) ?? [clean];
  const out: string[] = [];
  let cur = '';
  for (const s of sentences) {
    if ((cur + s).length > 220 && cur) {
      out.push(cur.trim());
      cur = '';
    }
    if (s.length > 260) {
      // a run-on sentence: break at commas
      for (const part of s.split(/(?<=,)\s+/)) {
        if ((cur + part).length > 220 && cur) {
          out.push(cur.trim());
          cur = '';
        }
        cur += part + ' ';
      }
    } else cur += s;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

/** A tanpura: four strings plucked in turn (Pa, Sa', Sa', Sa) on a slow cycle, through a soft low-pass and an echo. */
class Tanpura {
  private ctx: AudioContext | null = null;
  private master: GainNode | null = null;
  private timer = 0;
  private next = 0;
  private step = 0;

  start(volume: number) {
    if (this.ctx) return this.setVolume(volume);
    const Ctx = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!Ctx) return;
    const ctx = new Ctx();
    const master = ctx.createGain();
    master.gain.value = 0;
    master.gain.linearRampToValueAtTime(volume * 0.22, ctx.currentTime + 2);
    const echo = ctx.createDelay(1);
    echo.delayTime.value = 0.33;
    const fb = ctx.createGain();
    fb.gain.value = 0.35;
    echo.connect(fb).connect(echo);
    master.connect(ctx.destination);
    echo.connect(master);
    this.ctx = ctx;
    this.master = master;
    this.next = ctx.currentTime + 0.1;
    const sa = 138.59; // C♯3, a common tanpura pitch
    const strings = [sa * 0.75, sa * 2, sa * 2, sa];
    const pluck = (f: number, t: number) => {
      const g = ctx.createGain();
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.5, t + 0.03);
      g.gain.exponentialRampToValueAtTime(0.001, t + 4.2);
      const lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(2600, t);
      lp.frequency.exponentialRampToValueAtTime(700, t + 3);
      lp.Q.value = 2; // a little of the jawari buzz
      lp.connect(g);
      g.connect(master);
      g.connect(echo);
      for (const [type, detune, level] of [
        ['sawtooth', 0, 0.5],
        ['sawtooth', 4, 0.35],
        ['triangle', -3, 0.6],
      ] as const) {
        const o = ctx.createOscillator();
        o.type = type;
        o.frequency.value = f;
        o.detune.value = detune;
        const og = ctx.createGain();
        og.gain.value = level;
        o.connect(og).connect(lp);
        o.start(t);
        o.stop(t + 4.4);
      }
    };
    // schedule a little ahead so the rhythm stays even when the page is busy
    const tick = () => {
      while (this.next < ctx.currentTime + 1.5) {
        pluck(strings[this.step % 4], this.next);
        this.next += this.step % 4 === 3 ? 1.6 : 1.05;
        this.step++;
      }
    };
    tick();
    this.timer = window.setInterval(tick, 400);
  }

  setVolume(volume: number) {
    if (this.ctx && this.master) this.master.gain.linearRampToValueAtTime(volume * 0.22, this.ctx.currentTime + 0.3);
  }

  stop() {
    window.clearInterval(this.timer);
    const ctx = this.ctx;
    if (ctx && this.master) {
      this.master.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.8);
      window.setTimeout(() => ctx.close(), 1000);
    }
    this.ctx = null;
    this.master = null;
  }
}

export const speechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

/**
 * Reads `items` in order. `ready` is false while a passage loads; when the items run out, `onEnd` is called (to move to
 * the next passage) and reading picks up again by itself once the next passage is ready.
 */
export function useNarrator({ items, ready, title, onEnd, onPrevBlock }: { items: NarrationItem[]; ready: boolean; title: string; onEnd: () => boolean; onPrevBlock: () => void }) {
  const [active, setActive] = useState(false); // the player is open
  const [playing, setPlaying] = useState(false);
  const [pos, setPos] = useState({ item: 0, chunk: 0 });
  const [settings, setSettingsState] = useState(loadSettings);
  const voices = useVoices();
  const tanpura = useRef<Tanpura | null>(null);
  const waiting = useRef(false); // moved on to the next passage, read it once it has loaded
  const token = useRef(0); // invalidates callbacks from a cancelled utterance
  const pieces = useRef<string[][]>([]);
  pieces.current = items.map((i) => chunks(i.text));

  const setSettings = (s: Partial<Settings>) =>
    setSettingsState((old) => {
      const n = { ...old, ...s };
      try {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify(n));
      } catch {
        /* storage blocked */
      }
      return n;
    });

  const voice = voices.find((v) => v.voiceURI === settings.voice) ?? voices[0];

  const speakFrom = useCallback(
    (item: number, chunk: number) => {
      const my = ++token.current;
      speechSynthesis.cancel();
      // find the next non-empty piece
      while (item < pieces.current.length && chunk >= pieces.current[item].length) {
        item++;
        chunk = 0;
      }
      if (item >= pieces.current.length) {
        setPos({ item: 0, chunk: 0 });
        if (onEnd()) waiting.current = true;
        else setPlaying(false);
        return;
      }
      setPos({ item, chunk });
      const u = new SpeechSynthesisUtterance(pieces.current[item][chunk]);
      if (voice) {
        u.voice = voice;
        u.lang = voice.lang;
      }
      u.rate = settings.rate;
      u.onend = () => {
        if (my === token.current) speakFrom(item, chunk + 1);
      };
      u.onerror = (e) => {
        if (my !== token.current || e.error === 'interrupted' || e.error === 'canceled') return;
        speakFrom(item, chunk + 1);
      };
      speechSynthesis.speak(u);
    },
    [voice, settings.rate, onEnd],
  );

  // A new passage has loaded after moving on: carry on reading.
  const sig = items.map((i) => i.anchor).join('|');
  useEffect(() => {
    if (!ready) return;
    if (waiting.current && playing) {
      waiting.current = false;
      speakFrom(0, 0);
    }
    // only when the passage itself changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sig, ready]);

  const play = () => {
    if (!speechSupported) return;
    setActive(true);
    setPlaying(true);
    if (ready) speakFrom(pos.item, pos.chunk);
    else waiting.current = true;
  };
  const pause = () => {
    token.current++;
    waiting.current = false;
    speechSynthesis.cancel();
    setPlaying(false);
  };
  const close = () => {
    pause();
    waiting.current = false;
    setActive(false);
    setPos({ item: 0, chunk: 0 });
  };
  const skip = (d: number) => {
    let item = pos.item + d;
    if (item < 0) {
      if (pos.chunk > 0 || pos.item > 0) item = 0;
      else {
        onPrevBlock();
        return;
      }
    }
    if (playing) speakFrom(item, 0);
    else setPos({ item: Math.min(item, Math.max(items.length - 1, 0)), chunk: 0 });
  };

  // Settings changed mid-sentence: restart that sentence with them.
  useEffect(() => {
    if (playing && ready && !waiting.current) speakFrom(pos.item, pos.chunk);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settings.rate, settings.voice]);

  // Leaving the reader stops the voice and the music.
  useEffect(
    () => () => {
      token.current++;
      if (speechSupported) speechSynthesis.cancel();
      tanpura.current?.stop();
    },
    [],
  );

  // Music follows the player: on while it is open and the listener wants it.
  useEffect(() => {
    if (active && playing && settings.music) {
      tanpura.current ??= new Tanpura();
      tanpura.current.start(settings.volume);
    } else if (tanpura.current && (!active || !settings.music)) {
      tanpura.current.stop();
      tanpura.current = null;
    }
  }, [active, playing, settings.music, settings.volume]);

  // Highlight what is being read and keep it in view.
  const anchor = active ? (items[pos.item]?.anchor ?? '') : '';
  useEffect(() => {
    if (!anchor) return;
    const el = document.getElementById(anchor);
    if (!el) return;
    el.classList.add('speaking');
    const r = el.getBoundingClientRect();
    const box = el.closest('.pane') as HTMLElement | null;
    const view = box ? box.getBoundingClientRect() : { top: 0, bottom: window.innerHeight };
    if (r.top < view.top + 60 || r.top > view.bottom - 160) el.scrollIntoView({ block: 'start', behavior: 'smooth' });
    return () => el.classList.remove('speaking');
  }, [anchor, sig]);

  // Lock-screen and headphone controls.
  useEffect(() => {
    if (!('mediaSession' in navigator) || !active) return;
    navigator.mediaSession.metadata = new MediaMetadata({ title, artist: 'Vedic Library' });
    navigator.mediaSession.playbackState = playing ? 'playing' : 'paused';
    const h: [MediaSessionAction, () => void][] = [
      ['play', play],
      ['pause', pause],
      ['nexttrack', () => skip(1)],
      ['previoustrack', () => skip(-1)],
    ];
    for (const [a, f] of h) {
      try {
        navigator.mediaSession.setActionHandler(a, f);
      } catch {
        /* unsupported action */
      }
    }
  });

  return { active, playing, pos, total: items.length, settings, setSettings, voices, voice, play, pause, close, skip };
}

export type Narrator = ReturnType<typeof useNarrator>;
