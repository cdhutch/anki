# Vocabulary Dedup / Homograph Audit — Tooling & 2026-07-24 Audit

**Branch:** `feature/ua-vocab-dedup-homograph` (based off `main`)

This file documents the tooling built to support CLAUDE.md's "Vocabulary dedup & homograph
handling" section and item 0 of the UA pending-work queue, plus the results of the first
full-corpus audit run with it. See CLAUDE.md for the canonical description of the four
outcome buckets (new / homograph / duplicate / convergent-synonym) — this file covers the
*tooling* and the *audit results*, not the policy itself.

## Why this exists

CLAUDE.md's top-priority item (set by Craig, 2026-07-23) asked to wire dedup/homograph
checking directly into the per-chapter vocabulary generation scripts, so every candidate
word gets checked automatically instead of via a separate manual `check_lexeme_dedup.py`
run. Building that wiring surfaced a broader need: a one-time audit of the ~180 notes
already in the corpus, since the dedup/homograph policy postdates most of those notes. Craig
redirected scope to do the audit first (reusable tooling + a full-corpus pass), with
generator-script wiring deferred as a still-open follow-up.

## Tools

### `tools/anki/lib/lexeme_dedup.py`

Importable library — not a CLI script — providing the write-side logic for the three
spelling-keyed buckets (new / homograph / duplicate):

- `strip_stress(s)` — NFD-decompose/NFC-recompose stress stripping (removes only the
  combining acute U+0301; does not touch й/ї or other diacritics that naive Mn-category
  stripping would destroy).
- `load_corpus(lexeme_root=None)` — indexes every `ua-lexeme-*.md` by stripped spelling.
- `check_dedup(candidate, index)` — returns a `DedupResult` (new / matches found).
- `create_or_link_lexeme(candidate_lemma, note_content, new_note_path, *,
  dedup_decision=None, new_chapter_tag=None, dated_note=None,
  homograph_confusable_new=None, homograph_confusable_existing=None, lexeme_root=None,
  index=None)` — the main entry point. Given a decision (new/duplicate/homograph), either
  writes a new canonical note, or mutates the existing note in place (append chapter tag +
  dated verification note for a duplicate; cross-link `ConfusableSet` + tag
  `homograph:true` on both notes for a homograph). Returns a `DedupOutcome(bucket, written,
  modified)`.
- `next_note_id(prefix="ua-lexeme", lexeme_root=None)` — next free NoteID.

All writes go through the shared `tools/anki/cnsf_canonicalize.py` (`canonicalize_meta` +
`dump_yaml`) so output matches the same canonical formatting as the rest of the corpus —
see "The canonicalizer fix" below for a bug this surfaced.

**Status: not yet called from anywhere.** This is a ready-to-use library, but no
`gen_ch09_*.py`-style generator script imports it yet. Wiring it in is what item 0 in
CLAUDE.md still asks for — building this library was necessary groundwork for that, not the
completion of it.

**Tests:** `tests/ua/test_lexeme_dedup.py`, 49 tests, including a `TestMultilineFields`
class specifically regression-testing the canonicalizer bug below (multi-line
`ConfusableSet`/dated-note values must round-trip through canonicalization without
introducing blank lines inside YAML frontmatter).

### `tools/anki/inspect/build_lexeme_index.py`

CLI script. Walks the full lexeme corpus and writes one TSV row per note to
`build/ua_lexeme_index.tsv` (gitignored — regenerable artifact, not checked in):
`NoteID, LemmaStripped, Lemma, PartOfSpeech, Gender, EN_Gloss, ConfusableSet,
VerbMotion_Pair, CrossLang_Analog, Tags_Ch, Tags, Homograph, Status, Path`.

Built specifically to support the bucket-4 (convergent-synonym) audit: reading through 180
individual note files via the device bridge hits per-file staging rate limits at that
volume (HTTP 429, confirmed empirically), but a single master TSV lets the whole corpus be
read and semantically clustered in one pass. Craig suggested this approach directly.

Run with (Craig runs, per the Big 3 Rules):
```bash
python -m tools.anki.inspect.build_lexeme_index
```

**Tests:** `tests/ua/test_build_lexeme_index.py`, 11 tests.

