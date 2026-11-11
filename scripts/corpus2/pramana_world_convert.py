#!/usr/bin/env python3
"""Convert the cached English of pramana_world_texts into public/data/<dir>/<id>.json.

Entries are {"reference", "text", "title"?}: English only, no original-language fields. A reference is the source's own
chapter numbering plus a paragraph counted from 1 in reading order within it (Jātaka 316.4 is the fourth paragraph of
Jātaka 316); Pramāṇa's paragraph locs carry gaps and split paragraphs, so they are not kept. The Rājataraṅgiṇī is the
exception: its references are Kalhaṇa's book and verse numbers, read from Stein's text.

Translators' footnotes are left out, as are page markers ([95.], [p. 12]), footnote marks and running heads. Pramāṇa's
Milindapañha misfiles books IV–VI; they are put back in Rhys Davids's order (see milinda_book).

Set PRAMANA_SA_WORK to the fetch's cache folder.
Usage: python3 -I scripts/corpus2/pramana_world_convert.py [id ...]
"""
import collections
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pramana_sa_common import segments  # noqa: E402
from pramana_world_texts import WORLD  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data")
HEADING_KINDS = {"jataka", "lambaka", "taranga", "section", "book", "chapter"}
# How many numeric loc parts name a chapter, per text; deeper parts are paragraphs.
CHAPTER_DEPTH = {"jataka_cowell": 1, "kathasaritsagara_tawney": 2, "mahavamsa_geiger": 1, "milindapanha_rhysdavids": 2,
                 "faxian_legge": 1, "xuanzang_beal": 2, "xuanzang_life_beal": 1}

PAGE = re.compile(r"\[(?:p(?:age|\.)?\s*)?\d+[a-z]?\.?\]", re.I)  # [95.] [329] [p. 12] [Page 4] and numeric note marks [1]
SITE_MARK = re.compile(r"\{[A-Z_]+::[^}]*\}")  # wisdomlib's {GL_NOTE::}


def clean(t):
    t = SITE_MARK.sub("", t)
    t = PAGE.sub("", t)
    t = re.sub(r"\[\d{1,4}[.;]?\d?[\]1](?=\s|$)", "", t)  # OCR'd page marks: [23.7] [30;3] [3561
    t = re.sub(r"_{3,}", "", t)
    t = t.replace("[*]", "").replace("**", "")
    t = re.sub(r"(?<![\w_])_(?=\S)([^_\n]+?)(?<=\S)_(?![\w_])", r"\1", t)  # _italic_ markdown
    t = re.sub(r"(?<![\w*])\*(?=\S)|(?<=\S)\*(?![\w*])", "", t)  # *italic* markdown
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r" ([,;:.!?])", r"\1", t)
    return t.strip()


def is_note(s):
    return s.get("kind") == "note" or re.search(r"(^|\.)n\d+", s["loc"]) is not None


def numeric_parts(loc):
    """Leading chapter numbers of a loc, stopping at the first paragraph marker: '4.5-2' -> ['4', '5-2']."""
    out = []
    for p in loc.split("."):
        if re.match(r"^[pn]\d", p):
            break
        out.append(p)
    return out


def num(p):
    return re.match(r"^\d+", p).group(0)


def milinda_book(s, key, loose):
    """Pramāṇa files Rhys Davids's book IV chapters 1–4 under 'Book VI', and books V (the problem of inference, from
    Trenckner p. 329) and VI (the ascetic practices, from p. 348) as loose paragraphs 4.1, 4.2, ... after book IV's
    chapter 8, with '-2' added wherever a number was already taken. Book VI starts where that numbering starts again.
    `loose` carries [book, last number] across calls."""
    parts = numeric_parts(s["loc"])
    if parts[0] == "6" and key is not None:
        return ["4"] + key[1:]
    if parts[0] == "4" and len(parts) == 2 and s.get("kind") != "chapter":
        n = int(num(parts[1]))
        if loose[0] is None or n < loose[1]:
            loose[0] = "5" if loose[0] is None else "6"
        loose[1] = n
        return [loose[0], "0"]
    return key


MILINDA_BOOKS = {"5": "Book V: The Problem of Inference", "6": "Book VI: The Ascetic Practices"}


