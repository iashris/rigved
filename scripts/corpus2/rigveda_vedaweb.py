#!/usr/bin/env python3
"""Three more English Ṛgvedas for the reader's translation switcher, beside Griffith and Jamison & Brereton:
Max Müller's Vedic Hymns I (SBE 32, 1891: the hymns to the Maruts, Rudra, Vāyu and Vāta), Hermann Oldenberg's Vedic
Hymns II (SBE 46, 1897: the hymns to Agni in maṇḍalas I–V) and A. A. Macdonell's Hymns from the Rigveda (1922).

Taken from Pramāṇa, which has them verse by verse from VedaWeb's TEI (University of Cologne), under CC BY-NC-SA 4.0;
the translations themselves are public domain. Each is keyed maṇḍala.sūkta.ṛc like the Saṃhitā, so the reader pairs
it verse by verse (mode "aligned"); notes are left out. Writes public/data/vedas/rigveda_<id>.json and adds the rows
and the pairs to library_catalog.json, and the credits to translation_sources.json. Rerunnable.

Usage: PRAMANA_SA_WORK=cache/pramana_world python3 -I scripts/corpus2/rigveda_vedaweb.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_sa_common import segments  # noqa: E402
from pramana_world_convert import clean  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data", "vedas")
CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
LICENCE = "VedaWeb (University of Cologne), CC BY-NC-SA 4.0; the translation itself is public domain"
VERSIONS = [
    ("rigveda_muller", "in.veda.samhita.rg~en-muller", "Müller (1891)", "F. Max Müller",
     "Vedic Hymns, Part I: Hymns to the Maruts, Rudra, Vâyu, and Vâta, Sacred Books of the East 32, Oxford: Clarendon Press", "1891"),
    ("rigveda_oldenberg", "in.veda.samhita.rg~en-oldenberg", "Oldenberg (1897)", "Hermann Oldenberg",
     "Vedic Hymns, Part II: Hymns to Agni (Mandalas I–V), Sacred Books of the East 46, Oxford: Clarendon Press", "1897"),
    ("rigveda_macdonell", "in.veda.samhita.rg~en-macdonell", "Macdonell (1922)", "A. A. Macdonell",
     "Hymns from the Rigveda, Heritage of India series, Calcutta: Association Press", "1922"),
]


def rows(path):
    out = []
    for s in segments(path):
        m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", s["loc"])
        t = clean(s.get("text") or "")
        if s.get("kind") == "verse" and m and t:
            a, b, c = (int(x) for x in m.groups())
            out.append({"reference": f"{a:02d}.{b:03d}.{c:02d}", "text": t, "mandala": a, "hymn": b, "verse": c})
    return out


def main():
    raw = open(CAT, encoding="utf-8").read()
    lines = raw.split("\n")
    ids = {v[0] for v in VERSIONS}
    lines = [ln for ln in lines if not any(ln.strip().startswith(f'{{"id": "{i}"') for i in ids)]
    at = next(i for i, ln in enumerate(lines) if ln.strip().startswith('{"id": "rigveda_jamison_brereton"'))
    new_rows, credits = [], {}
    for tid, path, label, by, work, year in VERSIONS:
        rs = rows(path)
        with open(os.path.join(DATA, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rs, f, ensure_ascii=False, indent=1)
        hymns = len({r["reference"].rsplit(".", 1)[0] for r in rs})
        new_rows.append("    " + json.dumps({"id": tid, "file": f"vedas/{tid}.json", "name": f"Ṛgveda Saṃhitā — {by}", "veda": "rv", "layer": "samhita",
                                             "translationOf": "rigveda", "levels": ["Maṇḍala", "Sūkta", "Ṛc"],
                                             "source": f"{by}, {work} ({year}), {hymns} hymns; via VedaWeb and Pramāṇa"}, ensure_ascii=False) + ",")
        credits[tid] = {"english": {"by": by, "work": work, "year": year, "links": [{"label": "VedaWeb", "url": "https://vedaweb.uni-koeln.de/"}],
                                    "via": {"label": "Pramāṇa", "url": "https://indike.org/pramana/" + path}, "note": f"Licence: {LICENCE}. Only the hymns this translator rendered."}}
        print(f"{tid}: {len(rs)} verses in {hymns} hymns")
    lines[at + 1:at + 1] = new_rows
    raw = "\n".join(lines)
    # The Saṃhitā's switcher: Griffith (its own English), then Jamison & Brereton, then these.
    m = re.search(r'("id": "rigveda", [^{]*?"pairs": )(\[.*?\])', raw, re.S)
    pairs = [p for p in json.loads(m.group(2)) if p["with"] not in ids]
    pairs += [{"with": tid, "mode": "aligned", "label": label} for tid, _, label, *_ in VERSIONS]
    raw = raw[:m.start(2)] + json.dumps(pairs, ensure_ascii=False) + raw[m.end(2):]
    open(CAT, "w", encoding="utf-8").write(raw)
    json.load(open(CAT, encoding="utf-8"))
    have = json.load(open(SOURCES, encoding="utf-8"))
    have.update(credits)
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(have, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
