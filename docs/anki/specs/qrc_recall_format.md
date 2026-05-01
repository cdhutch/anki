# B737 QRC Recall Format Specification

## Purpose
This document defines the canonical formatting rules for B737 QRC Recall items
within the CNSF → Anki pipeline.

---

## 1. General Principles

- Preserve **verbatim procedural intent**
- Maintain **pipeline stability** (MD → HTML → TSV → Anki)
- Separate **content** from **presentation**
- Optimize for **high-stress recall readability**

---

## 2. YAML Frontmatter Requirements

Each note MUST include:

- schema: cnsf/v0
- domain: b737
- note_type: qrc_recall
- note_id: unique slug
- anki.model: B737_Structured
- anki.deck: B737::Core::QRC::Recall

---

## 3. Front Content

Format:

**<TITLE>**

Recall items?

Rules:
- Title in bold
- No additional hints
- No procedural leakage

---

## 4. Back Content Structure

### 4.1 Title Reinforcement
Repeat title at top of back:

**<TITLE>**

---

### 4.2 Primary Steps

- Use numbered list (1, 2, 3…)
- No trailing periods unless required
- Format:

Action ... Result

Example:
Autopilot (if engaged) ... Disengage

---

### 4.3 Ellipses Standard

Use:
...

DO NOT use:
- aligned dots (........)
- dashes (—)

---

### 4.4 Subordinate Logic

- Use dash (-)
- Indent with 2 spaces

Example:
4. Set configuration:
   - Flaps extended ... 10° and 80% N1
   - Flaps up ... 4° and 75% N1

---

### 4.5 Conditional Logic

Use bold emphasis:

**If** condition **continues**

Example:
**If** the runaway **continues**

---

### 4.6 QRC Break Symbol

Standard:

■ ■ ■ ■

Rules:
- Must be on its own line
- One blank line before and after
- Used only for major logical separation

---

## 5. Capitalization Rules

- Preserve source capitalization
- Do NOT force ALL CAPS
- Use mixed case unless source dictates otherwise

---

## 6. Punctuation Rules

- Avoid unnecessary periods
- Maintain imperative style
- Keep phrasing concise

---

## 7. Styling Rules (Anki Template Only)

- No inline HTML styling in Markdown
- Apply color (e.g., red) via CSS in card template
- Styling must be tied to note_type (qrc_recall)

---

## 8. File Organization

Store files in:

docs/anki/qrc_recall/

File naming:

qrc-<slug>.md

---

## 9. Version Control Considerations

- Avoid formatting that creates noisy diffs
- Maintain consistent indentation
- Keep symbols and spacing standardized

---

## 10. Future Extensions

- CSS-based rendering of QRC symbols
- Conditional styling (title vs full content)
- Automated validation scripts for format compliance
