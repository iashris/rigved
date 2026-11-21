#!/usr/bin/env python3
"""The Pāli Canon's discourses: the Mahāsaṅgīti Pāli beside Bhikkhu Sujato's English, from SuttaCentral.

Both come from SuttaCentral's bilara-data (github.com/suttacentral/bilara-data): the Pāli of the Mahāsaṅgīti
Tipiṭaka (public domain) and Sujato's translation (2018), which SuttaCentral dedicates to the public domain (CC0).
Bilara keeps the Pāli, the English and an HTML template as three files keyed by the same segment ids, so every
English sentence has its Pāli; the templates' paragraphs, stanzas and headings decide what one entry is. Pramāṇa
carries the same Sujato text, cut sutta by sutta; it is taken here whole from its source.

Fetch first (sparse, about 100 MB):
  git clone --depth 1 --filter=blob:none --sparse https://github.com/suttacentral/bilara-data.git cache/bilara-data
  git -C cache/bilara-data sparse-checkout set root/pli/ms/sutta translation/en/sujato/sutta html/pli/ms/sutta

One library text per collection: the four Nikāyas and the Khuddaka books Sujato translated in full (his Jātaka is
only 83 of the 547 verse sets, so it is left out; the Jātaka shelf has Cowell's). A reference is the sutta's own
number (MN 10 → 10, SN 12.2 → 12.2, AN 4.1-10 → 4.1-10, a file SuttaCentral keeps as one range) plus the paragraph
counted from 1 within it; the Dhammapada is the exception, chapter and verse number.

Writes public/data/pali/<id>.json and adds them to library_catalog.json and translation_sources.json. Rerunnable.
Usage: python3 -I scripts/corpus2/pali_suttacentral.py
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BILARA = os.path.join(ROOT, "cache", "bilara-data")
OUT = os.path.join(ROOT, "public", "data", "pali")
sys.path.insert(0, HERE)
from comparative_catalog import write  # noqa: E402

# (SuttaCentral collection, path under sutta/, id, name, group, levels)
COLLECTIONS = [
    ("dn", "dn", "pali_dn", "Dīgha Nikāya (Long Discourses)", "nikaya", ["Sutta", "Paragraph"]),
    ("mn", "mn", "pali_mn", "Majjhima Nikāya (Middle Discourses)", "nikaya", ["Sutta", "Paragraph"]),
    ("sn", "sn", "pali_sn", "Saṃyutta Nikāya (Linked Discourses)", "nikaya", ["Saṃyutta", "Sutta", "Paragraph"]),
    ("an", "an", "pali_an", "Aṅguttara Nikāya (Numbered Discourses)", "nikaya", ["Nipāta", "Sutta", "Paragraph"]),
    ("kp", "kn/kp", "pali_kp", "Khuddakapāṭha (Basic Passages)", "khuddaka", ["Text", "Paragraph"]),
    ("dhp", "kn/dhp", "pali_dhp", "Dhammapada (Sayings of the Dhamma)", "khuddaka", ["Vagga", "Verse"]),
    ("ud", "kn/ud", "pali_ud", "Udāna (Heartfelt Sayings)", "khuddaka", ["Vagga", "Sutta", "Paragraph"]),
    ("iti", "kn/iti", "pali_iti", "Itivuttaka (So It Was Said)", "khuddaka", ["Sutta", "Paragraph"]),
    ("snp", "kn/snp", "pali_snp", "Sutta Nipāta (Anthology of Discourses)", "khuddaka", ["Vagga", "Sutta", "Paragraph"]),
    ("thag", "kn/thag", "pali_thag", "Theragāthā (Verses of the Senior Monks)", "khuddaka", ["Nipāta", "Poem", "Stanza"]),
    ("thig", "kn/thig", "pali_thig", "Therīgāthā (Verses of the Senior Nuns)", "khuddaka", ["Nipāta", "Poem", "Stanza"]),
    ("cp", "kn/cp", "pali_cp", "Cariyāpiṭaka (The Conduct Leading to Buddhahood)", "khuddaka", ["Conduct", "Stanza"]),
    # The Vinaya, in Bhikkhu Brahmali's English (CC0). The Parivāra, a later catechism on the rest, is left out, and so is
    # the bare Pātimokkha, which bilara gives no template and whose every rule the two Vibhaṅgas quote.
    ("vin_bu", "vinaya:pli-tv-bu-vb", "pali_vin_bu", "Bhikkhu Vibhaṅga (the monks' rules analysed)", "vinaya", ["Rule", "Paragraph"]),
    ("vin_bi", "vinaya:pli-tv-bi-vb", "pali_vin_bi", "Bhikkhunī Vibhaṅga (the nuns' rules analysed)", "vinaya", ["Rule", "Paragraph"]),
    ("vin_kd", "vinaya:pli-tv-kd", "pali_vin_kd", "Khandhaka (the chapters on the community's life)", "vinaya", ["Khandhaka", "Paragraph"]),
]
VINAYA_CREDIT = {"english": {"by": "Bhikkhu Brahmali", "work": "The Monastic Law, SuttaCentral", "year": "2021",
                             "links": [{"label": "SuttaCentral", "url": "https://suttacentral.net/pitaka/vinaya"}],
                             "via": {"label": "bilara-data", "url": "https://github.com/suttacentral/bilara-data"},
                             "note": "Dedicated to the public domain (CC0) by the translator. Pāli: the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500, "
                                     "public domain, as segmented by SuttaCentral."}}

BAND = {"id": "pali_canon", "after": ["vedanga"], "name": "Pāli Canon",
        "blurb": "the Buddha's word as the Theravāda keeps it: the discourses in Pāli with Bhikkhu Sujato's English, the monastic law "
                 "with Bhikkhu Brahmali's, and three books of the Abhidhamma in English",
        "groups": [{"id": "nikaya", "name": "The four Nikāyas", "blurb": "the long, middle, linked and numbered discourses"},
                   {"id": "khuddaka", "name": "Minor Collection", "blurb": "the Dhammapada, the Sutta Nipāta, the elders' verses and other short books"},
                   {"id": "vinaya", "name": "Monastic Law", "blurb": "the Vinaya: the monks' and nuns' rules, each with the story of how it was laid down"},
                   {"id": "abhidhamma", "name": "Abhidhamma", "blurb": "the systematic doctrine, in English"}]}
ORIGINAL = {"name": "Pāli", "lang": "pi-Latn", "label": "Pāli", "short": "Pā"}
SOURCE = "Pāli: Mahāsaṅgīti Tipiṭaka (SuttaCentral); English: Bhikkhu Sujato (2018), CC0"
CREDIT = {"english": {"by": "Bhikkhu Sujato", "work": "The Discourses of the Buddha, SuttaCentral", "year": "2018",
                      "links": [{"label": "SuttaCentral", "url": "https://suttacentral.net/"}],
                      "via": {"label": "bilara-data", "url": "https://github.com/suttacentral/bilara-data"},
                      "note": "Dedicated to the public domain (CC0) by the translator. Pāli: the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500 "
                              "(World Tipiṭaka Edition), public domain, as segmented by SuttaCentral."}}
OPEN = re.compile(r"<(p|li|dd|dt|blockquote)\b")
CLOSE = re.compile(r"</(p|li|dd|dt)>")
HEAD = re.compile(r"<h([1-6])\b")
SKIP = re.compile(r"class='(end\w*|uddana-intro|uddanagatha)'")


def uid_of(path, kind):
    return os.path.basename(path).split(f"_{kind}")[0]


def natural(uid):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", uid)]


# The Vibhaṅgas' rule classes in the order the Pātimokkha recites them, not the alphabet's.
RULE_ORDER = ["pj", "ss", "ay", "np", "pc", "pd", "sk", "as"]
UNIT = {
    "vin_bu": lambda uid: uid[len("pli-tv-bu-vb-"):],  # pj1, ss13, as1-7
    "vin_bi": lambda uid: uid[len("pli-tv-bi-vb-"):],
    "vin_kd": lambda uid: uid[len("pli-tv-kd"):],  # 1 … 22
    "vin_pm": lambda uid: {"pli-tv-bu-pm": "monks", "pli-tv-bi-pm": "nuns"}[uid],
}


def order_key(sc, uid):
    if sc in ("vin_bu", "vin_bi"):
        u = UNIT[sc](uid)
        cls = re.match(r"[a-z]+", u).group(0)
        return [RULE_ORDER.index(cls)] + natural(u[len(cls):])
    if sc == "vin_pm":
        return [0 if "-bu-" in uid else 1]
    return natural(uid)


def paragraphs(html, pli, en):
    """[(title, pali, english, uid)] per paragraph or stanza, in template order; headings become the next one's title."""
    # Skipped: end-of-sutta and end-of-chapter lines, and the summary verses (uddāna) that list a chapter's suttas.
    out, cur, title, in_header, skipping = [], None, None, False, False
    for sid, tpl in html.items():
        p, e = (pli.get(sid) or "").strip(), (en.get(sid) or "").strip()
        if "<header" in tpl:
            in_header = True
        if HEAD.search(tpl):
            if e or p:
                h = f"{e} ({p})" if e and p and e != p else (e or p)
                title = f"{title} — {h}" if title else h
        if "</header>" in tpl:
            in_header = False
            continue
        if SKIP.search(tpl):
            skipping = not CLOSE.search(tpl)
            continue
        if skipping:
            skipping = not CLOSE.search(tpl)
            continue
        if in_header or HEAD.search(tpl):
            continue  # the collection's and chapter's names above the title
        if cur is None or OPEN.search(tpl):
            if cur and (cur[1] or cur[2]):
                out.append(cur)
            cur = [title, "", "", sid.split(":")[0]]
            title = None
        sep = "\n" if "verse-line" in tpl and cur[1] else " "
        if p:
            cur[1] = (cur[1] + sep + p) if cur[1] else p
        if e:
            cur[2] = (cur[2] + sep + e) if cur[2] else e
        if CLOSE.search(tpl):
            out.append(cur)
            cur = None
    if cur and (cur[1] or cur[2]):
        out.append(cur)
    return [(t, re.sub(r"[ \t]+", " ", p).strip(), re.sub(r"[ \t]+", " ", e).strip(), u) for t, p, e, u in out]


