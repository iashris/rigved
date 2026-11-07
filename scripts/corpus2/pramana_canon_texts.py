"""Scripture the corpus lacked, taken from Pramāṇa: the darśana sūtras, Gītā, Upapurāṇas, Smṛtis, Tantra, minor Upaniṣads.

Scope, set by the repo owner: the texts named as missing, plus any Hindu scripture Pramāṇa holds in both Sanskrit and
English. Keys are corpus ids. `sa` is the Sanskrit path, `en` a human translation. Machine English is never imported,
and a translation Pramāṇa marks "In copyright" is never taken, even when it is the only one: the site republishes what
it holds. A text with neither stays Sanskrit only.

Left out on purpose, because Pramāṇa's Sanskrit mixes the root text with commentary or editors' apparatus: Sātvata
Saṃhitā, Mahānirvāṇa Tantra, Ṣaḍviṃśa Brāhmaṇa, Sāmavidhāna Brāhmaṇa.

Placement is either `veda` + `layer` (the grid) or `band`, with `group` when the band is grouped. `dir` is the folder
under public/data. `en_of` marks an English that translates a commentary, sūtras included, so the reader is told.
`attach` adds a translation to a text already in the catalog instead of creating one. `match` says how pramana_canon_
concordance.py pairs chapters when numbers alone will not do: "names" by the names they share, "near" by a number that
only roughly corresponds, shown with the reader's low-confidence warning.
"""

D = "in.darsana."
V = "in.vedanga."
K = V + "kalpa."
P = V + "siksa.pratisakhya."
U = "in.veda.upanisad."
T = "in.sampradaya."
PD_AIYAR = {"en_name": "Aiyar", "en_label": "K. N. Aiyar (1914)"}

BANDS = [
    {"id": "darsana", "name": "Darśana", "blurb": "the root texts of the six schools", "after": "itihasa"},
    {"id": "upanisad_later", "name": "Later Upaniṣads", "blurb": "from the Muktikā canon's 108, in Aiyar's translation", "after": "darsana", "groups": [
        {"id": "samanya", "name": "Sāmānya", "blurb": "general Vedānta"},
        {"id": "sannyasa", "name": "Sannyāsa", "blurb": "on renunciation"},
        {"id": "yoga", "name": "Yoga", "blurb": "breath, sound and the subtle body"},
        {"id": "vaisnava", "name": "Vaiṣṇava", "blurb": "Viṣṇu and his names"},
    ]},
    {"id": "agama", "name": "Āgama & Tantra", "blurb": "the scriptures of temple and initiation", "after": "smrti", "groups": [
        {"id": "pancaratra", "name": "Pāñcarātra", "blurb": "Vaiṣṇava revelation"},
        {"id": "saiva", "name": "Śaiva", "blurb": "Śiva's revelation and the Nātha yoga manual"},
        {"id": "sakta", "name": "Śākta", "blurb": "Kaula and Goddess-centred Tantra"},
    ]},
    {"id": "upaveda", "name": "Upaveda", "blurb": "the sciences attached to the Veda: statecraft and medicine", "after": "agama"},
]

