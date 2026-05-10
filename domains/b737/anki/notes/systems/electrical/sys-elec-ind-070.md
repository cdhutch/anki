---
schema: cnsf/v0
domain: b737
note_type: system_panel_item
note_id: sys-elec-ind-070
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
  Source Location: Ch 6 §6.20.5 (DC Power System)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Overhead – Electrical
panel_name: ELEC light
function_type: indication
normal_state: 'On the ground: indicates a fault exists in the DC power system or standby power
  system. In flight: ELEC light is inhibited.'
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: DC power system; standby power system
notes: In flight inhibited (good as-is)
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

ELEC light: what does it indicate on the ground and in-flight?

# back_md

- On the ground: indicates a fault exists in the DC power system or standby power system.
- In flight: ELEC light is inhibited.
