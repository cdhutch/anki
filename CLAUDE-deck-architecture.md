# Deck Architecture

**Rule**: Never study from `B737` (root) directly — it bypasses pool limits.

## Pool 1 — Systems (study from `B737::Systems`)

**Preset: B737 Systems (FSRS)** — 40 new/day
- `B737::Systems::Aircraft_Systems` (General systems)
  - `B737::Systems::Aircraft_Systems::Electrical`
  - `B737::Systems::Aircraft_Systems::Engines`

**Preset: B737 Systems SV (FSRS)** — 40 new/day
- `B737::Systems::Systems_Verification` (MCQ exam format)
  - `B737::Systems::Systems_Verification::Draft` (suspended cards)
  - `B737::Systems::Systems_Verification::Verified` (active study)

## Pool 2 — Flows & Procedures (study from `B737::Flows`)

**Preset: B737 Flows (FSRS)** — 20 new/day · override tags
- Flow bookends (first/last action; `always_show` tag)
- Flow detail (discretionary; `always_hide` when paused)

## Pool 3 — Knowledge Base (study from `B737::Knowledge_Base`)

**Preset: B737 Knowledge (FSRS)** — 20 new/day
- System deep-dives, troubleshooting, reference

---

**SV Exam Preset** — 100 new/day · 9999 reviews/day · FSRS on · 90% desired retention
