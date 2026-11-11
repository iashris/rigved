// Vite copies all of public/ into docs/, which GitHub Pages publishes, and Pages caps a site at 1 GB.
// The site reads texts from docs/library (the reader's chunks). public/data stays in git as the master
// copy for the shorts engine, so the full per-text JSON is removed from the published build.
// The two legacy files are kept: the search page falls back to them for the Rigveda and Atharvaveda.
import fs from 'node:fs';
import path from 'node:path';

const site = path.resolve('docs', 'data');
const keep = new Set(['other/griffith.csv', 'other/av.txt']);

if (fs.existsSync(site)) {
  for (const dir of fs.readdirSync(site)) {
    const full = path.join(site, dir);
    if (!fs.statSync(full).isDirectory()) continue;
    for (const f of fs.readdirSync(full)) if (!keep.has(`${dir}/${f}`)) fs.rmSync(path.join(full, f), {recursive: true});
    if (!fs.readdirSync(full).length) fs.rmdirSync(full);
  }
}
console.log('docs/data pruned to:', [...keep].join(', '));
