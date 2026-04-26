# B737 Systems Verification Exam Mode Schema

## Purpose

The Systems Verification (SV) exam-mode schema converts existing B737 Systems Verification CNSF notes from cloze-style recall into recognition-format cards that match the expected test environment:

- Multiple choice questions using A / B / C / D choices
- True / false questions
- Distractors visible on the front of the card
- Optional shuffling of displayed answer choices
- Back side showing the correct answer and explanation

The goal is not to discard the existing SV note work. The goal is to preserve it as a legacy/source layer, convert it into a richer draft schema, then transform finalized draft notes into import-ready MCQ or T/F notes.

---

## Directory Plan

### Legacy copy

The current cloze-style SV notes should be copied unchanged to:

```text
domains/b737/anki/notes/systems_verification_legacy/
```

This preserves the original notes as source material.

### Draft conversion notes

The working conversion notes live in:

```text
domains/b737/anki/notes/systems_verification/
```

During conversion, these notes use:

```yaml
note_type: systems_verification_exam_draft
```

### Final exam-mode notes

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

# Temporary Conversion Schema

Use this schema after copying the original cloze notes into the active conversion directory. This format is intentionally verbose. It is designed to hold the original cloze prompt/answer, the future exam-mode question, the distractors, and a readiness flag.

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
  - source:aom
  - status:draft
fields:
  Source Document: <source document name>
  Source Location: <stable source reference>
  Legacy Note ID: <original sv-* note_id>
  Legacy Note Type: cloze
  Exam Format: mcq | tf | unset
  Conversion Status: legacy_imported | needs_authoring | ready_for_transform | transformed | hold
  Ready For Transform: false
  Shuffle Choices: true | false
  Correct Choice ID: <choice_id or blank>
  Correct Answer: A | B | C | D | True | False | blank
  Difficulty: easy | medium | tricky | unset
  Negative Wording: true | false
  Explanation: <brief explanation or blank>
  Transformation Notes: <notes for AI/human conversion>
---
```

## Required top-level YAML fields

| Field | Required | Expected value |
|---|---:|---|
| `schema` | yes | `cnsf/v0` |
| `domain` | yes | `b737` |
| `note_type` | yes | `systems_verification_exam_draft` |
| `note_id` | yes | `svdraft-<system>-<number>` |
| `anki.model` | yes | `B737_SV_Exam_Draft` |
| `anki.deck` | yes | `B737::Systems_Verification::Draft` |
| `tags` | yes | YAML list of tags |
| `fields` | yes | YAML mapping |

## Required tags for draft notes

```yaml
tags:
  - domain:b737
  - topic:systems_verification
  - system:<system>
  - format:draft
  - source:aom
  - status:draft
```

Recommended system tag values:

```text
system:acars
system:autoflight
system:electrical
system:engines
system:flight_controls
system:fms
system:hud
system:hydraulics
system:ice_and_rain_protection
system:landing_gear
system:navigation
system:weather_radar
```

## Draft field definitions

| Field | Values | Purpose |
|---|---|---|
| `Source Document` | text | Source manual or question-bank reference. |
| `Source Location` | text | Stable section/location reference. Prefer section over page. |
| `Legacy Note ID` | text | Original cloze `note_id`, e.g. `sv-electrical-001`. |
| `Legacy Note Type` | `cloze` | Identifies source format. |
| `Exam Format` | `mcq`, `tf`, `unset` | Final intended card format. |
| `Conversion Status` | `legacy_imported`, `needs_authoring`, `ready_for_transform`, `transformed`, `hold` | Workflow state. |
| `Ready For Transform` | `true`, `false` | Machine-readable gate. Only `true` notes are transformed. |
| `Shuffle Choices` | `true`, `false` | Whether answer choices may be shuffled in final card. Usually `true` for MCQ and `false` for T/F. |
| `Correct Choice ID` | stable ID | Stable answer identifier independent of A/B/C/D order. Recommended for shuffled MCQ. |
| `Correct Answer` | `A`, `B`, `C`, `D`, `True`, `False`, blank | Human-friendly answer key. For shuffled MCQ, this is draft-only and may be recalculated. |
| `Difficulty` | `easy`, `medium`, `tricky`, `unset` | Helps prioritize difficult distractor cards. |
| `Negative Wording` | `true`, `false` | Marks questions such as “Which is NOT correct?” |
| `Explanation` | text | Rationale shown on back. |
| `Transformation Notes` | text | Notes for the AI or future conversion tooling. |

---

# Draft CNSF Body Format

The draft note body should retain the original cloze note content and add an exam-authoring block.

## Draft body template

```markdown
# front_md

