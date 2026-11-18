#!/usr/bin/env python3
"""Jamison & Brereton, The Rigveda: The Earliest Religious Poetry of India (OUP 2014) -> public/data/vedas/rigveda_jamison_brereton.json.

The source is the publisher's born-digital PDF (three volumes in one file), so the text layer is real Unicode and no
OCR is involved. pdftotext -bbox-layout gives each word with its position, which settles what plain extraction gets
wrong: an accent drawn as its own glyph ("vā́ ja") sits inside a word, not after a space, and a verse's wrapped line
hangs further in than its next half-verse.

One entry per verse, keyed by the standard maṇḍala.hymn.verse (the Vālakhilya hymns are VIII.49-59, as in the
Sanskrit). The first verse of each hymn carries `title` (the deity, from the book's Anukramaṇī table, whose plain font
kept its diacritics where the display-font headings did not) and `about`: poet, meter, which translator made the
final version, the hymn's introduction and any preface to its maṇḍala or group of hymns.

Checks, printed rather than patched: verses per hymn against each hymn's own "N verses" line (three headers in the
book are misprinted: I.64 says 14 for 15, I.94 says 6 for 16, X.16 says 24 for 14), and hymns per maṇḍala.

Usage: python3 -I scripts/corpus2/jamison_brereton_rv.py <path to the PDF>
"""
import collections
import html
import json
import os
import re
import statistics
import subprocess
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "public", "data", "vedas", "rigveda_jamison_brereton.json")
WORK = os.path.join(ROOT, "cache", "jamison_brereton")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
HYMNS = [191, 43, 62, 58, 87, 75, 104, 103, 114, 191]
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')
HEAD = re.compile(r"^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.(\d+)\b\s*(?:\((\d+)\))?\s*(.*)$")
VCOUNT = re.compile(r"^(\d+) ver\w*\b")
MARK = "[\u0300-\u036f]"
# The display font scatters the diacritics of a maṇḍala title: "Mạnd ala V", "Mand ala II".
MANDALA_TITLE = re.compile(r"M\S*\s?\S*ala [IVX]+")


