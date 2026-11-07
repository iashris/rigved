#!/usr/bin/env python3
"""Convert the cached Pramāṇa Purāṇas (pramana_purana_fetch.py) into public/data/puranas/*.json.

References keep Pramāṇa's native numbering, so a citation can be checked on indike.org. Its loc values mix in markers:
  * `pN` unnumbered paragraph: in Sanskrit, joined to the unit before it (or to verse 0 of its chapter); in an English
    translation, where paragraphs are the only units, it becomes the number N;
  * `N_k`, `N-k`, `NxK` repeated or starred number: joined to the verse it belongs to;
  * colophons, notes and contents tables are dropped.
A chapter number that truly repeats is kept apart as `<chapter>-rK`, so nothing is glued together. A book whose chapters
come in two runs keeps its numbers and is regrouped in one place.

Machine English from Pramāṇa goes in `text_mt`, never in `text`. Set PRAMANA_SA_WORK to the fetch's cache folder.

Usage: python3 -I scripts/corpus2/pramana_purana_convert.py [id ...]
"""

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from pramana_purana_texts import PURANAS  # noqa: E402
from pramana_sa_common import segments  # noqa: E402
from titus_to_json import iast_to_devanagari  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "public", "data", "puranas")
SKIP_KINDS = {"colophon", "note"}
MARKER = re.compile(r"^[pcn]\d+")
MAX_JOIN = 800  # characters; a longer run without verse numbers continues as <verse>-2, <verse>-3, ...


def split_loc(loc):
    """(chapter parts, verse number or None, paragraph number or None) for one Pramāṇa loc."""
    parts, para = [], None
    for p in loc.split("."):
        if MARKER.match(p):
            para = int(re.match(r"^[pcn](\d+)", p).group(1))
        else:
            parts.append(p)
    if not parts:
        return [], None, para
    m = re.match(r"^(\d+)", parts[-1])
    # A last part with a marker after it (5.12.p3) names the place the paragraph sits, so it still counts as a verse.
    if m and (len(parts) > 1 or para is not None):
        return parts[:-1], m.group(1), para
    return parts, None, para


def english_loc(loc):
    """(chapter parts, unit number) for a translation: paragraphs are its units, numbered within their chapter."""
    parts = loc.split(".")
    for i, p in enumerate(parts):
        if MARKER.match(p):
            return parts[:i], re.match(r"^[pcn](\d+)", p).group(1)
    m = re.match(r"^(\d+)", parts[-1])
    return (parts[:-1], m.group(1)) if m and len(parts) > 1 else (parts, "0")


def modal_depths(segs, english=False):
    """The usual chapter depth per top-level book, so front matter can be padded to match it. A book holding under 5%
    of the text takes the text's usual depth instead, which keeps the reader's blocks at chapter size."""
    seen = collections.defaultdict(collections.Counter)
    for s in segs:
        if not keep(s):
            continue
        if english:
            chapter = english_loc(s["loc"])[0]
            if chapter:
                seen[chapter[0]][len(chapter)] += 1
        elif re.fullmatch(r"\d+(\.\d+)+", s["loc"]):
            seen[s["loc"].split(".")[0]][s["loc"].count(".")] += 1
    total = sum(sum(v.values()) for v in seen.values())
    usual = collections.Counter()
    for v in seen.values():
        usual.update(v)
    default = usual.most_common(1)[0][0] if usual else 1
    own = {k: v.most_common(1)[0][0] for k, v in seen.items()}
    return {k: (own[k] if sum(v.values()) >= 0.05 * total else default) for k, v in seen.items()}, default, own


def stray_runs(chapters):
    """Indexes in a run of at most 2 segments that interrupts a chapter which then carries on: a numbering slip, not a move."""
    runs, stray = [], set()
    for i, ch in enumerate(chapters):
        if runs and runs[-1][0] == ch:
            runs[-1][1].append(i)
        else:
            runs.append((ch, [i]))
    for n in range(1, len(runs) - 1):
        if len(runs[n][1]) <= 2 and runs[n - 1][0] == runs[n + 1][0]:
            stray.update(runs[n][1])
    return stray


def keep(s):
    t = (s.get("text") or "").strip()
    return bool(t) and s.get("kind") not in SKIP_KINDS and not t.startswith("|")


