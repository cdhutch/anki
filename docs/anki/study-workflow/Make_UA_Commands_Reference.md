---
title: Make UA Commands Reference
tags: [anki, ua, reference, make]
aliases: [UA Make Commands, make ua reference, UA Makefile reference]
updated: 2026-08-29
related: ["[[Card_Activation_and_FSRS_Tutorial]]", "[[CNSF_CLI_Reference]]", "[[DECK_PRESETS]]"]
---

# Make UA Commands Reference

Every `make ua-*` target, what it touches, and when to reach for it. This is a
reference, not a walkthrough — for the end-to-end story of how a note goes
from freshly authored to actually appearing (and staying scheduled) in Anki,
see [[Card_Activation_and_FSRS_Tutorial]].

> [!info] Conventions used throughout
> - `$(PYTHON)` resolves to the interpreter pinned at the top of the
>   `Makefile` (currently a `miniforge3` env), not necessarily your shell's
>   `python3`.
> - **Sync targets** (`ua-lexeme`, `ua-grammar`, `ua-verb`, `ua-visual`,
>   `ua-pvom`, and the aggregate `ua`) run through the `log_wrap` macro: each
>   run writes a timestamped combined stdout/stderr log to
>   `/tmp/anki-sync-logs/`, printed at the end of the run. Logs are not
>   committed and age out with the OS.
> - `FULL=1` forces a full resync on any of the five per-note-type sync
>   targets, bypassing the git-diff incremental scope calculator
>   (`tools/anki/sync/sync_scope.py`). Use it once after cloning fresh, after
>   editing `.anki_sync_state/` by hand, or any time you don't trust the
>   incremental baseline.
> - `STRICT=1` turns a report-only check into a build failure (non-zero
>   exit) on any finding. Every check target defaults to report-only.
> - Every sync and `-fix` target **requires Anki closed or AnkiConnect
>   reachable** only where noted below — canonicalization itself never
>   touches Anki; only `_ua-<type>` (the sync step) and `ua-check-flags` /
>   `ua-seed-mature` do.

---

## 1. Note-type setup

One-time (or rare) note-type/model creation in Anki. Requires Anki open with
AnkiConnect.

| Command | What it does |
|---|---|
| `make ua-setup` | Creates/updates all UA note types in Anki (`UA_Lexeme`, `UA_Grammar`, `UA_Visual`, `UA_Verb`, plus PVOM via its own script). |
| `make ua-setup-lexeme` | Just `UA_Lexeme`. |
| `make ua-setup-grammar` | Just `UA_Grammar`. |
| `make ua-setup-visual` | Just `UA_Visual`. |
| `make ua-setup-verb` | Just `UA_Verb`. |
| `make ua-setup-pvom` | PVOM infinitive note type, via `setup_ua_pvom_note_type.py` (also runs automatically as a prerequisite of `_ua-pvom`, see §3). |

> [!tip] You rarely run these directly
> Note-type setup only matters when a template or field changes. Day-to-day
> work is the sync targets in §3.

---

## 2. Scoped sync — one chapter or one textbook

For working a single chapter or textbook without touching the rest of the
lexeme corpus. Lexeme-only (`UA_LEXEME_ROOT`) — there's no batch/book
equivalent for grammar/verb/visual/pvom, since those note types aren't
organized by chapter subfolder the way lexemes are.

| Command | What it does |
|---|---|
| `make ua-batch-check BATCH=<book>/ch-<NN>` | CNSF format check for one chapter, no changes. |
| `make ua-batch-fix BATCH=<book>/ch-<NN>` | Canonicalize one chapter. |
| `make ua-batch BATCH=<book>/ch-<NN>` | Canonicalize **and sync** one chapter (always a full sync of that chapter — the incremental scope calculator only applies to the whole-corpus targets in §3). |
| `make ua-book-check BOOK=<book>` | CNSF format check for a whole textbook. |
| `make ua-book-fix BOOK=<book>` | Canonicalize a whole textbook. |
| `make ua-book BOOK=<book>` | Canonicalize **and sync** a whole textbook. |

