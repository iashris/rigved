#!/usr/bin/env python3
"""Insert catalog entries for the pramana_sa files into library_catalog.json next to their siblings (idempotent;
line-based so other entries and formatting are untouched)."""
import json
import os
import re

CAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_catalog.json")


def e(id_, file, name, levels, source, **kw):
    d = {"id": id_, "file": file, "name": name, **kw, "levels": levels, "source": source}
    return "    " + json.dumps(d, ensure_ascii=False) + ","


P = "Pramāṇa (indike.org/pramana)"
AFTER = {
    "apastamba_sulbasutra": [
        e("baudhayana_srautasutra", "sutras/baudhayana_srautasutra.json", "Baudhāyana Śrautasūtra", ["Praśna", "Kaṇḍikā", "Page", "Line"],
          f"{P}: TITUS e-text of W. Caland's edition (1904–24), cited praśna.kaṇḍikā:page.line", veda="kyv", layer="sutra"),
        e("baudhayana_sulbasutra", "sutras/baudhayana_sulbasutra.json", "Baudhāyana Śulbasūtra", ["Khaṇḍa", "Sūtra"],
          f"{P}: TITUS (Sen & Bag 1983)", veda="kyv", layer="sutra"),
    ],
    "hiranyakesin_grhyasutra": [
        e("hiranyakesin_sulbasutra", "sutras/hiranyakesin_sulbasutra.json", "Hiraṇyakeśi Śulbasūtra", ["Praśna", "Paṭala", "Sūtra"],
          f"{P}: Vedic Reserve e-text (Ānandāśrama ed. 1907, praśna 25)", veda="kyv", layer="sutra"),
    ],
    "manava_grhyasutra": [
        e("manava_sulbasutra", "sutras/manava_sulbasutra.json", "Mānava Śulbasūtra", ["Khaṇḍa", "Sūtra"],
          f"{P}: TITUS (Sen & Bag 1983)", veda="kyv", layer="sutra"),
        e("maitrayana_sulbasutra", "sutras/maitrayana_sulbasutra.json", "Maitrāyaṇīya Śulbasūtra", ["Khaṇḍa", "Sūtra"],
          f"{P}: Vedic Reserve e-text (ed. Damodar Jha)", veda="kyv", layer="sutra"),
    ],
    "paraskara_grhyasutra": [
        e("katyayana_sulbasutra", "sutras/katyayana_sulbasutra.json", "Kātyāyana Śulbasūtra", ["Khaṇḍa", "Sūtra"],
          f"{P}: TITUS (Sen & Bag 1983)", veda="syv", layer="sutra"),
    ],
    "nirukta": [
        e("sarvanukramani", "other/sarvanukramani.json", "Sarvānukramaṇī of Kātyāyana", ["Part", "Section / Maṇḍala", "Sūtra / Sūkta"],
          f"{P}: Sansknet e-text; part 1 paribhāṣā, part 2 index by Ṛgveda maṇḍala.sūkta", band="vedanga"),
        e("jyotisa_rk", "other/jyotisa_rk.json", "Ārca Jyotiṣa (Ṛgveda Vedāṅga Jyotiṣa)", ["Verse"],
          f"{P}: GRETIL (K. V. Sarma ed., input O. Hellwig)", band="vedanga"),
        e("jyotisa_yajus", "other/jyotisa_yajus.json", "Yājuṣa Jyotiṣa (Yajurveda Vedāṅga Jyotiṣa)", ["Verse"],
          f"{P}: sanskritdocuments.org", band="vedanga"),
        e("jyotisa_atharva", "other/jyotisa_atharva.json", "Ātharvaṇa Jyotiṣa", ["Prakaraṇa", "Verse"],
          f"{P}: Wikisource (Bhagavad Datta ed. 1924), OCR; partial", band="vedanga"),
        e("pingala_chandahsutra", "other/pingala_chandahsutra.json", "Chandaḥsūtra of Piṅgala", ["Adhyāya", "Sūtra"],
          f"{P}: Vedic Reserve e-text", band="vedanga"),
        e("atharvaveda_parisista", "other/atharvaveda_parisista.json", "Atharvaveda Pariśiṣṭa", ["Pariśiṣṭa", "Khaṇḍa", "Verse"],
          f"{P}: GRETIL (Bolling & von Negelein 1909–10)", band="vedanga"),
    ],
}

lines = open(CAT, encoding="utf-8").read().split("\n")
ID = re.compile(r'^\s*\{"id": "([^"]+)"')
have = {ID.match(l).group(1) for l in lines if ID.match(l)}
out = []
for i, line in enumerate(lines):
    out.append(line)
    s = line.strip()
    if not ID.match(line) or not s.endswith(("},", "}")):  # anchors are one-line entries
        continue
    anchor = ID.match(line).group(1)
    new = [n for n in AFTER.get(anchor, []) if ID.match(n).group(1) not in have]
    if not new:
        continue
    if not s.endswith(","):  # anchor was the last entry: it now needs a comma, the last new one must not have one
        out[-1] = line + ","
        new[-1] = new[-1].rstrip(",")
    out += new
open(CAT, "w", encoding="utf-8").write("\n".join(out))
json.load(open(CAT, encoding="utf-8"))
print("catalog ok")
