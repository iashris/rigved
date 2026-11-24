#!/usr/bin/env python3
"""Sāyaṇa's commentary (bhāṣya) on the Ṛgveda, verse by verse, beside the Saṃhitā.

Sāyaṇa (Vijayanagara, 14th century) wrote the one complete traditional commentary on the Ṛgveda. Sanskrit Wikisource
carries it on each sūkta page ("ऋग्वेदः सूक्तं १.१") inside the {{सायणभाष्यम्|…}} template. Inside the template, each verse
comes three times (the accented saṃhitā text, the accented padapāṭha, the unaccented padapāṭha, each block ending in
॥N), followed by Sāyaṇa's explanation of that verse. The text before the first verse is his introduction to the sūkta
(its seer, deity, metre and ritual use); it is kept as `preface` on the hymn's first row.

Read one page at a time through the MediaWiki API (action=parse, prop=wikitext), cached in cache/wikisource_sa.
Writes public/data/vedas/rigveda_sayana.json (rows keyed MM.SSS.VV like rigveda.json; `text` is the Sanskrit
commentary), adds the text to library_catalog.json and the Saṃhitā's switcher, and its credit to translation_sources.json.
Prints coverage: hymns with a bhāṣya, and verses whose commentary was found.

Usage: .venv/bin/python -I scripts/corpus2/rigveda_sayana_wikisource.py [--fetch-only] [--no-catalog]
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
CACHE = os.path.join(ROOT, "cache", "wikisource_sa")
DATA = os.path.join(ROOT, "public", "data", "vedas")
CAT = os.path.join(HERE, "library_catalog.json")
SOURCES = os.path.join(HERE, "translation_sources.json")
API = "https://sa.wikisource.org/w/api.php"
UA = "rigved-library/1.0 (Vedic text reader; one request at a time)"
SUKTAS = [191, 43, 62, 58, 87, 75, 104, 103, 114, 191]
DIG = str.maketrans("0123456789", "०१२३४५६७८९")
UNDIG = str.maketrans("०१२३४५६७८९", "0123456789")
TID = "rigveda_sayana"


def fetch(title):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, hashlib.sha1(title.encode()).hexdigest() + ".json")
    if os.path.exists(f):
        return json.load(open(f, encoding="utf-8"))
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "wikitext", "redirects": 1, "format": "json"})
    for attempt in range(7):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA}), timeout=60) as r:
                d = json.load(r)
            break
        except Exception as ex:  # transient errors and rate limits: back off and retry
            time.sleep(min(120, 5 * 2 ** attempt))
    else:
        print(f"  gave up on {title}", flush=True)
        return {}
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.8)
    return d


def prefetch(titles):
    """Fill the cache 50 pages per request (action=query, prop=revisions), so a full run is ~25 requests, not 1,028.
    Pages are stored in the same shape as action=parse, under the title asked for."""
    os.makedirs(CACHE, exist_ok=True)
    todo = [t for t in titles if not os.path.exists(os.path.join(CACHE, hashlib.sha1(t.encode()).hexdigest() + ".json"))]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                    "titles": "|".join(chunk), "redirects": 1, "format": "json", "formatversion": 2})
        for attempt in range(7):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA}), timeout=120) as r:
                    d = json.load(r)
                break
            except Exception:
                time.sleep(min(120, 5 * 2 ** attempt))
        else:
            print("  batch failed", chunk[0], flush=True)
            continue
        q_ = d.get("query", {})
        back = {}
        for m in q_.get("normalized", []) + q_.get("redirects", []):
            back[m["to"]] = back.get(m["from"], m["from"])
        got = set()
        for pg in q_.get("pages", []):
            asked = back.get(pg["title"], pg["title"])
            if pg.get("missing") or "revisions" not in pg:
                continue
            wt = pg["revisions"][0]["slots"]["main"]["content"]
            f = os.path.join(CACHE, hashlib.sha1(asked.encode()).hexdigest() + ".json")
            json.dump({"parse": {"title": pg["title"], "wikitext": {"*": wt}}}, open(f, "w", encoding="utf-8"), ensure_ascii=False)
            got.add(asked)
        print(f"  batch {i // 50 + 1}: {len(got)}/{len(chunk)} pages", flush=True)
        time.sleep(1)


def page(m, s):
    num = f"{m}.{s}".translate(DIG)
    for stem in ("ऋग्वेदः सूक्तं", "ऋग्वेद: सूक्तं"):
        d = fetch(f"{stem} {num}")
        if "parse" in d:
            return d["parse"]["wikitext"]["*"]
    return None


def bhashya(wt):
    i = wt.find("{{सायणभाष्यम्")
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(wt):  # find the template's matching close
        if wt.startswith("{{", j):
            depth += 1; j += 2; continue
        if wt.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0:
                break
            continue
        j += 1
    body = wt[i + len("{{सायणभाष्यम्"):j - 2].lstrip("|")
    return body


def clean(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


MARK = re.compile(r"॥\s*([०-९0-9]+)\s*॥?\s*$")


def split(body):
    """Return (preface, {verse: commentary})."""
    lines = [ln.strip() for ln in body.split("\n")]
    nonempty = [k for k, ln in enumerate(lines) if ln]
    material, seen = set(), {}
    for idx, k in enumerate(nonempty):
        mk = MARK.search(lines[k])
        if mk:
            n = mk.group(1).translate(UNDIG)
            seen[n] = seen.get(n, 0) + 1
        # a verse comes three times (saṃhitā, accented pada, plain pada); a later line ending in ॥N is commentary
        if mk and len(lines[k]) < 250 and seen[n] <= 3:
            material.add(k)
            # the verse's earlier line(s): short lines ending in a daṇḍa just before the marker line
            back = idx - 1
            while back >= 0 and len(material) and back >= idx - 3:
                pk = nonempty[back]
                if pk in material or not lines[pk].endswith("।") or len(lines[pk]) > 300 or MARK.search(lines[pk]):
                    break
                material.add(pk); back -= 1
    pre, com, cur = [], {}, 0
    for k in nonempty:
        if k in material:
            cur = int(MARK.search(lines[k]).group(1).translate(UNDIG)) if MARK.search(lines[k]) else cur
            continue
        (pre if cur == 0 else com.setdefault(cur, [])).append(lines[k])
    return clean("\n".join(pre)), {v: clean("\n".join(t)) for v, t in com.items()}


def main():
    verses = {}
    for r in json.load(open(os.path.join(DATA, "rigveda.json"), encoding="utf-8")):
        m, s, v = (int(x) for x in r["reference"].split("."))
        verses.setdefault((m, s), set()).add(v)
    first = [f"ऋग्वेदः सूक्तं {m}.{s}".translate(DIG) for m, n in enumerate(SUKTAS, 1) for s in range(1, n + 1)]
    prefetch(first)
    rows, have_hymn, missing_hymns, found, total = [], 0, [], 0, 0
    for m, n in enumerate(SUKTAS, 1):
        for s in range(1, n + 1):
            wt = page(m, s)
            vs = sorted(verses.get((m, s), []))
            total += len(vs)
            body = bhashya(wt) if wt else None
            if not body:
                missing_hymns.append(f"{m}.{s}")
                continue
            have_hymn += 1
            pre, com = split(body)
            for v in vs:
                t = com.get(v, "")
                if not t:
                    continue
                found += 1
                row = {"reference": f"{m:02d}.{s:03d}.{v:02d}", "text": t, "mandala": m, "hymn": s, "verse": v, "vedaId": TID}
                if v == vs[0] and pre:
                    row["preface"] = pre
                rows.append(row)
        print(f"maṇḍala {m}: done", flush=True)
    print(f"hymns with a bhāṣya: {have_hymn}/1028; verses with commentary: {found}/{total}")
    if missing_hymns:
        print("hymns without a bhāṣya:", len(missing_hymns), " ".join(missing_hymns[:60]), "…" if len(missing_hymns) > 60 else "")
    if "--fetch-only" in sys.argv:
        return
    with open(os.path.join(DATA, f"{TID}.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    if "--no-catalog" in sys.argv:
        return
    hymns = len({r["reference"].rsplit(".", 1)[0] for r in rows})
    raw = open(CAT, encoding="utf-8").read()
    lines = [ln for ln in raw.split("\n") if not ln.strip().startswith(f'{{"id": "{TID}"')]
    at = next(i for i, ln in enumerate(lines) if ln.strip().startswith('{"id": "rigveda_padapatha"'))
    lines.insert(at + 1, "    " + json.dumps({"id": TID, "file": f"vedas/{TID}.json", "name": "Ṛgveda Saṃhitā — Sāyaṇa's commentary",
                                              "veda": "rv", "layer": "samhita", "translationOf": "rigveda", "levels": ["Maṇḍala", "Sūkta", "Ṛc"],
                                              "source": f"Sāyaṇa (14th century), Ṛgvedabhāṣya, {hymns} hymns; Sanskrit Wikisource"}, ensure_ascii=False) + ",")
    raw = "\n".join(lines)
    mm = re.search(r'("id": "rigveda", [^{]*?"pairs": )(\[.*?\])', raw, re.S)
    pairs = [p for p in json.loads(mm.group(2)) if p["with"] != TID] + [{"with": TID, "mode": "aligned", "label": "Sāyaṇa's commentary (Sanskrit)"}]
    raw = raw[:mm.start(2)] + json.dumps(pairs, ensure_ascii=False) + raw[mm.end(2):]
    open(CAT, "w", encoding="utf-8").write(raw)
    json.load(open(CAT, encoding="utf-8"))
    have = json.load(open(SOURCES, encoding="utf-8"))
    have[TID] = {"english": {"by": "Sāyaṇa", "work": "Ṛgvedabhāṣya, the traditional commentary on the whole Ṛgveda", "year": "14th century",
                             "links": [{"label": "Sanskrit Wikisource", "url": "https://sa.wikisource.org/wiki/ऋग्वेदः"}],
                             "note": "Sanskrit commentary, verse by verse; the sūkta introduction (seer, deity, metre, ritual use) is kept with the first verse.",
                             "kind": "Commentary"}}
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(have, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {TID}.json: {len(rows)} rows in {hymns} hymns")


if __name__ == "__main__":
    main()
