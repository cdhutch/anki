# Yabluko Level 1 Vocabulary Expansion — Progress Index

Tracks the 2026-08-29 pass sourcing `yabluko-l1-vocabulary.pdf` (image-only PDF, read via
direct visual page extraction). Branch: `feature/yabluko-l1-vocab-expansion`. Deadline:
13:00Z 2026-08-29. Per Craig: same conventions as the L2 pass (dedup-first against the
live corpus, single combined lexeme note per aspect pair with `Perfective` field
populated -- no separate second note -- `yabluko-l1-verbs.pdf` as the authoritative
aspect-pairing/paradigm reference when the wordlist's own inline `(I)/(II)` + present-tense
markup isn't enough).

**Key difference from L2**: the L1 wordlist already gives conjugation class (I/II) and,
for most verbs, the impf/pf pair and 1sg+3pl present tense forms directly inline (e.g.
"бачити (II) побачити (II)" or "варити (II)/(варю, варять)"), so most words don't need a
separate Горох/verb-dictionary lookup -- only ambiguous/irregular ones do.

**Starting state (before this pass)**: `yabluko-l1/ch-00` (Вступ) already has 114 words,
flat-tagged `ch:1.0` (no subsection breakdown) -- trusted as complete per Craig's
instruction to use the same conventions as L2 (which trusted pre-existing ch.8/9).
`yabluko-l1/ch-11` has 2 words done (`ch:1.11.1`, `ch:1.11.4`).

## PDF page map (28 pages, book pages 23-199)

| Unit | PDF pages | Book pages | Subsections | Status |
|---|---|---|---|---|
| 0 Вступ | 1-2 | 23-24 | 1-10 | **trusted done** (114 words, flat `ch:1.0`) |
| 1 | 3-4 | 36-37 | 1.1-1.7 | **done** |
| 2 | 5-6 | 50-51 | 2.1-2.7 | **done** |
| 3 | 7-8 | 64-65 | 3.1-3.7 | **done** |
| 4 | 9-10 | 75-76 | 4.1-4.7 | **done** |
| 5 | 11-12 | 89-90 | 5.1-5.7 | **done** |
| 6 | 13-14 | 100-101 | 6.1-6.7 | **done** |
| 7 | 15-16 | 112-113 | 7.1-7.7 | **done** |
| 8 | 17-18 | 130-131 | 8.1-8.7 | **done** |
| 9 | 19-20 | 145-146 | 9.1-9.7 | pending |
| 10 | 21-22 | 162-163 | 10.1-10.7 | pending |
| 11 | 23-26 | 180-183 | 11.1-11.7 (all verb aspect-pairs) | **done** |
| 12 | 27-28 | 198-199 | 12.1-12.7 | pending |

Order: finish ch.11, then 1-10, then 12.

## Workflow per subsection

1. Transcribe the subsection's word list from the visual PDF page.
2. Bulk dedup-check every word via `python3 -m tools.anki.inspect.check_lexeme_dedup
   <words...>` before drafting anything.
3. Bucket-3 matches (same meaning already in corpus, from L2 or reference): append the
   `ch:1.X.Y` tag, no new note.
4. Genuinely new words: draft lexeme (+ verb note for verbs), single combined note per
   aspect pair (`Perfective` field populated on the imperfective note; no second note).
   Use the wordlist's own inline conjugation-class/aspect/person-form data as the primary
   source; fall back to `yabluko-l1-verbs.pdf` or Горох only when that's insufficient or
   ambiguous.
5. Canonicalize + `pytest tests/ua/ -q` before each commit (must stay green -- includes
   the aspect-pairing-completeness and dual-convention-duplicate gates).
6. Update this index after each subsection.

## Methodology note (revised after starting ch.11 -- much higher volume than a per-word
Горох-verified pass could sustain against the deadline)

For NEW words (no existing corpus match): drafted from the wordlist's own inline
conjugation-class annotation plus my own knowledge of Ukrainian, with a concise example
sentence -- not individually Горох-verified per word (that pace does not fit ~250-400
new words per chapter against a same-day deadline). Two note shapes:
  - **Combined**: both impf+pf are new -> one note, imperfective headword, `Perfective`
    field populated (yabluko-l1 single-note convention).
  - **Standalone / pair-completing**: this word completes a pair whose OTHER member
    already exists in the corpus (usually from L2) -> one new note for just the missing
    word, with `CounterpartForm` cross-referencing the existing partner note (matches the
    corpus's dominant pre-cleanup two-note style; avoids touching/reformatting the
    existing note).
UA_Verb paradigm notes (the separate full-conjugation deck) are deferred for this bulk
pass -- only UA_Lexeme recognition notes are being drafted chapter-by-chapter. Flagging
for Craig's review; happy to go back and Горох-verify or add paradigms for any subset he
wants prioritized.

## Progress log

