---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-100
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:thrust_reverser
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Page 7-20-21
  Verification Notes: Corrected
system: B737 Engines
subsystem: Thrust Reverser
panel_group: ''
panel_name: ''
function_type: failure_logic
normal_state: ''
failure_logic: Prevents deployment in flight
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — REVERSER INTERLOCKS**

What are the two thrust reverser deployment interlocks?

# back_md

- **Either RADALT** senses less than **10 feet altitude** OR
- **Air/ground safety sensor** is in **ground mode**.