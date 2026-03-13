---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-020
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:eec
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: EPage 7-20-6
  Verification Notes: Corrected
system: B737 Engines
subsystem: Electronic Engine Control
panel_group: ''
panel_name: ''
function_type: failure_logic
normal_state: EEC operates in normal mode
failure_logic: EEC reverts to alternate mode if normal mode fails
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — EEC MODE**

What happens if normal EEC operation fails?

# back_md

If **normal EEC operation fails**, the system **reverts to alternate mode**.

In alternate mode:

- Thust rating shortfalls or exceedances may occur
