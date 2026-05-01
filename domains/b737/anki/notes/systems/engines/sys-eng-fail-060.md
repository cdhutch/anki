---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-060
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:fuel
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Page 7-20-11
  Verification Notes: Corrected
system: B737 Engines
subsystem: Engine Fuel Control
panel_group: Control Stand
panel_name: ''
function_type: failure_logic
normal_state: ''
failure_logic: Engine shuts down when fuel supply is cut off
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — ENGINE SHUTDOWN**

How is an engine normally shut down?

# back_md

An engine is shut down by **moving the engine start lever to CUTOFF**.

This **closes the spar fuel shutoff valve and engine fuel shutoff valve**, terminating combustion.