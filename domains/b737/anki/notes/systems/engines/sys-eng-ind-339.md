---
schema: cnsf/v0
domain: b737
note_type: indication
note_id: sys-eng-ind-339
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:eec
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Section 7.20.3 Electronic Engine Control
  Verification Notes: ''
system: B737 Engines
subsystem: Electronic Engine Control
panel_group: Forward Overhead
panel_name: Engine Panel
function_type: indication
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — EEC SWITCH LIGHT INDICATIONS**

How do the **EEC switch lights indicate Soft Alternate Mode and Hard Alternate Mode**?

# back_md

The **EEC switches contain two lights**:

• **ON (green)**  
• **ALTN (amber)**

---

**Normal Mode**

- **ON light illuminated**
- **ALTN light extinguished**

---

**Soft Alternate Mode**

- **ON light extinguished**
- **ALTN light extinguished**

The EEC automatically reverts from **Normal Mode to Soft Alternate Mode** when certain faults occur.

---

**Hard Alternate Mode**

- **ALTN light illuminated**

Hard Alternate Mode occurs when the **EEC ALTN switch is selected** or when certain faults require deeper degradation of EEC control.