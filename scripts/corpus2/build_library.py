#!/usr/bin/env python3
"""Build the reader's library from public/data: a catalog plus each text split into small chunks.

The reader shows one *block* at a time: the level just above the smallest unit (a Ṛgveda sūkta, a
Mahābhārata adhyāya, a Śatapatha brāhmaṇa). Blocks are packed into chunk files of a few hundred KB so the
browser only fetches what is being read.

Output (generated, gitignored): public/library/catalog.json, public/library/texts/<id>/<n>.json
Concordances in public/library/concordance/ are inputs (tracked), not outputs.

Usage: python3 -I scripts/corpus2/build_library.py
"""

import json
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "public", "data")
OUT = os.path.join(ROOT, "public", "library")
CHUNK_BYTES = 400_000
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def norm_ref(r):
    return ".".join(str(int(p)) if p.isdigit() else p for p in str(r).split("."))


def compact(e):
    """Short keys keep chunks small: r ref, s IAST, d Devanagari, e English, t heading."""
    out = {"r": norm_ref(e["reference"])}
    iast = e.get("sanskrit_iast") or e.get("iast") or ""
    deva = e.get("meaning") or ""
    eng = e.get("text") or ""
    if iast:
        out["s"] = iast
    if deva and DEVANAGARI.search(deva):
        out["d"] = deva
    if eng and not DEVANAGARI.search(eng[:200]):
        out["e"] = eng
    elif eng and not deva:
        out["d"] = eng  # a few legacy files keep the Devanagari in `text`
    if e.get("title"):
        out["t"] = e["title"]
    return out


def build_text(meta):
    raw = json.load(open(os.path.join(DATA, meta["file"]), encoding="utf-8"))
    entries = [compact(e) for e in raw]
    depths = [len(e["r"].split(".")) for e in entries]
    block_depth = max(min(depths) - 1, 0)
    # Long entries (a Ganguli section, a Kāṭhaka anuvāka) are already a page each: read them one at a time.
    avg = sum(len(json.dumps(e, ensure_ascii=False).encode()) for e in entries) / len(entries)
    if avg > 3000:
        block_depth = min(depths)

    blocks = []  # [(key, [entries])] in text order
    for e in entries:
        key = ".".join(e["r"].split(".")[:block_depth]) if block_depth else ""
        if not blocks or blocks[-1][0] != key:
            blocks.append((key, []))
        blocks[-1][1].append(e)
    keys = [k for k, _ in blocks]
    if len(set(keys)) != len(keys):
        raise SystemExit(f"{meta['id']}: a block appears twice in text order; references are not grouped")

    tdir = os.path.join(OUT, "texts", meta["id"])
    os.makedirs(tdir, exist_ok=True)
    chunk_of, chunk, size, n = {}, {}, 0, 0
    for key, es in blocks:
        b = len(json.dumps(es, ensure_ascii=False).encode())
        if chunk and size + b > CHUNK_BYTES:
            json.dump(chunk, open(os.path.join(tdir, f"{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
            chunk, size, n = {}, 0, n + 1
        chunk[key] = es
        chunk_of[key] = n
        size += b
    json.dump(chunk, open(os.path.join(tdir, f"{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

    # Table of contents down to block level: nested [key, entryCount, children] with the chunk on block nodes.
    def tree(prefix_blocks, depth):
        groups = []
        for key, es in prefix_blocks:
            head = ".".join(key.split(".")[:depth])
            if not groups or groups[-1][0] != head:
                groups.append((head, []))
            groups[-1][1].append((key, es))
        nodes = []
        for head, members in groups:
            count = sum(len(es) for _, es in members)
            if depth == block_depth:
                first = members[0][1][0]
                nodes.append([head, count, chunk_of[head], first.get("t", "")])
            else:
                nodes.append([head, count, tree(members, depth + 1)])
        return nodes

    toc = tree(blocks, 1) if block_depth else [["", len(entries), 0, ""]]
    has = lambda k: sum(1 for e in entries if e.get(k))  # noqa: E731
    stats = {"entries": len(entries), "blocks": len(blocks), "english": round(100 * has("e") / len(entries)),
             "sanskrit": round(100 * max(has("s"), has("d")) / len(entries)), "chunks": n + 1}
    return {**{k: v for k, v in meta.items() if k != "file"}, "blockDepth": block_depth, "stats": stats, "toc": toc}


def main():
    cat = json.load(open(os.path.join(os.path.dirname(__file__), "library_catalog.json"), encoding="utf-8"))
    if os.path.isdir(os.path.join(OUT, "texts")):
        shutil.rmtree(os.path.join(OUT, "texts"))
    texts = []
    for meta in cat["texts"]:
        if not os.path.exists(os.path.join(DATA, meta["file"])):
            print(f"skip {meta['id']}: {meta['file']} missing")
            continue
        t = build_text(meta)
        texts.append(t)
        print(f"{t['id']:30s} {t['stats']['entries']:6d} entries {t['stats']['blocks']:5d} blocks {t['stats']['chunks']:3d} chunks  en {t['stats']['english']:3d}%")
    ids = {t["id"] for t in texts}
    for t in texts:
        for p in t.get("pairs", []):
            if p["with"] not in ids:
                raise SystemExit(f"{t['id']} pairs with missing text {p['with']}")
            if p["mode"] == "concordance":
                f = os.path.join(OUT, "concordance", f"{t['id']}__{p['with']}.json")
                p["available"] = os.path.exists(f)
    catalog = {k: cat[k] for k in ("vedas", "layers", "bands")} | {"texts": texts}
    json.dump(catalog, open(os.path.join(OUT, "catalog.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"catalog: {len(texts)} texts, {os.path.getsize(os.path.join(OUT, 'catalog.json')) // 1024} KB")


if __name__ == "__main__":
    main()
