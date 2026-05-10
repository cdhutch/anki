---
schema: cnsf/v0
domain: b737
note_type: system_panel_item
note_id: sys-elec-ind-068
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:electrical_general_cross_subsystem
- scope:common
- subtopic:lights_switches
- style:verbatim
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.5 (TR UNIT light logic)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Overhead – Electrical
panel_name: TR UNIT light
function_type: indication
normal_state: 'In flight: illuminates if: [TR1 OR  (TR2 AND TR3)]  has failed. On the ground:
  any TR fault causes the light to illuminate.'
failure_logic: ''
affects_bus: TR1; TR2; TR3
powered_by: ''
interacts_with: TR1; TR2; TR3
notes: ''
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

TR UNIT light: when does it illuminate in flight vs on the ground?

# back_md

- In flight: illuminates if: [TR1 OR (TR2 AND TR3)] has failed.
- On the ground: any TR fault causes the light to illuminate.
