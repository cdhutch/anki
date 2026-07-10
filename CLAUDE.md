# CLAUDE.md — Anki Project Context (B737 + Ukrainian)

**Current work**: Distractor authoring (Phase A), 26/29 systems verified.

See **[CLAUDE-active-status.md](CLAUDE-active-status.md)** for queue and last session.

## Workflow Notes

This repo builds and maintains Anki flashcard decks for two domains:

- **B737** (`domains/b737/`) — type rating study. CNSF markdown notes exported
  to TSV and imported via AnkiConnect.
- **Ukrainian** (`domains/ua/`) — formal language learning (Galician/Lviv
  register, Яблуко textbook). In early design phase on branch `feature/ua-domain`.
  See `domains/ua/anki/docs/design.md` for full schema and migration plan.

- **Shell commands are run by Craig**, not Claude. Claude provides commands to copy/paste; it does not execute git, make, or Python commands directly. (Claude's sandbox lacks access to the required conda env and git hooks will fail.)
- **Pull requests**: Claude provides the `gh pr create` command; Craig runs it and completes the PR on the GitHub website.

## Reference Files

| Topic | File |
|-------|------|
| **SV field spec** | [CLAUDE-sv-field-conventions.md](CLAUDE-sv-field-conventions.md) |
| **Deck architecture** | [CLAUDE-deck-architecture.md](CLAUDE-deck-architecture.md) |
| **Known issues** | [CLAUDE-known-issues.md](CLAUDE-known-issues.md) |
| **Key paths** | [CLAUDE-key-paths.md](CLAUDE-key-paths.md) |
| **Migration progress** | [CLAUDE-migration-log.md](CLAUDE-migration-log.md) |

---

## Ukrainian Domain (`domains/ua/`)

**Branch:** `feature/ua-domain` (based off `main`)

**Status (as of 2026-07-10):** Вступ (ch-00) complete — 113 notes live, stress verified, examples added.
Book 2 Ch. 9 in progress on branch `feature/ua-l2-ch09-motion-verbs`:
  - 18 UA_Lexeme notes authored (ua-lexeme-0114–0131): prefixed walking + vehicle motion verbs.
  - 7 UA_Grammar cloze notes authored (ua-grammar-0001–0007): two-group rule, aspect formation,
    prefix meanings, phonetic changes, apostrophe rule, піти and ходити meanings.
  - 9 UA_Visual notes authored (ua-visual-0001–0009): one per prefix, inline SVG diagrams,
    spatial meaning + prepositional government. Two cards each (Spatial→UA, UA→Spatial).
    Notes in `domains/ua/anki/notes/visual/`.
  - All new notes: `status:draft`. Stresses Горох-verified; `stress:unverified` tag removed.
  - `Verb_Conj_Table` fully populated for all 18 verb pairs (0114–0131).

**UA_Visual card template design (2026-07-10):**
  - Card 1 (Spatial→UA): front = diagram + English meaning; back = Ukrainian prefix, government, verb pairs, example.
  - Card 2 (UA→Spatial): front = Ukrainian prefix + verb pairs; back = diagram + English meaning + government + example.
  - Template redesign fixed & deployed ✅ — `setup_ua_note_types.py` now calls `updateModelTemplates` with all templates in single call (not per-template loop).
  - Templates update correctly via `make ua-setup-visual`.

**Pending before import:**
  1. ✓ Template fix committed & verified
  2. Run: `make ua-setup` (updates UA_Lexeme + UA_Grammar + UA_Visual in Anki with fixed templates)
  3. Flip `status:draft` → `status:verified` after review
  4. Import lexemes: `make ua-batch BATCH=yabluko-l2/ch-09`
  5. Import grammar: `make ua-grammar`
  6. Import visual prefix cards: `make ua-visual`

### Current Anki state
- 3,932 existing Ukrainian notes in vanilla Basic / Basic+reversed / Cloze types
- 788 leeches (20%) — triage before bulk migration
- Active deck hierarchy: `UA::Recognition::*` / `UA::Production::*`
- New canonical decks: `UA::Recognition::UA→EN` / `UA::Production::EN→UA`
- Legacy decks: `Ukrainian Active::Яблуко`, `Inactive::Ukrainian Inactive::*`
- Tags in use: `textbook:яблуко`, `ch:2.8.x` (= Level 2, Ch. 8, §x), `leech`, `converted`, `to_convert`

### Primary note type: `UA_Lexeme`

**Fields (authoritative):**
`NoteID`, `Lemma`, `PartOfSpeech`, `Gender`, `Perfective`, `EN_Gloss`,
`Govt_Case`, `CounterpartForm`, `IrregularForms`, `VerbMotion_Pair`,
`ConfusableSet`, `CrossLang_Analog`, `EuphonyNote`, `TypingAnswer`,
`UA_Example`, `EN_Example`, `Verb_Conj_Table`, `Tags_Ch`,
`Source_URL`, `Source_Note`

Key field notes:
- `Perfective` — PFV infinitive for verbs (blank for non-verbs)
- `CounterpartForm` — cross-gender pair, e.g. `f: акто́рка`
- `IrregularForms` — gen/pl irregularities, indeclinability
- `TypingAnswer` — Lemma stripped of stress marks (U+0301); student types without accents
- `Source_URL` — goroh.pp.ua URL for the bare lemma: `https://goroh.pp.ua/Словозміна/<lemma_no_stress>`
- `Source_Note` — free text: verification date, disambiguation notes, corrections applied

### Language conventions (critical)
- Dialect: modern Ukrainian, **Galician/Lviv** register
- Apostrophe: **U+02BC `ʼ`** — never ASCII `'`
- Stress marks: **never guess** — verify against Горох (goroh.pp.ua) via Claude in Chrome.
  Tag unverified with `stress:unverified`. Remove tag only after Горох confirms.
- Stress disambiguation: some words have stress-dependent meanings (e.g. му́зика = music,
  музи́ка = musician). Always check before "correcting" based on Горох alone.
- `сь` after vowels preferred (дивлюсь, вчусь) — preserve unless correcting
- Grammar explanations always in English

### Stress verification workflow (established)

Горох Словозміна (`goroh.pp.ua/Словозміна/<word>`) returns the full inflection paradigm
with stress marks. Accessible via Claude in Chrome (not via web_fetch — blocked).

Batch verification process:
1. Extract lemmas from notes (Python, strip stress to get bare form)
2. Fetch Горох pages in batch via Chrome JS `Promise.all` (30 at a time to avoid truncation)
3. Strip phonetic markers from Горох output: remove `<sup>...</sup>` WITH content,
   backtick, apostrophe, colons, `{дз}`/`{дж}` → keep content, `ў` stays as non-vowel
4. Compare vowel-index of stress in lemma vs Горох form; flag mismatches
5. Apply corrections; keep `stress:unverified` tag until user confirms

Important: Горох returns the **masculine adjective** form for adjectives (e.g. `-ський`
instead of `-ська`). The vowel-index comparison handles this correctly since the stressed
syllable is the same. The script is embedded in session context — rebuild from the pattern
in `tools/anki/inspect/` when needed as a standalone tool.

### Tooling status
| Path | Status | Purpose |
|---|---|---|
| Rename `UA` → `UA_Legacy` in Anki GUI | ✓ done | One-time manual rename; frees UA:: namespace |
| `tools/anki/setup/setup_ua_note_types.py` | ✓ done | Creates/updates UA_Lexeme + UA_Grammar + UA_Visual |
| `tools/anki/sync/ua_lexeme_import.py` | ✓ done | CNSF notes → Anki via AnkiConnect (upsert) |
| `tools/anki/sync/ua_grammar_import.py` | ✓ done | UA_Grammar CNSF notes → Anki (upsert) |
| `tools/anki/sync/ua_visual_import.py` | ✓ done | UA_Visual CNSF notes → Anki (upsert) |
| `tools/anki/extract/gen_ua_lexemes_vstup.py` | ✓ done | One-shot generator for Вступ batch |
| `tools/anki/inspect/backfill_source_url.py` | ✓ done | Add Source_URL + Source_Note to all lexeme notes |
| `tools/anki/inspect/verify_stress_goroh.py` | ✓ done | Stress verification vs Горох; Вступ pass complete |
| `tools/anki/generate/ua_generate_examples.py` | ✓ done | Populate UA_Example/EN_Example via Anthropic API |
| `tools/anki/inspect/patch_ch09_conj_tables.py` | ✓ done | One-shot: Verb_Conj_Table for notes 0117–0131 |
| `tools/anki/export/ua_lexeme_md_to_tsv.py` | not written | Canonical notes → TSV (if needed) |
| `tools/anki/extract/export_ua_legacy.py` | not written | Pull existing Anki cards → CNSF skeletons |

### Future work

**UA_Verb dedicated conjugation cards** (Phase 2, design decided 2026-07-07) —
Separate `UA_Verb` note type for active conjugation drill. Key decisions:

- **Not 1:1 with lexeme notes.** Ukrainian conjugation is a pattern skill; drilling
  every prefixed variant individually has diminishing returns once the class pattern
  is internalized. The `<details>` collapsible on the lexeme card back (Verb_Conj_Table)
  covers reference lookup for all verbs.
- **Option B architecture:** individual conjugation forms stored as YAML fields on
  UA_Verb notes (not as an HTML blob). The UA_Verb importer generates the
  `Verb_Conj_Table` HTML and pushes it to the linked UA_Lexeme note. Canonical
  data lives in structured YAML; HTML is a generated cache. `LexemeRef` field on
  UA_Verb links back bidirectionally.
- **Suspended by default on import** (`conj:suspended` tag); active drill is opt-in.
- **~90–100 cards unsuspended total**, across three tiers:
  1. *Class model leaders* (~20–25): one representative per conjugation pattern
     (ходити, іти, писати, читати, класти, стояти, їхати, казати, …). These teach
     the patterns everything else inherits.
  2. *Irregular verbs* (~30–40): forms that can't be derived from the class pattern
     (бути, дати, їсти, взяти, піти, стати, лягти, сісти, …).
  3. *High-frequency regulars* (~30–50): frequent verbs where active production
     practice earns its keep regardless of regularity; driven by Ukrainian National
     Corpus frequency list intersected with Яблуко vocabulary.
- **`conj:drill` tag** marks intentionally unsuspended cards.
- See `domains/ua/anki/docs/design.md` §3.3 for full schema and template spec.

**UA_Verb scope and sequencing** (decided 2026-07-08) —
*501 Ukrainian Verbs* (book) used as breadth/coverage map, not a to-do list.

- **Phase 2a** — Author all irregulars + class model leaders (~60–70 notes). These
  are the structural skeleton of Ukrainian conjugation; unsuspend all of them.
- **Phase 2b** — Cross-reference Яблуко vocabulary against Ukrainian National Corpus
  frequency list; author the high-frequency intersection (~60–100 additional notes).
  Unsuspend selectively.
- **Phase 2c (ongoing)** — Add from *501 Ukrainian Verbs* as curriculum demands,
  using the book as a checklist for conjugation class coverage. Target total:
  ~160–220 authored notes, ~90–100 unsuspended.
- Verb_Conj_Table HTML on UA_Lexeme notes without a UA_Verb companion remains
  hand-authored (as in ch-09) until Phase 2a/2b coverage reaches those verbs.

**LLM example sentence generation** — `tools/anki/generate/ua_generate_examples.py` ✓ written.
Run with `make ua-generate-examples BATCH=yabluko-l1/ch-00 [LIMIT=10]`.
Requires `ANTHROPIC_API_KEY` env var and `pip install anthropic`.
Generated examples tagged `example:generated` until reviewed; then remove tag.

Alternative: **extract examples from the Яблуко textbook PDF directly** — higher
authenticity than generated examples and no hallucination risk. The Level 1 PDF is
at `domains/ua/anki/sources/yabluko/level-1/`. Would require OCR/extraction tooling
and per-lemma lookup; feasible as a future enrichment pass to replace or supplement
generated examples.

**Unit 1–12 lexeme generation** — follow the pattern of `gen_ua_lexemes_vstup.py`,
extracting vocab from Яблуко appendix pages 220–237 unit by unit.

**Legacy card migration** — write `export_ua_legacy.py` to pull existing Basic/Cloze
cards from Anki and generate CNSF skeletons. Enrich with PoS, gender, stress marks
before re-importing. Priority: `to_convert` tagged (13) → Shevchuk → Яблуко ch-by-ch.

### Source materials
| Path | Purpose |
|---|---|
| `domains/ua/anki/sources/yabluko/level-1/` | Яблуко Level 1 PDF (good copy available) |
| `domains/ua/anki/sources/yabluko/level-2/` | Яблуко Level 2 PDF (most existing cards are ch:2.x.x — PDF not yet available) |
| `domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/` | 113 ua_lexeme notes — Вступ (= ch-00) |
| `domains/ua/anki/notes/grammar/` | ua_grammar canonical notes (not yet populated) |
| `domains/ua/anki/docs/design.md` | Full schema, deck architecture, migration plan |
| `tools/anki/inspect/survey_ukrainian.py` | AnkiConnect survey script |
