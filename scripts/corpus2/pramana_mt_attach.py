#!/usr/bin/env python3
"""Attach Pramāṇa's machine English (Gemini) to texts that have no human English, in the field `text_mt` (never `text`),
and credit it in translation_sources.json.

For each job, Pramāṇa's Sanskrit (`<work>`) and machine English (`<work>~en-mt`) are read from /api/segments and joined
on their location.  Each Pramāṇa unit is then found in our own Sanskrit by exact anchors: our entries are normalised and
run together, and the unit's opening 16 characters (tried from a few offsets, in case the editions differ at the start)
are looked for a little ahead of the previous unit.  The unit's English goes on the entry it starts in; several units
starting in one entry are joined.  So it works whatever edition or numbering our copy came from, and nothing is split.
A unit that cannot be anchored is reported and left out.

This replaces any earlier `text_mt` in a job's file.  Rerun after a convert script rewrites one of these files.

Usage: python3 -I scripts/corpus2/pramana_mt_attach.py [--write] [id ...]
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_en_common import segments  # noqa: E402
from composition_dates import work  # noqa: E402
from jsonfmt import load, save  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
# Left out (Nov 2026): Kālikā Purāṇa and Kulārṇava Tantra (Pramāṇa has almost none of their English yet), the Atharva
# Prātiśākhya (its Pramāṇa Sanskrit is garbled OCR), the Kāṭhaka Āraṇyaka (still 29 units; pramana_mt_aranyakas.py has them).
JOBS = [
    "rgvidhana", "kathaka_brahmana", "kauthuma_grhyasutra", "maitrayana_sulbasutra", "manava_srautasutra",
    "atharvaveda_parisista", "visnudharmottara_purana", "ahirbudhnya_samhita", "jayakhya_samhita",
]
PROBE = 16


def norm(t):
    t = unicodedata.normalize("NFD", t or "").lower()
    t = "".join(c for c in t if not unicodedata.combining(c) or c in "̣̄")
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"\d+", "", t)
    return re.sub(r"[^a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]", "", t)


def units(path):
    sa = segments(path)
    en = {s["loc"]: (s.get("text") or "").strip() for s in segments(path + "~en-mt")}
    return [(s["loc"], s.get("text") or "", en.get(s["loc"], "")) for s in sa if (s.get("text") or "").strip()]


def attach(entries, us):
    ours = [norm(e.get("sanskrit_iast") or "") for e in entries]
    whole, starts = "", []
    for x in ours:
        starts.append(len(whole))
        whole += x
    heads, missed, pos = {}, [], 0
    for loc, sa, en in us:
        n = norm(sa)
        if len(n) < PROBE + 4:
            missed.append(loc)
            continue
        at = -1
        for off in range(0, min(240, len(n) - PROBE), 6):
            i = whole.find(n[off:off + PROBE], pos)
            if i >= 0 and i - off - pos < max(3000, 4 * len(n)):
                at = max(pos, i - off)
                break
        if at < 0:
            missed.append(loc)
            continue
        pos = at + len(n) // 2
        if not en:
            continue
        k = max(j for j, st in enumerate(starts) if st <= at)
        # a unit starting in the last tenth of an entry really begins with the next one
        if k + 1 < len(entries) and at - starts[k] > 0.9 * max(1, len(ours[k])):
            k += 1
        heads.setdefault(k, []).append(en)
    return heads, missed


def main():
    write = "--write" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    cat = {t["id"]: t for t in json.load(open(CAT, encoding="utf-8"))["texts"]}
    sources = json.load(open(SOURCES, encoding="utf-8"))
    for cid in only or JOBS:
        meta = cat[cid]
        path = work(meta)
        file = os.path.join(REPO, "public/data", meta["file"])
        entries, fmt = load(file)
        us = units(path)
        for e in entries:
            for k in ("text_mt", "text_mt_source", "text_ref"):
                e.pop(k, None)
        heads, missed = attach(entries, us)
        for k, ens in heads.items():
            entries[k]["text_mt"] = "\n\n".join(ens)
        with_en = sum(1 for _, _, en in us if en)
        print(f"{cid:26s} units {len(us):6d} with English {with_en:6d} anchored-missed {len(missed):5d}  entries now with MT {len(heads):6d} of {len(entries)}"
              + (f"  e.g. missed {missed[:4]}" if missed else ""))
        if heads:
            k = sorted(heads)[min(2, len(heads) - 1)]
            print("    ", entries[k]["reference"], "|", (entries[k].get("sanskrit_iast") or "")[:50], "=>", entries[k]["text_mt"][:90].replace("\n", " "))
        if write and heads:
            save(file, entries, fmt)
            rec = sources.get(cid, {})
            rec["machine"] = {"by": "Gemini 3.8 Flash", "year": "2026", "via": {"label": "Pramāṇa", "url": f"https://indike.org/pramana/{path}~en-mt"},
                              "note": "Machine output, unreviewed."}
            sources[cid] = rec
    if write:
        with open(SOURCES, "w", encoding="utf-8") as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