### The canonicalizer fix (`tools/anki/cnsf_canonicalize.py`)

While applying the audit's edits, `dump_yaml()` was found to silently corrupt any multi-line
field value (e.g. a multi-scenario `ConfusableSet`) that didn't happen to contain an
apostrophe: PyYAML's default scalar-style heuristic picks single-quoted style for multi-line
strings unless the string contains a single quote (then it picks double-quoted, which
escapes `\n` safely instead of folding it into a blank line). Single-quoted style folds each
embedded `\n` into a *blank physical line* on dump, which trips the module's own "no blank
lines inside frontmatter" check (`_reject_blank_lines_in_yaml`) the next time the file is
parsed — e.g. by the pre-commit hook. `ua-lexeme-0058` (професія) only ever dumped safely
because its `ConfusableSet` text happened to mention "a plumber's expertise." Fixed by
forcing double-quoted style for any string containing `\n`, verified byte-identical against
`ua-lexeme-0058`'s existing on-disk content (not a formatting change for anything already
stored that way — only fixes cases that were previously silently broken). See the
`_force_dquote_multiline()` docstring in `cnsf_canonicalize.py` for the full detail; this was
a genuine pre-existing latent bug in a shared, pre-commit-enforced file, not specific to this
audit's fields, so it's worth knowing about regardless of dedup/homograph work.

## The 2026-07-24 full-corpus audit

Ran `build_lexeme_index.py` (180 notes, 0 tagged `homograph:true` yet, 0 distinct spellings
shared by more than one note — confirming no bucket-2/3 mechanical collisions exist in the
current corpus) and then read the full `EN_Gloss` list for bucket-4 semantic clustering, per
Craig's direction ("Claude reads the whole gloss list and clusters by judgment," not a
keyword heuristic). Findings applied (all `canonicalized_file_text()`-stable and idempotent,
verified before delivery):

- **добре / непогано / нормально / чудово** (ua-lexeme-0099/0100/0101/0104) — cross-linked
  via `ConfusableSet` as a "how are you?" register/enthusiasm scale (непогано < нормально <
  добре < чудово), rather than four interchangeable synonyms for "good/fine."
- **перегони / біг** (ua-lexeme-0144/0145) — cross-linked: перегони is racing by any
  mode/transport, біг narrows to racing/running specifically on foot. Both `EN_Gloss` values
  had overlapped on "race."
- **метелик homograph split** — ua-lexeme-0171 trimmed to the butterfly (insect) sense only;
  the unrelated bow-tie/flyer sense split into new note **ua-lexeme-0181**
  (`status:draft`), both tagged `homograph:true` and cross-linked (bucket 2, not bucket 4 —
  this one is a true same-spelling/unrelated-meaning homograph, not a synonym cluster).
- **вид homograph split** — Craig caught this one directly: "Isn't вид also used for verbal
  aspect, as in доконаний вид?" ua-lexeme-0143 (kind/type sense, e.g. вид спорту) now
  cross-links to new note **ua-lexeme-0182** (`status:draft`) for the grammatical-aspect
  sense (доконаний/недоконаний вид) — a third, previously undocumented homograph sense
  alongside the archaic face/appearance sense already noted on 0143. Includes a
  `CrossLang_Analog` note that English doesn't mark aspect morphologically the way Ukrainian
  does, since that's the actual source of learner confusion here.

Both new notes (`ua-lexeme-0181`, `ua-lexeme-0182`) are `status:draft` pending Craig's
review/stress-check, per the standing draft-until-reviewed rule.

## Open follow-up

- **Generator-script wiring** (CLAUDE.md item 0) — still not done. `lexeme_dedup.py` exists
  and is tested, but no `gen_ch09_*.py`-style script calls `create_or_link_lexeme()` yet.
- Whether to repeat the bucket-4 audit periodically (e.g. after each chapter batch) or only
  at natural review points is an open question — not yet decided.
- The `Mnemonic_EN`/`CompareA`/`CompareB` field repurposing for homographs generally
  (proposed in CLAUDE.md's bucket-2 section) still needs Craig's go-ahead before it's built
  out beyond the про-/пере- prefix pairs it was originally built for.