CANON = {
    # Darśana. No public-domain English of the bare Brahmasūtra or Nyāyasūtra exists on Pramāṇa, so each pairs with
    # the classic translation of its first commentary, which carries every sūtra.
    "brahma_sutra": {"name": "Brahmasūtra", "dir": "darsana", "band": "darsana", "sa": D + "vedanta.brahmasutra-works.brahmasutra",
                     "en": D + "vedanta.brahmasutra-works.brahmasutra!sankara~en-thibaut", "en_name": "Thibaut", "en_label": "Thibaut (1890–96), with Śaṅkara", "en_of": "Śaṅkara's commentary"},
    "yoga_sutra": {"name": "Yogasūtra", "dir": "darsana", "band": "darsana", "sa": D + "yoga.yogasutra",
                   "en": D + "yoga.yogasutra~en-vivekananda", "en_name": "Vivekananda", "en_label": "Vivekananda (1896)"},
    "nyaya_sutra": {"name": "Nyāyasūtra", "dir": "darsana", "band": "darsana", "sa": D + "nyaya.pracina.nyayasutra",
                    "en": D + "nyaya.pracina.nyayasutra!vatsyayana~en-jha", "en_name": "Jha", "en_label": "G. Jha (1912–19), with Vātsyāyana, part", "en_of": "Vātsyāyana's commentary"},
    "vaisesika_sutra": {"name": "Vaiśeṣikasūtra", "dir": "darsana", "band": "darsana", "sa": D + "vaisesika.vaisesikasutra",
                        "en": D + "vaisesika.vaisesikasutra~en-sinha", "en_name": "Sinha", "en_label": "N. Sinha (1911)"},
    "mimamsa_sutra": {"name": "Mīmāṃsāsūtra", "dir": "darsana", "band": "darsana", "sa": D + "mimamsa.mimamsasutra"},
    "samkhya_karika": {"name": "Sāṃkhyakārikā", "dir": "darsana", "band": "darsana", "sa": D + "samkhya.samkhyakarika"},
    "samkhya_sutra": {"name": "Sāṃkhyasūtra", "dir": "darsana", "band": "darsana", "sa": D + "samkhya.samkhyasutra",
                      "en": D + "samkhya.samkhyasutra~en-ballantyne", "en_name": "Ballantyne", "en_label": "Ballantyne (1885)"},

    # Itihāsa.
    "bhagavad_gita": {"name": "Bhagavadgītā", "dir": "epics", "band": "itihasa", "sa": D + "all.gita",
                      "en": D + "all.gita~en-telang", "en_name": "Telang", "en_label": "K. T. Telang (1882)"},
    "adhyatma_ramayana": {"name": "Adhyātma Rāmāyaṇa", "dir": "epics", "band": "itihasa", "sa": "in.lit.ramayana.upajivya.adhyatma",
                          "en": "in.lit.ramayana.upajivya.adhyatma~en-baijnath", "en_name": "Baij Nath", "en_label": "Baij Nath (1913)"},
    "yoga_vasistha": {"name": "Yogavāsiṣṭha", "dir": "epics", "band": "itihasa", "sa": "in.lit.ramayana.upajivya.yogavasistha",
                      "en": "in.lit.ramayana.upajivya.yogavasistha~en-mitra", "en_name": "Mitra", "en_label": "V. L. Mitra (1891–99)"},

    # Purāṇa: Upapurāṇas and digests, placed in the Purāṇa band's own groups.
    "devi_bhagavata_purana": {"name": "Devībhāgavatapurāṇa", "dir": "puranas", "band": "purana", "group": "sakta", "sa": "in.purana.upa.sakta.devibhagavata",
                              "en": "in.purana.upa.sakta.devibhagavata~en-vijnanananda", "en_name": "Vijnanananda", "en_label": "Vijñānānanda (1921–23)", "match": "names"},
    "kalika_purana": {"name": "Kālikāpurāṇa", "dir": "puranas", "band": "purana", "group": "sakta", "sa": "in.purana.upa.sakta.kalika"},
    "brhaddharma_purana": {"name": "Bṛhaddharmapurāṇa", "dir": "puranas", "band": "purana", "group": "sakta", "sa": "in.purana.upa.sakta.brhaddharma",
                           "en": "in.purana.upa.sakta.brhaddharma~en-banerji", "en_name": "Banerji", "en_label": "S. C. Banerji (1915), abridged", "match": "names"},
    "visnudharmottara_purana": {"name": "Viṣṇudharmottarapurāṇa (part)", "dir": "puranas", "band": "purana", "group": "vaisnava", "sa": "in.purana.upa.vaisnava.visnudharmottara"},
    "garuda_saroddhara": {"name": "Garuḍapurāṇa Sāroddhāra", "dir": "puranas", "band": "purana", "group": "vaisnava", "sa": "in.purana.garudasaroddhara",
                          "en": "in.purana.garudasaroddhara~en-wood-subrahmanyam", "en_name": "Wood", "en_label": "Wood & Subrahmanyam (1911)"},

    # Smṛti.
    "yajnavalkya_smrti": {"name": "Yājñavalkyasmṛti", "dir": "smrti", "band": "smrti", "sa": "in.niti.dharma.yajnavalkya"},
    "narada_smrti": {"name": "Nāradasmṛti", "dir": "smrti", "band": "smrti", "sa": "in.niti.dharma.narada",
                     "en": "in.niti.dharma.narada~en-jolly", "en_name": "Jolly", "en_label": "J. Jolly (1889)"},
    "visnu_smrti": {"name": "Viṣṇusmṛti", "dir": "smrti", "band": "smrti", "sa": "in.niti.dharma.visnu",
                    "en": "in.niti.dharma.visnu~en-jolly", "en_name": "Jolly", "en_label": "J. Jolly (1880)"},
    "brhaspati_smrti": {"name": "Bṛhaspatismṛti (fragments)", "dir": "smrti", "band": "smrti", "sa": "in.niti.dharma.uddhrta.brhaspati",
                        "en": "in.niti.dharma.uddhrta.brhaspati~en-jolly", "en_name": "Jolly", "en_label": "J. Jolly (1889)", "match": "near"},

    # Āgama and Tantra.
    "ahirbudhnya_samhita": {"name": "Ahirbudhnyasaṃhitā", "dir": "tantra", "band": "agama", "group": "pancaratra", "sa": T + "vaisnava.pancaratra.samhita.divyasamhita.ahirbudhnya"},
    "jayakhya_samhita": {"name": "Jayākhyasaṃhitā", "dir": "tantra", "band": "agama", "group": "pancaratra", "sa": T + "vaisnava.pancaratra.samhita.ratnatraya.jayakhya"},
    "malinivijaya_tantra": {"name": "Mālinīvijayottaratantra", "dir": "tantra", "band": "agama", "group": "saiva", "sa": T + "saiva.agama.trika.malinivijaya"},
    "hathapradipika": {"name": "Haṭhapradīpikā", "dir": "tantra", "band": "agama", "group": "saiva", "sa": T + "saiva.trika.natha.hathayoga.nibandha.hathapradipika",
                       "en": T + "saiva.trika.natha.hathayoga.nibandha.hathapradipika~en-sinh", "en_name": "Sinh", "en_label": "Pancham Sinh (1915)"},
    "kularnava_tantra": {"name": "Kulārṇavatantra", "dir": "tantra", "band": "agama", "group": "sakta", "sa": T + "saiva.trika.kaula.kularnava"},

    # Upaveda.
    "arthasastra": {"name": "Kauṭilīya Arthaśāstra", "dir": "upaveda", "band": "upaveda", "sa": "in.niti.artha.kautilya",
                    "en": "in.niti.artha.kautilya~en-shamasastry", "en_name": "Shamasastry", "en_label": "R. Shamasastry (1915)"},
    "caraka_samhita": {"name": "Carakasaṃhitā", "dir": "upaveda", "band": "upaveda", "sa": "in.med.samhita.caraka",
                       "en": "in.med.samhita.caraka~en-kaviratna", "en_name": "Kaviratna", "en_label": "A. C. Kaviratna (1890–1925), part", "match": "names"},
    "susruta_samhita": {"name": "Suśrutasaṃhitā", "dir": "upaveda", "band": "upaveda", "sa": "in.med.samhita.susruta-school.susruta",
                        "en": "in.med.samhita.susruta-school.susruta~en-bhishagratna", "en_name": "Bhishagratna", "en_label": "K. K. Bhishagratna (1907–16), part",
                        # Pramāṇa's provenance URL for this translation is a dead Wikisource page; these were checked by hand.
                        "en_links": [{"label": "Wikisource, vol. 1", "url": "https://en.wikisource.org/wiki/Sushruta_Samhita,_Volume_1/Chapter_1"}, {"label": "Wikisource, vol. 3", "url": "https://en.wikisource.org/wiki/Sushruta_Samhita,_Volume_3/Chapter_1"}, {"label": "Internet Archive scan, vol. 1", "url": "https://archive.org/details/englishtranslati01susruoft"}]},

    # Vedāṅga.
    "astadhyayi": {"name": "Aṣṭādhyāyī of Pāṇini", "dir": "other", "band": "vedanga", "sa": V + "vyakarana.astadhyayi-school.astadhyayi"},
    "rk_pratisakhya": {"name": "Ṛgveda Prātiśākhya", "dir": "other", "band": "vedanga", "sa": P + "rk.rg"},
    "taittiriya_pratisakhya": {"name": "Taittirīya Prātiśākhya", "dir": "other", "band": "vedanga", "sa": P + "krsnayajur.taittiriya"},
    "vajasaneyi_pratisakhya": {"name": "Vājasaneyi Prātiśākhya", "dir": "other", "band": "vedanga", "sa": P + "suklayajur.vajasaneyi"},
    "atharva_pratisakhya": {"name": "Atharvaveda Prātiśākhya", "dir": "other", "band": "vedanga", "sa": P + "atharva.atharvapratisakhya"},
    "suryasiddhanta": {"name": "Sūryasiddhānta", "dir": "other", "band": "vedanga", "sa": "in.astro.siddhanta.early.suryasiddhanta",
                       "en": "in.astro.siddhanta.early.suryasiddhanta~en-burgess", "en_name": "Burgess", "en_label": "E. Burgess (1860)"},
    "brhatsamhita": {"name": "Bṛhatsaṃhitā of Varāhamihira", "dir": "other", "band": "vedanga", "sa": "in.astro.samhita.rsi.brhatsamhita",
                     "en": "in.astro.samhita.rsi.brhatsamhita~en-iyer", "en_name": "Iyer", "en_label": "N. C. Iyer (1884)"},

    # The Vedic grid.
    "kanva_samhita": {"name": "Kāṇva Saṃhitā (Vājasaneyi)", "dir": "vedas", "veda": "syv", "layer": "samhita", "sa": "in.veda.samhita.suklayajur*vajasaneyi*kanva"},
    "kapisthala_samhita": {"name": "Kapiṣṭhala-Kaṭha Saṃhitā", "dir": "vedas", "veda": "kyv", "layer": "samhita", "sa": "in.veda.samhita.krsnayajur*kapisthala"},
    "arseya_brahmana": {"name": "Ārṣeya Brāhmaṇa", "dir": "brahmanas", "veda": "sv", "layer": "brahmana", "sa": "in.veda.brahmana.arseya"},
    "samhitopanisad_brahmana": {"name": "Saṃhitopaniṣad Brāhmaṇa", "dir": "brahmanas", "veda": "sv", "layer": "brahmana", "sa": "in.veda.brahmana.samhitopanisad"},
    "apastamba_srautasutra": {"name": "Āpastamba Śrautasūtra", "dir": "sutras", "veda": "kyv", "layer": "sutra", "sa": K + "srauta.apastamba-school.apastamba"},
    "hiranyakesi_srautasutra": {"name": "Hiraṇyakeśi Śrautasūtra", "dir": "sutras", "veda": "kyv", "layer": "sutra", "sa": K + "srauta.hiranyakesin.hiranyakesi"},
    "manava_srautasutra": {"name": "Mānava Śrautasūtra", "dir": "sutras", "veda": "kyv", "layer": "sutra", "sa": K + "srauta.maitrayaniya.manava"},
    "katyayana_srautasutra": {"name": "Kātyāyana Śrautasūtra", "dir": "sutras", "veda": "syv", "layer": "sutra", "sa": K + "srauta.katyayana-school.katyayana"},
    "latyayana_srautasutra": {"name": "Lāṭyāyana Śrautasūtra", "dir": "sutras", "veda": "sv", "layer": "sutra", "sa": K + "srauta.samaveda.latyayana"},
    "baudhayana_grhyasutra": {"name": "Baudhāyana Gṛhyasūtra", "dir": "sutras", "veda": "kyv", "layer": "sutra", "sa": K + "grhya.krsnayajur.baudhayana"},
    "vadhula_grhyasutra": {"name": "Vādhūla Gṛhyasūtra", "dir": "sutras", "veda": "kyv", "layer": "sutra", "sa": K + "grhya.krsnayajur.vadhula"},

    # English for texts the corpus already holds in Sanskrit.
    "kausitaki_brahmana": {"attach": "brahmanas", "en": "in.veda.brahmana.kausitaki~en-keith", "en_name": "Keith", "en_label": "A. B. Keith (1920)"},
    "kaivalya_upanishad": {"attach": "upanishads", "en": U + "saiva.kaivalya~en-aiyar", **PD_AIYAR},
    "garbha_upanishad": {"attach": "upanishads", "en": U + "samanya.garbha~en-aiyar", **PD_AIYAR},
    "nadabindu_upanishad": {"attach": "upanishads", "en": U + "yoga.nadabindu~en-aiyar", **PD_AIYAR},
}

