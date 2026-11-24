#!/usr/bin/env python3
"""The Ṛgveda word by word: every word's form, dictionary headword and grammar, from VedaWeb's Zurich annotation.

VedaWeb (University of Cologne, github.com/VedaWebProject/vedaweb-data, rigveda/TEI) annotates each word of the
Ṛgveda with its surface form, its lemma in Grassmann's Wörterbuch (as revised by VedaWeb), its word class, and its
morphosyntax in Leipzig-glossing terms (case, gender, number, person, tense, mood, voice, non-finite form). It also
gives Arnold's chronological stratum for each pāda (info/strata.json) and each hymn's addressee (info/addressees.json).

This is a study layer, not a translation, so it is not added to the reader's switcher. Essential Vedas uses it to
draft its decode cards, which are then checked against Sāyaṇa and the padapāṭha.

Reads cache/vedaweb/rv_book_NN.tei (download from the repo above). Writes public/data/vedas/rigveda_morph.json:
  {"01.001.01": [{"p": "a", "s": "agním", "l": "agní-", "c": "nominal stem", "g": {"case": "ACC", ...}}, ...], ...}
Usage: .venv/bin/python -I scripts/corpus2/rigveda_morph_vedaweb.py
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
CACHE = os.path.join(ROOT, "cache", "vedaweb")
OUT = os.path.join(ROOT, "public", "data", "vedas", "rigveda_morph.json")
T = "{http://www.tei-c.org/ns/1.0}"
X = "{http://www.w3.org/XML/1998/namespace}"


def ref(xid):
    m = re.match(r"b(\d+)_h(\d+)_(\d+)", xid)
    return f"{int(m.group(1)):02d}.{int(m.group(2)):03d}.{int(m.group(3)):02d}"


def feats(fs):
    out = {}
    for f in fs.findall(f"{T}f"):
        name = f.get("name")
        sym = f.find(f"{T}symbol")
        if sym is not None:
            out[name] = sym.get("value")
    return out


def token(fs, pada):
    t = {"p": pada}
    for f in fs.findall(f"{T}f"):
        name = f.get("name")
        if name == "surface":
            t["s"] = (f.findtext(f"{T}string") or "").strip()
        elif name == "gra_lemma":
            t["l"] = (f.findtext(f"{T}string") or "").strip()
        elif name == "gra_gramm":
            sym = f.find(f"{T}symbol")
            if sym is not None:
                t["c"] = sym.get("value")
        elif name == "morphosyntax":
            inner = f.find(f"{T}fs")
            if inner is not None:
                g = feats(inner)
                if g:
                    t["g"] = g
    return t


def main():
    data = {}
    for path in sorted(glob.glob(os.path.join(CACHE, "rv_book_*.tei"))):
        for _, el in ET.iterparse(path, events=("end",)):
            if el.tag == f"{T}div" and el.get("type") == "stanza":
                r = ref(el.get(f"{X}id"))
                toks = []
                for lg in el.findall(f"{T}lg"):
                    if lg.get("source") != "zurich":
                        continue
                    for l in lg.findall(f"{T}l"):
                        pass
                        for fs in l.findall(f"{T}fs"):
                            if fs.get("type") == "zurich_info":
                                m = re.search(r"_zur_([a-z])_\d+$", fs.get(f"{X}id") or ""); toks.append(token(fs, m.group(1) if m else ""))
                data[r] = toks
                el.clear()
        print(os.path.basename(path), len(data), flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(v) for v in data.values())
    print(f"wrote {OUT}: {len(data)} stanzas, {n} words")


if __name__ == "__main__":
    main()
