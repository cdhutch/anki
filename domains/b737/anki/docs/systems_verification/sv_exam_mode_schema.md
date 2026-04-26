# B737 Systems Verification Exam Mode Schema

## Purpose

The Systems Verification (SV) exam-mode schema converts existing B737 Systems Verification CNSF notes from cloze-style recall into recognition-format cards that match the expected test environment:

- Multiple choice questions using A / B / C / D choices
- True / false questions
- Distractors visible on the front of the card
- Optional shuffling of displayed answer choices
- Back side showing the correct answer and rationale

The goal is not to discard the existing SV note work. The goal is to preserve it as a legacy/source layer, convert it into a richer draft schema, then transform finalized draft notes into import-ready MCQ or T/F notes.

---

# Core Workflow Philosophy

The authoritative source data is the YAML `fields:` block.

Humans should primarily author structured data. AI helpers validate wording and logic. Scripts generate filenames, note IDs, `front_md`, `back_md`, and final transformed notes.

Preferred workflow:

1. Preserve legacy notes.
2. Create minimal draft notes.
3. Human edits question quality and answer choices.
4. AI validates note quality.
5. Scripts normalize numbering and transform notes.
6. Final notes sync into Anki.

---

# Directory Plan

## Legacy copy

The current cloze-style SV notes should be copied unchanged to:

```text
domains/b737/anki/notes/systems_verification_legacy/
```

This preserves the original notes as source material.

## Draft conversion notes

The working conversion notes live in:

```text
domains/b737/anki/notes/systems_verification/
```

During conversion, these notes use:

```yaml
note_type: systems_verification_exam_draft
```

## Final exam-mode notes

Final transformed notes may either replace the draft files in a clean generated directory or be emitted into parallel import-ready folders such as:

```text
domains/b737/anki/notes/systems_verification_exam/mcq/
domains/b737/anki/notes/systems_verification_exam/tf/
```

Recommended final note ID prefixes:

```text
svmcq-<system>-<number>
svtf-<system>-<number>
```

---

# Minimal Authoring Mode (Preferred)

During active note creation, the user may provide only the minimum structured YAML fields required to derive the final note.

Do not require manually authored `# front_md` or `# back_md` in draft notes.

The transformation tool or AI helper should generate card text from structured fields.

Preferred manually authored fields:

- Source Document
- Exam Format
- Conversion Status
- Original Note ID
- Original Prompt Style
- Original Text
- Question Stem
- Choice A
- Choice B
- Choice C
- Choice D
- Correct Choice
- Shuffle Choices
- Review Notes

---

# Temporary Conversion Schema

Use this schema after copying the original cloze notes into the active conversion directory.

## Draft YAML Header

```yaml
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_exam_draft
note_id: svdraft-<system>-<number>
anki:
  model: B737_SV_Exam_Draft
  deck: B737::Systems_Verification::Draft
tags:
  - domain:b737
  - topic:systems_verification
  - system:<system>
  - format:draft
  - source:question_bank
  - status:draft
fields:
  Source Document: <source document name>
  Exam Format: mcq | tf | unset
  Conversion Status: draft | human_ready | ready_for_transform | transformed | imported | hold
  Original Note ID: <legacy note id>
  Original Prompt Style: cloze
  Original Text: <original cloze text>
  Question Stem: <question text>
  Choice A: <text or blank>
  Choice B: <text or blank>
  Choice C: <text or blank>
  Choice D: <text or blank>
  Correct Choice: A | B | C | D | True | False | blank
  Shuffle Choices: true | false
  Review Notes: <notes or blank>
---
```

---

# Draft Field Definitions

| Field | Purpose |
|---|---|
| Source Document | Provenance |
| Exam Format | mcq / tf / unset |
| Conversion Status | Workflow state |
| Original Note ID | Legacy source note |
| Original Prompt Style | Usually cloze |
| Original Text | Original source question/answer |
| Question Stem | Final exam-style prompt |
| Choice A-D | Answer choices for MCQ |
| Correct Choice | Correct option |
| Shuffle Choices | Whether choices may be reordered |
| Review Notes | Human or AI comments |

---

# Generated Content Rule

For draft notes, `front_md` and `back_md` are generated artifacts.

Do not manually maintain them unless specifically debugging templates.

The authoritative source data is the YAML fields block.

---

# Final Multiple Choice Schema

## Final MCQ YAML Header

```yaml
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_mcq
note_id: svmcq-<system>-<number>
anki:
  model: B737_SV_MCQ
  deck: B737::Systems_Verification::Exam_Mode
tags:
  - domain:b737
  - topic:systems_verification
  - system:<system>
  - format:mcq
  - source:question_bank
  - status:unverified
fields:
  Source Document: <source document name>
  Legacy Note ID: <original note id>
  Question Type: multiple_choice
  Shuffle Choices: true
  Correct Choice: <final displayed letter>
  Correct Answer Text: <derived from selected choice>
  Review Notes:
---
```

