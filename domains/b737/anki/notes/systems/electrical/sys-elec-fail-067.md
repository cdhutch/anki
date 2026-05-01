---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-067
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
  Source Location: Ch 6 §6.20.5 (Cross bus tie relay) + §6.10.4 (BUS TRANSFER OFF)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Overhead – Electrical
panel_name: BUS TRANSFER switch
function_type: failure-logic
normal_state: ''
failure_logic: At glideslope capture during a flight director or autopilot ILS approach; and
  when the BUS TRANSFER switch is positioned to OFF.
affects_bus: ''
powered_by: ''
interacts_with: cross bus tie relay; BUS TRANSFER switch; ILS logic (GS capture)
notes: 'Consider splitting into 2 bullets: (1) GS capture condition; (2) BUS TRANSFER OFF
  condition.'
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

Under which two conditions does the cross bus tie relay open?

# back_md

- At glideslope capture during a flight director or autopilot ILS approach
- When the BUS TRANSFER switch is positioned to OFF.
