---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-012
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- style:verbatim
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.3 (AC Power System)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: It can be powered by any available source through the tie bus via the bus tie
  breakers (BTBs).
affects_bus: tie bus; BTBs
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

If the AC source powering an AC transfer bus fails or is disconnected, how can that transfer bus be powered?

# back_md

It can be powered by any available source through the tie bus via the bus tie breakers (BTBs).
