# Work Queue — Verification Checklist

**Purpose:** every open item across the project, one checkbox each, for Craig to
tick off personally. This file exists because prose status logs (`CLAUDE.md`,
`CLAUDE-active-status.md`) have repeatedly drifted from what's actually true in
Anki/the repo — see the "what the log claims" notes below, several of which
turned out to be stale or unconfirmed when checked against git history or the
tooling's own output.

**Rule for this file: no box gets checked because a log entry said something is
done.** Check a box only after you've personally confirmed it — in Anki, in the
repo, or against Горох. If you check something off, it's worth a one-line note
in `CLAUDE.md`'s dated log for the record, but this file is the one Claude
won't fill in for you.

Last built: 2026-08-08, cross-referenced against `git log`, `CLAUDE.md`'s dated
log, `CLAUDE-active-status.md`, and the repo's own generated manifests.

---

## Bugs — reported by Craig, needs investigation

- [ ] **EN→UA stress-mark feedback misjudges a correctly-stressed answer as
  INCORRECT** (reported 2026-08-08). Reproduction: ua-lexeme-0532 (phrase note,
  `Lemma: розве́дення ове́ць`, `TypingAnswer: розведення овець` — no aspect
  slots, so `TypingTarget_UA` falls back to `Lemma` per
  `compute_typing_target()`). Craig typed the stress correctly but the
  feedback script (`EN_UA_BACK` in `setup_ua_note_types.py`) reported
  `✗ INCORRECT`, and the on-screen reconstruction of what he typed rendered as
  `розведе ́ння ове́ць` — the combining accent (U+0301) appears **detached from
  its letter with a stray space before it**, and in the wrong position (after
  the 7th letter/second е, not the 5th letter/first е where `розве́дення`
  actually stresses).
  **What I checked:** the note's fields are correct (`Lemma` stress verified,
  Горох-sourced). The feedback script reconstructs "what was typed" by walking
  `#typeans`'s child nodes and concatenating only `.typeGood`/`.typeBad` span
  text content (`typedAnswer = chunks.map(el => el.textContent).join('')`),
  specifically to avoid the older, documented "combining mark renders detached
  from its base letter" bug from Anki's own raw diff (see "Typing-card design
  pattern for Ukrainian text" in `CLAUDE.md`). The fact that a *detached* mark
  is showing up in the reconstructed `typedAnswer` string itself — not just in
  Anki's raw diff — means either (a) Anki's `#typeans` diff, for this specific
  kind of mismatch, is inserting an un-classed space/text node *between* two
  `.typeGood`/`.typeBad` spans that the walker doesn't filter out, or (b)
  Anki's character-level diff treats the base letter and its combining accent
  as two independent diff units, and a one-position stress shift cascades into
  a run of spurious mismatches that happens to include a real space character
  from somewhere in that run. I can't tell which without seeing the actual
  `#typeans` DOM for a failing case — this needs on-device diagnosis, not a
  guess shipped blind (a wrong fix here means another sync-and-retest round
  trip). ~~**Next step:** next time this reproduces, open Chrome/Anki's
  DevTools...~~
  **ROOT-CAUSED 2026-08-18 — no DevTools session needed. Hypothesis (a) above
  was right.** It's Anki's own diff output, not the reconstruction loop. From
  Anki's `rslib/src/typeanswer.rs`:

  ```rust
  /// Prefixes a leading mark character with a non-breaking space to prevent it
  /// from joining the previous token.
  fn isolate_leading_mark(text: &str) -> Cow<'_, str> {
      if text.chars().next().is_some_and(|c| GeneralCategory::of(c).is_mark()) {
          Cow::Owned(format!("\u{a0}{text}"))
      } else {
          Cow::Borrowed(text)
      }
  }
  ```

  When Anki's character-level diff splits a chunk such that the chunk *begins*
  with U+0301, Anki deliberately prepends U+00A0 so the mark won't combine
  with the preceding letter. That nbsp sits **inside** a `.typeGood`/`.typeBad`
  span, so `chunks.map(el => el.textContent).join('')` swallows it into
  `typedAnswer` — which then matches nothing, and renders with a visible gap
  before a detached-looking accent. Exactly the reported symptom. It also
  answers the last question above: this is specific to a stress-mark
  **position** mismatch, because only a position shift makes the diff split
  mid-grapheme; it is not phrase-note-specific.
  **Fix:** normalise U+00A0 out of the reconstruction — drop it outright when
  followed by a combining mark (Anki's isolation artifact), convert any other
  occurrence to an ordinary space. Independent of the euphony/aspect work and
  fixable on its own; see `docs/ua-en-ua-euphony-aspect-refactor.md` §4(b),
  and §7(3) for the open question of whether to land it standalone or fold it
  into the refactor.

## UA Domain — Structural / card & note-type work

- [ ] **EN→UA card front shows the English example sentence** (`EN_Example` rendered
  under the gloss in `EN_UA_FRONT`). Log claims: coded 2026-08-03 (commit `904cd2c`),
  merged via PR #65, synced (`make ua-lexeme`: 584 updated, 0 errors), spot-checked
  "good" 2026-08-04. 567/585 lexeme notes have `EN_Example` populated. Check: open a
  few EN→UA cards for notes with a populated `EN_Example` and confirm the sentence
  actually renders.
- [ ] **Per-slot euphony tolerance — partially confirmed, real gap found (2026-08-11).**
  EN→UA typing accepts either в-/у- (etc.) form independently per aspect slot, not just
  at the whole-string level. The template had never actually been pushed live until this
  session (`make ua` doesn't push templates — see the field-order item below); after
  running `make ua-setup-lexeme`, Craig tested `ua-lexeme-0115` (входити/увійти): typing
  the euphonic alternate (`вхо́дити / ввійти́`) IS accepted rather than rejected, but only
  ever lands at the CORRECT tier, never PERFECT, even with full correct stress — a real
  bug in `EN_UA_BACK`'s feedback script (`everySlotPerfect` is set `false` before the
  euphonic-alternate check runs; full root cause in CLAUDE.md's euphony/aspect refactor
  section). `ua-lexeme-0124` (уїжджати/уїхати) not yet tested. Not being fixed in
  isolation — folded into the "EN→UA euphony + verbal-aspect refactor" item below.
- [ ] **UA→EN front multi-aspect display** — `_UA_EN_DisplayLemma` shows euphonic
  alternates inline, e.g. "вхо́дити / уві́йти (ввійти́)". Log claims code-complete
  2026-08-03, but the parenthetical format itself was Claude's own call, never
  confirmed by Craig. Check: does the format actually read well, or do you want it
  changed?
- [x] **Gruvbox palette holds up under the iOS red-tint Color Filter** on real
  content, not just the `Palette_Comparison_Demo` card. Log claims: A/B/C comparison
  done, Craig said "I'm pretty happy with the night mode" 2026-08-04. Check: the
  actual 3-pass Day/Night/red-tint walkthrough against live `UA_Lexeme`/`UA_Verb`
  cards specifically for red/orange legibility.
- [ ] **Verb-phrase aspect defaulting** (EN→UA typing target defaults to imperfective
  when a verb-phrase note doesn't clearly call for perfective) — scoped 2026-07-29,
  never coded. Authoring-guidance-only right now. Decide if/when this gets built.
- [ ] **EN→UA euphony + verbal-aspect refactor** (broader than the item above) —
  flagged 2026-08-11: Craig recalls abandoning a prior effort in this area and wants
  the whole approach to how euphony and verbal aspect are jointly managed on the
  EN→UA side reconsidered from scratch, including whether to keep the existing
  per-slot tolerance mechanism (built 2026-08-04) at all. Not started, no design yet.
  See "EN→UA Euphony + Verbal-Aspect Refactor (Future)" in `CLAUDE.md` for the full
  history to read before scoping.
- [x] **UA note-type field order not preserved across `make ua-setup-*` runs**
  (flagged 2026-08-11) — **Fixed and personally verified 2026-08-18** (branch
  `fix/ua-field-order-enforcement`, commit `5e9f2e4`). Checked off against live Anki,
  not a log claim: Craig ran `make ua-setup-lexeme` (repositioned 38 fields), re-ran it
  to confirm the no-op guard, ran `make ua-setup-verb` (26) and `make ua-setup-pvom`
  (17), eyeballed the resulting `UA_Lexeme` and `UA_Verb` field lists in the Anki
  Fields dialog against the expected order, and finished with
  `inspect_note_type_fields.py` reporting **all 5 note types matching exactly, set and
  order** — the first fully-clean run since that tool was built. Collection backup
  taken first; the one-time full AnkiWeb upload completed. **Note the original
  diagnosis above was wrong:** the setup script never pushed the `FIELDS` order at all
  (`inOrderFields` is `createModel`-only; the update paths only appended), so the
  constants were decorative and live order was the historical add-order. The 2026-08-11
  clobbering was `Verification Notes` + the 5 euphony fields being appended to the
  bottom. Fixed by adding a guarded `sync_field_order()` reposition pass — so the
  constants are now genuinely authoritative, and manual dragging in the GUI will be
  reverted by the next setup run **by design**. See CLAUDE.md item 20.
- [ ] **`UA_Grammar` 0001–0007 reviewed** against the 2026-07-22 atomicity /
  no-self-leak / no-cross-cloze-leak cloze principles (0008/0009 already meet them).
  No work started.
- [x] **Two pre-existing `tests/ua/test_lexeme_import.py` failure groups resolved
  (2026-08-11).** `TestComputeTypingTarget` (8 failures — tested an abandoned
  2026-07-25 design) rewritten against the real, live `compute_typing_target()`
  behavior; all 6 rewritten tests pass. `TestPruneOrphansSafetyGate` (5 failures —
  referenced `prune_orphans`/`collect_all_corpus_note_ids`/`all_anki_note_ids`/
  `delete_notes`, none of which exist) deleted outright per Craig, rather than left
  failing for unbuilt code — see CLAUDE.md item 19 for the design to rebuild against
  whenever that feature actually gets built. Craig personally ran `make ua-test` and
  confirmed clean (246 passed, 0 failed).
- [ ] **`domains/ua/anki/docs/design.md` refreshed** to match the live schema
  (currently predates `CounterpartForm`/`AspectCue`/`TypingTarget_UA` and others).
- [ ] **Compare-card "should be suspended" comment fixed** in
  `setup_ua_note_types.py` — the branch it describes is actually unreachable (Anki
  never generates an empty-front Compare card to begin with). Cosmetic, low
  priority.

## UA Domain — YAML/CNSF schema consistency

- [x] **Build a CNSF field-schema checker** (per note type: `UA_Lexeme`,
  `UA_Verb`, `UA_Grammar`, `UA_Visual`, `UA_PVOM_Infinitive`) that verifies
  every note carries the full standard field-key set — even blank (`''`) —
  rather than omitting keys for unused optional fields. Flag any note missing
  a standard key, and any note carrying a key that isn't in the standard set
  (typos, abandoned experiments).
- [x] **Establish the canonical field-set source of truth per note type**
  before trusting the checker's output — `setup_ua_note_types.py`'s `FIELDS`
  constants have already been caught stale relative to the live AnkiConnect
  model once before (missing `Verification Notes`/`Mnemonic_EN`/`CompareA`/
  `CompareB` at the time — see "Verb_Conj_Table Removal Plan" in `CLAUDE.md`).
  Reconcile the constant against `inspect_ua_lexeme_fields.py`'s live-model
  output first.
- [x] **Decide the convention for newer optional fields and enforce it** —
  verified directly against the corpus (2026-08-08, 585 `UA_Lexeme` notes):
  every core field (`Lemma`, `EN_Gloss`, `ConfusableSet`, `EuphonyNote`, etc.)
  is present as a key on all 585/585 notes, blank string when unused. The
  newer fields are not: `Lemma_Euphony` (6/585), `Perfective_Euphony` (5/585),
  `ImperfectiveUnidirectional_Euphony` (2/585), `CompareA`/`CompareB` (63/585),
  `CompareC`/`CompareD` (11/585, 8/585), `CompareScenario` (63/585),
  `Homograph_SenseA`/`SenseB` (10/585 each), `AspectCue` (19/585), `Mnemonic_EN`
  (487/585 — closest to universal, still 98 short). Pick one: either every
  note always carries these keys (blank when unused, matching the rest of the
  schema), or sparse-key-only is the intended design for optional fields — then
  make `cnsf_canonicalize.py` enforce whichever choice, so this doesn't keep
  drifting silently.
- [x] **Run the same field-presence check against `UA_Verb`/`UA_Grammar`/
  `UA_Visual`/`UA_PVOM_Infinitive`** — the numbers above only cover
  `UA_Lexeme`; the other four note types haven't been checked yet.
- [x] **CNSF `fields:` key order canonicalized from the Anki `FIELDS` constants**
  — **Done and personally verified 2026-08-18** (commit `1baf0c2`). Raised by Craig
  while reviewing the Anki-side field-order fix ("will this also ensure that all of
  the YAML notes' fields are in the same order?") — it would not have.
  `cnsf_canonicalize.py` ordered only the seven top-level keys; keys inside `fields:`
  were preserved as authored, and `cmd_check()` had the same blind spot, so the
  pre-commit hook had never looked at field-key order. Three distinct orders found in
  a 12-note sample. Per Craig, **Option A**: `cnsf_canonicalize.py` imports the same
  constants that drive the live models, so file order and Anki order can't drift
  apart. Checked off against real output, not a log claim: `--check` reported 585/585
  lexeme notes drifted with zero in other categories; `make ua-lexeme-fix` rewrote all
  585; the diff verified order-only (7497 insertions vs 7497 deletions, byte-identical
  sorted line multisets); the `--all-files` pre-commit hook then passed clean, having
  imported the new chain inside its pyyaml-only venv without error. `ua-verb`/
  `ua-grammar`/`ua-visual`/`ua-pvom` and all of B737 were already in constant order and
  were untouched. **No Anki re-sync needed** — the import scripts send fields as a
  name-keyed dict, so CNSF key order never affected what reaches Anki.
- [x] **Wire the checker into `make ua-check`** alongside the existing
  `audit_verb_aspect_forms.py`/`check_pending_confusables.py` audits, so field
  drift gets caught on every check run instead of accumulating unnoticed.

## UA Domain — Confusable-set / Compare-card content queue

- [ ] **виступ** — anticipated confusable cluster (performance/presentation/
  appearance senses). Not yet sourced. See `docs/ua-confusables-queue.md`.
- [ ] **вогонь** (ua-lexeme-0329) — anticipated confusable cluster vs
  ватра/пожежа/полум'я. Not yet sourced.
- [ ] **Motion-vocabulary confusable cluster** — `-правлятися`/`-правитися`
  reflexive verbs + `-правлення` nouns, `вирушати`, and the PVOM prefix set.
  Flagged 2026-08-03, not started.
- [ ] **ua-lexeme-0106 ("goodbye") Compare card** — папа/бувай and other
  goodbye-words aren't distinguished yet. Flagged 2026-08-03, not started.
- [ ] **Pending-confusable watchlist** — run `make ua-check`
  (`check_pending_confusables.py`) and write real `ConfusableSet`/`CompareA-D`
  content for any `pending-confusable:<lemma>` tag whose target word now exists.
  Known tagged lemmas from the ch-08 pass: зазвичай, затор, забагато, вигляд,
  доглянати, скільки, декілька, погода/природа/порода (off пригода), подорож
  (off мандрівка).
- [ ] **Generic `needs-confusable-set` tags** (open-ended prefix families, no
  single target spelling yet) — 0436 важкий, 0440 добрий, 0321 перепрошувати.

## UA Domain — Content verification (Craig + Горох sign-off required)

- [ ] **Ch-08 verification decisions written into fields** — 0482 дотримуватися
  missing its `Perfective` (дотриматися), and the 0474 раз counting-usage
  question. (0484 correction already applied and synced.)
- [ ] **55 draft `UA_Verb` notes stress-verified** (ua-verb-0033–0085) — 48 still
  `stress:unverified`. Full per-verb list in `CLAUDE-ua-verb-qa-worklist.md`.
- [ ] **`Participle_Adverbial_Past` filled** on those same 55 notes (required
  field, currently blank on all 55) plus remaining participles/examples where
  findable.
- [ ] **`status:draft` → `status:verified` review**: ua-lexeme-0581–0585
  (motion-verb triplets), ua-verb-0086/0087 (плисти/поплисти).
- [ ] **Spot-check the 87-note stress-verification pass** pulled in from
  `archive/ua-verb-participle-merge-and-stress-pass` — the 2026-08-04 merge was
  confirmed via a clean sync + a general spot-check, not a note-by-note read of
  the previously-`status:draft` 0033–0085 range.
- [ ] **Flagged notes cleaned up** (Phase 2 of the Flagged Card Fix Workflow,
  `CLAUDE-flag-audit.md`). **Note:** the docs consistently cite "11 flagged
  notes," but `flagged_cards_manifest.json` (the tool's own last `--query`
  output) currently lists **28** — that count is stale. Re-run
  `python tools/anki/inspect/ua_flag_audit.py --query` for a current number
  before starting the review.

## Cross-domain / infra

- [ ] **FSRS deck configs actually created in Anki** ("B737 FSRS" / "UA FSRS" /
  "Legacy FSRS" presets, assigned to the three top-level decks). No confirmation
  found anywhere in the log that this was ever done in Anki itself — full spec in
  `CLAUDE-fsrs-deck-configs.md`.
- [ ] **Deck presets + limits actually applied** in Anki
  (`create_deck_presets.py` → `update_deck_limits.py` →
  `update_b737_deck_limits.py`) — confirm these were run against live Anki, not
  just written to the repo.
- [ ] **`gen_ch09_subsection.py` exercised end-to-end** against a real batch
  (built 2026-07-25, still untested — currently nothing left to run it against
  unless new ch-09+ content is added).

## B737 Domain

- [ ] **Phase A distractor authoring finished** for the 3 remaining systems:
  `engines` (39/41 drafted), `autoflight` (39/42 drafted), `pneumatics` (39/39
  drafted, needs review).
- [ ] **Decide whether to extend the Gruvbox palette to B737** note types
  (currently deliberately out of scope — B737 stays on Solarized).

---

See also: [CLAUDE-active-status.md](CLAUDE-active-status.md) for the narrative
status board, `CLAUDE.md`'s dated log for full context on any item above, and
`CLAUDE-ua-verb-qa-worklist.md` for the per-verb stress/participle breakdown.
