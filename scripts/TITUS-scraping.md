# TITUS Scraping Guide

Notes on scraping Vedic/Sanskrit texts from [TITUS](https://titus.uni-frankfurt.de/) (Thesaurus Indogermanischer Text- und Sprachmaterialien).

## URL Structure

```
https://titus.uni-frankfurt.de/texte/etcs/ind/aind/ved/{collection}/{text}/{text}001.htm
https://titus.uni-frankfurt.de/texte/etcs/ind/aind/ram/ram001.htm  (Ramayana)
```

Pages are sequential: `{text}001.htm`, `{text}002.htm`, etc. Pages return 404 or contain "not (yet) available" when they don't exist. After 3 consecutive failures, stop.

Some texts (e.g., Kausitaki Brahmana) are behind basic auth on a different subdomain:
```
https://titus.fkidg1.uni-frankfurt.de/texte/etcc/...
```
Credentials: `titusstud` / `R2gveda5`

## Critical: Encoding

TITUS serves UTF-8 but does **not** declare it in HTTP headers. `requests` defaults to ISO-8859-1, which garbles all diacritical marks. **Always force UTF-8:**

```python
resp = requests.get(url, timeout=30)
resp.encoding = "utf-8"  # MUST set before accessing resp.text
```

Without this fix, `ā` → `Ä`, `ṇ` → `á¹`, `ʰ` → `Ê°`, etc.

## HTML Structure: Span IDs

TITUS HTML uses `<span id="...">` elements to encode structure and content. The span ID prefix determines the type:

### Text content spans (extract these)
- `iov*` — Standard text (e.g., `iovpl16`, `iovml16`) — used for most Vedic texts
- `iosk*` — Sanskrit text (e.g., `ioskml16`, `ioskms16`) — used for Ramayana, epics

### Structural spans (parse for metadata)
- `h1` — Text collection (e.g., "Text collection: RV")
- `h2` — Book/Kanda level (e.g., "Book: 1")
- `h3` — Top-level division (e.g., "Aranyaka: 1", "Chapter: 5")
- `h4` — Second-level (e.g., "Adhyaya: 1", "Verse: 3")
- `h5` — Third-level (e.g., "Paragraph: 1", "Halfverse: a")
- `h6` — Fourth-level (e.g., "Sentence: a")
- `h7` — Fifth-level

### Metadata spans (skip these)
- `h8` — "Page of ed.: N" (editorial page number)
- `h9` — "Line of ed.: N" (editorial line number)
- `ioc*` — Editorial comments, cross-references (e.g., "(RV III 13,1a)")
- `n16` — Line break / formatting
- `title`, `subtitle`, `textdescr`, `bibliogr`, `titus` — Header metadata

### Extracting structural labels

Structural info is in HTML comments within the span:
```html
<span id="h3"><!--Level 3-->Aranyaka: 1<a name="RV_AA_1"> </a></span>
```

Parse with:
```python
m = re.search(r'<!--\s*(?:X?Level \d+)\s*-->([^<]+)', str(span))
label = m.group(1).strip()  # "Aranyaka: 1"
```

## TITUS IAST Encoding

TITUS uses a non-standard IAST that requires cleaning:

| TITUS | Standard IAST | Notes |
|-------|--------------|-------|
| `kʰ`, `gʰ`, `tʰ`, `dʰ`, `pʰ`, `bʰ` | `kh`, `gh`, `th`, `dh`, `ph`, `bh` | Aspirated: superscript ʰ (U+02B0) |
| `r̥` (r + U+0325) | `ṛ` | Vocalic r |
| `l̥` | `ḷ` | Vocalic l |
| `m̐` (m + candrabindu) | `ṃ` | Nasalization |
| `á`, `à`, `í`, `ì`, etc. | `a`, `i`, etc. | Vedic accent marks (strip) |
| `{M: ...}`, `{P: ...}` | (remove) | Editorial apparatus |
| `\` at line end | (remove) | Pāda separator |
| `\\`, `//`, `--` around numbers | Verse markers | e.g., `\\ 42 \\` |

### Accent stripping pitfall

Vedic accent marks use combining acute/grave on vowels: `á` = a + U+0301. But `ś` (U+015B) also decomposes to s + U+0301 in NFD! **Do NOT use Unicode NFD normalization to strip accents.** Instead, explicitly map accented vowels:

```python
accent_map = {'á': 'a', 'à': 'a', 'é': 'e', 'è': 'e', 'í': 'i', 'ì': 'i', ...}
```

## Structural Hierarchy by Text

Each text has a different hierarchy. The "verse boundary" is the structural level at which you split into individual entries.

| Text | Hierarchy | Verse boundary | Reference format |
|------|-----------|---------------|------------------|
| Aitareya Aranyaka | Aranyaka > Adhyaya > Paragraph > Sentence | Paragraph | `aranyaka.adhyaya.paragraph` |
| Taittiriya Aranyaka | Prapathaka > Anuvaka > Kandika > Dasati | Anuvaka | `prapathaka.anuvaka` |
| Gopatha Brahmana | Bhaga > Prapathaka > Khanda > Paragraph | Paragraph | `prapathaka.khanda.paragraph` |
| Kausitaki Brahmana | Book > Chapter > Paragraph | Paragraph | `book.chapter.paragraph` |
| Pancavimsa Brahmana | Chapter > Paragraph | Paragraph | `chapter.paragraph` |
| Vajasaneyi Samhita | Paragraph (=adhyaya) > Verse | Verse (struct) | `paragraph.verse` |
| Rgveda Khilani | Adhyaya > Hymn > Verse > Halfverse | Verse (struct) | `adhyaya.hymn.verse` |
| Manu Smrti | Book > Verse > Half verse | Verse (struct) | `book.verse` |
| Ramayana | Book (kanda) > Chapter (sarga) > Verse > Halfverse | Verse (struct) | `book.chapter.verse` |

**Three boundary modes:**
1. **Paragraph boundary** — Emit verse when Paragraph number changes (prose texts like Brahmanas)
2. **Anuvaka boundary** — Emit verse when Anuvaka changes (Taittiriya Aranyaka)
3. **Verse (structural)** — Emit verse when `Verse: N` structural marker changes (metrical texts)

Note: Some texts also have `\\ N \\` text-level verse markers, but these are unreliable (sometimes they're word counts, not verse numbers).

## Gotchas

1. **No Adhyaya markers for some texts.** VS uses `Paragraph` at h5 for what is functionally the adhyaya. Manu uses `Book` at h3 level. Always check actual structural markers before assuming a hierarchy.

2. **Span ID prefixes vary.** Ramayana uses `iosk*`, not `iov*`. When adding a new text, check what span IDs the pages actually use.

3. **Fine-grained paragraphs.** Kausitaki Brahmana has 6,962 paragraph-level units — each is 1-2 sentences. This is the natural TITUS unit for prose texts. Don't expect paragraph = verse.

4. **Non-numeric structural values.** Some texts have `Hymn: col.`, `Adhyaya: S`, `Verse: _`, `Khanda: 0`. The parser should handle these gracefully (skip non-numeric values).

5. **Words in separate `<a>` tags.** Each word is a clickable `<a>` link (for the TITUS dictionary). Extract text from all children of the span, don't rely on `get_text()` with separators.

6. **h2 contains Book/Kanda.** Don't skip h2 — for texts like Ramayana, the highest structural division (Kanda) is at h2 level, not h3.
