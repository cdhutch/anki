---
schema: cnsf/v0
domain: b737
note_type: system_panel_item
note_id: sys-elec-swt-041
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
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.10.4 (BUS TRANSFER switch OFF)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: Overhead – Electrical
panel_name: BUS TRANSFER switch
function_type: control
normal_state: ''
failure_logic: ''
affects_bus: AC transfer bus 1; AC transfer bus 2; TR3; DC bus 1; DC bus 2; DC buses
powered_by: IDG
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

BUS TRANSFER switch — OFF: what does it do (AC + DC + TR3 input)?

# back_md

- AC: isolates AC transfer bus 1 from AC transfer bus 2 (if one IDG is supplying both).
- DC: DC cross tie relay opens to isolate DC bus 1 from DC bus 2.
- Also inhibits TR3 input from connecting to AC transfer bus 1.
