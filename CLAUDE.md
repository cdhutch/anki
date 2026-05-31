# CLAUDE.md — Anki Project Context (B737 + Ukrainian)

Read this file at the start of every session to restore working context.

---

## Project Overview

This repo builds and maintains Anki flashcard decks for two domains:

- **B737** (`domains/b737/`) — type rating study. CNSF markdown notes exported
  to TSV and imported via AnkiConnect.
- **Ukrainian** (`domains/ua/`) — formal language learning (Galician/Lviv
  register, Яблуко textbook). In early design phase on branch `feature/ua-domain`.
  See `domains/ua/anki/docs/design.md` for full schema and migration plan.

---

## Current Focus: Distractor Authoring + Anki Migration

### Phase A: Distractor authoring (ongoing)

All 29 SV systems are converted to `systems_verification_exam_draft` MCQ format.
Distractors are being authored system-by-system. Workflow per system:

1. User authors distractors directly in the `.md` files
2. User calls Claude back for review, grammar/typo fixes, and any clarifications
3. Run `make sve-fix` to canonicalize
4. Claude provides `git add` + `git commit` commands
5. Move to next system

**Distractor authoring status (as of 2026-05-25):**

| Status | Systems |
|---|---|
| Finalized (`note_type: systems_verification_exam`) | acars, adverse, emergency_equipment |
| All distractors complete (`status:verified`) | acars, adverse, air_conditioning, apu, atc_tcas_trans, communications, electrical, emergency_equipment, fire_protection, flight_controls, flight_instrumentation, flight_warning, fuel, general, gpws, hud, hydraulics, ice_and_rain_protection, landing_gear, lighting, navigation, oxygen, performance, pressurization, weather_radar |
| Partially complete — T/F/2-choice blanks only | fms (sv-fms-024 is intentional 2-choice; all others verified) |
| Distractors not yet authored (`status:draft`) | autoflight, engines, pneumatics |

Note: `status:draft` notes import into Anki as **suspended** cards. `status:verified` import as active.

**Remaining distractor queue (draft count, smallest-first):**

| System | Total | Draft |
|---|---|---|
| engines | 41 | 39 |
| autoflight | 42 | 39 |
| pneumatics | 39 | 39 |

---

### Phase B: Anki migration (in progress — paused mid-execution)

Goal: replace 688 legacy `B737_SV_Cloze` cards in Anki with new `B737_SV_MCQ` /
`B737_SV_TF` cards, using a dedicated FSRS deck preset.

**Migration run order (Anki must be open, AnkiConnect active):**

#### Step 1 — Create note types in Anki (COMPLETED by user this session)
Fields and card templates for `B737_SV_MCQ` and `B737_SV_TF` were provided and
manually created in Anki by the user.

- `B737_SV_MCQ` fields: NoteID, Text, Source Document, OriginalNoteID, Choice1–4, CorrectChoice
- `B737_SV_TF` fields: NoteID, Text, Source Document, OriginalNoteID, CorrectAnswer
- Script (idempotent, for future reference): `tools/anki/setup/update_sv_exam_templates.py`

#### Step 2 — Create "B737 SV Exam" deck preset (COMPLETED)

Script: `tools/anki/setup/create_sv_exam_preset.py`

Settings: 100 new/day · 9999 reviews/day · FSRS on · 90% desired retention

Preset created and applied to `B737::Systems::SV::MCQ` and `B737::Systems::SV::TF`.

Note: if run multiple times, duplicate presets named "B737 SV Exam" will appear —
remove extras via Tools → Manage Deck Presets in Anki.

#### Step 3 — Delete legacy cloze notes

```bash
python tools/anki/setup/delete_sv_cloze.py --dry-run   # verify count first
python tools/anki/setup/delete_sv_cloze.py              # type 'yes' to confirm
```

Deletes all `B737_SV_Cloze` notes and removes the empty `B737::Systems::SV` deck.

#### Step 4 — Import new MCQ cards (COMPLETED)

```bash
make sve
```

All systems imported. `status:draft` cards import suspended; `status:verified` import active.
Use `make sve-<system>` after completing distractors for a single system.

