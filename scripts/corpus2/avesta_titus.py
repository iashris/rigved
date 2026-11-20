#!/usr/bin/env python3
"""The Avesta for the comparative shelf: Geldner's Avestan beside the Sacred Books of the East English.

Avestan: TITUS's Avesta corpus (K. F. Geldner, Avesta, the Sacred Books of the Parsis, Stuttgart 1886–96, prepared by
S. Fritz and J. Gippert), downloaded by `titus_fetch.py avest` into cache/titus/raw/avest. Only the Avestan itself is
taken (the main-size iija*/iiaa* spans): TITUS interleaves the Pahlavi and Sanskrit versions, which are left out.

English: J. Darmesteter (SBE 4, Vendīdād, 1880; SBE 23, Yašts, Sīrōzas and Nyāyišns, 1883) and L. H. Mills (SBE 31,
Yasna, Visperad, Āfrīnagāns and Gāhs, 1887), all public domain, from the sacred-texts.com transcriptions fetched
through the Wayback Machine into cache/sacred_texts (sacred-texts.com itself answers scripts with a bot challenge).
Not avesta.org: its Yasna replaces Mills's Gāthās with Bartholomae via Taraporewala (1951) and its chapter 12 with
Peterson's own copyrighted version.

The translators number paragraphs after Westergaard and Spiegel, which often differ from Geldner's, so the English is
paired by chapter (`prefix`): a Yasna chapter, a Yašt or a Fargard opens with its Avestan on the left and the whole
English chapter on the right, never a verse beside a verse it does not translate.

Writes public/data/avesta/<id>.json and <id>_en.json and adds them to library_catalog.json and
translation_sources.json. Rerunnable.

Usage: .venv/bin/python -I scripts/corpus2/avesta_titus.py
"""
import glob
import html
import json
import os
import re
import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(ROOT, "cache", "titus", "raw", "avest")
SBE = os.path.join(ROOT, "cache", "sacred_texts")
OUT = os.path.join(ROOT, "public", "data", "avesta")
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

AVESTAN = re.compile(r"^ii(ja|aa)[a-z]*16$")

BAND = {"id": "avesta", "after": ["travel"], "name": "Avesta",
        "blurb": "not Indic: the Zoroastrian scripture, the Ṛgveda's nearest kin — the same haoma (soma), Mithra (Mitra), "
                 "Vərəθraγna (Vṛtrahan), and Indra among the demons. Geldner's Avestan with the Sacred Books of the East English"}
ORIGINAL = {"name": "Avestan", "lang": "ae-Latn", "label": "Avestan", "short": "Av"}

MILLS = {"by": "L. H. Mills", "work": "The Zend-Avesta, Part III: The Yasna, Visparad, Âfrînagân, Gâhs, and Miscellaneous Fragments, "
         "Sacred Books of the East vol. 31, Oxford: Clarendon Press", "year": "1887", "vol": "sbe31"}
DARM4 = {"by": "James Darmesteter", "work": "The Zend-Avesta, Part I: The Vendîdâd, Sacred Books of the East vol. 4, Oxford: Clarendon Press",
         "year": "1880", "vol": "sbe04"}
DARM23 = {"by": "James Darmesteter", "work": "The Zend-Avesta, Part II: The Sîrôzahs, Yasts, and Nyâyis, Sacred Books of the East vol. 23, "
          "Oxford: Clarendon Press", "year": "1883", "vol": "sbe23"}

# id -> TITUS book, name, levels, translation, and the SBE pages: {Geldner chapter: page number in that volume}.
TEXTS = OrderedDict([
    ("avesta_yasna", {"book": "Y", "name": "Yasna", "levels": ["Hāiti", "Paragraph"], "tr": MILLS,
                      "note": "the liturgy; chapters 28–34 and 43–53 are the Gāthās, Zarathuštra's own hymns, and 9–11 the hymn to Haoma"}),
    ("avesta_visperad", {"book": "Vr", "name": "Visperad", "levels": ["Karde", "Paragraph"], "tr": MILLS}),
    ("avesta_yasht", {"book": "Yt", "name": "Yašts", "levels": ["Yašt", "Paragraph"], "tr": DARM23,
                      "note": "hymns to the gods: Mithra (10), Tištrya (8), Vərəθraγna (14), Anāhitā (5)"}),
    ("avesta_vendidad", {"book": "Vd", "name": "Vīdēvdād (Vendīdād)", "levels": ["Fargard", "Paragraph"], "tr": DARM4,
                         "note": "the law against the daēvas; Indra is named among them at 10.9 and 19.43"}),
    ("avesta_nyayisn", {"book": "Ny", "name": "Nyāyišns (Khorda Avesta)", "levels": ["Nyāyišn", "Paragraph"], "tr": DARM23}),
    ("avesta_sirozah", {"book": "S", "name": "Sīrōzas (Khorda Avesta)", "levels": ["Sīrōza", "Day"], "tr": DARM23}),
    ("avesta_gah", {"book": "G", "name": "Gāhs (Khorda Avesta)", "levels": ["Gāh", "Paragraph"], "tr": MILLS}),
    ("avesta_afrinagan", {"book": "A", "name": "Āfrīnagāns (Khorda Avesta)", "levels": ["Āfrīnagān", "Paragraph"], "tr": MILLS}),
])


