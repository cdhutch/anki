# Ch.10-12 + Ch.1-7 Vocabulary Expansion — Progress Index

Tracks the 2026-08-28 autonomous pass sourcing `yabluko-l2-vocabulary.pdf` chapters other
than 8/9 (already done). Branch: `feature/yabluko-l2-vocab-expansion`. Order per Craig:
ch.10, then ch.1–7, then ch.11–12.

**Purpose:** a lightweight, committed, human-readable index of exactly which NoteIDs this
pass has generated, so a later session (me or Craig) can pick up mid-chapter without
re-deriving state from git log or re-running `build_lexeme_index.py`. This is a progress
tracker, not the dedup source of truth — dedup still re-scans the live corpus per
`CLAUDE-ch09-vocab-workflow.md`.

## PDF page map (24 pages total, confirmed against the known ch.8/ch.9 boundary)

| Chapter | PDF pages | Subsections | Status |
|---|---|---|---|
| 1 Будні та свята | 1–2 | 1.1–1.7 | in progress (1.1, 1.2 done) |
| 2 Вечірка | 2–4 | 2.1–2.7 | in progress (2.1–2.5 done) |
| 3 Чого нам бракує до повного щастя | 4–7 | 3.1–3.7 | not started |
| 4 Люди та історії | 7–9 | 4.1–4.7 | not started |
| 5 Скажи де, скажи коли | 9–11 | 5.1–5.6 | not started |
| 6 Що сталося? | 11–13 | 6.1–6.7 | not started |
| 7 Наше майбутнє | 13–16 | 7.1–7.7 | not started (1 stray lexeme, ua-lexeme-0379, already exists from the grammar-guide PDF — unrelated source, will surface again in dedup) |
| 8 Риба шукає, де глибше | 16–17 | 8.1–8.7 | **done** (pre-existing) |
| 9 Рух — це життя | 17–20 | 9.1–9.7 | **done** (pre-existing) |
| 10 Суворо заборонено! | 20–22 | 10.1–10.7 | **done** |
| 11 Якби всі люди... | 22–23 | 11.1–11.7 | not started |
| 12 Не журись! | 23–24 | 12.1–12.7 | not started |

## Generated this pass

### Ch.10.1 (airport/travel prohibitions) — commit `d4091e3f`

- Lexemes: **ua-lexeme-0616 – ua-lexeme-0653** (38 notes: 26 standalone headwords, 7 noun
  phrases, 1 bundled modal-phrase-cluster note)
- Verbs: **ua-verb-0088 – ua-verb-0091** (тримати, витягати, палити, пакувати)
- All `status:draft`. Tag `ch:2.10.1`.
- **Known gap, flagged in ua-lexeme-0653's Verification Notes, not silently dropped:** the
  permission/obligation modal words (можна, треба, потрібно, мусити, могти, дозволити,
  заборонити) were checked against the corpus and are genuinely absent as standalone
  lexemes — bundled into one phrase note instead of drafting all seven as full entries, to
  keep the sub-chapter a manageable size. A future pass should give each its own
  `UA_Lexeme` (+ `UA_Verb` for the four that are verbs).
- 3 homograph collisions resolved to a single sense with the other sense(s) documented in
  `Verification Notes` but not drafted (посадка, магазин, палити) — see individual notes.

### Ch.10.2 (family/games; feelings & social verbs) — commit `93b62449`

- Lexemes: **ua-lexeme-0654 – ua-lexeme-0674** (21 notes: 5 family/fairy-tale
  nouns, 1 board-game phrase, 2 adjectives, 2 predicative adverbs, 1
  pillow-fight phrase, 10 social/feeling/conflict verbs)
- Verbs: **ua-verb-0092 – ua-verb-0102** (бажати, вірити, дзвонити,
  дивуватися, довіряти, допомагати, дякувати, радіти, дратувати, нападати,
  ображатися)
- All `status:draft`. Tag `ch:2.10.2`.
- Dedup: вибачати = bucket-3 true duplicate of **ua-lexeme-0319** (existing
  ch:2.9.6 note) — appended `ch:2.10.2` to its tags/Tags_Ch rather than
  creating a new note.