#### Step 5 — Verify in Anki (COMPLETED)

`note:B737_SV_MCQ` confirmed in Anki. "B737 SV Exam" preset applied to MCQ and TF decks.

---

## Flags for Human Review (RESOLVED)

| File | Issue | Resolution |
|---|---|---|
| `hydraulics/sv-hydraulics-037.md` | Blank source answer | Filled: 3000 psi |
| `autoflight/sv-autoflight-17.md` | "10 degrees nose down" — correct? | Confirmed correct (first ~90 kts of takeoff roll) |

---

## Exam Draft Field Conventions

```yaml
note_type: systems_verification_exam_draft
note_id: sv-<system>-<NNN>
anki:
  model: B737_SV_Exam_Draft
  deck: B737::Systems_Verification::Draft
tags:
  - domain:b737
  - topic:systems_verification
  - system:<system>
  - format:mcq
  - source:question_bank
  - status:draft
fields:
  Source Document: Systems Validation Question Bank
  Exam Format: mcq
  Conversion Status: draft
  Original Note ID: <system>-<NNN>
  Original Prompt Style: cloze
  Original Text: <original cloze text preserved verbatim>
  Question Stem: <human-readable question>
  Choice A/B/C/D: <one contains the answer, rest are ''>
  Correct Choice: A | B | C | D
  Shuffle Choices: true
  Review Notes: <null or flag>
  Verification Notes: ''
```

Correct choice cycles B → C → D → A → B... per note within each system.

T/F questions use format:mcq with Choice A: 'True', Choice B: 'False',
Correct Choice: A or B, Shuffle Choices: false.

---

## Deck Architecture (as of 2026-05-01)

The B737 decks are organised into two independent study pools, each with its own
daily new-card budget. Never study from `B737` (root) directly — it bypasses the
pool limits.

### Pool 1 — Systems (study from `B737::Systems`)

Preset: **B737 Systems (FSRS)** — 40 new/day

| Deck | Content |
|---|---|
| `B737::Systems::Aircraft_Systems` | General systems knowledge (Electrical, Engines sub-decks) |
| `B737::Systems::Aircraft_Systems::Electrical` | Electrical system cards |
| `B737::Systems::Aircraft_Systems::Engines` | Engines cards |

Preset: **B737 Systems SV (FSRS)** — 40 new/day (separate for now, tune later)

| Deck | Content |
|---|---|
| `B737::Systems::SV` | Systems Verification cloze notes |

### Pool 2 — Core (study from `B737::Core`)

Preset: **B737 FSRS Core** — 20 new/day

| Deck | Content |
|---|---|
| `B737::Core::Limits` | Weight, speed, engine limits (+ Non-Trivia / Trivia sub-decks) |
| `B737::Core::QRC` | QRC recall notes |
| `B737::Core::Triggers_and_Flows` | Triggers, Flows, Supplemental (mnemonics, sequences, phase-recalls) |
| `B737::Core::Procedures` | Normal, Non_Normal, Inflight_Maneuvers sub-decks |

### Supplemental deck

`B737::Core::Triggers_and_Flows::Supplemental` exists in Anki with the **B737 FSRS Core**
preset assigned. The 40 source notes (mnemonics, sequences, phase-recalls) have their
deck paths corrected and are ready to sync via `make triggers`.

### Staged card script

`tools/anki/sync/set_stage.py` activates/deactivates Core decks by study stage.

- **Active decks**: suspended new cards are unsuspended.
- **Inactive decks**: ALL unsuspended cards (any state — new, learning, review)
  are suspended. FSRS history is preserved; cards resume from where they left off
  when the deck is reactivated.
- **Seat filter**: suspends all cards tagged for the opposite crew role across all
  B737 decks (including review/learning cards).
- **Flow sequence filter**: `type:flow_sequence` cards are always suspended
  regardless of stage (unless tagged `always_show`).
- **Override tags** (applied last, beat everything else):
  - `always_show` — unsuspend card regardless of stage or seat
  - `always_hide` — suspend card regardless of stage or seat
  - If both tags present, `always_show` wins.

