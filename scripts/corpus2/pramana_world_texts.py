"""Story literature from beyond the Veda, taken from Pramāṇa in English only: Buddhist birth stories and chronicles,
the great story collection, the Kashmir chronicle and the Chinese pilgrims' records of India.

Scope, set by the repo owner: these seven works, chosen for the stories they hold. Only the public-domain English is
taken; the Pāli, Sanskrit and Chinese originals are not imported, and machine English is never used. Keys are corpus ids.
`en` is the Pramāṇa path of the translation, `dir` the folder under public/data, `band` the home page band. `levels`
names the reference parts. `by`, `work`, `year` credit the translator in translation_sources.json; `label` is the
short form shown in the catalog.
"""

BANDS = [
    {"id": "bauddha", "name": "Bauddha", "blurb": "the Buddha's former births, a king's questions and the chronicle of Laṅkā, in English", "after": "vedanga"},
    {"id": "katha", "name": "Kathā", "blurb": "the great story collections, in English", "after": "bauddha"},
    {"id": "chronicle", "name": "Chronicle", "blurb": "history told as verse: the kings of Kashmir, in English", "after": "katha"},
    {"id": "travel", "name": "Pilgrims' records", "blurb": "India as Chinese monks saw it, 399–645 CE, in English", "after": "chronicle"},
]

WORLD = {
    "jataka_cowell": {"name": "Jātaka (the 547 birth stories)", "dir": "bauddha", "band": "bauddha",
                      "en": "in.bauddha.theravada.sp.khuddaka.jataka!jatakatthavannana~en-cowell", "levels": ["Jātaka", "Paragraph"],
                      "by": "E. B. Cowell (ed.); tr. R. Chalmers, W. H. D. Rouse, H. T. Francis, R. A. Neil, E. B. Cowell",
                      "work": "The Jātaka, or Stories of the Buddha's Former Births, 6 vols., Cambridge University Press", "year": "1895–1907",
                      "label": "E. B. Cowell (ed.), 1895–1907"},
    "milindapanha_rhysdavids": {"name": "Milindapañha (The Questions of King Milinda)", "dir": "bauddha", "band": "bauddha",
                                "en": "in.bauddha.theravada.sp.khuddaka.milindapanha~en-rhysdavids", "levels": ["Book", "Chapter", "Paragraph"],
                                "by": "T. W. Rhys Davids", "work": "The Questions of King Milinda, Parts I–II, Sacred Books of the East vols. 35–36, Oxford: Clarendon Press",
                                "year": "1890–94", "label": "T. W. Rhys Davids (1890–94)"},
    "mahavamsa_geiger": {"name": "Mahāvaṃsa (The Great Chronicle of Ceylon)", "dir": "bauddha", "band": "bauddha",
                         "en": "in.bauddha.theravada_postcanon.vamsa.mahavamsa~en-geiger", "levels": ["Chapter", "Paragraph"],
                         "by": "Wilhelm Geiger, assisted by Mabel Haynes Bode", "work": "The Mahāvaṃsa or the Great Chronicle of Ceylon, Pali Text Society Translation Series 3, London",
                         "year": "1912", "label": "W. Geiger (1912)"},
    "kathasaritsagara_tawney": {"name": "Kathāsaritsāgara (Ocean of the Streams of Story)", "dir": "katha", "band": "katha",
                                "en": "in.lit.brhatkatha.kathasaritsagara~en-tawney", "levels": ["Lambaka", "Taraṅga", "Paragraph"],
                                "by": "C. H. Tawney", "work": "The Kathá Sarit Ságara, or Ocean of the Streams of Story, 2 vols., Calcutta: Baptist Mission Press (Bibliotheca Indica)",
                                "year": "1880–84", "label": "C. H. Tawney (1880–84)"},
    "rajatarangini_stein": {"name": "Rājataraṅgiṇī (The River of Kings)", "dir": "chronicle", "band": "chronicle",
                            "en": "in.lit.historical.kashmir.rajatarangini~en-stein", "levels": ["Book", "Verse"],
                            "by": "M. A. Stein", "work": "Kalhaṇa's Rājataraṅgiṇī: A Chronicle of the Kings of Kaśmīr, 2 vols., Westminster: Archibald Constable",
                            "year": "1900", "label": "M. A. Stein (1900)"},
    "faxian_legge": {"name": "Faxian, A Record of Buddhistic Kingdoms", "dir": "travel", "band": "travel",
                     "en": "in.bauddha.taisho.2085~en-legge", "levels": ["Chapter", "Paragraph"],
                     "by": "James Legge", "work": "A Record of Buddhistic Kingdoms: Being an Account by the Chinese Monk Fâ-hien of his Travels in India and Ceylon (A.D. 399–414), Oxford: Clarendon Press",
                     "year": "1886", "label": "J. Legge (1886)"},
    "xuanzang_beal": {"name": "Xuanzang, Records of the Western World (Xiyuji)", "dir": "travel", "band": "travel",
                      "en": "in.bauddha.taisho.2087~en-beal", "levels": ["Book", "Country", "Paragraph"],
                      "by": "Samuel Beal", "work": "Si-yu-ki: Buddhist Records of the Western World, translated from the Chinese of Hiuen Tsiang, 2 vols., London: Trübner",
                      "year": "1884", "label": "S. Beal (1884)"},
    "xuanzang_life_beal": {"name": "Huili, The Life of Xuanzang (books 1–5)", "dir": "travel", "band": "travel",
                           "en": "in.bauddha.taisho.2053~en-beal", "levels": ["Book", "Paragraph"],
                           "by": "Samuel Beal", "work": "The Life of Hiuen-Tsiang, by the Shaman Hwui Li, new edition, London: Kegan Paul",
                           "year": "1911", "label": "S. Beal (1911)"},
}
