#!/usr/bin/env python3
"""Credit the English of the older corpus files in translation_sources.json. Idempotent; other records are left alone.

Each attribution was tested by finding our own text at the source, not taken from an old label: that test is how Manu
turned out to be Jhā rather than Bühler, and Chāndogya mostly Nikhilananda. A record with `noSource` has no public
source to link, which the reader says outright.

Usage: python3 -I scripts/corpus2/translation_credits.py
"""
import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ST = "https://sacred-texts.com/hin/"
PR = "https://indike.org/pramana/"
GUT = "https://www.gutenberg.org/ebooks/"
WL = "https://www.wisdomlib.org/hinduism/book/"
ASHRAM = "https://search.motherandsriaurobindo.in/_StaticContent/SriAurobindoAshram/-09 E-Library/-01 Works of Sri Aurobindo/-01 English/-03_CWSA/"
UPANISHADS_ORG = {"label": "upanishads.org.in", "url": "https://upanishads.org.in/"}


def link(label, url):
    return {"label": label, "url": quote(url, safe=":/~*!-_.%")}


def sacred(path):
    return [link("sacred-texts.com", ST + path)]


def pramana(path):
    return link("Pramāṇa", PR + path)


def english(by, work, year, links, via=None, note=None):
    rec = {"by": by, "work": work, "links": links}
    if year:
        rec["year"] = year
    if via:
        rec["via"] = via
    if note:
        rec["note"] = note
    return {"english": rec}


def aurobindo(work_file, verified_note=None):
    return english("Sri Aurobindo", "Kena and Other Upanishads, Complete Works of Sri Aurobindo vol. 18", None,
                   [link("Sri Aurobindo Ashram", ASHRAM + "-18_Kena And Other Upanishads/" + work_file)], UPANISHADS_ORG, verified_note)


def sbe(by, work, year, vol):
    return english(by, f"{work}, Sacred Books of the East vol. {vol}", year, sacred(f"sbe{vol:02d}/index.htm"))


GRIHYA_1 = ("Hermann Oldenberg", "The Grihya-Sûtras, Part I", "1886", 29)
GRIHYA_2 = ("Hermann Oldenberg", "The Grihya-Sûtras, Part II", "1892", 30)
LAWS_1 = ("Georg Bühler", "The Sacred Laws of the Âryas, Part I", "1879", 2)
LAWS_2 = ("Georg Bühler", "The Sacred Laws of the Âryas, Part II", "1882", 14)

