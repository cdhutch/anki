# Ch.10-12 + Ch.1-7 Vocabulary Expansion — Progress Index

Tracks the 2026-08-28/29 autonomous pass sourcing `yabluko-l2-vocabulary.pdf` chapters
other than 8/9 (already done). Branch: `feature/yabluko-l2-vocab-expansion`. Order per
Craig: ch.10, then ch.1-7, then ch.11-12. **As of 2026-08-29, all chapters (1-12) are
complete** -- this was the last remaining scope for the pass.

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
| 6 Що сталося? | 11–13 | 6.1–6.7 | **done** (all of 6.1-6.7 complete) |
| 7 Наше майбутнє | 13–16 | 7.1–7.7 | **done** (all of 7.1-7.7 complete) |
| 8 Риба шукає, де глибше | 16–17 | 8.1–8.7 | **done** (pre-existing) |
| 9 Рух — це життя | 17–20 | 9.1–9.7 | **done** (pre-existing) |
| 10 Суворо заборонено! | 20–22 | 10.1–10.7 | **done** |
| 11 Якби всі люди... | 22–23 | 11.1–11.7 | **done** (all of 11.1-11.7 complete) |
| 12 Не журись! | 23–24 | 12.1–12.7 | **done** (12.1/12.3/12.5/12.6/12.7 complete -- 12.2/12.4 have no vocabulary) |

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

### Ch.6.2 (daily routine; imperfective-perfective verb pairs; frequency adverbs)

- Lexemes: **ua-lexeme-1688 - ua-lexeme-1726** (39 notes: 2 standalone nouns, 5 frequency
  adverbs, 4 lexeme upgrades for pre-existing verb-only notes (годувати, іти, піти,
  працювати), 28 new verb-pair lexemes).
- Verbs: **ua-verb-0359 - ua-verb-0387** (29 notes: 1 verb-note upgrade for the pre-existing
  lexeme-only повертатися, 28 new verb-pair notes covering 19 aspect pairs: вставати/встати,
  годувати/нагодувати, грати/пограти, гуляти/погуляти, закінчуватися/закінчитися,
  змінюватися/змінитися, іти/піти, лягати/лягти, обідати/пообідати, одягатися/одягнутися,
  повертатися/повернутися, починатися/початися, працювати/попрацювати, приймати/прийняти,
  прокидатися/прокинутися, сідати/сісти, слухати/послухати, снідати/поснідати,
  спізнюватися/спізнитися). Proper Pugh & Press class tags throughout (conj1-irregular for
  лягти/сісти/початися/прийняти's suppletive or ablaut alternations; mobile-stress conj2-ити
  for змінитися/спізнитися; conj1-нути for the -нутися perfectives).
- All `status:draft`. Tag `ch:2.6.2`.
- Reused without new notes (retagged ch:2.6.2, independently bulleted again here): обідати
  (ua-lexeme-0874/ua-verb-0158, ch:2.1), повертатися (ua-lexeme-0611, ch:2.9 -- lexeme
  reused, new verb note added), приймати (ua-lexeme-0775/ua-verb-0127, ch:2.10), сідати
  (ua-lexeme-1093/ua-verb-0231, ch:2.2), послухати (ua-lexeme-0773/ua-verb-0125, ch:2.10),
  снідати (ua-lexeme-0876/ua-verb-0160, ch:2.1), зазвичай (ua-lexeme-0952, ch:2.1), постійно
  (ua-lexeme-0847, ch:2.1). читати/прочитати (ua-lexeme-1682/1683, ua-verb-0357/0358, both new
  this session in ch.6.1) also retagged ch:2.6.2 -- the wordlist's читати-прочитати pair
  appears to recur at the end of both 6.1's and 6.2's verb-pair lists in the source PDF.
- Judgment calls: повернутися/одягнутися stress normalized to a consistent mobile pattern
  (1sg/3pl end-stressed, middle forms stressed on -не-) after Горох flagged internal
  disagreement; прокинутися kept fixed-stress (differs from the -нутися mobile family) per
  the well-attested "я прокинувся" pronunciation; прийняти (душ) textbook parenthetical
  treated as a sense-note on the existing приймати/прийняти pair rather than a separate
  phrase, since no new phrase-specific vocabulary is introduced.
- Next NoteIDs: ua-lexeme-1727, ua-verb-0388.

### Ch.6.3 (crime/prison; getting lost; solitude; imperfective-perfective verb pairs; duration/manner adverbs)

- Lexemes: **ua-lexeme-1727 - ua-lexeme-1788** (62 notes: 19 nouns/NP phrases, 2 adjectives,
  32 verb-pair lexemes, 1 lexeme upgrade (потрапити), 6 duration phrases, 5 manner adverbs).
- Verbs: **ua-verb-0388 - ua-verb-0415** (28 notes covering 16 aspect pairs: вживати/вжити,
  виливати/вилити, вирушати/вирушити, відповідати/відповісти, доводити/довести (+ довести до
  кінця idiom), доглядати/доглянути, блукати/заблудитися, задумуватися/задуматися,
  занурюватися/зануритися, зачинятися/зачинитися, зловживати/зловжити, красти/вкрасти,
  курити/покурити, наказувати/наказати, підніматися/піднятися, турбуватися/потурбуватися).
  Proper Pugh & Press class tags (conj1-irregular for the жи-/жив- ablaut family
  вжити/зловжити/вилити and the -няти family піднятися; conj1-consonant+ти for
  красти/вкрасти/довести).
- All `status:draft`. Tag `ch:2.6.3`.
- **Judgment call**: the source PDF's wordlist has an orphaned line "– заблудитися" with no
  legible left-hand word (two-column OCR artifact after "доглядати – доглянути"). Reconstructed
  as блукати-заблудитися, a well-attested real aspect pair fitting the chapter's "getting lost"
  theme.
- Reused without new notes (retagged ch:2.6.3): вживати (ua-lexeme-0840/ua-verb-0143, ch:2.1),
  вирушати (ua-lexeme-0340/ua-verb-0072, ch:2.9), відповісти (ua-verb-0308, ch:2.4.6 -- verb
  only, its imperfective partner відповідати drafted fresh here), підніматися
  (ua-lexeme-0286/ua-verb-0056, ch:2.9), потрапляти (ua-lexeme-1087/ua-verb-0225, ch:2.2),
  потрапити (ua-verb-0289, ch:2.4.3 -- given its first lexeme note here), міцний
  (ua-lexeme-0593, ch:reference).
- Next NoteIDs: ua-lexeme-1789, ua-verb-0416.

### Ch.6.4 (magic trick anecdote vocabulary) -- small sub-chapter

