---
schema: cnsf/v0
domain: b737
note_type: system_general
note_id: sys-elec-swt-132
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- subtopic:lights_switches
- style:verbatim
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.10.4 (GRD PWR switch ON)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: Overhead – Electrical
panel_name: ''
function_type: control
normal_state: ''
failure_logic: ''
affects_bus: AC transfer buses
powered_by: external power
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

What happens when the GRD PWR switch is  moved to ON (with ground power available)?

# back_md

Removes previously connected power from AC transfer buses, then connects ground power to the AC transfer buses (if power quality is correct).
