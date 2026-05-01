---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-001
anki:
  model: B737_Systems
  deck: B737::Systems::Aircraft_Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:electrical_general_cross_subsystem
- scope:common
- style:verbatim
- format:bullets
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual (Electrical)
  Source Location: Ch 6 §6.20.1–6.20.2 (Electrical system principles)
  Verification Notes: ''
system: B737 Electrical
subsystem: Electrical — General (cross-subsystem)
panel_group: Aircraft electrical architecture (conceptual)
panel_name: ''
function_type: concept
normal_state: ''
failure_logic: ''
affects_bus: ''
powered_by: ''
interacts_with: AC sources; transfer buses; bus tie logic
notes: 'Consider splitting into 2 bullets in answer (principle 1: no paralleling; principle
  2: auto-disconnect on transfer bus).'
---

# front_md

**B737 ELECTRICAL — ELECTRICAL — GENERAL (CROSS-SUBSYSTEM)**

What are the two basic principles of operation for the B737 electrical system?

# back_md

- No paralleling of AC sources.
- Connecting a source to a transfer bus automatically disconnects an existing source.
