---
schema: cnsf/v0
domain: b737
note_type: cats_and_dogs
note_id: cat-bleed-transition-r-engine-taxi-to-dual-engine
anki:
  model: B737_Structured
  deck: B737::Core::Cats_and_Dogs
tags:
- domain:b737
- topic:air_conditioning
- type:cats_and_dogs
- status:unverified
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Verification Notes: ''
---

# front_md

**Bleed/Pack/ISO — Transition**

Taxiing on R engine → Taxiing on both engines: what switch changes are made?

# back_md

**Changes:**

| Switch    | From   | To   |
| --------  | ------ | ---- |
| ISO Valve | CLOSED | AUTO |
| APU Bleed | ON     | OFF  |

**New Configuration:**

| Switch        | Position   |
| --------      | ---------- |
| ISO Valve     | AUTO       |
| Packs         | Both AUTO  |
| Engine Bleeds | Both ON    |
| APU Bleed     | OFF        |
