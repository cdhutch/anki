# Ukrainian Domain — Canonical Note Design

*Branch: `feature/ua-domain` · Last updated: 2026-05-30*

---

## 0. Language and Orthographic Conventions

These conventions apply to all content in this domain.

**Dialect / register:** Modern post-Soviet Ukrainian with strong **Galician/Lviv** influence.
Formal written register. Less Russian-influenced lexicon where practical.
Source textbook (Яблуко series) originates from Lviv and reflects western Ukrainian norms.

**Formal address:** Always `Ви` / `Ваш` / `Вам` (capitalized) in formal contexts.

**Apostrophe:** Always use the Ukrainian apostrophe **U+02BC `ʼ`** — never the ASCII `'`.

**`сь` vs `ся`:** `сь` after vowels is the user's preference (дивлюсь, вчусь). Preserve
unless a specific correction is required.

**Stress marks — critical rule:** Stress placement must **never be guessed**. Verify against:
- ULIF Dictionary: https://lcorp.ulif.org.ua/dictua/
- Горох: https://goroh.pp.ua/

Do not add stress marks casually (e.g. in homework corrections). Include them only when
explicitly producing vocabulary entries or when directly requested.

**Vocabulary output format:**
```
чита́ти (IPFV) — прочита́ти (PFV) · "to read"
```
Always provide aspectual pairs for verbs. Grammar explanations always in English.

**Lexical preferences:** `ціна` over `вартість`; `Земля` over `світ` in global/satellite
contexts; `поживні речовини` for "nutrients".

---

## 1. Current State (Survey Findings)

All 3,932 existing Ukrainian notes use vanilla Anki types with no semantic
structure:

| Note Type | Count | Fields |
|---|---|---|
| Basic (and reversed card) | 2,832 | Front, Back |
| Cloze | 659 | Text, Extra |
| Basic | 441 | Front, Back |

Key tags: `textbook:яблуко` (3,229), `leech` (788 — 20%), `converted` (164),
`shevchuk` (66), `grammar_terminology` (43), `verb_of_motion` (41), `ch:2.8.x`
chapter markers.

**Problems with the current cards:**
- No part-of-speech, gender, or aspect metadata — leaner context is likely
  the root cause of the 20% leech rate.
- Verb pairs (imperfective/perfective) are sometimes merged into one Front
  field and sometimes split across separate cards.
- Grammar cloze cards contain raw HTML tables with no topic label or chapter link.
- No canonical source files — cards exist only inside Anki.

**What's already working:**
- The `UA::Recognition::*` / `UA::Production::*` deck split is the right
  architecture and should be preserved.
- The `converted` / `to_convert` tags show that manual migration has already
  been validated at small scale.

---

## 2. Goals

1. Author new Ukrainian content as CNSF markdown canonical notes under
   `domains/ua/anki/notes/`.
2. Generate Anki-importable TSV from those notes (mirroring the B737 SV
   pipeline).
3. Migrate existing Basic/Cloze cards into canonical format over time,
   enriching them with metadata in the process.
4. Reduce the leech rate by giving every card richer context (PoS, gender,
   aspect, example sentence).

---

## 3. Proposed Note Types

### 3.1 `ua_lexeme` — Lexeme (primary note type)

One canonical note per lexeme. Handles vocabulary, aspectual pairs, case
government, motion verb distinctions, confusable sets, and euphony notes.
Generates UA→EN recognition and EN→UA production cards.

**Anki note type:** `UA_Lexeme`

**Fields:**

| Field | Description | Example |
|---|---|---|
| `NoteID` | Canonical ID | `ua-lexeme-0042` |
| `Lemma` | Primary Ukrainian form (stress verified) | `ми́ти` |
| `PartOfSpeech` | noun / verb / adjective / adverb / phrase / proper-noun | `verb` |
| `Gender` | m / f / n / indecl / '' (blank for non-nouns) | `` |
| `AspectPair_IPFV` | Imperfective infinitive | `ми́ти` |
| `AspectPair_PFV` | Perfective infinitive | `поми́ти` |
| `EN_Gloss` | English gloss | `to wash, clean (transitive)` |
| `Govt_Case` | Case government hint (subtle) | `Acc` |
| `Morphology_Note` | Irregular forms, gender, declension class | `noun f. II` |
| `VerbMotion_Pair` | For motion verbs: det / indet pair | `іти / ходити` |
| `ConfusableSet` | Similar/confusable lexemes | `мити / митися` |
| `CrossLang_Analog` | Cross-language analogues (Polish, Russian, etc.) | `` |
| `EuphonyNote` | Prefix euphony, apostrophe insertion, jotation | `зʼ- before vowel` |
| `TypingAnswer` | Canonical answer for typing production card | `ми́ти / поми́ти` |
| `UA_Example` | Example sentence in Ukrainian | `Він ми́є руки.` |
| `EN_Example` | English translation of example | `He is washing his hands.` |
| `Verb_Conj_Table` | Full conjugation table (HTML) | *(see below)* |
| `Tags_Ch` | Chapter tag string for Anki | `ch:2.8.2` (= Level 2, Ch. 8, §2) |

