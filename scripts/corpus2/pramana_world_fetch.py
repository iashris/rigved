"""Fetch and cache the English translations in pramana_world_texts, refusing any Pramāṇa does not mark public domain.

Rerunnable: cached responses are never refetched. Set PRAMANA_SA_WORK to choose the cache folder
(e.g. PRAMANA_SA_WORK=cache/pramana_world, which .gitignore keeps out of the repo).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pramana_sa_common import page, segments  # noqa: E402
from pramana_world_texts import WORLD  # noqa: E402

refused = []
for cid, t in WORLD.items():
    rights = " ".join(p.get("license") or "" for p in page(t["en"]).get("provenance") or [])
    if "public domain" not in rights.lower() or "in copyright" in rights.lower():
        refused.append((cid, t["en"], rights[:120]))
        print("NOT MARKED PUBLIC DOMAIN, not fetched:", cid, t["en"], rights[:120], flush=True)
        continue
    print(cid, t["en"], len(segments(t["en"])), flush=True)
print("done; refused:", refused, flush=True)
