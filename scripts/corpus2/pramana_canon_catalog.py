#!/usr/bin/env python3
"""Add pramana_canon_texts to library_catalog.json and translation_sources.json. Rerunnable.

Every translation is paired by the concordance pramana_canon_concordance.py writes, never `aligned`: that mode shows
only verses with a Sanskrit counterpart, which would hide part of these translations.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_canon_convert import DATA, english_id  # noqa: E402
from pramana_canon_texts import BANDS, CANON  # noqa: E402
from pramana_sa_common import page  # noqa: E402

CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
SA_LEVELS = {1: ["Verse"], 2: ["Adhyāya", "Verse"], 3: ["Khaṇḍa", "Adhyāya", "Verse"], 4: ["Part", "Khaṇḍa", "Adhyāya", "Verse"], 5: ["Part", "Book", "Khaṇḍa", "Adhyāya", "Verse"]}
EN_LEVELS = {1: ["Paragraph"], 2: ["Adhyāya", "Paragraph"], 3: ["Book", "Adhyāya", "Paragraph"], 4: ["Part", "Book", "Adhyāya", "Paragraph"], 5: ["Part", "Book", "Adhyāya", "Section", "Paragraph"]}
LEVELS = {"brahma_sutra": ["Adhyāya", "Pāda", "Sūtra"], "yoga_sutra": ["Pāda", "Sūtra"], "nyaya_sutra": ["Adhyāya", "Āhnika", "Sūtra"], "vaisesika_sutra": ["Adhyāya", "Āhnika", "Sūtra"],
          "mimamsa_sutra": ["Adhyāya", "Pāda", "Sūtra"], "samkhya_sutra": ["Adhyāya", "Sūtra"], "samkhya_karika": ["Part", "Kārikā"], "bhagavad_gita": ["Adhyāya", "Śloka"],
          "astadhyayi": ["Adhyāya", "Pāda", "Sūtra"], "devi_bhagavata_purana": ["Skandha", "Adhyāya", "Śloka"]}


def load(folder, name):
    return json.load(open(os.path.join(DATA, folder, name + ".json"), encoding="utf-8"))


def depth(entries):
    counts = {}
    for e in entries:
        d = e["reference"].count(".") + 1
        counts[d] = counts.get(d, 0) + 1
    return max(counts, key=counts.get)


def provenance(path):
    return page(path).get("provenance") or []


def source(path):
    seen = []
    for p in provenance(path):
        label = (p.get("edition") or "").split(" — ")[0].strip()
        label = f"{p.get('repo')}: {label[:90]}" if label else str(p.get("repo"))
        if label not in seen:
            seen.append(label)
    return "Pramāṇa (indike.org/pramana), " + path + (" · " + "; ".join(seen[:2]) if seen else "")


def source_record(t):
    pv = provenance(t["en"])
    edition = next((p.get("edition") for p in pv if p.get("edition")), "")
    links = t.get("en_links") or [{"label": re.sub(r"^https?://(www\.)?", "", p["url"]).split("/")[0], "url": p["url"]} for p in pv if p.get("url")]
    if not links:
        raise SystemExit(f"{t['en']}: Pramāṇa records no URL for this translation")
    years = re.search(r"\(([\d–-]+)\)", t["en_label"])
    by = re.split(r"\s*\(tr\.\)|,", edition, maxsplit=1)[0].strip()
    work = re.sub(r"^.*?\(tr\.\),?\s*", "", edition) if "(tr.)" in edition else edition.split(", ", 1)[-1]
    return {"english": {"by": by, "work": work, "year": years.group(1) if years else "", "links": links,
                        "via": {"label": "Pramāṇa", "url": "https://indike.org/pramana/" + t["en"]}}}


cat = json.load(open(CAT, encoding="utf-8"))
known = {t["id"]: t for t in cat["texts"]}
new, records = [], {}
for cid, t in CANON.items():
    folder = t.get("attach") or t["dir"]
    pair = None
    if t.get("en"):
        name = english_id(cid, t)
        en = load(folder, name)
        pair = {"with": name, "mode": "concordance", "label": t["en_label"]}
        records[cid] = source_record(t)
    if not t.get("attach"):
        sa = load(folder, cid)
        place = {k: t[k] for k in ("veda", "layer", "band", "group") if t.get(k)}
        entry = {"id": cid, "file": f"{folder}/{cid}.json", "name": t["name"], **place, "levels": LEVELS.get(cid, SA_LEVELS[depth(sa)]), "source": source(t["sa"])}
        if pair:
            entry["pairs"] = [pair]
        new.append(entry)
    if pair:
        host = t.get("name") or known[cid]["name"]
        place = {k: t[k] for k in ("veda", "layer", "band") if t.get(k)}
        if t.get("attach"):
            place = {k: known[cid][k] for k in ("veda", "layer", "band") if known[cid].get(k)}
        new.append({"id": name, "file": f"{folder}/{name}.json", "name": f"{host} — {t['en_name']}", **place, "translationOf": cid,
                    "levels": EN_LEVELS[depth(en)], "source": source(t["en"])})

# Edit as text: the catalog is laid out by hand, one text per line.
raw = open(CAT, encoding="utf-8").read()
ours = {e["id"] for e in new} - {c for c, t in CANON.items() if t.get("attach")}
bands = {b["id"] for b in BANDS}


def is_ours(line):
    m = re.match(r'\s*\{"id": "([^"]+)"', line)
    return bool(m) and (m.group(1) in ours or (m.group(1) in bands and '"blurb"' in line))


lines = [ln for ln in raw.split("\n") if not is_ours(ln)]
for cid, t in CANON.items():
    if t.get("attach"):
        pair = {"with": english_id(cid, t), "mode": "concordance", "label": t["en_label"]}
        for i, ln in enumerate(lines):
            if ln.lstrip().startswith(f'{{"id": "{cid}"'):
                lines[i] = re.sub(r',\s*"pairs": \[.*?\]\}(,?)$', r"}\1", ln)
                lines[i] = re.sub(r"\}(,?)$", lambda m: ', "pairs": ' + json.dumps([pair], ensure_ascii=False) + "}" + m.group(1), lines[i])
                break
        else:
            raise SystemExit(f"{cid}: not a one-line entry in the catalog")
for band in BANDS:
    row = {k: v for k, v in band.items() if k != "after"}
    at = next(i for i, ln in enumerate(lines) if f'{{"id": "{band["after"]}", "name"' in ln)
    lines.insert(at + 1, "    " + json.dumps(row, ensure_ascii=False) + ",")
raw = "\n".join(lines)
head, tail = raw.rsplit("\n  ]\n}", 1)
open(CAT, "w", encoding="utf-8").write(head.rstrip().rstrip(",") + ",\n" + ",\n".join("    " + json.dumps(e, ensure_ascii=False) for e in new) + "\n  ]\n}" + tail)
cat = json.load(open(CAT, encoding="utf-8"))
print(len(cat["texts"]), "texts;", [b["id"] for b in cat["bands"]])

have = json.load(open(SOURCES, encoding="utf-8")) if os.path.exists(SOURCES) else {}
have.update(records)
with open(SOURCES, "w", encoding="utf-8") as f:
    json.dump(have, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(len(records), "source records written;", len(have), "in all")