def build(sc, sub):
    """`sc` names the collection; `sub` is its folder under the sutta (or, prefixed vinaya:, the vinaya) tree."""
    pitaka, tr_dir = ("vinaya", "brahmali/vinaya") if sub.startswith("vinaya:") else ("sutta", "sujato/sutta")
    sub = sub.split(":", 1)[-1]
    tr_base = os.path.join(BILARA, "translation/en", tr_dir)
    tr_files = sorted(glob.glob(os.path.join(tr_base, sub, "**", "*.json"), recursive=True), key=lambda f: order_key(sc, uid_of(f, "translation")))
    if not tr_files:
        raise SystemExit(f"{sc}: no translation files; fetch bilara-data first (see the docstring)")
    rows, vagga = [], 0
    for f in tr_files:
        uid = uid_of(f, "translation")
        rel = os.path.relpath(os.path.dirname(f), tr_base)
        root = os.path.join(BILARA, "root/pli/ms", pitaka, rel, f"{uid}_root-pli-ms.json")
        html = os.path.join(BILARA, "html/pli/ms", pitaka, rel, f"{uid}_html.json")
        if not (os.path.exists(root) and os.path.exists(html)):
            raise SystemExit(f"{uid}: Pāli or template missing")
        en, pli, tpl = (json.load(open(x, encoding="utf-8")) for x in (f, root, html))
        if set(en) - set(tpl):
            raise SystemExit(f"{uid}: English segments with no place in the template: {sorted(set(en) - set(tpl))[:5]}")
        paras = paragraphs(tpl, pli, en)
        if sc == "dhp":
            vagga += 1  # one file per chapter; each verse is its own uid
            for t, p, e, u in paras:
                rows.append({"reference": f"{vagga}.{u[3:]}", "original": p, "text": e, **({"title": t} if t else {})})
            continue
        unit = UNIT[sc](uid) if sc in UNIT else uid[len(sc):]
        for n, (t, p, e, _) in enumerate(paras, 1):
            rows.append({"reference": f"{unit}.{n}", "original": p, "text": e, **({"title": t} if t else {})})
    if sc == "dhp":  # a verse split over two template paragraphs keeps one entry
        merged = {}
        for r in rows:
            if r["reference"] in merged:
                m = merged[r["reference"]]
                m["original"] = (m["original"] + "\n" + r["original"]).strip()
                m["text"] = (m["text"] + "\n" + r["text"]).strip()
            else:
                merged[r["reference"]] = r
        rows = list(merged.values())
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    texts, records = [], {}
    for sc, sub, tid, name, group, levels in COLLECTIONS:
        rows = build(sc, sub)
        depth = {len(r["reference"].split(".")) for r in rows}
        if len(depth) != 1 or depth.pop() != len(levels):
            raise SystemExit(f"{tid}: references are not all {len(levels)} deep")
        refs = [r["reference"] for r in rows]
        if len(set(refs)) != len(refs):
            raise SystemExit(f"{tid}: a reference repeats")
        with open(os.path.join(OUT, f"{tid}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        en = sum(1 for r in rows if r["text"])
        vin = sc.startswith("vin_")
        texts.append({"id": tid, "file": f"pali/{tid}.json", "name": name, "band": "pali_canon", "group": group,
                      "levels": levels, "original": ORIGINAL, "verseLines": True, "source": SOURCE.replace("Bhikkhu Sujato (2018)", "Bhikkhu Brahmali (2021)") if vin else SOURCE})
        records[tid] = VINAYA_CREDIT if vin else CREDIT
        print(f"{tid:12s} {len(rows):6d} entries, {en:6d} with English, {os.path.getsize(os.path.join(OUT, tid + '.json')) / 1e6:6.1f} MB")
    write([BAND], texts, records)


if __name__ == "__main__":
    main()