- Known gaps, flagged in Verification Notes, not silently dropped:
  насті́льна гра́ and би́тися поду́шками bundled as phrase notes without
  standalone component notes (насті́льний, гра́, би́тися, поду́шка) — same
  scope-management call as ua-lexeme-0653 in 10.1.
- нападати (напада́ти, impf, "to attack") homograph-flagged against an
  unrelated stress-shifted напа́дати (pf, "to fall in quantity, e.g. leaves")
  — not tagged homograph:true since no sibling note exists for that sense.

### Ch.10.3 (health/wellbeing) — commit `621beb43` (bundled with an unrelated
Доброї но́чі stress fix)

- Lexemes: **ua-lexeme-0675 – ua-lexeme-0700** (26 notes)
- Verbs: **ua-verb-0103 – ua-verb-0109** (зосередитися, кинути, містити,
  справлятися/справитися, страждати, схуднути, упоратися)
- All `status:draft`. Tag `ch:2.10.3`.

### Ch.10.4 (bedroom/chores) — commit `9dd09788`

- Lexemes: **ua-lexeme-0701 – ua-lexeme-0703** (3 notes: ліжко, phrase
  застеляти ліжко)
- Verbs: **ua-verb-0110** (застеляти/застелити)
- All `status:draft`. Tag `ch:2.10.4`.

### Ch.10.5 (civics/rights/repression-era history) — commit (see git log,
741 lexemes / 119 verbs after)

- Lexemes: **ua-lexeme-0704 – ua-lexeme-0743** (40 notes: civics/rights
  nouns, 6 repression-era past-participle adjectives, 2 adverbs, 8 bundled
  phrases)
- Verbs: **ua-verb-0111 – ua-verb-0119** (виділитися, відрізняти,
  дотримуватися, друкувати, обмежувати/обмежити, публікувати,
  спалювати/спалити, ставити/поставити, хрестити)
- All `status:draft`. Tag `ch:2.10.5`.
- Dedup: закон = bucket-3 true duplicate of **ua-lexeme-0473** (existing
  ch:2.8.3) — appended `ch:2.10.5` to its tags/Tags_Ch.
- Craig flagged a confusable pair from this sub-chapter's право (new
  ua-lexeme-0708) vs the pre-existing закон (ua-lexeme-0473) — added as
  the `law-right-vs-statute` cluster in `confusable_clusters.yaml`,
  commit `928bf79c` (separate from the ch.10.6 vocab commit below).

### Ch.10.6 (illness/injury symptoms; body parts; treatment) — commit `c741bd47`

- Lexemes: **ua-lexeme-0744 – ua-lexeme-0794** (51 notes: 24 standalone
  nouns/adjectives, 17 verb-lexeme entries, 10 bundled phrases)
- Verbs: **ua-verb-0120 – ua-verb-0136** (17 notes, paired 1:1 with the
  verb lexemes: боліти [pain sense, defective], виписати, зробити,
  оглянути, поміряти, послухати [medical sense], промивати, приймати,
  ворушити, змерзнути, кашляти, нудити, паморочитися, почуватися,
  свербіти, уникати, чхати)
- All `status:draft`. Tag `ch:2.10.6`.
- Dedup (bucket-3, tag appended rather than redrafted): сонячний →
  ua-lexeme-0400 (ch:2.8.1); удар → ua-lexeme-0174 (ch:2.9.2);
  температура → ua-lexeme-0516 (ch:2.8.5); рідина → ua-lexeme-0625
  (ch:2.10.1).
