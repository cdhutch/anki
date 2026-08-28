# Ch.10-12 + Ch.1-7 Vocabulary Expansion — Progress Index

Tracks the 2026-08-28 autonomous pass sourcing `yabluko-l2-vocabulary.pdf` chapters other
than 8/9 (already done). Branch: `feature/yabluko-l2-vocab-expansion`. Order per Craig:
ch.10, then ch.1–7, then ch.11–12.

**Purpose:** a lightweight, committed, human-readable index of exactly which NoteIDs this
pass has generated, so a later session (me or Craig) can pick up mid-chapter without
re-deriving state from git log or re-running `build_lexeme_index.py`. This is a progress
tracker, not the dedup source of truth — dedup still re-scans the live corpus per
`CLAUDE-ch09-vocab-workflow.md`.

## PDF page map (24 pages total, confirmed against the known ch.8/ch.9 boundary)

| Chapter | PDF pages | Subsections | Status |
|---|---|---|---|
| 1 Будні та свята | 1–2 | 1.1–1.7 | not started |
| 2 Вечірка | 2–4 | 2.1–2.7 | not started |
| 3 Чого нам бракує до повного щастя | 4–7 | 3.1–3.7 | not started |
| 4 Люди та історії | 7–9 | 4.1–4.7 | not started |
| 5 Скажи де, скажи коли | 9–11 | 5.1–5.6 | not started |
| 6 Що сталося? | 11–13 | 6.1–6.7 | not started |
| 7 Наше майбутнє | 13–16 | 7.1–7.7 | not started (1 stray lexeme, ua-lexeme-0379, already exists from the grammar-guide PDF — unrelated source, will surface again in dedup) |
| 8 Риба шукає, де глибше | 16–17 | 8.1–8.7 | **done** (pre-existing) |
| 9 Рух — це життя | 17–20 | 9.1–9.7 | **done** (pre-existing) |
| 10 Суворо заборонено! | 20–22 | 10.1–10.7 | **10.1 done**, 10.2–10.7 not started |
| 11 Якби всі люди... | 22–23 | 11.1–11.7 | not started |
| 12 Не журись! | 23–24 | 12.1–12.7 | not started |

## Generated this pass

### Ch.10.1 (airport/travel prohibitions) — commit `d4091e3f`

- Lexemes: **ua-lexeme-0616 – ua-lexeme-0653** (38 notes: 26 standalone headwords, 7 noun
  phrases, 1 bundled modal-phrase-cluster note)
- Verbs: **ua-verb-0088 – ua-verb-0091** (тримати, витягати, палити, пакувати)
- All `status:draft`. Tag `ch:2.10.1`.
- **Known gap, flagged in ua-lexeme-0653's Verification Notes, not silently dropped:** the
  permission/obligation modal words (можна, треба, потрібно, мусити, могти, дозволити,
  заборонити) were checked against the corpus and are genuinely absent as standalone
  lexemes — bundled into one phrase note instead of drafting all seven as full entries, to
  keep the sub-chapter a manageable size. A future pass should give each its own
  `UA_Lexeme` (+ `UA_Verb` for the four that are verbs).
- 3 homograph collisions resolved to a single sense with the other sense(s) documented in
  `Verification Notes` but not drafted (посадка, магазин, палити) — see individual notes.

### Next NoteIDs to use

- Next `ua-lexeme-` ID: **0654**
- Next `ua-verb-` ID: **0092**

## Environment notes for whoever continues this

- `git-lfs` is not on `device_bash`'s PATH by default — install once per session to
  `$HOME/tools/git-lfs/git-lfs` (static binary from GitHub releases, arm64) and prefix
  `PATH="$HOME/tools/git-lfs:$HOME/.local/bin:$PATH"` on every git/python command, or `git
  status`/`add`/`commit` will misbehave or the pre-commit hook will fail
  (`No module named pre_commit`). `pip3 install --user pre-commit pyyaml pytest` once per
  session likewise.
- `device_bash` cannot `rm`/`unlink` by default; git write commands can strand
  `.git/index.lock` (its own internal cleanup needs unlink too). Either request delete
  permission once via `device_request_delete_permission` on the anki folder (durable for
  the rest of that session), or ask Craig to `rm -f .git/index.lock`.
- Dedup: read the whole `domains/ua/anki/notes/lexemes/**/*.md` + `notes/verbs/*.md` corpus
  directly (grep/python frontmatter parse) into a scratch TSV rather than staging files
  individually (the real `build_lexeme_index.py` script exists but is Craig-run only, and
  per-file staging hits HTTP 429 past ~180 files). Cross-check candidates with the repo's
  own `python -m tools.anki.inspect.check_lexeme_dedup <words...>` (read-only, safe to run
  under a Big-3-suspension window) before drafting.
- After generating files: `python3 -m tools.anki.cnsf_canonicalize --write <paths>` to fix
  field order/YAML quoting, then `check_cnsf_field_schema.py` + `check_euphony_stress.py` +
  `pytest tests/ua/` (install pytest first) before committing.
