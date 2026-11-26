#!/usr/bin/env python3
"""The Babylonian Talmud for the comparative shelf: all thirty-seven tractates, Aramaic beside the William Davidson
Edition's English.

Both are the William Davidson Edition (Koren Noé Talmud, with Rabbi Adin Even-Israel Steinsaltz's commentary woven
into the translation), released by Sefaria under CC BY-NC; the library is free and shows the text unchanged, which
that licence allows. Taken from Sefaria's export (storage.googleapis.com/sefaria-export), where Aramaic and English
are cut into the same segments, page side (amud) by page side, so each segment's English sits beside its own
Aramaic. The one difference allowed: the Aramaic closes a chapter with its hadran (“we will return to you…”), which
has no English (an empty segment, or one past the English's last), and stands as Aramaic alone; any other
difference stops the script.

The edition sets the literal translation in bold and Steinsaltz's explanation in roman; the reader shows plain text,
so the bold is dropped (the credit says so). References are daf and side, then segment: 2a.1, 2a.2, … 64a.15.
Tractates are in the traditional order, grouped by the six orders. Writes public/data/talmud/<id>.json and adds the
tractates to library_catalog.json and translation_sources.json. Rerunnable; downloads are cached in
cache/sefaria/talmud.

Usage: .venv/bin/python -I scripts/corpus2/talmud_sefaria.py
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
CACHE = os.path.join(ROOT, "cache", "sefaria", "talmud")
OUT = os.path.join(ROOT, "public", "data", "talmud")
GCS = "https://storage.googleapis.com/sefaria-export/json/Talmud/Bavli"
LISTING = "https://storage.googleapis.com/storage/v1/b/sefaria-export/o"
AR = ("William Davidson Edition - Aramaic", "CC-BY-NC")
EN = ("William Davidson Edition - English", "CC-BY-NC")

ORDERS = [
    ("Zeraim", "Seeds", ["Berakhot"]),
    ("Moed", "Appointed Times", ["Shabbat", "Eruvin", "Pesachim", "Yoma", "Sukkah", "Beitzah", "Rosh Hashanah", "Taanit", "Megillah",
                                 "Moed Katan", "Chagigah"]),
    ("Nashim", "Women", ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin"]),
    ("Nezikin", "Damages", ["Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", "Makkot", "Shevuot", "Avodah Zarah", "Horayot"]),
    ("Kodashim", "Holy Things", ["Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", "Temurah", "Keritot", "Meilah", "Tamid"]),
    ("Tahorot", "Purities", ["Niddah"]),
]

sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

BAND = {"id": "talmud", "after": ["mishnah", "apocrypha"], "name": "Talmud",
        "blurb": "not Indic: the Babylonian Talmud, the rabbis' debate on the Mishnah, gathered over three centuries to about 500 CE — "
                 "argument as scripture, as the Brāhmaṇas argue the meaning of the rite. Aramaic with the William Davidson English",
        "groups": [{"id": o.lower(), "name": f"{o} ({en})"} for o, en, _ in ORDERS]}
ORIGINAL = {"name": "Aramaic", "lang": "arc", "dir": "rtl", "label": "ארמית", "short": "א"}
CREDIT = {"english": {"by": "Rabbi Adin Even-Israel Steinsaltz, Koren Publishers", "work": "The William Davidson Talmud (Koren Noé Talmud)",
                      "year": "2012–2019",
                      "links": [{"label": "Koren", "url": "https://korenpub.com/collections/the-noe-edition-koren-talmud-bavli-1"}],
                      "via": {"label": "Sefaria", "url": "https://www.sefaria.org/texts/Talmud"},
                      "note": "Licence: CC BY-NC (William Davidson Edition, Sefaria). The edition sets the literal translation in bold and "
                              "Steinsaltz's explanation in roman; here both are plain. Aramaic: the same edition, segment by segment."}}
TAGS = re.compile(r"</?(?:b|i|strong|big|small|span|em)(?:\s[^>]*)?>")
# A footnote goes with its marker, whole, before the tags around the text are taken off.
NOTES = re.compile(r'<sup class="footnote-marker">[^<]*</sup>\s*<i class="footnote">(?:[^<]|<(?!/?i[\s>])[^>]*>|<i>[^<]*</i>)*</i>')
HADRAN = "הדרן"


def fetch(order, tractate, lang, version):
    f = os.path.join(CACHE, f"{tractate}.{lang}.json")
    if not os.path.exists(f):
        os.makedirs(CACHE, exist_ok=True)
        path = f"Seder {order}/{tractate}/{'Hebrew' if lang == 'ar' else 'English'}/{version}.json"
        with urllib.request.urlopen(urllib.request.Request(f"{GCS}/{urllib.parse.quote(path)}",
                                                           headers={"User-Agent": "rigved-corpus-research/1.0"}), timeout=300) as r:
            data = r.read()
        json.loads(data)  # never cache a broken download
        open(f, "wb").write(data)
        time.sleep(0.5)
    return json.load(open(f, encoding="utf-8"))


def listed():
    """Sefaria's Bavli tractates, to check ORDERS names every one."""
    out = set()
    for order, _, _ in ORDERS:
        q = urllib.parse.urlencode({"prefix": f"json/Talmud/Bavli/Seder {order}/", "delimiter": "/"})
        with urllib.request.urlopen(f"{LISTING}?{q}", timeout=60) as r:
            out |= {p.rstrip("/").split("/")[-1] for p in json.load(r).get("prefixes", [])}
    return out


