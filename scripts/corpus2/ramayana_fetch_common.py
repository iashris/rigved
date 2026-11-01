"""Shared polite fetcher for the Wayback Machine (sacred-texts snapshots) with an on-disk cache."""
import gzip, os, re, time, json, subprocess

WORK = '/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/ramayana'
CACHE = f'{WORK}/cache'
UA = 'Mozilla/5.0 (corpus research; polite sequential fetch)'
_last = [0.0]

class HTTPStatus(Exception):
    def __init__(self, code): super().__init__(f'HTTP {code}'); self.code = code

def _get(url):
    """Fetch with curl (urllib hit repeated 'connection refused' from web.archive.org); ~1.5 s between requests,
    backoff on 429/5xx and network errors, 404 raised as HTTPStatus."""
    for attempt in range(10):
        wait = 1.5 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        r = subprocess.run(['curl', '-sL', '-m', '90', '-A', UA, '-w', '\n%{http_code}', url], capture_output=True)
        body, _, code = r.stdout.rpartition(b'\n')
        code = int(code or 0)
        if r.returncode == 0 and code == 200:
            return body
        if code in (404, 402): raise HTTPStatus(code)  # 402 = the archived capture itself is sacred-texts' 2026 paywall reply
        print('  retry', code, r.returncode, url, flush=True)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f'failed {url}')

def gunzip_all(b):
    while b[:2] == b'\x1f\x8b':
        b = gzip.decompress(b)
    return b

def wayback(path, ts='2026'):
    """path like 'hin/rama/index.htm' -> decoded HTML text (cached). ts = wayback timestamp prefix."""
    os.makedirs(CACHE, exist_ok=True)
    fn = f"{CACHE}/{path.replace('/', '_')}" + ('' if ts == '2026' else f'.{ts}')
    if os.path.exists(fn) and os.path.getsize(fn) > 200:
        b = open(fn, 'rb').read()
    else:
        try:
            b = gunzip_all(_get(f'https://web.archive.org/web/{ts}id_/https://sacred-texts.com/{path}'))
        except HTTPStatus as e:
            # capture missing, or the 2026 capture is a 402: take the newest 200 capture listed by the CDX API
            rows = _get(f'https://web.archive.org/cdx/search/cdx?url=sacred-texts.com/{path}'
                        '&filter=statuscode:200&filter=mimetype:text/html&fl=timestamp,original').decode().split('\n')
            rows = sorted(r.split() for r in rows if r.strip())
            if not rows: raise RuntimeError(f'no 200 snapshot for {path}')
            ts2, orig = rows[-1]
            print(f'  {path}: 2026 capture HTTP {e.code}, using {ts2}', flush=True)
            b = gunzip_all(_get(f'https://web.archive.org/web/{ts2}id_/{orig}'))
        open(fn, 'wb').write(b)
    for enc in ('utf-8', 'cp1252'):
        try: return b.decode(enc)
        except UnicodeDecodeError: pass
    return b.decode('latin1')
