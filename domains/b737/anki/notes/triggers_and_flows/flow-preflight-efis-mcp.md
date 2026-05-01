---
schema: cnsf/v0
domain: b737
note_type: flow
note_id: flow-preflight-efis-mcp
anki:
  model: B737_Structured
  deck: B737::Core::Triggers_and_Flows::Flows
tags:
- domain:b737
- topic:triggers_and_flows
- type:flow
- flow:preflight
- segment:efis_mcp
- sequence:05
- source:flows
- status:unverified
fields:
  Source Document: American Airlines B737 Aircraft Operating Manual Revision Number 9.0
  Source Location: Preflight — EFIS / MCP
  Verification Notes: null
---

# front_md

**Preflight — EFIS / MCP**

What is your flow?

# back_md

**Preflight — EFIS / MCP**

CA EFIS:
- MINS: BARO
  - ≤ 3DL: remove BARO MINS from PFD
  - > 3DL: E/O ACCEL ALT MSL
- BARO: SET
- MAP: SELECTED
- WXR: OFF
- TERR: AS REQ

MCP:
- COURSE knobs × 2: runway heading
- FD × 2: ON (PF first)
- A/T: ARM
- IAS: V2
- HEADING selector: runway heading
- LNAV: AS REQ
- VNAV: ARM
- ALTITUDE selector: HOLD DOWN ALTITUDE

FO EFIS:
- Same as CA EFIS

*Previous: Overhead Panel (Bottom Row)*  
*Next: Above Displays*