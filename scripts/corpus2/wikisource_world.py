#!/usr/bin/env python3
"""The Ṛgveda's kin beyond India: Homer, Hesiod, the Homeric Hymns, Apollodorus and the Orphic Hymns in Greek with
English beside them, and the Poetic Edda, the Prose Edda, the Völsunga saga and the Ynglinga saga in English.

All public-domain translations (Butler 1898–1900, Evelyn-White 1914, Frazer 1921, Taylor 1792, Bellows 1923, Brodeur
1916, Morris and Magnússon 1888, Laing 1844). Most are read from Wikisource's proofread transcriptions through the
MediaWiki API (action=parse), one request at a time. Each Wikisource subpage is a chapter (an Iliad book, an Eddic
poem, a hymn); an entry is one of its paragraphs or stanzas, numbered from 1. The Prose Edda and the Ynglinga saga
come as one page per part, and are cut into the translators' numbered chapters. The translators' footnotes,
Wikisource's page-number markers and its header boxes are left out.

The Greek comes first, as the text, line by line, with the English as its translation: Homer, Hesiod and the Hymns
from the Perseus Digital Library's canonical-greekLit (CC BY-SA 4.0). Apollodorus's Library (with the Epitome, as book
E) is Perseus's too, Frazer's Loeb Greek and his English both, so the two are paired section by section; his notes are
left out. The Orphic Hymns' Greek is Abel's 1885 text as Greek Wikisource transcribes it (CC BY-SA; its pages are not
yet marked proofread, so every line is checked against Abel's own line numbers and for stray characters before it is
taken; accents are not checked, and about a dozen words keep a slip, such as τρυφερον); Taylor's 1792 English is J. B.
Hare's sacred-texts.com transcription, read from a GitHub mirror pinned to one commit, without Taylor's notes. Taylor
follows the old editions in running the hymn to Hecate on at the end of the address to Musaeus (his lines 55–64), and
so numbers every later hymn one lower than Abel; here his English takes Abel's numbers, the Greek's.

Writes public/data/world/<id>.json and adds the texts to library_catalog.json and translation_sources.json
(--no-catalog skips that). Rerunnable; API responses and the Greek are cached in cache/wikisource.
Usage: .venv/bin/python -I scripts/corpus2/wikisource_world.py [--no-catalog]
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "cache", "wikisource")
OUT = os.path.join(ROOT, "public", "data", "world")
API = "https://en.wikisource.org/w/api.php"
EL_API = "https://el.wikisource.org/w/api.php"
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
PROSE_EDDA = "The Prose Edda (1916 translation by Arthur Gilchrist Brodeur)"
PERSEUS_HOME = "https://scaife.perseus.org/library/urn:cts:greekLit:"
# Taylor's hymns, from a GitHub mirror of sacred-texts.com (sacred-texts itself turns scripts away), pinned to one commit.
TAYLOR = "https://raw.githubusercontent.com/jonnyg23/mahabrain/b00aa504cf9a7fb368a040b97ebe9cafca950489/sacred_obsidian_vault/cla/hoo"
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
    {"id": "apollodorus_frazer", "name": "Apollodorus, The Library", "group": "greek", "levels": ["Book", "Chapter", "Section"],
     "rows": lambda: tei_rows(APOLLODORUS, "perseus-eng2"),
     "by": "Sir James George Frazer", "work": "Apollodorus, The Library, Loeb Classical Library 121–122, London: Heinemann", "year": "1921",
     "from": "the Perseus Digital Library", "links": [{"label": "Perseus", "url": f"{PERSEUS_HOME}tlg0548.tlg001.perseus-eng2/"},
                                         {"label": "Perseus (Epitome)", "url": f"{PERSEUS_HOME}tlg0548.tlg002.perseus-eng2/"}],
     "note": "Public domain; the Perseus Digital Library's text (CC BY-SA 4.0), Frazer's notes left out."},
    {"id": "orphic_hymns_taylor", "name": "The Orphic Hymns", "group": "greek", "levels": ["Hymn", "Paragraph"], "verseLines": True,
     "rows": lambda: taylor_rows(),
     "by": "Thomas Taylor", "work": "The Hymns of Orpheus, London: printed for the author", "year": "1792", "from": "sacred-texts.com",
     "links": [{"label": "sacred-texts.com", "url": "https://sacred-texts.com/cla/hoo/index.htm"}],
     "via": {"label": "GitHub mirror", "url": "https://github.com/jonnyg23/mahabrain/tree/b00aa504cf9a7fb368a040b97ebe9cafca950489/sacred_obsidian_vault/cla/hoo"},
     "note": "Public domain; J. B. Hare's proofread sacred-texts.com transcription, Taylor's notes left out. Taylor's hymn to Musaeus runs on into "
             "the hymn to Hecate (his lines 55–64), which stands here as hymn 1, and his later hymns take the Greek's numbers, one above his own."},
    {"id": "poetic_edda_bellows", "name": "The Poetic Edda", "group": "norse", "levels": ["Poem", "Stanza"], "verseLines": True,
     "pages": [(f"The Poetic Edda (tr. Bellows)/{p}", p) for p in EDDA],
     "by": "Henry Adams Bellows", "work": "The Poetic Edda, New York: American-Scandinavian Foundation", "year": "1923", "home": "The Poetic Edda (tr. Bellows)"},
    {"id": "prose_edda_brodeur", "name": "The Prose Edda", "group": "norse", "levels": ["Part", "Chapter", "Paragraph"], "verseLines": True,
     "rows": lambda: chapter_rows([(f"{PROSE_EDDA}/{p}", p) for p in ("Prologue", "Gylfaginning", "Skáldskaparmál")], bold_chapters),
     "by": "Arthur Gilchrist Brodeur", "work": "The Prose Edda by Snorri Sturluson, Scandinavian Classics 5, New York: American-Scandinavian Foundation",
     "year": "1916", "home": PROSE_EDDA},
    {"id": "volsunga_saga_morris", "name": "The Völsunga Saga", "group": "norse", "levels": ["Chapter", "Paragraph"], "verseLines": True,
     "rows": lambda: volsunga_rows(),
     "by": "William Morris and Eiríkr Magnússon", "work": "Völsunga Saga: The Story of the Volsungs and Niblungs, ed. H. Halliday Sparling, "
     "The Camelot Series, London: Walter Scott", "year": "1888", "home": "Völsunga Saga"},
    {"id": "ynglinga_saga_laing", "name": "The Ynglinga Saga", "group": "norse", "levels": ["Chapter", "Paragraph"], "verseLines": True,
     "rows": lambda: chapter_rows([("Heimskringla/Ynglinga Saga", "Ynglinga Saga")], heading_chapters),
     "by": "Samuel Laing", "work": "The Heimskringla; or, Chronicle of the Kings of Norway, vol. 1, London: Longman, Brown, Green, and Longmans",
     "year": "1844", "home": "Heimskringla/Ynglinga Saga"},
]
BAND = {"id": "kin", "after": ["avesta"], "name": "Indo-European kin",
        "blurb": "not Indic: the Ṛgveda's cousins in Greece and the North — Zeus the sky-father beside Dyauṣ Pitṛ, Thor's hammer beside Indra's vajra. The Greek in the original with English, the Norse in English",
        "groups": [{"id": "greek", "name": "Greek", "blurb": "Homer, Hesiod, the Homeric and Orphic Hymns, and Apollodorus's handbook of the myths"},
                   {"id": "norse", "name": "Norse", "blurb": "the Poetic and Prose Eddas, the Völsunga saga, and the Ynglinga saga of Odin's line"}]}


# The Greek, from the Perseus Digital Library's canonical-greekLit (CC BY-SA 4.0), line by line: Homer from Monro and
# Allen's Oxford text, Hesiod and the Hymns from Evelyn-White's Loeb. Keyed chapter.line, one chapter per English chapter.
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data"
PERSEUS_SOURCE = "Perseus Digital Library, canonical-greekLit (CC BY-SA 4.0)"
GREEK_ORIGINAL = {"name": "Greek", "lang": "grc", "label": "Ἑλληνικά", "short": "Ἑλ"}
GREEK = {
    "iliad_butler": ("iliad", "Homer, The Iliad", ["Book", "Line"], [("tlg0012.tlg001", None)]),
    "odyssey_butler": ("odyssey", "Homer, The Odyssey", ["Book", "Line"], [("tlg0012.tlg002", None)]),
    "hesiod_evelynwhite": ("hesiod", "Hesiod: Theogony, Works and Days, Shield", ["Poem", "Line"],
                           [("tlg0020.tlg001", 1), ("tlg0020.tlg002", 2), ("tlg0020.tlg003", 3)]),
    "homeric_hymns_evelynwhite": ("homeric_hymns", "The Homeric Hymns", ["Hymn", "Line"], [(f"tlg0013.tlg{n:03d}", n) for n in range(1, 34)]),
    # Prose, keyed book.chapter.section as Frazer's English is, so the two pair section by section.
    "apollodorus_frazer": ("apollodorus", "Apollodorus, The Library", ["Book", "Chapter", "Section"], lambda: tei_rows(APOLLODORUS, "perseus-grc2"),
                           {"mode": "aligned", "verseLines": False}),
    # Abel's text from Greek Wikisource, keyed hymn.line with Abel's numbers (0, the address to Musaeus, to 87).
    "orphic_hymns_taylor": ("orphic_hymns", "The Orphic Hymns", ["Hymn", "Line"], lambda: orphic_greek_rows(),
                            {"source": "Greek: Eugen Abel's Orphica (1885), from Greek Wikisource (CC BY-SA 4.0)"}),
}


def perseus(urn, edition="perseus-grc2"):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"{urn}.{edition}.xml")
    if not os.path.exists(f):
        author, work = urn.split(".")
        open(f, "wb").write(fetch(f"{PERSEUS}/{author}/{work}/{urn}.{edition}.xml"))
    return open(f, encoding="utf-8").read()


def greek_rows(files):
    """[(urn, chapter or None)]: None takes the chapter from the edition's own book divisions (Homer)."""
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


