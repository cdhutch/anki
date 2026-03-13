---
schema: cnsf/v0
domain: b737
note_type: indication
note_id: sys-eng-ind-346
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:thrust_management
- model:b737-800
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Section 7.11.1 Primary Engine Indications
  Verification Notes: ''
system: B737 Engines
subsystem: Thrust Management
panel_group: Upper Display Unit
panel_name: Engine Display
function_type: indication
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: FMC, autothrottle system, N1 SET control
notes: ''
---

# front_md

**ENGINES — THRUST MODE DISPLAY (-800)**

- What does the thrust mode display show?

Provide the name of the thrust modes associated with each of the following annunciations:

| Annunciation | Meaning |
| :--: | :--- |
| **R-TO** | |
| **R-CLB** | |
| **TO** | |
| **TO B** | |
| **CLB** | |
| **CRZ** | |
| **G/A** | |
| **CON** | |
| **MAN** | |
| **---** | |

# back_md

- The **thrust mode display** shows the **active N1 limit reference mode**.

Possible annunciations are:

| Annunciation | Meaning |
| :--: | :--- |
| **R-TO** | Reduced Takeoff |
| **R-CLB** | Reduced Climb |
| **TO** | Takeoff |
| **TO B** | Takeoff Bump Thrust |
| **CLB** | Climb |
| **CRZ** | Cruise |
| **G/A** | Go-Around |
| **CON** | Continuous |
| **MAN** | Manual N1 Setting |
| **---** | FMC Not Computing Thrust Limit |

Additional logic:

- **MAN** displays when the **N1 SET outer knob is in 1, 2, or BOTH**
- **AUTO** returns N1 reference control to the **FMC**