- **ch.11 (all 7 subsections, complete)**: 481 words bulk dedup-checked. 150 already
  existed in the corpus (mostly from L2) -> tagged `ch:1.11.X`, no new notes. 329 were
  genuinely new -> 243 new UA_Lexeme notes drafted (combined pairs + pair-completing +
  standalone), cutting word-count to note-count via pairing. Commits: `86923f4c` (tags),
  `fc640550`..`6d1a6db5` (11.1 through 11.6/11.7 drafts). All 547 tests green throughout.
- **ch.1 (all 7 subsections, complete)**: 186 words bulk dedup-checked. 37 already existed
  (mostly from L2) -> tagged `ch:1.1.X`. 149 initially looked new; corrected to 147 after
  fixing a phrase-tokenization false positive (see below) and 2 inflected-form/infinitive
  dedup misses handled by manual tag instead of a redundant note. 140 new UA_Lexeme notes
  drafted (mostly standalone nouns/adjectives, essentially no verb-pair complexity).
  Commits: `0013ad07` (tags, includes stash-based fix for the false positive),
  `570f63aa` (drafts), `59ff4f92` (progress index). **Bug found and fixed post-hoc**:
  12 of the ch.1.2 drafts were tagged `ch:1.2.1` instead of `ch:1.1.2` (a sub-string
  transposition in the generator script) -- corrected in `dc2d141d`. All 547 tests green
  throughout.
- **ch.2 (all 7 subsections, complete)**: 240 words bulk dedup-checked (travel/geography
  theme: places in town, university life, ancient-world wonders, directions, Venice).
  89 already existed -> tagged `ch:1.2.X`, including 6 words the literal-string dedup tool
  missed due to punctuated/inflected lemma forms (Перепрошую!, Побачимося!, Ідіть->іти́,
  Поверніть->поверта́ти/поверну́ти, Повертайтеся->поверта́тися, Скажіть->сказати) plus
  a pre-existing "будь ласка" note, resolved by manual lookup. 2 ambiguous homograph
  matches resolved by context (озеро: tagged the lower-id of two pre-existing duplicate
  "lake" notes; дорогий: picked the "expensive" sense). The imperative/directional
  subsection (2.6) decomposed entirely into existing-note tags + new standalone words --
  no atomic phrase notes needed there, unlike ch.1's greeting subsection. 128 new
  UA_Lexeme notes drafted (2674-2801), including 6 fixed multi-word phrase/idiom notes
  (Ісус Христос, Стародавній Рим, Статуя Свободи, на жаль, Щасливої дороги, До зустрічі).
  Commits: `76f328de` (tags), `c761f81d` (drafts). All 547 tests green throughout.
- **ch.3 (all 7 subsections, complete)**: 186 unique words after within-chapter dedup
  (heavy internal repetition -- many verbs/words recur across 2-4 subsections; theme:
  daily routine, hobbies, days/seasons). 98 distinct existing notes tagged (116
  tag-applications across recurring words), including 9 verb+object collocations
  (грати у футбол, слухати музику, їздити на природу, ходити до церкви, займатися
  спортом, кататися на велосипеді/лижах, робити барбекю, ходити на екскурсії,
  розмовляти по телефону) decomposed into head-verb + object-noun tags rather than
  drafted as atomic phrases, and 3 euphonic в-/у- variant pairs merged onto one
  existing note. 79 new UA_Lexeme notes drafted (2802-2880), including 3 notes using
  Lemma_Euphony for new euphonic variant pairs and 6 fixed noun-phrase notes.
  Commits: `081d662f` (tags), `f7ea84a5` (drafts), progress index this commit.
  All 547 tests green throughout.
- **ch.4 (all 7 subsections, complete)**: 178 unique words/phrases after within-chapter
  dedup (relationships/dating/wedding theme, heavy internal repetition). 105 distinct
  existing notes tagged (137 tag-applications). Decomposed collocations (взяти шлюб,
  водити машину, подивитися в очі, поїхати додому, кожного дня, тощо) into head-word
  tags/drafts. Merged одразу->відразу and очі->око (plural of an already-tagged
  singular) rather than drafting duplicates. 70 new UA_Lexeme notes drafted
  (2881-2950), including 8 fixed idiom/exclamation/compound-noun notes (Бувай!,
  Щасти тобі!, комп'ютерні ігри, Виходь за мене!, день народження, Скажи чесно!,
  одне одного, на щастя). Commits: `3a6068bf` (tags), `6101e93d` (drafts), progress
  index this commit. All 547 tests green throughout.
