# Anki Automation Repository --- Branch Naming Convention

## Purpose

This document defines the official branch naming convention for the Anki
Git-backed automation system. The goal is:

-   Clean history
-   Clear intent
-   Domain separation
-   Safe architectural evolution
-   Scalable collaboration (future-proof)

This convention applies to all domains (ua, b737, future domains) and
all automation layers (schema, pipeline, validation, etc.).

------------------------------------------------------------------------

# 1. Branch Categories

All branches must use one of the following prefixes:

## 1.1 architecture/

For structural, schema, or system-level changes.

Examples:

-   architecture/cnsf-v0
-   architecture/schema-validation
-   architecture/render-layer-refactor

Use this when: - Defining canonical formats - Changing transformation
contracts - Modifying global repo structure - Introducing validation
layers

These are high-impact branches.

------------------------------------------------------------------------

## 1.2 pipeline/

For transformation logic changes between layers.

Examples:

-   pipeline/md-to-html
-   pipeline/html-to-tsv
-   pipeline/anki-update-engine
-   pipeline/tag-normalization

Use this when: - Updating transformation scripts - Modifying TSV
structure - Changing AnkiConnect interaction logic

------------------------------------------------------------------------

## 1.3 feature/`<domain>`{=html}/

For domain-specific note development or automation.

Examples:

-   feature/b737/limits-model-cards
-   feature/ua/lexeme-import
-   feature/ua/grammar-validation

Use this when: - Adding new notes - Refactoring a domain's note
structure - Adding domain-specific tooling

------------------------------------------------------------------------

## 1.4 validation/

For schema or note validation logic.

Examples:

-   validation/cnsf-required-fields
-   validation/tag-prefix-policy

Use this when: - Adding or tightening validation rules - Introducing
schema enforcement - Adding consistency checks

------------------------------------------------------------------------

## 1.5 bootstrap/

For import/export or reverse-generation work.

Examples:

-   bootstrap/anki-export-to-cnsf
-   bootstrap/legacy-tsv-import

Use this when: - Migrating old notes - Converting TSV → CNSF - Creating
mapping files

------------------------------------------------------------------------

## 1.6 refactor/

For non-functional structural cleanup.

Examples:

-   refactor/update-notes-from-tsv
-   refactor/pipeline-restructure

Use this when: - Improving clarity - Renaming scripts - Breaking large
scripts into modules

No functional changes should occur here.

------------------------------------------------------------------------

## 1.7 hotfix/

For urgent corrections to main.

Examples:

-   hotfix/tag-policy-bug
-   hotfix/render-missing-block

Used rarely.

------------------------------------------------------------------------

# 2. Naming Rules

-   Use lowercase only
-   Use hyphen-separated words
-   No spaces
-   Keep names concise but descriptive
-   Avoid including ticket numbers unless required

------------------------------------------------------------------------

# 3. Main Branch Policy

main must remain:

-   Stable
-   Buildable
-   Free of unverified structural experiments
-   Passing validation checks

All changes must arrive via pull request.

------------------------------------------------------------------------

# 4. Architecture Change Policy

Any change to:

-   CNSF schema
-   Field mapping rules
-   Transformation contracts
-   Tag prefix rules

MUST:

1.  Occur in an architecture/ branch
2.  Update documentation
3.  Be reviewed before merge

------------------------------------------------------------------------

# 5. Domain Isolation Principle

Domain work must not modify:

-   Core schema
-   Global tag rules
-   Pipeline contracts

Unless done in architecture/ or pipeline/ branches.

------------------------------------------------------------------------

# 6. Recommended Workflow

1.  Create architecture branch
2.  Merge to main
3.  Rebase feature branches onto updated main
4.  Continue domain work

This keeps architectural evolution clean and intentional.

------------------------------------------------------------------------

# 7. Future-Proofing

This structure supports:

-   Multiple aircraft types
-   Multiple languages
-   Additional flashcard domains
-   Shared pipeline across domains

------------------------------------------------------------------------

# END OF BRANCH NAMING CONVENTION