def chaptered(cid, segs):
    depth = CHAPTER_DEPTH[cid]
    has_kids = {".".join(s["loc"].split(".")[:-1]) for s in segs if not is_note(s)}
    entries, key, title, count, loose = [], None, None, collections.Counter(), [None, 0]
    seen = {}
    for s in segs:
        if is_note(s):
            continue
        loc = s["loc"]
        if cid == "mahavamsa_geiger" and loc.split(".")[0] == "0":
            continue  # wisdomlib's own preface and Turnour's introduction, not Geiger
        if (s.get("title") or "").startswith("NOTE ") and re.search(r"_\d+$", loc):
            continue  # Beal's appended notes
        parts = numeric_parts(loc)
        text = clean(s.get("text") or "")
        structural = len(parts) <= depth and (s.get("kind") in HEADING_KINDS or bool(s.get("title")) or (not text and loc in has_kids))
        here = key
        if structural:
            key = [num(p) for p in parts] + ["0"] * (depth - len(parts))
            if cid == "milindapanha_rhysdavids":
                key = milinda_book(s, key, loose)
            here = key
            own = clean(s.get("title") or "")
            if cid == "milindapanha_rhysdavids" and own.startswith("Book VI: The Solving"):
                own = "Book IV: The Solving of Dilemmas"
            # A book heading straight before its first chapter heading: keep both.
            title = (f"{title} · {own}" if title and own else own or title)
        elif cid == "milindapanha_rhysdavids" and numeric_parts(loc)[0] == "4" and len(numeric_parts(loc)) == 2:
            here = milinda_book(s, key, loose)
        if not text or re.fullmatch(r"CHAPTER \d+\.", text):
            continue
        if not structural and here is key and count[".".join(here)] == 0 and not title and re.match(r"^CHAPTER [IVXLC]+\.", text) and text.upper() == text:
            title = text  # Faxian's last chapter carries its heading as a paragraph
            continue
        if here is None:
            raise SystemExit(f"{cid}: paragraph before any chapter at {loc}")
        ch = ".".join(here)
        twin = re.search(r"(\.p\d+)-\d+$", loc)
        if twin and difflib.SequenceMatcher(None, seen.get(loc[: twin.start()] + twin.group(1), ""), text).ratio() > 0.95:
            continue  # a second copy of a run of paragraphs (Mahāvaṃsa 37), filed under 'pN-2'
        seen[loc] = text
        count[ch] += 1
        e = {"reference": f"{ch}.{count[ch]}", "text": text}
        if here is key and title:
            e["title"] = title
            title = None
        elif here is not key and count[ch] == 1 and here[0] in MILINDA_BOOKS:
            e["title"] = MILINDA_BOOKS[here[0]]
        entries.append(e)
    return entries


VERSE = re.compile(r"^(\[|†\s*)?(\d+)(?:\s*[-–]\s*(\d+))?(?:\.\s+(?=\S)|\s+(?=[A-Z\"“‘]))")
# Stein's own notes, by the way they cite: "comp. viii. 3356", "l.c.", "K." for Kalhaṇa, manuscript sigla.
NOTEY = re.compile(r"\b(?:comp|l\.c|Prof|cf)\.|\b[ivx]+\.\s?\d+|\bK\.\s|J\.A\.S\.B|Rājat\.|A[₁₂_]|Bühler|identif")
FOOTNOTE = re.compile(r"^\*\*\d+(?:\s*[-–]\s*\d+)?\.?\*\*")
ENDS = re.compile(r"[.!?…][\"'’”)\]]*\s*$")
DROPPED, JOINED = [], []
NOT_KINGS = ("INTRODUCTION", "REVERENCE", "RĀJATARAṄGIṆĪ", "APPENDICES")


def king(head):
    """'PRAVARASENA II.' -> 'Pravarasena II'."""
    return " ".join(w if re.fullmatch(r"[IVX]+", w) else w.capitalize() for w in head.rstrip(".").split())