## Final MCQ Body Template

```markdown
# front_md

**<System Name> — Systems Verification**

<Question Stem>

A. <choice>
B. <choice>
C. <choice>
D. <choice>

# back_md

**Correct Answer:** <letter> — <correct answer text>
```

---

# Final True / False Schema

## Final T/F YAML Header

```yaml
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_tf
note_id: svtf-<system>-<number>
anki:
  model: B737_SV_TF
  deck: B737::Systems_Verification::Exam_Mode
tags:
  - domain:b737
  - topic:systems_verification
  - system:<system>
  - format:true_false
  - source:question_bank
  - status:unverified
fields:
  Source Document: <source document name>
  Legacy Note ID: <original note id>
  Question Type: true_false
  Correct Choice: True | False
  Review Notes:
---
```

## Final T/F Body Template

```markdown
# front_md

**<System Name> — Systems Verification**

True or False:

<statement>

# back_md

**Correct Answer:** True | False
```

---

# Filename and Note ID Normalization

Draft note filenames and note IDs may be temporary during authoring.

Normalization scripts may later:

- renumber notes sequentially
- rename files to match final numbering
- convert `svdraft-*` to `svmcq-*`
- convert `svdraft-*` to `svtf-*`
- reconcile duplicates or gaps

During drafting, content correctness takes priority over numbering.

---

# Transformation Rules

## Draft to Final MCQ

Transform when:

```yaml
Exam Format: mcq
Conversion Status: ready_for_transform
```

Steps:

1. Change `note_type` to `systems_verification_mcq`
2. Rename `note_id` to `svmcq-*`
3. Rename file accordingly
4. Change Anki model/deck
5. Replace `format:draft` with `format:mcq`
6. Generate front/back text
7. If `Shuffle Choices: true`, deterministically shuffle choices
8. Recalculate displayed correct letter
9. Mark note transformed

## Draft to Final T/F

Transform when:

```yaml
Exam Format: tf
Conversion Status: ready_for_transform
```

Steps:

1. Change `note_type` to `systems_verification_tf`
2. Rename `note_id` to `svtf-*`
3. Rename file accordingly
4. Change Anki model/deck
5. Replace `format:draft` with `format:true_false`
6. Generate front/back text
7. Mark note transformed

---

# Validation Checklist

Validate each draft note for:

- Valid YAML syntax
- Required fields present
- Question stem is clear
- Grammar is correct
- Exactly one correct answer (MCQ)
- Distractors are plausible
- Correct answer matches source text
- No invented aircraft facts
- Numbering may remain temporary
- Ready for transform only when complete

---

# AI Chat Bot Instructions

Use the following guidance when helping with note migration.

## Mission

Convert B737 Systems Verification notes from cloze recall into exam-mode recognition cards while preserving legacy source material.

## Required Behavior

1. Preserve original facts.
2. Do not invent procedures, limitations, or aircraft behavior.
3. Improve wording only when clarity is increased.
4. If uncertain, flag for review instead of guessing.
5. Keep YAML valid.
6. Respect project field ordering.
7. Do not renumber notes manually unless requested.
8. Prefer concise, exam-like wording.
9. Make distractors plausible but clearly incorrect.
10. Keep only one correct answer unless explicitly multi-select.

## Draft Validation Response Style

When validating a note, provide a positive summary:

- YAML valid
- Metadata complete
- Stem clear
- Distractors strong
- Correct answer confirmed
- Ready for transformation

---

# Conversion Status Lifecycle

Use these values consistently:

```yaml
draft
human_ready
ready_for_transform
transformed
imported
hold
```

Definitions:

- draft — initial authored note
- human_ready — reviewed by user
- ready_for_transform — approved for script conversion
- transformed — final note generated
- imported — synced into Anki
- hold — pause for later review

---

# Strategic Git Checkpoints

Recommended commits:

1. docs(b737): define systems verification exam-mode schema
2. chore(b737): preserve legacy systems verification notes
3. feat(b737): add systems verification draft tooling
4. chore(b737): convert systems verification notes to draft schema
5. feat(b737): add systems verification transform tooling
6. feat(b737): generate systems verification exam notes
7. feat(b737): add systems verification import support

---

# Checklist Before Ready for Transform

- [ ] Exam Format set
- [ ] Conversion Status = ready_for_transform
- [ ] Source Document present
- [ ] Question Stem complete
- [ ] Correct answer unambiguous
- [ ] MCQ has four choices
- [ ] T/F has True or False
- [ ] Grammar checked
- [ ] Note validated