# The rest of Aiyar's Thirty Minor Upaniṣads: (id stem, Pramāṇa path below in.veda.upanisad, name, group).
_MINOR = [
    ("adhyatma", "samanya.adhyatma", "Adhyātma", "samanya"), ("atmabodha", "samanya.atmabodha", "Ātmabodha", "samanya"),
    ("muktika", "samanya.muktika", "Muktikā", "samanya"), ("niralamba", "samanya.niralamba", "Nirālamba", "samanya"),
    ("paingala", "samanya.paingala", "Paiṅgala", "samanya"), ("sariraka", "samanya.sariraka", "Śārīraka", "samanya"),
    ("sarvasara", "samanya.sarvasara", "Sarvasāra", "samanya"), ("skanda", "samanya.skanda", "Skanda", "samanya"),
    ("subala", "samanya.subala", "Subāla", "samanya"), ("vajrasuchi", "samanya.vajrasuchi", "Vajrasūcī", "samanya"),
    ("bhiksuka", "sannyasa.bhiksuka", "Bhikṣuka", "sannyasa"), ("brahma", "sannyasa.brahma", "Brahma", "sannyasa"),
    ("maitreya", "sannyasa.maitreya", "Maitreya", "sannyasa"), ("naradaparivrajaka", "sannyasa.naradaparivrajaka", "Nāradaparivrājaka", "sannyasa"),
    ("tejobindu", "sannyasa.tejobindu", "Tejobindu", "sannyasa"), ("kalisantarana", "vaisnava.kalisantarana", "Kalisantaraṇa", "vaisnava"),
    ("narayana", "vaisnava.narayana", "Nārāyaṇa", "vaisnava"), ("tarasara", "vaisnava.tarasara", "Tārasāra", "vaisnava"),
    ("amrtabindu", "yoga.amrtabindu", "Amṛtabindu", "yoga"), ("amrtanada", "yoga.amrtanada", "Amṛtanāda", "yoga"),
    ("dhyanabindu", "yoga.dhyanabindu", "Dhyānabindu", "yoga"), ("hamsa", "yoga.hamsa", "Haṃsa", "yoga"),
    ("mandalabrahmana", "yoga.mandalabrahmana", "Maṇḍalabrāhmaṇa", "yoga"), ("sandilya", "yoga.sandilya", "Śāṇḍilya", "yoga"),
    ("varaha", "yoga.varaha", "Varāha", "yoga"), ("yogakundalini", "yoga.yogakundalini", "Yogakuṇḍalinī", "yoga"),
    ("yogatattva", "yoga.yogatattva", "Yogatattva", "yoga"),
]
for _stem, _path, _name, _group in _MINOR:
    CANON[f"{_stem}_upanishad"] = {"name": f"{_name} Upaniṣad", "dir": "upanishads", "band": "upanisad_later", "group": _group,
                                   "sa": U + _path, "en": U + _path + "~en-aiyar", **PD_AIYAR}
