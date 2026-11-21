#!/usr/bin/env python3
"""The Qur'an for the comparative shelf: the Arabic beside Pickthall's English.

Arabic: the Tanzil Project's Uthmani text (version 1.1), under Creative Commons Attribution 3.0 on Tanzil's terms:
copied verbatim, never changed, with Tanzil named and linked, which the reader's credit does. The text is therefore
written exactly as downloaded, including the basmala Tanzil keeps at the head of each sūra's first āya.
English: Muhammad Marmaduke Pickthall, The Meaning of the Glorious Koran (1930): public domain in the United States
since 2026 and wherever copyright runs seventy years from the author's death (1936). Taken from Tanzil's edition.
Both are numbered āya by āya the same way (6,236 āyāt); the script stops if they are not.

Writes public/data/quran/quran.json and adds it to library_catalog.json and translation_sources.json. Rerunnable;
downloads are cached in cache/tanzil.

Usage: python3 -I scripts/corpus2/quran_tanzil.py
"""
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "tanzil")
OUT = os.path.join(ROOT, "public", "data", "quran")
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

URLS = {
    "uthmani.txt": "https://tanzil.net/pub/download/index.php?marks=true&sajdah=true&rub=false&tatweel=true&quranType=uthmani&outType=txt-2&agree=true",
    "pickthall.txt": "https://tanzil.net/trans/en.pickthall",
    "meta.xml": "https://tanzil.net/res/text/metadata/quran-data.xml",
}
BAND = {"id": "quran", "after": ["christian_east", "new_testament", "old_testament"], "name": "Islam",
        "blurb": "not Indic: the Qur'an, revelation as recitation as the Veda is śruti, heard, in Arabic with Pickthall's English; and Rūmī's Mathnawī in English"}
ORIGINAL = {"name": "Arabic", "lang": "ar", "dir": "rtl", "label": "العربية", "short": "ع"}
CREDIT = {"english": {"by": "Muhammad Marmaduke Pickthall", "work": "The Meaning of the Glorious Koran, New York: Alfred A. Knopf", "year": "1930",
                      "links": [{"label": "Tanzil", "url": "https://tanzil.net/trans/"}],
                      "via": {"label": "Tanzil", "url": "https://tanzil.net/"},
                      "note": "Arabic: Tanzil Quran Text (Uthmani, Version 1.1), Copyright (C) 2007-2026 Tanzil Project, licensed under Creative Commons "
                              "Attribution 3.0. Copied verbatim from tanzil.net, which keeps it verified and up to date: http://tanzil.net/updates/"}}


def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, name)
    if not os.path.exists(f):
        with urllib.request.urlopen(urllib.request.Request(URLS[name], headers={"User-Agent": "rigved-corpus-research/1.0"}), timeout=120) as r:
            open(f, "wb").write(r.read())
        time.sleep(1)
    return open(f, encoding="utf-8").read()


def ayat(raw):
    out = {}
    for ln in raw.splitlines():
        if ln and not ln.startswith("#"):
            s, a, t = ln.split("|", 2)
            out[(int(s), int(a))] = t
    return out


def main():
    ar, en = ayat(fetch("uthmani.txt")), ayat(fetch("pickthall.txt"))
    if "Creative Commons Attribution 3.0" not in fetch("uthmani.txt"):
        raise SystemExit("Tanzil's licence block has changed: read it before importing")
    if list(ar) != list(en) or len(ar) != 6236:
        raise SystemExit("Arabic and English number the āyāt differently")
    suras = {int(m["index"]): m for m in (dict(re.findall(r'(\w+)="([^"]*)"', x)) for x in re.findall(r"<sura [^>]*/>", fetch("meta.xml")))}
    rows = []
    for (s, a), t in ar.items():
        row = {"reference": f"{s}.{a}", "original": t, "text": en[(s, a)].strip()}
        if a == 1:
            m = suras[s]
            row["title"] = f"{m['tname']} ({m['ename']}) · {m['name']} · {m['type']}"
        rows.append(row)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "quran.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    text = {"id": "quran", "file": "quran/quran.json", "name": "The Qur'an", "band": "quran", "levels": ["Sūra", "Āya"], "original": ORIGINAL,
            "date": [610, 632], "source": "Arabic: Tanzil Quran Text (Uthmani 1.1), CC BY 3.0, tanzil.net; English: M. M. Pickthall (1930)"}
    write([BAND], [text], {"quran": CREDIT})
    print(f"quran: {len(suras)} sūras, {len(rows)} āyāt")


if __name__ == "__main__":
    main()
