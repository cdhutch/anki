---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-092
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
- status:verifie
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.6 (Standby Power System – normal conditions)
  Verification Notes: ''
system: B737 Electrical
subsystem: Standby Power
panel_group: ''
panel_name: ''
function_type: concept
normal_state: ''
failure_logic: ''
affects_bus: AC transfer buses; battery bus; AC standby bus; TR1; TR2; TR3
powered_by: battery
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — STANDBY POWER**

With both AC Transfer Buses powered by their generators and the guards down on the BAT and STANDBY POWER switches, what powers the following buses?
- AC Standby Bus
- DC Standby Bus
- Battery Bus
- Hot Battery Bus
- Switched Hot Battery Bus

# back_md

With both AC Transfer Buses powered by their generators and the guards down on the BAT and STANDBY POWER switches, what powers the following buses?
- AC Standby Bus: AC Transfer Bus #1
- DC Standby Bus: TR1, TR2, and TR3
- Battery Bus: TR3
- Hot Battery Bus: Battery and/or Battery Charger
- Switched Hot Battery Bus: Battery and/or Battery Charger.