# Apollodorus: the Library proper (three books) and the Epitome of its lost end, which Perseus keeps as a second work;
# the Epitome is book E here.
APOLLODORUS = [("tlg0548.tlg001", None), ("tlg0548.tlg002", "E")]
TEI = "{http://www.tei-c.org/ns/1.0}"
# Left out with what they hold: notes (and the Greek's commented-out ones), citations (the Greek's are mangled
# beta code), page and volume markers.
TEI_SKIP = {"note", "NOTE", "bibl", "pb", "milestone", "head"}


def tei_text(el):
    """A section's running text. Kept: the editor's supplements in ⟨ ⟩, the words he would delete in [ ], a lacuna as
    …, verse quoted in prose with its lines parted by /. A skipped element's tail (the words after a note) stays."""
    out = []

    def walk(e, first_l):
        tag = e.tag.split("}")[-1] if isinstance(e.tag, str) else None
        if tag is None:  # a comment
            pass
        elif tag in TEI_SKIP:
            pass
        elif tag == "gap":
            out.append(" … ")
        else:
            if tag == "l" and not first_l[0]:
                out.append(" / ")
            if tag == "l":
                first_l[0] = False
            out.append({"add": "⟨", "del": "["}.get(tag, ""))
            out.append(e.text or "")
            inner = [True] if tag in ("quote", "cit") else first_l
            for c in e:
                walk(c, inner)
            out.append({"add": "⟩", "del": "]"}.get(tag, ""))
        out.append(e.tail or "")

    first = [True]
    out.append(el.text or "")
    for c in el:
        walk(c, first)
    t = re.sub(r"\s+", " ", "".join(out)).strip()
    t = re.sub(r"(?<=[Ͱ-῿])gt\.", ".", t)  # a stray, half-escaped “&gt;” in the Epitome's Greek (6.15c)
    t = re.sub(r"\s+([,.;:·”)>⟩\]])", r"\1", t)
    return re.sub(r"([“(<⟨\[])\s+", r"\1", t)


