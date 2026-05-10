---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-020
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- subtopic:lights_switches
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.3 (AC Power System) + §6.10.4 (GRD PWR switch)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: ''
panel_name: ''
function_type: concept
normal_state: ''
failure_logic: ''
affects_bus: AC transfer buses
powered_by: external power
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

What does selecting GRD PWR Switch ON do on the ground with both generators off the bus?

# back_md

If ground power available:
- Removes previously connected power from AC transfer buses
- Connects ground power to AC transfer buses if power quality is correct