def convert(segs, english, mt_by_loc=None):
    depth, default_depth, own = modal_depths(segs, english)
    active = []
    kept = [s for s in segs if keep(s)]
    stray = {id(kept[i]) for i in stray_runs([english_loc(s["loc"])[0] if english else split_loc(s["loc"])[0] for s in kept])}

    def shown_chapter(chapter):
        """The chapter as cited. Only a chapter number that truly repeats gets -rK; a book that comes back keeps its numbers."""
        nonlocal active
        raw = ".".join(chapter)
        if active != chapter:
            if raw in seen_ch:
                variant[raw] = variant.get(raw, 1) + 1
                stats["reopened"] += 1
            seen_ch.add(raw)
            active = chapter
        return f"{raw}-r{variant[raw]}" if raw in variant else raw

    entries, title, seen_ch, variant, stats = [], None, set(), {}, collections.Counter()
    used, cont = collections.defaultdict(set), {}
    for s in segs:
        if s.get("title") and not (s.get("text") or "").strip():
            title = s["title"]
            continue
        if s.get("kind") == "heading" and (s.get("text") or "").strip():
            title = s["text"].strip()
            continue
        if not keep(s):
            if (s.get("text") or "").strip():
                stats["dropped"] += 1
            continue
        if english:
            chapter, number = english_loc(s["loc"])
            para = None
        else:
            chapter, number, para = split_loc(s["loc"])
            if number is None:
                number = "0"
        top = chapter[0] if chapter else "0"
        want = depth.get(top, default_depth)
        # A marker shallower than its own book, or one that interrupts a chapter, belongs to the verse in progress.
        short = len(chapter) < own.get(top, 0)
        if entries and active and (id(s) in stray or (short and active[0] == top)):  # noqa: E501
            field = "text" if english else "sanskrit_iast"
            text, mt = s["text"].strip(), (mt_by_loc or {}).get(s["loc"], "").strip()
            if len(entries[-1][field]) + len(text) <= MAX_JOIN:
                entries[-1][field] += "\n" + text
                if mt:
                    entries[-1]["text_mt"] = (entries[-1].get("text_mt", "") + "\n" + mt).strip()
                stats["joined"] += 1
                continue
            base = re.sub(r"-c\d+$", "", entries[-1]["reference"])
            cont[base] = cont.get(base, 1) + 1
            e = {"reference": f"{base}-c{cont[base]}", "sanskrit_iast": "", "meaning": "", "text": ""}
            e[field] = text
            if mt:
                e["text_mt"] = mt
            entries.append(e)
            stats["continued"] += 1
            continue
        if len(chapter) < want:
            chapter = chapter + ["0"] * (want - len(chapter))
        shown = shown_chapter(chapter)
        ref = f"{shown}.{number}"
        text = s["text"].strip()
        mt = (mt_by_loc or {}).get(s["loc"], "").strip()
        field = "text" if english else "sanskrit_iast"
        joins = entries and (entries[-1]["reference"] == ref or (not english and para is not None
                                                                 and entries[-1]["reference"].startswith(shown + ".")))
        if not joins and entries and ref in used[shown]:
            joins = True
        if joins and len(entries[-1][field]) + len(text) > MAX_JOIN:
            base = re.sub(r"-c\d+$", "", entries[-1]["reference"])
            cont[base] = cont.get(base, 1) + 1
            ref, joins = f"{base}-c{cont[base]}", False
            stats["continued"] += 1
        if joins:
            entries[-1][field] += "\n" + text
            if mt:
                entries[-1]["text_mt"] = (entries[-1].get("text_mt", "") + "\n" + mt).strip()
            stats["joined"] += 1
            continue
        e = {"reference": ref, "sanskrit_iast": "", "meaning": "", "text": ""}
        e[field] = text
        if mt:
            e["text_mt"] = mt
        if title:
            e["title"] = title
            title = None
        used[shown].add(ref)
        entries.append(e)
    entries = grouped(entries)
    if not english:
        for e in entries:
            e["meaning"] = iast_to_devanagari(e["sanskrit_iast"])
    return entries, stats


def grouped(entries):
    """Keep every book and section together, in the order each first appears. The sources sometimes list a book's
    chapters in two separate runs; this puts them back in one place without touching any reference."""
    first, keys = {}, []
    for i, e in enumerate(entries):
        parts = e["reference"].split(".")[:-1]
        key = []
        for n in range(1, len(parts) + 1):
            key.append(first.setdefault(".".join(parts[:n]), len(first)))
        keys.append((key, i))
    return [entries[i] for _, i in sorted(keys, key=lambda k: k)]


def write(entries, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n")
    return os.path.getsize(path) / 1e6


def main():
    only = set(sys.argv[1:])
    for cid, t in PURANAS.items():
        if only and cid not in only:
            continue
        mt = None
        if t.get("mt"):
            mt = {s["loc"]: s["text"] or "" for s in segments(t["mt"])}
        entries, stats = convert(segments(t["sa"]), False, mt)
        size = write(entries, cid)
        n_mt = sum(1 for e in entries if e.get("text_mt"))
        print(f"{cid}: {len(entries)} entries, {size:.1f} MB, machine English {n_mt}, {dict(stats)}", flush=True)
        if t.get("en"):
            name = f"{cid}_{t['en_name'].lower().replace(' ', '')}"
            entries, stats = convert(segments(t["en"]), True)
            size = write(entries, name)
            print(f"{name}: {len(entries)} entries, {size:.1f} MB, {dict(stats)}", flush=True)


if __name__ == "__main__":
    main()
