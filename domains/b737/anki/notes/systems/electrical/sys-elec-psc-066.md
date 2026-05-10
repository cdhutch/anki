---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-066
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:electrical_general_cross_subsystem
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.5 (DC buses / TR3)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: ''
panel_name: ''
function_type: concept
normal_state: TR3 powers the battery bus and serves as a backup power source for TR1 and TR2.
failure_logic: ''
affects_bus: battery bus
powered_by: battery
interacts_with: TR1; TR2
notes: TR3 normally powers battery bus; can back up TR1/TR2 if they fail.
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

Under normal conditions, what does TR3 power and what is its role?

# back_md

TR3 powers the battery bus and serves as a backup power source for TR1 and TR2.