Stage definitions:
- Stage 1: Limits::Non-Trivia, QRC, Triggers_and_Flows::Triggers
- Stage 2: Stage 1 + Triggers_and_Flows::Flows + Triggers_and_Flows::Supplemental
- Stage 3: Stage 2 + Procedures::Normal
- Stage 4: Stage 3 + Procedures::Non_Normal + Procedures::Inflight_Maneuvers
- Stage 5: Stage 4 + Limits::Trivia (full Core)

Seat options: `fo` (default) — suppresses `crew_role:captain` cards;
`captain` — suppresses `crew_role:first_officer` cards.
`crew_role:pilot_flying` and `crew_role:pilot_monitoring` are never suppressed.

Usage (with Anki open + AnkiConnect running):
```bash
python tools/anki/sync/set_stage.py --dry-run --stage 2
python tools/anki/sync/set_stage.py --stage 2              # FO seat (default)
python tools/anki/sync/set_stage.py --stage 2 --seat captain
```

### Flow bookend notes

Each flow has a companion `*-bookends.md` note in `triggers_and_flows/` that
asks for the first and last action only. These are tagged `always_show` so they
remain active at all stages. Single-item flows use "Only action:" on the back.

Filename convention: `flow-fo-<name>-bookends.md` for FO flows,
`flow-pm-<name>-bookends.md` / `flow-pf-<name>-bookends.md` for PM/PF flows,
`flow-<name>-bookends.md` for joint (shared) flows.

### Flow detail filter script (retired)

`tools/anki/sync/set_flow_detail.py` is superseded by `set_stage.py`.
The `always_show` / `always_hide` override tags in `set_stage.py` replace
its functionality. The file is kept for reference but should not be used.

---

## Known Tooling Notes

- `make sve-fix` runs `cnsf_canonicalize.py --write` — fixes YAML formatting
- YAML boolean coercion bug (True/False → true/false): fixed in `_normalize_meta()`
  in `tools/anki/cnsf_canonicalize.py`
- YAML colon-at-end-of-value bug: any field value ending in `:` must be quoted
  in single quotes, e.g. `Question Stem: 'You must select ALTN, then:'`
- `tools/anki/setup/fix_conflict_markers.py`: strips git conflict markers from
  working tree files, keeping HEAD (ours) content — created for post-merge cleanup
- AnkiConnect action `getDeckConfigs` (plural) does NOT exist — use `cloneDeckConfigId`
  + `setDeckConfigId` (apply to temp deck) + `getDeckConfig` + `saveDeckConfig`
- `sv_exam_md_to_tsv.py`: per-note errors no longer crash the run; all failures reported
  at end with note path and error message, exit code 1 if any errors occurred
- `sv_exam_md_to_tsv.py`: `_s()` helper fixed to handle falsy non-None values (e.g. `0`)
- `delete_sv_cloze.py`: generalised with `--model` flag (default: B737_SV_Cloze)

---

## Key Paths

| Path | Purpose |
|---|---|
| `domains/b737/anki/notes/systems_verification/` | SV note source files |
| `domains/b737/anki/docs/systems_verification/sv_exam_mode_schema.md` | Full schema spec |
| `build/` | Generated TSV output files |
| `tools/anki/export/sv_exam_md_to_tsv.py` | Converts exam_draft notes → TSV |
| `tools/anki/sync/sv_exam_import_to_anki.py` | Imports TSV into Anki via AnkiConnect |
| `tools/anki/setup/create_sv_exam_preset.py` | Creates "B737 SV Exam" deck preset |
| `tools/anki/setup/delete_sv_cloze.py` | Deletes all legacy B737_SV_Cloze notes |
| `tools/anki/setup/update_sv_exam_templates.py` | Creates B737_SV_MCQ / B737_SV_TF note types |
| `tools/anki/sync/set_stage.py` | Activate/deactivate Core decks by study stage; seat filter; always_show/always_hide overrides |
| `tools/anki/sync/set_flow_detail.py` | Retired — superseded by set_stage.py override tags |
| `domains/b737/anki/notes/triggers_and_flows/*-bookends.md` | Flow bookend notes (first/last action per flow; always_show) |

---

