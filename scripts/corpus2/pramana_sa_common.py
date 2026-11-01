"""Polite, cached client for Pramāṇa (indike.org/pramana) used by the pramana_sa_* importers.

One request at a time, >=1 s apart, every response cached on disk so reruns never refetch.
Never touches the robots-excluded endpoints (/api/sql, /api/search, /api/export, ...).
"""

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://indike.org/pramana/api"
UA = "rigved-corpus-research/1.0 (+https://github.com/iashris/rigved)"
WORK = os.environ.get(
    "PRAMANA_SA_WORK",
    "/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/pramana_sa",
)
CACHE = os.path.join(WORK, "cache")
os.makedirs(CACHE, exist_ok=True)
FORBIDDEN = ("sql", "query", "search", "suggest", "export", "lemma-occ", "mt", "contrib")
_last = [0.0]


def get(path, **params):
    if path.split("/")[0] in FORBIDDEN:
        raise SystemExit(f"robots: /api/{path} is off limits")
    params = {k: v for k, v in params.items() if v is not None}
    url = f"{API}/{urllib.parse.quote(path)}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    f = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json")
    if os.path.exists(f):
        return json.load(open(f, encoding="utf-8"))
    for attempt in range(6):
        wait = 1.0 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            _last[0] = time.time()
            json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False)
            return data
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            if e.code not in (429, 500, 502, 503, 504):
                raise SystemExit(f"HTTP {e.code}: {url}")
            print("retry", e.code, url, file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            _last[0] = time.time()
            print("retry", url, e, file=sys.stderr)
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f"failed: {url}")


def page(path):
    return get(f"page/{path}", show="-")


def segments(path, limit=1000):
    """All segments of a text, in order, following the `next` cursor."""
    out, after = [], None
    while True:
        d = get(f"segments/{path}", limit=limit, after=after)
        out += d.get("segments") or d.get("items") or []
        after = d.get("next")
        if not after:
            return out
