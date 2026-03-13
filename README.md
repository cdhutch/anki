# Anki Knowledge Repository

This repository is the **source of truth for structured knowledge used in Anki decks**.

All notes are stored as **canonical CNSF Markdown files** and are converted into Anki notes through a reproducible pipeline.

The design goals are:

- Git-controlled knowledge
- reproducible deck builds
- clean separation between **content**, **rendering**, and **Anki synchronization**
- support for multiple note models

---

# Quick Start (30-second summary)

To rebuild the B737 Electrical systems deck from canonical notes:

```bash
tools/anki/cnsf_to_anki.sh domains/b737/anki/notes/systems/electrical
```

This runs the full pipeline:

```
CNSF Markdown
      │
      ▼
HTML rendering
      │
      ▼
TSV export
      │
      ▼
AnkiConnect import
```

The resulting deck is rebuilt entirely from the repository.

---

# Repository Philosophy

This repo treats **Anki as a rendering target, not the source of truth**.

| Component | Role |
|---|---|
| Git repository | canonical knowledge store |
| CNSF Markdown | structured note format |
| Export pipeline | transforms notes into Anki format |
| Anki | spaced-repetition review interface |

This allows:

- version control for knowledge
- deterministic deck rebuilds
- large-scale refactoring of notes
- automated validation

---

# Pipeline Architecture

The pipeline converts CNSF notes into Anki notes using three stages.

```
CNSF Markdown
    │
    ▼
cnsf_to_import_tsv.py
    │
    ▼
TSV (Anki import format)
    │
    ▼
tsv_to_anki.py
    │
    ▼
AnkiConnect
    │
    ▼
Anki deck
```

### Stage 1 — Canonical validation

Ensures CNSF notes conform to required YAML structure.

```
tools/anki/cnsf_canonicalize.py
```

Checks include:

- YAML key ordering
- no blank lines in YAML
- required metadata fields

---

### Stage 2 — CNSF → TSV export

Script:

```
tools/anki/export/cnsf_to_import_tsv.py
```

Responsibilities:

- load CNSF notes
- render Markdown → HTML
- map CNSF fields to Anki fields
- output TSV file

Example:

```bash
python -m tools.anki.export.cnsf_to_import_tsv \
  --in domains/b737/anki/notes/systems/electrical \
  --out /tmp/cnsf_to_anki_import.tsv \
  --overwrite
```

---

### Stage 3 — TSV → Anki import

Script:

```
tools/anki/sync/tsv_to_anki.py
```

Responsibilities:

- read TSV export
- detect model fields
- create or update notes via AnkiConnect

Example:

```bash
python -m tools.anki.sync.tsv_to_anki /tmp/cnsf_to_anki_import.tsv
```

---

# Export Profiles

Export behavior is defined by **model-specific export profiles**.

Location:

```
tools/anki/export_profiles/
```

Example:

```
B737_Systems.yml
B737_Structured.yml
```

Profiles define how CNSF data maps to Anki fields.

Example:

```yaml
fields:
  note_id: note_id
  Front: front_html
  Back: back_html
  system: system
  subsystem: subsystem
  Source Document: fields.Source Document
  Source Location: fields.Source Location
  tags: tags_joined
```

This design allows the exporter to support **multiple note models without code changes**.

---

# CNSF Note Format

CNSF notes use structured YAML front matter followed by Markdown content.

Example:

```markdown
---
schema: cnsf/v0
domain: b737
note_type: system_concept
note_id: sys-elec-psc-010
anki:
  model: B737_Systems
  deck: B737::Systems
tags:
- domain:b737
- topic:systems
- system:electrical
- subsystem:ac_power
- scope:common
- status:unverified

system: "B737 Electrical"
subsystem: "AC Power"

fields:
  Source Document: "B737 Aircraft Systems Manual"
  Source Location: "Ch 6 §6.20.3"
---

# front_md

**B737 ELECTRICAL — AC POWER**

Which buses does each AC power system consist of?

# back_md

- Transfer bus
- Main bus
- Galley buses
```

---

# Systems Deck Workflow

Systems notes live here:

```
domains/b737/anki/notes/systems/
```

Example:

```
domains/b737/anki/notes/systems/electrical/sys-elec-psc-010.md
```

To rebuild the electrical deck:

```bash
tools/anki/cnsf_to_anki.sh domains/b737/anki/notes/systems/electrical
```

This wrapper runs:

1. canonical check
2. CNSF → TSV export
3. TSV → Anki import

---

# Rebuilding a Deck from Scratch

If duplicate errors occur during import:

1. Delete existing notes in Anki.

Search:

```
deck:"B737::Systems"
```

Delete all notes.

2. Re-run the pipeline.

```
tools/anki/cnsf_to_anki.sh domains/b737/anki/notes/systems/electrical
```

---

# Repository Layout

```
anki/
│
├─ domains/
│   └─ b737/
│       └─ anki/
│           └─ notes/
│               └─ systems/
│                   └─ electrical/
│
├─ tools/
│   └─ anki/
│       ├─ export/
│       │   └─ cnsf_to_import_tsv.py
│       │
│       ├─ sync/
│       │   └─ tsv_to_anki.py
│       │
│       ├─ extract/
│       │   └─ legacy extraction scripts
│       │
│       └─ export_profiles/
│           ├─ B737_Systems.yml
│           └─ B737_Structured.yml
│
└─ README.md
```

---

# Developer Guide

## Adding a new note model

1. Create a new export profile.

Example:

```
tools/anki/export_profiles/B737_Flows.yml
```

2. Define field mappings.

3. Ensure the Anki model fields match the profile.

No exporter code changes are required.

---

## Adding new notes

1. Create CNSF Markdown file.

2. Validate canonical form.

```
tools/anki/cnsf_canonicalize.py --check <file>
```

3. Commit to repository.

4. Rebuild deck.

---

# Key Scripts

| Script | Purpose |
|---|---|
| `cnsf_canonicalize.py` | enforce canonical YAML |
| `cnsf_to_import_tsv.py` | convert CNSF → TSV |
| `tsv_to_anki.py` | upload TSV to Anki |
| `cnsf_to_anki.sh` | wrapper for full pipeline |

---

# Long-Term Direction

Planned extensions:

- flows deck
- memory items deck
- maneuver cards
- automated validation of note completeness

The goal is a **fully reproducible aviation knowledge system built on Git**.