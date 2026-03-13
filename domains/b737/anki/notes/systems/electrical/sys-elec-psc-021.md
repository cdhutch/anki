---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-021
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
function_type: concept
normal_state: ''
failure_logic: ''
affects_bus: AC transfer buses
powered_by: IDG; APU generator; external power
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

What does selecting either APU GEN switch to ON do to the AC transfer buses in the following cases?

- Neither AC transfer bus powered by IDG
- Both AC transfer buses powered by IDGs

# back_md

If neither AC transfer bus powered by IDG:
- Connects both AC transfer buses to APU generator
- Disconnects external power
- Illuminates opposite SOURCE OFF light until other APU GEN switch moved to ON.

If both AC transfer buses powered by IDGs:
- Powers the related transfer bus from the APU generator
- Other transfer bus continues to receive power from the IDG