def clean(v):
    v = NOTES.sub("", v)
    v = re.sub(r"\s*(?:<br\s*/?>\s*)+", "\n", v)
    v = TAGS.sub("", v)
    if "<" in v:
        raise SystemExit(f"markup left in segment: {v[:160]}")
    v = "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in v.split("\n"))
    return re.sub(r"\n{2,}", "\n", v).strip()


def amud(i):
    return f"{i // 2 + 1}{'ab'[i % 2]}"


def slug(name):
    return "bavli_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    want = {t for _, _, ts in ORDERS for t in ts}
    have = listed()
    if want != have:
        raise SystemExit(f"tractates: missing here {sorted(have - want)}, not at Sefaria {sorted(want - have)}")
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for order, _, tractates in ORDERS:
        for tractate in tractates:
            ar, en = fetch(order, tractate, "ar", AR[0]), fetch(order, tractate, "en", EN[0])
            for d, (version, licence) in ((ar, AR), (en, EN)):
                if d.get("versionTitle") != version or d.get("license") != licence:
                    raise SystemExit(f"{tractate}: expected {version} under {licence}, got {d.get('versionTitle')} under {d.get('license')}")
            at, et = ar["text"], en["text"]
            if len(at) < len(et):
                raise SystemExit(f"{tractate}: English runs past the Aramaic")
            rows, sides = [], 0
            for i, a in enumerate(at):
                e = et[i] if i < len(et) else []
                if not a and not e:
                    continue
                extra = a[len(e):]
                if len(a) < len(e) or any(HADRAN not in s for s in extra):
                    raise SystemExit(f"{tractate} {amud(i)}: {len(a)} Aramaic segments, {len(e)} English")
                sides += 1
                for n, s in enumerate(a, 1):
                    row = {"reference": f"{amud(i)}.{n}", "original": clean(s)}
                    if n <= len(e) and e[n - 1].strip():
                        row["text"] = clean(e[n - 1])
                    elif HADRAN not in s:
                        raise SystemExit(f"{tractate} {amud(i)}.{n}: no English, and the Aramaic is not a hadran")
                    rows.append(row)
            tid = slug(tractate)
            with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
            texts.append({"id": tid, "file": f"talmud/{tid}.json", "name": f"Talmud Bavli, {tractate}", "band": "talmud",
                          "group": order.lower(), "levels": ["Daf", "Segment"], "original": ORIGINAL, "date": [200, 500],
                          "source": "Aramaic and English: The William Davidson Talmud (Koren, Steinsaltz), CC BY-NC, from Sefaria"})
            records[tid] = CREDIT
            print(f"{tid:26s} {sides:4d} sides {len(rows):6d} segments", flush=True)
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
