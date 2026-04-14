---
schema: cnsf/v0
domain: b737
note_type: flow
note_id: flow-after-start-air-subflow
anki:
  model: B737_Structured
  deck: B737::Triggers_and_Flows::Flows
tags:
- domain:b737
- topic:triggers_and_flows
- type:flow
- flow:after_start
- subflow:air
- source:flows
- status:unverified
fields:
  Source Document: American Airlines B737 Flows
  Source Location: After Start Air Sub-Flow
  Verification Notes: null
---

# front_md

**After Start — Air Sub-Flow**

What is the flow?

# back_md

**After Start — Air Sub-Flow**

- ENG and WING ANTI-ICE switches: VERIFY
- AIR CONDITIONING PANEL: SET

Single engine on #2 or dual engines:
- Both PACKS: AUTO
- Both engine bleeds: ON
- APU BLEED:
  - Single engine #2: ON
  - Dual engine: OFF
- ISOLATION VALVE:
  - Single engine #2: CLOSED
  - Dual engine: AUTO

Single engine on #1:
- Both PACKS: AUTO
- Engine bleeds: #1 OFF; #2 ON
- APU BLEED: ON
- ISOLATION VALVE: AUTO