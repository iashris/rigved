# Story bank: reel-ready stories from the whole corpus

Built 2026-11-01 from every English-bearing text in `public/data` (Rigveda, Atharvaveda, Sama- and Yajurveda, the Shatapatha, Jaiminiya, Aitareya and Kaushitaki Brahmanas, the Upanishads, the Brhaddevata, Ganguli's Mahabharata, Dutt's Ramayana and Harivamsa). Every citation below was resolved against the corpus files, and a key phrase from each story was confirmed inside the cited range, so the shorts engine's research and fact-check stages will find the text. `stories/topics.candidates.json` holds the same entries in the engine's `topics.json` shape.

**How this was built.** A narrative-density scan (speech verbs, quotes, motion verbs, proper names per section, the same heuristic as the engine's discovery) ranked every section of every English text; the top sections were read, and the known story cycles (Indra, the Ashvins, Janaka's court, the seer legends in the Brhaddevata, the Mahabharata's inner tales) were checked one by one. Stories already on the channel or in `topics.json` of the shorts repo are excluded; sequels to them are included and say so.

**How to read an entry.** *Hook* is the cold open (guide §5–6: a paradox you can see, hero named by ~5 s); Tier A entries carry a Hindi draft of it. *Arc* is want → obstacle → turn → payoff (constitution rule 6). *Kicker* is the new frame after the payoff (guide §7, F2): never a recap. *Notes* carry the playbook fit (F-numbers from `insights/PLAYBOOK.md`), the devotional or plot-hole risks (F9), and which corpus passages are patchy.

**Tiers.** A · make next: a clear arc, a protagonist, a hook that is not a correction (F6), sources complete in the corpus. B · strong, needs the right cut: strong story, one risk to handle. C · micro, risky or thin: a micro (under 60 s), a pinned-comment story, or a risk the producer must decide.

**Counts.** 111 entries: 40 A, 49 B, 22 C.


## Contents

- [Indra: the series](#s1-indra-the-series) (22)
- [Women who bargain, refuse and win](#s2-women-who-bargain-refuse-and-win) (15)
- [Animals, loyalty and the ones who stayed](#s3-animals-loyalty-and-the-ones-who-stayed) (11)
- [Defiance: outsiders who out-argued the insiders](#s4-defiance-outsiders-who-out-argued-the-insiders) (9)
- [Students, teachers and kings](#s5-students-teachers-and-kings) (15)
- [Gods behaving badly](#s6-gods-behaving-badly) (7)
- [Seers and kings of the Rigveda](#s7-seers-and-kings-of-the-rigveda) (11)
- [Mahabharata roots in the Vedas](#s8-mahabharata-roots-in-the-vedas) (4)
- [Argument shorts](#s9-argument-shorts) (5)
- [Epic tier: Mahabharata, Ramayana, Harivamsa](#s10-epic-tier-mahabharata-ramayana-harivamsa) (12)
- [Corpus notes: what the data can and cannot support](#corpus-notes)
- [Considered and not recommended](#considered-and-not-recommended)


## S1 · Indra: the series

F7 says Indra is a franchise. Each entry is a different side of him: trickster, insecure husband, beggar, student, hostage, judge.

### 1. Tvashtr cursed Indra. The curse killed his own son.

- **Tier:** A · make next · **tags:** indra, rivalry, twist
- **Source:** `satapatha_brahmana` 1.6.3.1–1.6.3.17 (17 entries)
- **Hook:** A father brews a monster to kill the god who murdered his son. He says one sentence over it. That sentence kills the monster instead.
- **Hook (Hindi draft):** त्वष्टा ने अपने बेटे के हत्यारे को मारने के लिए एक राक्षस बनाया। उस पर एक वाक्य बोला। उसी वाक्य ने राक्षस को मार दिया।
- **Arc:** Tvashtr's three-headed son Vishvarupa drinks Soma with one mouth, liquor with another; Indra cuts off all three heads (birds fly out of each mouth). Tvashtr excludes Indra from Soma; Indra drinks it uninvited. Tvashtr pours the leftover on the fire with the words 'Grow, having Indra as your foe' (indraśatru), and it rolls out as Vritra, growing an arrow's range a day. Indra wins over Agni and Soma from inside Vritra, strikes, and Vritra collapses 'like a leather bottle drained'. Vritra asks to be cut in two: one half becomes the moon, the other the bellies of living beings.
- **Kicker:** The Sanskrit explains why the curse backfired: 'indraśatru' with the accent in one place means 'Indra's killer', in another 'whose killer is Indra'. Tvashtr got the accent wrong. In the Veda, even a curse has to be pronounced correctly.
- **Notes:** Indra series, episode: the trickster who out-drank his enemy. The accent point lives in the Sanskrit (meaning field), not in Eggeling's English ('Grow thou, having Indra for thy foe!'); phrase the kicker as the text does, or add the grammarians' explanation as a producer note so the fact-checker allows it. F9 watch: 'why birds from the mouths?' is answered in the text (partridge, sparrow, francolin), so say it.

### 2. Indra made a clone of himself. His wife could not tell them apart.

- **Tier:** A · make next · **tags:** indra, comedy, marriage
- **Source:** `jaiminiya_brahmana` 3.199–3.201 (3 entries)
- **Hook:** Indra built a charioteer out of his own thigh, in his own image. The first person fooled was his wife.
- **Hook (Hindi draft):** इंद्र ने अपनी जांघ से अपना हमशक्ल बनाया, सारथी के तौर पर। सबसे पहले धोखा उनकी पत्नी शची ने खाया।
- **Arc:** Kutsa Aurava, fashioned from Indra's thighs, looks exactly like him; Indra makes him charioteer. Shachi Paulomi embraces Kutsa by mistake: 'I could not tell you two apart.' Indra shaves Kutsa bald; Kutsa sleeps under a turban. Indra pours dust between his shoulders; Kutsa covers it. She embraces him again. Indra throws him out as a cheat; Kutsa begs 'give us something to live by, we were born from you', shakes off the dust, and a whole people (the Rajas) rise from it, with kings and a priest, Upagu Sausravasa, who bans sacrifice. Indra comes to Upagu three times, 'let me sacrifice for you', and three times the people defeat him for it.
- **Kicker:** Every charioteer's turban and the dust on his shoulders, says the text, come from a husband trying to tell himself apart from his double. The joke of the Jaiminiya is that even Indra could not keep his own identity.
- **Notes:** Indra series: Indra the insecure husband. Pure comedy with a sting; keep the three disguises as the rhythm (refrain of doubt, guide §2). The Upagu tail (3.200-3.201) can be cut at 'a people rose from the dust'. Companion micro: JB 1.227 (Kutsa and Lusha both call Indra; Lusha ties him by the testicles with a hundred straps; Indra splits himself between them) is too bawdy for the channel but worth a pinned-comment tease.

### 3. A queen in mourning. An old man who would not stop dancing.

- **Tier:** A · make next · **tags:** indra, woman, disguise, war
- **Source:** `jaiminiya_brahmana` 3.246–3.248 (3 entries)
- **Hook:** The king's army had lost; the queen's brother was dead. An old beggar with a pole on his shoulder danced beside her, smearing her with ghee, and would not go away.
- **Hook (Hindi draft):** रानी का भाई मारा गया था। एक बूढ़ा, कंधे पर बहंगी, उसके पास नाचता रहा, घी पोतता रहा, हटाओ तो फिर पास आ जाता।
- **Arc:** Upama Savedasi, wife of King Pratardana, runs about lamenting her brother. Indra sees her, puts on a dry hide, hangs a cake on one end of a carrying-pole and clotted milk on the other, and dances near her all day, smearing ghee on her whenever she pushes him off. At night her husband asks what she saw; from her description he knows: 'Indra has come to our invocation. Don't harm him. Make him your ally.' Next day the old man dances further off; she chases him and they trade riddling insults ('may your pole break' / 'even broken, the father will mend it'). He runs to her: 'Let us win the battle!', shakes the hairs from the deer-hide, horse-chariots rise from them, and the battle is won.
- **Kicker:** Indra did not arrive with a thunderbolt. He arrived as the man you shove away. The Jaiminiya says the god comes to the house that is grieving, and comes in disguise.
- **Notes:** Indra series + a woman lead. The riddle exchange is partly untranslatable (mahira, pevasma); use two or three clear lines and let the rest be dance. The 'Bharadvaja said we did not run to a wife' tag is ritual etymology, drop it.

### 4. Indra swore not to kill him by day or night, wet or dry. So he used foam at dusk.

- **Tier:** A · make next · **tags:** indra, oath, trick
- **Source:** `satapatha_brahmana` 12.7.3.1–12.7.3.4 (4 entries); `satapatha_brahmana` 12.7.1.10–12.7.1.14 (5 entries)
- **Hook:** Indra had given a demon his word: not by day, not by night, not with anything wet, not with anything dry. Then the demon stole his strength with liquor.
- **Hook (Hindi draft):** इंद्र ने नमुचि को वचन दिया था: ना दिन में मारूंगा, ना रात में, ना सूखे से, ना गीले से। फिर नमुचि ने शराब पिलाकर उनका बल चुरा लिया।
- **Arc:** Namuci the Asura, with sura liquor, carries off Indra's strength, the essence of food, the Soma. Indra runs to the Ashvins and Sarasvati: 'I have sworn to Namuci, I will slay you neither by day nor by night, neither with staff nor with bow, neither with the flat nor the fist, neither dry nor wet; and he has taken these from me. Bring them back.' They ask for a share, then pour out foam of water as a thunderbolt: 'it is neither dry nor wet', and at the junction of night and day, 'neither day nor night', Indra strikes off Namuci's head with it.
- **Kicker:** The Rigveda already sings 'with foam of water, Indra, you tore off Namuci's head'. Indra did not break his word. He found the one hour and the one substance the word did not cover. In the Veda, cleverness is not cheating.
- **Notes:** Indra series: the lawyer-god. F9: viewers will ask 'is a loophole honest?'; the kicker should take a side (F11). The Rigveda verse 8.14.13 is quoted inside SB 12.7.3.4 so it can be cited from the packet. The Mahabharata retells it for Vritra (see epic tier).

### 5. Indra confessed to murder, then said: not a hair of me is harmed.

- **Tier:** A · make next · **tags:** indra, argument, philosophy
- **Source:** `kausitaki_upanishad` 3.1–3.3 (3 entries); `aitareya_brahmana` 35.2–35.2 (1 entries)
- **Hook:** A king died fighting and came to Indra's house. Indra offered him a boon. The king said: you choose for me. And Indra began to confess.
- **Hook (Hindi draft):** राजा प्रतर्दन लड़ते-लड़ते मरकर इंद्र के घर पहुंचे। इंद्र ने वरदान मांगने को कहा। राजा बोले, आप ही चुन लीजिए। और इंद्र ने अपने अपराध गिनाने शुरू किए।
- **Arc:** Pratardana, son of Divodasa, reaches Indra's abode by valour. 'Choose a boon.' 'Choose it for me.' Indra: 'Know me. That is the most beneficial thing for man. I killed the three-headed son of Tvashtr; I threw the ascetics to the hyenas; I broke many treaties; I killed the Prahladas in the sky, the Paulomas in the air, the Kalakanjas on earth; and not a hair of me was harmed. He who knows me, no deed of his destroys his world, not even killing his mother or father, not theft, not killing an embryo. The colour does not leave his face.' Then: 'I am the breath, the conscious self; worship me as life.' The Aitareya adds the other side: the gods themselves once excluded Indra from Soma for these same crimes.
- **Kicker:** The oldest text to list Indra's crimes puts them in Indra's own mouth, as the opening of a lesson on consciousness. The Veda does not hide what the god did. It asks what, in you, is untouched by what you did.
- **Notes:** Indra series + F11 argument hybrid (the kind of short that gets comments). Devotional sensitivity: 'killing his mother' is in the text as the extreme case of the knower's immunity, not a licence; frame it as the text's own shock. Pair the AB line (gods list Indra's crimes) as the 'other side'.

### 6. Indra asked to become Prajapati. So Prajapati became 'Who'.

- **Tier:** B · strong, needs the right cut · **tags:** indra, micro, wordplay
- **Source:** `aitareya_brahmana` 12.9–12.10 (2 entries)
- **Hook:** After killing Vritra, Indra had one wish left: let me be what you are. The creator asked him back: then who am I?
- **Arc:** Indra, about to kill Vritra, asks the gods to back him; when they rush in, he thinks they are coming for him and breathes fire at them; they flee. He kills Vritra alone. Winner of everything, he goes to Prajapati: 'Let me be what you are. Let me be great.' Prajapati: 'Then who am I?' Indra: 'Exactly what you just said.' From then Prajapati's name is Ka, 'Who'; and Indra became great, hence Mahendra.
- **Kicker:** The Rigveda's famous refrain 'to which god shall we offer?' (kasmai devaya) has an answer in the Brahmana: to Who. The god with no name got it from Indra's ambition.
- **Notes:** Indra series micro (60-75 s). Needs a visual for 'Who' (an empty throne, an unlabelled altar). Doctrine risk: it is wordplay, keep it as a joke with a kicker.

### 7. Indra killed Vritra and ran away. He thought he had lost.

- **Tier:** C · micro, risky or thin · **tags:** indra, fear
- **Source:** `satapatha_brahmana` 4.1.3.1–4.1.3.8 (8 entries)
- **Hook:** The most famous victory in the Veda ended with the winner hiding. Indra threw the bolt, thought he was the weaker, and fled; the gods hid too.
- **Arc:** No one knows if Vritra is dead. The gods send Vayu to check, for the price of the first Soma offering. Vritra is dead, but his stench is unbearable; Vayu blows through him for a second share; the gods push the rest of the smell into cattle and dead bodies. Indra comes out of hiding.
- **Kicker:** The hero of the Vedas did not know he had won. Somebody else had to go and look.
- **Notes:** Indra series, minor: good as a cold open or a kicker for another Vritra episode; thin as a full short (ritual explanation of the Soma cups). Keith's Taittiriya version (TS 2.5.1, English) is longer and adds that Vritra was swallowing Indra.

### 8. He taught with a horse's head because teaching with his own meant losing it.

- **Tier:** A · make next · **tags:** indra, loyalty, secret, animal
- **Source:** `satapatha_brahmana` 14.1.1.18–14.1.1.26 (9 entries); `rigveda` 01.116.12–01.116.12 (1 entries); `brhaddevata` 3.22–3.24 (3 entries)
- **Hook:** Indra told the sage: teach this secret to anyone and I cut off your head. Two gods still wanted the secret. They found a way that cost the sage his head, twice.
- **Hook (Hindi draft):** इंद्र ने ऋषि दध्यंच से कहा: ये रहस्य किसी को सिखाया तो सिर काट दूंगा। अश्विनों को वही रहस्य चाहिए था। रास्ता निकला, जिसमें ऋषि का सिर दो बार कटा।
- **Arc:** Dadhyanc Atharvana knows the 'honey' doctrine: how the head of the sacrifice is put back on. Indra forbids him on pain of beheading. The Ashvins come as pupils; he tells them of the threat; they say 'we will protect you: we will cut off your head, keep it aside, fix a horse's head on you; you teach us with that; when Indra strikes it off, we put your own head back.' So it happens: the horse-headed sage teaches; Indra cuts off the horse's head; the Ashvins restore his own. The Rigveda remembers it ('Dadhyanc with a horse's head spoke to you the sweet doctrine'), and the Brhaddevata says the horse's head fell into a lake on Mount Sharyanavat, and still rises from the water to grant boons.
- **Kicker:** The Mahabharata's Dadhichi gives his bones for Indra's thunderbolt. The Veda's Dadhyanc gives his head to keep a promise to Indra and a promise to the Ashvins at the same time. Loyalty in the Veda is a logic puzzle solved with a horse.
- **Notes:** Indra series + animal + loyalty (F4). SB 14.1.1.24 ends mid-sentence in the corpus (flagged truncated); the RV verse and BD fill it. Devotional tie-in: the horse-headed teacher later becomes Hayagriva.

### 9. The gods needed someone to carry Indra's sin. They picked the man in the well.

- **Tier:** B · strong, needs the right cut · **tags:** indra, injustice, justice
- **Source:** `satapatha_brahmana` 1.2.3.1–1.2.3.5 (5 entries); `brhaddevata` 3.132–3.137 (6 entries); `rigveda` 01.105.01–01.105.19 (19 entries)
- **Hook:** Indra killed a priest's son. Indra is a god, so the sin could not stick to him. It had to go somewhere.
- **Arc:** Trita, Dvita and Ekata (the Aptyas) follow Indra 'as a Brahman follows a king'. When Indra kills Vishvarupa, the Aptyas 'knew of it', so the guilt passes to them; they pass it on to whoever sacrifices without a fee; the gods make it the rule for the new-moon cake. In the Rigveda and the Brhaddevata, Trita is also the man thrown into a well by 'the sons of the she-wolf' who stole his cows; from the bottom of the well he presses Soma, calls all the gods and reproaches them: 'where is your all-seeing power?' They come, share his offering, and pull him out.
- **Kicker:** The Veda keeps both Tritas: the scapegoat who carries a god's guilt, and the man who, from the bottom of a well, demanded that the gods show up. Sometimes they are the same person.
- **Notes:** Indra series, the uncomfortable one. Two texts, one character; the SB passage is short and ritual, so let the RV well-hymn carry the images (the moon running in the waters, the stars that shine by night and go nowhere by day). F9: say plainly the text says the Aptyas were punished for knowing.

### 10. The Soma was stolen by a bird. An archer shot one feather off.

- **Tier:** A · make next · **tags:** animal, heist, indra
- **Source:** `rigveda` 04.026.01–04.027.05 (12 entries); `aitareya_brahmana` 13.2–13.2 (1 entries)
- **Hook:** Before Indra could drink Soma, somebody had to steal it from heaven. The thief was a falcon. The guard was an archer who never missed. He missed, by a feather.
- **Hook (Hindi draft):** इंद्र सोम पी सकें, उससे पहले किसी को उसे स्वर्ग से चुराना था। चोर एक बाज़ था। पहरेदार एक तीरंदाज़, जो कभी नहीं चूकता था। वो चूका, एक पंख से।
- **Arc:** A voice declares 'I was Manu, I was Surya' (Vamadeva speaking as Indra), then praises the Bird 'above all birds': the falcon that seized the Soma stalk from the iron fortresses of heaven and flew 'swift as thought', bearing a thousand libations. In 4.27 the seer says 'while in the womb I knew all the births of the gods; a hundred iron fortresses held me; I flew out as a falcon.' The guardian archer Krishanu shoots as the bird speeds down; the Aitareya says the arrow cut off the nail of her left foot (it became a porcupine) and a feather fell (it became the parna tree).
- **Kicker:** The Vedic heist has no hero who stays behind to cover the escape. It has one feather on the ground, and a tree grows from it. Every leaf-plate at a Hindu meal is, the Brahmana says, that feather.
- **Notes:** Animal protagonist (F4). Mix: RV gives the flight and the archer, AB 13.2 gives the feather/nail aftermath (AB calls the bird Gayatri). 4.27.1 ('I knew all the births while in the womb') is a second story in itself; keep it as one line or drop. Vamadeva is the seer of the published 'Indra's childhood' (4.18): same voice, so a natural series link.

### 11. Indra's wife versus a monkey: the rudest hymn in the Rigveda.

- **Tier:** C · micro, risky or thin · **tags:** indra, comedy, animal, adult
- **Source:** `rigveda` 10.086.01–10.086.23 (23 entries)
- **Hook:** People have stopped pouring Soma for Indra, because a monkey is eating the offerings. Indra's wife wants it dead. Indra loves the monkey.
- **Arc:** A three-way dialogue: Indrani complains the ape Vrishakapi has spoiled her things and has grown bold; Indra defends his pet; the ape answers; the quarrel turns bawdy (Indrani's boast of her own charms, Indra's 'my wife is the best of women'), ends with the ape's return and a feast (the dog, the boar, the tame beast slaughtered), and the refrain 'Indra is above all'. Brhaddevata reads the ape as the sun.
- **Kicker:** The hymn chanted at the biggest royal sacrifice is a marital spat about a monkey. The priests kept it because, they said, it was Indra's.
- **Notes:** Hold for a mature-audience test; several verses are explicit in Griffith's Latin and in any honest Hindi. Funny, famous among scholars, risky with devotees. If made: play it as a domestic comedy with the ape as the third character, never a lecture about 'what it really means'.

### 12. The first woman to win a chariot race did it with one bull and a wooden club.

- **Tier:** A · make next · **tags:** woman, indra, race, animal
- **Source:** `rigveda` 10.102.01–10.102.12 (12 entries); `brhaddevata` 8.12–8.12 (1 entries)
- **Hook:** Everyone else had horses. Mudgala had one bull, a club for the other side of the yoke, and a wife who could drive.
- **Hook (Hindi draft):** बाकी सबके पास घोड़े थे। मुद्गल के पास एक बैल था, जुए के दूसरी तरफ़ एक लकड़ी का मूसल, और एक पत्नी जो रथ चला सकती थी।
- **Arc:** Mudgala's cattle are stolen (or he is poor); he yokes a lone bull with a wooden club, and Mudgalani takes the reins ('the wife of Mudgala drove'). The bull runs mad, 'his dung flies', the club does its work; Indra speeds the car; they win the thousand and recover the cows. The Brhaddevata says with this hymn Mudgala overcame Indra and Soma in a contest, yoking a bull and a mallet to his chariot.
- **Kicker:** The Rigveda's only named woman charioteer did not ask to be included in the race. She drove, and the hymn says the dust of her bull's hooves was the shout of victory.
- **Notes:** Woman lead; animal; Indra as helper, so an Indra-series side-episode. Griffith's text of 10.102 is obscure in places; the writer should keep to the clear verses (1, 2, 5-9) and let the pictures run. F3: open on the bull and the club, name Mudgalani by 5 s.

### 13. Indra was jealous of his own gang. A sage had to talk him down.

- **Tier:** B · strong, needs the right cut · **tags:** indra, jealousy, dialogue
- **Source:** `rigveda` 01.165.01–01.165.15 (15 entries); `rigveda` 01.170.01–01.170.05 (5 entries); `brhaddevata` 4.47–4.56 (10 entries)
- **Hook:** Agastya cooked an offering for Indra, then gave it to the Maruts. Indra arrived to find his food gone and his army fed.
- **Arc:** The Maruts ask Indra why he goes alone; Indra boasts he killed Vritra alone, 'where were you?'; the Maruts remind him of their help; he relents ('I feared nothing when you were with me'). In 1.170 the tone turns: 'Why, brother, do you want to kill us?' The Brhaddevata frames it: Agastya prepared an oblation for Indra and praised the Maruts; Indra, reading his intent, confronted him; Agastya pacified him, and from then the Maruts drink Soma with Indra.
- **Kicker:** The god who could not share the credit learned to share the cup. The Rigveda's hymn of reconciliation was written by the mediator, not the winner.
- **Notes:** Indra series: Indra the insecure leader. Dialogue hymn, so the voice can switch characters. Agastya is the husband of the published Lopamudra short: same seer, new story.

### 14. Indra's daughter-in-law complained he skipped her feast. He turned up with riddles.

- **Tier:** C · micro, risky or thin · **tags:** indra, family, riddles
- **Source:** `rigveda` 10.028.01–10.028.12 (12 entries); `brhaddevata` 7.30–7.32 (3 entries, 1 empty)
- **Hook:** 'All my other friends are here. Only my father-in-law has not come.' The father-in-law is Indra.
- **Arc:** Vasukra's wife, Indra's daughter-in-law, laments that Indra has not come to the Soma; Indra arrives ('I am the one for whom the bull was cooked') and the hymn turns into riddles: the hare swallowing the razor, the fox stealing up on the lion, the jackal hunting the boar. Brhaddevata: the Bolt-bearer, hearing her, came that moment and stood on the northern altar.
- **Kicker:** Even Indra had in-laws. And he answered a complaint with a riddle contest, which is how the Veda says a family makes peace.
- **Notes:** Minor; the riddles are hard to picture. Good as a pinned-comment story or a 45-second filler in the series.

### 15. Indra went into hiding, and a human was made king of the gods. He wanted Indra's wife.

- **Tier:** A · make next · **tags:** indra, epic, woman, pride
- **Source:** `mahabharata_ganguli` 5.11–5.17 (7 entries)
- **Hook:** After killing Vritra, Indra hid inside a lotus stalk. Heaven needed a king, so the gods crowned a man. The man's first demand was Indra's wife.
- **Hook (Hindi draft):** वृत्र को मारकर इंद्र कमल की डंडी में छिप गए। स्वर्ग को राजा चाहिए था, तो देवताओं ने एक इंसान को ताज पहनाया। इंसान की पहली मांग थी इंद्र की पत्नी।
- **Arc:** Indra, guilt-struck after Vritra, vanishes; Nahusha is made king of the gods and asks for Shachi. She stalls: 'come to me in a palanquin carried by sages.' Nahusha has the seven seers carry him and kicks Agastya, 'sarpa, sarpa' (move!); Agastya's curse turns him into a serpent (sarpa). Shachi finds Indra with Brhaspati's help; he returns after expiation.
- **Kicker:** The Mahabharata makes Indra's greatest enemy not a demon but the man who replaced him. Nahusha was undone by one word to a sage, the word that became his new body.
- **Notes:** Epic tier (Mahabharata, Ganguli sections 5.11-5.17: Udyoga Parva). Confirm the exact section span where Nahusha's fall and 'sarpa' pun sit before scripting; Ganguli chapters are long, so the packet will be big. Devotional sensitivity: Indra as a guilty, hiding god is the text's own portrait; audience comments ask exactly for this.

### 16. Indra went looking for the demon king he had beaten. He found him living as a donkey.

- **Tier:** A · make next · **tags:** indra, epic, philosophy, animal
- **Source:** `mahabharata_ganguli` 12.223–12.225 (3 entries)
- **Hook:** Indra could not find Bali anywhere in the three worlds. Brahma told him: look in an empty house, in the body of a donkey.
- **Arc:** Indra, curious how the mighty Bali lives after his fall, finds him as an ass in an empty house and taunts him. Bali answers with the longest, calmest speech on Time in the Mahabharata: 'you did not win, Time won; I grieve not; what you own will pass from you too.' Shri (Fortune) then leaves Bali and comes to Indra, and tells Indra why she stays with no one.
- **Kicker:** The winner came to gloat and left with a lecture on losing. The Mahabharata lets the demon have the last word, and lets Indra listen.
- **Notes:** Epic tier (Shanti Parva). Indra series: Indra the student again, which is the trait the audience named (F7). Keep the Shri sequel as the kicker or a part 2; the Bali speech must be cut hard to three images.

### 17. Indra became a student to learn why Prahlada could not be defeated. Then he asked for it as his fee.

- **Tier:** A · make next · **tags:** indra, epic, trick, ethics
- **Source:** `mahabharata_ganguli` 12.124–12.124 (1 entries)
- **Hook:** Prahlada ruled the three worlds and could not be beaten in battle. Indra went to him disguised as a Brahmin student and asked one question: what makes you unbeatable?
- **Arc:** Prahlada, the demon king, is undefeatable through 'shila', good conduct. Indra serves him as a student for years; when Prahlada offers a boon, Indra asks for his shila. Bound by his word, Prahlada gives it; a shining form leaves his body (Conduct), then Dharma follows it, then Truth, then Good Deeds, then Strength, then Shri herself: 'where conduct goes, I go.' Prahlada asks who the student was; she tells him: Indra.
- **Kicker:** Indra did not win with a weapon. He won by asking a good man to give away the one thing that made him good, and the good man kept his word. The Mahabharata does not say who is the villain here.
- **Notes:** Epic tier (Shanti Parva, one long Ganguli section). Indra series, dark episode; F10 (emotion → shares): injustice. F6 trap: do not open on 'you think Prahlada's story is about Narasimha'; open on the disguised student.

### 18. Indra came begging in a Brahmin's robe. Karna cut his own skin off to pay him.

- **Tier:** B · strong, needs the right cut · **tags:** indra, epic, sacrifice
- **Source:** `mahabharata_ganguli` 3.308–3.310 (3 entries)
- **Hook:** Karna was born with armour grown into his skin. Indra wanted it off him before the war. He came at noon, when Karna refuses no one.
- **Arc:** Surya warns Karna in a dream that Indra will come disguised to beg the armour and earrings; Karna refuses to refuse. Indra comes; Karna cuts the armour from his body, blood running, and hands it over; Indra, ashamed, gives him the single-use spear. The gods shout; Karna is called Vaikartana, the cutter.
- **Kicker:** Indra's cheating gave Arjuna the war. Karna's keeping his word cost him everything, and he knew it in advance. The epic says the god blushed.
- **Notes:** Epic tier, very well known; the value is the Indra angle for the series (the god who begs). Companion: Indra as hawk testing Shibi (animal section).

### 19. The thunderbolt was a dead sage's spine.

- **Tier:** B · strong, needs the right cut · **tags:** indra, epic, sacrifice
- **Source:** `mahabharata_ganguli` 3.100–3.101 (2 entries)
- **Hook:** No weapon could kill Vritra. The gods went to a living sage and asked for his bones.
- **Arc:** Vishnu tells the gods only a weapon made from Dadhicha's bones can kill Vritra; the sage gives up his body; Tvashtr makes the vajra; Indra kills Vritra; the demons flee into the sea and plot by night to kill the sages. (The Vedic root is the Ashvins' Dadhyanc, see the horse-head story.)
- **Kicker:** In the Veda Dadhyanc lost his head to keep a secret. In the epic he gives his whole skeleton to end a war. The same name, a thousand years apart, and the thing he gives up grows.
- **Notes:** Epic tier; companion to indra-dadhyanc-horse-head. Risk: 'everyone knows this'; the hook must start on the sage, not on Vritra.

### 20. Indra's punishment, and the ram that gave him back his manhood.

- **Tier:** B · strong, needs the right cut · **tags:** indra, epic, adult, animal
- **Source:** `ramayana_dutt` 1.47–1.49 (3 entries)
- **Hook:** Everyone knows Ahalya became a stone. Few know what Gautama did to Indra, and what the gods used to repair him.
- **Arc:** Indra, in Gautama's shape, seduces Ahalya, who knows him and consents; Gautama returns, curses Indra to lose his testicles and Ahalya to live unseen on ashes for a thousand years until Rama comes. Indra, 'deprived of my scrotum', complains to the gods that he did it to serve them (to break Gautama's ascetic power); the gods fit him with a ram's testicles, taken from the ram of the sacrifice. Rama arrives; Ahalya is restored.
- **Kicker:** The Valmiki Ramayana says Ahalya was not fooled. And Indra's excuse to the gods was: I did it for you. The oldest telling is uglier and more honest than the stone.
- **Notes:** Epic tier (Bala Kanda, Dutt). Indra series, the fall. Adult content; devotional sensitivity high (Ahalya's consent is in the text, 1.47). F6 trap: do not open on 'you think she was a stone'. Open on Gautama's door.

### 21. The day Indra lost to a cowherd, and crowned him anyway.

- **Tier:** B · strong, needs the right cut · **tags:** indra, krishna, epic
- **Source:** `harivamsa_dutt` 1.73–1.77 (5 entries)
- **Hook:** Krishna told the cowherds to stop worshipping Indra. Indra answered with seven days of rain.
- **Arc:** Krishna argues that cowherds should worship the mountain and the cows, not the rain-god; the Govardhana festival is held; Indra, insulted, sends the clouds of doom; Krishna lifts the mountain as an umbrella for seven days; Indra comes down, accepts, and anoints Krishna 'Govinda', lord of cows, with milk from Surabhi.
- **Kicker:** In the Harivamsa Indra does not sulk. He comes down, admits it, and gives the boy a new name. The audience that wants Indra redeemed should see the one story where he redeems himself.
- **Notes:** Epic tier (Harivamsa, Dutt translation; the corpus has it in English). Indra series, closing episode candidate. The published channel has a Samaveda-Krishna short; this is a different cut.

### 22. Indra was taken prisoner by a teenager.

- **Tier:** B · strong, needs the right cut · **tags:** indra, epic, war
- **Source:** `ramayana_dutt` 7.32–7.35 (4 entries)
- **Hook:** Ravana's son fought the king of the gods, tied him up, and carried him to Lanka. Brahma had to come and negotiate the ransom.
- **Arc:** Meghanada fights Indra, uses invisibility, binds him and takes him to Lanka; Brahma comes to Ravana's court to bargain; Meghanada asks for immortality, gets a conditional boon instead, and the title Indrajit; Indra is released. Brahma reminds Indra it is the price of Ahalya (in the Uttara Kanda's version).
- **Kicker:** The god who was 'never harmed' ended up a hostage in a demon's palace, and the Ramayana says he deserved it.
- **Notes:** Epic tier (Uttara Kanda). Dutt's Uttara Kanda sections 7.32 (the march on Indra's heaven) to 7.35 (Brahma names him Indrajit and recalls Ahalya); numbering differs from the critical edition.


## S2 · Women who bargain, refuse and win

Apala (796k) was a girl who made a deal with a god. These are her successors: women with a want, an obstacle and a line of their own.

### 23. She grew old in her father's house, sick and unmarried. Then she wrote to the twin gods.

- **Tier:** A · make next · **tags:** woman, healing, marriage
- **Source:** `rigveda` 10.039.01–10.040.14 (28 entries); `brhaddevata` 7.48–7.48 (1 entries)
- **Hook:** Ghosha stayed in her father's house past the age of marriage, with a disease on her skin. Her father was a famous poet. She wrote her own hymn.
- **Hook (Hindi draft):** घोषा पिता के घर में बूढ़ी होती रही, बीमार, अविवाहित। पिता मशहूर कवि थे। उसने अपना सूक्त खुद लिखा।
- **Arc:** Ghosha, daughter of Kakshivat, calls the Ashvins' chariot 'as easy to invoke as a father's name', lists every rescue they ever did (Bhujyu from the sea, Rebha from the well, the old Chyavana made young, the mare's foal, the bride for Vimada), and asks them: you did all that for strangers, do it for me. 10.40 is her wedding-eve hymn ('the bride goes to the groom's house'). The Brhaddevata records that the Nasatyas gave Ghosha a husband.
- **Kicker:** The Rigveda has two hymns by a woman who refused to be a story told about her. She listed the gods' record like a lawyer and asked for her turn. The published Apala made a deal with Indra; Ghosha filed a claim with the Ashvins.
- **Notes:** Woman lead; direct successor to Apala (the hit). F3: open on the skin and the father's house. The Ashvin catalogue in 10.39 is where the Bhujyu, Rebha, Vandana stories can be dropped as one-line images.

### 24. He offered her half of everything. She asked whether it would make her immortal.

- **Tier:** A · make next · **tags:** woman, philosophy, marriage
- **Source:** `brhadaranyaka_upanishad` 2.4.1–2.4.14 (14 entries)
- **Hook:** The richest sage in Videha was leaving home. He called his wife to divide the property. She asked a question that made him sit back down.
- **Hook (Hindi draft):** विदेह के सबसे धनी ऋषि याज्ञवल्क्य घर छोड़ने चले। पत्नी मैत्रेयी को बुलाया, संपत्ति बांटने। उसने एक सवाल पूछा, और ऋषि वापस बैठ गए।
- **Arc:** Yajnavalkya: 'I am going away; let me settle between you and Katyayani.' Maitreyi: 'If this whole earth full of wealth were mine, would I be immortal by it?' 'No. Your life would be like the life of the rich.' 'Then what would I do with what does not make me immortal? Tell me what you know.' He teaches: the husband is dear not for the husband's sake but for the self's; the lump of salt dissolved in water; 'after death there is no consciousness, that is what I say'. She: 'you have confused me.' He explains: where there is duality one sees another; where all is self, who sees whom?
- **Kicker:** The second wife, the text says, 'knew only what women know'. The first wife refused the money. Only one of them has an Upanishad named after her conversation.
- **Notes:** Woman lead, philosophy (saves, F10). Madhavananda's translation in the corpus interleaves Shankara's commentary; the writer must use only the dialogue lines. The 'other wife knew only what women know' line is the text's, and it is the hook's edge; do not soften, do not lecture.

### 25. A woman stood up in the king's assembly with two questions, like an archer with two arrows.

- **Tier:** A · make next · **tags:** woman, debate, death
- **Source:** `brhadaranyaka_upanishad` 3.6.1–3.6.1 (1 entries); `brhadaranyaka_upanishad` 3.8.1–3.8.12 (12 entries, 1 empty); `brhadaranyaka_upanishad` 3.9.1–3.9.26 (25 entries, 1 empty)
- **Hook:** King Janaka put a thousand cows in a pen for the wisest man present. Yajnavalkya told his pupil to drive them home before the debate began. Then a woman stood up.
- **Hook (Hindi draft):** जनक ने हज़ार गायें बांध दीं, सबसे ज्ञानी के लिए। याज्ञवल्क्य ने शिष्य से कहा, बहस से पहले ही हांक ले जाओ। फिर एक स्त्री खड़ी हुई।
- **Arc:** Gargi Vachaknavi asks what water is woven on, then air, then the sky, upward until Yajnavalkya says 'do not ask too much, Gargi, or your head will fall off.' She stops. Later she rises again: 'like a warrior from Kashi with two arrows'; she asks about what is above heaven, below earth, between; he answers 'the imperishable', in which space is woven. She tells the Brahmins: 'bow to him; none of you will defeat him.' Then Shakalya keeps pushing, 'how many gods?', three hundred and three, thirty-three, six, three, two, one and a half, one; Yajnavalkya warns him; he asks once more, and his head falls off, and robbers carry away his bones thinking they are something else.
- **Kicker:** Two people were warned that day that a question could cost them their head. The woman knew when to stop. The man did not. The Upanishad lets her declare the winner.
- **Notes:** Woman lead + death stakes. BU 3.9 is long; cite 3.9.1-3.9.26 but script only the countdown of gods and the head. SB 11.6.3 and JB 2.75-2.77 have the cows episode in English too. Expect comments about 'head will fall off' (the text's idiom for a debate forfeit; say so in one line, F9).

### 26. A queen's spell to rule her husband and crush her rivals. It is in the Rigveda.

- **Tier:** B · strong, needs the right cut · **tags:** woman, indra, spell, marriage
- **Source:** `rigveda` 10.159.01–10.159.06 (6 entries)
- **Hook:** 'My sons kill their enemies. My daughter is a queen. I have conquered my husband.' The woman speaking is Indra's wife.
- **Arc:** Shachi Paulomi (per the tradition) speaks in the first person as the sun rises: 'I am the banner and the head; my husband obeys my will; I have seized the glory of the other wives; I am victorious over my rivals, that I may hold imperial sway over this hero and his people.'
- **Kicker:** The Veda's model of a wife is not a silent one. It is a woman at dawn announcing that she has won. Six verses, no apology.
- **Notes:** Woman's first-person voice; Indra crossover. No plot, so build the arc around a palace morning (the co-wives, the rising sun, the sons). Companion: 10.145, the herb spell against a rival wife (same genre, anonymous speaker) can supply the images of the rival being 'blown away like a leaf'.

### 27. She dug a plant at dawn and whispered her rival's name into it. Then she did not say the name.

- **Tier:** C · micro, risky or thin · **tags:** woman, spell, marriage
- **Source:** `rigveda` 10.145.01–10.145.06 (6 entries)
- **Hook:** A woman digs up a herb to drive away her husband's other wife: 'Her very name I utter not.'
- **Arc:** The speaker digs 'the most effectual plant', blows the rival away, claims to be stronger, refuses to speak her name, and binds the husband 'as a cow hastens to her calf'.
- **Kicker:** The Rigveda preserved a co-wife's spell word for word, and its sharpest line is the thing she refused to say.
- **Notes:** Micro; pair with shachi-co-wife-spell rather than run alone. Risk: no protagonist with a name.

### 28. The gods sold a goddess to buy Soma. Then they stole her back with a song.

- **Tier:** A · make next · **tags:** woman, music, gods, trick
- **Source:** `satapatha_brahmana` 3.2.4.1–3.2.4.7 (7 entries); `aitareya_brahmana` 5.1–5.1 (1 entries)
- **Hook:** Soma was in heaven; the gods were on earth. The Gandharvas who guarded it loved women. The gods had one woman: Speech.
- **Hook (Hindi draft):** सोम स्वर्ग में था, देवता धरती पर। सोम के पहरेदार गंधर्व स्त्रियों के शौकीन थे। देवताओं के पास एक ही स्त्री थी: वाक्, यानी वाणी।
- **Arc:** Gayatri as a bird steals Soma; the Gandharva Vishvavasu snatches it. 'Gandharvas are fond of women; send Vac; she will come back.' They trade: Soma for Vac, 'as long as she wishes to stay'. The Gandharvas recite the Vedas to her: 'see how we know!' The gods invent the lute and sit playing and singing: 'thus we will amuse you.' She turns to the gods. In the Aitareya, Speech herself proposes the bargain, and the gods first refuse: 'how could we be without you?'
- **Kicker:** Faced with scholars and musicians, the goddess of language chose the musicians. The Brahmana says that is why women to this day prefer the one who sings. The Veda invented the vina to win back a woman.
- **Notes:** Music angle (F8: the audience notices and talks about music). F6 trap: not 'Soma was really a drink'; open on the sale. The text's 'women are fond of the one who sings' line is the kicker, say it as the text's claim.

### 29. Fortune was born shining, and the gods' first thought was to rob her.

- **Tier:** B · strong, needs the right cut · **tags:** woman, gods, lakshmi
- **Source:** `satapatha_brahmana` 11.4.3.1–11.4.3.10 (10 entries)
- **Hook:** Shri came out of Prajapati resplendent and trembling. The gods looked at her and said: let us kill her and take all this.
- **Arc:** Prajapati forbids the killing ('she is a woman; one does not kill women') but lets them take: Agni takes her food, Soma her royal power, Varuna her sovereignty, Mitra her rank, Indra her strength, Brhaspati her holy lustre, Savitr her dominion, Pushan her wealth, Sarasvati her prosperity, Tvashtr her beauty. She complains; Prajapati: 'ask it back by sacrifice.' She invents the ten-dish offering and, naming each god, takes back each thing.
- **Kicker:** The goddess of wealth was not given wealth. She was stripped of it, told to earn it back, and did, item by item, from the gods who took it. That is the Veda's origin of Lakshmi.
- **Notes:** Devotional sensitivity: gods robbing Lakshmi; it is the text's own story and ends with her winning. Keep the list of ten to four or five images (food, power, strength, beauty).

### 30. Mind and Speech argued over who was greater. Speech lost, and stopped speaking.

- **Tier:** C · micro, risky or thin · **tags:** micro, gods, wordplay
- **Source:** `satapatha_brahmana` 1.4.5.8–1.4.5.13 (6 entries)
- **Hook:** 'I say what you only think.' 'You only say what I have already thought.' They went to Prajapati to decide.
- **Arc:** Mind: 'you only speak what I understand'; Speech: 'what you know, I make known'. Prajapati rules for Mind ('speech imitates you'). Speech, gainsaid, is dismayed and miscarries; she refuses to carry oblations for Prajapati, so he is offered to in silence.
- **Kicker:** Because Speech once lost an argument, one god in the Veda is still worshipped without a word.
- **Notes:** Micro (45-60 s). Good interstitial for the series on Vac (pair with vac-sold-for-soma).

### 31. The gods raced for the bride. The twins won on a donkey cart.

- **Tier:** B · strong, needs the right cut · **tags:** woman, race, animal, wedding
- **Source:** `aitareya_brahmana` 17.1–17.3 (3 entries); `rigveda` 10.085.06–10.085.16 (11 entries)
- **Hook:** Surya, the Sun's daughter, was to be married. The gods decided the groomsmen by a race. Agni was fastest, Ushas was the dawn, Indra had the horses. The Ashvins turned up with asses.
- **Arc:** Prajapati gives his daughter Surya Savitri to King Soma; all the gods come as groomsmen; they race for her: Agni on a mule-cart, Ushas on red cows, Indra on horses, the Ashvins on an ass-cart; each bargains for a share as it is overtaken; the Ashvins win the bride, and that is why the Ashvina litany is theirs. The Rigveda wedding hymn (10.85) describes the bride's journey, 'the Ashvins were the wooers'.
- **Kicker:** Every Hindu wedding still recites mantras from Surya's wedding. Few know the groomsmen were chosen by a race, and the slowest animal won.
- **Notes:** Explainer risk (F1): keep one protagonist, the Ashvins (underdogs, physicians, excluded from Soma). The AB passage is dense with ritual; use only the race. RV 10.85 verses 6-16 for the wedding pictures.

### 32. A king who had been turned into a woman, and the wife who prayed him back.

- **Tier:** C · micro, risky or thin · **tags:** gender, seer, sparse
- **Source:** `brhaddevata` 6.40–6.41 (2 entries); `rigveda` 08.001.33–08.001.34 (2 entries)
- **Hook:** Asanga, son of Playoga, was changed into a woman by a curse. His wife Shashvati composed a verse. The seer Medhatithi changed him back.
- **Arc:** The Brhaddevata records the curse and the restoration in two lines; the Rigveda keeps Shashvati's verse rejoicing at her husband's manhood restored (8.1.34) and Asanga's gift of ten thousand cattle to the singer.
- **Kicker:** The Rigveda contains a verse by a woman celebrating that her husband is a man again. Three thousand years ago gender was already a story people told.
- **Notes:** Fascinating, thin in the corpus (BD 6.40 text, RV verse explicit). Treat as a pinned-comment or part of a 'strange verses' compilation, not a stand-alone short unless the producer wants the risk.

### 33. She followed Death into the forest and out-talked him.

- **Tier:** A · make next · **tags:** woman, death, epic
- **Source:** `mahabharata_ganguli` 3.292–3.297 (6 entries)
- **Hook:** She chose a husband who had one year to live. On the day, she walked behind Yama as he carried the soul away, and would not go home.
- **Hook (Hindi draft):** सावित्री ने वो पति चुना जिसके पास एक साल था। उस दिन, यम उसकी आत्मा ले चले, और सावित्री पीछे-पीछे चलती रही, लौटी नहीं।
- **Arc:** Savitri chooses Satyavan knowing Narada's prophecy; on the day she fasts, accompanies him to the forest; Yama comes in person; she follows him, speaking of dharma until he grants boons: her father-in-law's sight and kingdom, her father's sons, and 'a hundred sons for me', which cannot happen without Satyavan. Yama laughs and returns the soul.
- **Kicker:** The boy Nachiketa won from Death with silence and refusal. Savitri won with argument. Both are in the same tradition, and only one of them is told as a 'wife's duty'.
- **Notes:** Epic tier (Vana Parva). Woman lead; natural pairing with the queued Nachiketa short (same opponent). The 'devoted wife' frame is the trap (F6): open on her walking behind Yama.

### 34. The king denied knowing her. She answered him in front of his whole court.

- **Tier:** A · make next · **tags:** woman, defiance, epic, bharat
- **Source:** `mahabharata_ganguli` 1.73–1.74 (2 entries)
- **Hook:** Shakuntala walked into Dushyanta's hall with their son. The king said: I do not know you. There was no ring in this version.
- **Arc:** In the Mahabharata (not Kalidasa) there is no ring, no curse: the king simply lies. Shakuntala's speech: a wife is half the man; a son is the father reborn; 'you alone know your own truth; the gods who live in the heart see it'; she turns to leave. A voice from the sky confirms the boy; Dushyanta says he feared the court would doubt; the boy is Bharata, after whom the land is named.
- **Kicker:** Kalidasa gave the king a magic excuse. The Mahabharata gave him none. In the older story the only magic is a woman refusing to be told she is lying.
- **Notes:** Epic tier (Adi Parva). F6 trap: 'you think there was a ring' is a correction hook; open instead on the hall and the child. The Bharata naming is the kicker's second beat (and links to AB 39.9, Bharata's horse-sacrifices).

### 35. A princess threw a Brahmin's daughter into a well. The Brahmin's daughter made her a servant.

- **Tier:** B · strong, needs the right cut · **tags:** woman, rivalry, epic
- **Source:** `mahabharata_ganguli` 1.78–1.83 (6 entries)
- **Hook:** Two girls fought over a dress. One was the king's daughter, one the priest's. The priest's daughter ended up in a well, and then on top.
- **Arc:** Devayani (daughter of Shukra, priest of the demons) and Sharmishtha (the demon king's daughter) quarrel; Sharmishtha pushes her into a well; Yayati pulls her out by the hand. Devayani demands Sharmishtha as her maid as the price of her father's priesthood; the demon king agrees. Devayani marries Yayati; Sharmishtha, the maid, secretly bears Yayati three sons; Devayani discovers it; Shukra curses Yayati with old age.
- **Kicker:** Of the two women, the one who was made a servant became the mother of the line that leads to the Kurus. The Mahabharata keeps score over centuries.
- **Notes:** Epic tier. Women's rivalry story with a sting; leads into yayati-puru. Keep Kacha (the previous chapters) as a separate short.

### 36. A mother's speech to a son who would not fight. The Mahabharata preserved every word.

- **Tier:** B · strong, needs the right cut · **tags:** woman, war, epic, argument
- **Source:** `mahabharata_ganguli` 5.133–5.136 (4 entries)
- **Hook:** Her son had lost his kingdom and lay in bed. Vidula stood over him and said: either blaze for a moment or smoulder for a lifetime.
- **Arc:** Kunti tells Krishna the old story to carry to Yudhishthira: Vidula's son Sanjaya, defeated, lies depressed; she rains contempt and argument on him ('I did not bear you to be a eunuch of fortune'); he answers; she wins; he rises and fights.
- **Kicker:** Kunti sent this to her sons instead of a blessing. The most ferocious speech in the Mahabharata before the war is a mother's.
- **Notes:** Epic tier (Udyoga Parva). Argument short (F11) with a protagonist. Dark on gender ('eunuch', 'is my womb to blame'); keep the text's own force without adding.

### 37. A snake killed her son. A fowler caught the snake. She refused to let it die.

- **Tier:** A · make next · **tags:** woman, animal, death, argument, epic
- **Source:** `mahabharata_ganguli` 13.1–13.1 (1 entries)
- **Hook:** The fowler dragged the snake to the mother in a noose: say the word and it dies. The mother said: killing it will not bring my son back. Then the snake spoke.
- **Hook (Hindi draft):** बहेलिया सांप को फंदे में बांधकर मां के पास लाया: कह दो, मार दूं। मां बोली: इसे मारने से मेरा बेटा नहीं लौटेगा। तब सांप बोला।
- **Arc:** Gautami's son dies of snakebite; Arjunaka the fowler brings the snake; she refuses revenge; the snake says 'Death sent me'; Death appears: 'Time sent me'; Time: 'the boy's own deeds sent him'; each defendant hands the blame up the chain, and the boy's karma is the final answer; the fowler frees the snake.
- **Kicker:** A courtroom with four defendants (snake, Death, Time, karma) and a mother who refuses to be the executioner. The Mahabharata opens its last book of teachings not with a sage but with her.
- **Notes:** Epic tier (Anushasana Parva, one long section). Animal + loyalty to principle + argument (comments) + grief (shares). Strong candidate for the 'argument inside a story' test (F11).


## S3 · Animals, loyalty and the ones who stayed

F4: the two dog shorts out-shared everything. Dogs, a horse's head, a falcon, a fish, a vulture, four unborn birds.

### 38. A hawk demanded the pigeon back. The king gave his own flesh instead.

- **Tier:** A · make next · **tags:** animal, indra, sacrifice, epic
- **Source:** `mahabharata_ganguli` 3.130–3.131 (2 entries)
- **Hook:** A pigeon flew into King Shibi's lap, chased by a hawk. The hawk spoke: that is my food. Give it back. The king said: take me instead.
- **Hook (Hindi draft):** एक कबूतर राजा शिबि की गोद में आ गिरा, पीछे एक बाज़। बाज़ ने कहा: वो मेरा खाना है, लौटा दो। राजा ने कहा: मुझे ले लो।
- **Arc:** Shibi refuses to surrender the refugee bird; the hawk argues like a lawyer (the hunter must eat too; you deprive my chicks); the king offers a bull, then his own flesh, equal to the pigeon's weight. He cuts and cuts; the scale will not balance; he climbs onto it himself. The hawk is Indra, the pigeon Agni; they reveal themselves and restore him.
- **Kicker:** The gods did not test whether the king was generous. They tested whether he would keep protecting someone after it stopped being cheap.
- **Notes:** Epic tier (Vana Parva). Animal + loyalty (F4) + Indra series crossover. One of the most shareable stories in the corpus (emotion → shares, F10).

### 39. The dogs held a Vedic chant. The subject was lunch.

- **Tier:** A · make next · **tags:** animal, comedy, satire
- **Source:** `chandogya_upanishad` 1.12.1–1.12.5 (5 entries)
- **Hook:** A student went out to study the Veda. A white dog appeared. The other dogs asked it: revered sir, please sing for us, we are hungry.
- **Hook (Hindi draft):** एक विद्यार्थी वेद पढ़ने निकला। एक सफ़ेद कुत्ता आया। बाकी कुत्तों ने उससे कहा: श्रीमान, हमारे लिए गाइए, हमें भूख लगी है।
- **Arc:** Baka Dalbhya sees a white dog; small dogs gather and ask it to sing them food; 'come tomorrow morning'. Next morning the dogs move in a line, each holding the tail of the one in front, exactly as priests do holding each other at the chant, sit, say 'Him', and chant: 'Om, let us eat! Om, let us drink! Om, may the god who gives rain bring us food!'
- **Kicker:** The Upanishad that teaches the secret of Om also records dogs performing a flawless Soma chant for breakfast. It is either the oldest satire of priests, or the oldest admission that hunger is holy. The text does not say which.
- **Notes:** Animal (F4, the channel's two dog shorts out-share everything). Comedy with a real arc (request → promise → performance). One cold open, one image system (the tails). F9 watch: 'is it mocking priests?' Answer in the kicker as the text's ambiguity.

### 40. The greatest sage in the Rigveda was caught burgling a god's house by a dog.

- **Tier:** A · make next · **tags:** animal, seer, comedy, spell
- **Source:** `rigveda` 07.055.01–07.055.08 (8 entries); `brhaddevata` 6.11–6.13 (3 entries, 1 empty)
- **Hook:** Vasishtha was starving. At night he crept into Varuna's house for food. The dog woke up.
- **Hook (Hindi draft):** वसिष्ठ भूखे थे। रात में वरुण के घर में घुसे, कुछ खाने को। कुत्ता जाग गया।
- **Arc:** The Brhaddevata: Vasishtha, after three days without food, enters Varuna's house at night; a dog runs at him barking; he pacifies it with the verses that are now RV 7.55: 'Son of Sarama, tawny one, your teeth gleam like spears; bark at the thief, not at Indra's singers; sleep, mother, sleep, father, sleep dog, sleep master of the house; the women sleeping in the court, we close their eyes as we close this house.' The dog sleeps; the sage goes in.
- **Kicker:** The Rigveda's sleep spell was composed by a hungry sage talking his way past a watchdog. The dog is the son of Sarama, the same dog family as the one who found Indra's cows. In this story the dog is the honest one.
- **Notes:** Animal + a sage behaving badly; the Dog and Sarama shorts were the channel's biggest. BD 6.11 and 6.13 are truncated in the corpus; the RV hymn is complete, and the burglary frame is in BD 6.12 which is intact. The 'house of Varuna' and the famine are also in the later Vasishtha tradition; keep to BD.

### 41. The god of fire ran away from his job. A fish told the gods where he was.

- **Tier:** A · make next · **tags:** animal, gods, burnout
- **Source:** `yajurveda_black` 2.6.6–2.6.6 (1 entries); `rigveda` 10.051.01–10.051.09 (9 entries); `brhaddevata` 7.62–7.66 (5 entries)
- **Hook:** Agni had three elder brothers. All three died carrying offerings to the gods. So Agni hid in the water.
- **Hook (Hindi draft):** अग्नि के तीन बड़े भाई थे। तीनों देवताओं तक हवि पहुंचाते-पहुंचाते मर गए। तो अग्नि पानी में छिप गए।
- **Arc:** Taittiriya: Agni, afraid of the fate of his brothers, enters the waters; the gods search; a fish betrays him; Agni curses it: 'may they kill you at pleasure, since you told'; the gods promise him the first and last offering and 'life unwasting'. Rigveda 10.51: the dialogue: Varuna, 'who saw you hidden in the plants and waters?'; Agni, 'I fled in fear of the office; my elder brothers chose this road and died'; the gods, 'come, man is pious and waits; we give you a life that does not wear out'; Agni names his terms: the first offerings and the last, the fat of the waters, the long life of the gods.
- **Kicker:** The Veda's first recorded resignation letter was written by Fire, and the first severance package was negotiated by the god everyone thought was the servant. He only came back with a contract.
- **Notes:** Animal in a supporting role (the fish, cursed to be eaten); burnout angle for today. Three texts tell one story; TS 2.6.6 is one long English entry, RV 10.51 is complete dialogue; BD 7.61 and 7.67 are empty in the corpus (skip). Pair with the epic Bhrigu-curses-Agni story.

### 42. A father left his son in the middle of the ocean 'as a dead man leaves his riches'.

- **Tier:** B · strong, needs the right cut · **tags:** rescue, father, sea
- **Source:** `rigveda` 01.116.03–01.116.05 (3 entries); `rigveda` 01.117.14–01.117.15 (2 entries); `rigveda` 01.182.05–01.182.07 (3 entries)
- **Hook:** Tugra abandoned Bhujyu in the ocean, 'in the cloud of waters, where there is nothing to hold'. The twin gods came with ships that had a hundred oars.
- **Arc:** Bhujyu, son of Tugra, is left in the sea (the hymns vary: a father's abandonment, a shipwreck); for three nights and three days the Ashvins carry him in winged ships, 'with a hundred oars', over the sea that gives no support, and set him on the shore. The same hymns list their other rescues: Rebha left for dead in a well for ten nights, Vandana buried, Atri thrown into the burning pit by the demons and kept cool.
- **Kicker:** The Ashvins were the two gods the other gods would not let drink Soma. They spent their time pulling people out of wells, pits and oceans. The Rigveda remembers the physicians better than their superiors.
- **Notes:** Rescue sequence with a father's betrayal as the opening image. Risk: the hymns are catalogues, so one protagonist (Bhujyu) must carry it and the others are the kicker's montage. Ashvins thread: also suryas-wedding, ghosha, dadhyanc, (published) sukanya.

### 43. In another Veda, Indra's dog took the bribe.

- **Tier:** B · strong, needs the right cut · **tags:** animal, indra, argument, sequel
- **Source:** `brhaddevata` 8.24–8.34 (11 entries, 3 empty); `jaiminiya_brahmana` 2.439–2.440 (2 entries)
- **Hook:** You have seen Sarama find Indra's cows. The Brhaddevata has the ending the Rigveda left out: she drank the Panis' milk, and lied to Indra.
- **Arc:** The Panis hide the cows across the Rasa; Sarama crosses, refuses their offer of sisterhood (the RV dialogue), but then, by 'natural taste and greed', asks for milk, drinks it, returns, and tells Indra 'no' when he asks if she found the cows; Indra kicks her; she vomits the milk and confesses; Indra goes himself. The Jaiminiya version has her succeed, and Indra blesses her offspring: 'they shall be eaters of food'.
- **Kicker:** The channel's loyal dog has a second life in the Brahmanas, and in one of them loyalty failed. The Veda keeps both endings and never chooses.
- **Notes:** Sequel/argument short (F11) built on the published Sarama hit; the audience knows the character. F6 caution: this is a 'but actually' structure by nature; open on the milk, not on 'you were told'. BD 8.30, 8.32-8.33, 8.35-8.36 are empty in the corpus; the key lines (8.31, 8.34) are present.

### 44. A sage became a bird to have children fast. Then he left them in the forest that was about to burn.

- **Tier:** A · make next · **tags:** animal, father, fire, epic
- **Source:** `mahabharata_ganguli` 1.231–1.235 (5 entries)
- **Hook:** Mandapala learned that heaven is closed to the childless. He became a bird, fathered four chicks in a week, and flew off with another female. Then Arjuna and Krishna set the Khandava forest on fire.
- **Arc:** The four unhatched chicks are left with their mother Jarita; the fire comes; she offers to cover them with her body; the chicks, still featherless, debate: 'go, save yourself, you can have more sons'; one proposes the rat-hole, the others refuse ('the mongoose'); the mother flees; the chicks pray to Agni, who spares them because Mandapala had once praised him; the father returns; Jarita's speech to him is the sharpest in the chapter.
- **Kicker:** The longest dialogue in the burning of Khandava is not Arjuna's. It is four unborn birds arguing about whether their mother should live. The Mahabharata gives the smallest creatures the biggest question.
- **Notes:** Epic tier (Adi Parva). Animal + abandonment + loyalty; shares (F10). The Mandapala-Lapita subplot can be cut; keep the nest.

### 45. An old vulture fought a king for a woman he had met once.

- **Tier:** A · make next · **tags:** animal, loyalty, epic
- **Source:** `ramayana_dutt` 3.49–3.51 (3 entries); `ramayana_dutt` 3.67–3.69 (3 entries)
- **Hook:** Jatayu was old enough to have been Dasharatha's friend. He saw Ravana's chariot and did not calculate.
- **Arc:** Jatayu first argues with Ravana (the dharma of kings and guests), then attacks: breaks the chariot, kills the mules, tears the charioteer; Ravana cuts his wings. Rama finds him dying; he gives his report and dies; Rama performs his funeral as for a father.
- **Kicker:** Rama found Sita's trail because a bird refused to be too old for a fight. The epic's first funeral rite in exile was for a vulture.
- **Notes:** Epic tier (Aranya Kanda, Dutt). The two dog shorts were the channel's most-shared; loyal animals travel (F4). Dutt's 3.68 is the dying report, 3.69 the cremation ('I shall produce fire and burn the body of this king of birds').

### 46. Two sisters bet on the colour of a horse's tail. The loser's son became the king of birds.

- **Tier:** A · make next · **tags:** animal, rivalry, epic, vedic-root
- **Source:** `mahabharata_ganguli` 1.20–1.23 (4 entries); `satapatha_brahmana` 3.6.2.2–3.6.2.9 (8 entries)
- **Hook:** Kadru said the divine horse had a black tail. Vinata said white. The loser would be the other's slave. Kadru had a thousand snake sons, and told them to hang from the tail.
- **Arc:** The snakes refuse to cheat; Kadru curses them to burn in Janamejaya's fire; some relent and hang from the tail as black hairs; Vinata loses and serves; her son Garuda is born, learns the price of freedom (the amrita), and the great heist begins. The Shatapatha has the Vedic seed: two 'illusions', Suparni and Kadru, bet on who sees farther across the ocean ('a white horse at a post; I see its tail waving'), and the loser must fetch Soma from heaven for the winner.
- **Kicker:** The Mahabharata's snakes-and-birds war began with a bet in the Veda, where the two sisters were Speech and Earth and the prize was Soma. The story grew a thousand snakes and a horse's tail; the bet is the same.
- **Notes:** Epic tier with a verified Vedic root (SB 3.6.2, English). Animal; family feud. Could be two shorts: the bet (above) and Garuda's heist (1.24-1.34). F9: 'why did the snakes get cursed by their own mother?' is in the text, say it.

### 47. He gave half his life to bring his bride back, and vowed to kill every frog. A frog talked him out of it.

- **Tier:** B · strong, needs the right cut · **tags:** animal, love, epic
- **Source:** `mahabharata_ganguli` 1.8–1.9 (2 entries)
- **Hook:** Pramadvara died of a snakebite the day before her wedding. Ruru begged the gods; a messenger said: give her half your life. He did. Then he picked up a stick.
- **Arc:** Ruru revives Pramadvara at the cost of half his years and vows to kill every snake; he finds a dundubha (a harmless water-snake, a 'frog-eater'), raises his staff; the creature speaks: it was a Brahmin, Sahasrapat, cursed into this form for frightening a friend with a grass snake; it argues that killing the harmless is sin; Ruru relents; the curse lifts.
- **Kicker:** The man who had just bought back his wife with half his life nearly spent the rest of it on revenge against animals. One snake with a human past stopped him.
- **Notes:** Epic tier (Adi Parva, Pauloma). Animal + love; the 'frog' is a water-snake in Ganguli. Short enough for 90 s.

### 48. Before man, the gods tried living inside a cow. They said: not enough.

- **Tier:** B · strong, needs the right cut · **tags:** animal, creation, micro
- **Source:** `aitareya_upanishad` 1.1–2.5 (9 entries)
- **Hook:** The Self made the gods, and the gods fell into the great ocean, and Hunger and Thirst jumped on them. They asked for a body to live in.
- **Arc:** He brings them a cow: 'not sufficient for us'. A horse: 'not sufficient'. He brings them a human: 'O well made!' and they enter: fire as speech into the mouth, wind as breath, sun as sight. Then Hunger and Thirst ask: 'and where do we live?' 'Inside them, with the gods. Wherever an offering is made, you have a share.'
- **Kicker:** Hunger is a god who lives where the gods live, by the oldest treaty in the Upanishads. That is why, the text says, you cannot feed a god without feeding hunger.
- **Notes:** Aitareya Upanishad 1-2 (short, complete in English). Animal as the rejected option; comedy of creation. Micro (60-75 s).


## S4 · Defiance: outsiders who out-argued the insiders

Slaves' sons, disinherited sons, crooked boys, gleaners, shopkeepers. Injustice travels (F10) and starts arguments (F11).

### 49. They called him a slave woman's son and sent him to die of thirst. The river followed him.

- **Tier:** A · make next · **tags:** defiance, caste, river
- **Source:** `aitareya_brahmana` 8.1–8.1 (1 entries); `kausitaki_brahmana` 12.3.11–12.3.11 (1 entries)
- **Hook:** At the sages' session on the Sarasvati, Kavasha sat down among them. 'Child of a slave woman. A cheat. No Brahmin. How did he get consecrated?' They sent him into the desert: let thirst kill him.
- **Hook (Hindi draft):** सरस्वती के किनारे ऋषियों के सत्र में कवष बैठ गया। 'दासी का बेटा। धोखेबाज़। ब्राह्मण नहीं।' उसे रेगिस्तान में भेज दिया: प्यास से मर जाए।
- **Arc:** In the wilderness, dying of thirst, Kavasha Ailusha 'sees' the hymn to the Child of the Waters; the waters well up after him; the Sarasvati runs all around him (the place is still called Parisaraka, 'where she went around'). The seers: 'the gods know him; call him back.' They summon him and recite his hymn. The Kaushitaki version: 'we will not eat with you', and the river comes anyway.
- **Kicker:** Two Vedas record that a slave woman's son was driven out by the Brahmins and that the holiest river in the Veda chose him. His hymn is in the Rigveda. Theirs, the text does not quote.
- **Notes:** Defiance; caste; river as a character. Both passages complete in English. Strong F10 (injustice → shares) and F11 (comments). Do not editorialise beyond the text; the text is already the editorial.

### 50. His brothers gave him nothing. His father gave him a trick worth a thousand cows.

- **Tier:** B · strong, needs the right cut · **tags:** inheritance, father, trick
- **Source:** `aitareya_brahmana` 22.9–22.9 (1 entries)
- **Hook:** Nabhanedishtha came home from his studies to find his brothers had divided the property. 'What did you give me?' 'Him', they said, pointing at their father.
- **Arc:** The father: 'don't mind it; the Angirases are stuck on the sixth day of their sacrifice; teach them these two hymns and they will give you the thousand cows.' He does; they discern heaven and pay. As he gathers the herd, a man in black from the north claims it: 'what is left on the sacrificial ground is mine.' Father: 'it is his; but he will give it to you.' The boy goes back and says so; the man (Rudra) gives the thousand 'to you who spoke the truth'.
- **Kicker:** The disinherited son won twice: once with a hymn, once by admitting the cows were not his. The Brahmana says truth is a speech that wins a thousand.
- **Notes:** One complete English passage; clean arc. The 'man in black from the north' is Rudra; show, don't name until the end.

### 51. Banned from the sacrifice, the outsider cited Indra's own exclusion to the king.

- **Tier:** B · strong, needs the right cut · **tags:** defiance, indra, argument
- **Source:** `aitareya_brahmana` 35.1–35.3 (3 entries)
- **Hook:** King Vishvantara held a sacrifice without the Shyaparnas. They came anyway and sat down inside the altar. One of them opened his mouth.
- **Arc:** Rama Margaveya tells the king the story of Indra's exclusion by the gods (for misusing Vishvarupa, giving the ascetics to hyenas, breaking pacts) and how Indra still got his Soma back; he reasons that a king who sacrifices without the people who know will fail; the king relents and lets them drink.
- **Kicker:** The outsider's argument for being let in was that even Indra had once been thrown out. The Brahmana ends with the king pouring for him.
- **Notes:** Defiance; pairs with indra-confession-pratardana (same list of Indra's crimes, AB 35.2). The passage is argumentative; keep the throne-room staging.

### 52. A boy bent in eight places walked into Janaka's court to free his father from the man who drowned losers.

- **Tier:** A · make next · **tags:** defiance, debate, epic, disability
- **Source:** `mahabharata_ganguli` 3.132–3.134 (3 entries)
- **Hook:** At Janaka's court, Bandin defeated every scholar in debate and had them drowned. One of them was a boy's father. The boy was twelve, and bent in eight places.
- **Hook (Hindi draft):** जनक के दरबार में बंदी हर विद्वान को बहस में हराकर पानी में डुबवा देता था। उनमें एक लड़के का पिता भी था। लड़का बारह साल का था, आठ जगह से टेढ़ा।
- **Arc:** Ashtavakra, cursed in the womb for correcting his father's recitation, goes with his uncle Shvetaketu to Mithila; the gatekeeper mocks his age; he answers; the court laughs at his body; he answers ('a man is not old by grey hair'); the duel with Bandin is a numbers game (one fire, two friends, three Vedas... up to thirteen); Bandin fails at thirteen; the drowned scholars rise from the sea; the father bathes in a river and his son's body is made straight.
- **Kicker:** The boy who was mocked for his body won with arithmetic, and the first thing the father did with his freedom was fix the body. The Mahabharata lets you decide if that was necessary.
- **Notes:** Epic tier (Vana Parva). Defiance + disability + debate (comments). Note Shvetaketu, Uddalaka, Janaka: the Upanishad cast in an epic frame, a hook for the channel's Upanishad audience.

### 53. It began with a dog that barked at the wrong man.

- **Tier:** B · strong, needs the right cut · **tags:** defiance, animal, epic
- **Source:** `mahabharata_ganguli` 1.134–1.134 (1 entries)
- **Hook:** The Pandavas' dog wandered into the forest and barked at a dark boy practising archery. Seven arrows closed its mouth without hurting it. That is how the princes found Ekalavya.
- **Arc:** The Nishada prince, refused by Drona, makes a clay Drona and learns from it; the dog's filled mouth reveals him; Arjuna complains; Drona asks for his fee: the right thumb; Ekalavya cuts it off, smiling, and keeps shooting, worse.
- **Kicker:** Everyone remembers the thumb. The epic's own first image is a dog that could not bark and was not bleeding. That was the skill Arjuna could never have.
- **Notes:** Epic tier, universally known; the only reason to make it is the dog-first cut (F4) and the honesty of the kicker. Short section (one Ganguli chapter).

### 54. The gleaner was offered heaven in person. He asked for the terms, and said no.

- **Tier:** A · make next · **tags:** defiance, philosophy, epic
- **Source:** `mahabharata_ganguli` 3.257–3.260 (4 entries)
- **Hook:** Mudgala lived on grain gleaned like a pigeon, and fed guests before himself. Durvasa came six times to eat everything he had. Then a messenger of the gods arrived with a chariot.
- **Arc:** Durvasa, the sage of rages, tests Mudgala's generosity by devouring his fortnight's grain repeatedly; Mudgala never flinches; heaven's messenger comes to take him up bodily; Mudgala asks what heaven is like; the messenger describes it honestly: the joy, and the fall when merit runs out, and the envy. Mudgala declines ('I do not want a place from which one falls') and goes on to seek the state beyond.
- **Kicker:** The epic's humblest man is the only one to interview heaven before accepting it, and the only one to turn it down.
- **Notes:** Epic tier (Vana Parva). Defiance of a different kind; saves (F10 philosophy). Confirm the Ganguli section span; the story is Vana 260-261 in some numberings.

### 55. The ascetic who thought he was the most righteous man alive was sent to learn from a shopkeeper.

- **Tier:** B · strong, needs the right cut · **tags:** defiance, caste, ethics, epic
- **Source:** `mahabharata_ganguli` 12.261–12.264 (4 entries)
- **Hook:** Jajali stood so still in the forest that birds nested in his matted hair and raised their young. A voice said: you are not as righteous as Tuladhara, the grocer of Benares.
- **Arc:** Jajali goes to the market; Tuladhara, 'holder of the scales', already knows the story of the birds; he teaches harmlessness, fair weights, and that the man who hurts no creature outranks the man who hurts himself; Jajali objects, Tuladhara answers.
- **Kicker:** The sage with a bird's nest on his head learned ethics from a man weighing rice. The Mahabharata placed its sermon on non-violence in a shop.
- **Notes:** Epic tier (Shanti Parva). Pairs with the Dharmavyadha (butcher) story; pick one. The bird-nest image is the hook.

### 56. A Brahmin was sent to learn dharma from a meat-seller in Mithila.

- **Tier:** B · strong, needs the right cut · **tags:** defiance, caste, ethics, epic
- **Source:** `mahabharata_ganguli` 3.206–3.215 (10 entries)
- **Hook:** A housewife told the proud Brahmin Kaushika she could not come at once because she was serving her husband; he lost his temper; she told him what he had done that morning. Then she sent him to a butcher.
- **Arc:** Kaushika burnt a crane with his anger; the housewife knows it without being told; she sends him to Dharmavyadha, a fowler and meat-seller of Mithila, who explains how he lives righteously in a cruel trade, serves his parents, and reads the heart's dharma; Kaushika goes home to his own neglected parents.
- **Kicker:** The two best teachers in the Vana Parva are a wife at her chores and a man who sells meat. The Brahmin's whole journey was to learn he had parents.
- **Notes:** Epic tier (Vana Parva, ten long sections; cut to the housewife and the butcher's first speech). Caste, ethics; comments will be heavy (F11).

### 57. He wanted the Vedas without a teacher. Indra came as an old man throwing sand into the Ganga.

- **Tier:** A · make next · **tags:** indra, pride, epic, teacher
- **Source:** `mahabharata_ganguli` 3.135–3.138 (4 entries)
- **Hook:** Yavakri burned with austerities to get the Vedas directly from the gods, without studying. Indra refused. Then Indra appeared on the riverbank, an old man, pouring handfuls of sand into the Ganga to build a dam.
- **Arc:** 'You are mad, old man; you cannot dam the Ganga with sand.' 'No madder than you, trying to learn the Vedas without a teacher.' Yavakri persists; Indra grants it; the knowledge without discipline leads him to Raibhya's hermitage, the daughter-in-law, Raibhya's two demons from his hair, and his death; his father's grief; and Raibhya's own son kills his father by mistake; the chain is undone by Brhadadyumna's boon.
- **Kicker:** Indra, in this story, is the only sane person. The god the audience wants redeemed spends a whole chapter warning a young man, and is ignored.
- **Notes:** Epic tier (Vana Parva). Indra series crossover and a 'student' story for the Upanishad audience. The sexual-assault element (Yavakri and Raibhya's daughter-in-law) must be handled as the text does, briefly, or the cut ends at the dam.


## S5 · Students, teachers and kings

Indra & Virochana (686k) was a student story. The Upanishads are full of them, and in most the teacher is a king or a fire, not a Brahmin.

### 58. In a famine he ate a stranger's leftover beans and refused the water. Then he crashed a king's sacrifice.

- **Tier:** A · make next · **tags:** hunger, ethics, priest
- **Source:** `chandogya_upanishad` 1.10.1–1.11.9 (20 entries)
- **Hook:** Hail had destroyed the Kuru crops. Ushasti and his child-wife were starving in an elephant-driver's village. The driver was eating beans.
- **Hook (Hindi draft):** ओलों ने कुरु देश की फ़सल खत्म कर दी थी। उषस्ति और उसकी बाल-पत्नी एक महावत के गांव में भूखे थे। महावत बीन्स खा रहा था।
- **Arc:** Ushasti begs; the driver says 'only these, which I have begun eating'; 'give me them'; he eats the leftovers but refuses the leftover water: 'eating these I could not have lived; water I can get anywhere.' He keeps some beans for his wife; she has already begged her own, saves his. Next morning he hears a king's sacrifice is on, walks in, and tells the three chief priests that if they chant without knowing the deity of their chant, their heads will fall off; the king makes him chief priest; he teaches the three deities (breath, sun, food).
- **Kicker:** The Upanishad that teaches the secret of the chant opens with a man explaining why eating a stranger's leftovers is not a sin and drinking his water is. Hunger has rules, and the rules have reasons.
- **Notes:** Complete in English (Ch 1.10-1.11). F1: a protagonist with a want and a turn. F9: 'why refuse water but eat the beans?' is the text's own point; make it the mid-story question. The three 'heads will fall off' threats echo Gargi (see gargi-two-arrows).

### 59. The teacher left him behind. So the sacred fires taught him themselves.

- **Tier:** B · strong, needs the right cut · **tags:** student, teacher, fire
- **Source:** `chandogya_upanishad` 4.10.1–4.15.5 (19 entries)
- **Hook:** Upakosala tended his teacher's fires for twelve years. Every other student was sent home with the knowledge. He was not.
- **Arc:** Satyakama (himself the boy who did not know his father) lets his other pupils go but withholds from Upakosala; the teacher's wife pleads; Satyakama goes away without teaching; the boy stops eating; the three fires take pity and teach him 'breath is Brahman'; each fire adds its lesson; when Satyakama returns he sees the boy's face shining 'like one who knows Brahman': 'who taught you?' 'The fires.' 'They told you the worlds; I will tell you the way.'
- **Kicker:** The published Satyakama was taught by a bull, a fire, a swan and a bird. His own student had to be taught by the fires because Satyakama, of all people, held back. The Upanishads do not pretend good students make good teachers.
- **Notes:** Direct sequel to the queued satyakama short (Ch 4.4-4.9); make them a pair. The teacher's-wife line is the turn.

### 60. He had learnt everything from his father. A king asked him five questions. He knew none.

- **Tier:** A · make next · **tags:** student, king, humiliation, father
- **Source:** `chandogya_upanishad` 5.3.1–5.10.10 (29 entries)
- **Hook:** Shvetaketu came to the Panchala court sure of himself. The king asked: do you know where creatures go after death? How they come back? Where the two roads part? Why the other world never fills up? How water becomes a man? Five times: no.
- **Hook (Hindi draft):** श्वेतकेतु पांचाल दरबार में पहुंचा, अपने ज्ञान पर पक्का। राजा ने पूछा: मरकर प्राणी कहां जाते हैं? लौटते कैसे हैं? दो रास्ते कहां बंटते हैं? परलोक भरता क्यों नहीं? पानी इंसान कैसे बनता है? पांच बार: पता नहीं।
- **Arc:** The boy goes home angry: 'you said you taught me everything'; the father admits he does not know either and goes to the king as a pupil; the king offers wealth; Uddalaka asks for the knowledge; the king says 'this knowledge has never before gone to a Brahmin; among all peoples it belonged to the kshatriya' and teaches the five fires and the two paths.
- **Kicker:** The most famous father-son teaching pair in the Upanishads got their best lesson by being humiliated by a king who then told them Brahmins had never owned it. The text wrote that down about itself.
- **Notes:** Also BU 6.2 (same story). 29 entries; script the five questions as a drumbeat (guide §2 refrain). F11 flavour: 'the kshatriya's knowledge' line will drive comments; keep it as the text's claim.

### 61. Twelve years of Veda made him arrogant. His father fixed it with a fruit and a glass of salt water.

- **Tier:** A · make next · **tags:** father, son, philosophy
- **Source:** `chandogya_upanishad` 6.1.1–6.1.7 (7 entries); `chandogya_upanishad` 6.12.1–6.13.3 (6 entries); `chandogya_upanishad` 6.16.1–6.16.3 (3 entries)
- **Hook:** Shvetaketu came home at twenty-four, 'conceited, thinking himself learned'. His father asked: did you ask for the teaching by which the unheard becomes heard?
- **Hook (Hindi draft):** श्वेतकेतु चौबीस साल का होकर लौटा, घमंडी, खुद को विद्वान समझता। पिता ने पूछा: वो शिक्षा मांगी, जिससे अनसुना सुना हो जाता है?
- **Arc:** Uddalaka: 'bring a banyan fruit; break it; what do you see? seeds; break one; what do you see? nothing. From that nothing this great tree. That is the self. You are that.' 'Put this salt in water; bring it tomorrow; find the salt. Taste the top, the middle, the bottom.' 'It is salt everywhere.' 'So the being you cannot see is in all of this. You are that.' The last image: a man blindfolded, led from his home and left in the forest, asking his way village by village.
- **Kicker:** 'Tat tvam asi' is repeated nine times in the text, every time after an object: a seed, salt, a river, a blindfolded man. The Upanishad did not want it believed. It wanted it tasted.
- **Notes:** Three short ranges instead of the whole 69-entry chapter. The published Indra-Virochana used the same father-pupil 'return with doubt' rhythm; this is the companion with concrete demonstrations (guide §4: concrete images before the summing line).

### 62. Three sages met a king on the road. He out-argued them. One of them ran after his chariot.

- **Tier:** B · strong, needs the right cut · **tags:** king, sage, humility
- **Source:** `satapatha_brahmana` 11.6.2.1–11.6.2.10 (10 entries)
- **Hook:** Janaka asked three travelling Brahmins how each performed the fire offering. Each answered. Each was wrong, the king explained, and drove on.
- **Arc:** Shvetaketu, Somashushma and Yajnavalkya each describe their Agnihotra; Janaka shows how each falls short; 'this fellow of a Rajanya has out-talked us; let us challenge him'; Yajnavalkya: 'we are Brahmins; he is a kshatriya; if we lose we will be the laughing-stock'; he runs after Janaka's chariot alone and asks to learn; Janaka teaches where the two libations go (air, sky, earth, man, woman) and grants him a boon; Yajnavalkya, who had refused to be taught by a king, becomes his man. (BU 4.3 continues: 'from then Janaka was a Brahmin', jokes Yajnavalkya.)
- **Kicker:** The sage who later took Janaka's thousand cows without a debate first lost to him on a road, and ran behind his chariot to say so.
- **Notes:** Companion to gargi-two-arrows (same two men, earlier). JB 1.22-1.26 has a parallel (five Brahmins plot to beat Janaka); SB 11.6.2 is the clean version.

### 63. The proud scholar offered to teach the king. The king paid a thousand cows and then taught him.

- **Tier:** B · strong, needs the right cut · **tags:** king, scholar, sleep
- **Source:** `kausitaki_upanishad` 4.1–4.20 (20 entries)
- **Hook:** Gargya Balaki, who had travelled every kingdom, came to Ajatashatru of Kashi: 'Shall I tell you Brahman?' The king: 'A thousand cows for that speech, for people run to Janaka and leave us.'
- **Arc:** Balaki offers sixteen definitions (the person in the sun, the moon, lightning, the mirror, the shadow, the echo, the dream); the king rejects each 'do not make me talk about him'; Balaki falls silent; 'so much only?' The king takes him by the hand to a sleeping man, calls him by names; he does not wake; strikes him with a stick; he wakes. 'Where was he? Where did he come back from?' And teaches the self in sleep and the veins of the heart.
- **Kicker:** The king's lesson was not a speech. It was a man asleep and a stick. The Upanishad says the Brahmin came as a teacher and 'with fuel in hand', as a pupil, went home.
- **Notes:** Twenty short entries; BU 2.1 parallel. The sixteen definitions must become a quick montage (three or four), not a list (F1 leak).

### 64. A king asked the priest's son one question. The priest's son went home. The priest came back as a student.

- **Tier:** B · strong, needs the right cut · **tags:** king, moon, death, teacher
- **Source:** `kausitaki_upanishad` 1.1–1.6 (6 entries)
- **Hook:** Citra Gangyayani asked young Shvetaketu, come to be his priest: is there a closed door in the world where you will put me, or a road on? 'I don't know; let me ask my teacher.'
- **Arc:** The father, Aruni, admits he does not know either; both go to the king with fuel in hand; the king, pleased: 'you are worthy'. He teaches: all who leave this world go to the moon; the moon asks each 'who are you?'; those who cannot answer are rained back into life; the one who answers 'I am you' passes the moon, to the river Vijara, the tree Ilya, the city Salajja, the throne Vicakshana, where Brahman asks 'who are you?' again.
- **Kicker:** In this Upanishad death is an interview conducted by the moon, and the only passing answer is a sentence. The teacher of the greatest Upanishadic father was a king.
- **Notes:** Kaushitaki 1 (six entries, English). Visual-rich afterlife itinerary (the river, the tree, the couch). F9: 'why the moon?' is unanswered in the text; say so.

### 65. The thunder said one syllable. Gods, men and demons each heard a different word.

- **Tier:** B · strong, needs the right cut · **tags:** micro, gods, wordplay
- **Source:** `brhadaranyaka_upanishad` 5.2.1–5.2.3 (3 entries)
- **Hook:** Three classes of Prajapati's children finished their studies and asked their father for a last teaching. He said: Da.
- **Arc:** The gods: 'you said damyata, control yourselves; yes.' Men: 'you said datta, give; yes.' The demons: 'you said dayadhvam, be compassionate; yes.' 'This the divine voice, the thunder, repeats: da, da, da.'
- **Kicker:** One syllable, three listeners, three commands, and each heard the one it needed. The Upanishad's shortest lesson is the one the thunder still gives.
- **Notes:** Micro (45-60 s). T. S. Eliot ended The Waste Land with it; a pinned-comment fact, not a line in the short.

### 66. Five times he came back with an answer. Five times his father said: go and think again.

- **Tier:** B · strong, needs the right cut · **tags:** father, son, philosophy, refrain
- **Source:** `taittiriya_upanishad` 3.1.1–3.6.1 (6 entries)
- **Hook:** Bhrigu asked his father Varuna: teach me Brahman. Varuna named the hints (food, breath, eye, ear, mind) and sent him away to find it himself.
- **Arc:** Bhrigu does tapas, returns: 'food is Brahman, from food all are born'; 'go, think again'; 'breath'; 'again'; 'mind'; 'again'; 'knowledge'; 'again'; 'bliss', and there the text stops asking him to return. Then the practical rules: do not blame food; do not reject food; heap food; welcome the guest.
- **Kicker:** The same Bhrigu, in another text, is sent by his father to see hell (the queued short). Here the father sends him to think, five times, and never once tells him the answer. The Taittiriya says that is the teaching.
- **Notes:** Complete in English (TU 3). Same refrain rhythm that worked in Indra-Virochana (return with doubt). Companion to the queued bhrigu-other-world (JB/SB) as a two-part 'Varuna's son'.

### 67. The gods could not burn, lift or recognise a blade of grass. A woman told them why.

- **Tier:** A · make next · **tags:** gods, humility, woman, micro
- **Source:** `kena_upanishad` 3.1–4.9 (21 entries)
- **Hook:** The gods had won. 'Ours is the victory.' Something appeared before them they did not know. They sent Agni to find out what it was.
- **Hook (Hindi draft):** देवता जीत गए थे। 'हमारी जीत है।' तभी सामने कुछ प्रकट हुआ, जिसे वे पहचान नहीं पाए। उन्होंने अग्नि को भेजा: पता करो, ये क्या है।
- **Arc:** 'Who are you?' 'I am Agni, I can burn anything.' It lays a blade of grass before him: 'burn this.' He cannot. Vayu: 'I can carry anything away.' He cannot move it. Indra goes; it vanishes; in that place he sees a woman, Uma, daughter of the mountain, and asks her; she says: 'it was Brahman; by its victory you were victorious.' So Indra 'touched it nearest', and Agni and Vayu after him.
- **Kicker:** The three greatest gods were defeated by a blade of grass, and the only one who knew what had happened was the woman standing where it had been. The Kena Upanishad puts her name before Indra's.
- **Notes:** Short (Kena 3-4, 21 entries), complete, vivid. Devotional plus (Uma). Indra series side-note: Indra is 'first among gods' because he was the one who went to ask.

### 68. He knew every science there was. He came to say he was still sad.

- **Tier:** C · micro, risky or thin · **tags:** student, philosophy
- **Source:** `chandogya_upanishad` 7.1.1–7.1.5 (5 entries); `chandogya_upanishad` 7.26.1–7.26.2 (2 entries)
- **Hook:** Narada listed the Vedas, history, grammar, mathematics, logic, astrology, snake-charming, the fine arts: 'all this I know, sir; I know the words. I am a knower of words only, not a knower of the Self. I have heard that the knower of the Self crosses sorrow. I am in sorrow.'
- **Arc:** Sanatkumara leads him up a ladder: name, speech, mind, will, memory, hope, breath... each 'greater' than the last, to the Infinite, 'where one sees nothing else'; and the last line, 'the pure in food, the pure in nature; Narada's darkness destroyed'.
- **Kicker:** The first thing the Upanishad asks of its most learned student is a list of what his learning has failed to fix. Then it does not add a subject. It subtracts.
- **Notes:** Doctrine-heavy; the 'I am sad' confession and the syllabus list are the only dramatic beats. Better as a 60-s hook-and-kicker piece than a full arc; or as a pinned-comment reply to 'how to start reading the Vedas'.

### 69. Six scholars went to a king for knowledge. He began by listing what his kingdom did not have.

- **Tier:** C · micro, risky or thin · **tags:** king, scholar
- **Source:** `chandogya_upanishad` 5.11.1–5.18.2 (21 entries)
- **Hook:** 'In my kingdom there is no thief, no miser, no drunkard, no man without a sacred fire, no ignorant man, no adulterer, so how could there be an adulteress?' Then Ashvapati taught the six what each of them had been worshipping as the whole.
- **Arc:** Six great householders cannot agree what the universal Self is; they go to Uddalaka, who sends them to King Ashvapati; the king boasts of his kingdom, then shows each man that his 'self' (sky, sun, wind, space, water, earth) is only the head, eye, breath, trunk, bladder or feet of one being.
- **Kicker:** A king's boast about law and order is the preface to the Upanishad's lesson that everyone's god is a body part.
- **Notes:** Thin arc (F1 leak risk: six answers in a row). Keep only if the producer wants a 'king teaches Brahmins' mini-series with shvetaketu-five-questions and balaki-and-ajatashatru.

### 70. A king gave away his kingdom, stood in the sun for a thousand days with his arms raised, and asked what a body is for.

- **Tier:** C · micro, risky or thin · **tags:** king, renunciation
- **Source:** `maitri_upanishad` 1.2–1.4 (3 entries)
- **Hook:** 'What is the use of pleasure in this body, a mass of bones, skin, sinews, marrow, flesh, seed, blood, mucus, tears, phlegm, ordure, bile and slime?'
- **Arc:** Brihadratha installs his son, goes to the forest, stands facing the sun with arms up; Shakayanya appears; the king's speech lists the body's parts and the names of dead emperors (Sudyumna, Bhuridyumna, Marutta, Bharata...) who had to leave it all; the sage agrees to teach the Self.
- **Kicker:** The Maitri Upanishad's catalogue of vanished kings reads like a roll-call of the channel's own stories: Marutta, Bharata, Sudyumna. The king asking the question had read them too.
- **Notes:** Mood piece with a strong monologue, weak arc (constitution rule 6). Use the body-list as a cold open for another short, or skip.

### 71. The son called his father 'grey-haired' to his face for serving three rival kings.

- **Tier:** C · micro, risky or thin · **tags:** father, son, micro
- **Source:** `jaiminiya_brahmana` 2.327–2.327 (1 entries)
- **Hook:** Jabala Aruni became chaplain to three competing kings at once, Kashi, Kosala and the Ikshvaku, and grew rich. His son Shvetaketu said: grey-haired one, you match others in fame, never yourself.
- **Arc:** The father: 'do not speak so to me; the rite was known to me; you, like a wretched pseudo-Brahmin, tried to find it out; it was as they taught me, and even more.' Then the text turns to the gods outwitting Death.
- **Kicker:** Even in the Brahmanas the famous son of the famous father was a brat. The same Shvetaketu is humiliated by a king in the Chandogya, which may be why.
- **Notes:** Micro only; one entry. Feeds the Shvetaketu thread (salt, five questions, Ashtavakra's uncle).

### 72. Six seekers came with questions. The teacher made them wait a year before asking.

- **Tier:** C · micro, risky or thin · **tags:** student, micro
- **Source:** `prasna_upanishad` 1.1–1.4 (4 entries)
- **Hook:** 'Live another year in austerity and faith; then ask what you will, and if I know, I will hide nothing.'
- **Arc:** Six named students (Sukesha, Satyakama, Gargya, Kaushalya, Bhargava, Kabandhi) wait a year with Pippalada; then the first question: where do creatures come from? And the answer: the Creator made a pair, breath and matter, the sun and the moon.
- **Kicker:** The Prashna Upanishad's first teaching is the year of silence before the first question. The questions are the second teaching.
- **Notes:** Micro; no conflict. Keep only as an interstitial or a pinned comment on 'how to start reading the Vedas'.


## S6 · Gods behaving badly

Brahmana comedies and horrors: gods robbing a goddess, sending a dwarf, creating illusions, building a god to punish their father.

### 73. The demons were dividing the earth. The gods sent a dwarf to ask for 'as much as he can lie on'.

- **Tier:** B · strong, needs the right cut · **tags:** gods, trick, vishnu
- **Source:** `satapatha_brahmana` 1.2.5.1–1.2.5.9 (9 entries); `yajurveda_black` 2.1.3–2.1.3 (1 entries)
- **Hook:** The Asuras had won the earth and were measuring it out with ox-hides, west to east. The gods came to beg a share.
- **Arc:** 'As much as this Vishnu lies on.' 'Now Vishnu was a dwarf.' The Asuras, not offended, give it; the gods lay him down, enclose him on three sides with the metres and fire on the fourth, and by that 'sacrifice' win the whole earth. Then Vishnu, tired, hides in the roots of the plants; the gods dig for him. The Taittiriya adds that Vishnu 'saw' the dwarf and offered it to its own deity.
- **Kicker:** In the Shatapatha the dwarf is the gods' con, not an avatar: the earth was won by sacrifice, not by three steps. The three steps come later, from the same seed.
- **Notes:** F6 warning: do not open with 'you think Vamana was Vishnu's avatar, but...'. Open on the Asuras measuring with hides. Devotional sensitivity moderate; the text is the Veda's own Vamana.

### 74. The demons lost because they fed only themselves.

- **Tier:** B · strong, needs the right cut · **tags:** gods, micro, ethics
- **Source:** `satapatha_brahmana` 5.1.1.1–5.1.1.2 (2 entries)
- **Hook:** Gods and demons, both children of Prajapati, strove. The demons, in arrogance, said: 'to whom should we offer?' and put the offerings into their own mouths.
- **Arc:** The gods went on offering to one another; Prajapati gave himself up to them; so they became the sacrifice and won. 'Wherefore let no one be arrogant, for verily arrogance is the cause of ruin.'
- **Kicker:** The Veda's shortest explanation of why the demons lost: they ate what they should have given. Two sentences, one rule.
- **Notes:** Micro (30-45 s), perfect as a series bumper or a reel with one image (two tables). Also at SB 11.1.8.1.

### 75. The newborn god cried until his father gave him a name. Then he wanted another. Eight times.

- **Tier:** A · make next · **tags:** shiva, father, names, micro
- **Source:** `satapatha_brahmana` 6.1.3.7–6.1.3.18 (12 entries)
- **Hook:** Prajapati's son was born crying. 'My boy, why do you cry?' 'I have not been given a name. Give me a name.'
- **Hook (Hindi draft):** प्रजापति का बेटा रोता हुआ पैदा हुआ। 'बेटा, रोते क्यों हो?' 'मुझे नाम नहीं मिला। मुझे नाम दो।'
- **Arc:** 'You are Rudra.' The boy: 'I am greater than that; give me another.' 'Sharva.' 'Pashupati.' 'Ugra.' 'Ashani.' 'Bhava.' 'Mahan Deva.' 'Ishana.' Each name makes a part of the world his: fire, water, plants, wind, lightning, rain, moon, sun. 'These are the eight forms of Agni; Kumara, the boy, is the ninth.' (The Kaushitaki version: 'without a name I cannot eat food here.')
- **Kicker:** Shiva's first word was a complaint, and his first eight names were extracted from a father one at a time. The Veda's fiercest god began as a baby who would not stop until he had the whole world.
- **Notes:** Devotional plus; micro-to-short (75-90 s). Note that the text calls the boy Agni/Kumara; the names are the Rudra names. KB 6.1-6.3 has the fuller 'cannot eat without a name' dialogue if the producer wants it.

### 76. The gods created two illusions and made them bet.

- **Tier:** B · strong, needs the right cut · **tags:** gods, bet, vedic-root
- **Source:** `satapatha_brahmana` 3.6.2.2–3.6.2.9 (8 entries)
- **Hook:** Soma was in heaven; the gods were here. So they created Suparni and Kadru, who were Speech and Earth, and set them quarrelling.
- **Arc:** 'Who sees farther?' Suparni: 'a white horse at a post across the ocean.' Kadru: 'I see its tail waving.' 'Fly and check.' Suparni flies; Kadru was right; 'I have won your own self; fetch me Soma from heaven.' Suparni sends her children (the metres) for Soma, which is enclosed in two sharp golden cups closing every blink.
- **Kicker:** The Mahabharata turned this into Kadru and Vinata, a thousand snakes and Garuda. In the Veda the two sisters were a trick the gods played on themselves to get Soma down to earth.
- **Notes:** Vedic root of kadru-vinata-bet (epic tier); make the epic one first and this as the 'where it came from' follow-up, or fold into one. Short and complete.

### 77. The gods built a god to punish their father. He became the hunter in the sky.

- **Tier:** B · strong, needs the right cut · **tags:** gods, sky, rudra, sensitive
- **Source:** `aitareya_brahmana` 13.9–13.9 (1 entries); `satapatha_brahmana` 1.7.4.1–1.7.4.4 (4 entries)
- **Hook:** Prajapati desired his own daughter, the Dawn. He became a stag; she a doe. The gods said: this is a sin; who among us can punish him? And they found no one.
- **Arc:** They pour their most terrible forms together and make a god (Bhutavat, Rudra); he pierces Prajapati with an arrow; Prajapati becomes the deer in the sky (Mriga, the Orion stars), the arrow is the belt, the archer the star Mrigavyadha; the seed falls and becomes the lake Sharyanavat, the Adityas, the Angirases. The Shatapatha quotes the Rigveda verse about it.
- **Kicker:** Look up in winter: the Veda says the three stars of Orion's belt are an arrow still in the body of the creator, fired by a god made for one job. Punishment, in the Veda, is written on the sky.
- **Notes:** High devotional sensitivity (Prajapati-daughter incest as the text states it). Astronomy angle is the safe entry (the channel's audience asked for 'mythological beings'). AB 13.9 is complete; SB 1.7.4.1-4 gives the arrow/Rudra. Producer decision.

### 78. Death stalked the gods from chant to chant. They ran to their father.

- **Tier:** C · micro, risky or thin · **tags:** gods, death, micro
- **Source:** `jaiminiya_brahmana` 2.328–2.329 (2 entries)
- **Hook:** 'They are chanting the Trivrt,' thought Death, and went to wait for them at the next chant. They went around him.
- **Arc:** The gods sing a sequence of stomas; Death moves ahead to each; they take refuge in the Vishvajit, in Prajapati; 'having outwitted Death they went to heaven'. Thus the ten-day rite is 'the outwitting of Death'.
- **Kicker:** The Jaiminiya describes a sacrifice as a chase scene. Death is the one who gets lost.
- **Notes:** Ritual allegory; only as a 30-s bumper or an image for another short.

### 79. Indra and Agni won the race. That is why they get the cake.

- **Tier:** C · micro, risky or thin · **tags:** gods, race, micro
- **Source:** `satapatha_brahmana` 2.4.3.1–2.4.3.5 (5 entries)
- **Hook:** Creatures were starving. The gods found the sap of heaven and earth and could not agree whose it was. So they raced for it.
- **Arc:** Each god claims it ('mine!'); they agree 'whoever beats the others, his it shall be'; Indra and Agni win; hence the twelve-potsherd cake for Indra-Agni at the seasonal offering.
- **Kicker:** The oldest tie-breaker in Indian theology was a footrace.
- **Notes:** Micro; combine with suryas-wedding-donkey-race as 'the gods' races'.


## S7 · Seers and kings of the Rigveda

The historical layer: a datable war, a sick prince who gave up a throne, a hungry sage, a priest on strike, frogs.

### 80. Ten kings against one, at a river. The oldest war in Indian history has a hymn.

- **Tier:** A · make next · **tags:** history, war, river, indra
- **Source:** `rigveda` 07.018.01–07.018.25 (25 entries); `rigveda` 07.033.01–07.033.06 (6 entries); `rigveda` 07.083.01–07.083.08 (8 entries)
- **Hook:** Ten kings crossed the Parushni to crush Sudas. The river was the ally that turned.
- **Hook (Hindi draft):** दस राजा सुदास को कुचलने परुष्णी नदी पार कर आए। नदी ही वो साथी थी, जो पलट गई।
- **Arc:** 7.18: Vasishtha's victory hymn: the Turvashas, Yakshus, Matsyas, Bhrigus, Druhyus, the Purus, Anus 'desiring plunder like unfed fish', 'Indra made the ford easy for Sudas and the waters hard for the enemy'; the Anu king's armour and chariot taken; Bheda's fall; the sixty-six thousand slain, 'as a cow kicks her calf'; the kings' names, the priests Vasishtha in white robes (7.33). 7.83: Indra and Varuna 'heard Sudas in the battle of ten kings'.
- **Kicker:** The channel has told the stories of priests and demons. This one has a date-able king, named enemies, a river that drowned an army, and a poet on the winning side writing his own fee into the last verse.
- **Notes:** History angle (the audience asked for 'how to start reading the Vedas'; this is where historians start). Griffith's 7.18 is readable but dense; the writer should pick six concrete verses (the fish, the ford, the armour, the calf, the fee). 7.33 adds Vasishtha's sons in white. Risk: list of tribes (F1 leak); keep to three names.

### 81. King Sudas's heir killed Vasishtha's hundred sons. The sage wrote a curse, and a confession.

- **Tier:** B · strong, needs the right cut · **tags:** seer, grief, curse, feud
- **Source:** `rigveda` 07.104.01–07.104.25 (25 entries); `brhaddevata` 6.28–6.34 (7 entries, 1 empty); `kausitaki_brahmana` 4.6.1–4.6.1 (1 entries)
- **Hook:** The sage who won Sudas his war lost his hundred sons to Sudas's descendants. The Rigveda keeps the hymn he wrote that night.
- **Arc:** Brhaddevata: Vasishtha, his hundred sons slain by the Saudasas (Sudas's line, under a curse), 'full of pain', saw the demon-killing hymn 7.104 ('Indra and Soma, burn the fiends'), and in it says, as if accused of being a sorcerer himself: 'if I am a demon, if I have harmed a man, may I die today'. The Kaushitaki records the 'Vasishtha sacrifice' he saw to 'overcome the Saudasas' and win offspring again.
- **Kicker:** The Rigveda's most famous curse against demons contains a father swearing he is not one. Grief, in the Veda, had to prove its innocence before it could ask for revenge.
- **Notes:** Seer feud (Vasishtha-Vishvamitra via Shakti, BD 4.112, is truncated in the corpus). BD 6.31-6.32 empty; 6.28, 6.33, 6.34 carry the frame. 7.104 is complete (25 verses). The later Kalmashapada/Saudasa tale is Mahabharata (Adi 176-177), not in the Vedic packet; flag as later.

### 82. 'What was my sin, Varuna? I once rode in your boat.' A sage's confession, in his own voice.

- **Tier:** B · strong, needs the right cut · **tags:** seer, guilt, emotion
- **Source:** `rigveda` 07.086.01–07.086.08 (8 entries); `rigveda` 07.088.01–07.088.07 (7 entries); `rigveda` 07.089.01–07.089.05 (5 entries)
- **Hook:** Vasishtha had been Varuna's friend; they had sailed together on the god's ship and 'the sun rose on us both'. Now he is sick, bound, and asking what he did.
- **Arc:** 7.86: 'I ask the wise what my sin was; they say Varuna is angry with you'; 'it was not my will but wine, dice, anger, a dream'; 'free us from our fathers' sins and our own'. 7.88: the memory of the boat. 7.89: 'let me not go to the house of clay; if I have wronged you it was through weakness; have mercy'.
- **Kicker:** The oldest first-person prayer of a man who does not know what he did wrong. Three thousand years before 'guilt' had a word in psychology, a sage listed the four excuses: wine, dice, anger, a dream.
- **Notes:** Emotion (F10: shares) but no plot; build the arc from the boat (friendship) to the clay house (illness) to the plea. The two published hits are both story-first; test this as the 'inner' short. Companion: the queued gambler's lament (10.34).

### 83. The elder brother had a skin disease, so he gave the throne to Shantanu. Then it stopped raining.

- **Tier:** A · make next · **tags:** brothers, mahabharata-root, drought
- **Source:** `rigveda` 10.098.01–10.098.12 (12 entries); `brhaddevata` 7.156–8.8 (10 entries)
- **Hook:** Shantanu, Bhishma's father, had an elder brother. The Rigveda remembers him: Devapi, who refused the crown and went to the forest. Twelve years without rain followed.
- **Hook (Hindi draft):** शांतनु, यानी भीष्म के पिता, के एक बड़े भाई थे। ऋग्वेद उन्हें याद रखता है: देवापि, जिन्होंने राज ठुकराया और जंगल चले गए। फिर बारह साल बारिश नहीं हुई।
- **Arc:** Brhaddevata: Devapi, afflicted with skin disease, declares himself unfit; Shantanu is anointed; Parjanya withholds rain; the Brahmins say the younger brother was wrongly made king while the elder lived; Shantanu goes to the forest and offers the crown back; Devapi refuses again but agrees to be his priest; he sacrifices with the hymn 10.98 ('Brhaspati, be Mitra, Varuna, Pushan; place brilliant speech in my mouth'), and the rain falls.
- **Kicker:** The Mahabharata mentions Devapi in a line. The Rigveda has his hymn: the sick elder brother asking the gods for rain for the brother he gave the kingdom to. The Kuru story begins in the Veda with a man refusing a throne.
- **Notes:** Mahabharata root (the published Dog short proved this audience likes Vedic roots of the epic). BD 7.155, 7.157, 8.1, 8.4, 8.6, 8.8, 8.9 are truncated/empty in the corpus; 7.156, 8.2, 8.3, 8.5, 8.7 carry the plot; RV 10.98 is complete. Also in Nirukta 2.10 (no English in corpus) and Yaska's story matches.

### 84. The king's chariot killed a Brahmin boy. The king blamed the priest. The priest blamed the king.

- **Tier:** B · strong, needs the right cut · **tags:** justice, king, priest, sparse
- **Source:** `brhaddevata` 5.14–5.20 (7 entries); `rigveda` 05.002.01–05.002.12 (12 entries)
- **Hook:** King Tryaruna was driving; his chaplain Vrisha held the reins. A boy was cut down. Whose fault, the driver's or the one who told him to go fast?
- **Arc:** Each blames the other; the Ikshvakus are asked to judge; they side with the king; Vrisha revives the boy with Atharvan spells and leaves; the fire in the king's house dies with him; the king comes begging; Vrisha returns and finds the 'heat' hidden by a Pishachi, the king's wife's demon, under a cushion; he recovers it with the verse 'whom do you hide, as a boy?' (RV 5.2).
- **Kicker:** The Rigveda's hymn 5.2 begins 'a young mother hides the boy' and no one knew why until the Brhaddevata told the story: a wrongful death, a priest's strike, and a kingdom whose fire went out.
- **Notes:** Justice theme (F10 injustice). BD 5.19, 5.21, 5.22 truncated/empty; 5.14-5.18, 5.20 intact. RV 5.2 is complete but cryptic; the BD frame is the story.

### 85. He wanted the princess. The king said: only a seer may marry her. So he became one.

- **Tier:** B · strong, needs the right cut · **tags:** love, seer, sparse
- **Source:** `brhaddevata` 5.50–5.80 (31 entries, 13 empty); `rigveda` 05.061.01–05.061.19 (19 entries)
- **Hook:** At King Rathaviti's sacrifice, the young priest Shyavashva saw the king's daughter. The king was willing. The queen asked: is he a rishi?
- **Arc:** He is not; the match is refused; Shyavashva wanders, is blessed by Queen Shashiyasi, meets the Maruts on the road and praises them; they make him a seer; he composes the hymns to the Maruts (5.52-5.61) and sends a message to the king through the night (5.61: 'tell Rathaviti...'); the king gives his daughter.
- **Kicker:** The Rigveda's hymns 5.52 to 5.61 exist because a boy was told he was not good enough for a princess. The Maruts, gods of storm, were his tutors in the art of becoming good enough.
- **Notes:** Romance; the only one in the corpus with a clean rom-com shape. BD 5.50-5.80 is 32 entries and several are empty in the corpus (5.81 blank); the writer must work from the intact ones (5.50, 5.55, 5.56, 5.60, 5.65 confirmed). RV 5.61 carries the message to the king.

### 86. A student fell asleep on the road home. He woke up married to ten princesses.

- **Tier:** C · micro, risky or thin · **tags:** seer, luck, sparse
- **Source:** `brhaddevata` 3.142–3.150 (9 entries, 1 empty); `rigveda` 01.125.01–01.126.05 (12 entries)
- **Hook:** Kakshivat, son of a slave-woman and the blind sage Dirghatamas, walked home from his studies, lay down in the forest and slept. King Svanaya found him 'like the son of a god'.
- **Arc:** The king asks his lineage, marries him to his ten daughters, gives a hundred necklets, a hundred bulls, horses, ten chariots; Kakshivat praises him in 1.125-1.126 ('at morn the giver of a hundred came'); his father Dirghatamas blesses the gift.
- **Kicker:** Not every seer in the Rigveda earned his hymns by austerity. One slept well in the right forest. His hymn is a thank-you note.
- **Notes:** Sparse but intact (BD 3.142-3.150, except 3.147). Dirghatamas (blind from birth; thrown in the Ganga in later texts) is only glancingly in the corpus (BD 4.15 'suddenly blind'); not enough for his own short.

### 87. The fish prayed to the gods from the dry land, and the fishermen let them go.

- **Tier:** C · micro, risky or thin · **tags:** animal, micro, sparse
- **Source:** `brhaddevata` 6.88–6.90 (3 entries); `rigveda` 08.067.01–08.067.21 (21 entries)
- **Hook:** Fishermen on the Sarasvati cast a net, caught the fish and threw them on the bank. The fish, frightened, praised the sons of Aditi.
- **Arc:** The Adityas release them, and tell the fishermen: do not fear hunger; you will reach heaven. The hymn 8.67 ('let not Vivasvat's net destroy us before old age') is, the Brhaddevata says, the fishes' hymn.
- **Kicker:** A Rigvedic hymn attributed to fish. The channel's two dog shorts were its biggest. This is the aquatic sequel.
- **Notes:** Micro, charming, thin; 8.67 (the corpus has Wilson's rendering for this hymn) is long for a fish prayer. Pair with agni-quit-fish-told in a 'fish in the Veda' pinned comment.

### 88. A year of silence, then the rains, and the frogs sang like priests. The Rigveda meant it as a compliment.

- **Tier:** B · strong, needs the right cut · **tags:** animal, comedy, season
- **Source:** `rigveda` 07.103.01–07.103.10 (10 entries)
- **Hook:** 'Like Brahmins who have kept their vows, the frogs lay quiet for a year. Then the rains came, and they lifted up their voice.'
- **Arc:** Each frog answers the other 'as a pupil repeats the teacher'; Cow-bellow and Goat-bleat, Green and Spotty, croak in turn 'as Brahmins round the Soma vessel at the all-night rite'; 'they keep the twelve-month order; they never neglect the season'; and in the last verse they grant cattle and long life.
- **Kicker:** The hymn was sung to bring rain, and the only priests in it are frogs. Vasishtha's family kept it in the family book. The channel's audience will decide whether it is satire; the text has been letting people decide for three thousand years.
- **Notes:** No protagonist; the arc is the year (silence, first drop, chorus). Treat like the Vratyas short (an explainer with a twist), expect Vratya-like retention (F1), but the animal comedy may out-share it (F4). Ten verses, complete.

### 89. 'I'm a poet. Dad's a doctor. Mum grinds corn.' The Rigveda's hymn on jobs.

- **Tier:** C · micro, risky or thin · **tags:** micro, society
- **Source:** `rigveda` 09.112.01–09.112.04 (4 entries)
- **Hook:** We all have different plans: the carpenter wants a crack, the doctor a patient, the priest a sponsor. 'A bard am I, my dad's a leech, mammy lays corn upon the stones.'
- **Arc:** Four verses: trades and desires (the smith, the horse that wants an easy cart, the frog that wants water), ending 'flow, Soma, for Indra'.
- **Kicker:** The oldest 'what does your family do' in Indian literature, and the family is mixed: poet, physician, miller. Caste, in this hymn, is three jobs in one house.
- **Notes:** Micro (45 s); argument-short flavour (F11) on occupations and caste. The published 'professions in the Yajurveda' covered the Purushamedha list; this is the personal version.

### 90. A child made a chariot with no wheels and rode it to Yama's tree.

- **Tier:** C · micro, risky or thin · **tags:** death, child, cryptic
- **Source:** `rigveda` 10.135.01–10.135.07 (7 entries)
- **Hook:** 'In the tree with fair leaves where Yama drinks with the gods, the father looks after the men of old.' A child has followed him.
- **Arc:** The child mounts a wheel-less car he made in his mind; the Saman follows it; 'who was the father of the child? who made the car roll?'; the funeral gift is placed; the point of flame appears; 'here is the seat where Yama dwells'.
- **Kicker:** Nachiketa, who went to Death's house, has a nameless forerunner: a child in Rigveda 10.135 who built his own chariot to go there. The Veda did not explain it. The Katha Upanishad did.
- **Notes:** Cryptic hymn; the queued Nachiketa short should mention it in the pinned comment rather than this being its own short.


## S8 · Mahabharata roots in the Vedas

The Dog short (4.4M) connected the epic to the Veda. Here are the other threads: Parikshit, Janamejaya, Bharata, Devapi.

### 91. A possessed woman was asked: where did the Parikshitas go? The Upanishad records the answer.

- **Tier:** A · make next · **tags:** mahabharata-root, possession, oracle
- **Source:** `brhadaranyaka_upanishad` 3.3.1–3.3.2 (2 entries); `brhadaranyaka_upanishad` 3.7.1–3.7.1 (1 entries)
- **Hook:** At Janaka's debate, Bhujyu told Yajnavalkya: we were travelling in Madra, in the house of Patanchala Kapya, whose daughter was possessed by a Gandharva. We asked it who it was, and we asked it: where did the Parikshitas go?
- **Hook (Hindi draft):** जनक की सभा में भुज्यु ने याज्ञवल्क्य से कहा: हम मद्र देश में पतंचल काप्य के घर ठहरे थे। उनकी बेटी पर एक गंधर्व सवार था। हमने उससे पूछा: परीक्षित के वंशज कहां गए?
- **Arc:** The Gandharva (in 3.3) says 'they went where the horse-sacrificers go', and the question is thrown at Yajnavalkya: where is that? He answers with the size of the world, thirty-two days of the sun's chariot, and the winds that carry the sacrificers beyond it. In 3.7 another Gandharva, possessing the same household's wife, asks about the 'thread' that holds the worlds together.
- **Kicker:** The Mahabharata's royal family, the Parikshitas, were already a lost dynasty when the Upanishads were composed. People asked spirits where they had gone. That is how old the Kurus are.
- **Notes:** Mahabharata root (the published Dog short cited Sarama's curse on Janamejaya; this is the same family). The BU translation in the corpus carries Shankara's commentary; take only the narrative sentences. Also SB 11.5.5.13 ('the palace of Janamejaya') and AB 39.7 (Janamejaya's horse sacrifice at Asandivant) can be cited.

### 92. Seven kings were anointed like Indra. When one tried to give away the Earth, the Earth sang back.

- **Tier:** B · strong, needs the right cut · **tags:** mahabharata-root, kings, earth
- **Source:** `aitareya_brahmana` 39.7–39.9 (3 entries)
- **Hook:** With the 'great anointing of Indra', Tura Kavasheya anointed Janamejaya, Vasishtha anointed Sudas, Dirghatamas anointed Bharata. Each went round the earth conquering. Then Vishvakarman Bhauvana tried to give the earth itself to his priest.
- **Arc:** The Aitareya's roll of anointed kings: Janamejaya Parikshita (the horse at Asandivant 'with a yellow garland'), Sharyata, Shatanika, Ambashthya, Yudhamshraushti, Vishvakarman, Sudas, Marutta, Anga, Bharata Daushyanti (133 horses by the Yamuna and the Ganga, 'no man can reach his deeds, as no man can seize the sky with his hands'); and the Earth singing to Vishvakarman: 'No man whatsoever ought to give me; you wished to give me; I shall plunge into the middle of the waters; vain was your compact with Kashyapa.'
- **Kicker:** The land is named after one king on this list. The list's only speaking character is the land, refusing to be a gift.
- **Notes:** Explainer risk (a list of kings); the arc is Vishvakarman's gift and the Earth's refusal, with Janamejaya and Bharata as the frame. The published 'Mahabharata dog' audience and the docs/mahabharata_references note in this repo back the angle.

### 93. 'Which shall I cook for you, curds or barley brew?' the wife asks, in the kingdom of King Parikshit.

- **Tier:** B · strong, needs the right cut · **tags:** mahabharata-root, atharvaveda, micro
- **Source:** `atharvaveda` 20.127.07–20.127.10 (4 entries)
- **Hook:** The Atharvaveda has a jingle about a king: 'under Parikshit the ripe barley springs up, the people thrive, a Kauravya says to his wife...' It is the Mahabharata's Parikshit, or his ancestor, and it is the oldest mention of the Kurus by name.
- **Arc:** Four verses: the king 'excelling mortals like a god'; the husband 'ordering his house' says the king has given rest; the wife asks what to serve, curds, milk-gruel or barley-brew; the barley springs 'up to the cleft'.
- **Kicker:** A kitchen conversation is the oldest surviving portrait of Kuru rule. Not a battle. A wife asking what to cook.
- **Notes:** Micro (45-60 s), a 'Mahabharata root' bumper; cite docs/mahabharata_references_in_vedic_texts.md in this repo for the Devanagari. F6: don't open on 'before the Mahabharata'; open on the wife's question.

### 94. King Soma took a Brahmin's wife. The gods made him give her back.

- **Tier:** C · micro, risky or thin · **tags:** gods, marriage, micro
- **Source:** `rigveda` 10.109.01–10.109.07 (7 entries)
- **Hook:** The Brahmin's wife, the hymn says, was taken; the gods and the Seven Seers sat in austerity until King Soma 'without reluctance made restitution'.
- **Arc:** Seven verses: the gods' decree that the Brahmin's wife must be returned, 'the kings who kept their promise' restoring her, the ones who shared the bribe freed from sin.
- **Kicker:** The Puranic Tara, taken by the moon from Brhaspati, has her seed here, in a hymn that is a verdict: give her back.
- **Notes:** Micro; thin. Only if the producer builds a 'where Puranic stories come from' series.


## S9 · Argument shorts

F11: a thesis gets comments and shares but fewer complete views. These have no protagonist; test them against the stories, not instead of them.

### 95. The Rigveda's creation hymn ends with: he who is highest in heaven knows. Or maybe he does not.

- **Tier:** B · strong, needs the right cut · **tags:** argument, philosophy, famous
- **Source:** `rigveda` 10.129.01–10.129.07 (7 entries)
- **Hook:** 'Then there was neither death nor immortality, nor night nor day. Who knows whence it came? The gods came after.'
- **Arc:** Seven verses: the void, the breath without wind, desire as the first seed, the sages' cord of measurement, and the two closing verses that refuse to answer: 'he who is the overseer in highest heaven, he knows, or perhaps he does not know.'
- **Kicker:** The Veda ends its only creation account with a shrug. Every religion claims certainty about the beginning. The oldest one wrote down its doubt and kept chanting it.
- **Notes:** Argument short (F11: comments, saves). No protagonist; test against the story shorts. Famous; the hook must not be 'you think X'. Open on the line about the gods coming after.

### 96. 'Two sit and whisper together; the king knows it, as the third.' The Vedic god of surveillance.

- **Tier:** B · strong, needs the right cut · **tags:** argument, varuna, famous-line
- **Source:** `atharvaveda` 04.016.01–04.016.09 (9 entries)
- **Hook:** The Atharvaveda to a liar: the man who stands, walks, sneaks, hides, lies down, or rises, Varuna sees. Whatever two people plot, sitting together, King Varuna knows it, as the third.
- **Arc:** The hymn to Varuna's spies: they descend from heaven, thousand-eyed; the one who flees beyond the sky is not free; the oceans are his two cups; the closing curse with Varuna's nooses on the liar.
- **Kicker:** Three thousand years before anyone said 'if you have nothing to hide', the Veda described a god with spies who count your blinks. It was a threat used in oaths. It still works.
- **Notes:** Argument short on truth and surveillance. The famous 'third' verse is 4.16.2 in Griffith's numbering; verify the exact verse in the packet. Pair with the published 'Atharvaveda and Varuna' explainer if any.

### 97. The verse used for Sati tells the widow to get up.

- **Tier:** B · strong, needs the right cut · **tags:** argument, women, famous, sensitive
- **Source:** `rigveda` 10.018.07–10.018.09 (3 entries)
- **Hook:** At a Rigvedic funeral the widow lies down beside the body. Then a voice: 'Rise, come to the world of the living, woman; he is lifeless by whose side you lie.'
- **Arc:** Three verses: the wives with living husbands go forward with ointment; the widow is raised and (in the text) takes the hand of the man who takes her; the bow is taken from the dead man's hand. One syllable's difference in a later reading turned 'agre' (forward) into 'agneh' (of fire).
- **Kicker:** The Veda's funeral told the widow to stand up and live. A later misreading of one word was used to tell her to burn. The channel can show the verse; the audience can decide what one syllable is worth.
- **Notes:** High F11 (argument, comments, shares) and high F6 risk (correction hook). Open on the funeral scene and the voice, not on 'you have been told'. The 'agre/agneh' claim is a scholarly argument not in the packet; present it as such or keep to the verse.

### 98. Viraj was a cow. Gods, men, demons, snakes and the dead each milked her, and got something different.

- **Tier:** C · micro, risky or thin · **tags:** argument, cosmology, animal
- **Source:** `atharvaveda` 08.010.01–08.010.33 (33 entries)
- **Hook:** At her birth all feared her: she will become everything. She rose; she became a cow; and everyone came with a calf and a pail.
- **Arc:** The gods milk her with Savitr as calf and get strength; men with Manu and get agriculture and corn; the fathers get svadha; the Asuras get maya (illusion); the snakes get poison; the Gandharvas fragrance; 'he who knows this becomes a lord of the household'.
- **Kicker:** In the Atharvaveda, poison, magic, fragrance and farming all come from one cow, depending on who did the milking. What you get from the world depends on your calf.
- **Notes:** Allegory; argument-short material. 33 verses, repetitive; select four milkings.

### 99. See sarama-the-other-version (S3).

- **Tier:** C · micro, risky or thin · **tags:** pointer
- **Source:** `brhaddevata` 8.31–8.34 (4 entries, 2 empty)
- **Hook:** Pointer entry: the Sarama sequel doubles as an argument short.
- **Arc:** See S3.
- **Kicker:** See S3.
- **Notes:** Cross-reference only; do not queue separately.


## S10 · Epic tier: Mahabharata, Ramayana, Harivamsa

The corpus holds Ganguli's Mahabharata, Dutt's Ramayana and Harivamsa in English. Outside the channel's Vedic identity, so chosen for Vedic resonance, an animal, a woman, or Indra.

### 100. Fire refused to lie. So a sage cursed it to eat everything.

- **Tier:** A · make next · **tags:** agni, epic, truth, curse
- **Source:** `mahabharata_ganguli` 1.5–1.7 (3 entries)
- **Hook:** A demon asked the sacred fire: is this woman Bhrigu's wife? Fire knew that lying was a sin and that telling was a disaster. It told the truth.
- **Hook (Hindi draft):** एक राक्षस ने अग्नि से पूछा: ये स्त्री भृगु की पत्नी है? अग्नि जानते थे, झूठ पाप है, और सच कहना तबाही। उन्होंने सच कहा।
- **Arc:** The Rakshasa Puloma, once betrothed to her, claims Bhrigu's pregnant wife Puloma; Agni, asked as witness, admits she was promised to the demon first; the demon carries her off as a boar; the child Chyavana falls from the womb and burns the demon to ash; Bhrigu curses Agni: 'you shall eat everything'; Agni withdraws from all rites; the gods are starving; Brahma turns the curse: what fire touches becomes pure.
- **Kicker:** Why does fire eat garbage and the holiest offering alike? Because it told the truth once and was punished for it. The Mahabharata's Agni and the Veda's Agni (who ran away from the job) are the same tired god.
- **Notes:** Epic tier (Pauloma Parva, three sections). Pairs with agni-quit-fish-told (S3) as 'Agni, the god who hated his job'. Chyavana born here is the Chyavana of the published Sukanya short: a series thread.

### 101. He saw his ancestors hanging upside down over a pit, held by a single root a rat was chewing.

- **Tier:** A · make next · **tags:** epic, ancestors, image, marriage
- **Source:** `mahabharata_ganguli` 1.13–1.15 (3 entries); `mahabharata_ganguli` 1.45–1.47 (3 entries)
- **Hook:** The ascetic Jaratkaru had decided never to marry. On the road he saw men hanging head-down in a pit from a single grass root, and a rat gnawing it. They said: we are your ancestors. You are the root.
- **Arc:** He agrees to marry on absurd terms (a wife of his own name, given freely); the snake king Vasuki's sister Jaratkaru is offered; he leaves her the day she wakes him for the evening rite ('you insulted me'); she is already pregnant with Astika, who will stop Janamejaya's snake sacrifice.
- **Kicker:** The whole Mahabharata is told at a sacrifice that one boy stopped, and that boy exists because his father saw a rat chewing a root. The epic's chain of causes begins with pest control.
- **Notes:** Epic tier (Astika Parva). The pit image is one of the best in the corpus for the house style (silhouettes, negative space). Links to the published Dog/Janamejaya short.

### 102. The father asked his sons for their youth. Four refused. The youngest gave it, and became king.

- **Tier:** A · make next · **tags:** epic, father, desire, old-age
- **Source:** `mahabharata_ganguli` 1.83–1.85 (3 entries)
- **Hook:** Cursed with old age at the height of his life, Yayati went to his sons one by one: take my old age, give me your youth, for a thousand years.
- **Arc:** Yadu, Turvasu, Druhyu, Anu refuse (and are cursed with the fates of their lines); Puru accepts; Yayati enjoys a thousand years, then returns it with the sentence 'desire is not quenched by enjoyment; it grows, as fire with ghee'; Puru, the youngest, is made king; the elders' descendants become outsiders.
- **Kicker:** The Kuru line descends from the one son who agreed to grow old for his father. The epic says the four who said no founded the peoples outside the Vedic fold. That is a strange thing for an epic to admit about ancestry.
- **Notes:** Epic tier (Sambhava Parva). The 'desire grows with enjoyment' verse is quotable and saved (F10). Devayani-Sharmishtha (S2) is the prequel.

### 103. The demons killed him three times. The third time they fed him to his own teacher.

- **Tier:** B · strong, needs the right cut · **tags:** epic, student, teacher, love
- **Source:** `mahabharata_ganguli` 1.76–1.78 (3 entries)
- **Hook:** Kacha came to learn the art of raising the dead from Shukra, the demons' priest. The demons killed him, ground him, burned him, and mixed the ashes into Shukra's wine.
- **Arc:** Devayani loves him and begs her father each time; Shukra revives him; the third time Kacha is inside Shukra; to come out he must learn the art and revive his teacher from within; he does; Devayani asks him to marry her; he refuses ('you are my sister now'); she curses him; he curses her back.
- **Kicker:** The only way to learn the secret was to be inside the man who knew it. The Mahabharata invented the Trojan student.
- **Notes:** Epic tier. Student/teacher thread for the Upanishad audience; a refusal of love as the turn (like the queued Urvashi). Leads into devayani-sharmishtha.

### 104. A student went to fetch earrings for his teacher's wife. A snake stole them on the road.

- **Tier:** B · strong, needs the right cut · **tags:** epic, student, quest, indra
- **Source:** `mahabharata_ganguli` 1.3–1.3 (1 entries)
- **Hook:** Utanka's teacher's wife wanted Queen Madayanti's earrings in four days. He got them. Takshaka the snake took them from his hands while he bathed.
- **Arc:** He follows the snake into the underworld, sees two women weaving black and white threads on a loom turned by six boys, a man on a horse (Indra and his horse); blows into the horse and fills the snake world with smoke; gets the earrings; returns on the day; then goes to Janamejaya and demands the snake sacrifice.
- **Kicker:** The snake sacrifice at which the Mahabharata is recited was started by a student with a grudge about earrings. The epic begins with petty revenge.
- **Notes:** Epic tier (Paushya Parva; one huge Ganguli section, 35k characters: the packet will be big, the producer may want to split by hand). Indra appears as the horseman, series link.

### 105. The boy raised by a deer-horned sage had never seen a woman. A kingdom needed rain.

- **Tier:** B · strong, needs the right cut · **tags:** epic, innocence, rain
- **Source:** `mahabharata_ganguli` 3.110–3.113 (4 entries); `ramayana_dutt` 1.9–1.10 (2 entries)
- **Hook:** Rishyashringa, born of a doe, had seen only his father. King Lomapada's land had no rain, and the remedy was to bring the boy to the city.
- **Arc:** Courtesans arrive in a floating hermitage; the boy describes 'the student' he met to his father (the 'student' had no beard, round fruits on his chest, and sang sweetly); he is lured onto the boat; the rain comes; he marries Shanta.
- **Kicker:** The boy's innocent description of a woman, delivered to a furious father, is the funniest page in the Vana Parva. The rain, the text says, came because he left.
- **Notes:** Epic tier; famous. Comedy of innocence; keep the father's reaction. The Ramayana (Dutt 1.9-1.10) gives the Dasharatha link (Shanta is Rama's sister).

### 106. The demon brother cooked as a goat, was eaten, and called back from inside the guest. Then he met Agastya.

- **Tier:** B · strong, needs the right cut · **tags:** epic, demon, trick, agastya
- **Source:** `mahabharata_ganguli` 3.96–3.99 (4 entries)
- **Hook:** Ilvala would turn his brother Vatapi into a goat, feed him to a Brahmin, then call 'Vatapi, come out!' and the brother would tear through the guest's belly. Then Agastya came to dinner.
- **Arc:** Agastya, seeking wealth for Lopamudra, visits kings, finds them with nothing to spare, and goes to Ilvala; eats the goat; Ilvala calls; Agastya says 'Vatapi is digested'; Ilvala pays.
- **Kicker:** The sage who in the Rigveda negotiated with his wife for desire (the published Lopamudra) in the epic negotiates with a demon for her dowry, by digesting his brother. Same marriage, new chapter.
- **Notes:** Epic tier (Vana Parva, Tirtha-yatra). Sequel to the published Lopamudra short; the audience knows the couple. Confirm 3.96-3.99 span before scripting.

### 107. A king wanted heaven in his body. The priests refused. So Vishvamitra built him a new one.

- **Tier:** B · strong, needs the right cut · **tags:** epic, defiance, indra, sky
- **Source:** `ramayana_dutt` 1.56–1.60 (5 entries)
- **Hook:** Trishanku asked Vasishtha to send him to heaven alive. No. Vasishtha's sons cursed him into an outcaste. He went to Vishvamitra.
- **Arc:** Vishvamitra performs the sacrifice; the gods do not come; by his own power he raises Trishanku bodily; Indra throws him down head-first; Vishvamitra stops him in mid-air and begins creating a second heaven with new stars and new gods; Indra negotiates: Trishanku stays, hanging, among new constellations.
- **Kicker:** There is a man hanging upside down in the southern sky because two sages hated each other. The Ramayana's gods did not stop it; they made a treaty with it.
- **Notes:** Epic tier (Bala Kanda, Dutt). Indra series crossover (Indra the negotiator). Astronomy angle. The Vasishtha-Vishvamitra feud is otherwise sparse in the corpus (BD 4.112 truncated), so this is where to tell it.

### 108. Indra stole the horse. Sixty thousand princes dug the earth to find it and were burned by one glance.

- **Tier:** B · strong, needs the right cut · **tags:** epic, indra, ganga
- **Source:** `ramayana_dutt` 1.38–1.44 (7 entries)
- **Hook:** King Sagara's horse-sacrifice needed a horse. Indra, as a Rakshasa, stole it. Sagara's sixty thousand sons dug down to the underworld to find it.
- **Arc:** They dig the earth into the ocean (the 'sagara'), find the horse beside the meditating Kapila, accuse him; his glance burns them to ash; the grandson Amshuman finds the ash; Garuda tells him only the Ganga can release them; three generations later Bhagiratha brings the river down.
- **Kicker:** The Ganga came to earth because Indra stole a horse. The Ramayana tells the greatest river story in India as an aftermath of petty theft by the king of gods.
- **Notes:** Epic tier (Bala Kanda, seven sections; cut at the ash). Indra series crossover; the descent itself is another short.

### 109. A Brahmin's son died. The reason, said the sages, was a Shudra doing penance. Rama went to find him.

- **Tier:** C · micro, risky or thin · **tags:** epic, caste, controversial
- **Source:** `ramayana_dutt` 7.87–7.88 (2 entries)
- **Hook:** A Brahmin laid his dead son at the palace gate: in your kingdom a child has died before his father. Narada said: somewhere a Shudra is practising austerities. Rama took his chariot.
- **Arc:** Rama finds Shambuka hanging head-down in penance, asks his caste and purpose (heaven, in his body), draws his sword and cuts off his head; the gods applaud; the boy revives.
- **Kicker:** The text tells it as Rama doing his duty. The audience will not agree with each other. The channel's job is to show the text exactly, and let the comments be the argument.
- **Notes:** Highest controversy in the bank (F11 extreme). Only with the producer's explicit decision; if made, verbatim and without editorial. Dutt's Uttara Kanda numbering (7.87-7.88) is confirmed for 7.88; check 7.87.

### 110. A golden swan carried the king's love letter to the princess. Then four gods asked him to carry theirs.

- **Tier:** C · micro, risky or thin · **tags:** epic, love, animal, long
- **Source:** `mahabharata_ganguli` 3.53–3.57 (5 entries)
- **Hook:** Nala caught a swan in his garden. It said: let me go and I will tell Damayanti about you. At her svayamvara, four gods took Nala's shape and sat beside him.
- **Arc:** The swan courts for him; the gods (Indra, Agni, Varuna, Yama) make Nala their messenger to Damayanti against his own suit; he goes, invisible, and pleads for them; she chooses him anyway, and at the svayamvara picks the one whose garland fades, whose feet touch the ground, who blinks: the human.
- **Kicker:** Damayanti recognised the human among four gods because he sweated, blinked and cast a shadow. The epic's definition of a man is the things gods cannot fake.
- **Notes:** Epic tier; only the opening of the Nala story (sections 53-57) fits a short; the dice and exile are a long-form candidate (F5: long-form for subscribers). Indra appears as a suitor (series link).

### 111. Four brothers died drinking from a lake because they did not answer the voice. The fifth answered.

- **Tier:** B · strong, needs the right cut · **tags:** epic, riddles, famous
- **Source:** `mahabharata_ganguli` 3.311–3.313 (3 entries)
- **Hook:** 'Do not drink before you answer my questions.' Nakula drank and fell. Sahadeva, Arjuna, Bhima. Yudhishthira came last and stopped.
- **Arc:** The crane/Yaksha's questions (what is heavier than earth, faster than wind; what is the greatest wonder: that men see others die and live as if they will not); the boon: revive one brother; Yudhishthira chooses Nakula, Madri's son, so both mothers have a living son; the Yaksha is Dharma, his father.
- **Kicker:** He could have brought back Arjuna or Bhima. He chose the brother whose mother was dead. The questions were the test; the choice was the answer.
- **Notes:** Epic tier; very famous; the dog short proved the audience will watch a famous Yudhishthira scene told well. Confirm the Ganguli span (Araneya Parva 3.311-3.313).


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
