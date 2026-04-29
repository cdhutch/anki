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

The following 9 systems were converted in the last session and are **staged but not yet committed**
(a stale `.git/index.lock` blocked the commit — remove it first):

```bash
rm /Users/craig/Documents/GitHub/anki/.git/index.lock   # if it still exists

git add domains/b737/anki/notes/systems_verification/fuel/
git commit -m "chore(b737): convert fuel SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/pneumatics/
git commit -m "chore(b737): convert pneumatics SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/autoflight/
git commit -m "chore(b737): convert autoflight SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/air_conditioning/
git commit -m "chore(b737): convert air_conditioning SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/flight_warning/
git commit -m "chore(b737): convert flight_warning SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/electrical/
git commit -m "chore(b737): convert electrical SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/hydraulics/
git commit -m "chore(b737): convert hydraulics SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/flight_controls/
git commit -m "chore(b737): convert flight_controls SV notes to exam_draft (blank distractors)"

git add domains/b737/anki/notes/systems_verification/engines/
git commit -m "chore(b737): convert engines SV notes to exam_draft (blank distractors)"
```

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

## Next Steps: Distractor Authoring

Each exam_draft note has three blank choice slots. The next phase is filling in
plausible distractors for each MCQ. This is a human + AI review task.

Suggested order: work through systems alphabetically or by exam priority.

---

## Next Steps: AnkiConnect FSRS Settings

Goal: use AnkiConnect to apply **consistent FSRS settings across all deck presets**
rather than configuring each preset manually in the GUI.

Approach:
1. Use `getDeckConfig` to read an existing preset
2. Modify FSRS fields: `fsrs`, `fsrsWeights`, `desiredRetention`, `fsrsReschedule`
3. Use `saveDeckConfig` to write back to each target preset

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
