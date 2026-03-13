---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-eng-psc-307
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:EEC
- model:b737-800
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

**ENGINES — APPROACH IDLE (737-800)**

Under what conditions does the EEC command **approach idle** on the 737-800?

# back_md

On the **737-800**, the EEC commands **approach idle** when **any of the following conditions exist**:

- **Cowl thermal anti-ice switch is ON for either engine 1 or engine 2**
- **Altitude is below 19K' MSL and left or right MLG down and locked**
- **Altitude is below 19K' MSL and left or right flaps ≥ 15**

Approach idle increases N2 to improve **engine acceleration during landing configuration**.