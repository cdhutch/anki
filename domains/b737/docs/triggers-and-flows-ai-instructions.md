# AI Instructions — B737 Triggers & Flows Recall Card Expansion

## Goal

Create additional Anki/CNSF trigger-and-flow study cards to supplement the existing trigger cards.

The existing trigger cards already ask:

- Front: flow / procedure
- Back: trigger

Do not duplicate those.

Create new cards in three categories:

1. Phase recall cards
2. Mnemonic expansion cards
3. Sequence cards

## Source Material

The AI has access to the AOM in:

`~/Documents/GitHub/anki/domains/b737/anki/sources/`

The existing triggers and flows notes are in:

`~/Documents/GitHub/anki/domains/b737/anki/notes/triggers_and_flows/`

Use existing notes as formatting and YAML models.

## Macro Flight Timeline

Use this master timeline:

1. Preflight
2. Pushback / Start
3. Taxi
4. Takeoff
5. Departure
6. Enroute
7. Arrival
8. After Landing
9. Shutdown

Mnemonic:

**Cold Jet → Move → Roll → Fly → Cruise → Down → Land → Park**

## Procedure / Flow Outline

### Preflight
- Electrical Power Up Procedure
- IRS Alignment
- Origination Flow
- FMS Preflight
- Exterior Inspection
- Route Verification
- Leg Verification
- Performance Verification
- Departure Briefing
- Preflight Flow
- Before Start Flow
- Before Pushback Flow
- Before Start Checklist

### Pushback / Start
- After Start Flow
- After Start Checklist

### Taxi
- Load Closeout Review
- Before Takeoff Flow
- Before Takeoff Checklist to the line
- Before Taking Runway Flow
- Before Takeoff Checklist below the line

### Takeoff
- After Takeoff Flow
- After Takeoff Checklist

### Departure
- Climbing Through 10K' Flow
- Transition Altitude Flow

### Enroute — PF Cruise
- Minimum Drag Trim Setting
- Standard Descent Speed
- FMS+
- Update Cruise Winds
- Enter Descent Forecast

### Enroute — PM Cruise
- Center Fuel Pumps
- Initial Climb / Cruise PA
- Fuel Log
- Depressurization Routes
- Company Position Report

### Enroute — PF Prior to TOD
- Load Arrival in FMS
- Approach Preparation
- Autobrakes
- Terrain Display
- Engine Anti-Ice

### Enroute — PM Prior to TOD
- Mechanical Discrepancy Notifications
- ATIS
- Approach Preparation
- Pressurization
- Recall Check
- Terrain Display
- Changeover Report
- Before Descent Announcement

### After FMS Loaded
- Landing Performance Assessment
- Arrival Briefing

### Arrival
- Descent Flow
- Descent Checklist
- Transition Level Flow
- Before Landing Flow
- Before Landing Checklist to the Line
- Approach

### After Landing
- After Landing Flow

### Shutdown
- Shutdown Flow
- Shutdown Checklist
- Crew Debriefing
- Post Flight Inspection
- Secure Checklist

## Card Type 1 — Phase Recall Cards

Create cards that ask what procedures belong to a macro phase.

Example:

Front:
“What procedures belong to the Taxi phase?”

Back:
- Load Closeout Review
- Before Takeoff Flow
- Before Takeoff Checklist to the line
- Before Taking Runway Flow
- Before Takeoff Checklist below the line

Use one card per macro phase.

Keep lists short where possible. If a phase is too long, split by role or subphase.

## Card Type 2 — Mnemonic Expansion Cards

Create cards that ask the user to expand a mnemonic.

Suggested mnemonics:

- Preflight: **Power → Program → Inspect → Plan → Configure**
- Pushback / Start: **Start → Stabilize**
- Taxi: **Paperwork → Configure → Runway**
- Takeoff: **Clean Up**
- Departure: **Ten → Transition**
- PF Cruise: **Trim → Speed → Box → Winds → Descent**
- PM Cruise: **Fuel → PA → Log → Escape → Report**
- Prior to TOD: **Arrival → Weather → Landing → Brief**
- Arrival: **Down → Transition → Landing → Approach**
- Shutdown: **Stop → Review → Inspect → Secure**

Each mnemonic card should include:
- mnemonic phrase
- expanded meaning
- associated procedures

## Card Type 3 — Sequence Cards

Create sequence cards that ask what comes before or after a flow/procedure.

Examples:

Front:
“What comes after Before Takeoff Checklist to the line?”

Back:
“Before Taking Runway Flow.”

Front:
“What comes before After Start Checklist?”

Back:
“After Start Flow.”

Create sequence cards primarily at phase boundaries and checklist/flow boundaries.

Avoid excessive cards for every single item unless the sequence is operationally important.

## Naming and Tagging

Use filenames that distinguish the new supplemental cards from existing trigger cards.

Recommended prefixes:

- `phase-recall-<phase>.md`
- `mnemonic-<phase>.md`
- `sequence-<phase-or-boundary>.md`

Use tags such as:

- `domain:b737`
- `topic:triggers-and-flows`
- `type:phase_recall`
- `type:mnemonic`
- `type:sequence`
- `phase:<phase_name>`
- `status:unverified`

## Quality Rules

- Do not invent AOM content.
- Use the pasted outline as the controlling sequence unless the AOM or existing notes clearly contradict it.
- If the AOM/source conflicts with the outline, flag the discrepancy rather than silently changing it.
- Keep each card focused on one recall task.
- Avoid duplicating the existing trigger cards.
- Prefer short answers that support memorization.
- Preserve existing CNSF/YAML conventions from nearby files.
- Canonicalize notes before staging.
- Run the existing trigger/flow linter if applicable.

## Additional Things to Add

Ask the AI chatbot to also create:

1. **Boundary cards**
   - last item in one phase → first item in next phase

2. **Role-specific enroute cards**
   - PF Cruise
   - PM Cruise
   - PF Prior to TOD
   - PM Prior to TOD

3. **Checklist pairing cards**
   - flow → checklist
   - checklist to the line → below the line

4. **Gap-detection report**
   - list any procedures in the pasted outline that do not have corresponding existing trigger cards

5. **Duplicate-detection report**
   - list any proposed supplemental cards that would duplicate existing cards

6. **Commit strategy**
   - first commit: documentation / plan
   - second commit: generated draft cards
   - third commit: validated cards after review

## Final Instruction

Before writing notes, produce a proposed card inventory grouped by:

- phase recall
- mnemonic expansion
- sequence / boundary

Wait for user approval before creating files.