CREDITS = {
    "rigveda": english("R. T. H. Griffith", "The Hymns of the Rigveda", "1896", sacred("rigveda/index.htm")),
    "samaveda": english("R. T. H. Griffith", "The Hymns of the Samaveda", "1893", sacred("sv.htm")),
    "atharvaveda": english("R. T. H. Griffith", "The Hymns of the Atharvaveda", "1895", sacred("av/index.htm")),
    "yajurveda_white": english("R. T. H. Griffith", "The Texts of the White Yajurveda", "1899", sacred("wyv/index.htm")),
    "yajurveda_black": english("A. B. Keith", "The Veda of the Black Yajus School, Harvard Oriental Series 18–19", "1914", sacred("yv/index.htm")),
    "satapatha_brahmana": english("Julius Eggeling", "The Śatapatha-Brāhmaṇa, Sacred Books of the East vols. 12, 26, 41, 43, 44", "1882–1900",
                                  sacred("sbr/sbe12/index.htm"), link("wisdomlib", WL + "satapatha-brahmana-english")),
    "aitareya_brahmana": english("A. B. Keith", "Rigveda Brahmanas, Harvard Oriental Series 25", "1920",
                                 [link("archive.org", "https://archive.org/details/rigvedabrahmana00keitgoog")], pramana("in.veda.brahmana.aitreya~en-keith")),
    "maitri_upanishad": english("F. Max Müller", "The Upanishads, Part II, Sacred Books of the East vol. 15", "1884", sacred("sbe15/index.htm"),
                                pramana("in.veda.upanisad.mukhya.maitri~en-muller")),
    "brhaddevata": english("A. A. Macdonell", "The Bṛhad-Devatā attributed to Śaunaka, Harvard Oriental Series 5–6", "1904",
                           [link("wisdomlib", WL + "brihaddevata-attributed-to-shaunaka")], pramana("in.vedanga.misc.anukramani.saunaka.brhaddevata~en-macdonell")),
    "manu_smrti": english("Gaṅgānāth Jhā", "Manusmṛti with the Commentary of Medhātithi", "from 1920",
                          [link("wisdomlib", WL + "manusmriti-with-the-commentary-of-medhatithi")]),
    "asvalayana_grhyasutra": sbe(*GRIHYA_1),
    "sankhayana_grhyasutra": sbe(*GRIHYA_1),
    "khadira_grhyasutra": sbe(*GRIHYA_1),
    "paraskara_grhyasutra": sbe(*GRIHYA_1),
    "gobhila_grhyasutra": sbe(*GRIHYA_2),
    "hiranyakesin_grhyasutra": sbe(*GRIHYA_2),
    "apastamba_grhyasutra": sbe(*GRIHYA_2),
    "apastamba_dharmasutra": sbe(*LAWS_1),
    "gautama_dharmasutra": sbe(*LAWS_1),
    "vasistha_dharmasutra": sbe(*LAWS_2),
    "baudhayana_dharmasutra": sbe(*LAWS_2),
    "mahabharata_ganguli": english("Kisari Mohan Ganguli", "The Mahabharata of Krishna-Dwaipayana Vyasa", "1883–96",
                                   [link(f"Project Gutenberg vol. {i}", f"{GUT}{n}") for i, n in enumerate((15474, 15475, 15476, 15477), 1)]),
    "harivamsa_dutt": english("Manmatha Nath Dutt", "A Prose English Translation of Harivamsha", "1897", [link("Project Gutenberg", f"{GUT}61937")]),
    "ramayana_dutt": english("Manmatha Nath Dutt", "The Ramayana", "1891–94",
                             [link(f"Project Gutenberg vol. {i}", f"{GUT}{n}") for i, n in enumerate((57265, 57826, 60188, 62496), 1)]),
    "isha_upanishad": english("Sri Aurobindo", "Isha Upanishad, Complete Works of Sri Aurobindo vol. 17", None,
                              [link("Sri Aurobindo Ashram", ASHRAM + "-17_Isha Upanishad/-01_Isha Upanishad.htm")], UPANISHADS_ORG),
    "kena_upanishad": aurobindo("-01_Kena Upanishad.htm"),
    "katha_upanishad": aurobindo("-17_Katha Upanishad.htm"),
    "mundaka_upanishad": aurobindo("-19_Mundaka Upanishad.htm"),
    "prasna_upanishad": aurobindo("-22_The Prusna Upanishad of the Athurvaveda.htm"),
    "mandukya_upanishad": aurobindo("-23_The Mandoukya Upanishad.htm"),
    "aitareya_upanishad": aurobindo("-24_The Aitereya Upanishad.htm"),
    "taittiriya_upanishad": aurobindo("-25_Taittiriya Upanishad.htm"),
    "svetasvatara_upanishad": aurobindo("-26_Svetasvatara Upanishad.htm", "Sri Aurobindo's text matches 58 of 111 verses; the translator of the other 53 could not be identified."),
    "chandogya_upanishad": english(
        "Swami Nikhilananda; opening verses by Sri Aurobindo", "The Upanishads, Harper & Brothers / Ramakrishna-Vivekananda Center", "1949–59",
        [link("Nikhilananda, archive.org", "https://archive.org/details/upanishads.thevolume4swaminikhilanandar.k.mutt_202003_240_Z"),
         link("Sri Aurobindo Ashram", ASHRAM + "-18_Kena And Other Upanishads/-27_Chhandogya Upanishad.htm")], UPANISHADS_ORG,
        "Matched verse by verse: 589 of 625 Nikhilananda, 31 Sri Aurobindo, 5 unmatched."),
    "brhadaranyaka_upanishad": english("Swami Madhavananda", "The Bṛhadāraṇyaka Upaniṣad, with the Commentary of Śaṅkarācārya", "1934",
                                       [link("wisdomlib", WL + "the-brihadaranyaka-upanishad"), link("scan, archive.org", "https://archive.org/details/in.ernet.dli.2015.20823")]),
    "kausitaki_upanishad": english("A. G. Krishna Warrier", "Kauṣītaki-Brāhmaṇa Upaniṣad, The Theosophical Publishing House", None,
                                   [link("Upanishad Scripts", "https://sites.google.com/site/upanishadscripts/025-kaushitakibrahmana")]),
    "bhagavata_purana_subbarau": english("S. Subba Rau", "The Srimad Bhagavatam, Tirupati: Sri Venkatesa Printing Works", "1928",
                                         [link("archive.org", "https://archive.org/details/in.ernet.dli.2015.272624")], pramana("in.purana.bhagavata~en-subbarau")),
    "garuda_purana_dutt": english("Manmatha Nath Dutt", "The Garuda Puranam, Calcutta", "1908", [link("wisdomlib", WL + "the-garuda-purana-dutt")],
                                  pramana("in.purana.garuda~en-dutt"), "Dutt translated book 1 only."),
    "markandeya_purana_pargiter": english("F. E. Pargiter", "The Mārkaṇḍeya Purāṇa, Bibliotheca Indica", "1888–1904", [link("wisdomlib", WL + "the-markandeya-purana")],
                                          pramana("in.purana.markandeya~en-pargiter")),
    "matsya_purana_taluqdar": english("A Taluqdar of Oudh", "The Matsya Puranam, Sacred Books of the Hindus 17", "1916–17",
                                      [link("archive.org", "https://archive.org/details/in.ernet.dli.2015.274264")], pramana("in.purana.matsya~en-taluqdar")),
    "visnu_purana_wilson": english("H. H. Wilson", "The Vishńu Puráńa, a System of Hindu Mythology and Tradition", "1840", sacred("vp/index.htm"), pramana("in.purana.visnu~en-wilson")),
    "agni_purana": {"machine": {"by": "Gemini 3.8 Flash", "year": "2026", "via": pramana("in.purana.agni~en-mt")}},
    "skanda_purana": {"machine": {"by": "Gemini 3.8 Flash", "year": "2026", "via": pramana("in.purana.skanda~en-mt")}},
    # `inText`: this English sits in the file's `text` field, so build_library has to move it to the labelled machine layer.
    "jaiminiya_brahmana": {"machine": {"by": "Engine not recorded", "inText": True, "noSource": True,
                                       "note": "Added to this project in March 2026 with no record of how it was made, and it is not Pramāṇa's machine translation. No public source to check it against."}},
}

# Catalog `source` lines that named the wrong translator or hid what the English is.
SOURCE = {
    "manu_smrti": "English: Gaṅgānāth Jhā, with Medhātithi's commentary (wisdomlib)",
    "jaiminiya_brahmana": "Sanskrit: TITUS; machine English of unrecorded origin",
}


def main():
    path = os.path.join(HERE, "translation_sources.json")
    sources = json.load(open(path, encoding="utf-8"))
    sources.update(CREDITS)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)
        f.write("\n")
    path = os.path.join(HERE, "library_catalog.json")
    lines = open(path, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        for text_id, source in SOURCE.items():
            if f'"id": "{text_id}"' in line:
                entry = json.loads(line.strip().rstrip(","))
                entry["source"] = source
                lines[i] = "    " + json.dumps(entry, ensure_ascii=False) + ("," if line.rstrip().endswith(",") else "")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(len(CREDITS), "records written;", len(sources), "in total")


if __name__ == "__main__":
    main()
