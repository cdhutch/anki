---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-053
anki:
  model: B737_Systems
  deck: B737::Systems
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
  Source Location: Ch 6 §6.20.4 (APU Automatic Load Shedding)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Overhead – Electrical
panel_name: CAB/UTIL switch (used for restoration)
function_type: failure-logic
normal_state: ''
failure_logic: 'Ground APU overload: sheds galley+main until within limits; restoration attempt
  via CAB/UTIL OFF → ON.'
affects_bus: galley buses; main buses
powered_by: 'APU generator; external power (context: ground)'
interacts_with: CAB/UTIL switch
notes: ''
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

APU on the ground with overload sensed: what does the APU shed, and how can you attempt restoration?

# back_md

Sheds galley buses and main buses until load is within limits. Restoration can be attempted by moving CAB/UTIL switch OFF then back ON.
