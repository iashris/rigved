#!/usr/bin/env python3
"""The Chinese classics for the comparative shelf: the Dao De Jing, the Four Books (the Analects, the Great Learning, the
Doctrine of the Mean, the Mencius) and the Zhuangzi, each in Classical Chinese beside James Legge's English.

English: James Legge (1815–1897), all public domain, and never an OCR scan.
  Dao De Jing, Zhuangzi       Sacred Books of the East 39–40 (1891), the sacred-texts.com transcription.
  Great Learning, Mean        The Chinese Classics vol. 1 (1893), the sacred-texts.com etexts.
  Analects                    The Chinese Classics vol. 1, English Wikisource's transcription.
  Mencius                     The Chinese Classics vol. 2, English Wikisource's book pages.
sacred-texts is read through the Internet Archive's Wayback Machine, since the site serves robots a challenge.
English Wikisource's own Dao De Jing ("The Tao that can be described") and its Great Learning and Mean (pinyin names,
the Great Learning re-sorted into the Liji's order) are later reworkings of Legge and are not used. They serve only as
a second transcription to catch the etexts' slips, which FIXES corrects ("the people become final" for "filial",
"Auddle Kingdom", "you cannot sunrise", a dropped "the height of filial piety"). The Zhuangzi, with no second
transcription, is swept instead for a full stop before a lower-case word and for the figure 1 standing for "I", and
the Dao De Jing and Zhuangzi for words no dictionary knows (none beyond British spellings, archaisms and names were
found). The Mencius is the exception: the
sacred-texts etext drops the opening paragraph of a dozen chapters (II.ii.6 and VII.i.7 begin at "2."), and its wider
gaps suggest whole one-paragraph chapters lost as well, so the English comes from Wikisource's complete text. That text
writes Legge's names in pinyin (Qi, Teng, King Wen where Legge wrote Ch'î, T'ang, King Wan). Its paragraphing and names
appear to be those of ctext.org's Legge edition, though the page history (2017) names no source. It is therefore
written but catalogued only when asked for by name (OPT_IN). Legge's notes, his paragraph numbers, and the etexts' page
markers and footnotes are left out.
Chinese: Chinese Wikisource (zh.wikisource.org), public domain.
  Dao De Jing     Wang Bi's text, his commentary left out.
  Great Learning, Mean   Zhu Xi's Sishu zhangju, the arrangement Legge translated. Zhu's notes, his preface and "右…章"
                  colophons, and his own supplement to the Great Learning's fifth commentary chapter (which Legge does
                  not translate) are left out. What remains is checked against the Liji chapters: the same characters,
                  variant forms (後/后, 爲/為) aside.
  Analects, Mencius, Zhuangzi   as Wikisource gives them, its editors' collation notes left out.
Variant readings keep Wikisource's main reading.

How each pair is aligned, at the level where the two agree:
  Dao De Jing   chapter (81). Legge's paragraphs within a chapter follow no Chinese edition's breaks. His English names
                for the chapters (Ho-shang Kung's titles) are the entries' titles.
  Analects      book.chapter (20 books, 499 chapters): Legge's numbering, which is Zhu Xi's. Legge printed the Chinese
                above his English, and Wikisource transcribes both on one page. His Chinese chapter marks (【第N章】) and
                English headings ("Chapter N.") must number alike, book by book. That transcription of his Chinese
                breaks off in places (XV.30, XVI.14), so the Chinese shown is Chinese Wikisource's. Each of Legge's
                chapters takes the Wikisource chapter that best shares its characters, or two where Wikisource cuts
                one of Legge's in two (V.1, and IX.6, whose fourth section 牢曰 Wikisource makes a chapter of its own).
  Great Learning  part.chapter: 1.1 the Text of Confucius (經), 2.1–2.10 the ten chapters of the Commentary of the
                philosopher Tsang (傳). The etext carries no chapter numbers; each chapter is found by its opening words,
                and each must quote the Master and the Odes as often as its Chinese.
  Mean          chapter (33), Zhu Xi's, found and checked the same way.
  Mencius       book.part.chapter (7 books × 2 parts, 260 chapters). Wikisource's English pages set each paragraph of
                Chinese over its English but do not mark chapters. Each paragraph is placed in a Chinese Wikisource
                chapter (===N===) by lining the two Chinese texts up character by character, and a paragraph that would
                fall across two chapters stops the script.
  Zhuangzi      chapter (33). Legge's numbered paragraphs and Wikisource's break at different places (Book I: Legge's
                §2 opens at 且夫水之積, Wikisource's second paragraph at 蜩與鷽鳩), so nothing finer holds.
Every chapter is also checked by the ratio of English words to Chinese characters, and outliers are printed.

Writes public/data/china/<id>.json. With --catalog, also adds the texts to library_catalog.json and
translation_sources.json. Rerunnable; Wikisource API responses are cached in cache/wikisource, the sacred-texts pages in
cache/sacred_texts.
Usage: .venv/bin/python -I scripts/corpus2/chinese_classics.py [--catalog] [text id …]
  With no ids, all six are written and all but the Mencius catalogued; name ids to build (and catalogue) only those.
"""
import difflib
import gzip
import hashlib
import html
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WS_CACHE = os.path.join(ROOT, "cache", "wikisource")
ST_CACHE = os.path.join(ROOT, "cache", "sacred_texts")
OUT = os.path.join(ROOT, "public", "data", "china")
UA = "rigved-corpus-research/1.0 (https://github.com/iashris/rigved)"
sys.path.insert(0, HERE)

ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
          "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX", "XXXI", "XXXII", "XXXIII"]
ORIGINAL = {"name": "Classical Chinese", "lang": "lzh", "label": "文言", "short": "文"}
BAND = {"id": "china", "after": ["near_east", "kin"], "name": "Chinese classics",
        "blurb": "not Indic: the Dao, the way of heaven and earth, beside ṛta, the Veda's order of the world — Laozi's Dao De Jing, "
                 "the Four Books of Confucius and Mencius, and the Zhuangzi. Classical Chinese with James Legge's English"}


# ---------------------------------------------------------------- fetching

