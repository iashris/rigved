"""Literature from beyond the Veda, taken from Pramāṇa in English only: Buddhist birth stories and chronicles, the great
story collection, the Kashmir chronicle and the Chinese pilgrims' records of India; and, for comparative study of
religion (scope widened by the repo owner, 2026-11), the Mahāyāna sūtras and poems, the Chinese Āgamas, the
Abhidhamma, the Jain Āgamas, Vedānta and Tantra, Tamil and Hindi devotion, the Pahlavi books, Rumi, and the Ethiopic
and Syriac Christian classics.

Only public-domain (or CC0) English from clean transcriptions is taken (sacred-texts, Wikisource, wisdomlib, Gutenberg,
SuttaCentral), never an OCR'd scan; the originals are not imported, and machine English is never used. Keys are corpus ids.
`en` is the Pramāṇa path of the translation, `dir` the folder under public/data, `band` the home page band. `levels`
names the reference parts. `by`, `work`, `year` credit the translator in translation_sources.json; `label` is the
short form shown in the catalog.
"""

BANDS = [
    {"id": "bauddha", "name": "Bauddha", "blurb": "the Buddha's former births, a king's questions, the chronicle of Laṅkā, and the early discourses "
                                                  "as the Chinese canon keeps them, beside the Pāli, in English", "after": ["pali_canon", "vedanga"]},
    {"id": "mahayana", "name": "Mahāyāna", "blurb": "the Great Vehicle: the Lotus, the Pure Land and Perfection of Wisdom sūtras, the bodhisattva's path, in Sanskrit with the old English translations",
     "after": ["bauddha"], "groups": [{"id": "sutra", "name": "Sūtras", "blurb": "the Lotus, the Pure Land sūtras, the Diamond and the Heart"},
                                      {"id": "sastra", "name": "Poems and treatises", "blurb": "the Buddha's life, the bodhisattva's path, the Awakening of Faith"},
                                      {"id": "chinese", "name": "In the Chinese canon", "blurb": "the Lotus, Vimalakīrti and Pure Land sūtras as China read them, Chan's Platform Sūtra and rule (BDK English Tripiṭaka)"}]},
    {"id": "jaina", "name": "Jaina", "blurb": "the Śvetāmbara canon: Mahāvīra's life, the monk's discipline, the doctrine of non-violence, in English", "after": ["mahayana"]},
    {"id": "bhakti", "name": "Bhakti and the regional voices", "blurb": "Tamil ethics and Śaiva hymns, Kabīr, Jayadeva, Tulsīdās's Rāmcaritmānas in Awadhi and the Hindi Kṛṣṇa story", "after": ["jaina"]},
    {"id": "christian_east", "name": "Eastern Christian", "blurb": "not Indic: the Ethiopian and Syriac churches' own scriptures and lore, in English", "after": ["new_testament"]},
    {"id": "katha", "name": "Kathā", "blurb": "the great story collections, in English", "after": ["bhakti", "bauddha"]},
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


def _w(cid, name, band, en, by, work, year, group=None, dir=None, levels=("Chapter", "Paragraph")):
    WORLD[cid] = {"name": name, "dir": dir or band, "band": band, "en": en, "levels": list(levels), "by": by, "work": work, "year": year,
                  "label": f"{by} ({year})", **({"group": group} if group else {})}


SBE = "Sacred Books of the East"
B, J = "in.bauddha.sanskrit.", "in.jaina.sveta."
# Mahāyāna
_w("lotus_kern", "Saddharmapuṇḍarīka (The Lotus Sūtra)", "mahayana", B + "mahayanasutra.vaipulya.saddharmapundarika~en-kern", "H. Kern",
   f"The Saddharma-Puṇḍarīka or the Lotus of the True Law, {SBE} 21, Oxford: Clarendon Press", "1884", "sutra")
_w("sukhavati_larger_muller", "Larger Sukhāvatīvyūha (The Land of Bliss)", "mahayana", B + "mahayanasutra.buddha.sukhavativyuha~en-muller", "F. Max Müller",
   f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sutra")
_w("sukhavati_smaller_muller", "Smaller Sukhāvatīvyūha", "mahayana", B + "mahayanasutra.buddha.sukhavativyuha-smaller~en-muller", "F. Max Müller",
   f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sutra")
_w("amitayurdhyana_takakusu", "Amitāyurdhyāna Sūtra (Meditation on the Buddha of Infinite Life)", "mahayana", B + "mahayanasutra.buddha.amitayurdhyana~en-takakusu",
   "J. Takakusu", f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sutra")
_w("vajracchedika_muller", "Vajracchedikā (The Diamond Sūtra)", "mahayana", B + "prajnaparamita.samksipta.vajracchedika~en-muller", "F. Max Müller",
   f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sutra")
_w("hrdaya_muller", "Prajñāpāramitāhṛdaya (The Heart Sūtra)", "mahayana", B + "prajnaparamita.samksipta.hrdaya~en-muller", "F. Max Müller",
   f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sutra")
_w("buddhacarita_cowell", "Aśvaghoṣa, Buddhacarita (The Acts of the Buddha)", "mahayana", "in.lit.kavya.mahakavya.aitihasika.bauddha.buddhacarita~en-cowell",
   "E. B. Cowell", f"Buddhist Mahâyâna Texts, {SBE} 49, Oxford: Clarendon Press", "1894", "sastra")
_w("bodhicaryavatara_barnett", "Śāntideva, Bodhicaryāvatāra (The Path of Light)", "mahayana", B + "marga.santideva.bodhicaryavatara~en-barnett",
   "L. D. Barnett", "The Path of Light, Wisdom of the East, London: John Murray", "1909", "sastra")
_w("jatakamala_speyer", "Āryaśūra, Jātakamālā (The Garland of Birth Stories)", "mahayana", B + "avadana.jataka.jatakamala~en-speyer",
   "J. S. Speyer", "The Jātakamālā or Garland of Birth-Stories of Āryaśūra, Sacred Books of the Buddhists 1, London: Henry Frowde", "1895", "sastra")
_w("awakening_faith_suzuki", "The Awakening of Faith in the Mahāyāna", "mahayana", B + "darsana.yogacara.mahayanasraddhotpadasastra*zh-siksananda~en-suzuki",
   "D. T. Suzuki", "Aśvaghosha's Discourse on the Awakening of Faith in the Mahâyâna, Chicago: Open Court", "1900", "sastra")
# Their Sanskrit originals came in through pramana_canon_texts (2026-11): these Englishes are now filed as translations
# of those texts (`of`), named for the translator, and the original takes the shelf.
for _cid, _of, _tr in (("lotus_kern", "lotus", "Kern"), ("sukhavati_larger_muller", "sukhavati_larger", "Müller"),
                       ("sukhavati_smaller_muller", "sukhavati_smaller", "Müller"), ("vajracchedika_muller", "vajracchedika", "Müller"),
                       ("hrdaya_muller", "hrdaya", "Müller"), ("buddhacarita_cowell", "buddhacarita", "Cowell"),
                       ("bodhicaryavatara_barnett", "bodhicaryavatara", "Barnett"), ("jatakamala_speyer", "jatakamala", "Speyer")):
    WORLD[_cid].update(name=f"{WORLD[_cid]['name']} — {_tr}", of=_of)
for _k, _n, _p in (("dirgha","Dīrgha Āgama (Long Discourses, Chinese; selected sūtras)", "dirgha.dirghagama*zh-buddhayasas"),
                   ("madhyama", "Madhyama Āgama (Middle Discourses, Chinese)", "madhyama.madhyamagama*zh-sanghadeva"),
                   ("samyukta", "Saṃyukta Āgama (Connected Discourses, Chinese; selected sūtras)", "samyukta.samyuktagama*zh-gunabhadra"),
                   ("ekottara", "Ekottara Āgama (Numbered Discourses, Chinese; selected sūtras)", "ekottara.ekottaragama*zh-sanghadeva")):
    # Not Mahāyāna: the early schools' discourses, the Nikāyas' parallels, as the Chinese canon keeps them.
    _w(f"{_k}_agama_patton", _n, "bauddha", B + f"agama.{_p}~en-patton", "Charles Patton", "translations of the Chinese Āgamas, SuttaCentral (CC0)", "2019",
       dir="mahayana")
# Abhidhamma, beside the Pāli Canon
_w("kathavatthu_aung", "Kathāvatthu (Points of Controversy)", "pali_canon", "in.bauddha.theravada.ap.kathavatthu~en-aung-rhysdavids", "S. Z. Aung and C. A. F. Rhys Davids",
   "Points of Controversy, Pali Text Society Translation Series 5, London", "1915", "abhidhamma", dir="pali")
_w("puggalapannati_law", "Puggalapaññatti (Designation of Human Types)", "pali_canon", "in.bauddha.theravada.ap.puggalapannati~en-law", "B. C. Law",
   "Designation of Human Types, Pali Text Society Translation Series 12, London", "1924", "abhidhamma", dir="pali")
_w("dhammasangani_rhysdavids", "Dhammasaṅgaṇī (A Buddhist Manual of Psychological Ethics)", "pali_canon", "in.bauddha.theravada.ap.dhammasangani~en-rhysdavids",
   "C. A. F. Rhys Davids", "A Buddhist Manual of Psychological Ethics, Oriental Translation Fund, London: Royal Asiatic Society", "1900", "abhidhamma", dir="pali")
# Jain
_w("acaranga_jacobi", "Ācārāṅga Sūtra", "jaina", J + "anga.1~en-jacobi", "Hermann Jacobi", f"Jaina Sūtras, Part I, {SBE} 22, Oxford: Clarendon Press", "1884")
_w("kalpasutra_jacobi", "Kalpa Sūtra (the lives of the Jinas)", "jaina", J + "cheda.1.kalpasutra~en-jacobi", "Hermann Jacobi", f"Jaina Sūtras, Part I, {SBE} 22, Oxford: Clarendon Press", "1884")
_w("sutrakrtanga_jacobi", "Sūtrakṛtāṅga", "jaina", J + "anga.2~en-jacobi", "Hermann Jacobi", f"Jaina Sūtras, Part II, {SBE} 45, Oxford: Clarendon Press", "1895")
_w("uttaradhyayana_jacobi", "Uttarādhyayana Sūtra", "jaina", J + "mula.2~en-jacobi", "Hermann Jacobi", f"Jaina Sūtras, Part II, {SBE} 45, Oxford: Clarendon Press", "1895")
# Vedānta and the schools
_w("sribhasya_thibaut", "Rāmānuja, Śrībhāṣya (on the Brahmasūtra)", "darsana", "in.darsana.vedanta.brahmasutra-works.brahmasutra!ramanuja~en-thibaut", "George Thibaut",
   f"The Vedânta-Sûtras with the Commentary by Râmânuja, {SBE} 48, Oxford: Clarendon Press", "1904")
_w("vivekacudamani_johnston", "Vivekacūḍāmaṇi (The Crest-Jewel of Discrimination)", "darsana", "in.darsana.advaita.prakarana.early.sankara-prakarana.vivekacudamani~en-johnston",
   "Charles Johnston", "The Crest-Jewel of Wisdom, Covina: Quarterly Book Department", "1925")
_w("aparoksanubhuti_venkataramanan", "Aparokṣānubhūti (Direct Experience)", "darsana", "in.darsana.advaita.prakarana.early.sankara-prakarana.aparoksanubhuti~en-venkataramanan",
   "S. Venkataramanan", "Select Works of Sri Sankaracharya, Madras: G. A. Natesan", "1911")
_w("atmabodha_venkataramanan", "Ātmabodha (Knowledge of the Self)", "darsana", "in.darsana.advaita.prakarana.early.sankara-prakarana.atmabodha-2~en-venkataramanan",
   "S. Venkataramanan", "Select Works of Sri Sankaracharya, Madras: G. A. Natesan", "1911")
_w("sarvadarsana_cowell", "Mādhava, Sarvadarśanasaṃgraha (Review of the Different Systems)", "darsana", "in.darsana.all.sarvadarsana.sarvadarsanasangraha~en-cowell",
   "E. B. Cowell and A. E. Gough", "The Sarva-Darśana-Saṃgraha, Trübner's Oriental Series, London", "1882")
# Tantra
_w("mahanirvana_avalon", "Mahānirvāṇa Tantra", "agama", "in.sampradaya.general.sakta.kali.mahanirvana~en-avalon", "Arthur Avalon (Sir John Woodroffe)",
   "Tantra of the Great Liberation, London: Luzac", "1913", "sakta")
_w("satcakra_avalon", "Ṣaṭcakranirūpaṇa (The Six Centres)", "agama", "in.sampradaya.saiva.trika.natha.hathayoga.satcakra-works.satcakrabheda-2~en-avalon",
   "Arthur Avalon (Sir John Woodroffe)", "The Serpent Power, London: Luzac", "1919", "sakta")
_w("padukapancaka_avalon", "Pādukāpañcaka (The Fivefold Footstool)", "agama", "in.sampradaya.saiva.trika.kaula.guru.padukapancaka~en-avalon",
   "Arthur Avalon (Sir John Woodroffe)", "The Serpent Power, London: Luzac", "1919", "sakta")
# The epic's philosophical books
_w("anugita_telang", "Anugītā", "itihasa", "in.lit.mahabharata.vyasa.anugita~en-telang", "K. T. Telang",
   f"The Bhagavadgîtâ with the Sanatsugâtîya and the Anugîtâ, {SBE} 8, Oxford: Clarendon Press", "1882", dir="epics")
_w("sanatsujatiya_telang", "Sanatsujātīya", "itihasa", "in.lit.mahabharata.vyasa.sanatsujatiya~en-telang", "K. T. Telang",
   f"The Bhagavadgîtâ with the Sanatsugâtîya and the Anugîtâ, {SBE} 8, Oxford: Clarendon Press", "1882", dir="epics")
# Devotion and the regional literatures
_w("tirukkural_pope", "Tiruvaḷḷuvar, Tirukkuṟaḷ", "bhakti", "in.sangam.eighteen_lesser.tirukkural~en-pope*complete", "G. U. Pope, W. H. Drew, J. Lazarus and F. W. Ellis",
   "The 'Sacred' Kurral of Tiruvalluva-Nayanar, London: W. H. Allen", "1886")
_w("tiruvacakam_pope", "Māṇikkavācakar, Tiruvācakam (hymns I–X)", "bhakti", "in.sampradaya.saiva.siddhanta.tirumurai.tiruvacakam~en-pope", "G. U. Pope",
   "The Tiruvāçagam or 'Sacred Utterances' of Māṇikka-Vāçagar, Oxford: Clarendon Press", "1900")
_w("kabir_tagore", "Songs of Kabīr", "bhakti", "in.vernacular.hindi.sant.kabir.songs~en-tagore", "Rabindranath Tagore (with Evelyn Underhill)",
   "Songs of Kabir, New York: Macmillan", "1915")
_w("gitagovinda_arnold", "Jayadeva, Gītagovinda (The Indian Song of Songs)", "bhakti", "in.lit.kavya.khanda.gitakavya.gitagovinda-2~en-arnold", "Edwin Arnold",
   "The Indian Song of Songs, London: Trübner", "1875")
_w("premsagar_hollings", "Lallū Lāl, Prem Sāgar (The Ocean of Love)", "bhakti", "in.vernacular.hindi.katha.premsagar~en-hollings", "W. Hollings",
   "The Prem Sagur, Calcutta", "1848")
# Beyond India
_w("bundahisn_west", "Bundahišn (Creation)", "avesta", "inf.ir.pal.bundahisn~en-west", "E. W. West", f"Pahlavi Texts, Part I, {SBE} 5, Oxford: Clarendon Press", "1880")
_w("wahman_yasn_west", "Zand-ī Wahman Yasn (the Bahman Yašt)", "avesta", "inf.ir.pal.zand-wahman-yasn~en-west", "E. W. West", f"Pahlavi Texts, Part I, {SBE} 5, Oxford: Clarendon Press", "1880")
_w("skand_gumanig_west", "Škand-gumānīg Wizār (Doubt-Dispelling Exposition)", "avesta", "inf.ir.pal.skand-gumanig-wizar~en-west", "E. W. West",
   f"Pahlavi Texts, Part III, {SBE} 24, Oxford: Clarendon Press", "1885")
_w("mathnawi_whinfield", "Rūmī, Mathnawī (abridged)", "quran", "inf.isl.fa.shir.mathnawi~en-whinfield", "E. H. Whinfield",
   "Masnavi i Ma'navi, the Spiritual Couplets of Maulana Jalalu-'d-Din Muhammad Rumi, translated and abridged, 2nd ed., London: Kegan Paul, Trench, Trübner", "1898", dir="islam")
_w("kebra_nagast_budge", "Kebra Nagast (The Glory of the Kings)", "christian_east", "inf.sy.gez.kebra-nagast~en-budge", "E. A. Wallis Budge",
   "The Queen of Sheba and her Only Son Menyelek, London: Medici Society", "1922")
_w("book_of_the_bee_budge", "Solomon of Basra, The Book of the Bee", "christian_east", "inf.sy.syr.book-of-the-bee~en-budge", "E. A. Wallis Budge",
   "The Book of the Bee, Anecdota Oxoniensia, Oxford: Clarendon Press", "1886")

# How many numeric parts of a Pramāṇa loc name the chapter (deeper parts are paragraphs), and the reference levels.
# Depth 0: the text has no headings to divide it; it is read as one part, its paragraphs numbered through.
_SHAPE = {
    "lotus_kern": (1, ["Chapter", "Paragraph"]), "sukhavati_larger_muller": (0, ["Text", "Paragraph"]),
    "sukhavati_smaller_muller": (0, ["Text", "Paragraph"]), "amitayurdhyana_takakusu": (0, ["Text", "Paragraph"]),
    "vajracchedika_muller": (1, ["Section", "Paragraph"]), "hrdaya_muller": (1, ["Recension", "Paragraph"]),
    "buddhacarita_cowell": (1, ["Book", "Paragraph"]), "bodhicaryavatara_barnett": (1, ["Chapter", "Paragraph"]),
    "jatakamala_speyer": (1, ["Story", "Paragraph"]), "awakening_faith_suzuki": (1, ["Chapter", "Paragraph"]),
    "dirgha_agama_patton": (1, ["Sūtra", "Paragraph"]), "madhyama_agama_patton": (1, ["Sūtra", "Paragraph"]),
    "samyukta_agama_patton": (1, ["Sūtra", "Paragraph"]), "ekottara_agama_patton": (2, ["Nipāta", "Sūtra", "Paragraph"]),
    "kathavatthu_aung": (2, ["Book", "Point", "Paragraph"]), "puggalapannati_law": (2, ["Part", "Chapter", "Paragraph"]),
    "dhammasangani_rhysdavids": (1, ["Part", "Paragraph"]),
    "acaranga_jacobi": (3, ["Book", "Lecture", "Lesson", "Paragraph"]), "kalpasutra_jacobi": (1, ["Part", "Paragraph"]),
    "sutrakrtanga_jacobi": (3, ["Book", "Lecture", "Chapter", "Paragraph"]), "uttaradhyayana_jacobi": (1, ["Lecture", "Paragraph"]),
    "sribhasya_thibaut": (2, ["Adhyāya", "Pāda", "Paragraph"]), "vivekacudamani_johnston": (1, ["Chapter", "Paragraph"]),
    "aparoksanubhuti_venkataramanan": (0, ["Text", "Verse"]), "atmabodha_venkataramanan": (0, ["Text", "Verse"]),
    "sarvadarsana_cowell": (1, ["Chapter", "Paragraph"]), "mahanirvana_avalon": (1, ["Chapter", "Paragraph"]),
    "satcakra_avalon": (2, ["Section", "Verse", "Paragraph"]), "padukapancaka_avalon": (1, ["Verse", "Paragraph"]),
    "anugita_telang": (1, ["Chapter", "Paragraph"]), "sanatsujatiya_telang": (1, ["Chapter", "Paragraph"]),
    "tirukkural_pope": (2, ["Part", "Chapter", "Paragraph"]), "tiruvacakam_pope": (1, ["Hymn", "Paragraph"]),
    "kabir_tagore": (1, ["Song", "Paragraph"]), "gitagovinda_arnold": (1, ["Canto", "Paragraph"]),
    "premsagar_hollings": (1, ["Chapter", "Paragraph"]), "bundahisn_west": (1, ["Chapter", "Paragraph"]),
    "wahman_yasn_west": (1, ["Chapter", "Paragraph"]), "skand_gumanig_west": (1, ["Chapter", "Paragraph"]),
    "mathnawi_whinfield": (2, ["Book", "Story", "Paragraph"]), "kebra_nagast_budge": (1, ["Chapter", "Paragraph"]),
    "book_of_the_bee_budge": (1, ["Chapter", "Paragraph"]),
}
for _cid, (_d, _lv) in _SHAPE.items():
    WORLD[_cid]["depth"], WORLD[_cid]["levels"] = _d, _lv
# Verse translations: the reader keeps their line breaks.
for _cid in ("tirukkural_pope", "tiruvacakam_pope", "kabir_tagore", "gitagovinda_arnold", "mathnawi_whinfield"):
    WORLD[_cid]["verseLines"] = True

# Licensed, not public domain: non-commercial and share-alike translations, added on the repo owner's decision (2026-11-21)
# that a free, non-commercial site sharing them unaltered meets those terms. `licence` is shown in the credit and is what
# lets pramana_world_fetch.py take a text it would otherwise refuse.
BDK_NC = "CC BY-NC-SA 3.0, Bukkyō Dendō Kyōkai and Numata Center for Buddhist Translation and Research (BDK English Tripiṭaka)"
JLOR_NC = "CC BY-NC 4.0, Jain Literature Open Repository (JLOR); the Jain eLibrary's text of the printed edition"
BDK_PUB = "BDK English Tripiṭaka, Berkeley: Numata Center for Buddhist Translation and Research"


def _l(cid, name, band, en, by, work, year, licence, group=None, dir=None):
    _w(cid, name, band, en, by, work, year, group, dir)
    WORLD[cid]["licence"] = licence


T = "in.bauddha.taisho."
M = "in.bauddha.sanskrit.mahayanasutra."
for _cid, _n, _en, _by, _vol in (
        ("lotus_bdk", "The Lotus Sūtra (Kumārajīva's Chinese)", M + "vaipulya.saddharmapundarika*zh-kumarajiva~en-bdk", "Tsugunari Kubo and Akira Yuyama", "13-I, rev. 2nd ed."),
        ("vimalakirti_bdk", "The Vimalakīrti Sūtra", M + "dharma.vimalakirtinirdesa*zh-kumarajiva~en-bdk", "John R. McRae", "26-I"),
        ("srimala_bdk", "The Sūtra of Queen Śrīmālā of the Lion's Roar", M + "tathagatagarbha.srimaladevi*zh-gunabhadra~en-bdk", "Diana Y. Paul", "20-I"),
        ("larger_amitayus_bdk", "The Larger Sūtra on Amitāyus (Chinese)", M + "buddha.sukhavativyuha*zh-sanghavarman-wei~en-bdk", "Hisao Inagaki and Harold Stewart", "12-II"),
        ("contemplation_amitayus_bdk", "The Sūtra on Contemplation of Amitāyus (Chinese)", M + "buddha.amitayurdhyana*zh-kalayasas~en-bdk", "Hisao Inagaki and Harold Stewart", "12-II"),
        ("smaller_amitayus_bdk", "The Smaller Sūtra on Amitāyus (Chinese)", M + "buddha.sukhavativyuha-smaller*zh-kumarajiva~en-bdk", "Hisao Inagaki and Harold Stewart", "12-II"),
        ("mahavairocana_bdk", "The Vairocanābhisaṃbodhi Sūtra", "in.bauddha.sanskrit.tantra.carya.mahavairocana*zh~en-bdk", "Rolf W. Giebel", "30-I"),
        ("buddhacarita_bdk", "Buddhacarita: In Praise of Buddha's Acts (Chinese)", "in.lit.kavya.mahakavya.aitihasika.bauddha.buddhacarita*zh-dharmaksema~en-bdk", "Charles Willemen", "4-IV"),
        ("platform_sutra_bdk", "The Platform Sūtra of the Sixth Patriarch", T + "2008~en-bdk", "John R. McRae", "73-II"),
        ("baizhang_bdk", "The Baizhang Zen Monastic Regulations", T + "2025~en-bdk", "Shohei Ichimura", "77"),
        ("perfect_enlightenment_bdk", "The Sūtra of Perfect Enlightenment", T + "842~en-bdk", "Peter N. Gregory", "25"),
        ("forty_two_sections_bdk", "The Sūtra of Forty-two Sections", T + "784~en-bdk", "Heng-ching Shih", "25"),
        ("bequeathed_teaching_bdk", "The Bequeathed Teaching Sūtra", T + "389~en-bdk", "J. C. Cleary", "25"),
        ("ullambana_bdk", "The Ullambana Sūtra", T + "685~en-bdk", "Shojun Bando", "25"),
        ("filial_love_bdk", "The Sūtra on the Profundity of Filial Love", T + "2887~en-bdk", "Keiyo Arai", "25")):
    _l(_cid, _n, "mahayana", _en, _by, f"{BDK_PUB}, vol. {_vol}", "2005–", BDK_NC, "chinese")

J2 = "Padma Prakashan, Delhi (Sthānakavāsī edition by Amar Muni and Shreechand Surana)"
for _cid, _n, _en, _by, _yr in (
        ("acaranga_bothra", "Ācārāṅga Sūtra (Amar Muni edition)", "in.jaina.sveta.anga.1*amarmuni1999~en-surendra", "Surendra Bothra", "1999"),
        ("sthananga_bothra", "Sthānāṅga Sūtra", "in.jaina.sveta.anga.3*amarmuni2004~en-surendra", "Surendra Bothra", "2004"),
        ("bhagavati_bothra", "Bhagavatī Sūtra (Vyākhyāprajñapti), part", "in.jaina.sveta.anga.5*amarmuni2005~en-surendra", "Surendra Bothra", "2005"),
        ("prasnavyakarana_jain", "Praśnavyākaraṇa Sūtra", "in.jaina.sveta.anga.10*amarmuni2008~en-rajkumar", "Rajkumar Jain", "2008"),
        ("aupapatika_bothra", "Aupapātika Sūtra", "in.jaina.sveta.upanga.1*amarmuni2003~en-surendra", "Surendra Bothra", "2003"),
        ("rajaprasniya_jain", "Rājapraśnīya Sūtra", "in.jaina.sveta.upanga.2*amarmuni2002~en-rajkumar", "Rajkumar Jain", "2002"),
        ("jambudvipa_jain", "Jambūdvīpaprajñapti", "in.jaina.sveta.upanga.6*amarmuni2006~en-rajkumar", "Rajkumar Jain", "2006"),
        ("dasavaikalika_bothra", "Daśavaikālika Sūtra", "in.jaina.sveta.mula.1*amarmuni1997~en-surendra", "Surendra Bothra", "1997"),
        ("nandi_bothra", "Nandī Sūtra", "in.jaina.sveta.cullika.1*amarmuni1998~en-surendra", "Surendra Bothra", "1998"),
        ("anuyogadvara_bothra", "Anuyogadvāra Sūtra", "in.jaina.sveta.cullika.2*amarmuni2001~en-surendra", "Surendra Bothra", "2001")):
    _l(_cid, _n, "jaina", _en, _by, J2, _yr, JLOR_NC)
# Left out as OCR, against the clean-text rule, and already here in Jacobi's English: Lalwani's Kalpasūtra (1979) and
# Brajmohan Jain's Uttarādhyayana from the same repository.
_l("jnanasara_gopani", "Yaśovijaya, Jñānasāra", "jaina", "in.jaina.anuyoga.moral.yoga.svetambara-adhyatma.jnanasara-2*girishkumar1961~en-gopani", "A. S. Gopani",
   "Gyansara, Jain Sahitya Vikas Mandal", "1961", JLOR_NC)
_l("apadana_walters", "Apadāna (Legends of the Buddhist Saints)", "pali_canon", "in.bauddha.theravada.sp.khuddaka.apadana~en-walters", "Jonathan S. Walters",
   "Legends of the Buddhist Saints: Apadānapāli, Walla Walla: Whitman College", "2017",
   "CC BY-NC-SA 3.0, Jonathan S. Walters (via SuttaCentral)", "khuddaka", dir="pali")
# Divided at the printed page or Taishō column, not by the work's own sections: read as one part (depth 0). The
# Apadāna's two books are the monks' (thera) and the nuns' (therī) legends.
for _cid, _v in WORLD.items():
    if _v.get("licence") and "depth" not in _v:
        _v["depth"], _v["levels"] = 0, ["Part", "Passage"]  # parts of 40 passages, cut by pramana_world_convert.py
WORLD["apadana_walters"]["depth"], WORLD["apadana_walters"]["levels"] = 2, ["Book", "Legend", "Paragraph"]
