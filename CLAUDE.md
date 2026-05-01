# CLAUDE.md — B737 Anki Project Context

Read this file at the start of every session to restore working context.

---

## Project Overview

This repo builds and maintains Anki flashcard decks for B737 type rating study.
The primary domain is `domains/b737/`. Cards are authored as CNSF markdown notes,
exported to TSV, and imported into Anki via AnkiConnect or manual import.

---

## Current Focus: Systems Verification (SV) Exam Mode Conversion

### What the conversion does

Converts legacy B737 SV notes from **cloze** format (`note_type: systems_verification`)
to **exam draft** MCQ format (`note_type: systems_verification_exam_draft`).

Source notes live in:
```
domains/b737/anki/notes/systems_verification/<system>/
```

The schema is documented in:
```
domains/b737/anki/docs/systems_verification/sv_exam_mode_schema.md
```

The conversion script is at:
```
outputs/cloze_to_exam_draft.py   ← temporary working dir, recreate if needed
```

### Conversion status (as of 2026-04-28)

All 29 systems are converted. None remain in raw cloze format.

| Status | Systems |
|---|---|
| `systems_verification_exam` (finalized) | acars, adverse, emergency_equipment |
| `systems_verification_exam_draft` (blank distractors, needs review) | all others (26 systems) |

### Uncommitted changes

All 29 systems are committed on `feature/b737-sv-exam-mode`. Nothing pending here.

---

## Flags for Human Review

These notes were edited during the review pass and need a human decision:

| File | Issue |
|---|---|
| `hydraulics/sv-hydraulics-037.md` | Source cloze had blank answer `{{c1::}}` — answer is 3000 psi, needs manual entry |
| `autoflight/sv-autoflight-17.md` | Source says "10 degrees nose down" on TO/GA takeoff — verify against FCOM (likely should be nose UP) |

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

### Pending: Supplemental deck

40 notes reference `B737::Core::Triggers_and_Flows::Supplemental` but that deck
does not yet exist in Anki. Create it and assign the **B737 FSRS Core** preset
before importing those notes.

### Pending: deck-reorganization branch

Branch `feature/deck-reorganization` contains ~1,835 modified note files and
updated tool scripts / docs reflecting the above architecture. Commit and merge
before starting the next workstream.

```bash
# Note: .git/index.lock may be present — remove if git add fails:
# rm /Users/craig/Documents/GitHub/anki/.git/index.lock

git add domains/b737/anki/notes/
git commit -m "chore(b737): update deck paths for Core/Systems pool reorganization"

git add tools/ docs/ CLAUDE.md
git commit -m "chore: update tool scripts and docs for deck reorganization"
```

---

## Next Steps: Distractor Authoring

Each exam_draft note has three blank choice slots. The next phase is filling in
plausible distractors for each MCQ. This is a human + AI review task.

Suggested order: work through systems alphabetically or by exam priority.

---

## Next Steps: AnkiConnect FSRS Settings

Goal: use AnkiConnect to enable FSRS and apply consistent settings across all
four active presets rather than configuring each manually in the GUI.

Target presets (all currently have `fsrs: false`):
- **B737 FSRS Core** (id: 1773449586553) — Core pool, 20 new/day
- **B737 Systems (FSRS)** (id: 1774213424514) — Aircraft_Systems pool, 40 new/day
- **B737 Systems SV (FSRS)** (id: 1777637147023) — SV pool, 40 new/day

Approach:
1. Use `getDeckConfig` to read each preset by id
2. Set `fsrs: true`, `desiredRetention`, `fsrsWeights`, `fsrsReschedule`
3. Use `saveDeckConfig` to write back

Anki version must be 2.1.55+ for FSRS fields to be present in config objects.
The FSRS optimizer (computing weights from review history) is GUI-only and cannot
be driven via AnkiConnect.

AnkiConnect must be running (Anki open, AnkiConnect add-on active, default port 8765).

---

## Key Paths

| Path | Purpose |
|---|---|
| `domains/b737/anki/notes/systems_verification/` | SV note source files |
| `domains/b737/anki/docs/systems_verification/sv_exam_mode_schema.md` | Full schema spec |
| `domains/b737/anki/exports/` | TSV exports for Anki import |
| `build/` | Generated TSV output files |
| `tools/anki/export/sv_exam_md_to_tsv.py` | Converts exam_draft notes → TSV |
| `tools/anki/sync/sv_exam_import_to_anki.py` | Imports TSV into Anki via AnkiConnect |
