---
schema: cnsf/v0
domain: b737
note_type: principle
note_id: sys-eng-psc-331
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:eec
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: 7-20-6 EEC Operating Modes
  Verification Notes: ''
system: B737 Engines
subsystem: Electronic Engine Control
panel_group: ''
panel_name: ''
function_type: principle
normal_state: Normal Mode
failure_logic: Soft Alternate / Hard Alternate
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — EEC OPERATING MODES**

What operating modes are available in the **Electronic Engine Control (EEC)**?

# back_md

The EEC operates in **three possible modes**:

• **Normal Mode**  
• **Soft Alternate Mode**  
• **Hard Alternate Mode**

**Normal Mode**
- Full engine control logic
- Provides engine limit protections

**Soft Alternate Mode**
- Entered automatically if **normal mode is unavailable**
- Some control functions may be degraded
- Basic engine control and limit protection remain

**Hard Alternate Mode**
- Occurs with more significant EEC faults
- Engine operates with **reduced automatic protections**