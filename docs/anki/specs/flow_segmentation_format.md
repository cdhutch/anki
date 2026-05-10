# B737 Flow Segmentation Format Specification

## Purpose
This document defines the canonical formatting and segmentation rules for B737
Flow items within the CNSF → Anki pipeline.

---

## 1. General Principles

- Separate **trigger recognition** from **flow execution**
- Preserve **procedural intent**
- Maintain **pipeline stability** (MD → HTML → TSV → Anki)
- Optimize for **cockpit-usable mental chunking**
- Prefer **spatial segmentation** over oversized monolithic cards

---

## 2. Deck Architecture

Triggers and Flows MUST live in separate child decks under a common parent:

- `B737::Core::Triggers_and_Flows::Triggers`
- `B737::Core::Triggers_and_Flows::Flows`

Rules:
- Trigger notes answer: **When do I do this?**
- Flow notes answer: **What do I do?**

---

## 3. YAML Frontmatter Requirements

Each Flow note MUST include:

- `schema: cnsf/v0`
- `domain: b737`
- `note_type: flow`
- `note_id: unique slug`
- `anki.model: B737_Structured`
- `anki.deck: B737::Core::Triggers_and_Flows::Flows`

Recommended tags include:

- `domain:b737`
- `topic:triggers_and_flows`
- `type:flow`
- `flow:<name>`
- `segment:<segment_name>`
- `sequence:<nn>`
- `source:<source_name>`
- `status:verified` or `status:unverified`

---

## 4. Segmentation Principles

### 4.1 Segmentation Objective

Flows SHOULD be divided into cards that are:
- operationally coherent
- spatially meaningful
- short enough for efficient recall
- large enough to preserve procedural context

---

### 4.2 Preferred Segmentation Basis

Long flows SHOULD be segmented by **cockpit area / physical zone**, not by
arbitrary line count.

Preferred examples:
- Emergency Equipment
- Aft Overhead
- Pedestal
- Floor Systems

Avoid:
- random split by number of bullets
- splitting without regard to cockpit geography
- giant single-card flows when multiple spatial chunks exist

---

### 4.3 Secondary Segmentation Basis

When one cockpit zone is still too large, it MAY be subdivided by functional
subgroup inside that zone.

Example:
- Aft Overhead — Configuration
- Aft Overhead — Tests

This is preferred to creating one oversized “Aft Overhead” card.

---

## 5. Trigger / Flow Relationship

Architecture rules:

- one Trigger note per flow
- at least one Flow note per flow
- one Trigger may point conceptually to multiple segmented Flow cards
- segmented Flow cards together represent the executable sequence for that flow

---

## 6. Naming Conventions

### 6.1 File Names

Flow file names MUST reflect actual note purpose.

Format:

`flow-<flow-name>-<segment-name>.md`

Examples:
- `flow-origination-emergency-equipment.md`
- `flow-origination-aft-overhead-configuration.md`
- `flow-origination-aft-overhead-tests.md`
- `flow-origination-pedestal.md`
- `flow-origination-floor-systems.md`

---

### 6.2 Note IDs

`note_id` MUST match the file’s semantic purpose and SHOULD match the filename
stem exactly.

Examples:
- `note_id: flow-origination-emergency-equipment`
- `note_id: flow-origination-pedestal`

---

## 7. Front Content

Format:

**<FLOW TITLE>**

What is your flow?

Rules:
- Title in bold
- Prompt should be generic and stable
- No extra hints that reveal downstream steps
- Segment identity belongs in the title

Example:

**Origination Flow — Pedestal**

What is your flow?

---

## 8. Back Content Structure

### 8.1 Title Reinforcement

Repeat title at top of back:

**<FLOW TITLE>**

---

### 8.2 Step Presentation

- Use unordered bullet list unless strict numbering is operationally necessary
- Keep items concise
- Preserve operational wording
- Avoid unnecessary punctuation

Example:
- Stab trim cutout switches NORMAL
- Parking brake SET
- Engine start levers CUTOFF

---

### 8.3 Embedded Substeps

Use nested bullets for subordinate items.

Example:
- All lights out except:
  - GEAR LIGHTS × 3
  - FLIGHT RECORDER
  - IRS ALIGN

---

### 8.4 Sequence Bridging

Segmented flow cards SHOULD include minimal context linking them to adjacent
segments.

Preferred format at bottom of back:
- *Previous: <segment name>*
- *Next: <segment name>*

This context must orient sequence without restating the entire flow.

---

## 9. Title and Segment Naming Rules

Titles SHOULD include:
- flow name
- segment or zone
- optional functional qualifier when needed

Examples:
- `Origination Flow — Emergency Equipment`
- `Origination Flow — Aft Overhead (Configuration)`
- `Origination Flow — Aft Overhead (Tests)`
- `Origination Flow — Pedestal`

Titles should be:
- operationally clear
- spatially meaningful
- stable over time

---

## 10. Capitalization and Punctuation Rules

- Preserve source capitalization where operationally important
- Do NOT force ALL CAPS unless source requires it
- Avoid unnecessary periods
- Keep checklist phrasing concise and imperative where applicable

---

## 11. Styling Rules (Anki Template Only)

- No inline HTML styling in Markdown
- Presentation belongs in the Anki template / CSS layer
- Styling may later distinguish `note_type: flow` from other note types

---

## 12. File Organization

Store flow notes in:

`domains/b737/anki/notes/triggers_and_flows/`

File naming must distinguish trigger and flow purpose clearly.

---

## 13. Pilot Example: Origination Flow

The Origination Flow is the pilot implementation for this segmentation model.

Canonical segmented flow cards:

1. `flow-origination-emergency-equipment.md`
2. `flow-origination-aft-overhead-configuration.md`
3. `flow-origination-aft-overhead-tests.md`
4. `flow-origination-pedestal.md`
5. `flow-origination-floor-systems.md`

This set establishes the baseline rule:
- segment long flows spatially first
- subdivide within a zone only when needed for recallability

---

## 14. Version Control Considerations

- Prefer stable naming
- Avoid formatting that creates noisy diffs
- Keep indentation and bullet structure consistent
- Keep sequence metadata predictable through tags and filenames

---

## 15. Future Extensions

- formal Trigger specification parallel to this document
- automated validation for segment naming and sequence tags
- optional parent/child linkage conventions between trigger and flow notes
- heuristics for maximum recommended flow card length