#!/usr/bin/env python3
"""Convert cached Pramāṇa segments into corpus JSON (one entry per smallest natively numbered unit) for:
Baudhāyana Śrautasūtra, five Śulbasūtras, the three Jyotiṣa recensions, Piṅgala's Chandaḥsūtra and the
Atharvaveda Pariśiṣṭas. (The Sarvānukramaṇī has its own script, pramana_sa_sarvanukramani.py.)

Pramāṇa's `loc` mirrors its source e-text's numbering, with its own additions:
  * lettered children (1.1.1.a) are lines of one numbered unit; `.pN` children are unnumbered paragraphs -> joined;
  * `N-k` / `N_k` mark a repeated number in the source (k-th occurrence) -> joined to the unit before;
  * colophons and editorial notes are separate segments -> dropped.
Numbering slips in the sources are repaired conservatively and every merge is counted and printed.

Usage: python3 -I scripts/corpus2/pramana_sa_convert.py [name ...]
"""

import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from pramana_sa_common import WORK, page, segments  # noqa: E402
from pramana_sa_texts import TEXTS  # noqa: E402
from titus_to_json import iast_to_devanagari  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "public", "data")
SKIP_KINDS = {"colophon", "note"}


def jyotisa_atharva_prepare(segs):
    """Pramāṇa's numbers here are a running count over an OCR'd edition. The verses end in their own '..N..'
    numbers and the prakaraṇas start at '[k]' headings, so rebuild prakaraṇa.verse: an unnumbered verse takes
    the next number; apparatus lines (sigla, bullets), closing titles and front matter before '[1]' are dropped."""
    prak, last = 0, 0
    for s in segs:
        t = (s["text"] or "").strip()
        m = re.fullmatch(r"\[\s*(\d+)\s*\]", t)
        if m:
            prak, last = int(m.group(1)), 0
            s["text"] = None
            continue
        if (not prak or re.search(r"[●•©]|\(!\)|\b[A-Z]{1,3}\b|prakaraṇam\s*\.\.\s*\d+\s*\.\.", t)
                or len(re.findall(r"[a-zāīūṛṃḥśṣṇṭḍñṅ]", t)) < 12):
            s["text"] = None
            continue
        m = re.search(r"\.\.\s*(\d+)\s*\.\.", t)
        if m and int(m.group(1)) > last:
            last = int(m.group(1))
        elif "\n" in t:
            last += 1
        else:
            s["_loc"] = f"{prak}.p"
            continue
        s["_loc"] = f"{prak}.{last}"
    return segs


CFG = {
    # Caland's edition is cited praśna.kaṇḍikā:page.line, which is Pramāṇa's 4-level loc. The Pravarādhyāya
    # appendix ('Pr', not numbered into the praśnas) and the editor's footnotes ('Fn') are left out.
    "baudhayana_srautasutra": dict(D=4, drop=r"^Pr|Fn"),
    "baudhayana_sulbasutra": dict(D=2),
    "katyayana_sulbasutra": dict(D=2),
    "manava_sulbasutra": dict(D=2, verse_num=True),  # verses 'v-7a' share the khaṇḍa's sūtra numbering
    "maitrayana_sulbasutra": dict(D=2, drop=r"^0\."),
    # Praśna 25 of the Hiraṇyakeśi corpus. After paṭala 6 sūtra 71 the file appends the 445
    # 'cayanopayogikārikāḥ' (a separate verse work with its own numbering): left out.
    "hiranyakesin_sulbasutra": dict(D=3, drop=r"^25\.0\.", stop_after="25.6.71"),
    "jyotisa_rk": dict(D=1),
    "jyotisa_yajus": dict(D=1),
    "jyotisa_atharva": dict(D=2, prepare=jyotisa_atharva_prepare),
    # Adhyāya 8 ends at sūtra 35; what follows is a later pariśiṣṭa on Prakrit metres: left out.
    "pingala_chandahsutra": dict(D=2, drop=r"^0\.", stop_after="8.35"),
    # The lettered sub-pariśiṣṭas (1b, 18b, 18c, 19b, 30b, 58b, 70b, 70c; Pramāṇa locs 'P_k') need letters in
    # their references, which our schema cannot hold: left out and reported.
    "atharvaveda_parisista": dict(D=3, drop=r"^\d+_\d+$"),
}


