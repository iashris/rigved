import { useEffect, useState } from 'react';

// Hash routes, so links work on GitHub Pages without server rewrites:
//   #/                         canon map
//   #/read/<text>/<block>?with=<translation>&v=<ref>
//   #/analysis                 the original word-distribution tool

export type Route =
  | { page: 'home' }
  | { page: 'analysis' }
  | { page: 'read'; text: string; block: string; with?: string; v?: string };

export function parseHash(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?');
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent);
  const q = new URLSearchParams(query);
  if (parts[0] === 'analysis') return { page: 'analysis' };
  if (parts[0] === 'read' && parts[1]) {
    return { page: 'read', text: parts[1], block: parts[2] ?? '', with: q.get('with') ?? undefined, v: q.get('v') ?? undefined };
  }
  return { page: 'home' };
}

export function readHref(text: string, block: string, opts: { with?: string; v?: string } = {}): string {
  const q = new URLSearchParams();
  if (opts.with) q.set('with', opts.with);
  if (opts.v) q.set('v', opts.v);
  const qs = q.toString();
  return `#/read/${encodeURIComponent(text)}/${encodeURIComponent(block)}${qs ? `?${qs}` : ''}`;
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parseHash(window.location.hash));
  useEffect(() => {
    const on = () => setRoute(parseHash(window.location.hash));
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  return route;
}
