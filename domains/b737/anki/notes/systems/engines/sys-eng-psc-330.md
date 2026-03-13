---
schema: cnsf/v0
domain: b737
note_type: principle
note_id: sys-eng-psc-330
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
  Source Location: Electronic Engine Control (EEC)
  Verification Notes: ''
system: B737 Engines
subsystem: Electronic Engine Control
panel_group: ''
panel_name: ''
function_type: principle
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — EEC ARCHITECTURE**

How is the **Electronic Engine Control (EEC)** structured on the B737 engine?

# back_md

The **Electronic Engine Control (EEC)** uses a **dual-channel architecture**.

- The EEC contains **two independent channels**:
  - **Primary channel**
  - **Secondary channel**

- Either channel is capable of **controlling engine operation**.

- The EEC functions as the **engine control computer**, managing:
  - Fuel metering
  - Engine limit protection
  - Thrust control logic

This architecture provides **redundancy for engine control functions**.