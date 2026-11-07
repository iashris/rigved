"""Credit the Āraṇyaka English in library_catalog.json and translation_sources.json.  Idempotent; other entries are untouched."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IA = "https://archive.org/details/"
MT = lambda path: {"by": "Gemini (machine translation)", "note": "Machine output, unreviewed.", "via": {"label": "Pramāṇa", "url": f"https://indike.org/pramana/{path}~en-mt"}}
CREDITS = {
    "aitareya_aranyaka": {"english": {
        "by": "F. Max Müller; A. B. Keith",
        "work": "Müller, The Upanishads Part I, Sacred Books of the East vol. 1, 1879 (Books 1–3); Keith, The Aitareya Āraṇyaka, Oxford: Clarendon Press, 1909 (Books 4–5 and 1.3.6)",
        "year": "1879, 1909",
        "links": [{"label": "Keith 1909, archive.org", "url": IA + "in.ernet.dli.2015.195520"}],
        "via": {"label": "Pramāṇa (Müller)", "url": "https://indike.org/pramana/in.veda.aranyaka.aitareya~en-muller"}}},
    "sankhayana_aranyaka": {"english": {
        "by": "A. B. Keith",
        "work": "The Śāṅkhāyana Āraṇyaka, with an Appendix on the Mahāvrata, Oriental Translation Fund n.s. 18, London: Royal Asiatic Society, 1908",
        "year": "1908",
        "links": [{"label": "archive.org", "url": IA + "sankhayanaaranya00keitrich"}],
        "note": "From OCR; spellings of names keep some OCR damage."},
        "machine": MT("in.veda.aranyaka.kausitaki")},
    "jaiminiya_upanisad_brahmana": {"english": {
        "by": "Hanns Oertel",
        "work": "The Jāiminīya or Talavakāra Upaniṣad Brāhmaṇa, Journal of the American Oriental Society 16 (1896), pp. 79–260",
        "year": "1896",
        "links": [{"label": "archive.org", "url": IA + "jstor-592488"}],
        "note": "From OCR. Where a sentence number was unreadable, that sentence's English stays with the sentence before."},
        "machine": MT("in.veda.brahmana.jaiminiya_upanisad")},
    "taittiriya_aranyaka": {"english": {
        "by": "Oppiliappan Koil V. Sadagopan",
        "work": "Aruṇa Praśnam, 3 vols., and Mantra Puṣpam, e-books (Book 1 only)",
        "links": [{"label": f"Aruṇa Praśnam vol. {v}, sadagopan.org", "url": f"https://www.sadagopan.org/ebook/pdf/Aruna%20Prasnam%20%20v{v}.pdf"} for v in (1, 2, 3)]
                  + [{"label": "Mantra Puṣpam, sadagopan.org", "url": "https://www.sadagopan.org/ebook/pdf/Manthra%20Pushpam.pdf"}],
        "note": "Book 1 only. A devotional commentary with word-by-word meanings after Sāyaṇa, not a literal translation."}},
    "kathaka_aranyaka": {"machine": MT("in.veda.aranyaka.katha")},
}
SOURCE = {
    "aitareya_aranyaka": "TITUS; English: Müller (SBE 1, Books 1–3), A. B. Keith (1909, Books 4–5)",
    "sankhayana_aranyaka": "GRETIL (Kümmel); English: A. B. Keith (1908)",
    "jaiminiya_upanisad_brahmana": "TITUS; English: H. Oertel (1896)",
    "taittiriya_aranyaka": "sanskritdocuments.org (Muralidhara B A); English, Book 1 only: V. Sadagopan (commentary)",
}


def main():
    p = os.path.join(HERE, "translation_sources.json")
    d = json.load(open(p, encoding="utf-8"))
    d.update(CREDITS)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")
    p = os.path.join(HERE, "library_catalog.json")
    lines = open(p, encoding="utf-8").read().split("\n")
    done = 0
    for i, ln in enumerate(lines):
        for k, src in SOURCE.items():
            if f'"id": "{k}"' in ln:
                e = json.loads(ln.strip().rstrip(","))
                e["source"] = src
                lines[i] = "    " + json.dumps(e, ensure_ascii=False) + ("," if ln.rstrip().endswith(",") else "")
                done += 1
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    json.load(open(p, encoding="utf-8"))
    print("catalog lines", done, "credits", len(CREDITS))


if __name__ == "__main__":
    main()
