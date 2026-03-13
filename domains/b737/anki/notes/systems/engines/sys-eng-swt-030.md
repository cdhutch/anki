---
schema: cnsf/v0
domain: b737
note_type: switch
note_id: sys-eng-swt-030
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:fuel
- scope:common
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: Engine Start Levers
  Verification Notes: ''
system: B737 Engines
subsystem: Fuel Shutoff
panel_group: Control Stand
panel_name: Engine Start Levers
function_type: switch
normal_state: CUTOFF when engine not operating
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: fuel spar valve
notes: ''
---

# front_md

**ENGINES — START LEVER VALVES**

Which valves are controlled by the engine start lever?

# back_md

The engine start lever controls two fuel shutoff valves:

- **Engine fuel spar valve**
- **Engine fuel shutoff valve**

When the start lever is moved to **IDLE**, both valves open to allow fuel flow to the engine.

Moving the lever to **CUTOFF** closes both valves and stops fuel flow.