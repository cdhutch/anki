# LLM Bootstrap Prompt — Anki repo automation architecture (B737 + UA)

Use this prompt at the start of a new ChatGPT session to load context for the repo automation and note pipeline work. It is written so you can paste it as-is.

---

You are helping me maintain an **Anki notes monorepo** with “domain-first” structure under `domains/<domain>/anki/…` and shared tooling under `tools/anki/…`.

## Repo: high-level goals

1) **Canonical source of truth lives in git** (not inside Anki UI), especially for important note content and tags.
2) **Deterministic regeneration** of derived artifacts (HTML, TSV) from canonical content.
3) **Fast update loop** for reviewing changes before pushing them to Anki via AnkiConnect.
4) Avoid committing generated intermediates; keep only canonical inputs and stable tooling/docs.

---

# Key components we added

## 1) Canonical Markdown source files (domain-specific)

For B737 (systems), we use **canonical Markdown** files stored in:
- `domains/b737/anki/sources/<slug>__canonical.md`

This file contains a repeatable structure per note, including:
- A header containing the canonical note ID (`Note_ID` / `note_id` pattern).
- A `### AFTER` block that is the canonical “back-side” answer content for the systems cards.
- Separators (`---`) between notes.

Important: **canonical Markdown is intended to drive the HTML that gets pushed into Anki’s “answer/back” field** for systems-style notes. Other note types may have different canonical formats.

## 2) Pipeline scripts (shared tooling under `tools/anki/`)

We implemented a generalized workflow:
- `tools/anki/pipeline.py` — orchestrator (argparse subcommands)
- `tools/anki/md_to_html.py` — converts canonical MD → HTML (MultiMarkdown or Pandoc)
- `tools/anki/html_after_to_tsv.py` — extracts AFTER block HTML into TSV with `note_id` → `after_html`
- `tools/anki/merge_base_and_after.py` — merges `base.tsv` + `after_html.tsv` by `note_id` into `import_html.tsv`
- `tools/anki/update_notes_from_tsv.py` — updates Anki note fields via AnkiConnect (`updateNoteFields`), supports dry-run

Canonical file naming convention (B737 examples):
- canonical MD: `systems-electrical__canonical.md`
- generated HTML: `systems-electrical__canonical.html` (in generated dir)
- base TSV: `systems-electrical__canonical__base.tsv`
- after_html TSV: `systems-electrical__canonical__after_html.tsv`
- import_html TSV: `systems-electrical__canonical__import_html.tsv`

## 3) Validator for canonical Markdown

- `tools/anki/validate_canonical_md.py`
- It validates canonical formatting for AFTER blocks (e.g., bullet normalization rules).
- It supports `--in <path>` and optional `--fix` behavior.
- We tuned it because it was initially too aggressive.

## 4) Tag utilities for canonical “Tags_Ch” → managed Anki tags

- `tools/anki/tag_utils.py`
- Purpose: treat a canonical Tags field like `Tags_Ch` as the **single source of truth** for tags.
- It parses composite tags like: `textbook:яблуко ch:2.8.6; sensory; appearance; comparison`
- It normalizes them into valid Anki tag tokens, and can produce “managed” tags (e.g., prefixes) to avoid collisions.

Goal: important tags should be reproducible from git, not hand-maintained in Anki.

---

# Directory conventions (domain-first)

Typical domain layout:

- `domains/<domain>/anki/sources/` — canonical sources (MD, etc.)
- `domains/<domain>/anki/generated/` — generated HTML and other derived artifacts (ignored by git)
- `domains/<domain>/anki/exports/` — pipeline TSVs and intermediates (mostly ignored by git)
- `domains/<domain>/anki/tmp/` — scratch pipeline outputs (ignored by git)
- `domains/<domain>/anki/docs/` — domain-specific docs about the workflow
- `tools/anki/` — shared scripts for pipeline, validation, tagging, etc.

`.gitignore` includes patterns to ignore:
- `domains/**/anki/generated/`
- `domains/**/anki/tmp/`
- pipeline intermediate TSVs like `*__after_html.tsv`, `*__import_html.tsv`, etc.

---

# Typical B737 workflow (systems cards)

Given a dataset slug like `systems-electrical`:

1) Validate canonical MD:
   - `python tools/anki/validate_canonical_md.py --in domains/b737/anki/sources/systems-electrical__canonical.md`

2) Generate HTML from MD:
   - `python tools/anki/md_to_html.py --in ...__canonical.md --out domains/b737/anki/generated/...__canonical.html --engine multimarkdown`

3) Extract AFTER HTML → TSV:
   - `python tools/anki/html_after_to_tsv.py --in ...__canonical.html --out domains/b737/anki/exports/...__after_html.tsv`

4) Merge base TSV + after_html TSV → import_html TSV:
   - `python tools/anki/merge_base_and_after.py --base ...__base.tsv --after ...__after_html.tsv --out ...__import_html.tsv`

5) Dry run AnkiConnect update:
   - `python tools/anki/update_notes_from_tsv.py --in ...__import_html.tsv --anki-url http://127.0.0.1:8765 --dry-run`

6) Apply update:
   - same command without `--dry-run`

This updates the Anki field (commonly `answer`) for those note IDs.

---

# What we learned / pitfalls

- Missing line breaks inside bulleted lists can occur if canonical markdown is malformed or HTML conversion collapses whitespace.
- Consistent Markdown list syntax (`- item`) and blank lines before lists reduce formatting surprises.
- Git should not track generated intermediates; regenerate them locally.
- Separate “content PRs” (domain notes) from “tooling PRs” (scripts/docs) when possible.
- When a mixed branch contains both tooling and domain content, we used cherry-pick onto a clean branch from `main` to split it.

---

# UA note types (planned / starting)

We created a new `domains/ua/` tree to support Ukrainian note types, especially:
- `UA_Lexeme`
- `UA_Grammar`

We added `Note_ID` to both models, aligning with the B737 approach: a stable, human-curated identifier in git.

We are working toward storing Ukrainian canonical content in the repo as well, but the canonical format may differ:
- Lexeme cards likely use structured TSV or structured MD templates per note
- Grammar cards may be better as MD with sections per pattern/topic

The goal is still: git is canonical, Anki is a render target.

---

# What you should do when I ask for help

- Treat canonical git content and scripts as primary.
- Prefer workflows that are reproducible.
- Provide terminal commands step-by-step and stop between steps if I request it.
- When suggesting schema changes, consider backwards compatibility and migration steps.
- For tags: prefer a canonical tag field in git and a deterministic mapping to Anki tags (avoid manual drift).

---

End of bootstrap prompt.