# ---- Avestan (TITUS) ----

def titus_books():
    """{book: {chapter: {paragraph: [(verse label, text piece)]}}} in page order."""
    books, book, ch, para, verse = OrderedDict(), None, None, None, None
    for f in sorted(glob.glob(os.path.join(RAW, "*.htm"))):
        for sp in BeautifulSoup(open(f, encoding="utf-8").read(), "html.parser").find_all("span"):
            sid, t = sp.get("id") or "", sp.get_text(" ", strip=True)
            if sid in ("h2", "h3", "h4", "h5"):
                val = t.split(":", 1)[1].strip()
                if sid == "h2":
                    book, ch, para = val, None, None
                    books.setdefault(book, OrderedDict())
                elif sid == "h3":
                    ch, para = val, None
                elif sid == "h4":
                    para = val
                else:
                    verse = val
            elif AVESTAN.match(sid) and book and ch is not None and para is not None:
                books[book].setdefault(ch, OrderedDict()).setdefault(para, []).append((verse, sp.get_text("", strip=False)))
    return books


def avestan(pieces):
    """Geldner's lines as TITUS gives them ("haomō. upāit̰. zaraϑuštrəm.::") to plain transliteration, one line per
    verse: the word-divider dots become spaces, a dot inside a compound a hyphen, and the editor's marks of
    emendation (*, +) and verse ends (:, ::) go; brackets around later additions stay."""
    lines = OrderedDict()
    for verse, text in pieces:
        lines.setdefault(verse, []).append(text)
    out = []
    for parts in lines.values():
        s = " ".join(parts).replace("\xa0", " ")
        s = re.sub(r"[*+†^Õ]", "", s)
        s = re.sub(r":+", " ", s)
        s = re.sub(r"(?<=\S)\.(?=[^\s.])", "-", s)  # pairi.yaoždaϑəṇtəm → pairi-yaoždaϑəṇtəm
        s = re.sub(r"\.", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            out.append(s)
    return "\n".join(out)


def para_key(p):
    """TITUS paragraph labels: "12", a repeat "12_R1" (folded into 12 by the caller), and in Visperad 21 the
    Yasna Haptaŋhāiti it recites, "0:35,1" → "Y35,1"."""
    m = re.fullmatch(r"0:(\d+)(?:,(\d+))?", p)
    if m:
        return f"Y{m.group(1)}" + (f",{m.group(2)}" if m.group(2) else "")
    return p


def avestan_entries(chapters):
    """A repeat ("12_R1": the liturgy says the stanza, or a run of stanzas, again) joins its own paragraph."""
    rows, at = [], {}
    for ch, paras in chapters.items():
        for p, pieces in paras.items():
            text = avestan(pieces)
            if not text:
                continue  # a paragraph TITUS only cites (Visperad 21 points to the Yasna) has no Avestan of its own
            base, repeat = p.split("_R", 1)[0], "_R" in p
            ref = f"{ch}.{para_key(base)}"
            if repeat and ref in at:
                at[ref]["original"] += "\n" + text
            elif ref in at:
                raise SystemExit(f"paragraph {ref} twice")
            else:
                at[ref] = {"reference": ref, "original": text}
                rows.append(at[ref])
    return rows


# ---- English (SBE, sacred-texts.com) ----

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s):
    n = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMAN[a]
        n += -v if b != " " and ROMAN.get(b, 0) > v else v
    return n


SMALL = "\x00"  # marks a paragraph set in small type: Darmesteter's contents summary at the head of a Fargard


