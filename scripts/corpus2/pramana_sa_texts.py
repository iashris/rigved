"""The texts pramana_sa imports (scope set by the repo owner: narrative, attribution, research or video value)."""

K = "in.vedanga.kalpa."
TEXTS = {
    "sutras/baudhayana_srautasutra.json": K + "srauta.baudhayana-school.baudhayana",
    "sutras/baudhayana_sulbasutra.json": K + "sulba.baudhayana",
    "sutras/katyayana_sulbasutra.json": K + "sulba.katyayana",
    "sutras/manava_sulbasutra.json": K + "sulba.manava",
    "sutras/maitrayana_sulbasutra.json": K + "sulba.maitrayana",
    "sutras/hiranyakesin_sulbasutra.json": K + "sulba.hiranyakesi",
    "other/sarvanukramani.json": "in.vedanga.misc.anukramani.katyayana.sarvanukramani",  # pramana_sa_sarvanukramani.py
    "other/jyotisa_rk.json": "in.vedanga.jyotisa.rk",
    "other/jyotisa_yajus.json": "in.vedanga.jyotisa.yajus",
    "other/jyotisa_atharva.json": "in.vedanga.jyotisa.atharva",
    "other/pingala_chandahsutra.json": "in.vedanga.chanda.pingala-school.pingala",
    "other/atharvaveda_parisista.json": "in.vedanga.misc.parisista.atharvaveda.atharva",
}
COMPARE = {"nirukta": "in.vedanga.nirukta.yaska"}  # compared with our other/nirukta.json: pramana_sa_nirukta.py
