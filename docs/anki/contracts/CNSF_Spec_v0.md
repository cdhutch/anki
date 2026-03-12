# CNSF Spec v0 (Canonical Note Source Format)

This document defines the **canonical, repo-owned note file format**
used to generate, validate, and sync Anki notes for **all domains**
(e.g., `b737`, `ua`).

-   Schema identifier remains: `schema: cnsf/v0`
-   This spec tightens rules (naming + delimiters + validation) without
    introducing a new schema version.

------------------------------------------------------------------------

## Goals

1)  **1:1 mapping** --- one file corresponds to one Anki note.\
2)  **Deterministic transforms** --- same input yields same outputs
    (HTML/TSV).\
3)  **Domain-agnostic** --- works for B737 and Ukrainian note types.\
4)  **Repo is source of truth** --- tags, sources, and field payloads
    live in the repo.

------------------------------------------------------------------------

## File location and 1:1 mapping

Each note is a single Markdown file:

    domains/<domain>/anki/notes/<note_type>/<note_id>.md

-   `<domain>` is a short identifier (e.g., `b737`, `ua`)
-   `<note_type>` is the **CNSF note type** identifier (underscores
    only)
-   `<note_id>` is the **canonical note ID** (lowercase tokens separated
    by hyphens or underscores)

**1 file = 1 Anki note**.

------------------------------------------------------------------------

## Required structure

A CNSF note file has:

1)  YAML front matter (metadata + non-front/back fields)\
2)  A `# front_md` section\
3)  A `# back_md` section

Example skeleton:

``` yaml
---
schema: cnsf/v0
domain: b737
note_type: limits_weight_model
note_id: b737_limits_weight_800

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

aliases:
  - b737-limits-weight-800
---

# front_md
...markdown...

# back_md
...markdown...
```

------------------------------------------------------------------------

## Canonical naming grammar

### Repo identifiers

-   `note_type` **must use underscores only**
-   `note_id` **may use hyphens or underscores**
-   Filenames must match `note_id` exactly

### Allowed character set

    [a-z0-9_-]

### Recommended patterns

Preferred style for `note_id` is **kebab-case (hyphens)**:

    lim-wind-026
    lim-spd-007
    lim-wt-002-max

Underscores remain allowed for legacy compatibility:

    lim_wind_026
    lim_spd_007

------------------------------------------------------------------------

# Canonical `note_id` grammar (domain-scoped)

To maintain consistency across domains and allow deterministic tooling,
`note_id` values follow a **structured token grammar**.

General form:

    <category>-<topic>-<identifier>[-<variant>]

Tokens are lowercase and separated by hyphens.

Underscores remain allowed for legacy compatibility but **new IDs SHOULD
use hyphens**.

------------------------------------------------------------------------

## Category tokens

Each domain defines a short **category prefix**.

  Category    Meaning
  ----------- ----------------------------
  `lim`       Aircraft limitations
  `sys`       Aircraft systems knowledge
  `flow`      Cockpit flows
  `callout`   Standard callouts
  `man`       Maneuvers / memory scripts
  `ua`        Ukrainian language notes

------------------------------------------------------------------------

## B737 domain conventions

### Limits

    lim-<subject>-<index>

Examples:

    lim-alt-001
    lim-spd-003
    lim-wind-026
    lim-wt-002-max

Variant tokens may indicate aircraft models:

    lim-wt-001-800
    lim-wt-001-max

Grouped tables:

    lim-wind-ldg-rcc-models

------------------------------------------------------------------------

### Systems

    sys-<system>-<concept>

Examples:

    sys-elec-ac-bus-loss
    sys-hyd-pump-b
    sys-fuel-crossfeed
    sys-yaw-damper-power

------------------------------------------------------------------------

### Flows

    flow-<crew>-<phase>

Examples:

    flow-fo-before-start
    flow-capt-after-start
    flow-fo-secure

------------------------------------------------------------------------

### Callouts

    callout-<phase>-<trigger>

Examples:

    callout-takeoff-80-knots
    callout-takeoff-v1
    callout-approach-minimums

------------------------------------------------------------------------

### Maneuvers

    man-<maneuver>

Examples:

    man-windshear-escape
    man-rejected-takeoff
    man-single-engine-go-around

------------------------------------------------------------------------

## Stability guarantees

The following identifiers must remain stable once published:

-   `note_id`
-   file path
-   mapping to Anki notes

Renaming requires a migration step.

------------------------------------------------------------------------

## Tags policy (canonical in repo)

`tags:` in CNSF is canonical and synchronized to Anki.

Examples:

    domain:b737
    topic:limits
    subtopic:weight
    model:max8
    source:aom
    status:unverified

Verification status tags:

    status:unverified
    status:verified

------------------------------------------------------------------------

## Fields policy (non-front/back)

`fields:` stores non‑Front/Back model fields.

Example fields:

    Source Document
    Source Location
    Verification Notes

------------------------------------------------------------------------

## Front/back ownership

`# front_md` and `# back_md` are the canonical source for Anki
Front/Back fields.

Card templates should provide static elements (e.g., source footer).

------------------------------------------------------------------------

## Renderer requirement

Preferred renderer:

**Fletcher Penney MultiMarkdown** (`multimarkdown` or `mmd`).

Fallback renderers must:

-   emit warnings
-   remain deterministic
-   annotate fallback outputs.

------------------------------------------------------------------------

## Validation rules

A validator must fail when:

-   YAML front matter missing
-   required keys missing
-   identifier grammar violated
-   missing `front_md` or `back_md`
-   file path mismatches metadata

Recommended warnings:

-   missing `domain:<domain>` tag
-   missing verification status tag

------------------------------------------------------------------------

## Mapping to Anki

Canonical identifier: `note_id`

Linkage options:

-   Anki field `NoteID`
-   mapping TSV (`note_id` ↔ Anki internal ID)

Legacy hyphen IDs may be mapped using `aliases`.

------------------------------------------------------------------------

## Versioning

Schema identifier remains **cnsf/v0**.

Future incompatible changes require **cnsf/v1**.
