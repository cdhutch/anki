---
schema: cnsf/v0
domain: b737
note_type: indication
note_id: sys-eng-ind-080
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:start
- parameter:n2
- aircraft:737-800
- aircraft:737-max8
- scope:common
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: Engine Start Indications
  Verification Notes: ''
system: B737 Engines
subsystem: Engine Start
panel_group: Upper DU
panel_name: ''
function_type: indication
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: starter system
notes: ''
---

# front_md

**ENGINES — N2 START VALUES**

What N2 values are typically observed during engine start?

# back_md

Typical N2 values during start:

737-800 (CFM56-7B)

- Fuel introduction: **≈ 25% N2**
- Idle N2 after start: **≈ 60–63%**

737 MAX-8 (LEAP-1B)

- Fuel introduction: **≈ 25% N2**
- Idle N2 after start: **≈ 55–60%**

N2 represents **core compressor speed** and is used to monitor proper engine acceleration during start.