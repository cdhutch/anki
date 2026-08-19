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

- [x] **EN→UA stress-mark feedback misjudges a correctly-stressed answer as
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
  **FIXED AND VALIDATED ON-DEVICE 2026-08-18** (branch
  `fix/typeans-combining-mark-nbsp`, commit `f9a4525`).
  `normalizeTypeansText()` added to `EN_UA_BACK` and to
  `setup_ua_pvom_note_type.py`'s `FEEDBACK_SCRIPT` — PVOM uses the identical
  `#typeans` reconstruction, so it had the identical bug, and every PVOM
  answer carries a stress mark. Craig ran all five checks himself after
  `make ua-setup-lexeme` / `make ua-setup-pvom`:
    - ua-lexeme-0532 typed correctly (`розве́дення ове́ць`) → **✓ PERFECT**
      (this is the originally-reported failure — it used to grade INCORRECT)
    - ua-lexeme-0532 with the accent on the wrong vowel → ✗ INCORRECT, but the
      echoed answer now reads cleanly, **no phantom space, no detached mark**
    - ua-lexeme-0532 with no stress marks → ~ CORRECT (tier ladder intact —
      a real risk, since over-eager normalisation could have collapsed the
      unstressed answer into the PERFECT bucket)
    - `наї́хати` (PVOM) → ✓ PERFECT; `наїхати` → ~ CORRECT
    - `на́їхати` (PVOM, accent on the wrong vowel) → ✗ INCORRECT with a clean
      echo — the nbsp branch, confirmed across the `ї` digraph
  **Note the first two PVOM answers do not exercise the fix**: an exact match
  renders one clean `#typeans` line, and a wholly-missing mark puts the accent
  on the correct-answer line past `#typearrow`, which the reconstruction stops
  at. Only a stress-*position* mismatch splits the diff mid-grapheme and makes
  Anki emit the isolation nbsp — so the 2nd and 5th checks above are the ones
  that actually prove it. Covered by `tests/ua/test_typeans_normalization.py`
  (12 tests); `make ua-test` 285 passed.
  **Box left unticked on purpose** — per this file's own rule, it's yours to
  check, not Claude's to fill in.

## UA Domain — Structural / card & note-type work

- [x] **`make ua-lexeme` run 2026-08-18** — 585 updated, 0 errors. `ua-lexeme-0115`'s
  ввійти́/увійти́ flip, its new `Lemma_Euphony: ухо́дити`, and the recomputed
  `TypingTarget_UA` of `вхо́дити / ввійти́` are now live in Anki. The EN→UA card asks for
  the в- form as primary and accepts either у- form per slot via `_EuphonySlots`
  (`ухо́дити / увійти́`); the UA→EN front now reads
  `вхо́дити (ухо́дити) / ввійти́ (увійти́)` — see the display-format item below, which is
  the one open judgement call left from this session.
- [x] **EN→UA card front shows the English example sentence — CONFIRMED WORKING
  2026-08-18, needs only your tick.** Craig checked a live `ua-lexeme-0532` EN→UA card
  while testing the stress-mark fix: the English sentence renders under the gloss as
  intended. Open since 2026-08-03.
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
  **Second, independent defect found 2026-08-18:** `everySlotPerfect`'s ordering is
  not the whole story. `euphonyAltsForSlot()` stress-strips the stored alternates
  *and* the typed slot, so the code **structurally cannot** tell "euphonic alternate,
  perfectly stressed" from "euphonic alternate, no stress at all". Reordering the
  lines does not fix that — it needs a data-shape change, which is why Craig chose
  Option B (structured `_TypingSpec`) over patching in place. See
  `docs/ua-en-ua-euphony-aspect-refactor.md` §4(a).