## Legacy Prompt

<original cloze/front prompt preserved here>

## Exam Draft

<Question text to be used for MCQ or T/F.>

### Choices

- choice_id: <stable_id_1>
  label: A
  text: <choice text>
  correct: false
- choice_id: <stable_id_2>
  label: B
  text: <choice text>
  correct: true
- choice_id: <stable_id_3>
  label: C
  text: <choice text>
  correct: false
- choice_id: <stable_id_4>
  label: D
  text: <choice text>
  correct: false

# back_md

## Legacy Answer

<original cloze/back answer preserved here>

## Explanation

<brief rationale explaining the correct answer and why distractors are wrong if useful>
```

For true/false drafts, use this body format:

```markdown
# front_md

## Legacy Prompt

<original cloze/front prompt preserved here>

## Exam Draft

<True/false statement.>

# back_md

## Legacy Answer

<original cloze/back answer preserved here>

## Correct Answer

True | False

## Explanation

<brief rationale>
```

---

# Final Multiple Choice Schema

Final MCQ notes should be import-ready and should no longer include the legacy cloze prompt as primary card text. The legacy note ID may remain in metadata for traceability.

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
  - source:aom
  - status:unverified
fields:
  Source Document: <source document name>
  Source Location: <stable source reference>
  Legacy Note ID: <original sv-* note_id>
  Question Type: multiple_choice
  Shuffle Choices: true
  Correct Choice ID: <stable correct choice id>
  Correct Answer Text: <correct answer text>
  Difficulty: easy | medium | tricky | unset
  Negative Wording: true | false
  Explanation: <brief explanation>
---
```

## Final MCQ body template

```markdown
# front_md

**<System Display Name> — Systems Verification**

<Question text?>

A. <choice text>
B. <choice text>
C. <choice text>
D. <choice text>

# back_md

**Correct Answer:** <display letter> — <correct answer text>

<explanation>
```

## MCQ choice shuffling behavior

For final notes with:

```yaml
Shuffle Choices: true
```

the transformation tool should treat `Correct Choice ID` as authoritative, not the displayed A/B/C/D label.

The tool may either:

1. Shuffle choices during generation and write a fixed A/B/C/D order into the final CNSF note, or
2. Preserve all choices as structured fields and allow the Anki card template to shuffle choices with JavaScript.

Recommended first implementation: deterministic shuffle at transformation time using `note_id` as the seed. This avoids JavaScript complexity while preventing the correct answer from always being in the same position across cards.

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
  - source:aom
  - status:unverified
fields:
  Source Document: <source document name>
  Source Location: <stable source reference>
  Legacy Note ID: <original sv-* note_id>
  Question Type: true_false
  Correct Answer: True | False
  Difficulty: easy | medium | tricky | unset
  Negative Wording: false
  Explanation: <brief explanation>
---
```

## Final T/F body template

```markdown
# front_md

**<System Display Name> — Systems Verification**

True or False:

<statement>

# back_md

**Correct Answer:** True | False

<explanation>
```

---

# Examples

## Example 1: MCQ draft note

```markdown
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_exam_draft
note_id: svdraft-electrical-001
anki:
  model: B737_SV_Exam_Draft
  deck: B737::Systems_Verification::Draft
