"""The 19 Mahāpurāṇas taken from Pramāṇa, with the one English translation chosen for each.

Keys are corpus ids. `sa` is the Sanskrit path. `en` is the human translation, written as its own file and paired
through library_catalog's `translationOf`. `mt` is Pramāṇa's machine English, used only where no human translation is
available, stored in `text_mt` on the Sanskrit entries so the reader labels it. `group` is the one god a text puts
first, a judgement checked against deity-name counts in the Sanskrit; it is what the home page clusters on.
"""

PURANA_GROUPS = [
    {"id": "vaisnava", "name": "Vaiṣṇava", "blurb": "Viṣṇu and his forms, Kṛṣṇa above all, stand supreme"},
    {"id": "saiva", "name": "Śaiva", "blurb": "Śiva stands supreme"},
    {"id": "sakta", "name": "Śākta", "blurb": "The Goddess stands supreme. Of the Mahāpurāṇas only Mārkaṇḍeya belongs here, for the Devī Māhātmya it holds"},
    {"id": "mixed", "name": "Mixed", "blurb": "No one god holds the whole text"},
]

PURANAS = {
    "agni_purana": {"name": "Agnipurāṇa", "group": "mixed", "sa": "in.purana.agni", "mt": "in.purana.agni~en-mt"},
    "bhagavata_purana": {"name": "Bhāgavatapurāṇa", "group": "vaisnava", "sa": "in.purana.bhagavata", "en": "in.purana.bhagavata~en-subbarau", "en_name": "Subba Rau", "en_label": "Subba Rau (1928)"},
    "bhavisya_purana": {"name": "Bhaviṣyapurāṇa", "group": "mixed", "sa": "in.purana.bhavisya"},
    "brahma_purana": {"name": "Brahmapurāṇa", "group": "mixed", "sa": "in.purana.brahma"},
    "brahmanda_purana": {"name": "Brahmāṇḍapurāṇa", "group": "mixed", "sa": "in.purana.brahmanda"},
    "brahmavaivarta_purana": {"name": "Brahmavaivartapurāṇa", "group": "vaisnava", "sa": "in.purana.brahmavaivarta"},
    "garuda_purana": {"name": "Garuḍapurāṇa", "group": "vaisnava", "sa": "in.purana.garuda", "en": "in.purana.garuda~en-dutt", "en_name": "Dutt", "en_label": "M. N. Dutt (1908)", "en_covers": ["0", "1"]},
    "kurma_purana": {"name": "Kūrmapurāṇa", "group": "saiva", "sa": "in.purana.kurma"},
    "linga_purana": {"name": "Liṅgapurāṇa", "group": "saiva", "sa": "in.purana.linga"},
    "markandeya_purana": {"name": "Mārkaṇḍeyapurāṇa", "group": "sakta", "sa": "in.purana.markandeya", "en": "in.purana.markandeya~en-pargiter", "en_name": "Pargiter", "en_label": "Pargiter (1888–1904)"},
    "matsya_purana": {"name": "Matsyapurāṇa", "group": "mixed", "sa": "in.purana.matsya", "en": "in.purana.matsya~en-taluqdar", "en_name": "Taluqdar", "en_label": "A Taluqdar of Oudh (1916–17)"},
    "narada_purana": {"name": "Nāradapurāṇa", "group": "vaisnava", "sa": "in.purana.narada"},
    "padma_purana": {"name": "Padmapurāṇa", "group": "vaisnava", "sa": "in.purana.padma"},
    # The default Śiva path holds only books 1 and 7; this recension is the whole text.
    "siva_purana": {"name": "Śivapurāṇa", "group": "saiva", "sa": "in.purana.siva*complete-3"},
    "skanda_purana": {"name": "Skandapurāṇa", "group": "saiva", "sa": "in.purana.skanda*vulgate", "mt": "in.purana.skanda~en-mt"},
    "vamana_purana": {"name": "Vāmanapurāṇa", "group": "mixed", "sa": "in.purana.vamana"},
    "varaha_purana": {"name": "Varāhapurāṇa", "group": "vaisnava", "sa": "in.purana.varaha"},
    "vayu_purana": {"name": "Vāyupurāṇa", "group": "saiva", "sa": "in.purana.vayu"},
    "visnu_purana": {"name": "Viṣṇupurāṇa", "group": "vaisnava", "sa": "in.purana.visnu*crit", "en": "in.purana.visnu~en-wilson", "en_name": "Wilson", "en_label": "H. H. Wilson (1840)"},
}