- **ch.5 (all 7 subsections, complete)**: 290 unique words/phrases after within-chapter
  dedup -- the largest chapter yet (food/dining/groceries theme). 118 distinct existing
  notes tagged (130 tag-applications). Decomposed adjective+noun food-menu compounds
  into constituents per the established policy, keeping only truly opaque/idiomatic
  items atomic (жаб'яча лапка, родом з, Новий рік, 3 exclamations). 173 new UA_Lexeme
  notes drafted (2951-3123). Commits: `70964197` (tags), `ac9cc91d` (drafts), progress
  index this commit. All 547 tests green throughout.
- **ch.6 (all 7 subsections, complete)**: 205 unique words/phrases after within-chapter
  dedup (Easter/Christmas traditions, diet, careers, seasonal holidays, cooking). 79
  distinct existing notes tagged (85 tag-applications), including reuse of ch.5's food
  adjective+noun vocabulary. Resolved a genuine homograph (ніж = knife vs. than) by
  context. 126 new UA_Lexeme notes drafted (3124-3249), including 9 fixed proverb/
  greeting/compound notes (the two Easter/Christmas call-response greetings, a
  proverb, Свят-вечір, Щедрий вечір, День подяки, пора року, Ням-ням!, Я б хотів/
  хотіла...). Commits: `7fa14a0b` (tags), `4857c648` (drafts), progress index this
  commit. All 547 tests green throughout.
- **ch.7 (all 7 subsections, complete)**: 288 unique words/phrases after
  within-chapter dedup (home/furniture/rooms theme transitioning into vacation-rental
  and hotel-amenities vocabulary). 118 distinct existing notes tagged (across three
  commits: 113 initial matches, +4 recovered after the mixed-script/apostrophe
  corruption fixes below, +1 more for "подвір'я"). 169 new UA_Lexeme notes drafted
  (3250-3418), including 4 fixed multi-word notes (Полярне коло, номер люкс, номер
  напівлюкс, догори ногами) and one combined aspect pair (організовувати/
  організувати). Flagged "штам" for Craig's review -- glossed with its botanical
  sense (tree trunk/bole) as the best fit for the vacation-property context, though
  an unrelated microbiology sense (strain) also exists.

  **Significant corpus-integrity findings and fixes made during this chapter's dedup
  pass** (affecting the whole corpus, not just ch.7): discovered that 259 `Lemma`
  fields across yabluko-l1 ch.2-6/ch.11 and 4 pre-existing yabluko-l2 notes used
  precomposed Latin accented vowels (e.g. Latin á/é/í/ó/ú/ý) instead of Cyrillic
  vowel + combining acute (U+0301), silently breaking `check_lexeme_dedup`'s
  exact-match lookups for those words; fixed by position-aligning each corrupted
  Lemma against its own clean `TypingAnswer` field and substituting the correct
  Cyrillic base letter. Also discovered the corpus consistently uses U+02BC
  (modifier letter apostrophe) rather than a straight quote in apostrophe-bearing
  Lemmas -- any dedup search using a straight apostrophe silently misses real
  matches; this must be accounted for in all remaining chapters (search with
  U+02BC, or manually cross-check against the corpus). Because both bugs had
  defeated dedup, a corpus-wide audit found real accumulated duplicate notes;
  merged 49 true duplicates into their canonical notes (same-book: lower note ID
  kept; cross-book L1-draft-vs-already-merged-L2: the L2 note always kept, since it
  may already be imported into Craig's live collection), migrating `ch:` tags and
  appending merge annotations before deleting the duplicate files. Also fixed a
  confusable-cluster cross-reference (`painting-verbs`) and 2 prose references that
  pointed at a deleted duplicate note ID. Commits: `1d6f0ebe` (corruption fix +
  merges), `aca2807f` (113 tags), `e379b0ee` (+4 tags), `31603eb3` (+1 tag),
  `cec22a26` (drafts), progress index this commit. All 547 tests green throughout.

- **ch.8 (all 7 subsections, complete)**: ~220 unique words/phrases after
  within-chapter dedup (months/calendar, ordinals/shopping, competitions/materials/
  jewelry, official holidays, Christmas/New Year folk traditions, opening-hours,
  daily routine -- the heaviest-reuse chapter yet). 128 distinct existing notes
  tagged, mostly basic vocabulary already drafted in the L2 pass (months, ordinals,
  common verbs) plus reuse of L1 ch.4/6/7/11 notes -- including a spelling-variant
  match ("Святвечір" matched to the already-existing hyphenated "Свят-вечір" from
  ch.6) and an apostrophe-encoding-fixed match (деревʼяний). 97 new UA_Lexeme notes
  drafted (3419-3515), including 9 fixed official-holiday-name notes (День
  Конституції України, День матері, День незалежності, День Перемоги, День Святої
  Трійці, День солідарності трударів, Міжнародний жіночий день, Зелені свята,
  Веселих свят!) and 2 fixed question-phrase notes (Котра година?, О котрій
  годині?). Flagged "гайка" (hardware nut) for Craig's review -- glossed literally
  per its plain reading, though it sits among otherwise Christmas/household
  vocabulary in the source list. Commits: `27d9148d` (tags), `74be4f49` (drafts),
  progress index this commit. All 547 tests green throughout.