# ---------------------------------------------------------------- text cleaning
ACCENTS = {"̱": "॒", "̍": "॑", "̎": "᳚"}


def clean(t):
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"</?(?:sic|corr|note|lb|pb)[^>]*>", " ", t)
    t = t.replace("<", " ").replace(">", " ")  # Pramāṇa marks quoted mantras with <...>: keep the words
    t = re.sub(r"\[[^\]]*(?:\d|cf\.|ed\.|sic)[^\]]*\]", " ", t)  # [cf. 3,15], [350]: apparatus
    t = t.replace("[", "").replace("]", "")  # editorial insertions / restorations: keep the words
    t = re.sub(r"\([^)]*\d[^)]*\)", " ", t)
    t = re.sub(r"\((?:mantrāḥ|sic)[^)]*\)|\([^)]*\?[^)]*\)", " ", t)
    t = t.replace("(", " ").replace(")", " ")
    t = re.sub(r"\S*[A-Z]\S*", " ", t)  # sigla and markers (F, TSan): never Sanskrit in IAST
    t = t.replace("``", " ").replace("''", " ").replace("^", "").replace("}", "").replace("{", "")
    t = re.sub(r"\.{3,}", " … ", t)  # lacuna
    t = t.replace("..", " || ")
    t = re.sub(r"\s*\.(?=\s|$)", " |", t)  # full stop used as daṇḍa
    t = t.replace(".", " ")
    t = re.sub(r"-{2,}|—+|–+", " ", t)
    t = t.replace("\\\\", " || ").replace("\\", " | ")
    t = t.replace("//", " || ").replace("/", " | ")
    t = re.sub(r"(?<=[a-zāīūṛṝḷḹṃḥñṅṇṭḍśṣ̀-ͯ])3", "\x01", t)  # pluti 3: keep
    t = re.sub(r"\d+", " ", t).replace("\x01", "3")
    t = re.sub(r"[_*#=]", " ", t)
    t = re.sub(r"\|\s*\|", "||", t)
    t = re.sub(r"\|{3,}", "||", t)
    t = re.sub(r"(\|\|?\s*)+\|\|", "||", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(\|\|?\s*)+", "", t).strip()
    t = re.sub(r"\s*,\s*", ", ", t)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", t).strip())


def deva(iast):
    out = iast_to_devanagari(iast)
    for k, v in ACCENTS.items():
        out = out.replace(k, v)
    out = re.sub("म्̐", "ँ", out).replace("̐", "ँ")
    out = out.replace("||", "॥").replace("|", "।").replace("3", "३")
    return unicodedata.normalize("NFC", out)


# ---------------------------------------------------------------- structure
NUM = re.compile(r"(\d+)([a-z]?)")
DUP = re.compile(r"(\d+)[-_](\d+)")


def key_of(loc, D, verse_num=False):
    """(numeric key up to D levels, is_repeat). A key shorter than D means 'unnumbered, join to a unit'."""
    key, cont = [], False
    for c in loc.split("."):
        if len(key) == D or c == "0":  # a 0th division (preface) is unnumbered text
            break
        m = NUM.fullmatch(c)
        if m and (not m.group(2) or len(key) == D - 1):
            key.append(int(m.group(1)))
            continue
        m = DUP.fullmatch(c)
        if m:
            key.append(int(m.group(1)))
            cont = True
            continue
        m = re.fullmatch(r"v-(\d+)[a-z]*(?:_\d+)?", c) if verse_num else None
        if m and len(key) == D - 1:
            key.append(int(m.group(1)))
            continue
        break
    return tuple(key), cont


def convert(name, path):
    cfg, D = CFG[name], CFG[name]["D"]
    allsegs = [dict(s) for s in segments(path)]
    if cfg.get("prepare"):
        allsegs = cfg["prepare"](allsegs)
    segs = []
    for s in allsegs:
        if cfg.get("stop_after") and segs and segs[-1]["loc"] == cfg["stop_after"]:
            break
        if not s["text"] or s["kind"] in SKIP_KINDS or (cfg.get("drop") and re.search(cfg["drop"], s["loc"])):
            continue
        segs.append(s)
    keyed = [[s, *key_of(s.get("_loc") or s["loc"], D, cfg.get("verse_num"))] for s in segs]

    # A mistyped unit number (…29, 30, 61, 32, 33…) is repaired from its neighbours.
    fixed = 0
    full = [k for k in keyed if len(k[1]) == D]
    for i in range(1, len(full) - 1):
        a, b, c = full[i - 1][1], full[i][1], full[i + 1][1]
        if a[:-1] == b[:-1] == c[:-1] and c[-1] == a[-1] + 2 and b[-1] != a[-1] + 1:
            full[i][1], full[i][2] = a[:-1] + (a[-1] + 1,), False
            fixed += 1

    units, order, pending = {}, [], []
    merged = joined = 0
    for s, key, cont in keyed:
        text = s["text"]
        if len(key) < D:  # unnumbered paragraph: belongs to the unit just read (or the next, at a division's start)
            if order and order[-1][: len(key)] == key:
                units[order[-1]].append(text)
                joined += 1
            else:
                pending.append(text)
            continue
        if order and (key in units or key < order[-1] or cont
                      or (order[-1][:-1] == key[:-1] and key[-1] > order[-1][-1] + 20)):
            # repeated, out-of-order or absurd number (OCR debris): text continues the unit before
            if key != order[-1] or cont:
                merged += 1
                if os.environ.get("DEBUG"):
                    print("  merge", s["loc"], "->", order[-1], repr(text[:50]))
            units[order[-1]].append(text)
            continue
        units[key] = pending + [text]
        pending = []
        order.append(key)
    if pending:
        units[order[-1]] += pending

    vid = name
    out = []
    for key in order:
        iast = clean(" ".join(units[key]))
        if not iast:
            continue
        e = {"reference": ".".join(map(str, key)), "sanskrit_iast": iast, "meaning": deva(iast), "text": "", "mandala": key[0]}
        if len(key) > 1:
            e["hymn"] = key[1]
        if len(key) > 2:
            e["verse"] = key[2]
        e["vedaId"] = vid
        out.append(e)
    return out, dict(entries=len(out), joined_unnumbered=joined, merged=merged, repaired_numbers=fixed)


def validate(name, ents):
    refs = [e["reference"] for e in ents]
    assert len(set(refs)) == len(refs), f"{name}: duplicate refs"
    ks = [tuple(map(int, r.split("."))) for r in refs]
    assert ks == sorted(ks), f"{name}: refs out of order"
    assert all(re.fullmatch(r"[1-9]\d*(\.[1-9]\d*)*", r) for r in refs), f"{name}: bad ref"
    sus = []
    for e in ents:
        s = e["sanskrit_iast"]
        assert s.strip(), f"{name}: empty {e['reference']}"
        assert re.search(r"[ऀ-ॿ]", e["meaning"]), f"{name}: no Devanagari {e['reference']}"
        if re.search(r"[<>\[\]{}()_^#*=]|//|[A-Z]|[0-24-9]", s):
            sus.append(e["reference"])
    return sus


def main():
    only = sys.argv[1:]
    report = {}
    for rel, path in TEXTS.items():
        name = os.path.basename(rel)[:-5]
        if name not in CFG or (only and name not in only):
            continue
        ents, stats = convert(name, path)
        sus = validate(name, ents)
        with open(os.path.join(DATA, rel), "w", encoding="utf-8") as f:
            json.dump(ents, f, ensure_ascii=False, indent=1)
        prov = page(path).get("provenance") or []
        stats.update(path=path, file=rel, first=ents[0]["reference"], last=ents[-1]["reference"], suspicious=sus[:6],
                     provenance=[{k: p.get(k) for k in ("repo", "url", "edition", "license")} for p in prov])
        report[name] = stats
        print(f"{rel:42s} {len(ents):6d}  {ents[0]['reference']}..{ents[-1]['reference']}  joined {stats['joined_unnumbered']} "
              f"merged {stats['merged']} repaired {stats['repaired_numbers']} suspicious {len(sus)} {sus[:4]}")
    json.dump(report, open(os.path.join(WORK, "convert_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