def rajatarangini(segs):
    """Stein's verses are the paragraphs that open with Kalhaṇa's number ('30.', '9-10.', '1460-62.', '[361-386.' for
    his bracketed summary of verses he condenses, '† 343.' for a lost verse). A verse broken by a page runs on in the next paragraph, which joins it
    only while it is unfinished. The few footnotes that came through ('**30.** By the name of Nāga ...') are dropped,
    page heads too ('INTRODUCTION.'), except the king's name a page is headed with, which becomes the next verse's title."""
    entries, book, mode, title, last_head = [], None, None, None, None
    expect = 0
    # A paragraph sometimes holds several verses, one per line: split it so each verse is its own unit.
    units = []
    for s in segs:
        t = re.sub(r"\\([.*_\[\]#()'-])", r"\1", (s.get("text") or "").strip())
        head = re.match(r"^([A-ZĀĪŪṚṜḶṢṆŚḌṬÑṄṀṂ'-]+(?: [A-ZĀĪŪṚṜḶṢṆŚḌṬÑṄṀṂ'-]+)*\.)\s+(?=\d)", t)
        if head:  # 'MEGHAVĀHANA. 2. Then the subjects ...'
            units.append((s, head.group(1)))
            t = t[head.end():]
        for part in re.split(r"\n(?=(?:\[|†\s*)?\d+(?:\s*[-–]\s*\d+)?\.\s)|(?<=[.!?\"”’])\s+(?=\d+(?:\s*[-–]\s*\d+)?\.\s+[\"“‘A-Z])", t):
            units.append((s, part.strip()))
    segs, texts = [u[0] for u in units], [u[1] for u in units]
    for i, s in enumerate(segs):
        raw = texts[i]
        if s.get("kind") == "section" and not raw:
            book, mode, expect = num(s["loc"]), None, 0
            title = king(clean(s.get("title") or ""))
            continue
        if not raw:
            continue
        if FOOTNOTE.match(raw):
            mode = "note"
            continue
        m = VERSE.match(raw)
        n, to = (int(m.group(2)), m.group(3)) if m else (0, None)
        if to and int(to) < n:  # "1460-62."
            to = m.group(2)[: len(m.group(2)) - len(to)] + to
        if m and (expect < n <= expect + 40 or (to and n <= expect < int(to))):
            shown = n
            n = max(n, expect + 1)  # '3435-3439.' after '3431-3435.': cited from the first verse not yet given
            text = clean(raw[m.end():])
            if m.group(1) == "[" and text.endswith("]"):
                text = "[" + text  # Stein's summary of verses he condenses
            elif m.group(1):
                text = "† " + text  # a verse lost in the manuscripts
            if to:
                text = f"({shown}–{to}) " + text
            e = {"reference": f"{book}.{n}", "text": text}
            if title:
                e["title"] = title
                title = None
            entries.append(e)
            mode, expect = "verse", int(to or n)
            continue
        text = clean(raw)
        words = text.split()
        if not re.search(r"[a-zāīūṛṣṇśḍṭñ]", text) and len(words) <= 8:
            if not any(w in text for w in NOT_KINGS) and king(text) != last_head:
                title = last_head = king(text)
            continue
        nxt = texts[i + 1] if i + 1 < len(segs) else ""
        if len(words) <= 6 and text[0].isupper() and text.endswith(".") and VERSE.match(nxt):
            title = text.rstrip(".")
            continue
        # Inside a run of verses an unnumbered paragraph is the verse going on, unless it reads like Stein's note;
        # after a note it is the verse going on only if that verse was left unfinished.
        if entries and not NOTEY.search(text) and (mode == "verse" or not ENDS.search(entries[-1]["text"])):
            entries[-1]["text"] += " " + text
            JOINED.append((s["loc"], text))
            continue
        mode = "note"  # the rest of a note carried over from the page before, or a colophon
        DROPPED.append((s["loc"], text))
    return entries


def validate(cid, entries):
    refs = [e["reference"] for e in entries]
    dup = [r for r, c in collections.Counter(refs).items() if c > 1]
    if dup:
        raise SystemExit(f"{cid}: duplicate references {dup[:10]}")
    keys = [tuple(int(x) for x in r.split(".")) for r in refs]
    if keys != sorted(keys):
        bad = next(i for i in range(1, len(keys)) if keys[i] < keys[i - 1])
        raise SystemExit(f"{cid}: out of order at {refs[bad - 1]} -> {refs[bad]}")
    if len({len(k) for k in keys}) != 1:
        raise SystemExit(f"{cid}: mixed reference depths {collections.Counter(len(k) for k in keys)}")
    left = [(e["reference"], m) for e in entries for m in re.findall(r"\[\d+\.?\]|\{[A-Z_]+::|\[\*\]|\[back to top\]", e["text"])]
    if left:
        raise SystemExit(f"{cid}: markers left {left[:10]}")


def write(entries, folder, name):
    out = os.path.join(DATA, folder)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n")
    return os.path.getsize(path) / 1e6


def main():
    only = set(sys.argv[1:])
    for cid, t in WORLD.items():
        if only and cid not in only:
            continue
        segs = segments(t["en"])
        entries = rajatarangini(segs) if cid == "rajatarangini_stein" else chaptered(cid, segs)
        if not entries:
            raise SystemExit(f"{cid}: no entries")
        entries.sort(key=lambda e: tuple(int(x) for x in e["reference"].split(".")))
        validate(cid, entries)
        words = sum(len(e["text"].split()) for e in entries)
        size = write(entries, t["dir"], cid)
        print(f"{cid}: {len(entries)} entries, {words} words, {size:.1f} MB, {entries[0]['reference']} .. {entries[-1]['reference']}", flush=True)


if __name__ == "__main__":
    main()