def clean(s):
    s = s.replace("\ufeff", "").replace("\u200c", "").replace("\u00ad", "").replace("\u2009", " ")
    # Dotless i carrying a detached accent or macron: "Sarasvatı ̄", "Rātrı,̄"
    s = re.sub(r"ı ?(" + MARK + ")", r"i\1", s)
    s = re.sub(r"ı([,.;:)’”])(" + MARK + ")", r"i\2\1", s)
    s = s.replace("ı", "i")
    # A mark drawn one letter late, the word split after it: "Pavaman̄ a" → "Pavamāna", "Asv́ ins" → "Aśvins".
    # Only the acute and macron drift so: a ring below after r is syllabic r̥ in place ("Vr̥ tra"), handled further down.
    s = re.sub(r"([A-Za-z])([b-df-hj-np-tv-z])([\u0301\u0304]) (?=[a-z" + MARK[1:-1] + "])", r"\1\3\2", s)
    # A mark floating before its letter's word part: "Pūs ̣an", "Vis ̣ṇu"
    s = re.sub(r"(\w) (" + MARK + r")(?=\w)", r"\1\2", s)
    # Syllabic r̥ split from the rest of its word: "R̥ gveda", "tr̥ ca"
    s = re.sub(r"([rR]\u0325) (?=[a-zāīūṛṣṇśṭḍḥṃ])", r"\1", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = unicodedata.normalize("NFC", s).strip()
    # Accented syllabic r̥ (ŕ̥) twice comes apart beyond the rules above; both are in introductions.
    for a, b in (("r\u00b4\u0325 c", "r\u0325\u0301c"), ("nr\u0301pati\u0325", "nr\u0325\u0301pati")):
        s = s.replace(unicodedata.normalize("NFC", a), unicodedata.normalize("NFC", b))
    return s


def join_words(ws):
    gaps = [b[0] - a[2] for a, b in zip(ws, ws[1:])]
    med = statistics.median(gaps) if gaps else 3.0
    out = ws[0][4]
    for (a, b), g in zip(zip(ws, ws[1:]), gaps):
        out += ("" if g < min(1.7, 0.65 * med) else " ") + b[4]
    return out


def read_pages(path):
    t = open(path, encoding="utf-8").read()
    for pm in re.finditer(r"<page[^>]*>(.*?)</page>", t, re.S):
        ws = []
        for lm in re.finditer(r"<line[^>]*>(.*?)</line>", pm.group(1), re.S):
            for a, b, c, d, w in WORD.findall(lm.group(1)):
                w = html.unescape(w)
                if w.strip():
                    ws.append((float(a), float(b), float(c), float(d), w))
        # Rebuild lines by baseline: pdftotext sometimes splits "1." from its verse.
        ws.sort(key=lambda w: (round(w[3]), w[0]))
        lines = []
        for w in ws:
            if lines and abs(lines[-1][-1][3] - w[3]) < 2.0:
                lines[-1].append(w)
            else:
                lines.append([w])
        out = []
        for lw in lines:
            lw.sort(key=lambda w: w[0])
            # A lone accent drawn above a heading word belongs to that heading, not a line of its own.
            if all(re.fullmatch(MARK + "+", w[4]) for w in lw):
                continue
            out.append({"x": lw[0][0], "x2": lw[1][0] if len(lw) > 1 else None, "y": lw[0][3], "words": lw, "text": join_words(lw)})
        yield out


def body_lines(pages):
    """Every line from I.1 to the end of X.191, with page-relative indent and a gap flag."""
    started = False
    for pno, lines in enumerate(pages, 1):
        lines = [l for l in lines if l["y"] > 42]  # running header (hymn ref + page number)
        if not lines:
            continue
        margin = 63.0 if pno % 2 else 54.0
        prev_y = None
        for l in lines:
            text = clean(l["text"])
            if not started:
                # Begin at the Maṇḍala I title page (after "Volume I", p. 102), so its introduction comes along as I.1's preface.
                if pno > 102 and MANDALA_TITLE.fullmatch(text) or re.match(r"^I\.1 Agni$", text):
                    started = True
                else:
                    continue
            if re.match(r"^Deities and Poets of the R", text):
                return
            if re.fullmatch(r"\d+", text) and l["y"] > 600:
                continue  # folio at the foot of a chapter-opening page
            gap = prev_y is not None and l["y"] - prev_y > 17.0
            prev_y = l["y"]
            yield {"page": pno, "d": l["x"] - margin, "d2": (l["x2"] - margin) if l["x2"] is not None else None, "y": l["y"], "text": text, "gap": gap,
                   "top": prev_y == l["y"] and gap is False and l is lines[0], "raw": l["text"]}


def appendix(pages):
    """Deity and poet per hymn from the closing table, whose plain font kept its diacritics; "____" repeats the row above."""
    rows, on = {}, False
    last = None
    for pno, lines in enumerate(pages, 1):
        margin = 63.0 if pno % 2 else 54.0
        for l in lines:
            if l["y"] < 42:
                continue
            if re.match(r"^Deities and Poets of the R", clean(l["text"])):
                on = True
                continue
            if not on:
                continue
            ws = l["words"]
            left = [w for w in ws if w[0] < margin + 150]
            right = [w for w in ws if w[0] >= margin + 150]
            first = left[0][4] if left else ""
            hm = re.fullmatch(r"(I|II|III|IV|V|VI|VII|VIII|IX|X)\.(\d+)", first)
            if hm and left[0][0] < margin + 5:
                last = (ROMAN.index(hm.group(1)) + 1, int(hm.group(2)))
                rows[last] = [clean(join_words(left[1:])) if len(left) > 1 else "", clean(join_words(right)) if right else ""]
            elif last and left and left[0][0] >= margin + 10 and not re.fullmatch(r"M.*", clean(join_words(left))):
                rows[last][0] += " " + clean(join_words(left))
                if right:
                    rows[last][1] += " " + clean(join_words(right))
            elif last and right and not left:
                rows[last][1] += " " + clean(join_words(right))
    prev = ["", ""]
    out = {}
    for k in sorted(rows):
        d, p = rows[k]
        d = prev[0] if d.strip() == "____" else d.strip()
        p = prev[1] if p.strip() == "____" else p.strip()
        out[k] = (d, p)
        prev = [d, p]
    return out


# Each hymn's final version is one translator's (Introduction, "Hymn Distribution by Translator"). Brereton's share
# is listed; every other hymn is Jamison's.
JPB = {1: "1, 24-25, 32, 46-47, 116-120, 157-158, 161, 164-165, 170-171", 2: "11-24, 27-28, 39", 3: "1-7, 9-29, 58-60",
       4: "33-37, 42", 5: "1-28, 62-78, 85", 7: "1-17, 48, 50-52, 60-74, 82-89", 10: "71-72, 81-82, 90, 108, 121, 129-130"}


def translator(m, h):
    for part in JPB.get(m, "").split(","):
        if not part.strip():
            continue
        a, _, b = part.strip().partition("-")
        if int(a) <= h <= int(b or a):
            return "Joel P. Brereton"
    return "Stephanie W. Jamison"


def entries(hymns):
    out = []
    for hy in hymns:
        for n, v in enumerate(hy["verses"], 1):
            e = {"reference": f"{hy['m']:02d}.{hy['h']:03d}.{n:02d}", "text": v, "mandala": hy["m"], "hymn": hy["h"], "verse": n}
            if n == 1:
                e["title"] = hy["title"]
                about = {"poet": hy["poet"], "meter": hy["meter"], "by": translator(hy["m"], hy["h"]), "intro": hy["intro"]}
                if hy["pre"]:
                    about["preface"] = hy["pre"]
                e["about"] = about
            out.append(e)
    return out


def main(src, dst):
    pages = list(read_pages(src))
    table = appendix(pages)
    lines = list(body_lines(pages))
    hymns = []
    m, h = 1, 0
    cur = None
    mode = None  # head | intro | verse | tail
    pending_pre = []
    problems = []

    def expected():
        nxt = [(m, h + 1)] if h < HYMNS[m - 1] else []
        if m < 10:
            nxt.append((m + 1, 1))
        return nxt

    i = 0
    while i < len(lines):
        l = lines[i]
        t = l["text"]
        hm = HEAD.match(t)
        if hm and l["d"] < 4:
            mm, hh = ROMAN.index(hm.group(1)) + 1, int(hm.group(2))
            # A real heading is the next hymn in sequence and is followed within a few lines by "N verses".
            look = [x["text"] for x in lines[i + 1 : i + 8]]
            if (mm, hh) in expected() and any(VCOUNT.match(x) for x in look):
                m, h = mm, hh
                title = [hm.group(4)]
                j = i + 1
                # Heading continuation lines sit before the poet line; the poet line precedes "N verses".
                vline = next(k for k in range(i + 1, i + 8) if VCOUNT.match(lines[k]["text"]))
                head_rest = [lines[k]["text"] for k in range(i + 1, vline)]
                poet = head_rest[-1] if head_rest else ""
                title += head_rest[:-1]
                meter = [lines[vline]["text"]]
                j = vline + 1
                while j < len(lines) and not lines[j]["gap"] and not re.match(r"^1\.\s", lines[j]["text"]):
                    meter.append(lines[j]["text"])
                    j += 1
                cur = {"m": m, "h": h, "grassmann": hm.group(3), "title": " ".join(title).strip(), "poet": poet, "meter": " ".join(meter),
                       "nverses": int(VCOUNT.match(meter[0]).group(1)), "pre": pending_pre, "intro": [], "verses": []}
                pending_pre = []
                hymns.append(cur)
                mode = "intro"
                i = j
                continue
        if cur is None:
            pending_pre.append(l)
            i += 1
            continue
        vm = re.match(r"^(\d+)\.\s*(.*)$", t)
        nextv = len(cur["verses"]) + 1
        # In an introduction a wrapped line can begin "1." ("…mentioned in verse / 1. This solution…", V.84). The hymn's
        # first verse is set off by space above it, opens a page, or has its next line hanging indented (III.52 has no space).
        first_verse = nextv == 1 and (l["gap"] or l["top"] or i + 1 < len(lines) and lines[i + 1]["d"] >= 8)
        if mode == "intro" and i and re.search(r"\b(verses?|vss?\.)$", lines[i - 1]["text"]):
            first_verse = False
        if vm and l["d"] < 8 and int(vm.group(1)) == nextv and (mode != "intro" or first_verse):
            if mode == "tail":
                # Prose was taken to have begun, yet another verse follows: the previous verse may have lost lines to it.
                problems.append(f"{ROMAN[cur['m']-1]}.{cur['h']}.{nextv}: verse follows text read as prose; check verse {nextv - 1}")
            cur["verses"].append({"lines": [("start", vm.group(2))], "meta": [l], "num_d2": l["d2"]})
            mode = "verse"
            i += 1
            continue
        if mode == "verse":
            v = cur["verses"][-1]
            text_d = v["num_d2"] if v["num_d2"] is not None else 10.0
            if l["d"] < 8:
                # Verse lines hang from their number; a line back at the margin is prose after the last verse,
                # the introduction to the next group of hymns or maṇḍala. Its first line may be indented like a
                # half-verse, so hand back everything from the last vertical gap.
                back = [k for k in range(1, len(v["lines"])) if v["meta"][k]["gap"]]
                if back:
                    k = back[-1]
                    pending_pre.extend(v["meta"][k:])
                    del v["lines"][k:], v["meta"][k:]
                mode = "tail"
                pending_pre.append(l)
                i += 1
                continue
            kind = "cont" if l["d"] >= text_d + 6 else "line"
            v["lines"].append((kind, t))
            v["meta"].append(l)
            i += 1
            continue
        if mode == "tail":
            pending_pre.append(l)
            i += 1
            continue
        cur["intro"].append(l)
        i += 1

    if pending_pre and hymns:
        hymns[-1]["post"] = pending_pre

    # Hyphen decisions from the whole text: keep "soma-presser", join "com-bination".
    vocab = collections.Counter(w.lower() for l in lines for w in re.findall(r"[\w’-]+", l["text"]))

    def join_hyphen(a, b, prose):
        """Line-end hyphen: keep it if the hyphenated compound is the book's usual spelling; drop it for a word break."""
        m1 = re.search(r"([\w’]+)-$", a)
        m2 = re.match(r"([\w’]+)", b)
        if not m1 or not m2:
            return a + b
        left, right = m1.group(1).lower(), m2.group(1).lower()
        hy, joined = vocab[left + "-" + right], vocab[left + right]
        if hy > joined:
            return a + b
        if joined > hy:
            return a[:-1] + b
        # Unseen either way: the prose is justified, so a break there is usually the typesetter's; verse lines are ragged.
        return a[:-1] + b if prose else a + b

    def run_on(parts, prose=False):
        s = ""
        for p in parts:
            if not s:
                s = p
            elif s.endswith("-"):
                s = join_hyphen(s, p, prose)
            elif s.endswith("—") or s.endswith("/"):
                s += p
            else:
                s += " " + p
        return s

    def para_text(ls):
        paras, buf = [], []
        for l in ls:
            if buf and (l["gap"] or l["d"] >= 8):
                paras.append(run_on([b["text"] for b in buf], True))
                buf = []
            buf.append(l)
        if buf:
            paras.append(run_on([b["text"] for b in buf], True))
        return "\n\n".join(p for p in paras if p)

    out = []
    for hy in hymns:
        verses = []
        for v in hy["verses"]:
            rows = []
            for kind, txt in v["lines"]:
                if kind == "cont" and rows:
                    rows[-1].append(txt)
                else:
                    rows.append([txt])
            verses.append("\n".join(run_on(r) for r in rows))
        nv = len(verses)
        if nv != hy["nverses"]:
            problems.append(f"{ROMAN[hy['m']-1]}.{hy['h']}: header says {hy['nverses']} verses, parsed {nv}")
        deity, poet = table.get((hy["m"], hy["h"]), ("", ""))
        if not deity or not poet:
            problems.append(f"{ROMAN[hy['m']-1]}.{hy['h']}: missing from the deities-and-poets table")
        # The maṇḍala title page ("V", "Maṇḍala V") opens a maṇḍala's preface: drop the title lines themselves.
        pre = [p for p in para_text(hy["pre"]).split("\n\n") if not (re.fullmatch(r"[IVX]+", p.strip()) or MANDALA_TITLE.fullmatch(p.strip()))]
        out.append({"m": hy["m"], "h": hy["h"], "grassmann": hy["grassmann"], "title": deity, "heading": clean(hy["title"]), "poet": poet,
                    "meter": hy["meter"], "nverses": hy["nverses"], "pre": "\n\n".join(pre), "intro": para_text(hy["intro"]), "verses": verses})
    per = collections.Counter(h["m"] for h in out)
    for k in range(1, 11):
        if per[k] != HYMNS[k - 1]:
            problems.append(f"Maṇḍala {k}: {per[k]} hymns, expected {HYMNS[k-1]}")
    json.dump(entries(out), open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{len(out)} hymns, {sum(len(h['verses']) for h in out)} verses")
    print(f"{len(problems)} problems")
    for p in problems:
        print(" ", p)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    os.makedirs(WORK, exist_ok=True)
    bbox = os.path.join(WORK, "bbox.xhtml")
    if not os.path.exists(bbox):
        subprocess.run(["pdftotext", "-bbox-layout", sys.argv[1], bbox], check=True)
    main(bbox, OUT)
