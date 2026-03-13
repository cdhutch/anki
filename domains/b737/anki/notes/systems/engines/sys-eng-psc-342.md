---
schema: cnsf/v0
domain: b737
note_type: principle
note_id: sys-eng-psc-342
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:lrd
- model:b737-max8
- status:unverified
fields:
  Source Document: B737 Aircraft Systems Manual — Engines
  Source Location: 7-20-17 Load Reduction Device
  Verification Notes: ''
system: B737 Engines
subsystem: Load Reduction Device
panel_group: ''
panel_name: ''
function_type: principle
normal_state: ''
failure_logic: LRD activation damages oil system and introduces oil into bleed air system
affects_bus: Bleed air system
powered_by: ''
interacts_with: oil system, compressor, bleed air system, air conditioning packs
notes: ''
---

# front_md

**ENGINES — LOAD REDUCTION DEVICE (LRD) AND SMOKE/FUMES**

What occurs when the **LEAP-1B Load Reduction Device (LRD)** activates and how can smoke enter the airplane?

# back_md

The **Load Reduction Device (LRD)** reduces **unbalanced dynamic loads** transmitted to the engine structures and pylon during a **full or partial fan blade-out event** by **decoupling the fan rotor**.

During **LRD activation**:

- The **engine oil system is damaged**
- **Large amounts of oil enter the bleed air system**
- Oil ingested into the **engine core compressor** can be exposed to high temperatures
- This may produce **smoke or fumes in the flightdeck or cabin**

---

### Cabin air distribution

- The **left pack primarily supplies the flightdeck**
- The **right pack supplies the forward and aft cabin**

Therefore, the **location of smoke/fumes depends on which engine is affected**.

---

### Isolating the affected bleed air system

The **engine bleed air valve isolates the affected bleed system** when:

- The **Engine Fire Switch is pulled**, or  
- The **Engine Start Lever is positioned to CUTOFF**