- [ ] **UA→EN front multi-aspect display — format endorsed, one open judgement call**
  (2026-08-18). Craig looked at `ua-lexeme-0115` and objected to
  `вхо́дити / увійти́ (ввійти́)` — but that was the **pre-flip data**, not the format:
  `make ua-lexeme` had not been run, so Anki still had увійти́ as primary. His stated
  preference (увійти́ belongs in the parentheses) is exactly what the committed flip
  produces, so the `primary (euphonic)` format itself is endorsed.
  **The open question is length.** Because `Lemma_Euphony: ухо́дити` was also added the
  same day, the computed value post-sync is four forms, not three:
      `вхо́дити (ухо́дити) / ввійти́ (увійти́)`
  0115 is the first note in the corpus with euphony on *both* slots, so this is the
  first time the front line carries four. Craig to decide once he sees it live: keep
  as-is, show parentheticals only where a slot is genuinely ambiguous, or drop them
  from the UA→EN front entirely and leave euphony purely as typing tolerance.
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
  per-slot tolerance mechanism (built 2026-08-04) at all. ~~Not started, no design
  yet.~~ **Design written and decisions taken 2026-08-18** —
  `docs/ua-en-ua-euphony-aspect-refactor.md` is now the working document; the
  `CLAUDE.md` history section it was written from is background only. Craig's calls:
    - **Option B** — replace the two positionally-aligned strings
      (`TypingTarget_UA` + `_EuphonySlots`) with one computed structured field
      (`_TypingSpec`, `{slots:[{primary, alts[]}]}`). Removes positional alignment
      as a correctness requirement rather than working around it.
    - **A fully-stressed euphonic alternate earns PERFECT** — `ввійти́` is not a
      lesser answer than `уві́йти`, just a different attested one. This is what
      forces the data-shape change (see the second defect noted above).
    - **Bug (b), the detached stress mark, lands standalone and first** — done, see
      the top of this file.
  Still undecided in that doc's §7: Option C (splitting EN→UA into one card per
  aspect slot, mirroring `UA_PVOM_Infinitive`'s 4-template rationale), and the (d)
  audit of singlet notes whose `EuphonyNote` holds prose rather than a bare
  alternate — those produce silent dead tolerance, matching nothing and warning
  about nothing. **Not started as code.**
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
- [x] **`*_Euphony` authoring convention decided and enforced** (2026-08-18,
  commit `05d8e74`). Three calls, all Craig's: values always carry stress; no
  `*_Euphony_Typing` companion field (derive by stripping, never store); and the
  four `UA_PVOM_Infinitive` `*_Euphony` fields are always-present-blank, matching
  item 17's `UA_Lexeme` convention. The drift was invisible because stress in
  these fields is currently **inert** — both feedback scripts strip it from stored
  alternates *and* the typed answer before comparing — which is exactly how
  `UA_Lexeme` came to store 4/4 stressed while PVOM stored 4/4 unstressed with
  neither failing any check. Enforced by `check_euphony_stress.py` (in
  `make ua-check`) plus a `setdefault` block in `cnsf_canonicalize.py` that runs
  before field ordering. Verified: `make ua-pvom-fix` rewrote 11 notes,
  `make ua-check` clean, `make ua-test` 303 passed.
- [x] **Audit PVOM tags in Anki against CNSF** — `ua_pvom_infinitive_import.py` never
  wrote tags on the update path until 2026-08-18 (it was the only one of the five UA
  importers missing the `removeTags`/`addTags` pass after `updateNoteFields`), so PVOM
  tags in Anki were frozen at note-creation state for the life of the note type. The
  `stress:` tags are now correct (verified: 13 `stress:verified`, 0 `stress:unverified`),
  but **any other tag edit made to a PVOM note since it was created also never landed**.
  Worth diffing one or two notes' Anki tags against their CNSF `tags:` list to see
  whether anything else drifted.
- [ ] **Orange flag call-out isn't scoped to the note type being synced** (found
  2026-08-18 on the first live `make ua-pvom`). `FLAG_DECK_QUERY` is `deck:UA::*`, so a
  PVOM sync printed 26 orange-flagged notes of which **none were PVOM** — all
  `ua-lexeme-*` plus `ua-verb-0016`/`ua-visual-0001`. The suspend set is still
  intersected correctly, so nothing is wrong; but every UA import now prints the same
  26 unrelated notes, which is how a useful warning turns into scrollback. Scope the
  call-out to the notes actually being imported.
