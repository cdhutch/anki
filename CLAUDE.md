# CLAUDE.md — B737 Anki Project (Active Work)

Restore working context here. Reference files archived separately.

---

## Project Overview

Anki flashcard decks for B737 type rating study. Source: CNSF markdown notes in `domains/b737/`.
Export: TSV via `sv_exam_md_to_tsv.py`. Import: AnkiConnect.

---

## Current Work: Distractor Authoring (Phase A)

**Status**: 26 of 29 systems verified; 3 remaining.

**Workflow per system:**
1. Author distractors in `.md` files
2. Call Claude for review, grammar, typo fixes
3. Run `make sve-fix` to canonicalize
4. Claude provides `git add` + `git commit`
5. Move to next system

**Queue (smallest first):**
- engines: 41 total, 39 draft
- autoflight: 42 total, 39 draft
- pneumatics: 39 total, 39 draft

**Note**: `status:draft` imports as suspended; `status:verified` imports active.

---

## Reference Files

- **[CLAUDE-migration-log.md](CLAUDE-migration-log.md)** — Phase B migration steps (mostly completed)
- **[CLAUDE-deck-schema.md](CLAUDE-deck-schema.md)** — SV field conventions, deck architecture, study stages
- **[CLAUDE-tooling-notes.md](CLAUDE-tooling-notes.md)** — Known issues, workarounds, key paths