**Batch path convention:** `<textbook>/ch-<NN>`

| Example | Meaning |
|---|---|
| `yabluko-l1/ch-00` | Вступ (introductory unit) |
| `yabluko-l1/ch-01` | Book 1, Chapter 1 |
| `yabluko-l2/ch-09` | Book 2, Chapter 9 (prefixed motion verbs) |

```bash
make ua-batch BATCH=yabluko-l1/ch-00
make ua-book  BOOK=yabluko-l2
```

---

## 3. Per-note-type sync — the whole corpus

The five workhorse targets. Each: canonicalizes (`-fix` step) → computes
incremental scope via `sync_scope.py` → syncs only what changed (or
everything, on `FULL=1` or first run) → records the new sync baseline.
**Requires Anki open with AnkiConnect.**

| Command | Note type | Root | Notes |
|---|---|---|---|
| `make ua-lexeme` | `UA_Lexeme` | `domains/ua/anki/notes/lexemes` | Recognition (UA→EN) + Production (EN→UA) cards, plus the Compare card. |
| `make ua-grammar` | `UA_Grammar` | `domains/ua/anki/notes/grammar` | Cloze cards. |
| `make ua-visual` | `UA_Visual` | `domains/ua/anki/notes/visual` | Also runs `fix_visual_svg_yaml.py` as part of its `-fix` step. |
| `make ua-verb` | `UA_Verb` | `domains/ua/anki/notes/verbs` | Excludes `*/exported/*` (inert legacy archive — not part of the active pipeline; see [[Card_Activation_and_FSRS_Tutorial]]#gotchas). |
| `make ua-pvom` | `UA_PVOM_Infinitive` | `domains/ua/anki/notes/pvom` | Runs `ua-setup-pvom` first (the only sync target that also re-asserts its note type every run). |

Each also has `-check` (format check, no sync) and `-fix` (canonicalize,
no sync) variants, e.g. `ua-lexeme-check`, `ua-lexeme-fix`.

```bash
make ua-lexeme                 # incremental — only notes changed since last sync
make ua-lexeme FULL=1          # force a full resync
make ua-lexeme-fix             # canonicalize only, no Anki needed
```

> [!note] What "incremental" means here
> `sync_scope.py` diffs against a per-note-type baseline commit SHA stored
> locally in `.anki_sync_state/<key>.sha` (gitignored — this is a
> per-machine bookmark, not repo state, so it doesn't transfer between
> machines and isn't something to commit). It unions committed changes since
> that baseline with anything currently dirty or untracked. No baseline yet
> (fresh clone, or the recorded commit no longer exists) triggers an
> automatic full sync instead of erroring.

---

## 4. Checks & audits — report-only, no Anki required

Pure CNSF-file checks. Safe to run with Anki closed. Default to report-only;
`STRICT=1` fails the build on any finding.

| Command | What it flags |
|---|---|
| `make ua-unverified` | Every note that's `status:draft` or has unverified stress — printed loud (bold/blink/yellow) since it also runs at the end of `ua` and `ua-fix`. |
| `make ua-compare-check` | `UA_Lexeme` Compare-card field shape (`ConfusableSet` / `CompareA-D` / `Homograph_SenseA-B` / `homograph:true`) against the documented mapping, plus a corpus-wide duplicate-`NoteID` check. |
| `make ua-check-aspect` | `pos:verb` notes with zero aspectual counterparts and no `aspect:*-only` tag. |
| `make ua-check-pending-confusables` | `pending-confusable:<lemma>` tags whose target now actually exists in the corpus (i.e. the watch is resolved and the tag can come off). |
| `make ua-check-fields` | CNSF field-schema consistency per note type, against the always-vs-sparse convention (see the target's own comment block in the `Makefile` for the current list of known, accepted sparse fields — don't "fix" those by hand-authoring values the importer overwrites anyway). |
| `make ua-check-euphony-stress` | Euphony stress-mark checks. |
| `make ua-check` | Aggregate: `ua-check-aspect` + `ua-check-pending-confusables` + `ua-check-fields` + `ua-check-euphony-stress`. |
| `make ua-check-flags` | Red/orange-flagged UA cards (things you flagged during study to revisit). **Requires AnkiConnect** — degrades gracefully to a one-line skip if unreachable rather than failing. Runs automatically at the end of `make ua`. |
| `make ua-audit` | Full sweep: `ua-unverified` + `ua-compare-check` + `ua-check`. Logged like the sync targets, since audit findings are worth a dated record. |

```bash
make ua-check STRICT=1     # fail the build if anything's found
```

---

## 5. Release pacing & mature-interval seeding

The lever that controls when authored, verified content actually enters
Anki rotation, and — for material you already know — starts it at a
realistic interval instead of a fresh Learning card. Full walkthrough in
[[Card_Activation_and_FSRS_Tutorial]]; this table is the command surface
only.

| Command | What it does | Requires Anki? |
|---|---|---|
| `make ua-release-wave-dry-run` | Preview what `release_plan.yaml` would promote this run — per group, how many notes are verified & ready vs. still blocked on `status:draft`. | No |
| `make ua-release-wave` | Apply: flips `release:pending` → `release:active` on verified notes per the batch sizes in `domains/ua/anki/config/release_plan.yaml`; stamps `relearn:pending` on notes from a `type: relearn` group. Warns if a whole side (new-content groups, or relearn groups) has nothing verified-and-ready this run. | No (edits `.md` files only) |
| `make ua-seed-mature-dry-run` | Preview mature-interval seeding — which relearn notes are eligible, and how many cards each has, without calling `setDueDate` or touching any file. | **Yes** — even dry-run needs live AnkiConnect to show real card counts. |
| `make ua-seed-mature` | Seed eligible notes (`status:verified` + `release:active` + `relearn:pending`, not yet `relearn:seeded`) with a mature FSRS interval via `setDueDate`, then flip the tag to `relearn:seeded`. | **Yes.** |

> [!note] `status:verified` is required to promote, not just `release:pending`
> Added 2026-08-29 after a real run promoted 21 still-`status:draft` notes
> to `release:active` — harmless in Anki itself (the sync AND-gate still
> kept those notes' cards suspended), but it let `ua-seed-mature` waste a
> mature-interval seed on cards that were never actually live. A note
> that's `release:pending` but still `status:draft` is now reported as
> "blocked on verification" instead of promoted, and if an entire side has
> nothing else ready, `ua-release-wave` says so explicitly.

> [!warning] Order matters
> `ua-release-wave` only edits files. The notes it promotes don't actually
> unsuspend in Anki until you run the matching sync target (`make
> ua-lexeme`, typically). `ua-seed-mature` needs the cards to already exist
> and be unsuspended in Anki, so it always comes *after* the sync, never
> before. See [[Card_Activation_and_FSRS_Tutorial]] for the full sequence.

---

## 6. Aggregate — all five note types at once

| Command | What it does |
|---|---|
| `make ua-fix` | Canonicalizes all five note types (lexeme, grammar, visual, verb, pvom) — no Anki, no sync. Also runs `ua-unverified` and `ua-compare-check` at the end. |
| `make ua` | Canonicalizes and syncs all five note types, in order, stopping on first failure. Then runs `ua-unverified`, `ua-check-flags`, and `ua-check-pending-confusables`. **Requires Anki + AnkiConnect.** This is "sync everything." |

```bash
make ua              # the everyday command
make ua FULL=1        # force a full resync of all five note types
```

---

## 7. Stress verification

Cross-checks stored stress marks against Горох (goroh.pp.ua).

| Command | What it does |
|---|---|
| `make ua-stress-extract` | Generates `goroh_input.json` + `goroh_fetch.js` into `/tmp/goroh/`. |
| `make ua-stress-fetch` | Fetches Горох pages via Python (no browser needed). |
| `make ua-stress-compare` | Compares stored forms against the cached Горох data; writes `/tmp/goroh/goroh_mismatches.tsv`. |
| `make ua-stress-apply` | Applies corrections from a filled-in `goroh_mismatches.tsv`. |
| `make ua-stress` | Runs extract → fetch → compare in sequence, then tells you to review the mismatches file before running `apply`. |
| `make ua-stress-wizard` | Interactive guided version of the same pipeline (`run_stress_verification.py`). |

```bash
make ua-stress
# review /tmp/goroh/goroh_mismatches.tsv, fill in the "correction" column
make ua-stress-apply
```

---

## 8. Example generation

Requires `ANTHROPIC_API_KEY` set and `pip install anthropic`.

| Command | What it does |
|---|---|
| `make ua-generate-examples BATCH=<book>/ch-<NN> [LIMIT=N]` | Generates `UA_Example`/`EN_Example` fields via the Anthropic API for one chapter (default `LIMIT=10`). |
| `make ua-inject-examples BATCH=<book>/ch-<NN> [JSON=<path>]` | Injects pre-generated examples from a JSON file (default: `<BATCH>/generated_examples.json`). |

---

## 9. Tests

| Command | What it does |
|---|---|
| `make ua-test` | `pytest tests/ua/ -v` — the full UA test suite, verbose. Prefer plain `python3 -m pytest tests/ua/ -q` when you just want pass/fail (quieter, and what's used elsewhere in this repo's own workflow). |

---

## Quick lookup — every target, alphabetical

| Target | Category | Anki required? |
|---|---|---|
| `ua` | §6 aggregate | Yes |
| `ua-audit` | §4 checks | No |
| `ua-batch` / `-check` / `-fix` | §2 scoped sync | sync only |
| `ua-book` / `-check` / `-fix` | §2 scoped sync | sync only |
| `ua-check` | §4 checks | No |
| `ua-check-aspect` | §4 checks | No |
| `ua-check-euphony-stress` | §4 checks | No |
| `ua-check-fields` | §4 checks | No |
| `ua-check-flags` | §4 checks | Yes (degrades gracefully) |
| `ua-check-pending-confusables` | §4 checks | No |
| `ua-compare-check` | §4 checks | No |
| `ua-fix` | §6 aggregate | No |
| `ua-generate-examples` | §8 examples | No (Anthropic API instead) |
| `ua-grammar` / `-check` / `-fix` | §3 per-type sync | sync only |
| `ua-inject-examples` | §8 examples | No |
| `ua-lexeme` / `-check` / `-fix` | §3 per-type sync | sync only |
| `ua-pvom` / `-check` / `-fix` | §3 per-type sync | sync only |
| `ua-release-wave` | §5 pacing | No |
| `ua-release-wave-dry-run` | §5 pacing | No |
| `ua-seed-mature` | §5 pacing | Yes |
| `ua-seed-mature-dry-run` | §5 pacing | Yes |
| `ua-setup` / `-lexeme` / `-grammar` / `-visual` / `-verb` / `-pvom` | §1 setup | Yes |
| `ua-stress*` / `-wizard` | §7 stress | No |
| `ua-test` | §9 tests | No |
| `ua-unverified` | §4 checks | No |
| `ua-verb` / `-check` / `-fix` | §3 per-type sync | sync only |
| `ua-visual` / `-check` / `-fix` | §3 per-type sync | sync only |



---

## See also

- [[Card_Activation_and_FSRS_Tutorial]] — the end-to-end story: draft → verified → released → seeded → scheduled.
- [[DECK_PRESETS]] — FSRS parameters and deck-preset tooling (separate from anything in this file).
- `docs/anki/pipeline/CNSF_CLI_Reference.md` — the underlying Python scripts' own `--help` output, generated directly from the CLIs.