def wikitext(host, title):
    """A page's wikitext through the MediaWiki API (action=parse), one request at a time. Wikitext and not HTML because
    the marks the pairing hangs on (Zhu Xi's {{annotate}} notes, Legge's 【第一章】, ===N=== chapters) are clearest there."""
    os.makedirs(WS_CACHE, exist_ok=True)
    f = os.path.join(WS_CACHE, f"{host}-" + hashlib.sha1(title.encode()).hexdigest() + ".json")
    if not os.path.exists(f):
        q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "wikitext", "format": "json", "formatversion": "2", "redirects": "1"})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"https://{host}.wikisource.org/w/api.php?{q}", headers={"User-Agent": UA}), timeout=90) as r:
                    data = json.load(r)
                break
            except (OSError, ValueError) as e:
                print(f"  retry {title}: {e}", flush=True)
                time.sleep(10 * (attempt + 1))
        else:
            raise SystemExit(f"{host}:{title}: could not fetch")
        if "error" in data:
            raise SystemExit(f"{host}:{title}: {data['error'].get('info')}")
        json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(1)
    return json.load(open(f, encoding="utf-8"))["parse"]["wikitext"]


def _curl(url):
    for attempt in range(8):
        r = subprocess.run(["curl", "-sL", "-m", "90", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
        body, _, code = r.stdout.rpartition(b"\n")
        code = int(code or 0)
        if r.returncode == 0 and code == 200:
            time.sleep(1.5)
            return body
        if code in (402, 404):
            return None
        print(f"  retry {code} {url}", flush=True)
        time.sleep(15 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}")


def sacred(path):
    """A sacred-texts.com page from the Wayback Machine's 2022 capture (the newest good one, from the CDX index, if that
    is missing), cached under cache/sacred_texts/<path>. Archive bodies sometimes come gzipped twice."""
    f = os.path.join(ST_CACHE, path)
    if not os.path.exists(f):
        b = _curl(f"https://web.archive.org/web/2022id_/https://sacred-texts.com/{path}")
        if b is None:
            rows = _curl(f"https://web.archive.org/cdx/search/cdx?url=sacred-texts.com/{path}&filter=statuscode:200&fl=timestamp,original")
            rows = sorted(r.split() for r in (rows or b"").decode().split("\n") if r.strip())
            if not rows:
                raise SystemExit(f"{path}: no archived copy")
            b = _curl(f"https://web.archive.org/web/{rows[-1][0]}id_/{rows[-1][1]}")
        while b[:2] == b"\x1f\x8b":
            b = gzip.decompress(b)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "wb").write(b)
    b = open(f, "rb").read()
    for enc in ("utf-8", "cp1252"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("latin-1")


# ---------------------------------------------------------------- cleaning

def drop_template(t, name, keep_first=False):
    """Remove every {{name|…}}, nested templates and all; or, with keep_first, put its first argument in its place."""
    out, i = [], 0
    while (j := t.find("{{" + name + "|", i)) >= 0:
        out.append(t[i:j])
        depth, links, k, bar = 0, 0, j, None
        while k < len(t):
            if t.startswith("{{", k):
                depth, k = depth + 1, k + 2
            elif t.startswith("}}", k):
                depth, k = depth - 1, k + 2
                if depth == 0:
                    break
            elif t.startswith("[[", k) or t.startswith("]]", k):
                links, k = links + (1 if t[k] == "[" else -1), k + 2
            else:
                if t[k] == "|" and depth == 1 and links == 0 and k > j + len(name) + 2 and bar is None:
                    bar = k
                k += 1
        if keep_first:
            out.append(t[j + len(name) + 3:bar if bar is not None else k - 2])
        i = k
    return "".join(out) + t[i:]


def zh(t):
    """Chinese wikitext to plain text: variant readings {{另|a|b}} keep the main reading a, -{x}- language-conversion
    guards and links keep their text, spacing templates and all whitespace go (Classical Chinese has none)."""
    t = drop_template(t, "annotate")
    t = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = drop_template(drop_template(t, "另2", keep_first=True), "另", keep_first=True)
    t = re.sub(r"-\{([^{}]*)\}-", lambda m: m.group(1).split(";")[0].split(":")[-1], t)  # -{zh:顚;zh-hant:顛}-: the first form
    t = re.sub(r"\{\{(?:gap|reflist)(\|[^{}]*)?\}\}", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"[\s　]+", "", html.unescape(t))
    if re.search(r"[{}\[\]|=A-Za-z<>]|-\{", t):
        raise SystemExit(f"markup left in the Chinese: {t[:200]}")
    return t


def en(t):
    """English wikitext (the Analects page) to plain text."""
    t = re.sub(r"\{\{sc\|([^{}]*)\}\}", r"\1", t)
    t = re.sub(r"'''?", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"<br\s*/?>", " ", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    if "{{" in t or "[[" in t:
        raise SystemExit(f"markup left in the English: {t[:200]}")
    return re.sub(r"[^\S\n]+", " ", t).strip()


def page_body(t):
    """A Chinese Wikisource page without its header box, quality and licence templates and category links."""
    t = drop_template(drop_template(t, "header2"), "header")
    t = drop_template(drop_template(t, "Header"), "道藏header")
    while re.search(r"\{\{(?!另2?\||annotate\|)[^{}]*\}\}", t):
        t = re.sub(r"\{\{(?!另2?\||annotate\|)[^{}]*\}\}", "", t)
    return re.sub(r"\[\[(?:[Cc]ategory|分類|[a-z]{2,3}):[^\]]*\]\]", "", t)


def cn(s):
    """Chinese numerals as Legge's Chinese and Wikisource write them: 十一, 二十, 廿一, 卅一, and 四一 for 41."""
    d = dict(zip("〇一二三四五六七八九", range(10)))
    s = s.replace("第", "").replace("廿", "二十").replace("卅", "三十")
    if "百" in s:
        h, s = s.split("百")
        return d[h] * 100 + (cn(s.lstrip("〇零")) if s else 0)
    if "十" in s:
        a, b = s.split("十")
        return (d[a] if a else 1) * 10 + (d[b] if b else 0)
    n = 0
    for c in s:
        n = n * 10 + d[c]
    return n


def roman(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    return sum(-v[a] if v[a] < v[b] else v[a] for a, b in zip(s, s[1:] + "I")) if s else 0


def no_punct(s):
    return re.sub(r"[^㐀-鿿豈-﫿]", "", s)


# Slips in the sacred-texts etexts, each must occur exactly once. Those in the Great Learning and the Mean were found by
# setting the etexts beside Wikisource's independent transcription of the same Legge; those in the Zhuangzi, which has
# no second transcription, by a sweep for a full stop followed by a lower-case word.
FIXES = {
    "daxue": [('That expression-"As we cut and then file," the work', 'That expression-"As we cut and then file," indicates the work'),
              ('depends on the government of his state," this:', 'depends on the government of his state," is this:'),
              ("the people become final;", "the people become filial;"),
              ("Auddle Kingdom", "Middle Kingdom"),
              ("therewith the. sovereign", "therewith the sovereign")],
    "zhongyong": [("you cannot sunrise;", "you cannot surmise;"),
                  ("had they been continued among them.", "had they been continued among them;-the height of filial piety."),
                  ("Wan and Wul taking", "Wan and Wu, taking"),
                  ("large emolument. and sharing", "large emolument, and sharing")],
    "zhuangzi": [("(as with a. friend)", "(as with a friend)"), ("with me, however. for many months", "with me, however, for many months"),
                 ("belonging to it. complete in those", "belonging to it, complete in those"),
                 ("a real existence. but it has", "a real existence, but it has"), ("ask the way. just then", "ask the way. Just then"),
                 ("to get a meal. and in five", "to get a meal, and in five")],
}


def fix(tid, t):
    for a, b in FIXES.get(tid, []):
        if t.count(a) != 1:
            raise SystemExit(f"{tid}: fix {a!r} matches {t.count(a)} times")
        t = t.replace(a, b)
    return t


def sacred_soup(path):
    """A sacred-texts page with its scripts, page-number markers and footnote references gone."""
    soup = BeautifulSoup(sacred(path), "html.parser")
    for el in soup.find_all(["script", "style"]):
        el.decompose()
    for a in soup.find_all("a"):
        if (a.get("name") or "").startswith("page_") or (a.get("href") or "").split("#")[-1].startswith("fn_"):
            a.decompose()
    return soup


def para_text(p):
    for br in p.find_all("br"):
        br.replace_with(" ")
    t = re.sub(r"\xa0+(?=[\s,.;:!?'\"’”)\]-]|$)", "", p.get_text())  # the space before a footnote mark, now gone
    t = re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()
    t = re.sub(r"(?<=[\w)'’]) +(?=[,.;:!?])", "", t)  # "Tho [3] . His": the space the mark stood in
    t = re.sub(r"(?<=\s)\.(?=[A-Z])", "", t)  # a stray stop: "Not long after this, .Dze-khî sent"
    return t.replace(" -- ", "--").replace("-- ", "--")


# ---------------------------------------------------------------- the texts

def daodejing():
    w = wikitext("zh", "道德經 (王弼本)")
    chunks = re.split(r"^==\s*([一二三四五六七八九十]+)章\s*==\s*$", w, flags=re.M)
    zhs = {}
    for num, body in zip(chunks[1::2], chunks[2::2]):
        body = re.split(r"^=", body, maxsplit=1, flags=re.M)[0]  # after 81 come the postscripts and Lu Deming's glosses
        keep = [ln for ln in body.split("\n") if ln.strip() and not ln.startswith((":", "{{", "[[", "<"))]
        zhs[cn(num)] = zh("".join(keep))
    if sorted(zhs) != list(range(1, 82)):
        raise SystemExit(f"Wang Bi text: chapters {sorted(zhs)[:5]}…, {len(zhs)} in all")
    rows = []
    for n in range(1, 82):
        soup = sacred_soup(f"tao/sbe39/sbe39{n + 7:03d}.htm")
        paras, title, started = [], None, False
        for el in soup.find_all(["h3", "p"]):
            if el.name == "h3":
                if re.fullmatch(r"\s*\d+\.\s*", el.get_text()):
                    if int(el.get_text().strip(" .\n")) != n:
                        raise SystemExit(f"sbe39 page for chapter {n} is chapter {el.get_text()}")
                    started = True
                continue
            if not started and re.match(rf"(Ch\. )?{n}\. ", para_text(el)):  # some pages lack the <h3> number
                started = True
            if not started:
                continue
            if el.find("img"):  # Legge's notes begin with the chapter's Chinese title, printed as an image, then his English for it
                note = para_text(el)
                m = re.match(r"\s*[,;]?\s*'(.+?)[.,;]?'(?=[\s-]|$)", note) or re.match(r"\s*[,;]?\s*'([^'!]+!)", note)
                title = m.group(1) if m else None
                noted = True
                break
            t = para_text(el)
            if t:
                t = re.sub(rf"^(Ch\. )?{n}\. ", "", t) if not paras else t
                paras.append(re.sub(r"^\d+\. ", "", t))
        else:
            noted = False
        if not paras or not noted:
            raise SystemExit(f"Dao De Jing {n}: {len(paras)} paragraphs, notes found: {noted}")
        rows.append({"reference": str(n), "original": zhs[n], "text": "\n\n".join(join_broken(paras)), **({"title": title} if title else {})})
    print(f"  Dao De Jing: Legge renders no title for chapters {[r['reference'] for r in rows if 'title' not in r]}")
    return rows


def join_broken(paras):
    """A paragraph that stops without closing punctuation ("…The" / "Master said"), or is followed by one that opens in
    lower case, runs on into the next: the transcription broke it at a page."""
    out = []
    for p in paras:
        if out and (not re.search(r"[.?!:;\"'”’)\]—-]$", out[-1]) or re.match(r"[a-z]", p)):
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def shared(a, b):
    return sum(m.size for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks())


def pair_runs(guide, chunks):
    """Give each guide text a run of one or two consecutive chunks, all chunks used in order, so that the characters
    they share, less those either side has alone, are greatest. Yields (guide index, first chunk index, run)."""
    plain = [no_punct(c) for c in chunks]
    n, m = len(guide), len(chunks)
    best = {(0, 0): (0, None)}
    for i in range(n):
        for j in range(m):
            if (i, j) not in best:
                continue
            for k in (1, 2):
                if j + k > m:
                    continue
                got = "".join(plain[j:j + k])
                score = best[(i, j)][0] + 2 * shared(guide[i], got) - len(guide[i]) - len(got)
                if (i + 1, j + k) not in best or score > best[(i + 1, j + k)][0]:
                    best[(i + 1, j + k)] = (score, (j, k))
    if (n, m) not in best:
        raise SystemExit(f"{n} chapters cannot be made from {m}")
    out, i, j = [], n, m
    while i:
        pj, k = best[(i, j)][1]
        out.append((i - 1, pj, chunks[pj:pj + k]))
        i, j = i - 1, pj
    return out[::-1]


# Chapters whose English heading Wikisource mistypes (II.18 is headed "XVII"); the Chinese 【十八章】 above it and the
# order of the page settle them.
ANALECTS_MISNUMBERED = {("II", 18)}


def analects():
    zh_books = re.findall(r"\[\[/([^|\]]+第[^|\]]+)\|", wikitext("zh", "論語"))[:20]
    rows, check, section_slips, joined, cover = [], [], [], [], []
    for b, r in enumerate(ROMANS[:20], 1):
        w = wikitext("en", f"The Chinese Classics/Volume 1/Confucian Analects/{r}")
        name = re.search(r"\|\s*section\s*=\s*(.+)", w).group(1).strip()
        # The page mostly alternates a chapter's Chinese and its English, but a Chinese block can hold several chapters
        # or break off mid-chapter, so the Chinese is read as one run cut at Legge's 【N章】 marks and the English as
        # one run cut at his "Chapter N." headings, and the two lists are paired by number.
        parts = re.split(r"\{\{lang(?: block)?\|zh\|(.*?)\}\}", w, flags=re.S)
        book_zh = zh(next(c for c in parts[1::2] if "章】" not in c))
        chinese = "".join(c for c in parts[1::2] if "】" in c)
        zch = re.split(r"【(第?[一二三四五六七八九十廿卅]+)章】", chinese)
        english = drop_template("\n\n".join(parts[0::2]), "header")
        while re.search(r"\{\{(?!sc\|)[^{}]*\}\}", english):  # licence and category boxes; small caps kept for en()
            english = re.sub(r"\{\{(?!sc\|)[^{}]*\}\}", "", english)
        english = en(english)
        ech = re.split(r"(?:^|\n)\s*Chapter ([IVXLC]+)\.? ?", english)
        if len(zch) != len(ech):
            raise SystemExit(f"Analects {r}: {len(zch) // 2} Chinese chapters, {len(ech) // 2} English")
        chapters = []
        for zn, zt, en_n, et in zip(zch[1::2], zch[2::2], ech[1::2], ech[2::2]):
            secs_zh = len(re.findall(r"【[一二三四五六七八九十]+節】", zt)) or 1
            paras = join_broken([p.strip() for p in re.split(r"\n\s*\n", et) if p.strip()])
            nums = [int(x.group(1)) for p in paras if (x := re.match(r"(\d+)\.(?= |[A-Z\"'])", p))]
            chapters.append((cn(zn), roman(en_n), secs_zh, len(nums) or 1,
                             zh(re.sub(r"【[^】]*】", "", zt)), "\n\n".join(re.sub(r"^\d+\.(?= |[A-Z\"'])\s*", "", p) for p in paras)))
        n = len(chapters)
        slips = {(r, i) for i, c in enumerate(chapters, 1) if c[1] != i}
        if [c[0] for c in chapters] != list(range(1, n + 1)) or slips - ANALECTS_MISNUMBERED:
            raise SystemExit(f"Analects {r}: Chinese {[c[0] for c in chapters]} English {[c[1] for c in chapters]}")
        section_slips.extend((f"{b}.{i}", c[2], c[3]) for i, c in enumerate(chapters, 1) if c[2] != c[3])
        # The Chinese itself comes from Chinese Wikisource, complete where the transcription of Legge's Chinese breaks
        # off (XV.30, XVI.14). Each of Legge's chapters takes one Wikisource chapter, or two where Wikisource splits it
        # (V.1, and IX.6, whose fourth section 牢曰 Wikisource makes a chapter of its own); which, is settled for the
        # whole book at once by the characters the two share.
        zw = wikitext("zh", "論語/" + zh_books[b - 1]).split("<onlyinclude>")[-1].split("</onlyinclude>")[0]
        zw = re.split(r"^=", zw, maxsplit=1, flags=re.M)[0]  # some books end with a 校勘記, the editors' collation notes
        wsc = [zh(x) for x in re.split(r'<div id="[一二三四五六七八九十]+之[一二三四五六七八九十]+"[^>]*>.*?</div>', zw)[1:]]
        for i, j, take in pair_runs([no_punct(c[4]) for c in chapters], wsc):
            c, legge, got = chapters[i], no_punct(chapters[i][4]), no_punct("".join(take))
            if len(take) > 1:
                joined.append(f"{b}.{i + 1}")
            cover.append((f"{b}.{i + 1}", shared(legge, got) / len(legge), len(legge), len(got)))
            rows.append({"reference": f"{b}.{i + 1}", "original": "".join(take), "text": c[5],
                         **({"title": f"Book {name.removeprefix('Book ')} · {book_zh}"} if i == 0 else {})})
        check.append((r, n, len(wsc), sum(c[2] for c in chapters)))
    print("  Analects chapters per book, Legge / zh.wikisource: " + ", ".join(f"{r} {n}/{w}" for r, n, w, _ in check))
    print(f"  Analects: zh.wikisource chapters joined to make Legge's: {joined}")
    low = [(ref, round(x, 2), a, g) for ref, x, a, g in cover if x < 0.9]
    print(f"  Analects: share of the characters Legge printed found in the zh.wikisource chapter: median {statistics.median(x for _, x, _, _ in cover):.3f};"
          f" under 0.9 (chapter, share, Legge's, zh.wikisource's): {low or 'none'}")
    short = [(ref, a, g) for ref, x, a, g in cover if a < 0.8 * g]
    print(f"  Analects: chapters where the transcription of Legge's Chinese is short of zh.wikisource's (chapter, Legge's, zh.wikisource's): {short}")
    print(f"  Analects: {sum(c[3] for c in check)} sections (節); chapters whose 節 and numbered English paragraphs differ (chapter, 節, English): {section_slips}")
    return rows


def etext(path, tid):
    """The Confucian etexts on sacred-texts (one <pre>-like page): paragraphs start with a three-space indent."""
    raw = sacred(path)
    raw = re.sub(r"(?s)<script.*?</script>", "", raw)
    t = html.unescape(re.sub(r"(?s)<[^>]+>", "", raw))
    t = t[t.index("translated by James Legge"):].split("\n", 1)[1]
    t = t[:t.rindex("THE END")]
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n {3}(?=\S)", t)]
    return [p for p in paras if p]


def by_anchors(paras, anchors, tid):
    """Cut a run of paragraphs into chapters at the paragraphs that open with each anchor, in order."""
    text = "\n\n".join(paras)
    text = fix(tid, text)
    starts = []
    for a in anchors:
        hits = [m.start() for m in re.finditer(r"(?:^|\n\n)" + re.escape(a), text)]
        if len(hits) != 1:
            raise SystemExit(f"{tid}: anchor {a!r} opens {len(hits)} paragraphs")
        starts.append(hits[0])
    if starts != sorted(starts):
        raise SystemExit(f"{tid}: anchors out of order")
    return [text[s:e].strip() for s, e in zip(starts, starts[1:] + [len(text)])]


def zhu_xi(title):
    """Zhu Xi's Sishu zhangju text as chapters: the paragraphs between his 右…章 colophons, his notes and his own prose
    (the 子程子曰 preface, the colophons and what follows them, the supplied fifth commentary chapter of the Great
    Learning) dropped. In the Mean all of Zhu's own prose is set in on lines that open with "::"."""
    w = drop_template(wikitext("zh", title), "annotate")
    w = w[w.index("}}", w.index("{{header")) + 2:]
    chapters, cur = [], []
    for ln in w.split("\n"):
        s = re.sub(r"\{\{gap(\|[^{}]*)?\}\}", "", ln).strip(" 　:")
        if not s or s.startswith(("{{left-right", "{{wikipedia", "{{PD", "[[category", "[[Category")):
            continue
        if s.startswith("右"):
            chapters.append(zh("".join(cur)))
            cur = []
            continue
        if ln.startswith("::") or s.startswith("子程子曰"):
            continue
        cur.append(s.removeprefix("中庸章句"))  # the Mean's first line carries the book's title before its text
    if zh("".join(cur)):
        raise SystemExit(f"{title}: text after the last colophon: {zh(''.join(cur))[:60]}")
    return chapters


def against_liji(tid, chapters, liji):
    """Zhu Xi rearranged the Great Learning but kept its characters; the Mean he kept in order. Report the difference
    from the Liji chapter, punctuation aside."""
    from collections import Counter
    ours, theirs = Counter(no_punct("".join(chapters))), Counter(no_punct(zh(page_body(wikitext("zh", liji)))))
    extra, missing = ours - theirs, theirs - ours
    print(f"  {tid}: {sum(ours.values())} characters; against {liji}: {sum(extra.values())} more, {sum(missing.values())} fewer"
          f" {''.join(sorted(extra.elements()))[:40]} / {''.join(sorted(missing.elements()))[:40]}")


DAXUE_ANCHORS = ["What the Great Learning teaches", "In the Announcement to K'ang, it is said, \"He was able", "On the bathing tub of T'ang",
                 "In the Book of Poetry, it is said, \"The royal domain", "The Master said, \"In hearing litigations",
                 "This is called knowing the root. This is called the perfecting", "What is meant by \"making the thoughts sincere",
                 "What is meant by, \"The cultivation of the person", "What is meant by \"The regulation of one's family",
                 "What is meant by \"In order rightly to govern", "What is meant by \"The making the whole kingdom"]
DAXUE_TITLES = ["The Text of Confucius · 經一章"] + [f"Commentary of the philosopher Tsang, chapter {ROMANS[i]} · 傳之{'首' if i == 0 else '二三四五六七八九十'[i - 1]}章 · {t}"
                                                      for i, t in enumerate(["釋明明德", "釋新民", "釋止於至善", "釋本末", "釋格物致知", "釋誠意",
                                                                             "釋正心脩身", "釋脩身齊家", "釋齊家治國", "釋治國平天下"])]


def marker_check(tid, rows):
    """For the texts cut by hand-picked opening words: in each chapter, the sayings of the Master and the quotations
    from the Odes should be as many in the English as in the Chinese."""
    odd = []
    for r in rows:
        zh_master = len(re.findall(r"(?:^|[。」；：，！？])(?:子|仲尼|孔子)曰", r["original"]))
        en_master = len(re.findall(r"The Master said|Chung-ni said|Confucius said", r["text"]))
        zh_ode = len(re.findall(r"《詩》|詩云|詩曰", r["original"]))
        en_ode = len(re.findall(r"Book of Poetry|another ode", r["text"]))
        if zh_master != en_master or zh_ode != en_ode:
            odd.append((r["reference"], f"子曰 {zh_master}/{en_master}", f"詩 {zh_ode}/{en_ode}"))
    print(f"  {tid}: chapters whose sayings of the Master or quotations from the Odes differ in number, Chinese/English: {odd or 'none'}")


def daxue():
    paras = etext("cfu/conf2.htm", "daxue")
    paras = [p.replace("WHAT THE GREAT LEARNING teaches", "What the Great Learning teaches") for p in paras]
    paras = [re.sub(r"\s*COMMENTARY OF THE PHILOSOPHER TSANG\s*$", "", p) for p in paras]
    english = by_anchors(paras, DAXUE_ANCHORS, "daxue")
    chinese = zhu_xi("四書章句集註/大學章句")
    if len(chinese) != 11:
        raise SystemExit(f"Great Learning: {len(chinese)} Chinese chapters")
    against_liji("daxue", chinese, "禮記/大學")
    refs = ["1.1"] + [f"2.{i}" for i in range(1, 11)]
    rows = [{"reference": r, "original": c, "text": e, "title": t} for r, c, e, t in zip(refs, chinese, english, DAXUE_TITLES)]
    marker_check("daxue", rows)
    return rows


ZHONGYONG_ANCHORS = ["What Heaven has conferred", "Chung-ni said, \"The superior man embodies", "The Master said, \"Perfect is the virtue",
                     "The Master said, \"I know how it is", "The Master said, \"Alas!", "The Master said, \"There was Shun",
                     "The Master said \"Men all say", "The Master said \"This was the manner of Hui", "The Master said, \"The kingdom, its states",
                     "Tsze-lu asked about energy", "The Master said, \"To live in obscurity", "The way which the superior man pursues",
                     "The Master said \"The path is not far from man", "The superior man does what is proper to the station",
                     "The way of the superior man may be compared to what takes place in traveling", "The Master said, \"How abundantly do spiritual beings",
                     "The Master said, \"How greatly filial was Shun", "The Master said, \"It is only King Wan", "The Master said, \"How far-extending",
                     "The Duke Ai asked about government", "When we have intelligence resulting from sincerity",
                     "It is only he who is possessed of the most complete sincerity", "Next to the above", "It is characteristic of the most entire sincerity",
                     "Sincerity is that whereby self-completion", "Hence to entire sincerity there belongs ceaselessness", "How great is the path proper to the Sage",
                     "The Master said, Let a man who is ignorant", "He who attains to the sovereignty", "Chung-ni handed down",
                     "It is only he, possessed of all sagely qualities", "It is only the individual possessed of the most entire sincerity",
                     "It is said in the Book of Poetry, \"Over her embroidered robe"]


def zhongyong():
    english = by_anchors(etext("cfu/conf3.htm", "zhongyong"), ZHONGYONG_ANCHORS, "zhongyong")
    chinese = zhu_xi("四書章句集註/中庸章句")
    if len(chinese) != 33:
        raise SystemExit(f"Mean: {len(chinese)} Chinese chapters")
    against_liji("zhongyong", chinese, "禮記/中庸")
    rows = [{"reference": str(i), "original": c, "text": e} for i, (c, e) in enumerate(zip(chinese, english), 1)]
    marker_check("zhongyong", rows)
    return rows


MENCIUS_PARTS = ["梁惠王上", "梁惠王下", "公孫丑上", "公孫丑下", "滕文公上", "滕文公下", "離婁上", "離婁下", "萬章上", "萬章下", "告子上", "告子下", "盡心上", "盡心下"]


def mencius():
    """Legge's English from Wikisource's book pages, where each paragraph of Chinese stands over its English but the
    chapters are not marked. Each paragraph is placed in a Chinese Wikisource chapter (===N===) by lining up the two
    Chinese texts character by character; a paragraph that would fall across two chapters stops the script."""
    rows, counts, straddle, weak = [], [], [], []
    # The parts' English names as Wikisource's contents page gives them ("Liang Hui Wang I"), in its pinyin.
    names = dict(re.findall(r"\{\{lang\|zh\|([^}]+)\}\} - ([^\]]+)\]\]", wikitext("en", "The Chinese Classics/Volume 2/The Works of Mencius")))
    if sorted(names) != sorted(MENCIUS_PARTS):
        raise SystemExit(f"Mencius contents page: {names}")
    for p, part in enumerate(MENCIUS_PARTS):
        w = wikitext("zh", f"孟子/{part}")
        w = re.split(r"^==[^=]", w.split("<onlyinclude>")[-1].split("</onlyinclude>")[0], maxsplit=1, flags=re.M)[0]
        bits = re.split(r"^===\s*(\d+)\s*===\s*$", w, flags=re.M)
        zch = [zh(x) for x in bits[2::2]]
        if [int(x) for x in bits[1::2]] != list(range(1, len(zch) + 1)):
            raise SystemExit(f"孟子/{part}: chapters {bits[1::2]}")
        # Legge's paragraphs, each with the Chinese printed over it.
        page = wikitext("en", f"The Chinese Classics/Volume 2/The Works of Mencius/chapter{p + 1:02d}")
        page = drop_template(page, "header")
        parts = re.split(r"\{\{lang\|zh\|(.*?)\}\}", page, flags=re.S)
        pairs = []
        for chinese, after in zip(parts[1::2], parts[2::2]):
            if zh(chinese) == part:
                continue  # the page's own title
            after = re.sub(r"\{\{[^{}]*\}\}", "", after)
            paras = join_broken([en(x) for x in re.split(r"\n\s*\n", after) if en(x)])
            if not paras:
                raise SystemExit(f"Mencius {part}: no English under {zh(chinese)[:20]}")
            pairs.append((no_punct(zh(chinese)), paras))
        # Line the paragraphs' Chinese up against the chapters' and give each paragraph the chapter its middle falls in.
        a = "".join(c for c, _ in pairs)
        bz = "".join(no_punct(c) for c in zch)
        starts, at = [], 0
        for c in zch:
            starts.append(at)
            at += len(no_punct(c))
        blocks = difflib.SequenceMatcher(None, a, bz, autojunk=False).get_matching_blocks()

        def chapter(j):
            return max(k for k, s0 in enumerate(starts) if s0 <= j)

        english = [[] for _ in zch]
        pos = 0
        for c, paras in pairs:
            # Where this paragraph's matched characters fall, chapter by chapter; it belongs where most of them do.
            hits = {}
            for blk in blocks:
                lo, hi = max(blk.a, pos), min(blk.a + blk.size, pos + len(c))
                for i in range(lo, hi):
                    k = chapter(blk.b + i - blk.a)
                    hits[k] = hits.get(k, 0) + 1
            if not hits:
                raise SystemExit(f"Mencius {part}: paragraph {c[:12]} matches nothing")
            first = max(hits, key=hits.get)
            if sorted(hits.values())[-2:][0] > 0.25 * sum(hits.values()) and len(hits) > 1:
                straddle.append((part, sorted(k + 1 for k in hits), c[:12]))
            english[first].extend(paras)
            pos += len(c)
        for k, c in enumerate(zch):
            if not english[k]:
                raise SystemExit(f"Mencius {part} {k + 1}: no English paragraph falls in this chapter")
        got = shared(a, bz)
        weak.append((part, round(got / len(bz), 3), round(got / len(a), 3)))
        counts.append((part, len(zch)))
        book, half = p // 2 + 1, p % 2 + 1
        for k, (chinese, paras) in enumerate(zip(zch, english), 1):
            title = {"title": f"Book {ROMANS[book - 1]}, Part {'I' * half}. {names[part]} · {part}"} if k == 1 else {}
            rows.append({"reference": f"{book}.{half}.{k}", "original": chinese, "text": "\n\n".join(join_broken(paras)), **title})
    if straddle:
        raise SystemExit(f"Mencius: paragraphs across two chapters (part, chapters, opening): {straddle}")
    print("  Mencius chapters per part (zh.wikisource ===N===):", ", ".join(f"{p} {n}" for p, n in counts), f"= {sum(n for _, n in counts)}")
    print("  Mencius: share of zh.wikisource's characters matched by the Chinese over Legge's paragraphs, and the reverse, per part:", weak)
    return rows


def zhuangzi():
    names = re.findall(r"\*\[\[/([^|\]]+)\|", wikitext("zh", "莊子"))[:33]
    pages = [f"tao/sbe39/sbe39{n:03d}.htm" for n in range(122, 139)] + [f"tao/sbe40/sbe40{n:02d}.htm" for n in range(2, 18)]
    rows, ones = [], 0
    for i, (name, page) in enumerate(zip(names, pages), 1):
        soup = sacred_soup(page)
        heads = [para_text(h) for h in soup.find_all("h3")]
        heads = heads[next(k for k, h in enumerate(heads) if h.startswith("PART")) + 1:]  # the book's name follows its part and section
        book = next((h for h in soup.find_all(["h2", "h3"]) if re.match(r"BOOK ([IVXL]+)", h.get_text().strip())), None)
        if not book or book.get_text().strip().rstrip(".").split()[-1] != ROMANS[i - 1]:
            raise SystemExit(f"{page} is not Book {ROMANS[i - 1]}: {book and book.get_text()!r}")
        name_en = heads[0]
        if name_en == "Footnotes":
            raise SystemExit(f"{page}: no title")
        paras = []
        for el in soup.find_all(["p", "h3"]):
            if el.name == "h3":
                if el.get_text().strip() == "Footnotes":
                    break
                continue
            cont = el.find(string=re.compile(r"\[paragraph continues\]"))
            if cont:
                cont.extract()
            t = para_text(el)
            if not t or re.fullmatch(r"p\. \d+", t):
                continue
            if cont and paras:
                paras[-1] += " " + t
            else:
                paras.append(t)
        paras = join_broken([re.sub(r"^\d+\. ", "", p) for p in paras])
        text, n_i = re.subn(r"(?<=[A-Za-z,;] )1(?=,? [a-z])", "I", "\n\n".join(paras))  # the etext's "when 1 sent you"
        ones += n_i
        chinese = page_body(wikitext("zh", f"莊子/{name}"))
        rows.append({"reference": str(i), "original": zh(chinese), "text": text,
                     "title": f"{ROMANS[i - 1]}. {re.sub(r'[.](?=\'?$)', '', name_en)} · {name}"})
    for a, b in FIXES["zhuangzi"]:
        if sum(r["text"].count(a) for r in rows) != 1:
            raise SystemExit(f"zhuangzi: fix {a!r} matches {sum(r['text'].count(a) for r in rows)} times")
        for r in rows:
            r["text"] = r["text"].replace(a, b)
    print(f"  Zhuangzi: {ones} times the etext's figure 1 standing for the word I, set right; {len(FIXES['zhuangzi'])} other slips")
    return rows


# ---------------------------------------------------------------- checks and output

def ratio_check(tid, rows):
    """English words per Chinese character, chapter by chapter; a chapter far from the text's median is printed."""
    rs = [(r["reference"], len(r["text"].split()) / max(1, len(no_punct(r["original"])))) for r in rows]
    med = statistics.median(x for _, x in rs)
    odd = [(ref, round(x / med, 2)) for ref, x in rs if not 0.5 <= x / med <= 2.0]
    print(f"  {tid}: {len(rows)} entries, median {med:.2f} English words per character; outside ½–2× the median: {odd or 'none'}")
    return odd


TEXTS = [
    ("daodejing", daodejing, {"name": "Laozi, Dao De Jing", "levels": ["Chapter"], "date": [-400, -250],
                              "source": "Chinese: Wang Bi's text, from Chinese Wikisource; English: James Legge, Sacred Books of the East 39 (1891), from sacred-texts.com"},
     {"by": "James Legge", "work": "The Texts of Taoism, Part I: The Tâo Teh King, Sacred Books of the East vol. 39, Oxford: Clarendon Press", "year": "1891",
      "links": [{"label": "sacred-texts.com", "url": "https://sacred-texts.com/tao/sbe39/index.htm"}],
      "via": {"label": "Internet Archive", "url": "https://web.archive.org/web/2022/https://sacred-texts.com/tao/sbe39/index.htm"},
      "note": "Public domain; Legge's notes left out. Chinese: Wang Bi's text of the Laozi (道德經 (王弼本)), from Chinese Wikisource, his commentary left out.",
      "zh": "https://zh.wikisource.org/wiki/道德經_(王弼本)"}),
    ("analects", analects, {"name": "Confucius, The Analects", "levels": ["Book", "Chapter"], "date": [-475, -250],
                            "source": "Chinese: Chinese Wikisource; English: James Legge, The Chinese Classics vol. 1 (1893), from English Wikisource"},
     {"by": "James Legge", "work": "The Chinese Classics, vol. 1: Confucian Analects, The Great Learning, and The Doctrine of the Mean, 2nd ed., Oxford: Clarendon Press", "year": "1893",
      "links": [{"label": "Wikisource", "url": "https://en.wikisource.org/wiki/The_Chinese_Classics/Volume_1/Confucian_Analects"}],
      "via": {"label": "Wikisource", "url": "https://en.wikisource.org/wiki/The_Chinese_Classics/Volume_1/Confucian_Analects"},
      "note": "Public domain; Legge's notes left out. Chinese: 論語 from Chinese Wikisource, matched chapter by chapter to the Chinese Legge printed "
              "above his English; where Wikisource divides a chapter of Legge's in two (V.1, IX.6) the halves are joined.",
      "zh": "https://zh.wikisource.org/wiki/論語"}),
    ("daxue", daxue, {"name": "The Great Learning (Daxue)", "levels": ["Part", "Chapter"], "date": [-300, -100],
                      "source": "Chinese: Zhu Xi's Sishu zhangju, from Chinese Wikisource; English: James Legge, The Chinese Classics vol. 1 (1893), from sacred-texts.com"},
     {"by": "James Legge", "work": "The Chinese Classics, vol. 1: The Great Learning, 2nd ed., Oxford: Clarendon Press", "year": "1893",
      "links": [{"label": "sacred-texts.com", "url": "https://sacred-texts.com/cfu/conf2.htm"}],
      "via": {"label": "Internet Archive", "url": "https://web.archive.org/web/2022/https://sacred-texts.com/cfu/conf2.htm"},
      "note": "Public domain; Legge's notes left out. Chinese: Zhu Xi's arrangement (四書章句集註/大學章句), which Legge translates, from Chinese Wikisource, "
              "Zhu's notes and his supplied fifth commentary chapter left out.",
      "zh": "https://zh.wikisource.org/wiki/四書章句集註/大學章句"}),
    ("zhongyong", zhongyong, {"name": "The Doctrine of the Mean (Zhongyong)", "levels": ["Chapter"], "date": [-300, -100],
                              "source": "Chinese: Zhu Xi's Sishu zhangju, from Chinese Wikisource; English: James Legge, The Chinese Classics vol. 1 (1893), from sacred-texts.com"},
     {"by": "James Legge", "work": "The Chinese Classics, vol. 1: The Doctrine of the Mean, 2nd ed., Oxford: Clarendon Press", "year": "1893",
      "links": [{"label": "sacred-texts.com", "url": "https://sacred-texts.com/cfu/conf3.htm"}],
      "via": {"label": "Internet Archive", "url": "https://web.archive.org/web/2022/https://sacred-texts.com/cfu/conf3.htm"},
      "note": "Public domain; Legge's notes left out. Chinese: Zhu Xi's text in his 33 chapters (四書章句集註/中庸章句), from Chinese Wikisource, his notes left out.",
      "zh": "https://zh.wikisource.org/wiki/四書章句集註/中庸章句"}),
    ("mencius", mencius, {"name": "Mencius", "levels": ["Book", "Part", "Chapter"], "date": [-320, -250],
                          "source": "Chinese: Chinese Wikisource; English: James Legge, The Chinese Classics vol. 2 (1861, 2nd ed. 1895), from English Wikisource"},
     {"by": "James Legge", "work": "The Chinese Classics, vol. 2: The Works of Mencius, Oxford: Clarendon Press", "year": "1861",
      "links": [{"label": "Wikisource", "url": "https://en.wikisource.org/wiki/Mencius_(Legge)"}],
      "via": {"label": "Wikisource", "url": "https://en.wikisource.org/wiki/Mencius_(Legge)"},
      "note": "Public domain; Legge's notes left out. The Wikisource text writes Legge's names in pinyin (Qi, King Wen for his Ch'î, King Wan). "
              "Chinese: 孟子 from Chinese Wikisource.",
      "zh": "https://zh.wikisource.org/wiki/孟子"}),
    ("zhuangzi", zhuangzi, {"name": "Zhuangzi", "levels": ["Chapter"], "date": [-350, -150],
                            "source": "Chinese: Chinese Wikisource; English: James Legge, Sacred Books of the East 39–40 (1891), from sacred-texts.com"},
     {"by": "James Legge", "work": "The Texts of Taoism, Parts I–II: The Writings of Kwang-dze, Sacred Books of the East vols. 39–40, Oxford: Clarendon Press", "year": "1891",
      "links": [{"label": "sacred-texts.com", "url": "https://sacred-texts.com/tao/sbe39/index.htm"}],
      "via": {"label": "Internet Archive", "url": "https://web.archive.org/web/2022/https://sacred-texts.com/tao/sbe39/index.htm"},
      "note": "Public domain; Legge's notes left out. Chinese: 莊子 (Guo Xiang's 33 chapters) from Chinese Wikisource.",
      "zh": "https://zh.wikisource.org/wiki/莊子"}),
]


# Built every run, but catalogued only when named, e.g. `--catalog daodejing analects daxue zhongyong mencius zhuangzi`.
OPT_IN = {"mencius": "its English is Wikisource's pinyin-named text of Legge, which appears to be ctext.org's edition"}


def main():
    os.makedirs(OUT, exist_ok=True)
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    texts, records, total = [], {}, 0
    for tid, build, row, credit in TEXTS:
        if only and tid not in only:
            continue
        print(tid, flush=True)
        rows = build()
        ratio_check(tid, rows)
        f = os.path.join(OUT, f"{tid}.json")
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)
        size = os.path.getsize(f)
        total += size
        print(f"  wrote china/{tid}.json: {len(rows)} entries, {size / 1024:.0f} KB")
        if "--catalog" in sys.argv and tid in OPT_IN and tid not in only:
            print(f"  {tid} written but left out of the catalog: name it to add it ({OPT_IN[tid]})")
            continue
        texts.append({"id": tid, "file": f"china/{tid}.json", "name": row["name"], "band": "china", "levels": row["levels"], "original": ORIGINAL,
                      "date": row["date"], "source": row["source"]})
        cred = {k: v for k, v in credit.items() if k != "zh"}
        cred["links"] = cred["links"] + [{"label": "Chinese Wikisource", "url": urllib.parse.quote(credit["zh"], safe=":/()_")}]
        records[tid] = {"english": cred}
    print(f"total {total / 1024 / 1024:.2f} MB")
    if "--catalog" in sys.argv:
        from comparative_catalog import write
        write([BAND], texts, records)


if __name__ == "__main__":
    main()
