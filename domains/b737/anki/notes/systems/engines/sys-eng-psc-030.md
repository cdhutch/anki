---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-eng-psc-030
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:eec
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: E7.20.2 Engine Indications
  Verification Notes: ''
system: B737 Engines
subsystem: Electronic Engine Control
panel_group: ''
panel_name: ''
function_type: system_concept
normal_state: EEC powered when engine is operating
failure_logic: ''
affects_bus: ''
powered_by: engine alternator
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — EEC POWER**

What powers the Electronic Engine Control (EEC)?

# back_md

- Prior to reaching 15% N2: **AC Transfer Bus 1/2 (respective)**.
- After reaching 15% N2: **Engine-mounted EEC Alternator**
