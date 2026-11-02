import json, re, sys, datetime
HERE = __import__('pathlib').Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from corpus import load, norm
ns = {}
exec(open(HERE/'bank_part1.py').read(), ns); exec(open(HERE/'bank_part2.py').read(), ns)
ENTRIES = ns['ENTRIES'] + ns['ENTRIES2']

SECTIONS = {
 'S1': ('Indra: the series', "F7 says Indra is a franchise. Each entry is a different side of him: trickster, insecure husband, beggar, student, hostage, judge."),
 'S2': ('Women who bargain, refuse and win', "Apala (796k) was a girl who made a deal with a god. These are her successors: women with a want, an obstacle and a line of their own."),
 'S3': ('Animals, loyalty and the ones who stayed', "F4: the two dog shorts out-shared everything. Dogs, a horse's head, a falcon, a fish, a vulture, four unborn birds."),
 'S4': ('Defiance: outsiders who out-argued the insiders', "Slaves' sons, disinherited sons, crooked boys, gleaners, shopkeepers. Injustice travels (F10) and starts arguments (F11)."),
 'S5': ('Students, teachers and kings', "Indra & Virochana (686k) was a student story. The Upanishads are full of them, and in most the teacher is a king or a fire, not a Brahmin."),
 'S6': ('Gods behaving badly', "Brahmana comedies and horrors: gods robbing a goddess, sending a dwarf, creating illusions, building a god to punish their father."),
 'S7': ('Seers and kings of the Rigveda', "The historical layer: a datable war, a sick prince who gave up a throne, a hungry sage, a priest on strike, frogs."),
 'S8': ('Mahabharata roots in the Vedas', "The Dog short (4.4M) connected the epic to the Veda. Here are the other threads: Parikshit, Janamejaya, Bharata, Devapi."),
 'S9': ('Argument shorts', "F11: a thesis gets comments and shares but fewer complete views. These have no protagonist; test them against the stories, not instead of them."),
 'S10': ('Epic tier: Mahabharata, Ramayana, Harivamsa', "The corpus holds Ganguli's Mahabharata, Dutt's Ramayana and Harivamsa in English. Outside the channel's Vedic identity, so chosen for Vedic resonance, an animal, a woman, or Indra."),
}
TIER = {'A': 'A · make next', 'B': 'B · strong, needs the right cut', 'C': 'C · micro, risky or thin'}

# ---- validate ----
problems = []
spans = {}
slugs = set()
for e in ENTRIES:
    if e['slug'] in slugs: problems.append(f"duplicate slug {e['slug']}")
    slugs.add(e['slug'])
    body = ''
    total = 0
    for s in e['sources']:
        ents = load(s['text'])
        ia = next((i for i, x in enumerate(ents) if norm(x['reference']) == norm(s['from'])), None)
        ib = next((i for i, x in enumerate(ents) if norm(x['reference']) == norm(s['to'])), None)
        if ia is None or ib is None or ib < ia:
            problems.append(f"{e['slug']}: {s['text']} {s['from']}..{s['to']} NOT RESOLVED ({ia},{ib})"); continue
        sl = ents[ia:ib+1]
        empty = sum(1 for x in sl if not (x.get('text') or '').strip())
        total += len(sl)
        body += ' '.join((x.get('text') or '') for x in sl) + ' '
        s['_n'] = len(sl); s['_empty'] = empty; s['_chars'] = sum(len(x.get('text') or '') for x in sl)
    spans[e['slug']] = total
    if not re.search(e['check'], body):
        problems.append(f"{e['slug']}: check /{e['check']}/ not found in cited text")
print('entries:', len(ENTRIES))
print('problems:', len(problems)); [print('  ', p) for p in problems]
if problems and '--force' not in sys.argv: sys.exit(1)