def tei_rows(works, edition):
    """book.chapter.section rows from Perseus TEI, `original` for the Greek and `text` for a translation."""
    rows = []
    field = "original" if edition.endswith("grc2") else "text"
    for urn, book in works:
        xml = perseus(urn, edition)
        if "creativecommons.org/licenses/by-sa/" not in xml:
            raise SystemExit(f"{urn}.{edition}: licence is not CC BY-SA; read it before importing")
        body = ET.fromstring(xml).find(f".//{TEI}body")

        def walk(el, path):
            for d in el.findall(f"{TEI}div"):
                st = d.get("subtype")
                if st == "section":
                    text = tei_text(d)
                    if text:
                        rows.append({"reference": ".".join(path + [d.get("n")]), field: text})
                elif st in ("book", "chapter"):
                    walk(d, path + [d.get("n")])
                else:
                    walk(d, path)

        walk(body, [book] if book else [])
    books = set()
    for r in rows:
        b = r["reference"].split(".")[0]
        if b not in books:
            books.add(b)
            r["title"] = "Epitome" if b == "E" else f"Book {ROMANS[int(b) - 1]}"
    return rows


_last = [0.0]


def fetch(url):
    """One request at a time, 2 s apart. Wikisource answers a busy client with 429 or an HTML error page in place of
    JSON: wait it out (30 s, then longer) rather than retry at once."""
    for attempt in range(6):
        time.sleep(max(0.0, _last[0] + 2 - time.time()))
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
                body = r.read()
            if "/w/api.php" not in url:
                return body
            data = json.loads(body)
            if data.get("error", {}).get("code") in ("ratelimited", "maxlag"):
                raise urllib.error.URLError(data["error"]["code"])
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                raise SystemExit(f"{url}: 404")
            print(f"  {type(e).__name__} {getattr(e, 'code', getattr(e, 'reason', ''))}; waiting {30 * (attempt + 1)} s", flush=True)
            time.sleep(30 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}")


