---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-065
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:standby_power
- scope:common
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.5 (DC buses / cross bus tie relay)
  Verification Notes: ''
system: B737 Electrical
subsystem: Standby Power
panel_group: ''
panel_name: ''
function_type: concept
normal_state: .TR1 and TR2 each power DC bus 1, DC bus 2, and the DC standby bus. They are
  connected via the cross bus tie relay;
failure_logic: ''
affects_bus: TR1; TR2; DC bus 1; DC bus 2; DC buses
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — STANDBY POWER**

- Under normal conditions, how are DC bus 1, DC bus 2, and the DC standby buses powered?
- How are they connected to one another?

# back_md

- All three DC buses powered jointly by TR1 and TR2
- All three DC buses are connected via the Cross Bus Tie Relay
