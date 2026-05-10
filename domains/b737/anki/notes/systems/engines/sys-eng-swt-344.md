---
schema: cnsf/v0
domain: b737
note_type: switch
note_id: sys-eng-swt-344
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:indications
- model:b737-800
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: 7.11.1 Primary Engine Indications
  Verification Notes: ''
system: B737 Engines
subsystem: Engine Indications
panel_group: Forward Panel
panel_name: Display Control Panel
function_type: control
normal_state: AUTO
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: FMC, engine indication system
notes: ''
---

# front_md

**ENGINES — N1 SET CONTROL (-800)**

How do the **N1 SET outer knob and inner knob** control the N1 reference bugs?

# back_md

The **N1 SET control** on the **Display Control Panel** consists of:

• **Outer knob (mode selector)**  
• **Inner knob (spring-loaded rotary control)**

---

### Outer Knob Positions

**AUTO**

- Both reference **N1 bugs set by the FMC**
- Based on **N1 LIMIT page** and **takeoff reference page**
- Displays the **active autothrottle N1 limit**

**BOTH**

- Both **N1 reference bugs and readouts manually set**
- Adjustment made with **inner knob**
- **No effect on autothrottle operation**

**1**

- **Engine 1 N1 bug and readout manually set**
- Adjustment made with **inner knob**
- **No effect on autothrottle operation**

**2**

- **Engine 2 N1 bug and readout manually set**
- Adjustment made with **inner knob**
- **No effect on autothrottle operation**

---

### Inner Knob

- **Spring-loaded to center**
- Rotating the knob **moves the selected N1 reference bug(s)** and **readouts**
- Active when the **outer knob is in BOTH, 1, or 2**