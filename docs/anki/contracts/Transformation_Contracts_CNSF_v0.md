# Transformation Contracts (CNSF v0 → Anki)

This document defines **adjacent-step contracts** for your Git-backed Anki system, based on the **CNSF v0** schema.

## Levels

**L1 — CNSF Note Markdown (canonical source)**
- File: `domains/<domain>/anki/notes/<note_type>/<note_id>.md`
- 1:1 mapping: **one file = one Anki note**
- Must contain:
  - YAML front matter (metadata + non-Front/Back fields)
  - Section bodies for `front_md` and `back_md`

**L2 — Rendered HTML**
- File: `domains/<domain>/anki/generated/<note_id>.html` (optional per-note; can be cacheable)
- Produced from `front_md` and `back_md` using **MultiMarkdown (Fletcher Penney)** when available.

**L3 — Import TSV (HTML payload)**
- File: `domains/<domain>/anki/exports/<note_type>__import_html.tsv`
- One row per note.
- Required columns:
  - `note_id` (string, matches YAML `note_id`)
  - `noteId` (Anki internal numeric ID; blank for create flows)
  - `model` (Anki note type/model name)
  - `deck` (target deck name)
  - `tags` (space-separated tags)
  - `front_html`
  - `back_html`
  - plus any extra fields for that model (e.g., `Source Document`, `Source Location`, `Verification Notes`)

**L4 — Anki (via AnkiConnect)**
- Create/update notes, set tags, and write all fields.

---

## Contract 1 — L1 → L2 (CNSF Markdown → HTML)

### Input (L1)
A single `.md` file with:

```yaml
---
schema: cnsf/v0
domain: b737
note_type: limits_weight_model
note_id: b737-limits-weight-800
anki:
  model: B737_Structured
  deck: "B737::Limits"
tags:
  - domain:b737
  - model:800
  - topic:limits
  - subtopic:weight
  - source:aom
  - status:unverified
fields:
  Source Document: "B737 AOM Rev 9.0"
  Source Location: "Ch 18 §18.2.3 Weight Limits (Certificated Limits table)"
  Verification Notes: ""
---
# front_md
...markdown...

# back_md
...markdown...
```

### Output (L2)
Two HTML fragments **or** a single HTML bundle that can be split deterministically:
- `front_html` (rendered from `front_md`)
- `back_html` (rendered from `back_md`)

### Rules
- Renderer MUST be **MultiMarkdown** if found on PATH:
  - probe `multimarkdown` or `mmd` executable
- Otherwise fallback to a secondary renderer (Python markdown), and annotate output with:
  - `<!-- renderer: python-markdown fallback -->`

### Deterministic rendering requirements
- No network calls
- Stable output given same input + same renderer version
- Tables must be rendered as `<table>…</table>` and preserve order

---

## Contract 2 — L2 → L3 (HTML fragments → Import TSV)

### Input
- `note_id`
- optional `noteId`
- `model`, `deck`, `tags`
- `front_html`, `back_html`
- extra fields

### Output
TSV row with required columns and model-specific columns.

### Rules
- TSV is UTF-8, `\t` delimiter, `\n` row separator
- HTML is stored raw; embedded newlines are allowed
- If `noteId` is missing, row is valid **only for CREATE flow**

---

## Contract 3 — L3 → L4 (Import TSV → AnkiConnect)

Two subflows:

### Update flow
Requires `noteId` (numeric).
Actions:
1) `updateNoteFields` for all provided fields (including Front/Back)
2) `addTags` and/or `removeTags` according to tag policy

### Create flow
If `noteId` is blank:
1) `addNote` with:
   - `deckName`
   - `modelName`
   - `fields`
   - `tags`
2) Record returned Anki `noteId` into a **mapping TSV**:
   - `domains/<domain>/anki/mapping/<note_type>__noteid_map.tsv`
   - columns: `note_id`, `noteId`

---

## Contract 4 — Reverse sync (Anki → Repo)

This is optional but recommended for legacy migration.

### Export
- query notes by `note_id` field value or tag selector
- write TSV with all fields + tags
- (optionally) regenerate CNSF files by template for review, never auto-overwrite without diff

---

## Note Type naming policy (underscores)

### Goal
Repo + Anki names match 1:1 and are machine-friendly:
- Anki model: `B737_Structured`, `UA_Lexeme`, `UA_Grammar`
- CNSF note_type identifiers: `b737_limits_weight_model`, `ua_lexeme`, `ua_grammar`

### Migration approach (recommended)
- **Do not rename existing Anki models in place** until you have a migration script.
- Instead:
  1) Create new models with underscore names
  2) Bulk-migrate notes by exporting TSV and re-importing into the new model
  3) Delete old models only after validation

(If you do want in-place rename, do it once, early, and back up your collection first.)

---

## Minimal scripts to implement contracts

Place these under `tools/anki/`:

1) `cnsf_parse.py`
- Parse YAML front matter + extract `front_md` and `back_md`

2) `md_to_html_mmd.py`
- Render markdown to HTML using MultiMarkdown if available
- Provide renderer provenance in output

3) `cnsf_to_import_tsv.py`
- Walk note tree, render each note, emit import TSV

4) `sync_to_anki.py`
- Apply TSV: create or update
- Maintain mapping TSV (note_id ↔ noteId)
- Apply tag policy via `tag_utils.py`

---

## Acceptance tests

For a given note:
- `front_html` contains the expected table headers and blank placeholders
- `back_html` contains the numeric values
- After sync, `cardsInfo` shows Front/Back fields match HTML (normalized whitespace ok)