tags:
  - domain:b737
  - topic:systems_verification
  - system:electrical
  - format:draft
  - source:aom
  - status:draft
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Source Location: Electrical System Verification
  Legacy Note ID: sv-electrical-001
  Legacy Note Type: cloze
  Exam Format: mcq
  Conversion Status: ready_for_transform
  Ready For Transform: true
  Shuffle Choices: true
  Correct Choice ID: transfer_buses_unpowered
  Correct Answer: B
  Difficulty: medium
  Negative Wording: false
  Explanation: The TRANSFER BUS OFF light indicates the related transfer bus is not powered.
  Transformation Notes: Converted from cloze recall to MCQ with distractors.
---

# front_md

## Legacy Prompt

When a TRANSFER BUS OFF light is illuminated, the related transfer bus is {{c1::unpowered}}.

## Exam Draft

What does an illuminated TRANSFER BUS OFF light indicate?

### Choices

- choice_id: normal_power_available
  label: A
  text: Normal power is available to the transfer bus.
  correct: false
- choice_id: transfer_buses_unpowered
  label: B
  text: The related transfer bus is unpowered.
  correct: true
- choice_id: battery_charger_failed
  label: C
  text: The battery charger has failed.
  correct: false
- choice_id: apu_powering_both_buses
  label: D
  text: The APU is powering both transfer buses.
  correct: false

# back_md

## Legacy Answer

The related transfer bus is unpowered.

## Explanation

The TRANSFER BUS OFF light indicates that the related transfer bus is not powered.
```

## Example 2: Final MCQ note

```markdown
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_mcq
note_id: svmcq-electrical-001
anki:
  model: B737_SV_MCQ
  deck: B737::Systems_Verification::Exam_Mode
tags:
  - domain:b737
  - topic:systems_verification
  - system:electrical
  - format:mcq
  - source:aom
  - status:unverified
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Source Location: Electrical System Verification
  Legacy Note ID: sv-electrical-001
  Question Type: multiple_choice
  Shuffle Choices: true
  Correct Choice ID: transfer_buses_unpowered
  Correct Answer Text: The related transfer bus is unpowered.
  Difficulty: medium
  Negative Wording: false
  Explanation: The TRANSFER BUS OFF light indicates that the related transfer bus is not powered.
---

# front_md

**Electrical — Systems Verification**

What does an illuminated TRANSFER BUS OFF light indicate?

A. Normal power is available to the transfer bus.
B. The related transfer bus is unpowered.
C. The battery charger has failed.
D. The APU is powering both transfer buses.

# back_md

**Correct Answer:** B — The related transfer bus is unpowered.

The TRANSFER BUS OFF light indicates that the related transfer bus is not powered.
```

## Example 3: True / false draft note

```markdown
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_exam_draft
note_id: svdraft-hydraulics-002
anki:
  model: B737_SV_Exam_Draft
  deck: B737::Systems_Verification::Draft
tags:
  - domain:b737
  - topic:systems_verification
  - system:hydraulics
  - format:draft
  - source:aom
  - status:draft
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Source Location: Hydraulic System Verification
  Legacy Note ID: sv-hydraulics-002
  Legacy Note Type: cloze
  Exam Format: tf
  Conversion Status: ready_for_transform
  Ready For Transform: true
  Shuffle Choices: false
  Correct Choice ID:
  Correct Answer: False
  Difficulty: easy
  Negative Wording: false
  Explanation: Correct explanation goes here.
  Transformation Notes: Converted from cloze recall to true/false.
---

# front_md

## Legacy Prompt

<legacy cloze prompt retained here>

## Exam Draft

True or False: <statement to evaluate>

# back_md

## Legacy Answer

<legacy answer retained here>

## Correct Answer

False

## Explanation

