---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-eng-psc-308
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:EEC
- model:b737-max8
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: 7.20.3 Electronic Engine Control
  Verification Notes: ''
system: B737 Engines
subsystem: Idle Control
panel_group: ''
panel_name: ''
function_type: system_concept
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — APPROACH IDLE (MAX-8)**

Under what conditions does the EEC command **approach idle** on the MAX-8?

# back_md

On the **MAX-8**, the EEC commands **approach idle** when **either of the following conditions exist**:

- **Flaps are extended to 15 or greater**
- **Flaps not up AND Engine anti-ice is ON**

Approach idle increases N2 to ensure **adequate engine acceleration margin during approach and landing**.