---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-051
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
- format:bullets
- status:verifie
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.4 (Automatic Load Shedding – Engine Generators)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: IFE/PASS buses restore automatically. Galley and main bus power require CAB/UTIL
  switch reset (OFF then ON) to restore.
affects_bus: main buses
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

When source capacity returns to two-generator operation, what restores automatically and what requires CAB/UTIL reset?

# back_md

IFE/PASS buses restore automatically. Galley and main bus power require CAB/UTIL switch reset (OFF then ON) to restore.