def page_text(path):
    """A sacred-texts page's body paragraphs, footnote calls and page numbers removed, as plain text."""
    h = open(path, encoding="utf-8", errors="strict").read()
    title = re.search(r"<TITLE>(.*?)</TITLE>", h, re.S | re.I).group(1)
    body = h.split("</h3>", 1)[-1] if "</h3>" in h.lower() else h
    body = re.split(r"<h3[^>]*>\s*Footnotes", body, flags=re.I)[0]
    # Darmesteter's small-type contents run over several paragraphs inside one <FONT SIZE="-1">: mark each
    # paragraph within it. Footnote calls and page numbers close their own tiny FONTs first, so hide those.
    body = re.sub(r'(<FONT SIZE="?1"?[^>]*>[^<]*)</FONT>', r"\1</font1>", body, flags=re.I)
    body = re.sub(r'<FONT SIZE="-1">(.*?)(?:</FONT>|$)', lambda m: re.sub(r"(<p[^>]*>)", r"\1" + SMALL, "<p>" + m.group(1))[3:],
                  body, flags=re.I | re.S)
    paras = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S | re.I):
        if re.search(r'NAME="page_\d+"', p) or "sacred-texts.com" in p:
            continue
        p = re.sub(r"<A NAME=\"fr_\d+\"></A><A HREF=\"#fn_\d+\"><FONT SIZE=\"1\">[^<]*</FONT1?></A>", "", p, flags=re.I)
        p = re.sub(r"<[^>]+>", "", p)
        p = re.sub(r"\s+", " ", html.unescape(p)).strip()
        p = re.sub(r"\s+([,.;:!?)])", r"\1", p).replace("( ", "(")  # the space a removed footnote call leaves
        if p:
            paras.append(p)
    return html.unescape(title), paras


def english_entries(ch, paras, who):
    """One entry per numbered paragraph: "1. …", Darmesteter's "2 (7). …" (his number, then Westergaard's), Mills's
    "3, 4. …" and "9-11. …". An unnumbered paragraph joins the one before it, or opens the chapter as paragraph 0
    when it comes first; "[paragraph continues]" (a page break in the printed book) runs on without a break.
    The translator's own preface, ended by Mills's heading "Translation." or Darmesteter's rule of underscores,
    becomes one entry headed as his, keyed "intro" so its numbers never pass for verses and its place never
    collides with a Yašt's opening invocation, which Darmesteter numbers 0."""
    intro = []
    first = next((i for i, p in enumerate(paras) if re.match(r"1(?:\s*\(\d+\))?\.\s", p)), len(paras))
    cut = next((i for i, p in enumerate(paras) if p.lstrip(SMALL) == "Translation."
                or re.fullmatch(r"_{5,}", p.lstrip(SMALL)) and i < first), None)  # a rule after § 1 only divides the text
    if cut is not None:
        intro, paras = paras[:cut], paras[cut + 1:]
    # Small type at the head is Darmesteter's contents ("1-16. Contracts") unless it holds § 0 or § 1 itself: he also sets
    # the abbreviated stock prayers of a Nyāyiš in small type, and those are the text.
    lead = next((i for i, p in enumerate(paras) if not p.startswith(SMALL)), len(paras))
    if any(re.match(r"[01](?:\s*\(\d+\))?\.\s", p.lstrip(SMALL)) for p in paras[:lead]):
        lead = 0
    intro, paras = intro + paras[:lead], paras[lead:]
    intro = [p.replace(SMALL, "").strip() for p in intro]
    paras = [p.replace(SMALL, "").strip() for p in paras]
    rows = []
    if intro:
        rows.append({"reference": f"{ch}.intro", "title": f"{who}\u2019s introduction", "text": "\n\n".join(intro)})
    for p in paras:
        m = re.match(r"(\d+(?:\s*[,\u2013-]\s*\d+)*)(?:\s*\([^)]*\))?\s*\.\s+(.*)", p, re.S)
        if p.startswith("[paragraph continues]") and rows:
            rows[-1]["text"] += " " + p[len("[paragraph continues]"):].strip()
        elif m:
            rows.append({"reference": f"{ch}." + re.sub(r"\s*[,\u2013-]\s*", "-", m.group(1)), "text": m.group(2)})
        elif rows and not rows[-1]["reference"].endswith(".intro"):
            rows[-1]["text"] += "\n\n" + p
        else:
            rows.append({"reference": f"{ch}.0", "text": p})
    # The translator's own slip (Darmesteter numbers Fargard V 40 twice) would give two entries one reference:
    # keep both, lettered in order, and say so.
    seen = {}
    for r in rows:
        seen.setdefault(r["reference"], []).append(r)
    for ref, rs in seen.items():
        if len(rs) > 1:
            print(f"  note: {who} numbers {ref} {len(rs)} times; lettered a, b, ...")
            for i, r in enumerate(rs):
                r["reference"] = ref + "abcdefgh"[i]
    return rows