> **Stress marks:** Only enter after verification against ULIF or Горох.
> Leave unstressed if unverified; flag with a `stress:unverified` tag.

**Card templates:**

*UA→EN (Recognition — deck: `UA::Recognition::UA→EN`)*
- Front: `Lemma` (IPFV / PFV shown together if both present)
- Back: `EN_Gloss` · `Morphology_Note` · `Govt_Case` (subtle) · `UA_Example` / `EN_Example`

*EN→UA Typing (Production — deck: `UA::Production::EN→UA::Typing`)*
- Front: `EN_Gloss` + PoS hint (no spoilers)
- Back: `TypingAnswer` · `UA_Example`

*Lexeme (Recognition — deck: `UA::Recognition::Lexeme`)*
- Front: an inflected form (from `ConfusableSet` or `Verb_Conj_Table` data)
- Back: `Lemma` · `EN_Gloss`

**CNSF frontmatter example:**

```yaml
---
note_type: ua_lexeme
note_id: ua-lexeme-0042
anki:
  model: UA_Lexeme
  deck: UA::Recognition::UA→EN
tags:
  - domain:ua
  - topic:vocabulary
  - textbook:яблуко
  - ch:2.8.2
  - pos:verb
  - status:verified
fields:
  NoteID: ua-lexeme-0042
  Lemma: ми́ти
  AspectPair_IPFV: ми́ти
  AspectPair_PFV: поми́ти
  EN_Gloss: to wash, clean (transitive)
  Govt_Case: Acc
  Morphology_Note: ''
  VerbMotion_Pair: ''
  ConfusableSet: митися
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: ми́ти / поми́ти
  UA_Example: Він ми́є руки.
  EN_Example: He is washing his hands.
  Verb_Conj_Table: ''
  Tags_Ch: ch:2.8.2
---
```

---

### 3.2 `ua_grammar` — Grammar Rules and Paradigms

Replaces the bare Cloze notes with a labelled, chapter-linked equivalent.
Content is still cloze-format so it maps cleanly to Anki's Cloze note type.

**Anki note type:** `UA_Grammar` (based on Cloze)

**Fields:**

| Field | Description | Example |
|---|---|---|
| `NoteID` | Canonical ID | `ua-grammar-0015` |
| `Topic` | Grammar topic label | `Verb Past Endings` |
| `Text` | Cloze text with `{{c1::...}}` markup | `masculine singular past: {{c1::~в}}` |
| `Extra` | Additional context, examples, table caption | `` |
| `SourceDocument` | | `яблуко` |
| `Chapter` | | `3.1` |

**Card template:** standard Anki cloze (deck: `UA::Recognition::Grammar`)

**CNSF frontmatter example:**

```yaml
---
note_type: ua_grammar
note_id: ua-grammar-0015
anki:
  model: UA_Grammar
  deck: UA::Recognition::Grammar
tags:
  - domain:ua
  - topic:grammar
  - textbook:яблуко
  - ch:3.1
  - grammar:verb_past
  - status:verified
fields:
  NoteID: ua-grammar-0015
  Topic: Verb Past Endings
  Text: 'masculine singular: {{c1::~в}} · feminine singular: {{c1::~ла}} · neuter singular: {{c1::~ло}} · plural: {{c1::~ли}}'
  Extra: ''
  SourceDocument: яблуко
  Chapter: '3.1'
---
```

---

### 3.3 `ua_verb` — Verb Conjugation Tables *(Phase 2)*

Full conjugation paradigm for a single verb pair. Designed for the
`UA::Recognition::Conjugation` and `UA::Production::Conjugation` decks.
Design deferred until the vocab pipeline is running.

Likely fields: `NoteID`, `Infinitive`, `Perfective`, `ConjTable` (HTML),
`PastTable`, `VerbClass`, `Notes`, `SourceDocument`, `Chapter`.

---

## 4. Deck Architecture

The existing `UA::` hierarchy is preserved and extended:

```
UA::Recognition::UA→EN          ← ua_vocab  (card: UA→EN)
UA::Recognition::Lexeme         ← future: inflected form → lemma
UA::Recognition::Grammar        ← ua_grammar  (cloze)
UA::Recognition::Conjugation    ← ua_verb  (Phase 2)
UA::Production::EN→UA::Typing   ← ua_vocab  (card: EN→UA Typing)
UA::Production::EN→UA::Mobile   ← ua_vocab  (card: EN→UA MCQ — Phase 2)
UA::Production::Conjugation     ← ua_verb  (Phase 2)
UA::Production::Comparatives    ← ua_grammar variant  (Phase 2)
```

> The `Ukrainian Active::Яблуко` and `Inactive::Ukrainian Inactive::*` decks
> hold the legacy cards. Migrated notes will land in the `UA::` decks; legacy
> decks are deleted card-by-card as migration is confirmed.

---

## 5. File and ID Conventions

**Directory layout:**

