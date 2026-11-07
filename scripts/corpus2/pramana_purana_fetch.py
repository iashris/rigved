"""Fetch and cache every Purāṇa path in pramana_purana_texts. Rerunnable: cached responses are never refetched.

Set PRAMANA_SA_WORK to choose the cache folder.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pramana_purana_texts import PURANAS  # noqa: E402
from pramana_sa_common import page, segments  # noqa: E402

for cid, t in PURANAS.items():
    for key in ("sa", "en", "mt"):
        path = t.get(key)
        if path:
            page(path)
            print(cid, key, path, len(segments(path)), flush=True)
print("done", flush=True)
