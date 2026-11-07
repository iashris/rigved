"""Fetch and cache every path in pramana_canon_texts, refusing any translation Pramāṇa marks as in copyright.

Rerunnable: cached responses are never refetched. Set PRAMANA_SA_WORK to choose the cache folder.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pramana_canon_texts import CANON  # noqa: E402
from pramana_sa_common import page, segments  # noqa: E402

refused = []
for cid, t in CANON.items():
    for key in ("sa", "en"):
        path = t.get(key)
        if not path:
            continue
        rights = " ".join(p.get("license") or "" for p in page(path).get("provenance") or [])
        if key == "en" and "in copyright" in rights.lower():
            refused.append((cid, path, rights[:120]))
            print("IN COPYRIGHT, not fetched:", cid, path, rights[:120], flush=True)
            continue
        print(cid, key, path, len(segments(path)), flush=True)
print("done; refused:", refused, flush=True)