# ---- render markdown ----
today = datetime.date.today().isoformat()
out = []
out.append(f"""# Story bank: reel-ready stories from the whole corpus

Built {today} from every English-bearing text in `public/data` (Rigveda, Atharvaveda, Sama- and Yajurveda, the Shatapatha, Jaiminiya, Aitareya and Kaushitaki Brahmanas, the Upanishads, the Brhaddevata, Ganguli's Mahabharata, Dutt's Ramayana and Harivamsa). Every citation below was resolved against the corpus files, and a key phrase from each story was confirmed inside the cited range, so the shorts engine's research and fact-check stages will find the text. `stories/topics.candidates.json` holds the same entries in the engine's `topics.json` shape.

**How this was built.** A narrative-density scan (speech verbs, quotes, motion verbs, proper names per section, the same heuristic as the engine's discovery) ranked every section of every English text; the top sections were read, and the known story cycles (Indra, the Ashvins, Janaka's court, the seer legends in the Brhaddevata, the Mahabharata's inner tales) were checked one by one. Stories already on the channel or in `topics.json` of the shorts repo are excluded; sequels to them are included and say so.

**How to read an entry.** *Hook* is the cold open (guide §5–6: a paradox you can see, hero named by ~5 s); Tier A entries carry a Hindi draft of it. *Arc* is want → obstacle → turn → payoff (constitution rule 6). *Kicker* is the new frame after the payoff (guide §7, F2): never a recap. *Notes* carry the playbook fit (F-numbers from `insights/PLAYBOOK.md`), the devotional or plot-hole risks (F9), and which corpus passages are patchy.

**Tiers.** {TIER['A']}: a clear arc, a protagonist, a hook that is not a correction (F6), sources complete in the corpus. {TIER['B']}: strong story, one risk to handle. {TIER['C']}: a micro (under 60 s), a pinned-comment story, or a risk the producer must decide.

**Counts.** {len(ENTRIES)} entries: {sum(1 for e in ENTRIES if e['tier']=='A')} A, {sum(1 for e in ENTRIES if e['tier']=='B')} B, {sum(1 for e in ENTRIES if e['tier']=='C')} C.

""")
out.append("## Contents\n")
for k, (name, _) in SECTIONS.items():
    out.append(f"- [{name}](#{k.lower()}-{re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')}) ({sum(1 for e in ENTRIES if e['section']==k)})")
out.append("- [Corpus notes: what the data can and cannot support](#corpus-notes)\n- [Considered and not recommended](#considered-and-not-recommended)\n")

n = 0
for k, (name, blurb) in SECTIONS.items():
    out.append(f"\n## {k} · {name}\n\n{blurb}\n")
    for e in [x for x in ENTRIES if x['section'] == k]:
        n += 1
        src = '; '.join(f"`{s['text']}` {s['from']}–{s['to']} ({s.get('_n','?')} entries{', ' + str(s['_empty']) + ' empty' if s.get('_empty') else ''})" for s in e['sources'])
        out.append(f"### {n}. {e['title']}\n")
        out.append(f"- **Tier:** {TIER[e['tier']]} · **tags:** {', '.join(e['tags'])}")
        out.append(f"- **Source:** {src}")
        out.append(f"- **Hook:** {e['hook']}")
        if e.get('hook_hi'): out.append(f"- **Hook (Hindi draft):** {e['hook_hi']}")
        out.append(f"- **Arc:** {e['arc']}")
        out.append(f"- **Kicker:** {e['kicker']}")
        out.append(f"- **Notes:** {e['notes']}\n")

