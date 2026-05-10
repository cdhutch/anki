---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-032
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- status:verifie
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.3–6.20.4 (AC Power / Bus Tie System)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: BTBs automatically close so the remaining generator can supply both transfer
  buses through the tie bus/BTBs.
affects_bus: AC transfer buses; tie bus; BTBs
powered_by: IDG
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

In flight, with one engine generator no longer supplying power and BUS TRANSFER in AUTO, what happens to the transfer buses?

# back_md

BTBs automatically close so the remaining generator can supply both transfer buses through the tie bus/BTBs.
