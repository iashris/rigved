"""Add the Purāṇas to library_catalog.json, with sources from Pramāṇa's provenance records. Rerunnable."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_purana_texts import PURANA_GROUPS, PURANAS  # noqa: E402
from pramana_sa_common import page  # noqa: E402

CAT = os.path.join(HERE, "library_catalog.json")
DATA = os.path.join(HERE, "..", "..", "public", "data", "puranas")
LEVELS = {2: ["Adhyāya", "Śloka"], 3: ["Khaṇḍa", "Adhyāya", "Śloka"], 4: ["Saṃhitā", "Khaṇḍa", "Adhyāya", "Śloka"]}
EN_LEVELS = {2: ["Adhyāya", "Paragraph"], 3: ["Book", "Adhyāya", "Paragraph"], 4: ["Part", "Book", "Adhyāya", "Paragraph"]}


def depth(name):
    d = json.load(open(os.path.join(DATA, name + ".json"), encoding="utf-8"))
    return collections.Counter(e["reference"].count(".") + 1 for e in d).most_common(1)[0][0]


def source(path):
    seen = []
    for p in page(path).get("provenance") or []:
        label = (p.get("edition") or "").split(" — ")[0].strip() or p.get("repo") or ""
        label = f"{p.get('repo')}: {label[:90]}" if p.get("edition") else str(p.get("repo"))
        if label not in seen:
            seen.append(label)
    return "Pramāṇa (indike.org/pramana), " + path + (" · " + "; ".join(seen[:2]) if seen else "")


cat = json.load(open(CAT, encoding="utf-8"))
new = []
for cid, t in PURANAS.items():
    src = source(t["sa"]) + (" · machine English from Pramāṇa, labelled" if t.get("mt") else "")
    new.append({"id": cid, "file": f"puranas/{cid}.json", "name": t["name"], "band": "purana", "group": t["group"], "levels": LEVELS[depth(cid)], "source": src})
    if t.get("en"):
        name = f"{cid}_{t['en_name'].lower().replace(' ', '')}"
        new[-1]["pairs"] = [{"with": name, "mode": "concordance", "label": t["en_label"]}]
        new.append({"id": name, "file": f"puranas/{name}.json", "name": f"{t['name']} — {t['en_name']}", "band": "purana",
                    "translationOf": cid, "levels": EN_LEVELS[depth(name)], "source": source(t["en"])})

# Edit the file as text: it is laid out by hand, one text per line, and rewriting it would bury the change.
raw = open(CAT, encoding="utf-8").read()
ours = {f'{{"id": "{e["id"]}",' for e in new}  # the band also holds Upapurāṇas from pramana_canon_catalog.py
kept = [ln for ln in raw.split("\n") if ln.strip().split(" \"file\"")[0] not in ours and '"id": "purana"' not in ln]
raw = "\n".join(kept)
band = {"id": "purana", "name": "Purāṇa", "blurb": "the old stories retold, grouped by the god each puts first", "groups": PURANA_GROUPS}
raw = raw.replace('    {"id": "smrti", "name": "Smṛti"', "    " + json.dumps(band, ensure_ascii=False) + ',\n    {"id": "smrti", "name": "Smṛti"', 1)
lines = ",\n".join("    " + json.dumps(e, ensure_ascii=False) for e in new)
head, tail = raw.rsplit("\n  ]\n}", 1)
open(CAT, "w", encoding="utf-8").write(head.rstrip().rstrip(",") + ",\n" + lines + "\n  ]\n}" + tail)
cat = json.load(open(CAT, encoding="utf-8"))
print(len(cat["texts"]), "texts in catalog;", sum(1 for t in cat["texts"] if t.get("band") == "purana"), "Purāṇa files")