- Lexemes: **ua-lexeme-1789 - ua-lexeme-1796** (8 notes: 4 nouns, 4 verb-pair lexemes).
- Verbs: **ua-verb-0416 - ua-verb-0419** (4 notes: вистрибувати/вистрибнути,
  лунати/пролунати -- the latter pair's imperative left blank, as a "sound resounding" is not
  naturally commanded).
- All `status:draft`. Tag `ch:2.6.4`. No dedup collisions -- everything new.
- Next NoteIDs: ua-lexeme-1797, ua-verb-0420.

### Ch.6.5 (crime/danger anecdote; imperfective-perfective verb pairs)

- Lexemes: **ua-lexeme-1797 - ua-lexeme-1834** (38 notes: 4 nouns, 32 verb-pair lexemes, 2 lexeme
  upgrades (вирішити, принести)).
- Verbs: **ua-verb-0420 - ua-verb-0451** (32 notes covering 16 aspect pairs: вбивати/вбити,
  вигнати (partner of existing виганяти), вирішувати/вирішити, вити/завити,
  віситися/повіситися, гавкати/загавкати, голодніти/зголодніти, запросити (partner of existing
  запрошувати), лізти/залізти, лякатися/злякатися, напиватися/напитися, полювати/вполювати,
  приносити/принести, спробувати (partner of existing пробувати), рятувати/врятувати,
  служити/послужити, старіти/постаріти, потерпіти (partner of existing терпіти),
  хапати/схопити). Ablaut families вбити (бити-group) and напитися (пити-group) classified
  conj1-irregular; вигнати (гнати-group ablaut) also conj1-irregular; лізти
  conj1-consonant+ти (нести/вести/лізти-family).
