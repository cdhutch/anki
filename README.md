# Anki Knowledge Repository

This repository is the **source of truth for structured knowledge used
in Anki decks**.

All notes are stored as **canonical CNSF Markdown files** and are
converted into Anki notes through a reproducible pipeline.

The design goals are:

-   Git-controlled knowledge
-   reproducible deck builds
-   clean separation between **content**, **rendering**, and **Anki
    synchronization**
-   support for multiple note models

------------------------------------------------------------------------

# Quick Start (30‑second summary)

To rebuild the B737 Electrical systems deck from canonical notes:

``` bash
tools/anki/cnsf_to_anki.sh domains/b737/anki/notes/systems/electrical
```

Pipeline:

CNSF Markdown → TSV export → AnkiConnect import

------------------------------------------------------------------------

# Repository Philosophy

This repo treats **Anki as a rendering target, not the source of
truth**.

  Component         Role
  ----------------- ------------------------------------
  Git repository    canonical knowledge store
  CNSF Markdown     structured note format
  Export pipeline   transforms notes into Anki format
  Anki              spaced‑repetition review interface

Benefits:

-   version control for knowledge
-   deterministic deck rebuilds
-   large‑scale refactoring
-   automated validation

------------------------------------------------------------------------

# Pipeline Architecture

CNSF notes are transformed into Anki notes using a simple three‑stage
pipeline.

CNSF Markdown\
↓\
TSV export\
↓\
AnkiConnect import

------------------------------------------------------------------------

# Makefile Commands

The repository includes a **Makefile workflow for building and importing
B737 Systems Verification (SV) decks**.

Systems Verification notes live here:

    domains/b737/anki/notes/systems_verification/

------------------------------------------------------------------------

## Validate notes

Validate canonical CNSF formatting without modifying files.

``` bash
make sv-check
```

This runs:

    tools/anki/cnsf_canonicalize.py --check

Checks include:

-   YAML key ordering
-   required metadata
-   canonical CNSF formatting

If violations exist, the command exits with an error.

------------------------------------------------------------------------

## Build and import all Systems Verification decks

``` bash
make sv
```

Pipeline executed by this command:

CNSF Markdown\
↓\
Canonical validation\
↓\
Fresh TSV generation\
↓\
AnkiConnect import

Important behavior:

-   **TSV files are rebuilt every time `make sv` runs**
-   This ensures **changes in `.md` files always overwrite cards in
    Anki**
-   Previously generated TSV files are overwritten automatically

Generated TSV files are written to:

    build/

Examples:

    build/sv-general.tsv
    build/sv-air_conditioning.tsv
    build/sv-hydraulics.tsv
    build/sv-electrical.tsv

These files are **temporary build artifacts and should not be
committed**.

------------------------------------------------------------------------

# Typical Workflow

Edit notes:

    edit Markdown files
          ↓
    make sv
          ↓
    Anki updated

Optional validation step:

    make sv-check
    make sv

------------------------------------------------------------------------

# Key Scripts

  Script                   Purpose
  ------------------------ -------------------------
  `cnsf_canonicalize.py`   enforce canonical YAML
  `sv_md_to_tsv.py`        convert CNSF → TSV
  `sv_import_to_anki.py`   import TSV to Anki
  `cnsf_to_anki.sh`        legacy wrapper pipeline

------------------------------------------------------------------------

# Long‑Term Direction

Planned extensions:

-   flows deck
-   memory items deck
-   maneuver cards
-   automated validation of note completeness

The goal is a **fully reproducible aviation knowledge system built on
Git**.
