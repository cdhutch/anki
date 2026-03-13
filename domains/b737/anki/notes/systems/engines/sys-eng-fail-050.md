---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-050
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:start
- scope:common
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: Starter Operation
  Verification Notes: ''
system: B737 Engines
subsystem: Engine Start
panel_group: ''
panel_name: ''
function_type: failure_logic
normal_state: Starter disengages automatically
failure_logic: Starter cuts out when engine reaches self-sustaining speed
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — STARTER CUTOUT**

When does the starter disengage during engine start?

# back_md

The **starter disengages automatically when the engine reaches self-sustaining speed**.

At that point:

- **Starter valve closes**
- **Engine start switch returns to OFF**