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
