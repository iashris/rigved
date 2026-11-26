#!/usr/bin/env python3
"""Japan's two founding chronicles and the Egyptian Book of the Dead, in English, from Wikisource's proofread
transcriptions.

- Kojiki, Records of Ancient Matters (712): Basil Hall Chamberlain's translation (1882), Ō no Yasumaro's preface and
  the 180 sections, a Wikisource page each. Chamberlain's own introduction and appendices are left out.
- Nihongi, Chronicles of Japan (720): William George Aston's translation (1896), the 30 books, a page each.
- The Book of the Dead, Theban recension: E. A. Wallis Budge's translation as reprinted in Egyptian Literature
  (The World's Great Classics, New York: Colonial Press, 1901), a selection of chapters chiefly from the Papyrus of
  Ani, read in order from that volume's scan pages (see bod_rows for why not from the chapter pages).

All public domain. Fetched one request at a time through wikisource_world.py's cached reader (cache/wikisource), and
cut into paragraphs by its pieces(), which takes only pages Wikisource marks proofread or validated and leaves out
footnotes, page numbers and header boxes. An entry is one paragraph, numbered from 1 within its section, book or
chapter.

Writes public/data/japan/ and public/data/egypt/ and adds the texts to library_catalog.json and
translation_sources.json (--no-catalog skips that). Rerunnable.
Usage: .venv/bin/python -I scripts/corpus2/wikisource_east_egypt.py [--no-catalog]
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "public", "data")
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402
from wikisource_world import API, CACHE, fetch, parse, pieces, roman, to_roman  # noqa: E402

KOJIKI = "Kojiki (Chamberlain, 1882)"
BOD = "Egyptian Literature/The Book of the Dead"
# The Book of the Dead's run of the 1901 volume's scan, from its first chapter's section to its last chapter's.
BOD_INDEX, BOD_PAGES = "Egyptian Literature (1901).djvu", (27, 155)
BOD_FIRST, BOD_LAST = "A Hymn to the Setting Sun", "Of the Four Flames"
CAPS = re.compile(r"[^a-z]+")  # a title-page or running-head line: no lower-case letters


def ws(title):
    return "https://en.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


OPEN = re.compile(r"[^.!?:;—\"'”’)\]]$")  # a paragraph that stops mid-sentence


def is_head(el):
    return el.find_parent("div", attrs={"role": "heading"}) is not None


def raw_paras(html):
    """pieces() of a page, as (element, text), with each illustration (a figure and its caption, Aston's
    “Magatama.”) left out. A rubric, set in small capitals for the papyri's red ink, begins lower-case on the page
    and is given its capital; a few rubrics are typed all in lower case, with no small-capitals markup, and are
    given a capital at each sentence (a roman numeral, “ii.”, stays as it is)."""
    soup = BeautifulSoup(html, "html.parser")
    for fig in soup.find_all("figure"):
        (fig.find_parent("div", class_="wst-block-center") or fig).decompose()
    out = []
    for el, t in pieces(str(soup)):
        first = el.find(string=lambda s: s.strip(" \n\t​"))
        if t[:1].islower() and first is not None and first.find_parent("span", class_=["smallcaps", "wst-asc"]):
            t = t[0].upper() + t[1:]
        elif len(t) > 40 and not any(c.isupper() for c in t):
            t = re.sub(r"(^|[.!?]\s+)(\[?)([a-z])(?![a-z]*\.)", lambda m: m.group(1) + m.group(2) + m.group(3).upper(), t)
        out.append((el, t))
    return out


def mend(items):
    """A paragraph that stops mid-sentence and one that goes on in lower case are halves of one, cut by a page
    break or a plate: they are joined again. Aston's variant readings, which interrupt a sentence as paragraphs of
    their own, end with a full stop and so are left apart."""
    out = []
    for el, t in items:
        if out and t[:1].islower() and OPEN.search(out[-1][1]) and not is_head(out[-1][0]) and not is_head(el):
            out[-1] = (out[-1][0], out[-1][1] + " " + t)
        else:
            out.append((el, t))
    return out


def paras(title):
    return [t for _, t in mend(raw_paras(parse(title)))]


def scan_range(index, first, last, title, fromsection=None, tosection=None, step=10):
    """The scan pages first…last of an index, in order, read ten at a time (a single transclusion of a hundred pages
    runs past MediaWiki's expansion limits and comes back short) and checked to hold every page asked for. Blank
    plates (quality 0, without text) are let through; every other page must be proofread, as pieces() requires."""
    out = []
    for a in range(first, last + 1, step):
        b = min(a + step - 1, last)
        args = f'index="{index}" from={a} to={b}'
        args += f' fromsection="{fromsection}"' if fromsection and a == first else ""
        args += f' tosection="{tosection}"' if tosection and b == last else ""
        q = urllib.parse.urlencode({"action": "parse", "text": f"<pages {args} />", "title": title, "prop": "text",
                                    "contentmodel": "wikitext", "format": "json", "formatversion": "2"})
        f = os.path.join(CACHE, "range-" + hashlib.sha1(q.encode()).hexdigest() + ".json")
        if not os.path.exists(f):
            json.dump(fetch(f"{API}?{q}"), open(f, "w", encoding="utf-8"), ensure_ascii=False)
        html = json.load(open(f, encoding="utf-8"))["parse"]["text"]
        got = {int(x) for x in re.findall(r'data-page-index="(\d+)"', html)}
        if got != set(range(a, b + 1)):
            raise SystemExit(f"{index} {a}–{b}: pages {sorted(got)} came back")
        html = re.sub(r'data-page-quality="0"', "", html)
        out += raw_paras(html)
    return mend(out)


def cap(word):
    """KAMI-YAMATO → Kami-yamato, (JIMMU → (Jimmu: the first letter up, the rest down."""
    i = next((k for k, c in enumerate(word) if c.isalpha()), None)
    return word if i is None else word[:i] + word[i].upper() + word[i + 1:].lower()


def kojiki_rows():
    """Section 0 is Yasumaro's preface (its title-page lines dropped); sections 1–180 each open with Chamberlain's
    bracketed “[Sect. N.—Title.]”, whose numeral must match the page, and which becomes the section's title. The
    running head above it (“RECORDS OF ANCIENT MATTERS.”, “VOL. II.”) is dropped."""
    rows = []
    ps = paras(f"{KOJIKI}/Preface")
    i = ps.index("PREFACE.")
    for n, t in enumerate(ps[i + 1:], 1):
        rows.append({"reference": f"0.{n}", "text": t, **({"title": "Preface, by Ō no Yasumaro"} if n == 1 else {})})
    for sec in range(1, 181):
        ps = paras(f"{KOJIKI}/Section {sec}")
        heads = [k for k, t in enumerate(ps) if re.match(r"\[?Sect\. [IVXLC]+\.", t)]
        if len(heads) != 1:
            raise SystemExit(f"Kojiki section {sec}: {len(heads)} section headings")
        k = heads[0]
        if any(not (CAPS.fullmatch(t) or re.fullmatch(r"Vol\. [IVX]+\.", t)) for t in ps[:k]):
            raise SystemExit(f"Kojiki section {sec}: text above the heading: {ps[:k]}")
        m = re.fullmatch(r"\[?Sect\. ([IVXLC]+)\.\s*[—–-]\s*(.+?)\.?\]?", ps[k])
        if not m or roman(m.group(1)) != sec:
            raise SystemExit(f"Kojiki section {sec}: heading {ps[k]!r}")
        body = ps[k + 1:]
        if not body:
            raise SystemExit(f"Kojiki section {sec}: no text")
        for n, t in enumerate(body, 1):
            rows.append({"reference": f"{sec}.{n}", "text": t, **({"title": f"Section {m.group(1)}. {m.group(2)}"} if n == 1 else {})})
    return rows


def nihongi_rows():
    """A book's page opens with its title lines in capitals (“BOOK III.”, “THE EMPEROR KAMI-YAMATO IHARE-BIKO.”,
    “(JIMMU TENNŌ.)”), which become the book's title; the emperors' headings further in stay as paragraphs."""
    rows = []
    for b in range(1, 31):
        ps = paras(f"Nihongi/Book {to_roman(b)}")
        if ps[0].replace(" ", "") == "NIHONGI.":  # the work's title, over Books I and XVII (once letter-spaced)
            ps = ps[1:]
        if ps[0] != f"BOOK {to_roman(b)}.":
            raise SystemExit(f"Nihongi book {b}: opens {ps[0]!r}")
        k = 1
        while k < len(ps) and (CAPS.fullmatch(ps[k]) or ps[k] in ("or", "Or")) and len(ps[k]) < 120:  # XX: “(BI-DATSU TENNŌ / or / BIN-DATSU…”
            k += 1
        sub = " ".join(cap(w) for w in " ".join(ps[1:k]).split())
        sub = re.sub(r"(?<=\s)(No|Of|The|Or)\b", lambda m: m.group().lower(), sub).rstrip(".")
        title = f"Book {to_roman(b)}" + (f". {sub}" if sub else "")
        for n, t in enumerate(ps[k:], 1):
            rows.append({"reference": f"{b}.{n}", "text": t, **({"title": title} if n == 1 else {})})
    return rows


SMALL = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "into", "of", "on", "or", "over", "the", "to", "unto", "upon", "with"}


def title_case(s):
    words = [cap(w) for w in s.split()]
    return " ".join(w.lower() if k and w.lower() in SMALL else w for k, w in enumerate(words)).rstrip(".")


def bod_rows():
    """Read from the volume's scan pages in order, not from Wikisource's chapter pages: those transclude each page
    by its chapter's section label, and a page left without labels (79, in the middle of a Thoth litany) appears on
    none of them. A level-2 heading (“COMING FORTH BY DAY”) opens a chapter and becomes its title; the level-3 one
    under it, Budge's note of the papyrus and sheet, stays as the chapter's first paragraph."""
    ps = scan_range(BOD_INDEX, BOD_PAGES[0], BOD_PAGES[1], BOD, fromsection=BOD_FIRST, tosection=BOD_LAST)
    rows, ch, n = [], 0, 0
    for el, t in ps:
        head = el.find_parent("div", attrs={"role": "heading"})
        if head is not None and head.get("aria-level") == "2":  # (mend never joins a heading)
            ch, n, title = ch + 1, 0, title_case(t)
            continue
        if not ch:
            raise SystemExit(f"Book of the Dead: text before the first chapter: {t[:80]!r}")
        n += 1
        rows.append({"reference": f"{ch}.{n}", "text": t, **({"title": title} if n == 1 else {})})
    empty = [r for r in rows if not r["text"]]
    if ch < 100 or empty:
        raise SystemExit(f"Book of the Dead: {ch} chapters, {len(empty)} empty paragraphs")
    return rows


JAPAN = {"id": "japan", "after": ["china", "near_east"], "name": "Japan",
         "blurb": "not Indic: the Shintō chronicles of Japan's gods and first emperors — Izanagi and Izanami stirring the sea with a jewelled "
                  "spear, Susanoo slaying the eight-headed serpent as Indra slays Vṛtra. In English"}
EGYPT = {"id": "egypt", "after": ["near_east", "kin"], "name": "Ancient Egypt",
         "blurb": "not Indic: the Book of the Dead, the spells that carried the soul through the underworld to the judgment of Osiris — the "
                  "heart weighed against the feather of Maat, order, as ṛta is order. In English"}


def main():
    texts, records = [], {}
    works = [
        ("kojiki_chamberlain", "japan", "Kojiki (Records of Ancient Matters)", ["Section", "Paragraph"], [711, 712], kojiki_rows,
         {"by": "Basil Hall Chamberlain", "work": "Kojiki, or Records of Ancient Matters, Transactions of the Asiatic Society of Japan 10, "
          "supplement, Yokohama", "year": "1882", "home": KOJIKI,
          "note": "Public domain; the proofread Wikisource transcription, Chamberlain's notes, introduction and appendices left out."}),
        ("nihongi_aston", "japan", "Nihongi (Chronicles of Japan)", ["Book", "Paragraph"], [720, 720], nihongi_rows,
         {"by": "William George Aston", "work": "Nihongi: Chronicles of Japan from the Earliest Times to A.D. 697, Transactions and "
          "Proceedings of the Japan Society, supplement I, London: Kegan Paul", "year": "1896", "home": "Nihongi",
          "note": "Public domain; the proofread Wikisource transcription, Aston's notes left out."}),
        ("book_of_the_dead_budge", "egypt", "The Book of the Dead (Theban recension)", ["Chapter", "Paragraph"], [-1550, -1070], bod_rows,
         {"by": "E. A. Wallis Budge", "work": "The Book of the Dead according to the Theban Recension, in Egyptian Literature, The World's "
          "Great Classics, New York: Colonial Press", "year": "1901", "home": BOD,
          "note": "Public domain; the proofread Wikisource transcription. A selection of chapters, chiefly from the Papyrus of Ani "
                  "(British Museum 10470), in the order of the 1901 volume."}),
    ]
    for tid, band, name, levels, date, rows_of, credit in works:
        rows = rows_of()
        os.makedirs(os.path.join(DATA, band), exist_ok=True)
        with open(os.path.join(DATA, band, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        texts.append({"id": tid, "file": f"{band}/{tid}.json", "name": name, "band": band, "levels": levels, "date": date,
                      "source": f"English: {credit['by']} ({credit['year']}), from Wikisource"})
        home = ws(credit["home"])
        records[tid] = {"english": {"by": credit["by"], "work": credit["work"], "year": credit["year"],
                                    "links": [{"label": "Wikisource", "url": home}], "via": {"label": "Wikisource", "url": home},
                                    "note": credit["note"]}}
        print(f"{tid:26s} {len({r['reference'].rsplit('.', 1)[0] for r in rows}):4d} {levels[0].lower()}s {len(rows):6d} paragraphs", flush=True)
    if "--no-catalog" in sys.argv:
        print("--no-catalog: library_catalog.json and translation_sources.json left alone")
    else:
        write([EGYPT, JAPAN], texts, records)


if __name__ == "__main__":
    main()