<brief rationale>
```

## Example 4: Final true / false note

```markdown
---
schema: cnsf/v0
domain: b737
note_type: systems_verification_tf
note_id: svtf-hydraulics-002
anki:
  model: B737_SV_TF
  deck: B737::Systems_Verification::Exam_Mode
tags:
  - domain:b737
  - topic:systems_verification
  - system:hydraulics
  - format:true_false
  - source:aom
  - status:unverified
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Source Location: Hydraulic System Verification
  Legacy Note ID: sv-hydraulics-002
  Question Type: true_false
  Correct Answer: False
  Difficulty: easy
  Negative Wording: false
  Explanation: Correct explanation goes here.
---

# front_md

**Hydraulics — Systems Verification**

True or False:

<statement to evaluate>

# back_md

**Correct Answer:** False

<brief rationale>
```

---

# Transformation Rules

## Draft to final MCQ

Transform a draft note into final MCQ when all of the following are true:

```yaml
Exam Format: mcq
Conversion Status: ready_for_transform
Ready For Transform: true
```

Transformation steps:

1. Change `note_type` from `systems_verification_exam_draft` to `systems_verification_mcq`.
2. Change `note_id` prefix from `svdraft-` to `svmcq-`.
3. Change `anki.model` to `B737_SV_MCQ`.
4. Change `anki.deck` to `B737::Systems_Verification::Exam_Mode`.
5. Replace tag `format:draft` with `format:mcq`.
6. Replace tag `status:draft` with `status:unverified` unless reviewed otherwise.
7. Keep `Legacy Note ID` for traceability.
8. Read the question from `## Exam Draft`.
9. Read choices from the `### Choices` block.
10. If `Shuffle Choices: true`, reorder choices using deterministic shuffle.
11. Determine final displayed correct answer letter from `Correct Choice ID`.
12. Write final `front_md` with A/B/C/D options.
13. Write final `back_md` with correct answer and explanation.
14. Remove legacy prompt from primary front/back text in the final note.

## Draft to final true / false

Transform a draft note into final T/F when all of the following are true:

```yaml
Exam Format: tf
Conversion Status: ready_for_transform
Ready For Transform: true
```

Transformation steps:

1. Change `note_type` from `systems_verification_exam_draft` to `systems_verification_tf`.
2. Change `note_id` prefix from `svdraft-` to `svtf-`.
3. Change `anki.model` to `B737_SV_TF`.
4. Change `anki.deck` to `B737::Systems_Verification::Exam_Mode`.
5. Replace tag `format:draft` with `format:true_false`.
6. Replace tag `status:draft` with `status:unverified` unless reviewed otherwise.
7. Keep `Legacy Note ID` for traceability.
8. Read the statement from `## Exam Draft`.
9. Read correct answer from `Correct Answer`.
10. Write final `front_md` as true/false prompt.
11. Write final `back_md` with correct answer and explanation.

---

# AI Chat Bot Work Instructions

Give the following instructions to an AI helper when performing the migration.

## Overall task

You are converting B737 Systems Verification CNSF notes from cloze-style recall into exam-mode recognition cards. Preserve the legacy notes. Create draft conversion notes first. Do not discard original source content.

## Required process

1. Start from a clean feature branch.
2. Copy the existing systems verification directory to `systems_verification_legacy`.
3. Preserve the original legacy files unchanged in that legacy folder.
4. Convert the active `systems_verification` files into `systems_verification_exam_draft` notes.
5. Keep the original prompt/answer content under `## Legacy Prompt` and `## Legacy Answer`.
6. Add an `## Exam Draft` section for the eventual MCQ or true/false question.
7. For MCQ notes, include four choices with stable `choice_id` values.
8. Mark unfinished notes with:

```yaml
Exam Format: unset
Conversion Status: needs_authoring
Ready For Transform: false
```

9. The user will edit the draft notes and mark finished notes with:

```yaml
Conversion Status: ready_for_transform
Ready For Transform: true
```

