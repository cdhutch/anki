---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-010
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:indications
- parameter:egt
- scope:common
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: Engine Limit Indications
  Verification Notes: ''
system: B737 Engines
subsystem: Engine Indications
panel_group: Upper DU
panel_name: ''
function_type: failure_logic
normal_state: ''
failure_logic: EGT indication blinks when temperature exceeds maximum limit
affects_bus: ''
powered_by: ''
interacts_with: EEC
notes: ''
---

# front_md

**ENGINES — EGT LIMIT**

What happens on the DU when EGT exceeds the maximum limit?

# back_md

When EGT exceeds the **maximum limit**, the **EGT indication blinks**.

This alerts the crew that the **engine temperature limit has been exceeded**.