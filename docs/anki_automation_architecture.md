# Anki Automation Architecture (B737 + Ukrainian)

## Purpose

This document defines the architecture for managing Anki notes via Git and Python automation.

It serves as the canonical explanation of:

- Repository structure
- Canonical sources (Markdown / TSV)
- Tag governance
- Update workflows
- Safety guarantees

This file should be provided to any LLM session working on this repo.

---

# Core Principles

## 1. The Repository Is the Source of Truth

All important note content and metadata must be reproducible from the repo.

This includes:

- Core note fields (Answer, Pattern, etc.)
- Canonical Markdown backs
- Metadata tags
- Workflow state (e.g., unverified / verified)

Anki is treated as a runtime execution environment, not the primary authoring location.

---

## 2. Deterministic Updates

All automation must be:

- Idempotent
- Reproducible
- Namespace-safe
- Non-destructive to manual tags outside managed prefixes

No hidden state should exist only inside Anki.

---

# Directory Architecture

## B737 Domain

```
domains/b737/
  anki/
    sources/        # canonical Markdown (systems, limits)
    exports/        # TSV intermediates (ignored in git)
    generated/      # HTML intermediates (ignored)
  systems/
    _scratch/       # working TSV datasets (not merged)
```

## Ukrainian Domain

```
domains/ua/
  anki/
    sources/        # canonical Markdown (grammar)
    exports/        # generated TSV (ignored)
    generated/      # generated HTML (ignored)
  lexeme/           # TSV-first datasets
  grammar/          # optional structured TSV datasets
```

---

# Canonical Note Sources

## Two Supported Authoring Modes

### A) Canonical Markdown (MD-first)

Used for:
- B737 Systems
- B737 Limits
- UA_Grammar (recommended)

Workflow:

```
canonical.md
  → md_to_html.py
  → html_after_to_tsv.py
  → merge_base_and_after.py
  → update_notes_from_tsv.py
  → AnkiConnect
```

Markdown is human-authored and version-controlled.

---

### B) TSV-first

Used for:
- UA_Lexeme
- Structured datasets

Workflow:

```
dataset.tsv
  → update_notes_from_tsv.py
  → AnkiConnect
```

TSV is canonical for structured field-heavy notes.

---

# Note_ID Policy

All managed note types must include:

```
Note_ID
```

This is a stable key used to map:

```
Repo note  →  Anki noteId
```

Never rely on Lemma, Title, or Prompt for deterministic mapping.

---

# Tag Governance

## Canonical Tag Field

```
Tags_Ch
```

This field is the canonical metadata container inside the repo.

Format:

```
semicolon-separated tokens
```

Example:

```
textbook:яблуко; ch:2.8.6; sensory; appearance; wf:unverified
```

---

## Managed Tag Namespaces

Automation manages only these prefixes:

| Prefix | Meaning |
|--------|---------|
| src:   | Source metadata (textbook, chapter) |
| topic: | Semantic/topic tags |
| wf:    | Workflow state |

---

## Canonical → Anki Tag Mapping

From `Tags_Ch`:

```
textbook:яблуко  →  src:textbook:яблуко
ch:2.8.6         →  src:ch:2.8.6
appearance       →  topic:appearance
wf:unverified    →  wf:unverified
```

---

## Safety Rule

When syncing tags:

1. Fetch current Anki tags.
2. Remove only tags beginning with:
   - `src:`
   - `topic:`
   - `wf:`
3. Add newly computed managed tags.
4. Leave all other tags untouched.

This guarantees:
- Manual tags survive.
- Repo-managed tags are deterministic.

---

# Tag Utilities

Located at:

```
tools/anki/tag_utils.py
```

Provides:

- Canonical tag parsing
- Namespace mapping
- Normalization
- Managed-prefix stripping

---

# Pipeline Components

Located in:

```
tools/anki/
```

Key scripts:

- md_to_html.py
- html_after_to_tsv.py
- merge_base_and_after.py
- update_notes_from_tsv.py
- validate_canonical_md.py
- pipeline.py
- tag_utils.py

---

# What Is Managed vs Not Managed

## Managed by Repo

- Note_ID
- Canonical MD content
- TSV datasets
- Tags_Ch
- Workflow tags (wf:)
- Source tags (src:)
- Topic tags (topic:)

## Not Managed (Safe to Edit in Anki)

- Temporary personal tags outside managed prefixes
- Scheduling data
- Ease factors
- Review history

---

# Unverified Policy

Notes containing:

```
wf:unverified
```

must not be merged into `main` unless verified.

Pre-commit hooks may warn but not block.

---

# Why This Architecture Exists

This design ensures:

- Cross-domain consistency (B737 + UA)
- Deterministic regeneration
- LLM-friendly structured context
- Zero hidden metadata
- Version control of everything important
- Safety during tag sync

---

# Future Enhancements

Planned:

- Add --update-tags flag to update script
- Add --dry-run for tag diff preview
- Add config-driven note-type mappings
- Add export-from-Anki canonical rebuild mode
- Add LLM-assisted migration tools for legacy notes

---

# Instructions for LLM Sessions

When working in a new ChatGPT session:

1. Treat this file as authoritative.
2. Treat the repo as canonical.
3. Never propose tag changes outside managed prefixes.
4. Always preserve deterministic mapping via Note_ID.
5. Never suggest manual tag editing as a primary workflow.

---

# Summary

The repository is the source of truth.

Anki is a runtime projection.

Tags are namespace-managed and reproducible.

All updates must be deterministic.
