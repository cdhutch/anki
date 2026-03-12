---
schema: cnsf/v0
domain: b737
note_type: system_panel_item
note_id: sys-elec-swt-095
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:standby_power
- scope:common
- subtopic:lights_switches
- style:verbatim
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.6 (Standby power switch – BAT)
  Verification Notes: ''
system: B737 Electrical
subsystem: Standby Power
panel_group: Overhead – Electrical
panel_name: Standby power switch
function_type: control
normal_state: ''
failure_logic: ''
affects_bus: battery bus; AC standby bus
powered_by: battery
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — STANDBY POWER**

Standby power switch — BAT: what does it do (and what happens if BAT switch is OFF)?

# back_md

- Overrides automatic switching and places AC standby bus, DC standby bus, and battery bus on battery power. Battery switch may be ON or OFF
- If battery switch is OFF, the switched hot battery bus is not powered.
