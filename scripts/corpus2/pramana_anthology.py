#!/usr/bin/env python3
"""Anthologies of short translations from Pramāṇa: many small works, each a chapter of one library text, so a shelf of
eighty-six short sūtras or fifty-six cuneiform letters is one entry in the catalog, not eighty-six.

The parts of each anthology are listed in pramana_anthologies.json (Pramāṇa paths, taken from its sitemap). Every part
opens with a source line naming its edition and licence, as their attribution terms ask; the rest are its paragraphs,
translators' notes left out. These are licensed, not public-domain, texts (CC BY, BY-SA, BY-NC, BY-NC-SA), shared
unaltered on a free, non-commercial site on the repo owner's decision (2026-11-21); a part whose licence is unknown or
whose rights are only a permission given to Pramāṇa is refused.

Set PRAMANA_SA_WORK to the cache folder. Writes public/data/<dir>/<id>.json and the catalog and credit entries.
Usage: PRAMANA_SA_WORK=cache/pramana_world python3 -I scripts/corpus2/pramana_anthology.py [id ...]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402
from pramana_sa_common import page, segments  # noqa: E402
from pramana_world_convert import clean, is_note  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data")
PARTS = json.load(open(os.path.join(HERE, "pramana_anthologies.json"), encoding="utf-8"))

ANTHOLOGIES = {
    "lotsawa_anthology": {"name": "Lotsawa House: sūtras, dhāraṇīs and praises from the Tibetan canon", "band": "mahayana", "group": "sutra",
                          "dir": "mahayana", "by": "Adam Pearcey and other Lotsawa House translators", "licence": "CC BY-NC 4.0 (Lotsawa House)"},
    "etcsl_anthology": {"name": "Sumerian myths and hymns (ETCSL)", "band": "near_east", "dir": "near_east",
                        "by": "J. A. Black, G. Cunningham, E. Robson, G. Zólyomi et al.",
                        "licence": "ETCSL, University of Oxford: free for non-commercial use with attribution"},
    "oracc_anthology": {"name": "Cuneiform letters and inscriptions (ORACC)", "band": "near_east", "dir": "near_east",
                        "by": "the ORACC project editions", "licence": "CC BY-SA 3.0 (ORACC project editions)"},
    "greek_latin_on_india": {"name": "Greek and Latin writers on India", "band": "foreign_accounts", "dir": "foreign",
                             "by": "the Loeb and other translators (Perseus Digital Library)",
                             "licence": "CC BY-SA 4.0 (Perseus Digital Library / Open Greek and Latin)"},
    "jewish_sources_on_india": {"name": "India in Jewish sources (Sefaria)", "band": "foreign_accounts", "dir": "foreign",
                                "by": "Sefaria's translators", "licence": "CC BY, CC BY-SA or CC BY-NC, as each part states (Sefaria)"},
}
BANDS = [
    {"id": "near_east", "after": ["kin", "avesta"], "name": "Ancient Near East",
     "blurb": "not Indic: Sumer's myths of Enki and the gods' order of the world, and the cuneiform letters of the age of the Mitanni, "
              "whose kings swore by Mitra, Varuṇa and Indra. In English"},
    {"id": "foreign_accounts", "after": ["travel"], "name": "India seen from outside",
     "blurb": "what Greek, Roman and Jewish writers said of India, in English"},
]


def refused(lic):
    l = lic.lower()
    return not l.strip() or "unknown" in l or "permission" in l or "in copyright" in l


def part_rows(n, path):
    p = page(path)
    doc = p.get("doc") or {}
    prov = p.get("provenance") or []
    lic = "; ".join(x.get("license") or "" for x in prov)
    if refused(lic):
        return None, lic
    title = clean(doc.get("title_en") or doc.get("title") or path.rsplit(".", 1)[-1])
    work = " ".join(b.get("title_en") or b.get("title") or "" for b in (p.get("breadcrumbs") or [])[-1:]).strip()
    edition = "; ".join(sorted({(x.get("edition") or "").strip() for x in prov if x.get("edition")}))
    urls = " ".join(sorted({(x.get("url") or "").strip() for x in prov if x.get("url")}))
    head = f"{work} — {title}" if work and work.lower() not in title.lower() else title
    rows = [{"reference": f"{n}.1", "title": head, "text": f"Source: {edition or 'see Pramāṇa'}. Licence: {lic}. {urls}".strip()}]
    for s in segments(path):
        if is_note(s):
            continue
        t = clean(s.get("text") or "")
        if t:
            rows.append({"reference": f"{n}.{len(rows) + 1}", "text": t})
    return (rows if len(rows) > 1 else None), lic


def main():
    only = set(sys.argv[1:])
    texts, records = [], {}
    for aid, a in ANTHOLOGIES.items():
        if only and aid not in only:
            continue
        rows, skipped = [], []
        for path in PARTS[aid]:
            got, lic = part_rows(len({r["reference"].split(".")[0] for r in rows}) + 1, path)
            if got is None:
                skipped.append((path, lic[:80]))
                continue
            rows += got
        os.makedirs(os.path.join(DATA, a["dir"]), exist_ok=True)
        with open(os.path.join(DATA, a["dir"], f"{aid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        parts = len({r["reference"].split(".")[0] for r in rows})
        texts.append({"id": aid, "file": f"{a['dir']}/{aid}.json", "name": a["name"], "band": a["band"], **({"group": a["group"]} if a.get("group") else {}),
                      "levels": ["Text", "Paragraph"], "source": f"Pramāṇa (indike.org/pramana): {parts} short translations; {a['licence']}"})
        records[aid] = {"english": {"by": a["by"], "work": a["name"], "year": "various",
                                    "links": [{"label": "Pramāṇa", "url": "https://indike.org/pramana/"}],
                                    "via": {"label": "Pramāṇa", "url": "https://indike.org/pramana/"},
                                    "note": f"Licence: {a['licence']}. Each part opens with its own edition and licence."}}
        print(f"{aid:26s} {parts:3d} parts {len(rows):5d} entries; skipped {len(skipped)} {skipped[:3]}", flush=True)
    write(BANDS, texts, records)


if __name__ == "__main__":
    main()
