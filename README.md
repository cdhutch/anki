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

---

# Makefile Commands

The repository includes a **Makefile-based workflow** for building and importing the **B737 Systems Verification (SV)** decks.

## Validate SV notes

```bash
make sv-check
```

Runs canonical validation on all systems verification notes.

---

## Build and import all SV decks

```bash
make sv
```

Pipeline:

```
CNSF Markdown
      │
      ▼
canonical validation
      │
      ▼
TSV generation
      │
      ▼
Anki import
```

Generated TSV files are written to:

```
build/
```

Example:

```
build/sv-general.tsv
build/sv-adverse.tsv
build/sv-flight_warning.tsv
build/sv-gpws.tsv
build/sv-air_conditioning.tsv
```

These TSV files are **intermediate build artifacts** and should not be committed.

---

# Long-Term Direction

Planned extensions:

- flows deck
- memory items deck
- maneuver cards
- automated validation of note completeness

The goal is a **fully reproducible aviation knowledge system built on Git**.
