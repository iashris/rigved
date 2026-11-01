#!/usr/bin/env python3
"""Download TITUS HTML pages for the rebuild_yajus task (public pages, sequential).

Usage: python3 -I rebuild_yajus_titus_fetch.py vs aa ab
Cached in WORK/titus/<name>/NNN.htm (rerunnable). Stops after 3 consecutive misses.
"""
import os, sys, time
import urllib.request, urllib.error

WORK = ('/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/'
        'c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/rebuild_yajus/titus')
BASE = 'https://titus.uni-frankfurt.de/texte/etcs/ind/aind/ved'
UA = 'rigved-corpus-research/1.0 (+https://github.com/iashris/rigved)'
TEXTS = {
    'vs': f'{BASE}/yvw/vs/vs',
    'aa': f'{BASE}/rv/aa/aa',
    'ab': f'{BASE}/rv/ab/ab',
}


def fetch(name):
    base = TEXTS[name]
    out = os.path.join(WORK, name)
    os.makedirs(out, exist_ok=True)
    n, fails, ok = 1, 0, 0
    while fails < 3 and n < 1000:
        path = os.path.join(out, f'{n:03d}.htm')
        if os.path.exists(path):
            n += 1; ok += 1; fails = 0; continue
        url = f'{base}{n:03d}.htm'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                t = r.read().decode('utf-8', errors='replace')
            if 'not (yet) available' not in t and len(t) > 500:
                open(path, 'w', encoding='utf-8').write(t)
                ok += 1; fails = 0
            else:
                fails += 1
        except urllib.error.HTTPError:
            fails += 1
        except Exception as e:
            print('  error', url, e); fails += 1
        n += 1
        time.sleep(1.2)
    print(f'{name}: {ok} pages', flush=True)


if __name__ == '__main__':
    for nm in sys.argv[1:] or TEXTS:
        fetch(nm)
