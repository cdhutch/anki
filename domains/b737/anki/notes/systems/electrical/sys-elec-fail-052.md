---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-052
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:electrical_general_cross_subsystem
- scope:common
- style:verbatim
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.4 (APU Automatic Load Shedding)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Automatic load shedding (logic)
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: 'Automatic load shedding in-flight on APU-only power: sheds galley+main; if
  overload persists, sheds both IFE buses.'
affects_bus: galley buses; main buses; IFE buses
powered_by: APU generator
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

APU-only electrical power in flight: what is shed automatically (and what else if overload persists)?

# back_md

All galley buses and main buses are automatically shed. If load still exceeds limits, both IFE buses are also automatically shed.
