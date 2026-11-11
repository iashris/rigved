#!/usr/bin/env python3
"""Add pramana_world_texts to library_catalog.json (bands and texts) and translation_sources.json. Rerunnable.

These are English-only files, so each is a primary text with its translator credited on the text itself; nothing pairs.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_sa_common import page  # noqa: E402
from pramana_world_texts import BANDS, WORLD  # noqa: E402

CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
DATA = os.path.join(HERE, "..", "..", "public", "data")


def provenance(path):
    return page(path).get("provenance") or []


def source(path):
    seen = []
    for p in provenance(path):
        label = (p.get("edition") or "").split(" — ")[0].strip()
        label = f"{p.get('repo')}: {label[:120]}" if label else str(p.get("repo"))
        if label not in seen:
            seen.append(label)
    return "Pramāṇa (indike.org/pramana), " + path + (" · " + "; ".join(seen[:2]) if seen else "")


def links(path):
    out = []
    for p in provenance(path):
        for url in (p.get("url") or "").split():
            out.append({"label": re.sub(r"^https?://(www\.)?", "", url).split("/")[0], "url": url})
    if not out:
        raise SystemExit(f"{path}: Pramāṇa records no URL for this translation")
    return out


new, records = [], {}
for cid, t in WORLD.items():
    file = f"{t['dir']}/{cid}.json"
    if not os.path.exists(os.path.join(DATA, file)):
        raise SystemExit(f"{file} missing: run pramana_world_convert.py first")
    new.append({"id": cid, "file": file, "name": t["name"], "band": t["band"], "levels": t["levels"], "source": source(t["en"])})
    records[cid] = {"english": {"by": t["by"], "work": t["work"], "year": t["year"], "links": links(t["en"]),
                                "via": {"label": "Pramāṇa", "url": "https://indike.org/pramana/" + t["en"]}}}

# Edit as text: the catalog is laid out by hand, one text per line.
raw = open(CAT, encoding="utf-8").read()
ours = {e["id"] for e in new} | {b["id"] for b in BANDS}
lines = [ln for ln in raw.split("\n") if not (re.match(r'\s*\{"id": "([^"]+)"', ln) and re.match(r'\s*\{"id": "([^"]+)"', ln).group(1) in ours)]
# Rebuild the bands list so each row but the last ends in a comma, whatever was there before.
start = next(i for i, ln in enumerate(lines) if ln.strip() == '"bands": [')
end = next(i for i in range(start, len(lines)) if lines[i].strip() in ("],", "]"))
rows = [ln.strip().rstrip(",") for ln in lines[start + 1:end] if ln.strip()]
for band in BANDS:
    row = json.dumps({k: v for k, v in band.items() if k != "after"}, ensure_ascii=False)
    at = next(i for i, r in enumerate(rows) if r.startswith(f'{{"id": "{band["after"]}"'))
    rows.insert(at + 1, row)
lines[start + 1:end] = ["    " + r + ("," if i < len(rows) - 1 else "") for i, r in enumerate(rows)]
raw = "\n".join(lines)
head, tail = raw.rsplit("\n  ]\n}", 1)
open(CAT, "w", encoding="utf-8").write(head.rstrip().rstrip(",") + ",\n\n" + ",\n".join("    " + json.dumps(e, ensure_ascii=False) for e in new) + "\n  ]\n}" + tail)
cat = json.load(open(CAT, encoding="utf-8"))
print(len(cat["texts"]), "texts;", [b["id"] for b in cat["bands"]])

have = json.load(open(SOURCES, encoding="utf-8"))
have.update(records)
with open(SOURCES, "w", encoding="utf-8") as f:
    json.dump(have, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(len(records), "source records written;", len(have), "in all")
