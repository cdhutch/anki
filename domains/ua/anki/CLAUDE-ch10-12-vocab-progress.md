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
| 1 Будні та свята | 1–2 | 1.1–1.7 | **done** (row was stale -- all of 1.1-1.7 completed earlier, see Ch.1.7 entry below; corrected 2026-08-28) |
| 2 Вечірка | 2–4 | 2.1–2.7 | done |
| 3 Чого нам бракує до повного щастя | 4–7 | 3.1–3.7 | **done** (all of 3.1-3.7 complete) |
| 4 Люди та історії | 7–9 | 4.1–4.7 | **done** (all of 4.1-4.7 complete) |
| 5 Скажи де, скажи коли | 9–11 | 5.1–5.6 | **done** (all of 5.1-5.6 complete) |
| 6 Що сталося? | 11–13 | 6.1–6.7 | in progress (6.1 done) |
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

### Tagging-convention corrections (2026-08-28)

Craig clarified the `ch:` tag convention: all Level-2 (яблуко-l2) chapters use the
3-component form `ch:2.<chapter>.<subchapter>` (e.g. `ch:2.3.5`), no exceptions among
chapters 1-12. `ch:1.0` (Level-1 book's вступ chapter) is a different book and stays
2-component, per Craig. Two corpus-wide corrective passes were needed since earlier work
(mine and pre-existing) had used a bare `ch:<chapter>.<subchapter>` form (missing the book
prefix) for chapters 1, 2, and 3.1-3.4:

- Commit `20aece3b`: fixed chapter 3 (`ch:3.N` -> `ch:2.3.N`, 174 files).
- Commit `0de89753`: fixed chapters 1 and 2 (`ch:1.N` -> `ch:2.1.N`, `ch:2.N` -> `ch:2.2.N`,
  450 files) -- these two chapters were completed before the correction and had never been
  swept. Verb `FreqSource` fields (chapter-level, no subchapter, e.g. `ch:2.1`) were already
  using the corrected 2-component book.chapter form for chapters 8/9/10 and are now
  consistent for 1/2/3 too.

Also added this session (commit `afe2a001`): a `castle-lock-homograph` confusable cluster
for за́мок (castle, ua-lexeme-1282, ch.2.3.4) / замо́к (lock, ua-lexeme-1302, new
reference-only companion note, `ch:reference` -- not itself a wordlist item).

### Ch.4.1 (centuries, era markers, everyday inventions) -- commit `5586ec84`

- Lexemes: **ua-lexeme-1366 - ua-lexeme-1374** (9 notes): століття, до нашої ери / до
  Різдва Христового, нашої ери / від Різдва Христового, винахід, мило, монета,
  книгодрукування, черга, котрий.
- All `status:draft`. Tag `ch:2.4.1`.
- Dedup (bucket-3, tag appended): виделка (ua-lexeme-1063, was ch:2.2.5).
- Flagged for Craig: plain який (котрий's near-synonym) not yet drafted -- only
  compounds якийсь/якийсь час exist -- so no confusable cluster registered yet.

### Ch.4.2 (months, dates, founding/proclaiming events) -- commit `b7d76377`

- Lexemes: **ua-lexeme-1375 - ua-lexeme-1391** (17 notes): 12 months, дата, хрещення,
  заснований, коронований, проголошений (deverbal adjectives, base verbs not drafted).
- Verbs: **ua-verb-0274** (виникнути, perfective, class:conj1-нути).
- All `status:draft`. Tag `ch:2.4.2`.
- Flagged for Craig: лютий (February) is a homograph with adjective лютий "fierce" (not
  yet drafted) -- flagged for future confusable-cluster registration.

### Verb-class tag fix (per Craig) -- commit `2818c10a`

- Confirmed the Pugh & Press verb-class scheme (PR #92, `d04ac539`/`02176dab`,
  `CLAUDE-ua-verb-design.md`) is merged to main and an ancestor of this branch, but only
  the original 87-note corpus was migrated -- verbs added by this vocab-expansion project
  (ch.1-4) mostly kept old ad-hoc `class:N`/`VerbClass: regular-N` values. Fixed the 5
  verb notes touched by today's session (ua-verb-0192, 0271-0274) to proper Pugh & Press
  tags. **Per Craig's explicit direction: ~120 other pre-existing verb notes across
  ch.1-3 still need a dedicated retroactive-fix pass later — deferred in favor of
  continuing ch.4-12 vocab work.** All new verb notes from here forward use correct
  Pugh & Press class tags (see ch.4.3 below for examples: conj1-vowel+й, conj1-нути,
  conj1-consonant+ти, conj2-ити).

### Ch.4.3 (WWII/occupation, emigration, education, timeline expressions) -- commit `28c6805e`

- Lexemes: **ua-lexeme-1392 - ua-lexeme-1446** (55 notes: 11 standalone nouns, 22 phrase
  notes, 4 deverbal adjectives, 12 timeline-expression phrases, 6 lexeme-only verb
  entries for VP components).
- Verbs: **ua-verb-0275 - ua-verb-0294** (20 notes, all proper Pugh & Press class tags).
- All `status:draft`. Tag `ch:2.4.3`.
- Dedup (bucket-3, tag appended): влада (ua-lexeme-0704), стаття (ua-lexeme-0063), табір
  (ua-lexeme-0265), радий (ua-lexeme-1141), розстріляний (ua-lexeme-0723), пізніше
  (ua-lexeme-0344).
- Flagged for Craig: літній професор uses літній="elderly" sense, homograph with
  літній="summery" (not yet drafted) -- flagged for future cluster.
- **Largest sub-chapter to date (75 new/retagged notes total).**

### Ch.4.4 (sports/competition, appearance, hosting verbs) -- commit `b8deb5f2`

- Lexemes: **ua-lexeme-1447 - ua-lexeme-1464** (18 notes: 7 phrase notes, 3 standalone
  nouns, 5 adjectives, 1 adverb, 2 lexeme-only verb entries for VP components).
- Verbs: **ua-verb-0295 - ua-verb-0302** (бути, стати, працювати, захоплюватися,
  цікавитися, займатися, попрощатися, годувати). All proper Pugh & Press class tags.
- All `status:draft`. Tag `ch:2.4.4`.
- бути drafted with modern zero-copula usage noted (Горох's є/єсть/єси present paradigm
  is largely archaic/emphatic-only in contemporary speech).
- стати's existing lexeme-only entry (ua-lexeme-1443, from ch.4.3) retagged ch:2.4.4
  alongside the new full UA_Verb conjugation note, since стати now also appears as its
  own bare-infinitive bullet here.
- Per Craig: progress index is now updated after every sub-chapter (this entry and
  onward), not batched across a whole chapter.

### Ch.4.5 (upbringing/community/generations, character traits) -- commit `202f5bbc`

- Lexemes: **ua-lexeme-1465 - ua-lexeme-1508** (44 notes: 12 nouns, 12 phrase notes, 12
  adjectives, 2 adverbs, 6 lexeme-only verb entries).
- Verbs: **ua-verb-0303 - ua-verb-0307** (виховати, впоратися, дбати, об'єднувати,
  поширитися). Proper Pugh & Press class tags.
- All `status:draft`. Tag `ch:2.4.5`.
- Reused without new notes (retagged ch:2.4.5): мандрівка (ua-lexeme-0330), проголошення
  незалежності (ua-lexeme-0739, whole phrase reused), бажати (ua-lexeme-0664 +
  ua-verb-0092).

### Ch.4.6 (job search/interview nouns; reporting verbs; володіти) -- commit `243dc217`

- Lexemes: **ua-lexeme-1509 - ua-lexeme-1511** (3 notes: екскурсовод, співбесіда,
  стажування). Small sub-chapter, no phrase bullets.
- Verbs: **ua-verb-0308 - ua-verb-0313** (відповісти, запитати, пообіцяти, попросити,
  сказати, володіти). All proper Pugh & Press class tags.
- All `status:draft`. Tag `ch:2.4.6`.
- відповісти drafted as `class:conj1-irregular` -- follows the archaic non-thematic
  "-вісти" conjugation shared with пові́сти (same suppletive-type paradigm as ї́сти).
- сказати drafted as the first corpus example of `class:conj1-consonant-mutation`
  (к→ж mutation runs through the whole non-past paradigm, not just 1sg, cf.
  CLAUDE-ua-verb-design.md); it is the с-prefixal perfective partner of the existing
  lexeme-only каза́ти (ua-lexeme-0317).
- Reused without new notes (retagged ch:2.4.6): досвід (ua-lexeme-1397, was ch:2.4.3
  only -- independently bulleted again here).

### Ch.4.7 (qualifications/education; civic activity; family-status forms) -- commit `d9f2feca` -- **chapter 4 complete**

- Lexemes: **ua-lexeme-1512 - ua-lexeme-1523** (12 notes: 1 lexeme-only verb entry
  захистити, 11 phrase notes). No new UA_Verb notes -- entirely NP/VP bureaucratic-form
  and academic-qualification collocations, no bare verb-infinitive bullets.
- All `status:draft`. Tag `ch:2.4.7`.
- Reused without new notes (component embedded in a longer NP/VP, not independently
  bulleted, no retag): вміння (ua-lexeme-1467, ch:2.4.5), громадський (ua-lexeme-0457,
  ch:2.8), сім'я (ua-lexeme-0062, ch:1.0), нагорода (ua-lexeme-0258, ch:2.9), отримати
  (lexeme-only ua-lexeme-1263 + full-conjugation ua-verb-0262, ch:2.3).
- "до моїх наукових зацікавлень входить" treated as one fixed formulaic-sentence phrase
  note (same precedent as Проходьте за мною., ch.3.6) rather than splitting out входити
  as a separate verb-component note.
- захистити drafted as a lexeme-only VP-embedded support-verb entry, per the extended
  VP-component rule (ua-lexeme-1263 отримати precedent) -- not independently
  bare-bulleted this sub-chapter, only inside захистити дисертацію.
- **All of chapter 4 (Люди та історії, 4.1-4.7) is now done.** Per Craig's processing
  order (2-7, then 11-12), chapter 5 (Скажи де, скажи коли) is next.

### Ch.5.1 (street/urban infrastructure; natural/property features; locative prepositions) -- commit `8446e59b`

- Lexemes: **ua-lexeme-1524 - ua-lexeme-1544** (21 notes: 9 street/infrastructure nouns
  incl. 2 phrases, 6 natural/property-feature nouns, 6 locative-preposition entries incl.
  3 phrases and one bundled synonym-pair preposition note).
- No new verbs -- pure nouns/prepositions sub-chapter.
- All `status:draft`. Tag `ch:2.5.1`.
- Reused without new notes (retagged ch:2.5.1, independently bulleted again here): будинок
  (ua-lexeme-0027, ch:1.0), озеро (ua-lexeme-0271, ch:2.9.5), паркан (ua-lexeme-1246,
  ch:2.3.4), поле (ua-lexeme-0192, ch:2.9.3).
- біля / коло bundled as one preposition note per the textbook's own pairing (same
  precedent as обидва/обидві/обоє, ch.1.1).
- Adverbial спра́ва (in справа від) flagged as a true homograph of the existing noun
  спра́ва (ua-lexeme-0799, ch:2.10.7, "matter, affair, case") -- not retagged, distinct
  lexeme, no cluster registered since the noun sense isn't bulleted here.
- Next NoteIDs: ua-lexeme-1545, ua-verb-0314.

### Ch.5.2 (train travel/station; house features; sightseeing verbs and adjectives) -- commit `3d8ea97a`

- Lexemes: **ua-lexeme-1545 - ua-lexeme-1564** (20 notes: 11 nouns, 2 phrases, 1
  lexeme-only verb entry вилізти + its phrase, 5 adjectives).
- Verbs: **ua-verb-0314 - ua-verb-0317** (забути, залишити, перевірити, побувати). All
  proper Pugh & Press class tags -- забути classified conj1-irregular (non-past stem
  parallels irregular бути's future with a за- prefix); побувати classified
  conj1-vowel+й as the documented бувати-rooted -увати exception that keeps -ва-.
- All `status:draft`. Tag `ch:2.5.2`.
- Reused without new notes (retagged ch:2.5.2, independently bulleted again here): вагон
  (ua-lexeme-0307, ch:2.9.6), виставка (ua-lexeme-1126, ch:2.2.7), ринок (ua-lexeme-0241,
  ch:2.9.4), останній (ua-lexeme-0277, ch:2.9.5).
- Two Горох summarizer garblings caught and corrected via cross-check: підлога (fetch's
  own prose contradicted its rendered accented form), залишити (reconstructed the
  mobile-stress paradigm from the попросити precedent after a badly garbled fetch).
- Next NoteIDs: ua-lexeme-1565, ua-verb-0318.

### Ch.5.3 (public buildings/monuments; architectural detail nouns; sightseeing adjectives) -- commit `c5739820` -- largest sub-chapter to date

- Lexemes: **ua-lexeme-1565 - ua-lexeme-1598** (34 notes: 22 standalone nouns, 5
  adjectives, 7 phrases).
- Verbs: **ua-verb-0318 - ua-verb-0320** (вміщувати, рекомендувати, розпочатися). All
  proper Pugh & Press class tags -- рекомендувати Горох-classified biaspectual (cf.
  дарувати, ch.1.5); розпочатися classified conj1-irregular (почати-type -н- epenthesis,
  same family as стати).
- All `status:draft`. Tag `ch:2.5.3`.
- Reused without new notes (retagged ch:2.5.3, independently bulleted again here): храм
  (ua-lexeme-1555, ch:2.5.2 -- appears in both 5.2 and 5.3 wordlists), розпис
  (ua-lexeme-0600, was ch:reference-only, now also has a real wordlist placement).
- Reused as phrase components without retag (embedded, not independently bulleted this
  sub-chapter): будівля (ua-lexeme-1524, ch:2.5.1), архітектурний (ua-lexeme-1253,
  ch:2.3), зал (ua-lexeme-1121, ch:2.2), місце (ua-lexeme-0205, ch:2.9).
- Several Горох summarizer garblings caught and corrected: затишний (spurious
  double-stress claim), глядацький (misspelled in the fetch's own prose),
  розпочатися (partial/inconsistent paradigm, reconstructed from the regular
  почати pattern).
- Next NoteIDs: ua-lexeme-1599, ua-verb-0321.

### Ch.5.4 (noon/midnight time expressions) -- commit `b521c3f1`

- Lexemes: **ua-lexeme-1599 - ua-lexeme-1602** (4 notes: південь, полудень, опівдні,
  опівночі). No verbs -- small sub-chapter.
- All `status:draft`. Tag `ch:2.5.4`.
- Reused without new notes (retagged ch:2.5.4): північ (ua-lexeme-0351, ch:2.9.7,
  midnight sense -- independently bulleted again here).
- південь/полудень textbook-listed synonym pair drafted as two cross-referenced notes,
  same precedent as житель/мешканець.
- Next NoteIDs: ua-lexeme-1603, ua-verb-0321.

### Ch.5.5 (festival/craft-fair vocabulary; joining/announcing verbs; descriptive adjectives) -- commit `d7996e4c`

- Lexemes: **ua-lexeme-1603 - ua-lexeme-1629** (27 notes: 16 standalone nouns, 2 phrases,
  1 lexeme-only verb entry збільшувати + its phrase, 7 adjectives/adverb).
- Verbs: **ua-verb-0321 - ua-verb-0323** (долучитися, заявити, приєднувати). All proper
  Pugh & Press class tags.
- All `status:draft`. Tag `ch:2.5.5`.
- захід drafted in its "event, function, measure" sense -- a third homograph layer on
  top of the existing "west" and "sunset" senses (ua-lexeme-1557, ch:2.5.2).
- Reused without new notes (retagged ch:2.5.5, independently bulleted again here):
  проходити (ua-lexeme-0120 + ua-verb-0021, ch:2.9.4), відбуватися (ua-lexeme-0868 +
  ua-verb-0152, ch:2.1.3 -- textbook-listed pair, same treatment as житель/мешканець),
  солодкий (ua-lexeme-0424, ch:2.8.2).
- Next NoteIDs: ua-lexeme-1630, ua-verb-0324.

### Ch.5.6 (resort/recreation vocabulary; arranging/overnighting verbs; hospitality formulas) -- commit `3eff865d` -- **chapter 5 complete**

- Lexemes: **ua-lexeme-1630 - ua-lexeme-1644** (15 notes: 4 standalone nouns, 9 phrases, 2
  adjectives).
- Verbs: **ua-verb-0324 - ua-verb-0325** (домовлятися, переночувати). Proper Pugh & Press
  class tags.
- All `status:draft`. Tag `ch:2.5.6`.
- Reused without new notes (retagged ch:2.5.6, independently bulleted again here): пляж
  (ua-lexeme-0998, ch:2.2.2), ходьба (ua-lexeme-0148, ch:2.9.1), гірськолижний
  (ua-lexeme-0510, ch:2.8.5).
- **All of chapter 5 (Скажи де, скажи коли, 5.1-5.6) is now done.** Per Craig's processing
  order (2-7, then 11-12), chapter 6 (Що сталося?) is next.
- Next NoteIDs: ua-lexeme-1645, ua-verb-0326.

### Ch.6.1 (household mishaps; imperfective-perfective verb pairs; frequency-adverb phrases) -- chapter 6 started, first use of ch-06 directory

- Lexemes: **ua-lexeme-1645 - ua-lexeme-1687** (43 notes: 3 standalone nouns, 3 adverbs, 33
  verb-pair lexemes, 1 lexeme upgrade for a pre-existing verb-only note (спіймати), 4
  frequency phrases).
- Verbs: **ua-verb-0326 - ua-verb-0358** (33 notes covering 17 imperfective-perfective pairs:
  давати/дати, брати/взяти, викликати/ви́кликати [stress-differentiated], виміряти/ви́міряти
  [stress-differentiated], готувати/приготувати, допомагати/допомогти, купувати/купити,
  ламатися/зламатися, ловити/спіймати, мити/помити, писати/написати, прасувати/випрасувати,
  прати/випрати, прибирати/прибрати, ремонтувати/відремонтувати, смердіти/засмердіти,
  телефонувати/зателефонувати, чистити/почистити, читати/прочитати). Proper Pugh & Press
  class tags throughout (writа́ти/пишу́-type conj1-consonant-mutation for писати/написати;
  mobile-stress conj2-ити for купити/ловити/смердіти pairs; conj1-irregular for the
  suppletive/ablaut verbs дати, взяти, допомогти, прати/випрати, прибрати).
- All `status:draft`. Tag `ch:2.6.1`.
- Reused without new notes (retagged ch:2.6.1, independently bulleted again here as this
  sub-chapter's aspect-pair items): давати (ua-lexeme-1508, ch:2.4.5 -- upgraded from
  lexeme-only to a full verb note here), брати (ua-lexeme-0914/ua-verb-0174, ch:2.1),
  викликати (ua-lexeme-0338/ua-verb-0071, ch:2.9), допомагати (ua-lexeme-0669/ua-verb-0097,
  ch:2.10), спіймати (ua-verb-0279, ch:2.4.3 -- given its first lexeme note here), чистити
  (ua-lexeme-0896/ua-verb-0173, ch:2.1), черевик (ua-lexeme-1128, ch:2.2.7).
- Judgment calls: виміряти/ви́міряти corrected from Горох's garbled "и"-spelling to the
  standard і-spelling (мі́ряти root); прибрати's past tense kept fixed-stress (при-family
  ablaut precedent) unlike the unprefixed брати/взяти's mobile past; допомогти and
  прати/прибрати classified conj1-irregular for their non-thematic/ablaut alternations rather
  than the regular consonant/vowel-final buckets.
- Next NoteIDs: ua-lexeme-1688, ua-verb-0359.

### Deadline update

Per Craig: deadline extended from 23:59Z 2026-08-28 to **13:00Z 2026-08-29**.

### Next NoteIDs to use

- Next `ua-lexeme-` ID: **1688**
- Next `ua-verb-` ID: **0359**

### Ch.3.7 (opinion formulas; happiness/values; trust and friendship) -- commit `24f60661` -- **chapter 3 complete**

- Lexemes: **ua-lexeme-1336 - ua-lexeme-1365** (30 notes). Verbs: **ua-verb-0271 -
  ua-verb-0273** (стверджувати, дивувати, зрадити).
- Dedup (bucket-3, tag appended): рух (ua-lexeme-0463, ch:2.8.3). Reused without
  retag: радість, час, справжній.
- **All of chapter 3 (3.1-3.7) is now done.** Per Craig's processing order,
  next up: chapters 4-7, then 11-12.

### Ch.3.6 (restaurant/cafe: menu items, ordering formulas) -- commit (see git log)

- Lexemes: **ua-lexeme-1303 - ua-lexeme-1335** (33 notes): закуска, салат, гарнір,
  десерт, напій, замовлення, вершки, відбивна, голубці, деруни, млинці, морозиво,
  оселедець, родзинки, чорнослив, шашлик, юшка, нежирний, смажений, тушкований
  (standalone), plus 13 phrase notes (перші страви/на перше, другі страви/на друге,
  щось пити, вільний столик, риба на грилі, стейк з яловичини, стейк зі свинини,
  (не)газована вода, напівсолодке вино, трав'яний чай, Проходьте за мною.,
  Принесіть відразу рахунок., Скільки з мене / з нас?).
- Verbs: **ua-verb-0270** (принести, perfective, imperfective приносити not
  drafted separately).
- All `status:draft`. Tag `ch:2.3.6`.
- Dedup (bucket-3, tag appended): келих (ua-lexeme-1065, ch:2.2.5), Що ви можете
  порадити? (ua-lexeme-1117, ch:2.2.6). Reused without retag (compositional only):
  страва, проходити, скільки, вода, стіл.
- Verified against literal PDF pages 205-206, not reconstructed memory.

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