out.append("""
## Corpus notes

What the data can and cannot support, found while building this bank:

- **Texts with English (usable by the engine's fact-checker):** rigveda, atharvaveda, samaveda, yajurveda_black (Keith's Taittiriya Samhita), yajurveda_white, satapatha_brahmana, jaiminiya_brahmana, aitareya_brahmana, kausitaki_brahmana (274 of 6,915 entries, Keith's abridged sections), aitareya_aranyaka (60 of 75), the Upanishads listed in the header, brhaddevata (986 of 1,223), manu_smrti, mahabharata_ganguli, ramayana_dutt, harivamsa_dutt, and the dharma- and grhya-sutras with English.
- **No English at all** (stories there cannot be fact-checked yet): taittiriya_brahmana (Bharadvaja's three lives, Kutsa, the Saramā of TB), pancavimsa_brahmana (Vṛśa Jāna, Dīrghajihvī's full tale, the Vrātya stomas), gopatha_brahmana, jaiminiya_upanisad_brahmana (machine translation only, in `text_mt`), taittiriya_aranyaka, kathaka and maitrayani samhitas, nirukta, the parisistas, and the srauta-sutras. Where this bank cites a story that also lives in one of these (Devāpi in Nirukta 2.10, Tryaruṇa in PB 13.3.12), it cites the English witness only.
- **Satapatha book 14 (the Brhadaranyaka portion) is dirty:** many entries in `satapatha_brahmana.json` from 14.4 onward end in JSON-LD scraped from sacred-texts.com (`"url": "https://sacred-texts.com/..."`). Cite `brhadaranyaka_upanishad.json` instead for those stories; that file carries Madhavananda's translation interleaved with Shankara's commentary, so the writer must take only the narrative sentences.
- **Brhaddevata is patchy:** roughly one entry in five is empty or ends mid-sentence (e.g. 5.81, 6.13, 7.61, 8.30–8.36). The bank marks every cited range's empty count. Where a Brhaddevata legend has its Rigveda hymn, the hymn is cited as the primary witness.
- **Ganguli's Mahabharata is chapter-level:** one entry per section, and a few are enormous (1.3 Utanka is 35k characters; 1.63 is 19k). The research stage will produce big packets for those; split by hand if the writer drowns.
- **Reference formats differ by text** (`10.086.01` in rigveda and atharvaveda, `1.6.3.1` in satapatha, `3.199` in jaiminiya, `12.9` in aitareya_brahmana where the corpus collapses pañcikā.adhyāya into a running adhyāya number, `4.16` in kausitaki_upanishad). The engine's `normRef` treats `10.86.1` and `10.086.01` as equal, so either spelling works.

## Considered and not recommended

Looked at and left out, so nobody re-checks them:

- **Already on the channel or queued** (`config/published.txt`, `topics.json`): Apala, Lopamudra, Sukanya/Chyavana, the Mahabharata dog, Saranyu, Sarama, the Vratyas, Indra's childhood (4.18), Indra 2.12 and 1.7, Shunahshepa/Harishchandra, Yama & Yima, Manu's fish, Nachiketa, Urvashi, Satyakama, Raikva, the gambler, Yama & Yami, Vishvamitra & the rivers, Indra & Virochana, Bhrigu's other world. Sequels are in the bank and labelled.
- **Dīrghajihvī** (JB 1.161–1.163: Indra sends Sumitra, who has genitals on every limb, to seduce the long-tongued demoness): too explicit for the channel; a pinned-comment legend at most.
- **Romaśā and Bhāvayavya** (RV 1.126.6–7; BD 3.155–3.156): a two-verse ribald exchange, no arc.
- **Vāmadeva's dog entrails** (RV 4.18.13; BD 4.126): belongs to the published Indra's-childhood short.
- **Dīrghatamas** (blind from birth, thrown in the river): only BD 4.15 and the Mahabharata's Adi 104 in the corpus; the famous version is Puranic and not here.
- **Nahuṣa and the rivers** (BD 6.20–6.22): all three entries truncated. His Mahabharata story is in the bank instead.
- **Śakti, Viśvāmitra and the Saudāsas** (BD 4.112–4.115): three of four entries empty; told via vasishthas-hundred-sons and trishanku instead.
- **The Puruṣa, Nāsadīya-style cosmogonies other than 10.129, the Skambha hymns (AV 10.7–10.8), Araṇyānī (10.146), the Bhikṣu hymn (10.117), the Aśvamedha ritual (SB 13; the queen-and-horse rite):** no protagonist or no arc (constitution rule 6), or unfilmable for the house.
- **Gṛhya-sūtra wedding vows and Manusmṛti rules:** explainers (the Vratyas curve, F1), not stories; keep for long-form.
- **Mahabharata and Ramayana set pieces everyone has made** (Draupadi's disrobing, Bhishma's vow, Abhimanyu, the golden deer, Lakshmana-rekha which is not in Valmiki, Hanuman's leap): no Vedic hook; left to the channel's judgement rather than this bank.
""")
open(HERE.parent/'STORY_BANK.md', 'w').write('\n'.join(out))

# ---- render topics json (engine shape) ----
topics = []
for e in ENTRIES:
    if 'pointer' in e['tags']: continue
    topics.append({
        'slug': e['slug'], 'title': e['title'],
        'angle': f"{e['hook']} Kicker: {e['kicker']}",
        'sources': [{'text': s['text'], 'from': s['from'], 'to': s['to']} for s in e['sources']],
        'notes': f"Arc: {e['arc']}\n\nPlaybook: {e['notes']}" + (f"\n\nHindi hook draft: {e['hook_hi']}" if e.get('hook_hi') else ''),
        'tier': e['tier'], 'tags': e['tags'],
    })
json.dump(topics, open(HERE.parent/'topics.candidates.json', 'w'), ensure_ascii=False, indent=1)
print('wrote', len(topics), 'topics;', 'md bytes', len('\n'.join(out)))
big = [(e['slug'], spans[e['slug']]) for e in ENTRIES if spans[e['slug']] > 45]
print('spans > 45 entries:', big)