```
domains/ua/anki/
  notes/
    lexemes/             ← ua_lexeme notes, grouped by source/chapter
      yabluko-l1/        ← Яблуко Level 1
        ua-lexeme-0001.md
        ...
      yabluko-l2/        ← Яблуко Level 2
        ...
      shevchuk/
        ...
    grammar/             ← ua_grammar notes
      ua-grammar-0001.md
      ...
    verbs/               ← ua_verb notes (Phase 2)
  sources/
    yabluko/
      level-1/
        yabluko-l1-sb-front.pdf
        yabluko-l1-sb-vstup-u01-u04.pdf
        yabluko-l1-sb-u05-u08.pdf
        yabluko-l1-sb-u09-u12.pdf
        yabluko-l1-sb-appendix.pdf   ← Перевірте себе (p.20+) + grammar ref + tables
        yabluko-l1-wb-full.pdf
      level-2/                        ← PDF not yet available
      level-3/
  docs/
    design.md            ← this file
```

All paths use ASCII. Ukrainian text (яблуко, etc.) belongs inside files only —
frontmatter, field values, and Anki tags — never in filenames or directory names.

### Key sources in the Level 1 appendix

| Section | Appendix PDF page | Content | Primary use |
|---|---|---|---|
| Перевірте себе | 20–37 | All active vocab per lesson, stress-marked; gender/plural/case hints inline | Primary `ua_lexeme` extraction source; stress pre-verified, chapter known |
| Граматичний довідник | 38–57 | Grammar rules + bilingual headers + textbook examples | `ua_grammar` cloze notes |
| Таблиці — Видові пари дієслів | 58–61 | Complete IPFV/PFV pairs, conjugation class, case government | Bulk-fills `AspectPair_IPFV/PFV` and `Govt_Case` |
| Таблиці — Дієвідміна дієслів | 57–58 | All verbs with conjugation class I/II | Fills conjugation class in `Morphology_Note` |
| Таблиці — Дієслова руху | 57 | Det/indet motion verb pairs | Fills `VerbMotion_Pair` |

### Grammar note design principles

- One note per **grammatical concept**, not per table row
- Full declension paradigm = one `ua_grammar` note with multiple `{{c1::}}` deletions
- Textbook examples go in `Extra`; the rule/pattern goes in `Text`
- Grammar reference section numbers (e.g. `2.2`, `3.1`) map to `Chapter` field and `ch:1.x` tags

**Note IDs:**
- `ua-lexeme-NNNN` — four-digit zero-padded, sequential
- `ua-grammar-NNNN`
- `ua-verb-NNNN`

**Filename:** matches note ID, e.g. `ua-lexeme-0042.md`.

---

## 6. Tagging Conventions

```
domain:ua
topic:vocabulary | topic:grammar | topic:verb
textbook:яблуко | textbook:shevchuk | textbook:other
ch:<level>.<chapter>.<section>   e.g. ch:2.8.2 = Яблуко Level 2, Ch. 8, §2
pos:noun | pos:verb | pos:adjective | pos:adverb | pos:phrase | pos:other
aspect:imperfective | aspect:perfective | aspect:both
gender:m | gender:f | gender:n | gender:pl
motion:det | motion:indet              for motion verb pairs
grammar:<topic>            e.g. grammar:verb_past, grammar:genitive
stress:unverified          when stress marks have not been checked against ULIF/Горох
status:draft | status:verified
```

`status:draft` notes import into Anki as **suspended** cards (same convention
as B737 SV). `status:verified` import as active.

---

## 7. Migration Plan

Migration is a background task, not a prerequisite for starting new content.
New notes authored from scratch use this schema immediately.

### Phase 0 — Leech triage (before migration)
788 leeches (20%) should be reviewed in Anki before being migrated. Options:
delete, suspend, or flag for enrichment. Migrating broken cards into canonical
format wastes effort.

### Phase 1 — Lexeme pipeline (current)
1. Define `UA_Lexeme` and `UA_Grammar` note types in Anki
   (script: `tools/anki/setup/setup_ua_note_types.py` — *to be written*)
2. Extract "Перевірте себе" (appendix p.20+) → skeleton `ua_lexeme` notes, reading
   the PDF chapter by chapter; add `EN_Gloss` by hand or via tutor review
3. Build `make ua-lexeme` target: `ua_lexeme_md_to_tsv.py` → `ua_lexeme_import.py`
4. Validate round-trip on a small batch (~20 notes from Вступ)

### Phase 2 — Bulk migration
Write `tools/anki/extract/export_ua_legacy.py` to pull existing Basic/Cloze
cards from Anki and generate CNSF skeleton files. User then enriches skeletons
(add PoS, gender, stress marks where missing, example sentences) before
re-importing.

Priority order for migration:
1. `to_convert` tagged (13) — already flagged by user
2. `Inactive::Ukrainian Inactive::Vocabulary::Shevchuk` — small, contained
3. `Ukrainian Active::Яблуко` — largest; tackle chapter by chapter
4. Grammar/cloze cards — last, most labour-intensive

### Phase 3 — Verb conjugation
Design and implement `ua_verb` note type and conjugation card templates.
