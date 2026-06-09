# SV Field Conventions

## YAML Schema

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

## Rules

- Correct choice cycles **B → C → D → A → B** per note within each system
- T/F questions use `format:mcq` with Choice A: 'True', Choice B: 'False', Correct Choice: A|B, Shuffle Choices: false
- Any field ending in `:` must be quoted (e.g., `Question Stem: 'You must select ALTN, then:'`)