def parse(title, api=API):
    os.makedirs(CACHE, exist_ok=True)
    key = title if api == API else f"{api} {title}"  # English Wikisource keeps its old cache names
    f = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest() + ".json")
    if not os.path.exists(f):
        q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text", "format": "json", "formatversion": "2", "redirects": "1"})
        data = fetch(f"{api}?{q}")
        if "error" in data:
            raise SystemExit(f"{title}: {data['error'].get('info')}")
        json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False)
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


# ---------------------------------------------------------------- the Norse prose: chapters inside a page

def roman(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    n = [v[c] for c in s]
    return sum(-a if i + 1 < len(n) and a < n[i + 1] else a for i, a in enumerate(n))


def to_roman(n):
    out = ""
    for v, s in ((100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out, n = out + s, n - v
    return out


def pieces(html):
    """Like paragraphs(), for the texts added later, and telling verse from prose by its markup: a stanza is a
    ws-poem-stanza, a <p> inside div.poem (one line per <br>), or a top-level <dl> (one line per <dd>, a nested <dd>
    a line of its own). Prose loses its soft line breaks. Each piece is (element, text). Only proofread or validated
    Wikisource pages are taken."""
    quality = set(re.findall(r'data-page-quality="(\d)"', html))
    if not quality or quality - {"3", "4"}:
        raise SystemExit(f"page quality {sorted(quality)}: not all proofread")
    soup = BeautifulSoup(html, "html.parser")
    for sel in DROP + ["#dynamic_layout_overrider"]:
        for el in soup.select(sel):
            el.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for cut in soup.select(".wst-cesura"):
        cut.replace_with(" ")
    out = []
    block = lambda el: el.name in ("p", "dl") or is_stanza(el)  # noqa: E731
    for p in soup.find_all(block):
        if p.find_parent(block) or p.find_parent("dd"):
            continue
        if p.name == "dl":
            items = p.find_all(["dt", "dd"])
            t, verse = "\n".join("".join(s for s in it.find_all(string=True) if s.find_parent(["dt", "dd"]) is it) for it in items), True
        else:
            t, verse = p.get_text(), is_stanza(p) or bool(p.find_parent("div", class_="poem"))
        t = t.replace("\u200b", "")
        if verse:
            t = re.sub(r" ?\u00a0\u00a0+ ?", "\u2003", t)  # Brodeur's half-line break, wide like a cesura
        t = re.sub(r"[ \t\u00a0\u2009]+", " ", t)
        t = "\n".join(ln.strip() for ln in t.split("\n")).strip()
        t = re.sub(r"\n{2,}", "\n", t)
        if not verse:
            t = t.replace("\n", " ")
        t = re.sub(r'^" ', '"', t)  # Laing's hanging quote mark, floated apart from its verse
        if t and not re.fullmatch(r"[\d\s.\[\]*·]+", t):
            out.append((p, t))
    return out


def bold_chapters(el, t):
    """Brodeur: a paragraph opening with a bold numeral (“IV.”, or “[XXI.” for a chapter he brackets as added) begins
    that chapter. → (number, text, heading)."""
    m = re.match(r"(\[?)([IVXLC]+)\.\s+", t)
    b = el.find("b") if el.name == "p" else None
    if m and b and b.get_text().strip() == f"{m.group(2)}.":
        return roman(m.group(2)), m.group(1) + t[m.end():], None
    return None


def heading_chapters(el, t):
    """Laing: a small-caps “Chapter IV.” (once “Chapter. II.”) over the chapter's title, a paragraph of its own."""
    m = re.fullmatch(r"Chapter\.? ([IVXLC]+)\.\s+(.+)", t)
    return (roman(m.group(1)), "", f"Chapter {m.group(1)}. {m.group(2)}") if m else None


# Laing's chapter IX: a stray, unparsed <poem> tag leaves Eyvind's verse in prose markup and its last line outside it.
REPAIRS = {"Heimskringla/Ynglinga Saga": [("&lt;poem&gt;\n<p>", '<div class="poem"><p>'),
                                         ("\n</p>\nWho loves to dwell on earth below.", "\nWho loves to dwell on earth below.</p></div>")]}


def chapter_rows(pages, chapters):
    """Pages (parts) cut into the translator's numbered chapters: part.chapter.paragraph, or chapter.paragraph for a
    single page. A part's title lines, before its first chapter, are left out; a part with no numbered chapters
    (Brodeur's Prologue) is one chapter. The chapters must run 1, 2, 3… without a gap."""
    rows = []
    for part, (page, label) in enumerate(pages, 1):
        html = parse(page)
        for a, b in REPAIRS.get(page, []):
            if a not in html:
                raise SystemExit(f"{page}: repair no longer applies: {a!r}")
            html = html.replace(a, b)
        ps = pieces(html)
        heads = [chapters(el, t) for el, t in ps]
        nums = [h[0] for h in heads if h]
        if not nums:
            while ps and re.fullmatch(r"[A-ZÁÉÍÓÚÆÖ .,'’-]+", ps[0][1]):
                ps = ps[1:]
            heads = [(1, ps[0][1], label)] + [None] * (len(ps) - 1)
        elif nums != list(range(1, len(nums) + 1)):
            raise SystemExit(f"{page}: chapters run {nums}")
        ch = n = 0
        title = None
        for (el, t), h in zip(ps, heads):
            if h:
                ch, n, t, title = h[0], 0, h[1], h[2] or f"{label} {to_roman(h[0])}"
            if not ch or not t:
                continue
            n += 1
            rows.append({"reference": (f"{part}." if len(pages) > 1 else "") + f"{ch}.{n}", "text": t, **({"title": title} if n == 1 else {})})
        print(f"  {label}: {len(nums) or 1} chapters")
    return rows


def volsunga_rows():
    """Morris and Magnússon, a Wikisource page a chapter, each opening “CHAP. I.” over the chapter's title."""
    rows = []
    for ch in range(1, 44):
        ps = [t for _, t in pieces(parse(f"Völsunga Saga/Chapter {ch}"))]
        m = re.fullmatch(r"CHAP\. ([IVXL]+)\.", ps[0])
        if not m or roman(m.group(1)) != ch and (ch, m.group(1)) != (32, "XXII"):  # the transcription heads 32 “CHAP. XXII.”
            raise SystemExit(f"Völsunga Saga/Chapter {ch}: opens {ps[0]!r}")
        for n, t in enumerate(ps[2:], 1):
            rows.append({"reference": f"{ch}.{n}", "text": t, **({"title": f"Chapter {to_roman(ch)}. {ps[1]}"} if n == 1 else {})})
    return rows


# ---------------------------------------------------------------- the Orphic Hymns

GREEK_CHARS = re.compile(r"[Ͱ-Ͽἀ-῿̀-ͯ  ,.;:·’'ʼ()\[\]⟨⟩<>†*—–\-!«»\"…]+")


def orphic_greek_rows():
    """Abel's Greek, a hymn per Greek Wikisource page, in the order of the work's contents page (Abel's numbering, 0
    the address to Musaeus). The pages are not yet marked proofread there, so each hymn must pass two checks before it
    is taken: Abel's line numbers (every fifth line, as a marker or, on a few pages, typed at the line's end) fall on
    the lines counted here, and nothing but Greek letters and punctuation appears. The older numbering Abel prints
    beside his own, in brackets, is dropped, and a bullet standing in for the raised point (·) put right."""
    index = BeautifulSoup(parse("Ορφικοί ύμνοι", EL_API), "html.parser")
    titles = [(a["title"], a.get_text()) for a in index.select("div.ws-summary a[title]")]
    if len(titles) != 88:
        raise SystemExit(f"Orphic Hymns: {len(titles)} hymns on the contents page")
    rows, bad = [], []
    for n, (page, label) in enumerate(titles):
        soup = BeautifulSoup(parse(page, EL_API), "html.parser")
        for span in soup.select("span[id]"):
            m = re.fullmatch(r"v(\(?)(\d+)\)?", span["id"])
            if m:
                span.replace_with("" if m.group(1) else f" {m.group(2)}")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        lines = []
        for poem in soup.select("div.poem"):
            if poem.find_parent("div", class_="poem"):
                continue
            lines += [ln for ln in (x.strip() for x in poem.get_text().split("\n")) if ln]
        for i, ln in enumerate(lines, 1):
            m = re.search(r"\s+(\d+)$", ln)
            if m:
                # The page for the hymn to Zephyrus sets Abel's 5 against its sixth and last line.
                if int(m.group(1)) != i and (n, m.group(1), i) != (81, "5", 6):
                    raise SystemExit(f"{page}: Abel's line {m.group(1)} falls on line {i}")
                ln = ln[:m.start()]
            ln = ln.replace("∙", "·")
            if not GREEK_CHARS.fullmatch(ln):
                bad.append((page, i, ln))
            rows.append({"reference": f"{n}.{i}", "original": ln, **({"title": label} if i == 1 else {})})
        if not lines:
            raise SystemExit(f"{page}: no lines")
    if bad:
        raise SystemExit("Orphic Hymns: not Greek: " + "; ".join(f"{p} {i}: {ln!r}" for p, i, ln in bad[:10]))
    return rows


def taylor(name):
    f = os.path.join(CACHE, "hoo", name)
    if not os.path.exists(f):
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "wb").write(fetch(f"{TAYLOR}/{name}"))
    t = open(f, encoding="utf-8").read()
    # The mirror read sacred-texts' Windows-1252 as Latin-1, so œ came through as U+009C: put such characters back.
    return re.sub(r"[\x80-\x9f]", lambda m: bytes([ord(m.group())]).decode("cp1252"), t)


TAYLOR_MISNUMBERED = []


def taylor_page(name):
    """(heading, fumigation, lines) of one of Taylor's hymns, with his line numbers checked and taken off, and his notes,
    page numbers and the site's links left out."""
    html = taylor(name).split('<h3 align="CENTER">Footnotes</h3>')[0]
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select("center, a[href^='#fn_']"):
        el.decompose()
    for a in soup.select("a[name^='page_']"):
        a.find_parent("p").decompose()
    h3 = soup.find("h3")
    head = h3.get_text(" ", strip=True).rstrip(" .*,").replace("T O L A T O N A", "TO LATONA")  # letter-spaced on the page
    fum = next((h.get_text(" ", strip=True) for h in soup.find_all("h6") if "FUMIGATION" in h.get_text().upper()), None)
    for br in soup.find_all("br"):
        br.replace_with("\n")
    lines = []
    for p in h3.find_all_next("p"):  # not the title-page lines above the first hymn
        lines += [ln for ln in (re.sub(r"\s+", " ", x).strip() for x in p.get_text().split("\n")) if ln]
    wrong = []
    for i, ln in enumerate(lines, 1):
        m = re.search(r"\s+(\d+)$", ln)
        if m:
            if int(m.group(1)) != i:
                wrong.append((int(m.group(1)), i))
            lines[i - 1] = ln[:m.start()]
    # A lone misprinted number (hymn X prints 55 for 45) is let pass; two in a row means a line lost or doubled.
    if any(b[1] - b[0] == a[1] - a[0] and b[1] == a[1] + 5 for a, b in zip(wrong, wrong[1:])):
        raise SystemExit(f"{name}: Taylor's line numbers {wrong} (printed, counted)")
    TAYLOR_MISNUMBERED.extend((name, *x) for x in wrong)
    caps = lambda s: re.sub(r"\b[A-ZÆŒ]{2,}\b", lambda m: m.group().capitalize(), s)  # noqa: E731
    head = re.sub(r"\s+", " ", caps(head)).replace(" The ", " the ").replace(" Of ", " of ").replace(" Or ", " or ").replace(" As ", " as ")
    return head, fum and caps(fum), lines


def taylor_rows():
    """Taylor's 86 hymns and the address to Musaeus (hoo05–hoo91), keyed by the Greek's numbers: his address runs on
    into the hymn to Hecate at his line 55, which becomes hymn 1, so his hymn I is hymn 2 and so on."""
    rows = []
    head, _, lines = taylor_page("hoo05.md")
    if len(lines) != 64 or not lines[54].startswith("I call Einodian Hecate"):
        raise SystemExit(f"Taylor's address to Musaeus: {len(lines)} lines, line 55 {lines[54]!r}")
    rows.append({"reference": "0.1", "text": "\n".join(lines[:54]), "title": "To Musaeus"})
    rows.append({"reference": "1.1", "text": "\n".join(lines[54:]), "title": "To Hecate (Taylor's To Musaeus, lines 55–64)"})
    for n in range(1, 87):
        head, fum, lines = taylor_page(f"hoo{n + 5:02d}.md")
        title = f"{head} (Taylor {to_roman(n)})"
        for i, t in enumerate(([fum] if fum else []) + ["\n".join(lines)], 1):
            rows.append({"reference": f"{n + 1}.{i}", "text": t, **({"title": title} if i == 1 else {})})
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for w in WORKS:
        if "rows" in w:
            rows = w["rows"]()
        else:
            rows = []
            for ch, (page, label) in enumerate(w["pages"], 1):
                paras = paragraphs(parse(page), w.get("verseLines", False))
                if not paras:
                    raise SystemExit(f"{page}: no paragraphs")
                for n, t in enumerate(paras, 1):
                    rows.append({"reference": f"{ch}.{n}", "text": t, **({"title": label} if n == 1 else {})})
        with open(os.path.join(OUT, f"{w['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        home = "https://en.wikisource.org/wiki/" + urllib.parse.quote(w["home"].replace(" ", "_")) if "home" in w else w["links"][0]["url"]
        via = w.get("from", "Wikisource")
        gid = None
        if w["id"] in GREEK:
            # The Greek comes first, as the text; the English is its translation, paired chapter by chapter.
            gid, gname, glevels, files, *opts = GREEK[w["id"]]
            opts = opts[0] if opts else {}
            grows = files() if callable(files) else greek_rows(files)
            with open(os.path.join(OUT, f"{gid}.json"), "w", encoding="utf-8") as f:
                json.dump(grows, f, ensure_ascii=False, indent=1)
            texts.append({"id": gid, "file": f"world/{gid}.json", "name": gname, "band": "kin", "group": w["group"], "levels": glevels,
                          "original": GREEK_ORIGINAL, **({"verseLines": True} if opts.get("verseLines", True) else {}),
                          "source": f"{opts.get('source', f'Greek: {PERSEUS_SOURCE}')}; English: {w['by']} ({w['year']}), from {via}",
                          "pairs": [{"with": w["id"], "mode": opts.get("mode", "prefix"), "label": f"{w['by'].split()[-1]} ({w['year']})"}]})
            print(f"{gid:28s} {len({r['reference'].rsplit('.', 1)[0] for r in grows}):3d} chapters {len(grows):6d} {'lines' if opts.get('verseLines', True) else 'sections'} of Greek")
        texts.append({"id": w["id"], "file": f"world/{w['id']}.json", "name": f"{w['name']} — {w['by'].split()[-1]}" if gid else w["name"],
                      "band": "kin", "group": w["group"], **({"translationOf": gid} if gid else {}), "levels": w["levels"],
                      **({"verseLines": True} if w.get("verseLines") else {}),
                      "source": f"English: {w['by']} ({w['year']}), from {via}"})
        records[w["id"]] = {"english": {"by": w["by"], "work": w["work"], "year": w["year"], "links": w.get("links", [{"label": "Wikisource", "url": home}]),
                                        "via": w.get("via", w["links"][0] if "links" in w else {"label": "Wikisource", "url": home}),
                                        "note": w.get("note", "Public domain; the proofread Wikisource transcription, footnotes left out.")}}
        print(f"{w['id']:28s} {len({r['reference'].rsplit('.', 1)[0] for r in rows}):3d} chapters {len(rows):6d} paragraphs")
    if "--no-catalog" in sys.argv:
        print("--no-catalog: library_catalog.json and translation_sources.json left alone")
    else:
        write([BAND], texts, records)
    return texts, records


if __name__ == "__main__":
    main()
