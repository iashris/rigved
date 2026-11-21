"""Shared by the comparative-shelf importers (bible_old_testament.py, bible_new_testament.py, avesta_titus.py): write their bands, texts and
translation credits into library_catalog.json and translation_sources.json. Rerunnable: a text or band already
there is replaced in place of being added twice.

The catalog is laid out by hand, one text or band per line, so it is edited as text rather than re-serialised.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
ROW_ID = re.compile(r'\s*\{"id": "([^"]+)"')


def write(bands, texts, records):
    """`bands`: band dicts, each with an `after` list naming the bands it may follow, first preferred. `texts`: catalog rows. `records`:
    translation_sources entries keyed by text id."""
    raw = open(CAT, encoding="utf-8").read()
    ours = {t["id"] for t in texts} | {b["id"] for b in bands}
    lines = [ln for ln in raw.split("\n") if not (ROW_ID.match(ln) and ROW_ID.match(ln).group(1) in ours)]
    start = next(i for i, ln in enumerate(lines) if ln.strip() == '"bands": [')
    end = next(i for i in range(start, len(lines)) if lines[i].strip() in ("],", "]"))
    rows = [ln.strip().rstrip(",") for ln in lines[start + 1:end] if ln.strip()]
    for band in bands:
        row = json.dumps({k: v for k, v in band.items() if k != "after"}, ensure_ascii=False)
        # `after` lists bands in order of preference, so either importer can run first.
        at = next(i for a in band["after"] for i, r in enumerate(rows) if r.startswith(f'{{"id": "{a}"'))
        rows.insert(at + 1, row)
    lines[start + 1:end] = ["    " + r + ("," if i < len(rows) - 1 else "") for i, r in enumerate(rows)]
    raw = "\n".join(lines)
    head, tail = raw.rsplit("\n  ]\n}", 1)
    body = ",\n".join("    " + json.dumps(t, ensure_ascii=False) for t in texts)
    open(CAT, "w", encoding="utf-8").write(head.rstrip().rstrip(",") + ",\n" + body + "\n  ]\n}" + tail)
    cat = json.load(open(CAT, encoding="utf-8"))  # stops here if the edit broke the JSON
    have = json.load(open(SOURCES, encoding="utf-8"))
    have.update(records)
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(have, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"catalog: {len(cat['texts'])} texts; bands {[b['id'] for b in cat['bands']]}")
