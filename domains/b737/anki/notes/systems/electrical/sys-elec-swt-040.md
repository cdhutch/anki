---
schema: cnsf/v0
domain: b737
note_type: system_panel_item
note_id: sys-elec-swt-040
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
  Source Location: Ch 6 §6.10.4 (BUS TRANSFER switch)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: Overhead – Electrical
panel_name: BUS TRANSFER switch
function_type: control
normal_state: ''
failure_logic: ''
affects_bus: AC transfer buses; BTBs
powered_by: external power
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

BUS TRANSFER switch — AUTO (guarded): what does it allow for AC and DC?

# back_md

- AC: BTBs operate automatically to maintain power to AC transfer buses from any operating generator or external power.
- DC: DC cross tie relay automatically provides normal or isolated operation as required.