- All `status:draft`. Tag `ch:2.6.5`.
- **Judgment call**: голодніти is another orphaned-imperfective OCR gap (Горох's own entry also
  404'd), reconstructed by analogy with its confirmed perfective partner зголодніти, matching
  the ch.6.3 блукати-заблудитися precedent.
- **Lower-confidence reconstructions** (flagged in Verification Notes): віситися/повіситися
  (base verb ви́сіти's reflexive, paradigm inferred rather than directly confirmed) and
  потерпіти (Горох's table was garbled/mislabeled; reconstructed via the standard п->пл
  mobile-stress mutation shared with терпіти).
- **Double-accent artifact** normalized to a single stress mark for старіти/постаріти
  (старі́ти/постарі́ти), matching prior corrections this chapter (смітник, сміття, красти).
- Reused without new notes (retagged ch:2.6.5): виганяти (ua-lexeme-1048/ua-verb-0209, ch:2.2),
  запрошувати (ua-lexeme-1143/ua-verb-0235, ch:2.2), пробувати (ua-lexeme-1094/ua-verb-0232,
  ch:2.2), терпіти (ua-lexeme-0937/ua-verb-0191, ch:2.1), повертатися (ua-lexeme-0611/
  ua-verb-0375, ch:2.9), повернутися (ua-lexeme-1714/ua-verb-0376, ch:2.6.2 -- second retag).
- Next NoteIDs: ua-lexeme-1835, ua-verb-0452.

### Ch.6.6 (UFO anecdote) -- small sub-chapter

- Lexemes: **ua-lexeme-1835 - ua-lexeme-1846** (12 notes: 1 noun (НЛО), 2 verb-pair lexemes,
  9 storytelling discourse formulas).
- Verbs: **ua-verb-0452 - ua-verb-0453** (2 notes: скасовувати/скасувати).
- **New pattern this sub-chapter**: fixed discourse/storytelling formulas (Уявляєш, ...; Ти не
  повіриш; І це ще не все; Виявилося...; Що, серйозно?; Не може бути!; Здуріти!; Ого!;
  Жартуєш?) drafted as single `pos:phrase` (+ `pos:interjection` where exclamatory) notes, each
  frozen as one lemma with no verb-conjugation component split, following the established
  Будьмо!/приvіт precedent (ua-lexeme-1098, ua-lexeme-0105).
- All `status:draft`. Tag `ch:2.6.6`.
- Reused without new notes (retagged ch:2.6.6): справді (ua-lexeme-0846, ch:2.1.2 -- adverb
  sense reused for its exclamatory "Справді?" reaction use), неймовірно (ua-lexeme-0575,
  ch:2.8.7 -- same, for "Неймовірно!").
- Next NoteIDs: ua-lexeme-1847, ua-verb-0454.

### Ch.6.7 (bear/berry-picking anecdote) -- small sub-chapter -- **chapter 6 complete**

- Lexemes: **ua-lexeme-1847 - ua-lexeme-1867** (21 notes: 4 nouns, 1 adjective, 6 augmentative
  intensive adjectives (-езн-/-елезн- suffix), 10 verb-pair lexemes).
- Verbs: **ua-verb-0454 - ua-verb-0463** (10 notes covering 5 aspect pairs:
  милуватися/помилуватися, плямкати/заплямкати, ревіти/заревіти, торопіти/сторопіти,
  сяяти/засяяти).
- All `status:draft`. Tag `ch:2.6.7`.
- **Judgment call**: торопіти resolves the OCR-dropped-imperfective gap flagged after
  ревіти-заревіти in the wordlist (third such gap this chapter, after блукати-заблудитися in
  6.3 and голодніти-зголодніти in 6.5); unlike those two, торопіти's own Горох entry exists
  and confirms the reconstruction directly rather than by pure analogy.
- ревіти/заревіти classified `conj1-irregular`: -іти infinitive shape but conjugation-I
  non-past endings (реву...ревуть), distinct from the regular conj2-іти verbs (e.g. летіти)
  already in this corpus.
- Augmentative adjectives (височезний, величезний, глибочезний, широчезний, довжелезний,
  старезний) cross-referenced to their base adjectives where already drafted (високий,
  великий, широкий, довгий, старий); глибокий not yet in the corpus, so глибочезний has no
  cross-reference.
- Reused without new notes (retagged ch:2.6.7): спина (ua-lexeme-1061, ch:2.2.5).
- **Chapter 6 (Що сталося?) is now fully complete, sub-chapters 6.1-6.7.**
- Next NoteIDs: ua-lexeme-1868, ua-verb-0464.

### Ch.7.1 (devices/tech vocabulary) -- start of chapter 7

- **Workflow note**: `device_stage_files` hit a stale-session auth error this pass (session
  needs re-login on the linked computer); switched to `pdftotext -layout` run directly via
  `device_bash` on the source PDF instead of staging it for image-based `Read`. This works well
  for this text-layer PDF and avoids staging entirely -- use it for the remaining chapters
  (7.2-7.7, 11, 12) too, retrying `device_stage_files` only if image-level inspection is ever
  needed.
- Lexemes: **ua-lexeme-1868 - ua-lexeme-1905** (38 notes: 16 nouns, 5 adverbs/discourse
  markers, 17 verb-pair lexemes/upgrades).
- Verbs: **ua-verb-0464 - ua-verb-0482** (19 notes covering 9 aspect pairs/upgrades:
  використовувати/використати, встановлювати/встановити, доводитися/довестися,
  дряпати/подряпати, заряджати/зарядити, з'являтися/з'явитися, користуватися/покористуватися,
  поповнювати/поповнити, розбити (partner of existing розбивати),
  розряджатися/розрядитися).
- All `status:draft`. Tag `ch:2.7.1`.
- **встановлювати and використовувати get their first-ever verb notes** (lexeme notes already
  existed from earlier chapters) since their perfective partners are newly bulleted here --
  resolves the progress index's previously-flagged "stray lexeme" ua-lexeme-0379
  (встановлювати, from an unrelated grammar-guide PDF source).
- **доводитися/довестися drafted as impersonal-only modal verbs** (dative experiencer +
  infinitive, "to have to"): only 3sg present/future and neuter past are grammatical, all
  other paradigm slots deliberately left blank, extending the лунати/пролунати precedent
  (ch.6.4) to a full-paradigm case.
- Reused without new notes (retagged ch:2.7.1): мишка (ua-lexeme-0983, ch:2.2), розбивати
  (ua-lexeme-1004/ua-verb-0200, ch:2.2.2), чистити (ua-lexeme-0896/ua-verb-0173,
  ch:2.1.4/2.6.1), почистити (ua-lexeme-1681/ua-verb-0356, ch:2.6.1), довго (ua-lexeme-1778,
  ch:2.6.3), нарешті (ua-lexeme-1135, ch:2.2), як тільки (ua-lexeme-0361, ch:2.9.3), одного
  разу (ua-lexeme-1686, ch:2.6.3), випадково (ua-lexeme-1650, ch:2.6.3), раптом
  (ua-lexeme-1786, ch:2.6.4), різко (ua-lexeme-1785, ch:2.6.4).
- Next NoteIDs: ua-lexeme-1906, ua-verb-0483.

### Ch.7.2 (accounts/passwords vocabulary)

- Lexemes: **ua-lexeme-1906 - ua-lexeme-1926** (21 notes: 3 nouns, 5 adjectives, 5 adverbs/
  discourse markers, 8 verb-pair lexemes/upgrades).
- Verbs: **ua-verb-0483 - ua-verb-0489** (7 notes covering 4 aspect pairs/upgrades:
  обмінюватися/обмінятися, дізнаватися/дізнатися, змінювати/змінити, продавати/продати).
- All `status:draft`. Tag `ch:2.7.2`.
- дізнатися gets its first lexeme note (verb note ua-verb-0280 already existed from ch.4.3).
  продавати/продати are давати/дати-family -авати verbs (theme -ва- drops in the non-past);
  продати's suppletive дати-style paradigm classified `conj1-irregular`.
- Reused without new notes (retagged ch:2.7.2): рівень (ua-lexeme-0263, ch:2.9), часто
  (ua-lexeme-1690, ch:2.6.2), рідко (ua-lexeme-1691, ch:2.6.2), завжди (ua-lexeme-1692,
  ch:2.6.2), регулярно (ua-lexeme-1693, ch:2.6.2), щодня (ua-lexeme-0834, ch:2.1).
- Next NoteIDs: ua-lexeme-1927, ua-verb-0490.

### Ch.7.3 (future tech/robotics/medicine vocabulary) -- large,
page-spanning sub-chapter

- **Workflow confirmation**: the source PDF's left and right print columns run as two
  independent, non-synchronized content streams (each column has its own continuous
  sequence of sub-chapter headers across page breaks). Ch.7.3 is unusually large because
  it spans two PDF pages' worth of right-column content with no intervening sub-chapter
  header; the "7.4" header visible nearby belongs to the LEFT column's independent stream,
  not to this content. This will need re-verifying when ch.7.4 is written.
- Lexemes: **ua-lexeme-1927 - ua-lexeme-2003** (77 notes: 28 nouns, 5 adjectives, 3
  discourse phrases, 30 verb-pair lexemes (15 full pairs), 4 imperfectiva-tantum verb
  lexemes, 7 pair-member-only/upgrade verb lexemes).
- Verbs: **ua-verb-0490 - ua-verb-0529** (40 notes: 15 full aspect pairs, 4 imperfectiva
  tantum verbs, 6 new pair-member verbs whose partners already existed).
- All `status:draft`. Tag `ch:2.7.3`.
- **Imperfectiva-tantum pattern** (confirmed via Горох, not an OCR gap): виглядати,
  коштувати, пишатися, сподіватися have no aspectual partner. A dash-only wordlist entry
  ("виглядати -") signals no partner exists, distinct from the OCR-gap reconstructions of
  ch.6 (блукати-заблудитися, голодніти-зголодніти, торопіти-сторопіти) where the dash
  entry really was a missing word to reconstruct.
- **дивувати gets its first-ever lexeme note** (verb note ua-verb-0272 already existed)
  since its perfective partner здивувати is newly bulleted here -- a lexeme upgrade,
  same pattern as вирішити/принести/встановлювати/використовувати in earlier
  sub-chapters.
- **6 pair-member-only new verbs**, existing partners retagged `ch:2.7.3` alongside them:
  опублікувати (partner публікувати, ua-lexeme-0731/ua-verb-0116), уникнути (partner
  уникати, ua-lexeme-0783/ua-verb-0135), вимірювати (new, more common imperfective
  spelling; partner ви́міряти, ua-lexeme-1655/ua-verb-0331 -- NOT ua-lexeme-1654/
  ua-verb-0330, a different-spelling imperfective виміря́ти left untouched), здивувати
  (partner дивувати, upgraded above), зрости (partner зростати, ua-lexeme-1266/
  ua-verb-0265), посісти (partner посідати, ua-lexeme-0220/ua-verb-0048).
- **Горох summarizer garbling corrected via native-level Ukrainian knowledge**: вразити
  (double-accented, normalized to mobile-stress вражу́/вра́зиш/вра́зить/вра́зимо/
  вра́зите/вра́зять), полегшити (double-accented, normalized to fixed root-stress
  поле́гшу/поле́гшиш/поле́гшить/поле́гшимо/поле́гшите/поле́гшать), розповісти
  (garbled/typo'd, reconstructed as a suppletive -вісти-family verb parallel to дати:
  розповім/розповіси́/розпові́сть/розповімо́/розповісте́/розповідя́ть).
- Reused without new notes (retagged ch:2.7.3): обмежені можливості (ua-lexeme-1410),
  температура (ua-lexeme-0516), тиск (ua-lexeme-0685), потужний (ua-lexeme-0574),
  вирішувати/вирішити (ua-lexeme-1804/ua-verb-0423 and ua-lexeme-1805, ch:2.6.5 --
  added a sense note for the "(завдання)" = "solve a task/problem" collocation),
  доводити/довести (ua-lexeme-1753/ua-verb-0393 and ua-lexeme-1754/ua-verb-0394,
  ch:2.6.3).
- **Process note**: an early retag-script bug (a Verification Notes field-append regex
  that didn't account for multi-line YAML folded scalars) corrupted ua-lexeme-1804 and
  ua-lexeme-1805 before the commit; caught via a full-corpus YAML parse sweep
  (`yaml.safe_load` over every note file) before canonicalize/test, and fixed by hand.
  Also: running `cnsf_canonicalize.py --write` over the *entire* notes tree reformatted
  ~120 unrelated pre-existing `notes/verbs/exported/` stub files (field reordering only);
  these were reverted with `git checkout --` before committing, since they were not part
  of this sub-chapter's work. Going forward, canonicalize should be scoped to changed
  files only, not the whole tree.
- Next NoteIDs: ua-lexeme-2004, ua-verb-0530.

### Ch.7.3 supplement -- аналізувати/проаналізувати

- Caught via a full `pdftotext -layout` re-read of pages 212-213 cross-checking the
  committed ch.7.3 generator against the actual wordlist, before starting ch.7.4.
  аналізувати - проаналізувати ("to analyze") was missed in the initial pass.
- Lexemes: **ua-lexeme-2004 - ua-lexeme-2005**. Verbs: **ua-verb-0530 - ua-verb-0531**.
- Next NoteIDs: ua-lexeme-2006, ua-verb-0532.

### Ch.7.4 (robots/devices vocabulary) -- left-column stream

- Lexemes: **ua-lexeme-2006 - ua-lexeme-2023** (18 notes: 7 nouns, 4 verb-pair lexemes
  (2 full pairs), 5 adjectives, 1 adverb, 1 discourse phrase).
- Verbs: **ua-verb-0532 - ua-verb-0535** (4 notes: підключати/підключити,
  реєструвати/зареєструвати).
- All `status:draft`. Tag `ch:2.7.4`.
- **Correction to ch.7.3**: виглядати (ua-lexeme-1993/ua-verb-0520) was tagged
  `ch:2.7.3` in the previous commit, but a closer pdftotext re-read (comparing column
  x-positions in the `-layout` dump) confirmed it belongs to the LEFT-column stream
  (ch.7.4, alongside підключати/реєструвати), not the RIGHT-column stream (ch.7.3,
  where коштувати/пишатися/сподіватися correctly remain). Retagged `ch:2.7.4`
  accordingly; the correction is documented in both notes' Verification Notes.
- **Process improvement going forward**: cross-check every generator script's word list
  against a fresh `pdftotext -layout` dump of the actual page range *before* running it,
  not just before starting the *next* sub-chapter -- this segment caught both the
  missed ch.7.3 item (аналізувати) and the ch.7.4 misattribution (виглядати) only
  retroactively, which cost two follow-up commits.
- Next NoteIDs: ua-lexeme-2024, ua-verb-0536.

### Ch.7.5 (energy/space/invention nouns) -- compact noun-only
sub-chapter

- Lexemes: **ua-lexeme-2024 - ua-lexeme-2035** (12 notes, all nouns: USB-кабель, блютуз,
  вертоліт, винахідник, відкриття, візок, галактика, генна інженерія, дріт, електрика,
  енергоощадна лампа, заряджання).
- No verbs. All `status:draft`. Tag `ch:2.7.5`.
- Reused without a new note (retagged ch:2.7.5): енергія (ua-lexeme-0274).
- Confirmed via `pdftotext -f 13 -l 17 -layout`: the LEFT-column stream's 7.5 section
  ends at заряджання with no verb pairs, adjectives, or discourse phrases before the
  page break into 7.6 -- genuinely a short, noun-only sub-chapter, not a truncated read.
- Next NoteIDs: ua-lexeme-2036, ua-verb-0536 (unchanged, no new verbs this sub-chapter).

### Ch.7.6 (virtual reality; invitations)

- Lexemes: **ua-lexeme-2036 - ua-lexeme-2052** (17 notes: 1 noun NP, 6 verb-pair lexemes
  (3 full pairs), 10 discourse-formula phrases).
- Verbs: **ua-verb-0536 - ua-verb-0541** (6 notes: узгоджувати/узгодити,
  збиратися/зібратися, відхиляти/відхилити (запрошення)).
- All `status:draft`. Tag `ch:2.7.6`.
- **зібратися**: irregular non-past стем збер- (брати-family ablaut), classified
  conj1-irregular; normalized from Горох's colloquial `-сь` reflexive endings to
  standard `-ся`.
- **відхилити**: Горох's 1sg output was garbled (duplicated the 1pl form); corrected to
  the regular mobile-stress 1sg відхилю́ (matches хилити's paradigm).
- Reused without new notes (retagged ch:2.7.6, with a sense note for the "(запрошення)"
  = "to accept an invitation" collocation): приймати/прийняти (ua-lexeme-0775/
  ua-verb-0127 and ua-lexeme-1719/ua-verb-0380).
- **Process fix**: rewrote the retag script's Verification-Notes-append helper to scan
  the full multi-line YAML folded scalar block (not just the first line) before
  appending -- this is what caused the ch.7.3 corruption of ua-lexeme-1804/1805.
  Verified clean with a `yaml.safe_load` check on the retagged files before
  canonicalize/test this time.
- Next NoteIDs: ua-lexeme-2053, ua-verb-0542.

### Ch.7.7 (final sub-chapter of chapter 7) -- CHAPTER 7 COMPLETE

- Lexemes: **ua-lexeme-2053 - ua-lexeme-2078** (26 notes: 6 nouns, 10 verb-pair lexemes
  (5 full pairs), 2 pair-member-only verb lexemes, 1 adjective, 7 connector
  adverbs/conjunctions).
- Verbs: **ua-verb-0542 - ua-verb-0553** (12 notes: випробовувати/випробувати,
  дозволяти/дозволити, домовлятися/домовитися, економити/зекономити (кошти),
  зводити/звести).
- All `status:draft`. Tag `ch:2.7.7`.
- **звести**: вести-family ablaut non-past stem (зведу/зведеш...), classified
  conj1-irregular, matching довести's paradigm (cf. ch.6.3/6.4).
- **оцінити** (partner of existing оцінювати, ua-lexeme-0891/ua-verb-0168, ch:2.1.4):
  confirmed via Горох as FIXED-stress conj2-ity (оці́ню throughout) -- note this
  contradicts the mobile-stress choice made for переоцінити in ch.7.3, which was an
  educated guess without a direct Горох citation at the time; переоцінити was not
  retroactively changed since Ukrainian citation dictionaries do show real variation
  here and both are defensible.
- **ставати** (partner of existing стати, ua-lexeme-1443/ua-verb-0296, ch:2.4.3/2.4.4):
  давати-family -авати verb (стаю́, not *ставаю). Sense note added to стати for the
  ставати/стати друзями = "to become friends" collocation.
- Reused without new notes (retagged ch:2.7.7): оцінювати (ua-lexeme-0891/
  ua-verb-0168), стати (ua-lexeme-1443/ua-verb-0296).
- **CHAPTER 7 (Наше майбутнє) IS NOW FULLY COMPLETE**, all of 7.1-7.7.
- Next up per processing order (2-7, then 11-12): **chapter 11**. Wordlist needs a
  fresh dedup re-run and re-verification against the PDF via `pdftotext -layout`
  (not yet read this segment) -- do not reuse any page-number assumptions from
  chapters 2-10, since this segment's ch.7 work revealed the actual PDF is only 24
  pages total and printed page numbers do not equal PDF page indices.
- Next NoteIDs: ua-lexeme-2079, ua-verb-0554.

### Process addition: aspect-tantum tag validation (2026-08-28)

Craig, mid-chapter-11 prep: "Make sure that your including the perfective aspect
verbs with the imperfective lemmas" + "Remember your resources for perfective verb
forms" (pointing at `yabluko-l2-verb-dictionary.pdf`) + "Update the testing suite to
identify verbs that only contain one aspect which also don't have specific
properties identifying the verb as specifically single-aspect" + "Decide whether
this would be a code testing process or a data validation process then implement
it" + "This process should be a prerequisite for committing tranches of lexeme
YAML files."

**Decision**: data-validation concern, implemented as a pytest test (matches the
existing `test_confusable_clusters.py`/`test_confusable_integration.py` pattern of
scanning the live corpus directly), so it's a native part of `pytest tests/ua/ -q`
-- already run before every commit in this pipeline. No extra step needed.

**New**: `tools/anki/inspect/audit_verb_aspect_tags.py` + `tests/ua/
test_audit_verb_aspect_tags.py`. Flags any `ua_verb` note or `pos:verb`-tagged
`ua_lexeme` note whose own Verification Notes/Source_Note prose claims
single-aspect (tantum) status but lacks the structured `aspect:imperfective-only`/
`aspect:perfective-only` tag (the pre-existing convention from
`audit_verb_aspect_forms.py`, now extended to verb notes and to prose-only claims
-- the original script only checked lexeme `Perfective`/`ImperfectiveUnidirectional`
fields, which this project's two-notes-per-pair convention doesn't populate).
Real-corpus integration test is the actual commit gate; a documented
`KNOWN_NOT_TANTUM` allowlist covers three confirmed false positives (звучати,
казати, виписати -- all genuinely paired; the word "tantum" only appears in a
negated or third-party context in their prose).

**Backfilled** the tag onto 21 pre-existing notes (9 lexemes + 12 verb notes,
chapters 1/2/3/7/10) whose prose already stated tantum status but never got the
tag -- includes this session's own ch.7.3 tantum verbs (виглядати, коштувати,
пишатися, сподіватися). Also fixed a real stale-data bug the check surfaced:
ua-verb-0069 (перепрошувати) still claimed imperfective-only after its lexeme
sibling ua-lexeme-0321 had already been corrected (2026-07-28) to add the
perfective partner перепросити.

**Going forward (chapter 11+)**: every new tantum verb note/lexeme drafted from
here on must get the `aspect:imperfective-only`/`aspect:perfective-only` tag at
creation time (not just prose) -- `pytest tests/ua/` will now fail the commit
otherwise. Committed separately (409b257b), before resuming chapter 11 vocab.

Scope note: this backfill only covers notes whose own prose already claimed
tantum status. It does not retroactively determine aspect-pairing for the much
larger set of verb notes with no such prose signal (pre-existing corpus debt,
consistent with this project's established practice of not retroactively fixing
older chapters).

### Ch.11.1 (Наше довкілля -- pollution sources & conservation actions)

- Confirmed the full chapter 11 wordlist (11.1-11.7) via a DIRECT VISUAL READ of PDF
  pages 221-223 (Read tool, image mode) rather than relying on the pdftotext -layout
  two-column text dump -- the dump's per-line widest-gap heuristic produced real
  column-attribution errors (e.g. mis-split "саморобний"/"тьмяний" and mixed up which
  subchapter several disaster-vocabulary items belonged to). Visual page reads resolved
  every ambiguity cleanly; recommend this method over pdftotext -layout reconstruction
  for any future multi-column subchapter that still has open attribution questions.
- Lexemes: **ua-lexeme-2079 - ua-lexeme-2110** (32 notes: 11 pollution-source nouns/
  adjectives, 6 more nouns/adjective/adverb (ресурси, свідомість, свідомий, сталий
  розвиток, благочинний, переробка, повторно), 7 full new verb pairs, 1 new perfective
  singleton).
- Verbs: **ua-verb-0554 - ua-verb-0568** (15 notes).
- All `status:draft`. Tag `ch:2.11.1`.
- **Every verb aspect pair cross-checked against yabluko-l2-verb-dictionary.pdf**
  (per Craig's explicit instruction this segment) -- this corrected two Горох-based
  guesses: сортувати's perfective is **посортувати** (not відсортувати), and
  вимикати's is **вимкнути** (Горох had wrongly suggested висмикнути, an unrelated
  word meaning "to yank out").
- **задовольняти/задовольнити spelling call**: the verb-dictionary PDF prints the
  perfective as "задовільнити", but this doesn't match any standard Ukrainian word
  family (задовільний/задовільно "satisfactory" is unrelated to задоволення/
  задовольняти "satisfaction"). Горох confirms задовольнити as a real, regularly-
  formed word. Judged the PDF's spelling an OCR/typo artifact (о/і confusion) and
  drafted задовольнити; documented the discrepancy in the note's own Verification
  Notes in case this needs revisiting.
- **відмовитися added as a new perfective partner for a PRE-EXISTING imperfective-only
  lexeme**: відмовлятися (ua-lexeme-0924, drafted ch.1.5, several chapters ago) never
  had a perfective partner. Per Craig's instruction ("make sure you're including the
  perfective aspect verbs with the imperfective lemmas") this applies retroactively
  whenever an already-corpus imperfective without a partner shows up again in a later
  chapter's wordlist -- not just to newly-drafted imperfectives. Added ua-lexeme-2110/
  ua-verb-0568 and retagged/annotated ua-lexeme-0924/ua-verb-0184.
- Reused without new notes (retagged ch:2.11.1): нафта (ua-lexeme-1946, ch.7.5),
  покоління (ua-lexeme-1473, ch.4.5), сміття (ua-lexeme-1647, ch.6.1), кран
  (ua-lexeme-0812, ch.10.7, + sense note for закривати кран), економити/зекономити
  (ua-lexeme-2065/2066, ch.7.7).
- **Process fix**: the retag script's `append_verification_note` helper had a real bug
  -- converting an unquoted plain YAML scalar to a single-quoted one requires doubling
  any literal internal apostrophes ('crane (lifting device)', Craig's), which it didn't
  do. Corrupted ua-lexeme-0812.md and ua-lexeme-0924.md this pass; caught by the
  standing yaml.safe_load safety sweep (run before every canonicalize since ch.7.3),
  fixed by hand with content verified unchanged via yaml.safe_load re-check. Future
  retag scripts need this fixed in the helper itself before reuse.
- Next NoteIDs: ua-lexeme-2111, ua-verb-0569.

### Ch.11.2 (landfills & waste generation)

- Lexemes: **ua-lexeme-2111 - ua-lexeme-2121** (11 notes: сміттєзвалище/звалище nouns,
  4 full new verb pairs, пересічний adjective). All new, no dedup hits.
- Verbs: **ua-verb-0569 - ua-verb-0576** (8 notes).
- All `status:draft`. Tag `ch:2.11.2`.
- продукувати -> **випродукувати** confirmed via yabluko-l2-verb-dictionary.pdf.
- розкладатися/розкластися classified `conj1-irregular` (д retained in non-past
  розкладу́ся, simplified before the past-tense -вся cluster: розкла́вся) -- matches
  the посісти/зрости irregular pattern from ch.7.3.
- Next NoteIDs: ua-lexeme-2122, ua-verb-0577.

### Ch.11.3 (greening, recycling improvement, urban environment)

- Lexemes: **ua-lexeme-2122 - ua-lexeme-2135** (14 notes: озеленення/покращення/
  сортування verbal nouns, брак/викид/парникові гази/корок/сміттєвоз/промінь/
  яскравість nouns, 2 full new verb pairs).
- Verbs: **ua-verb-0577 - ua-verb-0580** (4 notes).
- All `status:draft`. Tag `ch:2.11.3`.
- **брак**: Горох lists two senses ('shortage/lack' and 'defective product'); drafted
  with the 'shortage, lack' sense; checked and ruled out a feared homograph with
  'marriage' (not attested in Горох at all).
- **корок**: homograph with 'cork (stopper)' exists in Горох, not drafted -- this note
  is the 'traffic jam' sense only.
- запобігти classified `conj1-irregular` (г->ж mutation, matches берегти/зберегти
  from ch.11.1).
- **поглинути**: Горох's fetched conjugation had garbled double-stress marks on
  several forms (recurring resource issue, cf. ch.7.3/7.6) -- resolved by hand to the
  regular conj1-нути pattern.
- Reused without new notes (retagged ch:2.11.3, with sense notes for their
  collocations): переробка (ua-lexeme-2094, ch.11.1, for переробка відходів),
  громадський + простір (ua-lexeme-0457/1247, for громадський простір), сонячний
  (ua-lexeme-0400, for сонячний промінь), надмірний (ua-lexeme-0679, plain reuse).
- Next NoteIDs: ua-lexeme-2136, ua-verb-0581.

### Ch.11.4 (climate-change effects & solution-proposal discourse)

- Lexemes: **ua-lexeme-2136 - ua-lexeme-2153** (18 notes: 6 nouns, 12 discourse-formula
  phrases for proposing/agreeing/disagreeing with solutions). No verb notes (fixed
  idioms, matches ch.7.6 discourse-formula pattern). All new, no dedup hits.
- All `status:draft`. Tag `ch:2.11.4`.
- Next NoteIDs: ua-lexeme-2154, ua-verb-0581 (unchanged -- no new verb notes this pass).

### Ch.11.5 (disaster/crisis vocabulary: natural & man-made catastrophes,
evacuation/cleanup response, narrative & political-suppression terms)

- Lexemes: **ua-lexeme-2154 - ua-lexeme-2173** (20 notes: аварія, вибух, виверження
  вулкана, витік радіації, землетрус, пандемія, повінь, радіаційний фон,
  радіоактивне ураження, техногенна катастрофа, евакуація, ліквідація, сценарій,
  сюжет, брехня, небезпека, підлеглий, придушення критики, непридатний, вийти
  з-під контролю). All new, no dedup hits.
- 3 new verb pairs (**ua-lexeme-2174-2179** / **ua-verb-0581-0586**), each
  cross-checked against yabluko-l2-verb-dictionary.pdf per Craig's instruction to
  include perfective partners for imperfective lemmas:
  - вибухати/вибухнути ("to explode") -- dictionary line 90 ("вибухати вибухнути
    М. Ор."). Note: Горох's own page for the bare spelling "вибухати" is a
    homograph-by-stress pair (root-stressed вибуха́ти = this regular imperfective;
    a separately-listed prefix-stressed ви́бухати is a rare perfective variant,
    parallel to the ви́писати/виписувати stress pattern documented earlier this
    chapter) -- used the root-stressed imperfective as confirmed by the dictionary.
  - гинути/загинути ("to perish, die") -- dictionary line 388 ("гинути загинути
    від + Р, під час + Р"). Exceptional tagging note: гинути is an underived
    imperfective that happens to carry the -нути suffix shape normally reserved
    for perfectives in this corpus's class scheme -- classified conj1-нути purely
    by conjugational form, with the aspect direction (impf) noted explicitly in
    the lexeme's Verification Notes to avoid confusion with e.g. вибухнути/
    вимкнути (both perfective -нути verbs).
  - захищатися/захиститися ("to protect/defend oneself") -- dictionary line 621
    ("захищатися захиститися Ор., від + Р"). захиститися shows a ст→щ mutation in
    1sg only (захищу́ся vs захисти́шся/захисти́ться...) -- this corpus's first
    drafted example of that specific mutation (простити/пустити-family pattern),
    documented in the verb note for future reference. Reflexive -сь colloquial
    contractions from Горох normalized to standard -ся/-теся/-мося throughout
    (matches established convention, cf. відмовитися ch.11.1).
- Reused without new notes (retagged ch:2.11.5, plain retags -- same senses as the
  existing notes, no gap in aspect-pair coverage): пожежа (ua-lexeme-0173, ch.9.2,
  "fire"), очищення (ua-lexeme-1245, ch.3.4, "cleaning/purification"), скасувати/
  скасовувати (ua-lexeme-1837/1836, ch.6.6 -- already a complete, cross-referenced
  aspect pair via CounterpartForm; confirms full compliance with Craig's
  perfective-partner instruction rather than finding a gap).
- All `status:draft`. Tag `ch:2.11.5`.
- Verified against direct visual read of PDF page 223 (Read tool, image mode), not
  reconstructed memory.
- `pytest tests/ua/ -q`: 547 passed (aspect-tag validation gate included).
- Next NoteIDs: ua-lexeme-2180, ua-verb-0587.

### Ch.11.6 (crisis-response planning discourse questions)

- Lexemes: **ua-lexeme-2180 - ua-lexeme-2182** (3 notes: fixed discourse-formula
  questions "Як би нам переконати їх?", "Що ми їм приготуємо?", "Що нам робити?").
  No verb notes (fixed idioms, matches ch.7.6/ch.11.4 discourse-formula pattern).
  переконати not drafted separately (appears only inside this fixed phrase);
  приготувати (ua-lexeme-1657, ch.6.1) and робити (ua-lexeme-1212, ch.3.3) already
  exist and are reused compositionally.
- All `status:draft`. Tag `ch:2.11.6`.
- `pytest tests/ua/ -q`: 547 passed.
- Next NoteIDs: ua-lexeme-2183, ua-verb-0587 (unchanged -- no new verb notes this pass).

### Ch.11.7 (concessive discourse connectors) -- **chapter 11 complete**

- Lexemes: **ua-lexeme-2183** (new: хоча, "although, even though", pos:adverb per this
  corpus's convention for connector words -- cf. однак). Reused via retag: однак
  (ua-lexeme-1914, ch.7.2, "however"). No verb notes.
- All `status:draft`. Tag `ch:2.11.7`.
- `pytest tests/ua/ -q`: 547 passed.
- **Chapter 11 (Якби всі люди) is now fully complete: 11.1-11.7, ua-lexeme-2079 through
  ua-lexeme-2183 (105 lexeme notes) + ua-verb-0554 through ua-verb-0586 (33 verb notes),
  all committed.**
- Next NoteIDs: ua-lexeme-2184, ua-verb-0587.

## Chapter 12 (Не журись!)

Confirmed via direct visual read of PDF pages 222-223 (Read tool, image mode) that
chapter 12's vocabulary-bearing subchapters are **12.1, 12.3, 12.5, 12.6, 12.7 only**
-- 12.2 and 12.4 do not appear in the compiled wordlist PDF (likely grammar-only
subchapters with no new vocabulary bullets). Processing order: 12.1, 12.3, 12.5,
12.6, 12.7.

### Ch.12.1 (emotion verbs; impersonal-predicate feeling adverbs)

- Lexemes: **ua-lexeme-2184 - ua-lexeme-2194** (11 notes): боятися/побоятися,
  злитися/розізлитися, нудьгувати/занудьгувати (3 new verb pairs), весело, страшно,
  сумно (impersonal-predicate adverbs, join нудно/цікаво), здивований, злий
  (predicate adjectives).
- Verbs: **ua-verb-0587 - ua-verb-0592** (6 notes, one per verb-pair member).
- Govt-case correction: злитися/розізлитися -- yabluko-l2-verb-dictionary.pdf lists
  "на + Р" (line 685), corrected to "на + Зн." (Accusative is the standard case for
  "злитися на когось"; judged an OCR/transcription slip, same category of fix as
  ch.11.1's задовольнити spelling correction).
- Reused via retag: дивуватися (ua-lexeme-0667, ch.10.2), радіти (ua-lexeme-0671,
  ch.10.2), сумувати (ua-lexeme-0960, ch.1.7), нудно (ua-lexeme-0450, ch.8.2), цікаво
  (ua-lexeme-0103, ch.1.0).
- All `status:draft`. Tag `ch:2.12.1`.
- `pytest tests/ua/ -q`: 547 passed.
- Next NoteIDs: ua-lexeme-2195, ua-verb-0593.

### Ch.12.3 (migration/adaptation; settling-in and worry verbs)

- Lexemes: **ua-lexeme-2195 - ua-lexeme-2209** (15 notes): адаптація, мігрант,
  міграція, населення (nouns); взяти на себе + догляд (idiom + its illustrative
  collocation noun, drafted standalone); зближуватися/зблизитися,
  облаштовуватися/облаштуватися, тривожитися/стривожитися,
  хвилюватися/розхвилюватися (4 new verb pairs); підвищити кваліфікацію (fixed
  collocation, not in the verb dictionary, no partner drafted).
- Verbs: **ua-verb-0593 - ua-verb-0600** (8 notes). Two pairs -- облаштовуватися/
  облаштуватися and тривожитися/стривожитися -- are cases where the textbook only
  bullets one member (облаштуватися, тривожитися through) and the partner was added
  per Craig's instruction. verb-dictionary line 1698 prints тривожитися's
  government as "за/черєз + Зн." (OCR-garbled є), corrected to "через".
- Reused via retag: необхідність (ua-lexeme-0618, ch.10.1), переїзд
  (ua-lexeme-1197, ch.3.3), дратувати (ua-lexeme-0672, ch.10.2), почуватися
  (ua-lexeme-0781, ch.10.6).
- All `status:draft`. Tag `ch:2.12.3`.
- `pytest tests/ua/ -q`: 547 passed.
- Next NoteIDs: ua-lexeme-2210, ua-verb-0601.

### Ch.12.5 (community/history & character: ancestry, village life, civic terms,
personality traits)

- Lexemes: **ua-lexeme-2210 - ua-lexeme-2241** (32 notes): 17 nouns/phrases (біда,
  вибори, винахідливість, внутрішня і зовнішня політика, громада, заробіток,
  напад, нащадок, несправедливість, підписання договору, поведінка,
  працьовитість, предок, прізвисько, селянин-кріпак, сміливість, степ); 5 new
  verb pairs (виховувати/виховати, добувати/добути, руйнувати/зруйнувати,
  надихати/надихнути, привабити -- new pf. partner of the pre-existing
  приваблювати ua-lexeme-0288/ch.9.5); соромитися (tantum, no perfective in
  either Горох or the verb dictionary -- tagged aspect:imperfective-only); 4
  adjectives (безстрашний, малоемоційний, оспіваний, самоіронічний); 1 adverb
  (поступово).
- Verbs: **ua-verb-0601 - ua-verb-0610** (10 notes).
- Process note: the new aspect-tag validation gate caught a real gap here --
  соромитися's lexeme note was tagged aspect:imperfective-only but its paired
  verb note (ua-verb-0610) was not, and `pytest tests/ua/ -q` failed on the
  real-corpus gate test until the verb note's tag was added. This is exactly the
  scenario the gate was built for.
- Reused via retag: захищатися (ua-lexeme-2178, ch.11.5, applied here to
  community/historical self-defense).
- All `status:draft`. Tag `ch:2.12.5`.
- `pytest tests/ua/ -q`: 547 passed (after the aspect-tag fix above).
- Next NoteIDs: ua-lexeme-2242, ua-verb-0611.

### Ch.12.6 (car-accident vocabulary; blocking a phone/bank card)

- Lexemes: **ua-lexeme-2242 - ua-lexeme-2247** (6 notes): автомобільна аварія
  (reuses аварія ua-lexeme-2154 compositionally), свідок, телефон, банківська
  картка, блокувати (biaspectual)/заблокувати (1 new verb pair).
- Verbs: **ua-verb-0611 - ua-verb-0612** (2 notes). блокувати not in the verb
  dictionary; added as the imperfective/general-aspect counterpart of the
  textbook's own bulleted заблокувати per Craig's instruction, Горох-confirmed
  biaspectual (Aspect: biaspectual, matching the ua-verb-0061-style precedent
  already in this corpus).
- Reused via retag: передбачити (ua-lexeme-1972, ch.7.3), потрапити
  (ua-lexeme-1775, ch.6.3, for потрапити в аварію -- its imperfective partner
  потрапляти, ua-lexeme-1087, already exists as a complete pair, no gap).
- All `status:draft`. Tag `ch:2.12.6`.
- `pytest tests/ua/ -q`: 547 passed.
- Next NoteIDs: ua-lexeme-2248, ua-verb-0613.

### Ch.12.7 (grammar terminology; pronunciation/dictation verbs; manner adverbs)
-- **chapter 12 complete**

- Lexemes: **ua-lexeme-2248 - ua-lexeme-2274** (27 notes): 13 grammar-terminology
  nouns/phrases (артикль, відмінок, дієслово, доконаний і недоконаний вид,
  займенник, іменник, однина, особа, прикметник, прислівник, розділові знаки,
  розмовний рівень, транскрипція); лапки + літера (collocation nouns drafted
  standalone); брати в лапки (reuses брати ua-lexeme-0914 compositionally); 4 new
  verb pairs (вимовляти/вимовити, вимовлятися/вимовитися -- distinct verbs, both
  bulleted separately; диктувати/продиктувати; мучитися/помучитися); 3 manner
  adverbs (кардинально, мовчки, напам'ять).
- Verbs: **ua-verb-0613 - ua-verb-0620** (8 notes).
- Process note: помучитися is independently attested on Горох as a real,
  fully-conjugated perfective even though neither мучитися's own Горох page nor
  the verb dictionary cross-references it -- drafted as a genuine pair rather than
  tagging мучитися tantum. The aspect-tag gate flagged the literal word "tantum"
  appearing in that note's own prose explaining this decision (a false positive,
  since мучитися does have a real perfective) -- resolved by rewording the prose,
  not by adding the tag. This is the second time this session the gate has
  surfaced a real editorial question (see ch.12.5's true positive) rather than
  just noise, which is the intended behavior.
- Reused via retag: лякатися (ua-lexeme-1817, ch.6.5, already has a complete
  partner злякатися), вголос (ua-lexeme-1787, ch.6.3).
- All `status:draft`. Tag `ch:2.12.7`.
- `pytest tests/ua/ -q`: 547 passed.
- **Chapter 12 (Не журись!) is now fully complete: 12.1, 12.3, 12.5, 12.6, 12.7
  (12.2/12.4 have no vocabulary), ua-lexeme-2184 through ua-lexeme-2274 (91
  lexeme notes) + ua-verb-0587 through ua-verb-0620 (34 verb notes), all
  committed.**
- Next NoteIDs: ua-lexeme-2275, ua-verb-0621.

### Deadline update

Per Craig: deadline extended from 23:59Z 2026-08-28 to **13:00Z 2026-08-29**.

### Next NoteIDs to use

- Next `ua-lexeme-` ID: **2275**
- Next `ua-verb-` ID: **0621**

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

## 2026-08-29 follow-up: aspect-pairing completeness + dual-convention cleanup

After all chapters (1-12) were confirmed complete, Craig asked for a count of verb-POS
lexeme notes with incomplete aspect pairings, then asked to fix them.

- **Incomplete-pairing fix**: found 23 verb lexemes (9 in ch.3, 13 in ch.4, 1 in ch.10)
  with no confirmed aspect partner and no tantum tag. Researched each via Горох +
  `yabluko-l2-verb-dictionary.pdf`. Result: 16 new lexeme+verb pairs drafted
  (`ua-lexeme-2275`-`2290` / `ua-verb-0621`-`0636`), 5 reused an existing note as the
  partner (cross-referenced), 2 were genuine tantums (`ua-lexeme-1345` залежати,
  `ua-lexeme-0780` паморочитися -- tagged `aspect:imperfective-only`).
- **Dual-convention duplicate cleanup**: while reviewing this, Craig noticed some verbs
  had BOTH a combined note (imperfective lemma with `Perfective` field populated,
  `TypingAnswer` testing both forms) AND a separate standalone note for the perfective
  form alone -- redundant coverage of the same fact. A corpus-wide scan found 78 such
  pairs (not just ch.12.7 -- spanning ch.1,3,4,5,6,7,9,10,11,12). Per Craig's decision
  (scope: all 78, method: delete the separate note), each standalone perfective note was
  deleted, its distinct chapter tag and example were merged into the surviving combined
  note's `Tags_Ch`/Verification Notes, and any stray corpus cross-references to the
  deleted IDs were repointed. UA_Verb conjugation notes were left alone (different deck,
  not the reported duplication). See
  `domains/ua/anki/CLAUDE-aspect-dual-convention-cleanup-worklist.md` for the full list of
  deleted IDs and what each one's distinctive example was, in case any deserve a
  genuinely new, separately-drafted word later (not for ID reuse -- NoteIDs aren't dense).
- Final corpus state: 2210 lexeme notes, 705 verb notes. `pytest tests/ua/ -q` green (547
  tests) throughout both fixes. 0 incomplete aspect pairings, 0 dual-convention
  duplicates remaining (both re-verified after the cleanup).