10. Only transform notes where `Ready For Transform: true`.
11. Generate final MCQ notes using `svmcq-` note IDs.
12. Generate final true/false notes using `svtf-` note IDs.
13. Do not shuffle by changing correctness. If choices are shuffled, track correctness using `Correct Choice ID`.
14. Run canonicalization before staging.
15. Stage and commit at strategic checkpoints.

## AI Proofing Checklist

For each converted note, verify:

1. The question stem is clear, concise, and exam-like.
2. Multiple-choice choices are mutually exclusive, except where the true answer is a union of multiple answers (e.g. "all of the above", or "answers B and D").
3. Only one answer is correct unless explicitly marked multi-select.
4. Distractors are plausible, relevant, and not ambiguously correct.
5. True/False statements avoid double negatives, trick wording, or overly broad claims.
6. The original cloze answer/content is preserved in the explanation or rationale.
7. Source Document and Source Location are retained exactly when known.
8. Conversion Status remains unchanged unless explicitly instructed by the user.
9. Do not invent aircraft facts, limitations, or procedures.
10. If wording is uncertain, flag the note for human review instead of guessing.
11. Preserve note_id unless explicitly performing a final transformation.
12. Maintain valid YAML syntax and field ordering per project standards.

## Conversion Status Lifecycle

Use the following values consistently:

```yaml
Conversion Status: draft | human_ready | transform_ready | imported

### Definitions

  - draft — Initial converted note; requires human review.
  - human_ready — Human reviewed for wording/content; ready for final inspection.
  - transform_ready — Approved for automated conversion into final svmcq or svtf notes.
  - imported — Final note created and successfully synced into Anki.

### Safety Rule

If uncertain, preserve the source wording, add a review note, and defer to human validation.

## Strategic Git checkpoints

Recommended commits:

1. `docs(b737): define systems verification exam-mode schema`
2. `chore(b737): preserve legacy systems verification notes`
3. `feat(b737): add systems verification exam draft conversion tooling`
4. `chore(b737): convert systems verification notes to exam draft schema`
5. `feat(b737): add systems verification exam-mode transform tooling`
6. `feat(b737): generate systems verification exam-mode notes`
7. `feat(b737): add systems verification exam-mode Anki import support`

---

# Open Implementation Decisions

## Should the final note store choices as fields or body text?

First implementation can store choices in `front_md` body text because it works with current CNSF rendering.

A later implementation can add a dedicated Anki model with fields:

```text
Question
Choice_A
Choice_B
Choice_C
Choice_D
Correct_Letter
Correct_Choice_ID
Correct_Answer_Text
Explanation
Source Document
Source Location
Legacy Note ID
```

## Should shuffling happen at transform time or review time?

Recommended first implementation:

- deterministic shuffle at transform time
- seed = `note_id`
- correct answer letter written into final back side

Possible later implementation:

- Anki JavaScript shuffles choices per review
- stores structured choices as fields
- more realistic but more complex

## Should true/false use MCQ model?

Either is possible.

Recommended first implementation:

- separate `B737_SV_MCQ` and `B737_SV_TF` models

Simpler alternative:

- one `B737_SV_Exam` model with `Question Type` field

---

# Checklist for a Completed Draft Note

Before setting `Ready For Transform: true`, confirm:

- [ ] `Exam Format` is `mcq` or `tf`
- [ ] `Conversion Status` is `ready_for_transform`
- [ ] `Ready For Transform` is `true`
- [ ] Source document is present
- [ ] Source location is present
- [ ] Legacy note ID is present
- [ ] Question text is clear
- [ ] Correct answer is unambiguous
- [ ] Explanation is present
- [ ] MCQ notes have four choices
- [ ] MCQ choices have stable `choice_id` values
- [ ] MCQ exactly one choice has `correct: true`
- [ ] T/F notes have `Correct Answer: True` or `False`
- [ ] Negative wording is marked correctly
- [ ] Difficulty is set or left as `unset`

