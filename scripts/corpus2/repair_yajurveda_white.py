#!/usr/bin/env python3
"""Repair the 46 verses of yajurveda_white.json whose accented Devanagari lost characters to U+FFFD.

The accented text came from an old download in which some clusters were replaced by "�" (e.g. VS 1.2 य॒ज्ञप॑तिर�त्).
Each lost span is read back from TITUS's Mādhyandina text (Weber 1849, our vajasaneyi_samhita.json) by aligning the
two de-accented, TITUS's split words joined back: the characters TITUS has where this file has "�" go in its place,
unaccented. A span that does not align cleanly is reported and left alone. Also writes ॥ for the download's "।।".
Rerunnable (a repaired file has no "�" left to fix).

Usage: python3 -I scripts/corpus2/repair_yajurveda_white.py
"""
import difflib
import json
import os
import re

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "public", "data", "vedas")
ACC = re.compile("[॑-॔᳐-᳿꣠-ꣿ]")


def bare(s):
    """De-accented letters only, with a map from each kept character back to its index in s."""
    keep, idx = [], []
    for i, ch in enumerate(s):
        if ACC.match(ch) or ch.isspace() or ch in "।॥|ऽ'":
            continue
        keep.append("ं" if ch == "ँ" else ch)  # the accented text writes anusvāra before a sibilant as ँ (विँशति)
        idx.append(i)
    return "".join(keep), idx


# TITUS separates words, so a final consonant keeps its virāma before a word-initial vowel (म्आदि); joined, as the
# accented text writes it, that is a vowel sign (मादि).
MATRA = {"अ": "", "आ": "ा", "इ": "ि", "ई": "ी", "उ": "ु", "ऊ": "ू", "ऋ": "ृ", "ॠ": "ॄ", "ए": "े", "ऐ": "ै", "ओ": "ो", "औ": "ौ"}


def join(s):
    return re.sub("्\\s*([अआइईउऊऋॠएऐओऔ])", lambda m: MATRA[m.group(1)], s)


def main():
    path = os.path.join(DATA, "yajurveda_white.json")
    rows = json.load(open(path, encoding="utf-8"))
    titus = {e["reference"]: e.get("meaning", "") for e in json.load(open(os.path.join(DATA, "vajasaneyi_samhita.json"), encoding="utf-8"))}
    fixed, left = 0, []
    for e in rows:
        s = e.get("meaning", "").replace("।।", "॥")  # the download wrote the double daṇḍa as two single ones
        e["meaning"] = s
        if "�" not in s:
            continue
        a, ia = bare(s)
        b, _ = bare(join(titus.get(e["reference"], "")))
        edits = []
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op == "equal" or "\ufffd" not in a[i1:i2]:
                continue
            if a[i1:i2] != "\ufffd" or not b[j1:j2]:
                left.append((e["reference"], a[i1:i2], b[j1:j2]))
                continue
            edits.append((ia[i1], b[j1:j2]))
        for pos, rep in sorted(edits, reverse=True):
            s = s[:pos] + rep + s[pos + 1:]
        if edits:
            fixed += 1
            print(e["reference"], [r for _, r in edits])
        e["meaning"] = s
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"repaired {fixed} verses; not repaired: {left}")


if __name__ == "__main__":
    main()
