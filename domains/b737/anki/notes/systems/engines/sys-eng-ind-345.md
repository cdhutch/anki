---
schema: cnsf/v0
domain: b737
note_type: indication
note_id: sys-eng-ind-345
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:thrust_management
- model:b737-max8
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Section 7.10.1 Primary Engine Indications
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
interacts_with: FMC, autothrottle system
notes: ''
---

# front_md

**ENGINES — THRUST MODE DISPLAY (MAX-8)**

- What does the thrust mode display show?

Provide the name of the thrust modes associated with each of the following annunciations:

| Annunciation | Meaning |
| :--:         | :---    |
| **TO**       |         |
| **TO 1**     |         |
| **TO 2**     |         |
| **D-TO**     |         |
| **D-TO 1**   |         |
| **D-TO 2**   |         |
| **CLB**      |         |
| **CLB 1**    |         |
| **CLB 2**    |         |
| **CRZ**      |         |
| **MAN**      |         |
| **G/A**      |         |
| **CON**      |         |
| **---**     |         |


# back_md

- The **thrust mode display** shows the **active N1 limit reference mode**.

Possible annunciations are:

| Annunciation | Meaning                                                   |
| :--:         | :---                                                      |
| **TO**       | Takeoff                                                   |
| **TO 1**     | Derated Takeoff One                                       |
| **TO 2**     | Derated Takeoff Two                                       |
| **D-TO**     | Assumed Temperature Reduced Thrust Takeoff                |
| **D-TO 1**   | Derate One And Assumed Temperature Reduced Thrust Takeoff |
| **D-TO 2**   | Derate Two And Assumed Temperature Reduced Thrust Takeoff |
| **CLB**      | Climb                                                     |
| **CLB 1**    | Derated Climb One                                         |
| **CLB 2**    | Derated Climb Two                                         |
| **CRZ**      | Cruise                                                    |
| **MAN**      | Manual N1 Setting                                         |
| **G/A**      | Go-Around                                                 |
| **CON**      | Continuous                                                |
| **---**     | FMC Not Computing Thrust Limit                            |