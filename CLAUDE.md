# CLAUDE.md — B737 Anki Project Context

Read this file at the start of every session to restore working context.

---

## Project Overview

This repo builds and maintains Anki flashcard decks for B737 type rating study.
The primary domain is `domains/b737/`. Cards are authored as CNSF markdown notes,
exported to TSV, and imported into Anki via AnkiConnect or manual import.

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

**Distractor authoring status (as of 2026-05-10):**

| Status | Systems |
|---|---|
| Finalized (note_type: `systems_verification_exam`) | acars, adverse, emergency_equipment |
| Distractors complete, committed | hud, landing_gear, pressurization |
| Distractors pending | all others (see queue below) |

**Remaining distractor queue (smallest-first):**

| System | ~Notes |
|---|---|
| navigation | 28 |
| fms | 36 |
| fuel | 38 |
| pneumatics | 39 |
| engines | 41 |
| autoflight | 42 |
| air_conditioning | 43 |
| flight_warning | 45 |
| electrical | 47 |
| hydraulics | 50 |
| flight_controls | 52 |

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

#### Step 2 — Create "B737 SV Exam" deck preset (IN PROGRESS)

Script: `tools/anki/setup/create_sv_exam_preset.py`

Settings: 40 new/day · 9999 reviews/day · FSRS on · 90% desired retention

**STATUS: Script was fixed this session (removed invalid `getDeckConfigs` call)
but NOT yet successfully run. Run this first next session:**

```bash
python tools/anki/setup/create_sv_exam_preset.py
```

Applies preset to: `B737::Systems::SV::MCQ` and `B737::Systems::SV::TF`

Note: if run multiple times, duplicate presets named "B737 SV Exam" will appear —
remove extras via Tools → Manage Deck Presets in Anki.

#### Step 3 — Delete legacy cloze notes

```bash
python tools/anki/setup/delete_sv_cloze.py --dry-run   # verify count first
python tools/anki/setup/delete_sv_cloze.py              # type 'yes' to confirm
```

Deletes all `B737_SV_Cloze` notes and removes the empty `B737::Systems::SV` deck.

#### Step 4 — Import new MCQ cards

```bash
make sve
```

Exports TSV from all system directories and pushes to Anki via AnkiConnect.
Cards with blank distractors will import fine; they'll just be incomplete for study.

#### Step 5 — Verify in Anki

In Browse: search `note:B737_SV_MCQ` and confirm card count.
Right-click `B737::Systems::SV::MCQ` → Options → confirm "B737 SV Exam" preset is applied.

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

## Known Tooling Notes

- `make sve-fix` runs `cnsf_canonicalize.py --write` — fixes YAML formatting
- YAML boolean coercion bug (True/False → true/false): fixed in `_normalize_meta()`
  in `tools/anki/cnsf_canonicalize.py`
- YAML colon-at-end-of-value bug: any field value ending in `:` must be quoted
  in single quotes, e.g. `Question Stem: 'You must select ALTN, then:'`
- `tools/anki/setup/fix_conflict_markers.py`: strips git conflict markers from
  working tree files, keeping HEAD (ours) content — created for post-merge cleanup
- AnkiConnect action `getDeckConfigs` (plural) does NOT exist — use `createDeckConfig`
  + `saveDeckConfig` + `setDeckConfigId` for preset management

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
