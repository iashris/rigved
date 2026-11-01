#!/usr/bin/env python3
"""Download TITUS HTML pages (raw) for the corpus2 'titus' task.

Usage: python3 -I titus_fetch.py <name> [<name> ...]
Pages are cached in WORK/raw/<name>/NNN.htm (rerunnable; skips cached pages).
Restricted texts use TITUS_USER/TITUS_PASS from the repo .env (fallback: scripts/titus_scraper.py).
"""
import os, re, sys, time
import requests

WORK = os.environ.get("TITUS_WORK", "/private/tmp/claude-502/-Users-iashris-Desktop-iip-vedic-shorts/"
       "c00b0a6a-d6d9-40bf-b940-c4e03eed9a23/scratchpad/corpus/work/titus")
BASE = "https://titus.uni-frankfurt.de/texte/etcs/ind/aind/ved"
BASE_AUTH = "https://titus.fkidg1.uni-frankfurt.de/texte/etcc/ind/aind/ved"

TEXTS = {
    "ks": (f"{BASE}/yvs/ks/ks", False),
    "jub": (f"{BASE}/sv/jub/jub", False),
    "katharbr": (f"{BASE_AUTH}/yvs/katharbr/katha", True),
    "kathbcal": (f"{BASE_AUTH}/yvs/kathbcal/kathb", True),
    "manb": (f"{BASE}/sv/manb/manb", False),
    "dab": (f"{BASE}/sv/dab/dab", False),
    "vb": (f"{BASE}/sv/vb/vb", False),
}


def cred():
    """Basic-auth login for the restricted TITUS subdomain.

    Prefers TITUS_USER / TITUS_PASS from the repo's gitignored .env (read at runtime,
    never printed), else the same variables from the environment.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    env = os.path.join(here, "..", "..", ".env")
    vals = {}
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            m = re.match(r'\s*(?:export\s+)?(TITUS_USER|TITUS_PASS)\s*=\s*(.*?)\s*$', line)
            if m:
                vals[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if vals.get("TITUS_USER") and vals.get("TITUS_PASS"):
        return (vals["TITUS_USER"], vals["TITUS_PASS"])
    u, p = os.environ.get("TITUS_USER"), os.environ.get("TITUS_PASS")
    if not (u and p):
        raise SystemExit("restricted TITUS text: set TITUS_USER and TITUS_PASS in the repo .env")
    return (u, p)


def fetch(name):
    base, auth = TEXTS[name]
    out = os.path.join(WORK, "raw", name)
    os.makedirs(out, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (academic research; vedic-texts-project)"
    if auth:
        s.auth = cred()
    n, fails, ok = 1, 0, 0
    while fails < 3 and n < 2000:
        path = os.path.join(out, f"{n:03d}.htm")
        if os.path.exists(path):
            n += 1; ok += 1; fails = 0; continue
        url = f"{base}{n:03d}.htm"
        try:
            r = s.get(url, timeout=60)
            r.encoding = "utf-8"
            if r.status_code == 200 and "not (yet) available" not in r.text and len(r.text) > 500:
                open(path, "w", encoding="utf-8").write(r.text)
                ok += 1; fails = 0
            else:
                fails += 1
        except Exception as e:
            print("  error", url, e); fails += 1
        n += 1
        time.sleep(0.3)
    print(f"{name}: {ok} pages")


if __name__ == "__main__":
    for nm in sys.argv[1:] or TEXTS:
        fetch(nm)