## Ukrainian Domain (`domains/ua/`)

**Branch:** `feature/ua-domain` (based off `main`)

**Status (as of 2026-05-31):** Вступ lexeme batch complete. 113 notes live in Anki
(`UA::Canonical::Recognition::UA→EN` and `UA::Canonical::Production::EN→UA`).
Stress marks verified against Горох; 9 corrections applied. All notes still tagged
`stress:unverified` pending a full re-import after user review of outstanding edge cases.

### Current Anki state
- 3,932 existing Ukrainian notes in vanilla Basic / Basic+reversed / Cloze types
- 788 leeches (20%) — triage before bulk migration
- Active deck hierarchy: `UA::Recognition::*` / `UA::Production::*`
- New canonical decks: `UA::Canonical::Recognition::UA→EN` / `UA::Canonical::Production::EN→UA`
- Legacy decks: `Ukrainian Active::Яблуко`, `Inactive::Ukrainian Inactive::*`
- Tags in use: `textbook:яблуко`, `ch:2.8.x` (= Level 2, Ch. 8, §x), `leech`, `converted`, `to_convert`

### Primary note type: `UA_Lexeme`

**Actual fields (as implemented — differs slightly from design.md v1):**
`NoteID`, `Lemma`, `PartOfSpeech`, `Gender`, `Perfective`, `EN_Gloss`,
`Govt_Case`, `CounterpartForm`, `IrregularForms`, `VerbMotion_Pair`,
`ConfusableSet`, `CrossLang_Analog`, `EuphonyNote`, `TypingAnswer`,
`UA_Example`, `EN_Example`, `Verb_Conj_Table`, `Tags_Ch`

Key field notes:
- `Perfective` — PFV infinitive for verbs (blank for non-verbs)
- `CounterpartForm` — cross-gender pair, e.g. `f: акто́рка`
- `IrregularForms` — gen/pl irregularities, indeclinability
- `TypingAnswer` — Lemma stripped of stress marks (U+0301); student types without accents

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

Горох Транскрипція (`goroh.pp.ua/Транскрипція/<word>`) returns phonetic transcription
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
| `tools/anki/setup/setup_ua_note_types.py` | ✓ done | Creates/updates UA_Lexeme in Anki |
| `tools/anki/sync/ua_lexeme_import.py` | ✓ done | CNSF notes → Anki via AnkiConnect (upsert) |
| `tools/anki/extract/gen_ua_lexemes_vstup.py` | ✓ done | One-shot generator for Вступ batch |
| `tools/anki/export/ua_lexeme_md_to_tsv.py` | not written | Canonical notes → TSV (if needed) |
| `tools/anki/extract/export_ua_legacy.py` | not written | Pull existing Anki cards → CNSF skeletons |

### Future work

**LLM example sentence generation** — highest value next step for card quality.
Use Claude API (Haiku for cost) to populate `UA_Example` and `EN_Example` for notes
where these are blank. Inputs per note: `Lemma`, `PartOfSpeech`, `EN_Gloss`, `Govt_Case`.
Prompt must include: Galician/Lviv dialect constraint, apostrophe = U+02BC (ʼ),
no stress marks in output (students type without accents). One natural sentence +
English translation per note. Tag generated examples `example:generated` until reviewed.
Script: `tools/anki/generate/ua_generate_examples.py`.

**Stress verification script** (productionise the session workflow above).
`tools/anki/inspect/verify_stress_goroh.py` — reads all notes tagged `stress:unverified`,
drives Горох via Claude in Chrome, outputs `(note_id, lemma_current, lemma_goroh)` for
mismatches only. After user review and correction, remove `stress:unverified` tags and
re-import with `ua_lexeme_import.py`.

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
| `domains/ua/anki/notes/lexemes/yabluko-l1/vstup/` | 113 ua_lexeme notes — Вступ batch |
| `domains/ua/anki/notes/grammar/` | ua_grammar canonical notes (not yet populated) |
| `domains/ua/anki/docs/design.md` | Full schema, deck architecture, migration plan |
| `tools/anki/inspect/survey_ukrainian.py` | AnkiConnect survey script |
