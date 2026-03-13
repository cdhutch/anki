---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-030
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:start
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Pages 7-10-8, 7-11-8
  Verification Notes: Corrected
system: B737 Engines
subsystem: Engine Start
panel_group: Overhead
panel_name: ''
function_type: failure_logic
normal_state: Start valve light extinguished after start
failure_logic: Illuminates when start valve is open
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — START VALVE OPEN Alert**

What does the START VALVE OPEN Alert mean in both steady and blinking conditions?

# back_md

- Steady: Respective engine start valve open and air is supplied to starter
- Blinking: Uncommanded opening of start valve.

