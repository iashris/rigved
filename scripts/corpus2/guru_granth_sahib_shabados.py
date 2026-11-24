#!/usr/bin/env python3
"""The Gurū Granth Sāhib for its own Sikh shelf, in Gurmukhi alone: no English translation it carries is free.

Gurmukhi: the Shabad OS Database (github.com/shabados/database, archived 2026 in favour of shabados/shabados; read at
commit 918c1d4), digitised from the SGPC's Shabadaarth (4 vols., Amritsar, 2009-12) and proofread against it. Its MIT
licence covers the code and "content resting outside of the `data` folder"; the Gurbani itself it identifies as public
domain, "free of known copyright restrictions", which is what this import rests on. The script stops if that sentence
leaves the README.
English: none qualifies. The database carries two English translations, each a named asset with a citation and no
licence: Dr. Sant Singh Khalsa's (collections/assets/DSSK.toml, dated 2013-03) and Manmohan Singh's for the SGPC
(collections/assets/SBMS.toml, 2006-09 editions). Neither is public domain by age, and nothing in the repository grants
a licence for them, so neither is read. The Punjabi exegeses (Sahib Singh, Faridkot Ṭīkā, SGPC) and the SikhNet Spanish
are out of scope (the reader has one original and one English slot) and their licences were not assessed. The database
has no roman transliteration of the Granth (its schema allows a `pronunciation` content type, but no Granth line has
one), so none is written; none is generated here either.
The Gurmukhi is written as the database has it, less the vishraams: it marks reading pauses with ; , and . after the
Damdami Taksāl's Arth Paath Vishraam Pothi (2015), an editorial layer not in the printed text. The small subscript
numerals in 37 headings (ਗਉੜੀ₂ ਮਹਲਾ ੫) are kept as the database has them.

References are aṅg (the standard 1,430-page pagination) then paṅkti, counted in reading order within the aṅg: "1.1" is
the Mūl Mantar, and "1.7" is the seventh paṅkti, not printed line 7. The database's own `line` is the printed line on
the page, which up to six paṅktis share, so it cannot key an entry; a paṅkti number can. Each of the 51 sections (Jap,
the 31 rāgas, the closing saloks and svaiyye, Rāgmālā) titles its first paṅkti, in the database's romanisation
("Siree Raag"), with the closing sections' one-line English gloss. The text is read in the database's order: source,
sections, line groups (shabads), lines.

Writes public/data/sikh/guru_granth_sahib.json; with --catalog, also adds it to library_catalog.json (no record goes in
translation_sources.json: there is no translation to credit). Rerunnable; the database is shallow-cloned into
cache/shabados.

Usage: python3 -I scripts/corpus2/guru_granth_sahib_shabados.py [--catalog]
"""
import json
import os
import re
import subprocess
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "shabados")
COLL = os.path.join(CACHE, "collections")
OUT = os.path.join(ROOT, "public", "data", "sikh")
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

REPO = "https://github.com/shabados/database"
BAND = {"id": "sikh", "name": "Sikh", "after": ["bhakti"],
        "blurb": "the Gurū Granth Sāhib: the Sikh Gurus' hymns beside Kabīr's, Nāmdev's, Ravidās's and Farīd's, set out by rāga, in Gurmukhi"}
ORIGINAL = {"name": "Gurmukhi", "lang": "pa", "label": "ਗੁਰਮੁਖੀ", "short": "ਗੁ"}
VISHRAAM = re.compile(r"[;,.]")
# Gurmukhi, the double daṇḍa, the joiner some conjuncts need, and the headings' count numerals.
CLEAN = re.compile(r"[਀-੿ ॥‍₀-₉]+")


def toml(*parts):
    with open(os.path.join(COLL, *parts), "rb") as f:
        return tomllib.load(f)


def fetch():
    if not os.path.isdir(COLL):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", REPO, CACHE], check=True)
    if "free of known copyright restrictions" not in open(os.path.join(CACHE, "README.md"), encoding="utf-8").read():
        raise SystemExit("Shabad OS's statement on the Gurbani's copyright has changed: read it before importing")


def main():
    fetch()
    rows, seen, page, n = [], set(), 0, 0
    for sec_id in toml("sources", "SGGS.toml")["sections"]:
        sec = toml("sections", f"{sec_id}.toml")
        title = sec["name"]["Latn"]
        gloss = sec["description"].get("en", "")
        if gloss and len(gloss) < 60:  # the closing sections' one-line glosses; the rāgas carry long essays on mood
            title += f" · {gloss}"
        for g in sec["lineGroups"]:
            for line_id in toml("line-groups", g[0], f"{g}.toml")["lines"]:
                if line_id in seen:
                    raise SystemExit(f"line {line_id} is read twice")
                seen.add(line_id)
                prim = [c for c in toml("lines", line_id[0], line_id[:2], f"{line_id}.toml")["content"] if c["type"] == "primary"]
                if len(prim) != 1 or prim[0]["asset"] != "SSA2":
                    raise SystemExit(f"line {line_id}: expected one Shabadaarth primary, found {prim}")
                p = prim[0]
                if p["page"] < page:
                    raise SystemExit(f"line {line_id}: aṅg {p['page']} after aṅg {page}")
                n = n + 1 if p["page"] == page else 1
                page = p["page"]
                text = " ".join(VISHRAAM.sub(" ", p["data"]).split())
                if not CLEAN.fullmatch(text):
                    raise SystemExit(f"line {line_id}: unexpected characters in {text!r}")
                row = {"reference": f"{page}.{n}", "original": text}
                if title:
                    row["title"], title = title, None
                rows.append(row)
    if sorted({int(r["reference"].split(".")[0]) for r in rows}) != list(range(1, 1431)):
        raise SystemExit("the aṅgs are not exactly 1-1430")
    if len({r["reference"] for r in rows}) != len(rows):
        raise SystemExit("references repeat")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "guru_granth_sahib.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    if "--catalog" in sys.argv:
        text = {"id": "guru_granth_sahib", "file": "sikh/guru_granth_sahib.json", "name": "Gurū Granth Sāhib", "band": "sikh",
                "levels": ["Aṅg", "Paṅkti"], "original": ORIGINAL, "date": [1604, 1708],
                "source": "Gurmukhi: Shabad OS Database (github.com/shabados/database) after the SGPC's Shabadaarth (2009–12), public domain; no free English"}
        write([BAND], [text], {})
    print(f"guru_granth_sahib: {len(rows)} paṅktis on {page} aṅgs, {sum('title' in r for r in rows)} sections")


if __name__ == "__main__":
    main()
