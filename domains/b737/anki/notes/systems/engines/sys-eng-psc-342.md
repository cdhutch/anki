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
- status:verified
fields:
  Source Document: 737 Aircraft Systems Manual Rev 4.0
  Source Location: 7.20.7 Engine Start System
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

- What are the smoke/fumes implications of an LRD activation?
- What mechanical switch actions would isolate the affected bleed air system?

# back_md

### Cabin air distribution

- The **left pack primarily supplies the flightdeck**
- The **right pack supplies the forward and aft cabin**

Therefore, the **location of smoke/fumes depends on which engine is affected**.

---

### Isolating the affected bleed air system

The **engine bleed air valve isolates the affected bleed system** when:

- The **Engine Fire Switch is pulled**, or  
- The **Engine Start Lever is positioned to CUTOFF**