- Known gaps flagged in Verification Notes (not silently dropped): ніс,
  спеціальний, жодний, випадок bundled into phrase notes without
  standalone headwords (checked, genuinely absent from corpus); робити
  and прийняти (impf/pf counterparts of зробити/приймати) still absent,
  flagged for a future pass; болити's other 2 homograph senses
  ('worry about' / 'be ill') not drafted; паморочитися and свербіти have
  1st/2nd-person present + imperative fields intentionally left blank
  (Горох doesn't mark their stress on those forms — never-guess rule).
- Found (not fixed, out of scope): `validate_confusable_clusters.py` has
  a pre-existing bug — it looks up note_ids in a dict that
  `load_corpus()` actually keys by lemma, so it reports every cluster's
  members as "not found in corpus" regardless of correctness. Does not
  affect `pytest tests/ua/` (523/523 still green). Left for Craig.

### Ch.10.7 (consular services; border/customs; travel health) — commit `47e518b7`

- Lexemes: **ua-lexeme-0795 – ua-lexeme-0827** (33 notes: 22 standalone
  nouns/adjectives, 3 verb-lexeme entries, 8 bundled phrases)
- Verbs: **ua-verb-0137 – ua-verb-0139** (звернутися, перебувати,
  підтвердити)
- All `status:draft`. Tag `ch:2.10.7`.
- Dedup (bucket-3, tag appended rather than redrafted): контроль →
  ua-lexeme-0640 (ch:2.10.1); уникати → ua-lexeme-0783 (ch:2.10.6, appears
  in both 10.6 and 10.7 wordlists).
- Referenced but not re-tagged (basic ch:1.0 vocab embedded in a longer
VP phrase, same precedent as кинути палити): лікар (ua-lexeme-0006) in
  звернутися до лікаря; країна (ua-lexeme-0041) in перебувати в країні.
- **Chapter 10 (Суворо заборонено!) is now fully done, all of 10.1–10.7.**

### Ch.1.1 (weekdays/holidays; leisure verbs) — commit `e69d17f1`

- Lexemes: **ua-lexeme-0828 – ua-lexeme-0838** (11 notes: 2 standalone
  nouns, 3 verb-lexeme entries, 1 collective numeral, 1 adverb, 4 bundled
  phrases)
- Verbs: **ua-verb-0140 – ua-verb-0142** (відпочивати, ненавидіти,
  розважатися)
- All `status:draft`. Tag `ch:1.1`.
- обидва/обидві/обоє drafted as one lexeme note per the textbook's grouping.
- Dedup (referenced, NOT re-tagged — basic word inside a longer VP, same
  precedent as лікар/країна in ch.10.7): спорт (ua-lexeme-0142, ch:2.9.1) in
  займатися спортог; час (ua-lexeme-0356, ch:2.9.7) in проводити час;
  ходити (ua-lexeme-0581, ch:2.9.4) in ходити в гості.
- Known gaps flagged (not drafted, scope management): займатися,
  проводити, сидіти, інтернет, гість.

### Ch.1.2 (voice/speech; everyday verbs) — commit `041ddcfd`

- Lexemes: **ua-lexeme-0839 – ua-lexeme-0849** (11 notes: 1 noun, 7
  verb-lexeme entries, 3 adverbs)
- Verbs: **ua-verb-0143 – ua-verb-0149** (вживати, вишивати, відкривати,
  впізнавати, додавати, жартувати, здаватися)
- All `status:draft`. Tag `ch:1.2`.
- здаватися drafted for its "уявлятися" (to seem) sense only, matching the
  wordlist's здається ("it seems"); unrelated "admit defeat" sense not
  drafted.

### Ch.1.3 (time/weather/profession; opinion & routine verbs) — commit `354bdf23`

- Lexemes: **ua-lexeme-0850 – ua-lexeme-0882** (33 notes: 15 standalone
  nouns/adverbs, 14 verb-lexeme entries, 2 bundled phrases, plus 2
  pre-existing notes patched with an added `ch:1.3` tag)
- Verbs: **ua-verb-0150 – ua-verb-0164** (божеволіти, вважати, відбуватися,
  відчувати, завантажувати, знайомитися, називати, намагатися, обідати,
  снідати, створювати, триматися, шукати, залишатися)
- All `status:draft`. Tag `ch:1.3`.
- Dedup (referenced, retagged per dedup bucket 3 -- compound-phrase content
  word): сонячний (ua-lexeme-0400) in сонячна погода; кордон
  (ua-lexeme-0800) in їздити за кордон, both got `ch:1.3` appended to
  Tags_Ch/tags.
- Dedup (referenced, NOT retagged -- basic ch:1.0 word inside a longer VP,
  same precedent as лікар/країна in ch.10.7): рік, їздити, ходити, спорт,
  час, лікар, країна.
- New precedent established: when ALL components of a would-be bundled
  phrase are themselves freshly drafted in the same pass (not pre-existing
  gaps), skip the bundled phrase note and use the phrase as the example
  sentence on the relevant standalone entry instead (applied to
  "залишатися вдома", ua-lexeme-0880). Contrast with a genuine unresolved
  gap component (сидіти) -- still bundle as a phrase note in that case
  ("сидіти годинами за комп'ютером", "сидіти в інтернеті").

### Aspect-pairing review pass (ch.1.1–1.3, ch.10.1–10.7) — commit `96992818`

- Craig's instruction: systematically review every UA_Lexeme verb note
  drafted so far for missing perfective/imperfective aspect-partner
  cross-references, using `yabluko-l2-verb-dictionary.pdf` as the primary
  source (Горох as fallback), even where the vocabulary list doesn't
  explicitly call out the pairing. Where a headword has multiple listed
  perfectives (esp. PVOM), use the dictionary's primary/first-listed
  pairing.
- Lightweight convention (no separate note pairs created for the partner):
  imperfective headword -> fill `Perfective` field with the stressed
  perfective lemma, update `TypingAnswer` to `"{impf} / {pf}"`, extend
  `Source_URL` with the partner's Горох page, append a sentence to
  `Verification Notes`. Perfective headword -> just append a
  "Imperfective counterpart X added" sentence to `Verification Notes`
  (TypingAnswer/Perfective field untouched). Tantum verbs (no partner
  exists) -> append a note confirming the dictionary/Горох check found
  none.
- 52 existing lexeme notes patched (spanning ch:1.1, ch:1.2, ch:1.3,
  ch:2.10.1, ch:2.10.3, ch:2.10.5, ch:2.10.6, ch:2.10.7).
- Recovered from a self-inflicted duplicate-patch bug (importing the patch
  script from a diagnostic script re-executed all its top-level code,
  double-applying the Verification Notes addendum) — reverted all 52 files
  to HEAD and re-ran the patch script via direct execution only.
- Validated clean (schema/euphony/pytest 523/523) after the fix.
- **Going forward: this convention is now applied proactively at initial
  verb-drafting time (see ch.1.4 below), not deferred to a later review
  pass.**

### Ch.1.4 (mood/dental-care; everyday verbs) — commit `0a1ee745`

- Lexemes: **ua-lexeme-0883 – ua-lexeme-0896** (14 notes: 4 standalone
  nouns, 1 predicative adverb, 9 verb-lexeme entries)
- Verbs: **ua-verb-0165 – ua-verb-0173** (вставляти, заважати, носити,
  оцінювати, пекти, плакати, платити, різати, чистити)
- All `status:draft`. Tag `ch:1.4`.
- **First sub-chapter with aspect pairings applied at initial drafting
  time** (per Craig's instruction, see review pass above): вставляти ->
  вставити, заважати -> завадити, носити -> поносити (delimitative
  "carry/wear for a while" -- dictionary's primary listed pairing for
  multidirectional носити), оцінювати -> оцінити, пекти -> спекти,
  плакати -> заплакати, платити -> заплатити, різати -> порізати,
  чистити -> почистити. All sourced from `yabluko-l2-verb-dictionary.pdf`
  primary pairing, stress-verified via Горох.
- носити drafted with `VerbMotion_Pair: не́сти / носи́ти` per design.md's
  motion-verb convention (cf. доїжджати, ua-lexeme-0128) -- multidirectional
  partner of unidirectional нести, textbook context favors the extended
  "wear clothing" sense.
- плакати/платити cross-linked via `ConfusableSet` (similar spelling,
  unrelated meaning, stress-only 1sg minimal pair плачу́/пла́чу).
- New precedent reused: "чистити зуби перед сном" used as чистити's example
  sentence rather than a bundled phrase note, since зуб and сон are both
  freshly drafted in this same pass (not pre-existing gaps) -- same as
  залишатися вдома in ch.1.3.
- Dedup: конкурс, настрій, зуб, сон, важливо, вставляти, заважати, носити,
  оцінювати, пекти, плакати, платити, різати, чистити, "чистити зуби перед
  сном" all confirmed brand new (no corpus matches).

### Ch.1.5 (Christmas customs/traditions; celebration verbs) — commit `fb44960f`

- Lexemes: **ua-lexeme-0897 – ua-lexeme-0928** (32 notes: 10 nouns, 5
  adjectives, 2 adverbs, 11 impf-headword verb-lexeme pairs, 4 pf-headword
  verb-lexeme entries)
- Verbs: **ua-verb-0174 – ua-verb-0188** (брати, дарувати, обливати,
  очищувати, запалювати, підтримувати, святкувати, сприймати, ставитися,
  стрибати, відмовлятися, відзначити, скуштувати, надурити, змокнути)
- All `status:draft`. Tag `ch:1.5`.
- 4 pf-headword verbs drafted directly as perfective (no impf partner yet
  in corpus): відзначити (impf. відзначати undrafted), скуштувати (impf.
  куштувати undrafted), надурити (impf. дурити undrafted, not in the
  verb-dictionary either, confirmed via Горох), змокнути (impf. мокнути
  undrafted). дарувati Горох-classified "двовидове"/biaspectual but still
  paired with подарувати per Craig's aspect-pairing instruction.
- 5 existing notes retagged `ch:1.5` (dedup bucket 3, same meaning): смак
  (ua-lexeme-0553), участь (ua-lexeme-0375), вогонь (ua-lexeme-0329),
  жартувати (ua-lexeme-0845, Perfective пожартувати already present from
  the aspect-pairing review pass), нудити (ua-lexeme-0779, also got a
  short addendum documenting the "нудити від" construction).
- Bundled-phrase precedent applied twice more (all components freshly
  drafted this pass, use as example sentence instead of a phrase note):
  "почуття гумору" (on почуття), "змокнути до нитки" (on змокнути).
  Two more collocations reuse existing corpus entries as their example
  sentence without redrafting: "запалювати бенгальські вогні" (on
  запалювати), "стрибати через вогонь" (on стрибати).
- відзначити flagged for review: Горох's table shows two acute accents
  through most of the paradigm (відзна́чи́ти) -- read as two accepted
  stress placements; standard root-stress відзна́чити used pending review.
- **Aspect field convention change starting this sub-chapter**: full words
  `imperfective`/`perfective`/`biaspectual` used for the UA_Verb `Aspect`
  field (matching the majority of the pre-existing corpus, 106 notes),
  not the `impf`/`pf` abbreviations used in ch.1.1-1.4 (34 notes) --
  those 34 are a known, harmless inconsistency (no schema validator
  enforces an enum here) left as-is unless Craig asks for a cleanup pass.

### Ch.1.6 (conversation; communication verbs) — commit `ac15cf9f`

- Lexemes: **ua-lexeme-0929 – ua-lexeme-0938** (10 notes: 1 noun, 5
  adverbs, 4 impf-headword verb-lexeme pairs)
- Verbs: **ua-verb-0189 – ua-verb-0192** (зустрічатися, спілкуватися,
  терпіти, могти)
- All `status:draft`. Tag `ch:1.6`.
- казати (ua-lexeme-0317, ch:2.9.6) retagged ch:1.6 (dedup bucket 3) --
  already had Perfective сказати from the earlier aspect-pairing pass;
  reused as важко's example ("важко сказати") rather than redrafted.
- могти (modal) has no imperative forms per Горох's defective paradigm --
  left blank rather than guessed.
- Caught and fixed a copy-paste regression before validating: the 4 new
  UA_Verb notes were briefly written with `Aspect: impf` instead of the
  `imperfective`/`perfective` convention adopted starting ch.1.5.

### Ch.1.7 (adventures/reasons; narrating verbs) — commit `a9b25c6e` — **chapter 1 complete**

- Lexemes: **ua-lexeme-0939 – ua-lexeme-0961** (23 notes: 9 nouns, 1
  pronoun, 3 adjectives, 5 adverbs, 5 impf-headword verb-lexeme pairs)
- Verbs: **ua-verb-0193 – ua-verb-0197** (зупиняти, розказувати, снитися,
  сумувати, тривати)
- All `status:draft`. Tag `ch:1.7`.
- 5 existing notes retagged ch:1.7: пригода (ua-lexeme-0272), кілька
  (ua-lexeme-0477), почуття (ua-lexeme-0902, ch:1.5), казати
  (ua-lexeme-0317, ch:2.9.6/ch:1.6), сон (ua-lexeme-0886, ch:1.4 --
  resolves its own forward-reference to this sub-chapter).
- брати (ua-lexeme-0914, ch:1.5) referenced in "брати інтерв'ю" but NOT
  retagged (basic light verb in a longer VP, лікар/країна precedent).
- тривати drafted in its defective "last/occur over time" sense only
  (3rd person + future forms); снитися almost always impersonal
  (dative experiencer), same pattern as нудити.
- Caught and fixed a YAML-breaking bug immediately (before any file was
  corrupted): an unescaped colon in raw-appended Verification Notes text
  on сон broke cnsf_canonicalize.py's YAML parse; rephrased to avoid it.
- **All of chapter 1 (1.1-1.7) is now done.** Per Craig's processing
  order (10, then 1-7, then 11-12), chapters 11 and 12 are next -- their
  wordlists have not yet been transcribed from the page images.

### Ch.2.1 (shops; party/gift items) — commit `478c9cd6`

- Lexemes: **ua-lexeme-0962 – ua-lexeme-0993** (32 notes): shop-type compounds
  (зоомагазин, квітковий/комп'ютерний/продуктовий/ювелірний магазин,
  канцтовари, спорттовари, магазин взуття/електроніки/іграшок/косметики/
  одягу/сувенірів, кіоск, книгарня, супермаркет) and party/gift nouns
  (вазонок, вечірка, газета, краватка, листівка, мишка [comp. mouse sense],
  надувна кулька, папка, помада, парфуми, роликові ковзани, сережка,
  футболка, новосілля, отримувати, подарунок).
- Verbs: **ua-verb-0198** (отримувати, impf, Perfective отримати).
- All `status:draft`. Tag `ch:2.1`.
- Dedup (bucket-3, tag appended): магазин → ua-lexeme-0628 (was ch:2.10.1);
  дарувати → ua-lexeme-0915 (was ch:1.5).
- Known gaps flagged in Verification Notes (not silently dropped): several
  compound-phrase component nouns/adjectives (взуття, електроніка,
  іграшка, косметика, одяг, сувенір, канцелярський, надувний, ковзан) not
  separately drafted standalone this pass.
- **Craig's pivot instruction this pass: after chapter 1, do chapters 2–7
  in order (whole textbook chapters, each with its own N.1–N.7 sub-parts),
  THEN chapters 11–12. Deadline extended to 23:59Z 2026-08-28.**

### Ch.2.2 (beach picnic; tableware) — commit `638dad7c`

- Lexemes: **ua-lexeme-0994 – ua-lexeme-1004** (11 notes): крем-брюле,
  посуд, одноразовий, скляний, пляж, серце, ковбаска, смішний, історія,
  and verb-lexeme pairs смажити/розбивати.
- Verbs: **ua-verb-0199** (смажити, impf, Perfective посмажити),
  **ua-verb-0200** (розбивати, impf, Perfective розбити -- irregular
  perfective future розіб'ю/розіб'єш...).
- All `status:draft`. Tag `ch:2.2`. No dedup collisions.
- скляний flagged: recurs in ch.2.3's materials wordlist, expect a
  bucket-3 retag there.

### Ch.2.3 (crafts/toys; materials) — commit `8f8fe59d`

- Lexemes: **ua-lexeme-1005 – ua-lexeme-1038** (34 notes): craft/toy nouns
  (візерунок, дірка, картон, колесо, крапка, курча, майстер, майстриня,
  механізм, кораблик, літачок, прикраса, стрічка, ознака, іграшка
  [resolves ch:2.1 gap], крило), характерний, 7 material adjectives, 2
  adverbs, and verb-lexeme pairs виготовляти/вирізати/в'язати/ліпити/
  малювати/махати/розмічати/шити.
- Verbs: **ua-verb-0201 – ua-verb-0208**.
- All `status:draft`. Tag `ch:2.3`.
- Dedup (bucket-3, tag appended): малярство (ua-lexeme-0597, ch:reference),
  використовувати (ua-lexeme-0373, ch:2.9.3), вишивати (ua-lexeme-0841,
  ch:1.2), розписувати (ua-lexeme-0602, ch:reference), фарбувати
  (ua-lexeme-0603, ch:1.11.4), скляний (ua-lexeme-0997, ch:2.2).
- Judgment calls flagged: вирізати's perfective ви́різати is spelled
  identically to the impf, differs only by stress; малювати's perfective
  (намалювати) came via Горох fallback (not in the verb dictionary);
  махати's perfective chosen as махнути (semelfactive) over a co-listed
  delimitative помахати.

### Ch.2.4 (pets/staff; recency adjectives) — commit `cf427b0d`

- Lexemes: **ua-lexeme-1039 – ua-lexeme-1050** (12 notes): несподіванка,
  рибка, цуценя, кошеня, список, вчорашній, давній, колишній,
  несправжній, and verb-lexeme pairs виганяти/вимагати/складати.
- Verbs: **ua-verb-0209 – ua-verb-0211**. вимагати drafted as
  imperfectivum tantum (no perfective found in either source).
- All `status:draft`. Tag `ch:2.4`.
- Dedup (bucket-3, tag appended): водій (ua-lexeme-0003, ch:1.0), кухар
  (ua-lexeme-0005, ch:1.0).

### Next NoteIDs to use

- Next `ua-lexeme-` ID: **1099**
- Next `ua-verb-` ID: **0234**

## Environment notes for whoever continues this

- `git-lfs` is not on `device_bash`'s PATH by default — install once per session to
  `$HOME/tools/git-lfs/git-lfs` (static binary from GitHub releases, arm64) and prefix
  `PATH="$HOME/tools/git-lfs:$HOME/.local/bin:$PATH"` on every git/python command, or `git
  status`/`add`/`commit` will misbehave or the pre-commit hook will fail
  (`No module named pre_commit`). `pip3 install --user pre-commit pyyaml pytest` once per
  session likewise.
- `device_bash` cannot `rm`/`unlink` by default; git write commands can strand
  `.git/index.lock` (its own internal cleanup needs unlink too). Either request delete
  permission once via `device_request_delete_permission` on the anki folder (durable for
  the rest of that session), or ask Craig to `rm -f .git/index.lock`.
- Dedup: read the whole `domains/ua/anki/notes/lexemes/**/*.md` + `notes/verbs/*.md` corpus
  directly (grep/python frontmatter parse) into a scratch TSV rather than staging files
  individually (the real `build_lexeme_index.py` script exists but is Craig-run only, and
  per-file staging hits HTTP 429 past ~180 files). Cross-check candidates with the repo's
  own `python -m tools.anki.inspect.check_lexeme_dedup <words...>` (read-only, safe to run
  under a Big-3-suspension window) before drafting.
- After generating files: `python3 -m tools.anki.cnsf_canonicalize --write <paths>` to fix
  field order/YAML quoting, then `check_cnsf_field_schema.py` + `check_euphony_stress.py` +
  `pytest tests/ua/` (install pytest first) before committing.