def sbe_pages():
    """{(TITUS book, Geldner chapter): page path}, read off each volume's contents page. Mills's Āfrīnagāns I–III
    are Geldner's 2–4 (Geldner's first, the Dahmān, is not in SBE 31); every other book numbers its chapters alike."""
    rules = [
        ("sbe31", r"^Yasna ([LXVI]+)\b", "Y", 0),
        ("sbe31", r"^Visparad ([LXVI]+)\b", "Vr", 0),
        ("sbe31", r"^([LXVI]+)\. Âfrînagân", "A", 1),
        ("sbe31", r"^([LXVI]+)\. (?:The )?Gâh", "G", 0),
        ("sbe04", r"^Fargard ([LXVI]+)\b", "Vd", 0),
        ("sbe23", r"^Sîrôzah ([LXVI]+)\b", "S", 0),
        ("sbe23", r"^([LXVI]+)\. .*Yast\b", "Yt", 0),
        ("sbe23", r"^([LXVI]+)\. .*Nyâyis\b", "Ny", 0),
    ]
    out = {}
    for vol in ("sbe31", "sbe04", "sbe23"):
        idx = open(os.path.join(SBE, f"{vol}.index.htm"), encoding="utf-8").read()
        for href, label in re.findall(r'<A HREF="([^"#]+\.htm)">(.*?)</A>', idx, re.I | re.S):
            label = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", label))).strip()
            if href == "sbe31069.htm":  # listed as "Yasna LXIX", but it sits between LXIII and LXV: it is LXIV
                label = "Yasna LXIV"
            for v, pat, book, shift in rules:
                m = re.match(pat, label) if v == vol else None
                if m:
                    n = roman(m.group(1)) + shift
                    if book == "Yt" and n >= 20:
                        # Geldner's Yašt 20 is the Hōm Yašt (Yasna 9-11, which Darmesteter leaves to Mills) and his 21
                        # the Vanant; Darmesteter's XX is the Vanant, his XXI-XXIV fragments Geldner keeps out of the Yašts.
                        if n > 20:
                            break
                        n = 21
                    out.setdefault((book, str(n)), os.path.join(SBE, vol, href))
                    break
    return out


def main():
    books = titus_books()
    pages = sbe_pages()
    os.makedirs(OUT, exist_ok=True)
    rows_cat, records, report = [], {}, []
    for tid, meta in TEXTS.items():
        chapters = books[meta["book"]]
        av = avestan_entries(chapters)
        en = []
        for ch in chapters:
            page = pages.get((meta["book"], ch))
            if not page:
                report.append(f"{tid} {ch}: no English")
                continue
            if not os.path.exists(page):
                raise SystemExit(f"{page} not downloaded")
            _, paras = page_text(page)
            es = english_entries(ch, paras, meta["tr"]["by"].split()[-1])
            if not es:  # Yasna LXIII: the page has only a footnote (the chapter repeats passages found elsewhere)
                report.append(f"{tid} {ch}: the translator's page has no text")
                continue
            en += es
            n_av = sum(1 for r in av if r["reference"].split(".")[0] == ch)
            if abs(len(es) - n_av) > max(2, n_av // 4):
                report.append(f"{tid} {ch}: {n_av} Avestan paragraphs, {len(es)} English")
        for name, rows in ((tid, av), (f"{tid}_en", en)):
            with open(os.path.join(OUT, f"{name}.json"), "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
        tr = meta["tr"]
        label = f"{tr['by'].split()[-1]} ({tr['year']})"
        rows_cat.append({"id": tid, "file": f"avesta/{tid}.json", "name": meta["name"], "band": "avesta", "levels": meta["levels"],
                         "original": ORIGINAL, "source": f"Avestan: Geldner (1886–96), TITUS; English: {tr['by']}, SBE {int(tr['vol'][3:])} ({tr['year']})"
                         + (f" — {meta['note']}" if meta.get("note") else ""),
                         "pairs": [{"with": f"{tid}_en", "mode": "prefix", "label": label}]})
        rows_cat.append({"id": f"{tid}_en", "file": f"avesta/{tid}_en.json", "name": f"{meta['name']} — {tr['by'].split()[-1]}", "band": "avesta",
                         "translationOf": tid, "levels": meta["levels"], "source": f"{tr['by']}, {tr['work']} ({tr['year']})"})
        vol = tr["vol"]
        records[f"{tid}_en"] = {"english": {"by": tr["by"], "work": tr["work"], "year": tr["year"],
                                            "links": [{"label": "sacred-texts.com", "url": f"https://sacred-texts.com/zor/{vol}/index.htm"}],
                                            "note": "Paired by chapter: the translator numbers paragraphs after Westergaard and Spiegel, not Geldner."}}
        print(f"{tid:20s} {len(chapters):3d} chapters {len(av):5d} Avestan paragraphs {len(en):5d} English")
    print("\n".join(report))
    write([BAND], rows_cat, records)


if __name__ == "__main__":
    main()
