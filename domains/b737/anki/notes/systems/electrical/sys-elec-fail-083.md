---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-083
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:standby_power
- scope:common
- style:verbatim
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.5 (Battery Power – buses powered)
  Verification Notes: ''
system: B737 Electrical
subsystem: Standby Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: Battery bus; DC standby bus;Hot battery bus; Switched hot battery bus.
affects_bus: battery bus; DC buses
powered_by: battery
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — STANDBY POWER**

After loss of both generators, which DC buses does the battery power?

# back_md

- Battery bus
- DC standby bus
- Hot battery bus
- Switched hot battery bus.
