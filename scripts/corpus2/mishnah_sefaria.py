#!/usr/bin/env python3
"""The Mishnah for the comparative shelf: all sixty-three tractates, Hebrew beside Joshua Kulp's English.

Hebrew: the Romm edition (Vilna, 1913), public domain. English: Mishnah Yomit by Dr. Joshua Kulp (Conservative
Yeshiva), CC BY, the only complete English Mishnah under an open licence. Both come from Sefaria's export
(storage.googleapis.com/sefaria-export) in the same chapter and mishnah numbering, so each mishnah's English sits
beside its own Hebrew; the script stops if a chapter's counts disagree. Pirkei Avot is one of the tractates (Nezikin).
Bikkurim's fourth chapter, a later appendix the Vilna Mishnah leaves out, comes in English only.

Tractates are in the traditional order, each its own text in the library, grouped by the six orders (sedarim).
Writes public/data/mishnah/<id>.json and adds the tractates to library_catalog.json and translation_sources.json.
Rerunnable; downloads are cached in cache/sefaria/mishnah.

Usage: .venv/bin/python -I scripts/corpus2/mishnah_sefaria.py
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "sefaria", "mishnah")
OUT = os.path.join(ROOT, "public", "data", "mishnah")
GCS = "https://storage.googleapis.com/sefaria-export/json/Mishnah"
HE = ("Mishnah, ed. Romm, Vilna 1913", "Public Domain")
EN = ("Mishnah Yomit by Dr. Joshua Kulp", "CC-BY")

# (order, Sefaria's name for each tractate in the traditional order)
ORDERS = [
    ("Zeraim", "Seeds", "blessings and the laws of the land's produce: tithes, gleanings, mixed kinds, the sabbatical year",
     ["Berakhot", "Peah", "Demai", "Kilayim", "Sheviit", "Terumot", "Maasrot", "Maaser Sheni", "Challah", "Orlah", "Bikkurim"]),
    ("Moed", "Appointed Times", "the Sabbath and the festivals: Passover, the Day of Atonement, Tabernacles, the New Year, fasts",
     ["Shabbat", "Eruvin", "Pesachim", "Shekalim", "Yoma", "Sukkah", "Beitzah", "Rosh Hashanah", "Ta'anit", "Megillah", "Moed Katan", "Chagigah"]),
    ("Nashim", "Women", "marriage, divorce, vows and the Nazirite",
     ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin"]),
    ("Nezikin", "Damages", "civil and criminal law, the courts, idolatry, and the Sayings of the Fathers (Pirkei Avot)",
     ["Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", "Makkot", "Shevuot", "Eduyot", "Avodah Zarah", "Pirkei Avot", "Horayot"]),
    ("Kodashim", "Holy Things", "the Temple's sacrifices and service, and its measurements",
     ["Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", "Temurah", "Keritot", "Meilah", "Tamid", "Middot", "Kinnim"]),
    ("Tahorot", "Purities", "ritual purity and impurity",
     ["Kelim", "Oholot", "Negaim", "Parah", "Tahorot", "Mikvaot", "Niddah", "Makhshirin", "Zavim", "Tevul Yom", "Yadayim", "Oktzin"]),
]
# Bikkurim 4 (on the androgynos) is a later appendix: in Kulp, not in the Vilna Mishnah.
ENGLISH_ONLY_CHAPTERS = {"Bikkurim": {4}}

sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

BAND = {"id": "mishnah", "after": ["apocrypha", "old_testament"], "name": "Mishnah",
        "blurb": "not Indic: the oral law of the rabbis, set down about 200 CE — a body of ritual and law handed from teacher to pupil "
                 "as the Vedic sūtras were, with the Sayings of the Fathers. Hebrew with Joshua Kulp's English",
        "groups": [{"id": o.lower(), "name": f"{o} ({en})", "blurb": blurb} for o, en, blurb, _ in ORDERS]}
ORIGINAL = {"name": "Hebrew", "lang": "he", "dir": "rtl", "label": "עברית", "short": "א"}
CREDIT = {"english": {"by": "Joshua Kulp", "work": "Mishnah Yomit, Conservative Yeshiva, Jerusalem", "year": "2007–2019",
                      "links": [{"label": "Conservative Yeshiva", "url": "https://learn.conservativeyeshiva.org/mishnah/"}],
                      "via": {"label": "Sefaria", "url": "https://www.sefaria.org/texts/Mishnah"},
                      "note": "Licence: CC BY (Joshua Kulp, Mishnah Yomit). Hebrew: the Romm edition, Vilna 1913 (public domain), "
                              "in the same numbering."}}
TAG = re.compile(r"</?(?:small|b|i)>")


def fetch(order, tractate, lang, version):
    book = tractate if tractate == "Pirkei Avot" else f"Mishnah {tractate}"
    f = os.path.join(CACHE, f"{book}.{lang}.json")
    if not os.path.exists(f):
        os.makedirs(CACHE, exist_ok=True)
        url = f"{GCS}/Seder {order}/{urllib.parse.quote(book)}/{'Hebrew' if lang == 'he' else 'English'}/{urllib.parse.quote(version)}.json"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rigved-corpus-research/1.0"}), timeout=120) as r:
            data = r.read()
        open(f, "wb").write(data)
        time.sleep(0.5)
    return json.load(open(f, encoding="utf-8"))


def clean(v):
    v = re.sub(r"\s*<br>\s*", "\n", v)
    v = TAG.sub("", v)
    if "<" in v:
        raise SystemExit(f"markup left in mishnah: {v[:120]}")
    return re.sub(r"[ \t]+", " ", v).strip()


def slug(name):
    return "mishnah_" + re.sub(r"[^a-z0-9]+", "_", name.lower().replace("'", "")).strip("_")


def main():
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for order, _, _, tractates in ORDERS:
        for tractate in tractates:
            he, en = fetch(order, tractate, "he", HE[0]), fetch(order, tractate, "en", EN[0])
            for d, (version, licence) in ((he, HE), (en, EN)):
                if d.get("versionTitle") != version or d.get("license") != licence:
                    raise SystemExit(f"{tractate}: expected {version} under {licence}, got {d.get('versionTitle')} under {d.get('license')}")
            extra = ENGLISH_ONLY_CHAPTERS.get(tractate, set())
            hc, ec = he["text"], en["text"]
            if len(ec) != len(hc) + len(extra) or any(len(ec[c - 1]) != len(hc[c - 1]) for c in range(1, len(hc) + 1) if c not in extra):
                raise SystemExit(f"{tractate}: Hebrew and English number the mishnayot differently")
            rows = []
            for c, ech in enumerate(ec, 1):
                hch = hc[c - 1] if c <= len(hc) and c not in extra else [None] * len(ech)
                for m, (h, e) in enumerate(zip(hch, ech), 1):
                    if not e.strip():
                        raise SystemExit(f"{tractate} {c}.{m}: empty English")
                    rows.append({"reference": f"{c}.{m}", **({"original": clean(h)} if h else {}), "text": clean(e)})
            name = tractate if tractate == "Pirkei Avot" else f"Mishnah {tractate}"
            tid = slug(tractate)
            with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
            texts.append({"id": tid, "file": f"mishnah/{tid}.json", "name": name, "band": "mishnah", "group": order.lower(),
                          "levels": ["Chapter", "Mishnah"], "original": ORIGINAL, "date": [190, 220],
                          "source": "Hebrew: Mishnah, ed. Romm, Vilna 1913; English: Joshua Kulp, Mishnah Yomit (CC BY), from Sefaria"})
            records[tid] = CREDIT
            print(f"{tid:28s} {len(ec):3d} chapters {len(rows):5d} mishnayot")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
