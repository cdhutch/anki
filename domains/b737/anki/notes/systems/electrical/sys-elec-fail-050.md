---
schema: cnsf/v0
domain: b737
note_type: system_failure_logic
note_id: sys-elec-fail-050
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- style:verbatim
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.4 (Automatic Load Shedding – Engine Generators)
  Verification Notes: ''
system: B737 Electrical
subsystem: AC Power
panel_group: ''
panel_name: ''
function_type: failure-logic
normal_state: ''
failure_logic: 'Sheds incrementally: (1) galleys and main bus on transfer bus 2; (2) galleys
  and main bus on transfer bus 1; (3) IFE buses.'
affects_bus: AC transfer bus 1; AC transfer bus 2; main buses; IFE buses
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**B737 ELECTRICAL — AC POWER**

What is the order of load shedding during single generator operation?

# back_md

Sheds incrementally:
- Galleys and main bus on transfer bus 2
- Galleys and main bus on transfer bus 1
- IFE buses.