- [ ] **Flag counts in the docs are stale** — `CLAUDE-active-status.md` says 11 flagged
  notes, `flagged_cards_manifest.json` said 28. The live figure is **40** (14 red + 26
  orange), read straight off the 2026-08-18 `make ua-pvom` output, so no separate
  `ua_flag_audit.py --query` run is needed to know the number — only to get the note
  list for Phase 2.
- [ ] **`UA_Verb`'s `Tags_Conj` / `Source_Note` sparse-vs-always-present decision**
  — 1/87 notes each. This is now **the only thing left** blocking `STRICT=1` by
  default on `ua-check-fields`; `UA_Lexeme` (item 17) and `UA_PVOM_Infinitive`
  (above) are both settled. Note the 6 `UA_Lexeme` fields the checker also reports
  as "not present on every note" are **not** a gap — five are computed at sync time
  and one (`ImperfectiveUnidirectional`) is deliberately sparse; authoring them
  would write values the import script overwrites. See the Makefile comment above
  `ua-check-fields`.

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

- [x] **`ухо́дити` as `вхо́дити`'s euphonic partner — RESOLVED, needs only
  your tick.** Craig supplied the source 2026-08-18: **Shevchuk's UA-EN Collocation
  Dictionary attests the у- forms of both ходити and йти** — the same authority that
  settled the в- headword question, so the two decisions are consistent rather than
  competing. The apparent conflict with SUM-20 dissolves: SUM-20's `ВВІХО́ДИТИ
  (УВІХО́ДИТИ)` is a *different* variant pair of the same verb, not a rival claim
  about which у- form is correct — both alternations are attested. Горох independently
  lists `ухо́дити` as its own headword with sense 1 glossing to "входити кудись".
  NEEDS CRAIG DECISION flags cleared from both `ua-lexeme-0115` and `ua-pvom-0012`.
- [ ] **`ua-lexeme-0115` is `status:verified` while carrying an unverified change**
  — the 2026-08-18 `ввійти́`/`увійти́` flip. Its cards are active, and the next
  `make ua-lexeme` pushes a `TypingTarget_UA` of `вхо́дити / ввійти́`, changing what
  a live card demands mid-study. Decide: verify the flip and leave the tag, or
  downgrade the tag until you have. (`ua-pvom-0012` had the same issue and you've
  since flipped it to `stress:verified` — so its four stress placements are now
  covered by that tag too and want the same confirmation.)
- [x] **PVOM apostrophe in the typing target — RESOLVED 2026-08-18, no code change
  needed.** 12 of 52 PVOM cards carry U+02BC (ʼ) in their `*_Typing` field and neither
  feedback script normalises apostrophe variants, so the concern was that a keyboard
  emitting U+0027 or U+2019 would make those cards ungradeable. Tested live: typing
  `підʼї́хати` naturally graded **✓ PERFECT**, so Craig's layout emits U+02BC and the
  comparison matches. Left as an unticked item only so the finding is recorded — if the
  keyboard or platform ever changes, the fix is the same shape as the U+00A0 fix and
  belongs in the same `normalizeTypeansText()` helper.
- [ ] **Ch-08 verification decisions written into fields** — 0482 дотримуватися
  missing its `Perfective` (дотриматися), and the 0474 раз counting-usage
  question. (0484 correction already applied and synced.)
- [x] **All 13 `UA_PVOM_Infinitive` notes stress-verified** — Craig's own Горох pass,
  2026-08-18, `stress:unverified` → `stress:verified` on every note. Confirmed in Anki
  after the tag-write fix: `tag:stress:verified` = 13, `tag:stress:unverified` = 0.
- [x] **All 52 PVOM cards unsuspended and drilling** — confirmed in Anki 2026-08-18:
  none suspended. `should_suspend()` re-asserts from the CNSF tags on every sync, so
  flipping the 13 notes to `stress:verified` released the whole prefix-drilling set,
  including the mutation-heavy prefixes (`підʼїхати`, `підійти`, `сходити`) the
  4-template split was built for. This set had been dormant since it was created.
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
