---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-033
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
- format:bullets
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
failure_logic: '- Engine generators are automatically connected to their related AC transfer
  buses. - This occurs only once in flight and only in that circumstance.'
affects_bus: AC transfer buses
powered_by: IDG; APU generator
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

If the airplane takes off with the APU powering both transfer buses and the APU is shut down or fails, what happens? How many times can this occur?

# back_md

- Engine generators are automatically connected to their related AC transfer buses. - This occurs only once in flight and only in that circumstance.
