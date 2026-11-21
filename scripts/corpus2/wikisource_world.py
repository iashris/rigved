#!/usr/bin/env python3
"""The Ṛgveda's kin beyond India, in English, from English Wikisource: Homer, Hesiod, the Homeric Hymns, the Poetic
Edda and Gilgamesh.

All public-domain translations (Butler 1898–1900, Evelyn-White 1914, Bellows 1923, R. Campbell Thompson 1928), read
from Wikisource's proofread transcriptions through the MediaWiki API (action=parse), one request at a time. English
only: the Greek, Old Norse and Akkadian are not imported. Each Wikisource subpage is a chapter (an Iliad book, an
Eddic poem, a hymn); an entry is one of its paragraphs or stanzas, numbered from 1. The translators' footnotes,
Wikisource's page-number markers and its header boxes are left out.

Writes public/data/world/<id>.json and adds the texts to library_catalog.json and translation_sources.json.
Rerunnable; API responses are cached in cache/wikisource.
Usage: .venv/bin/python -I scripts/corpus2/wikisource_world.py
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "wikisource")
OUT = os.path.join(ROOT, "public", "data", "world")
API = "https://en.wikisource.org/w/api.php"
UA = "rigved-corpus-research/1.0 (https://github.com/iashris/rigved)"
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
          "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX", "XXXI", "XXXII", "XXXIII"]
HYMNS = ["I (To Dionysus)", "II (To Demeter)", "III (To Apollo)", "IV (To Hermes)", "V (To Aphrodite)", "VI (To Aphrodite)", "VII (To Dionysus)",
         "VIII (To Ares)", "IX (To Artemis)", "X (To Aphrodite)", "XI (To Athena)", "XII (To Hera)", "XIII (To Demeter)", "XIV (To the Mother of the Gods)",
         "XV (To Heracles)", "XVI (To Asclepius)", "XVII (To the Dioscuri)", "XVIII (To Hermes)", "XIX (To Pan)", "XX (To Hephaestus)", "XXI (To Apollo)",
         "XXII (To Poseidon)", "XXIII (To Zeus)", "XXIV (To Hestia)", "XXV (To the Muses and Apollo)", "XXVI (To Dionysus)", "XXVII (To Artemis)",
         "XXVIII (To Athena)", "XXIX (To Hestia)", "XXX (To Earth)", "XXXI (To Helios)", "XXXII (To Selene)", "XXXIII (To the Dioscuri)"]
# Bellows's order: the mythological poems, then the hero poems.
EDDA = ["Voluspo", "Hovamol", "Vafthruthnismol", "Grimnismol", "Skirnismol", "Harbarthsljoth", "Hymiskvitha", "Lokasenna", "Thrymskvitha", "Alvissmol",
        "Baldrs Draumar", "Rigsthula", "Hyndluljoth", "Svipdagsmol", "Völundarkvitha", "Helgakvitha Hjorvarthssonar", "Helgakvitha Hundingsbana I",
        "Helgakvitha Hundingsbana II", "Fra Dautha Sinfjotla", "Gripisspo", "Reginsmol", "Fafnismol", "Sigrdrifumol", "Brot af Sigurtharkvithu",
        "Guthrunarkvitha I", "Sigurtharkvitha en Skamma", "Helreith Brynhildar", "Drap Niflunga", "Guthrunarkvitha II, en Forna", "Guthrunarkvitha III",
        "Oddrunargratr", "Atlakvitha en Grönlenzka", "Atlamol en Grönlenzku", "Guthrunarhvot", "Hamthesmol"]

HES = "Hesiod, the Homeric Hymns and Homerica"
WORKS = [
    {"id": "iliad_butler", "name": "Homer, The Iliad", "group": "greek", "levels": ["Book", "Paragraph"],
     "pages": [(f"The Iliad (Butler)/Book {r}", f"Book {r}") for r in ROMANS[:24]],
     "by": "Samuel Butler", "work": "The Iliad of Homer, Rendered into English Prose, London: Longmans, Green", "year": "1898", "home": "The Iliad (Butler)"},
    {"id": "odyssey_butler", "name": "Homer, The Odyssey", "group": "greek", "levels": ["Book", "Paragraph"],
     "pages": [(f"The Odyssey (Butler)/Book {r}", f"Book {r}") for r in ROMANS[:24]],
     "by": "Samuel Butler", "work": "The Odyssey, Rendered into English Prose, London: Longmans, Green", "year": "1900", "home": "The Odyssey (Butler)"},
    {"id": "hesiod_evelynwhite", "name": "Hesiod: Theogony, Works and Days, Shield", "group": "greek", "levels": ["Poem", "Paragraph"],
     "pages": [(f"{HES}/The Theogony", "Theogony"), (f"{HES}/Works and Days", "Works and Days"), (f"{HES}/The Shield of Heracles", "The Shield of Heracles")],
     "by": "Hugh G. Evelyn-White", "work": "Hesiod, the Homeric Hymns and Homerica, Loeb Classical Library 57, London: Heinemann", "year": "1914", "home": HES},
    {"id": "homeric_hymns_evelynwhite", "name": "The Homeric Hymns", "group": "greek", "levels": ["Hymn", "Paragraph"],
     "pages": [(f"{HES}/Hymn {h}", f"Hymn {h}") for h in HYMNS],
     "by": "Hugh G. Evelyn-White", "work": "Hesiod, the Homeric Hymns and Homerica, Loeb Classical Library 57, London: Heinemann", "year": "1914", "home": HES},
    {"id": "poetic_edda_bellows", "name": "The Poetic Edda", "group": "norse", "levels": ["Poem", "Stanza"], "verseLines": True,
     "pages": [(f"The Poetic Edda (tr. Bellows)/{p}", p) for p in EDDA],
     "by": "Henry Adams Bellows", "work": "The Poetic Edda, New York: American-Scandinavian Foundation", "year": "1923", "home": "The Poetic Edda (tr. Bellows)"},
]
BAND = {"id": "kin", "after": ["avesta"], "name": "Indo-European kin",
        "blurb": "not Indic: the Ṛgveda's cousins in Greece and the North — Zeus the sky-father beside Dyauṣ Pitṛ, Thor's hammer beside Indra's vajra. In English",
        "groups": [{"id": "greek", "name": "Greek", "blurb": "Homer, Hesiod and the Homeric Hymns"},
                   {"id": "norse", "name": "Norse", "blurb": "the Poetic Edda"}]}


# The Greek, from the Perseus Digital Library's canonical-greekLit (CC BY-SA 4.0), line by line: Homer from Monro and
# Allen's Oxford text, Hesiod and the Hymns from Evelyn-White's Loeb. Keyed chapter.line, one chapter per English chapter.
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data"
GREEK_ORIGINAL = {"name": "Greek", "lang": "grc", "label": "Ἑλληνικά", "short": "Ἑλ"}
GREEK = {
    "iliad_butler": ("iliad", "Homer, The Iliad", ["Book", "Line"], [("tlg0012.tlg001", None)]),
    "odyssey_butler": ("odyssey", "Homer, The Odyssey", ["Book", "Line"], [("tlg0012.tlg002", None)]),
    "hesiod_evelynwhite": ("hesiod", "Hesiod: Theogony, Works and Days, Shield", ["Poem", "Line"],
                           [("tlg0020.tlg001", 1), ("tlg0020.tlg002", 2), ("tlg0020.tlg003", 3)]),
    "homeric_hymns_evelynwhite": ("homeric_hymns", "The Homeric Hymns", ["Hymn", "Line"], [(f"tlg0013.tlg{n:03d}", n) for n in range(1, 34)]),
}


def perseus(urn):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"{urn}.perseus-grc2.xml")
    if not os.path.exists(f):
        author, work = urn.split(".")
        with urllib.request.urlopen(urllib.request.Request(f"{PERSEUS}/{author}/{work}/{urn}.perseus-grc2.xml", headers={"User-Agent": UA}), timeout=90) as r:
            open(f, "wb").write(r.read())
        time.sleep(1)
    return open(f, encoding="utf-8").read()


def greek_rows(files):
    """[(urn, chapter or None)]: None takes the chapter from the edition's own book divisions (Homer)."""
    import xml.etree.ElementTree as ET
    tei = "{http://www.tei-c.org/ns/1.0}"
    rows = []
    for urn, chapter in files:
        root = ET.fromstring(perseus(urn))
        if "CC BY-SA" not in perseus(urn) and "by-sa" not in perseus(urn):
            raise SystemExit(f"{urn}: licence is not CC BY-SA; read it before importing")
        body = root.find(f".//{tei}body")
        books = [d for d in body.iter(f"{tei}div") if d.get("subtype", "").lower() == "book"] if chapter is None else [body]
        for b in books:
            ch = int(b.get("n")) if chapter is None else chapter
            for ln in b.iter(f"{tei}l"):
                text = re.sub(r"\s+", " ", "".join(ln.itertext())).strip()
                n = ln.get("n")
                if text and n and re.fullmatch(r"\d+", n):
                    rows.append({"reference": f"{ch}.{n}", "original": text})
    seen = set()
    rows = [r for r in rows if not (r["reference"] in seen or seen.add(r["reference"]))]
    return rows


