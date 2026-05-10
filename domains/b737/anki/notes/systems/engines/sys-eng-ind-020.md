---
schema: cnsf/v0
domain: b737
note_type: indication
note_id: sys-eng-ind-020
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:indications
- parameter:egt
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Page 7-10-6ngine Limit Indications
  Verification Notes: Corrected
system: B737 Engines
subsystem: Engine Indications
panel_group: Upper DU
panel_name: ''
function_type: failure_logic
normal_state: ''
failure_logic: EGT indication turns yellow when temperature exceeds continuous limit
affects_bus: ''
powered_by: ''
interacts_with: EEC
notes: ''
---

# front_md

**ENGINES — EGT LIMIT**

What happens on the DU when EGT exceeds the continuos limit?

# back_md

When EGT exceeds the **continuous limit**, the **EGT indication turns yellow**.

This alerts the crew that an **engine temperature limit has been exceeded**.