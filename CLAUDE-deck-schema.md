# Deck Schema & Architecture Reference

## SV Exam Field Conventions

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

**Rules:**
- Correct choice cycles B → C → D → A → B... per note within each system
- T/F questions use format:mcq with Choice A: 'True', Choice B: 'False', Correct Choice: A|B, Shuffle Choices: false

---

## Deck Architecture

Never study from `B737` (root) directly — it bypasses pool limits.

### Pool 1 — Systems (study from `B737::Systems`)

**Preset: B737 Systems (FSRS)** — 40 new/day
- `B737::Systems::Aircraft_Systems` (General systems)
  - `B737::Systems::Aircraft_Systems::Electrical`
  - `B737::Systems::Aircraft_Systems::Engines`

**Preset: B737 Systems SV (FSRS)** — 40 new/day
- `B737::Systems::SV` (Systems Verification MCQ/TF)

### Pool 2 — Core (study from `B737::Core`)

**Preset: B737 FSRS Core** — 20 new/day
- `B737::Core::Limits` (Weight, speed, engine limits + Non-Trivia/Trivia)
- `B737::Core::QRC` (QRC recall notes)
- `B737::Core::Triggers_and_Flows` (Triggers, Flows, Supplemental)
- `B737::Core::Procedures` (Normal, Non_Normal, Inflight_Maneuvers)

---

## Study Stage System

**Script**: `tools/anki/sync/set_stage.py`

**Behavior:**
- Active decks: suspended new cards → unsuspended
- Inactive decks: ALL unsuspended cards → suspended (FSRS history preserved)
- Seat filter: suppress opposite crew role
- Flow sequence filter: `type:flow_sequence` always suspended (unless `always_show`)
- Override tags (applied last):
  - `always_show` — unsuspend regardless
  - `always_hide` — suspend regardless
  - Both present → `always_show` wins

**Stage definitions:**
1. Limits::Non-Trivia, QRC, Triggers_and_Flows::Triggers
2. Stage 1 + Triggers_and_Flows::Flows + Supplemental
3. Stage 2 + Procedures::Normal
4. Stage 3 + Procedures::Non_Normal + Inflight_Maneuvers
5. Stage 4 + Limits::Trivia (full Core)

**Seat options:** `fo` (default, suppresses captain), `captain` (suppresses FO)

**Usage:**
```bash
python tools/anki/sync/set_stage.py --dry-run --stage 2
python tools/anki/sync/set_stage.py --stage 2              # FO seat
python tools/anki/sync/set_stage.py --stage 2 --seat captain
```

---

## Flow Bookend Notes

Each flow has a `*-bookends.md` companion asking for first + last action only.
Tagged `always_show` so they remain active at all stages.

**Naming convention:**
- `flow-fo-<name>-bookends.md` (FO flows)
- `flow-pm-<name>-bookends.md` / `flow-pf-<name>-bookends.md` (PM/PF flows)
- `flow-<name>-bookends.md` (joint/shared flows)

Single-item flows use "Only action:" on the back.
