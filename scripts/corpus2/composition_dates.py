#!/usr/bin/env python3
"""Write each text's approximate date of composition into library_catalog.json as `date: [start, end]` (negative = BCE).

The dates are Pramāṇa's consensus claim for the work (indike.org/pramana, the page's `consensus.date`), each end taken
as the midpoint of its range, so [-950..-850, -800..-650] becomes [-900, -725]; a point estimate (both midpoints the
same year) keeps its whole window instead, so "c. 0 ± 100" shows as [-100, 100]. PATHS ties each catalog text to its
Pramāṇa work. A text missing from it, or one whose work carries no consensus date, gets no date.
A dated text's English edition (`translationOf`) is not shown on the home page and is not dated.

Usage: python3 -I scripts/corpus2/composition_dates.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_sa_common import page  # noqa: E402

CAT = os.path.join(HERE, "library_catalog.json")
PATH_IN_SOURCE = re.compile(r"\b(in\.[a-z0-9_.!-]+)")

# Catalog id -> Pramāṇa work, for the texts whose `source` line does not already name it.
V = "in.veda."
K = "in.vedanga.kalpa."
PATHS = {
    "rigveda": V + "samhita.rg",
    "rgveda_khilani": "in.vedanga.misc.parisista.rgveda.rgvedakhila",
    "samaveda": V + "samhita.sama",
    "atharvaveda": V + "samhita.atharva*saunaka",
    "paippalada_samhita": V + "samhita.atharva*paippalada",
    "taittiriya_samhita": V + "samhita.krsnayajur*taittiriya",
    "maitrayani_samhita": V + "samhita.krsnayajur*maitrayani",
    "kathaka_samhita": V + "samhita.krsnayajur*kathaka",
    "kathaka_samhita_asvamedha": V + "samhita.krsnayajur*kathaka",
    "kapisthala_samhita": V + "samhita.krsnayajur*kapisthala",
    "vajasaneyi_samhita": V + "samhita.suklayajur*vajasaneyi",
    "kanva_samhita": V + "samhita.suklayajur*vajasaneyi*kanva",
    "aitareya_brahmana": V + "brahmana.aitreya",
    "kausitaki_brahmana": V + "brahmana.kausitaki",
    "pancavimsa_brahmana": V + "brahmana.pancavimsa",
    "jaiminiya_brahmana": V + "brahmana.jaiminiya",
    "jaiminiya_upanisad_brahmana": V + "brahmana.jaiminiya_upanisad",
    "mantra_brahmana": V + "brahmana.mantra",
    "devatadhyaya_brahmana": V + "brahmana.daivata",
    "vamsa_brahmana": V + "brahmana.vamsa",
    "taittiriya_brahmana": V + "brahmana.taittiriya",
    "kathaka_brahmana": V + "brahmana.kathaka",
    "satapatha_brahmana": V + "brahmana.satapatha",
    "gopatha_brahmana": V + "brahmana.gopatha",
    "aitareya_aranyaka": V + "aranyaka.aitareya",
    "sankhayana_aranyaka": V + "aranyaka.kausitaki",
    "taittiriya_aranyaka": V + "aranyaka.taittiriya",
    "kathaka_aranyaka": V + "aranyaka.katha",
    "mahanarayana_upanishad": V + "aranyaka.taittiriya",  # it is Taittirīya Āraṇyaka book 10
    "aitareya_upanishad": V + "upanisad.mukhya.aitreya",
    "kausitaki_upanishad": V + "upanisad.mukhya.kausitaki",
    "chandogya_upanishad": V + "upanisad.mukhya.chandogya",
    "kena_upanishad": V + "upanisad.mukhya.kena",
    "taittiriya_upanishad": V + "upanisad.mukhya.taittiriya",
    "katha_upanishad": V + "upanisad.mukhya.katha",
    "svetasvatara_upanishad": V + "upanisad.mukhya.svetasvatara",
    "maitri_upanishad": V + "upanisad.mukhya.maitri",
    "brhadaranyaka_upanishad": V + "upanisad.mukhya.brhadaranyaka",
    "isha_upanishad": V + "upanisad.mukhya.isa",
    "mundaka_upanishad": V + "upanisad.mukhya.mundaka",
    "mandukya_upanishad": V + "upanisad.mukhya.mandukya",
    "prasna_upanishad": V + "upanisad.mukhya.prasna",
    "nadabindu_upanishad": V + "upanisad.yoga.nadabindu",
    "kaivalya_upanishad": V + "upanisad.saiva.kaivalya",
    "garbha_upanishad": V + "upanisad.samanya.garbha",
    "brahmabindu_upanishad": V + "upanisad.yoga.amrtabindu",  # the same text as our Amṛtabindu
    "sivasamkalpa_upanishad": V + "upanisad.noncanon.navya.sivasamkalpa",
    "atharvasiras_upanishad": V + "upanisad.saiva.atharvashiras",
    "asvalayana_srautasutra": K + "srauta.asvalayana-school.asvalayana",
    "sankhayana_srautasutra": K + "srauta.sankhayana-school.sankhayana",
    "baudhayana_srautasutra": K + "srauta.baudhayana-school.baudhayana",
    "vaitana_sutra": K + "srauta.vaitana-school.vaitanasutra",
    "asvalayana_grhyasutra": K + "grhya.rgveda.asvalayana",
    "sankhayana_grhyasutra": K + "grhya.rgveda.sankhayana",
    "gobhila_grhyasutra": K + "grhya.samaveda.gobhila",
    "khadira_grhyasutra": K + "grhya.samaveda.khadira",
    "jaiminiya_grhyasutra": K + "grhya.samaveda.jaiminiya",
    "kauthuma_grhyasutra": K + "grhya.samaveda.kauthuma",
    "apastamba_grhyasutra": K + "grhya.krsnayajur.apastamba",
    "hiranyakesin_grhyasutra": K + "grhya.krsnayajur.hiranyakesi",
    "manava_grhyasutra": K + "grhya.krsnayajur.manava",
    "varaha_grhyasutra": K + "grhya.krsnayajur.varaha",
    "paraskara_grhyasutra": K + "grhya.paraskara",
    "kausika_sutra": K + "grhya.atharvaveda.kausika",
    "vasistha_dharmasutra": K + "dharma.vasistha",
    "gautama_dharmasutra": K + "dharma.gautama",
    "apastamba_dharmasutra": K + "dharma.apastamba",
    "baudhayana_dharmasutra": K + "dharma.baudhayana",
    "manu_smrti": K + "dharma.manusmrti",
    "apastamba_sulbasutra": K + "sulba.apastamba",
    "baudhayana_sulbasutra": K + "sulba.baudhayana",
    "hiranyakesin_sulbasutra": K + "sulba.hiranyakesi",
    "manava_sulbasutra": K + "sulba.manava",
    "maitrayana_sulbasutra": K + "sulba.maitrayana",
    "katyayana_sulbasutra": K + "sulba.katyayana",
    "rgvidhana": "in.vedanga.misc.vidhana.rgvidhana-works.rg",
    "nirukta": "in.vedanga.nirukta.yaska",
    "brhaddevata": "in.vedanga.misc.anukramani.saunaka.brhaddevata",
    "sarvanukramani": "in.vedanga.misc.anukramani.katyayana.sarvanukramani",
    "jyotisa_rk": "in.vedanga.jyotisa.rk",
    "jyotisa_yajus": "in.vedanga.jyotisa.yajus",
    "jyotisa_atharva": "in.vedanga.jyotisa.atharva",
    "pingala_chandahsutra": "in.vedanga.chanda.pingala-school.pingala",
    "atharvaveda_parisista": "in.vedanga.misc.parisista.atharvaveda.atharva",
    "mahabharata": "in.lit.mahabharata.vyasa",
    "harivamsa": "in.lit.mahabharata.harivamsa",
    "ramayana": "in.lit.ramayana.valmiki",
}


def mid(a, b):
    return round((a + b) / 2)


def date_of(path):
    claim = ((page(path).get("consensus") or {}).get("date") or {}).get("claim")
    if not claim or claim.get("start_lo") is None:
        return None
    start = mid(claim["start_lo"], claim.get("start_hi", claim["start_lo"]))
    end_lo = claim.get("end_lo") if claim.get("end_lo") is not None else claim["start_lo"]
    end_hi = claim.get("end_hi") if claim.get("end_hi") is not None else end_lo
    end = mid(end_lo, end_hi)
    if start >= end:
        # A point estimate with an uncertainty window (-100..100 for "around the turn of the era"): show the window,
        # not a midpoint that reads as an exact year.
        return [round(claim["start_lo"]), round(max(end_hi, claim["start_lo"]))]
    return [start, end]


def work(entry):
    if entry["id"] in PATHS:
        return PATHS[entry["id"]]
    m = PATH_IN_SOURCE.search(entry.get("source", ""))
    return m.group(1).rstrip(".") if m else None


def main():
    raw = open(CAT, encoding="utf-8").read()
    texts = json.loads(raw)["texts"]
    lines = raw.split("\n")
    dated, missing = 0, []
    for entry in texts:
        if entry.get("translationOf"):
            continue
        path = work(entry)
        date = date_of(path) if path else None
        # Entries are hand-laid (some run over several lines), so edit the entry's first line in place rather than
        # re-serialising: drop an old date, then set the new one just after the name.
        head = f'{{"id": "{entry["id"]}", '
        i = next(n for n, line in enumerate(lines) if line.lstrip().startswith(head))
        line = re.sub(r'"date": \[-?\d+, -?\d+\], ', "", lines[i])
        if date:
            name = f'"name": {json.dumps(entry["name"], ensure_ascii=False)}, '
            assert name in line, entry["id"]
            line = line.replace(name, f'{name}"date": [{date[0]}, {date[1]}], ', 1)
            dated += 1
        else:
            missing.append(f"{entry['id']} ({path or 'no Pramāṇa work'})")
        lines[i] = line
    out = "\n".join(lines)
    json.loads(out)  # still valid
    open(CAT, "w", encoding="utf-8").write(out)
    print(dated, "dated")
    if missing:
        print("no date:", ", ".join(missing))


if __name__ == "__main__":
    main()