def parse(title):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, hashlib.sha1(title.encode()).hexdigest() + ".json")
    if not os.path.exists(f):
        q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text", "format": "json", "formatversion": "2", "redirects": "1"})
        with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA}), timeout=90) as r:
            data = json.load(r)
        if "error" in data:
            raise SystemExit(f"{title}: {data['error'].get('info')}")
        json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(1)
    return json.load(open(f, encoding="utf-8"))["parse"]["text"]


DROP = ["sup.reference", "ol.references", "div.references", ".mw-references-wrap", ".ws-noexport", ".wst-header", "table.headertemplate",
        "#headertemplate", ".pagenum", ".ws-pagenum", ".mw-editsection", ".noprint", "style", "span.wst-linenum", ".wst-linenum", "span.linenumber"]


def is_stanza(el):
    return el.name == "div" and "ws-poem-stanza" in (el.get("class") or [])


def paragraphs(html, verse=False):
    """Prose paragraphs, and the stanzas of Wikisource's poem markup (div.ws-poem-stanza, one line per ws-poem-line,
    the half-line break kept as a wide space). Line breaks survive only in verse; in prose they are soft wraps."""
    soup = BeautifulSoup(html, "html.parser")
    for sel in DROP:
        for el in soup.select(sel):
            el.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for cut in soup.select(".wst-cesura"):
        cut.replace_with(" ")
    out = []
    for p in soup.find_all(lambda el: el.name in ("p", "dd") or is_stanza(el)):
        if p.find_parent(lambda el: el.name in ("p", "dd") or is_stanza(el)):
            continue
        t = p.get_text()
        t = re.sub(r"[ \t ]+", " ", t)
        t = "\n".join(ln.strip() for ln in t.split("\n")).strip()
        t = re.sub(r"\n{2,}", "\n", t)
        if not (verse or is_stanza(p)):
            t = t.replace("\n", " ")
        if t and not re.fullmatch(r"[\d\s.\[\]*·]+|[IVXL]+\.?", t):  # page numbers, a hymn's bare numeral, rows of asterisks
            out.append(t)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for w in WORKS:
        rows = []
        for ch, (page, label) in enumerate(w["pages"], 1):
            paras = paragraphs(parse(page), w.get("verseLines", False))
            if not paras:
                raise SystemExit(f"{page}: no paragraphs")
            for n, t in enumerate(paras, 1):
                rows.append({"reference": f"{ch}.{n}", "text": t, **({"title": label} if n == 1 else {})})
        with open(os.path.join(OUT, f"{w['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        home = "https://en.wikisource.org/wiki/" + urllib.parse.quote(w["home"].replace(" ", "_"))
        gid = None
        if w["id"] in GREEK:
            # The Greek comes first, as the text; the English is its translation, paired chapter by chapter.
            gid, gname, glevels, files = GREEK[w["id"]]
            grows = greek_rows(files)
            with open(os.path.join(OUT, f"{gid}.json"), "w", encoding="utf-8") as f:
                json.dump(grows, f, ensure_ascii=False, indent=1)
            texts.append({"id": gid, "file": f"world/{gid}.json", "name": gname, "band": "kin", "group": w["group"], "levels": glevels,
                          "original": GREEK_ORIGINAL, "verseLines": True,
                          "source": f"Greek: Perseus Digital Library, canonical-greekLit (CC BY-SA 4.0); English: {w['by']} ({w['year']}), from Wikisource",
                          "pairs": [{"with": w["id"], "mode": "prefix", "label": f"{w['by'].split()[-1]} ({w['year']})"}]})
            print(f"{gid:28s} {len(files):3d} chapters {len(grows):6d} lines of Greek")
        texts.append({"id": w["id"], "file": f"world/{w['id']}.json", "name": f"{w['name']} — {w['by'].split()[-1]}" if gid else w["name"],
                      "band": "kin", "group": w["group"], **({"translationOf": gid} if gid else {}), "levels": w["levels"],
                      **({"verseLines": True} if w.get("verseLines") else {}),
                      "source": f"English: {w['by']} ({w['year']}), from Wikisource"})
        records[w["id"]] = {"english": {"by": w["by"], "work": w["work"], "year": w["year"], "links": [{"label": "Wikisource", "url": home}],
                                        "via": {"label": "Wikisource", "url": home},
                                        "note": "Public domain; the proofread Wikisource transcription, footnotes left out."}}
        print(f"{w['id']:28s} {len(w['pages']):3d} chapters {len(rows):6d} paragraphs")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
