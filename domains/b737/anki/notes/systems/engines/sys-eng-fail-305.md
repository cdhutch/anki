---
schema: cnsf/v0
domain: b737
note_type: failure_logic
note_id: sys-eng-fail-305
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:engines
- subsystem:oil
- scope:common
- status:verified
fields:
  Source Document: B737 Aircraft Systems Manual Rev 4.0
  Source Location: Page 7-10-9
  Verification Notes: Corrected
system: B737 Engines
subsystem: Oil System
panel_group: ''
panel_name: ''
function_type: failure_logic
normal_state: ''
failure_logic: Oil filter bypass valve open
affects_bus: ''
powered_by: ''
interacts_with: ''
notes: ''
---

# front_md

**ENGINES — OIL FILTER BYPASS**

What does the **OIL FILTER BYPASS** alert indicate?

- Blinking?
- Steady?

# back_md

The **OIL FILTER BYPASS** an imprending bypass of oil supply filter.

- Blinking: First 10 seconds
- Steady: After first 10 seconds

This means:

- The filter may be **clogged**
- Oil is flowing **around the filter**