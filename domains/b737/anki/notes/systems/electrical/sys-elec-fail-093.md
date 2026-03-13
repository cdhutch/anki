---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-093
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:standby_power
- scope:common
- special-formatting
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.6 (Standby Power System – alternate operation)
  Verification Notes: ''
system: B737 Electrical
subsystem: Standby Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: 'With the loss of all AC generators and the guards down on the BATTERY  and
  STANDBY POWER switches, what powers the following buses: AC Standby Bus: Battery via static
  inverter; DC Standby Bus: battery; Battery Bus: battery; Hot Battery Bus: battery; Switched
  Hot Battery Bus: battery?'
affects_bus: battery bus; AC standby bus
powered_by: battery; static inverter
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — STANDBY POWER**

With the loss of all AC generators and the guards down on the BATTERY and STANDBY POWER switches, what powers the following buses?

- AC Standby Bus
- DC Standby Bus
- Battery Bus
- Hot Battery Bus
- Switched Hot Battery Bus

# back_md

With the loss of all AC generators and the guards down on the BATTERY and STANDBY POWER switches, what powers the following buses?

- AC Standby Bus: Battery via Static Inverter
- DC Standby Bus: Battery
- Battery Bus: Battery
- Hot Battery Bus: Battery
- Switched Hot Battery Bus: Battery
