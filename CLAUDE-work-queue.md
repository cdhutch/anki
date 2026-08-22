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

**Structure (reorganized 2026-08-20):** open items come first, grouped by area —
that is the part that answers "what's left." Everything ticked has been moved,
verbatim and with its full DONE block, to **Archive — completed** at the back. Nothing
was summarized or dropped in the move; the archive is the project's record of *why*
each thing was done, which is usually the part that turns out to matter later.

Last built: 2026-08-08, cross-referenced against `git log`, `CLAUDE.md`'s dated
log, `CLAUDE-active-status.md`, and the repo's own generated manifests.

---

## UA Domain — Structural / card & note-type work

- [x] **Per-slot euphony tolerance — partially confirmed, real gap found (2026-08-11).**
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

  **CLOSED 2026-08-20 — absorbed, not separately fixed.** This item said as much itself
  ("folded into the EN→UA euphony + verbal-aspect refactor item below"); it stayed open
  only because the strike never happened. Both defects it names died with the mechanism:
  `everySlotPerfect`'s ordering is moot because `_EuphonySlots` no longer exists, and
  `euphonyAltsForSlot()`'s symmetric stress-stripping is gone because alternates are now
  stored stressed. Closed by `_TypingSpec` on 2026-08-19 (bugs (a)/(c)/(d)), validated
  across 14 typed cases — see the refactor item below and §9.4 of the design doc.

  ~~One residue survives:~~ **Residue closed 2026-08-20 — Craig typed `ua-lexeme-0124`
  and it graded ✓ PERFECT**, "accepted variant form", with `вʼїжджа́ти / вʼї́хати` shown as
  the primary. This was the last untested piece of the euphony work, and it is a stronger
  case than 0115's: both slots carry alternates, and the alternates differ from the
  primaries by more than one letter — `вʼїжджа́ти` → `уїжджа́ти` drops the U+02BC apostrophe
  entirely, so `_TypingSpec` is matching across a differing character count, not a в-/у-
  swap. 0124 remains orange-flagged and stays on the Phase 2 list on its own merits.

- [x] **UA→EN front multi-aspect display — format endorsed, one open judgement call**
  (2026-08-18). Craig looked at `ua-lexeme-0115` and objected to
  `вхо́дити / увійти́ (ввійти́)` — but that was the **pre-flip data**, not the format:
  `make ua-lexeme` had not been run, so Anki still had увійти́ as primary. His stated
  preference (увійти́ belongs in the parentheses) is exactly what the committed flip
  produces, so the `primary (euphonic)` format itself is endorsed.
  **The open question is length.** Because `Lemma_Euphony: ухо́дити` was also added the
  same day, the computed value post-sync is four forms, not three:
      `вхо́дити (ухо́дити) / ввійти́ (увійти́)`
  0115 is the first note in the corpus with euphony on *both* slots, so this is the
  first time the front line carries four. ~~Craig to decide once he sees it live: keep
  as-is, show parentheticals only where a slot is genuinely ambiguous, or drop them
  from the UA→EN front entirely and leave euphony purely as typing tolerance.~~

  **DECIDED 2026-08-20 by Craig, after `make ua` put the four-form line live: keep
  as-is.** No code change; the `primary (euphonic)` format stands at any length.

  The affected population is small: per the 2026-08-08 field census `Lemma_Euphony` was
  6/585, `Perfective_Euphony` 5/585, `ImperfectiveUnidirectional_Euphony` 2/585 — so
  roughly a dozen notes show any parenthetical at all.

  **Correction, same day:** an earlier draft of this closure claimed 0115 was the *only*
  note with euphony on both slots and therefore the only four-form card. That was wrong —
  it upgraded this item's own word "first" to "only" without checking. `ua-lexeme-0124`
  (`Lemma_Euphony: уїжджа́ти`, `Perfective_Euphony: уї́хати`) is a second, found when Craig
  typed it the same afternoon. The census caps `Perfective_Euphony` at 5 notes, so the
  four-form population is **somewhere between 2 and 5, and has not been counted**. Settle
  it with a corpus pass if the display question is ever reopened:

      python - <<'EOF'
      import pathlib, yaml
      for f in sorted(pathlib.Path('domains/ua/anki/notes/lexemes').rglob('ua-lexeme-*.md')):
          d = yaml.safe_load(f.read_text(encoding='utf-8').split('---')[1])['fields']
          if (d.get('Lemma_Euphony') or '') and (d.get('Perfective_Euphony') or ''):
              print(f.stem, d['Lemma'], '/', d['Perfective'])
      EOF

  The decision stands regardless — Craig looked at a live four-form line and accepted the
  format. Only the "population of one" justification was wrong, not the call.

- [x] **Verb-phrase aspect defaulting** (EN→UA typing target defaults to imperfective
  when a verb-phrase note doesn't clearly call for perfective) — scoped 2026-07-29,
  never coded. Authoring-guidance-only right now. ~~Decide if/when this gets built.~~

  **DECIDED 2026-08-20 by Craig: it stays authoring guidance. Not built, not a checker.**
  Recorded in `docs/ua-en-ua-euphony-aspect-refactor.md` §5, which already owns the
  question, rather than in this queue.

  The design doc's own reasoning is why: this governs *what goes in* `Lemma`/`Perfective`
  on phrase notes, not how the answer is graded, so it is independent of bugs (a)–(d) and
  of Options A–C. Enforcing it in code would mean detecting aspect programmatically,
  which is a harder problem than the one being solved. Per §5: "folding it in is what
  made the 2026-07-29 plan feel like one project when it was always two."

  **Known non-conformance, flagged rather than swept in:** today's `make ua-check` aspect
  audit lists phrase singlets in *both* aspects — `ua-lexeme-0299` (ви́лізти на ске́лю),
  `0300` (перелеті́ти…), `0301` (переплисти́ о́зеро) are perfective, while `0302`
  (підніма́тися на ске́лі) and `0303` (спуска́тися вниз) are imperfective. Whether the
  perfective ones are convention violations or legitimately perfective phrases is a
  content question, not a mechanical one. Closing this item does not resolve them; they
  belong to the singlet-review list the aspect audit already prints.

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
  about nothing. ~~**Not started as code.**~~
  **Built and validated live 2026-08-19** (branch `feature/ua-typing-spec-refactor`).
  `_TypingSpec` replaces `_EuphonySlots`; alternates now stored stressed; bugs (a),
  (c) and (d) closed. The (d) audit found exactly one note (ua-lexeme-0353) reaching
  the legacy fallback, holding prose; it was given a real `Lemma_Euphony` and the
  fallback deleted. 14 typed cases confirmed by Craig against live cards — matrix in
  `docs/ua-en-ua-euphony-aspect-refactor.md` §9.4. Option C remains undecided.
  **Leaving this box for Craig**, as the header requires.

  **Option C deferred 2026-08-20 by Craig — blocked behind the deck-preset cleanup**
  (see the FSRS item under Cross-domain / infra). Option C is an FSRS-scheduling change
  to the UA tree, and that tree's preset architecture was unresolved at the time: `UA FSRS`
  sat on 0 decks and two repo documents specified incompatible designs. Deciding per-slot
  cards before knowing which preset those cards live under stacks two unknowns on the
  same notes. Settle the presets first.

  **Blocker cleared 2026-08-20 — Option C is decidable again, on its own merits.** The UA
  tree runs on nine per-deck presets, one file each under `presets/`, specified in
  `DECK_PRESETS.md`. New per-slot cards inherit the preset of the deck they land in, and
  that is now a known quantity rather than an open question. Nothing else about Option C
  changed: the ordinal-preservation assumption below is still Claude's reasoning about
  Anki's card generation and still wants verifying against Anki before anyone acts on it.
  One consideration the preset work adds — FSRS optimizes per preset, so ~71 new cards
  land in one preset's training pool, which is a scheduling question on top of the
  card-count one.

  **Correction to the design doc's cost estimate, in Option C's favour.** §5 says
  "FSRS history implications for 585 notes." Today's aspect audit gives the real shape:
  **61 doublets + 5 triplets = 66 multi-slot notes.** The other 519 lexemes and 21
  single-slot verbs generate one EN→UA card either way. So the change adds roughly **71
  new cards across 66 notes**, not a 585-note upheaval — *provided* the existing EN→UA
  template keeps its ordinal so current cards survive as slot 1. That
  ordinal-preservation assumption is Claude's reasoning about Anki's card generation and
  **wants verifying against Anki before anyone acts on it**, not taking on trust.

  The precedent argument still cuts toward doing it eventually: `UA_PVOM_Infinitive`
  deliberately rejected the compound card because "the four forms are not equally hard"
  and separate templates allow independent suspend and leech tracking — and §5 says that
  reasoning "applies verbatim to aspect slots." A learner solid on `ходи́ти`/`піти́` but
  shaky on `йти` currently fails and re-drills all three.

- [ ] **ua-lexeme-0153 / 0379 — example sentences after the в-/у- flip** (2026-08-19,
  needs Craig, not code). Both notes had their headword direction corrected to в- per
  Shevchuk. Their `UA_Example` sentences still use the у- form, deliberately: в/у
  alternation is *phonetically conditioned*, and in 0379 ("Технік установлює нове
  обладнання") the у- form is arguably the correct choice after a consonant, so
  mechanically tracking the headword could make the example worse rather than better.
  Wants a read against the orthography, not a find-and-replace.
  ~~`Source_URL` on both still points at the у- spellings.~~ **Done — Craig repointed
  both at the в- forms 2026-08-19**, matching the house pattern in 0115/0211/0377/0484.
  (Claude had left these rather than assert a URL it had not opened.)

- [ ] **`UA_Grammar` 0001–0007 reviewed** against the 2026-07-22 atomicity /
  no-self-leak / no-cross-cloze-leak cloze principles (0008/0009 already meet them).
  No work started.

- [ ] **`domains/ua/anki/docs/design.md` refreshed** to match the live schema
  (currently predates `CounterpartForm`/`AspectCue`/`TypingTarget_UA` and others).

## UA Domain — YAML/CNSF schema consistency

- [ ] **Wire per-note-type `--strict` into `make ua-check`** (raised 2026-08-20 while
  closing the item above). `ua-check-fields` passes only a bare
  `$(if $(STRICT),--strict,)`, so `STRICT=1` scans all five note types at once and can
  never pass while `UA_Lexeme` carries its five computed fields at 0/585. As of
  2026-08-20 four note types — `UA_Grammar`, `UA_Visual`, `UA_Verb`,
  `UA_PVOM_Infinitive` — are fully clean and *could* be enforced, but nothing stops them
  regressing silently. Options: a `STRICT_TYPES` variable, or a `ua-check-fields-strict`
  target looping the clean four. Small, and it is what the `Source_Note` item was
  actually reaching for.

  **`Tags_Conj` is no longer part of this item — the field was deleted 2026-08-19**
  (`7657034`). It was a hand-maintained space-joined mirror of the note's own tags,
  rendered in the `UA_Verb` footer, present on 1/87 notes and already drifted (`ch:2.9`
  stored against an actual `ch:2.9.2` tag). The footer now renders Anki's built-in
  `{{Tags}}`, so the duplication is gone by construction and the footer names every
  suspend reason (`conj:`, `status:`, `stress:`) rather than just one.

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

  **Known limitation, found 2026-08-20: the watchlist cannot express a stress-shift
  homograph.** `check_pending_confusables.py` matches on stress-stripped spellings, so
  tagging `ua-lexeme-0116` (`вихо́дити`) with `pending-confusable:виходити` to watch for
  the `ви́ходити` homograph would match 0116 itself and resolve immediately. The pair is
  the same letters distinguished only by stress, which is exactly what the matcher
  discards. Craig confirmed 2026-08-20 that `ви́ходити` is not in the corpus yet. Either
  track it in `docs/ua-confusables-queue.md` instead, or teach the checker a
  stress-sensitive mode — decide before the word is sourced, not after.

- [ ] **Generic `needs-confusable-set` tags** (open-ended prefix families, no
  single target spelling yet) — 0436 важкий, 0440 добрий, 0321 перепрошувати.

## UA Domain — Content verification (Craig + Горох sign-off required)

- [ ] **`ua-lexeme-0115`'s `ConfusableSet` corrected to `вихо́дити`** (2026-08-20,
  `fe4efcc`). It read `ви́ходити` — the prefix-stressed homograph (*to wear out by
  prolonged walking*) — as входити's "directional opposite", left behind when you
  corrected 0116's own `Lemma` on 2026-08-19. Now agrees with 0116 and with
  `ua-verb-0018`. **Content change on a `status:verified` note, so it wants your tick**
  rather than being assumed; the substance is your own already-rechecked 0116 call, not a
  new stress claim. Found by the corpus sweep above.

- [ ] **`ua-lexeme-0115` is `status:verified` while carrying an unverified change**
  — the 2026-08-18 `ввійти́`/`увійти́` flip. Its cards are active, and the next
  `make ua-lexeme` pushes a `TypingTarget_UA` of `вхо́дити / ввійти́`, changing what
  a live card demands mid-study. Decide: verify the flip and leave the tag, or
  downgrade the tag until you have. ~~(`ua-pvom-0012` had the same issue and you've
  since flipped it to `stress:verified` — so its four stress placements are now
  covered by that tag too and want the same confirmation.)~~ **The `ua-pvom-0012` half
  is closed 2026-08-20** — Craig checked `ухо́дити` and `увійти́` against Горох and
  confirmed both; `уїжджа́ти`/`уї́хати` inherit `ua-lexeme-0124`'s verification. The 0115
  half stays open.

- [ ] **Ch-08 verification decisions written into fields** — ~~0482 дотримуватися
  missing its `Perfective` (дотриматися)~~ **— that half is STALE as of 2026-08-20: 0482
  carries `Perfective: дотри́матися`.** Noticed because it surfaced in the `TypingAnswer`
  drift list, which only fires on notes that HAVE two populated aspect slots. What remains
  open here is the 0474 раз counting-usage question. (0484 correction already applied and
  synced.)

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

- [x] **FSRS deck configs actually created in Anki** ("B737 FSRS" / "UA FSRS" /
  "Legacy FSRS" presets, assigned to the three top-level decks). No confirmation
  found anywhere in the log that this was ever done in Anki itself — full spec in
  `CLAUDE-fsrs-deck-configs.md`.

  **Checked 2026-08-20 by Craig in the GUI — the presets exist but the assignments
  did not happen, and the reason is a design conflict, not an oversight.** Live state:
  `B737 FSRS` on **0** decks, `B737 FSRS Core` on **14**, `UA FSRS` on **0**,
  `Legacy FSRS` on **1**. So the deck tree with active daily use is not on its tuned
  retention config, and `B737 FSRS Core` is a preset neither document mentions.

  **Two documents in this repo specify incompatible designs for the same decks:**
  `CLAUDE-fsrs-deck-configs.md` wants three presets, one per top-level tree, carrying
  *retention parameters*; `DECK_PRESET_MAPPING.md` wants nine presets across the UA tree
  carrying *daily limits*. In Anki a deck has exactly one preset and that object holds
  both `desiredRetention` and `new/rev perDay`, so both cannot be satisfied as written.
  The live collection follows `DECK_PRESET_MAPPING.md`, which is why `UA FSRS` sits at
  zero decks.

  **Decide the architecture before touching anything:**
  - *Option A* — keep the nine per-subdeck limit presets and set `desiredRetention` on
    each; delete `UA FSRS`/`B737 FSRS`. Preserves working behaviour, and the FSRS doc's
    isolation goal is already met since the UA and B737 preset sets are disjoint. Caveat
    worth confirming against Anki's own optimizer rather than assumed: FSRS optimizes
    per preset, so nine UA presets means nine smaller training pools.
  - *Option B* — collapse to the three FSRS presets and lose per-subdeck throttling.

  **Why this went unnoticed for six weeks: both survey tools are structurally blind to
  it.** `list_deck_presets.py` and `inspect_deck_configs.py` enumerate presets by
  iterating decks and collecting what they point at, so **a preset assigned to zero decks
  can never appear**. `list_deck_presets.py` also covers UA only (and its own
  "ALL AVAILABLE PRESETS" section is commented as not working); `inspect_deck_configs.py`
  filters to `"737" in d`. Any replacement should be driven by the *expected* preset names
  and report ones sitting at zero decks — that inverts the blindness.

  **Bootstrap deadlock, separate from the above:** `apply_ua_fsrs_to_subdecks.py` refuses
  to run unless the root `UA` deck is already on `UA FSRS`
  (`if ua_config.get("name") != "UA FSRS": return 1`), and nothing in the repo assigns it
  to the root. The rollout script could never have run from this state — it needs an
  undocumented manual GUI step first.

  **RESOLVED 2026-08-20 — Option A, and the architecture question is closed.** Neither
  competing document is current. `DECK_PRESETS.md` supersedes both, plus
  `CLAUDE-deck-architecture.md` and `docs/anki/options/*.md`, and is generated from live
  Anki rather than describing an intention. `presets/<slug>.json` holds one file per
  preset with all parameters except the FSRS ones, which Anki derives itself.

  `UA FSRS` and `B737 FSRS` were pruned as orphans along with 51 others — 85 presets down
  to 32. Every script that could recreate them is deleted, including
  `apply_ua_fsrs_to_subdecks.py` and `setup_fsrs_deck_configs.py`; the four survey tools
  named above are gone too, replaced by `survey_deck_presets.py`, which reads
  `deck_config` directly and so *can* see a zero-deck preset.

  Verified: `create_deck_presets.py` reports 0 created, 0 changed, 32 unchanged — the
  repo and Anki agree exactly. Idempotence was proven on a throwaway preset first, with a
  byte-identical round trip.

  **What is NOT resolved and does not belong to this item:** retention is 0.9 everywhere,
  against this file's 0.93–0.95 for B737; and nine presets carry `fsrsParams6` cloned from
  other content. Both are recorded in `CLAUDE-active-status.md` under FSRS Deck
  Configuration, and neither is a preset-inventory problem.

- [x] **Deck presets + limits actually applied** in Anki
  ~~(`create_deck_presets.py` → `update_deck_limits.py` →
  `update_b737_deck_limits.py`)~~ — confirm these were run against live Anki, not
  just written to the repo.

  **ANSWERED 2026-08-20: yes, and the question is now permanently answerable.**
  `create_deck_presets.py` dry run reports **0 created, 0 changed, 32 unchanged** — every
  preset in Anki matches its file in `presets/` exactly. The two other scripts named above
  were deleted; they wrote limits outside the pipeline. `update_deck_limits.py` and
  `update_b737_deck_limits.py` no longer exist.

  This is no longer a thing to confirm by hand: `export_deck_presets.py` + `git diff`
  reports any drift, because the export carries no timestamp and is byte-stable.

  ~~**Blocked on the architecture decision in the FSRS item above** (2026-08-20): the live
  collection appears to follow `DECK_PRESET_MAPPING.md`, but that cannot be confirmed
  deck-by-deck until a survey tool exists that sees all domains and reports zero-deck
  presets.~~ **Unblocked 2026-08-20 — both halves of that sentence are now answered.**
  The architecture item above resolved to Option A, and the survey tool it was waiting on
  exists: `survey_deck_presets.py` reads `deck_config` directly, covers every domain, and
  reports zero-deck presets. The deck-by-deck confirmation that could not be made is now
  one command. `DECK_PRESET_MAPPING.md` is superseded and bannered, so "the live collection
  appears to follow" it is no longer the right frame — the collection follows
  `presets/*.json`, which was exported *from* it.

- [ ] **B737 desired retention is 0.9, against 0.93–0.95 for safety-critical material.**
  Raised by the now-superseded `CLAUDE-fsrs-deck-configs.md`, whose *architecture* was
  wrong but whose *retention reasoning* was not. All seven B737 presets sit at Anki's 0.9
  default. UA's 0.9 is at the top of its own 0.85–0.90 band, so UA is arguably compliant;
  B737 is below its. Note the same file argues 0.97–0.98 only in the weeks before a
  checkride, so a permanent 0.95 may not be what you want either. Retention cost is
  steeply nonlinear — 0.90 → 0.95 roughly doubles reviews.

- [ ] **Nine presets carry FSRS parameters optimized for other content.** Eight UA presets
  and `B737` share one **bit-identical** `fsrsParams6` vector. A real optimization runs
  against a preset's own review history, so identical vectors across Ukrainian vocabulary
  and a B737 preset can only be a `cloneDeckConfigId` artifact. `B737 Checklists` is on
  FSRS-6 stock defaults. Wants an Optimize pass per preset — and per
  `FSRS_Preset__B737_Systems.md`, roughly 1,000 reviews or 2–4 weeks of use makes that
  meaningful. `presets/*.json` deliberately excludes these, so an apply cannot clobber the
  result.

- [ ] **15 Legacy presets are unspecified** — `DECK_PRESETS.md` §4. They have files like
  everything else, but no decision has been made about whether the repo should enforce
  them. The tree is mixed: `Legacy::Flight Training Active` carries 11 decks and is live,
  while `Legacy::Inactive::*` is dormant.

- [ ] **Two approved-but-unapplied changes in `DECK_PRESETS.md` §5.** (a) Normalize the two
  older B737 presets — five fields, of which only `reviewOrder 3→0` changes behaviour,
  moving 17 decks off *Ascending intervals* onto *Due date, then random*. **`fsrs` is
  excluded and still unresolved**: it is `null` on three presets and `true` on four, and
  the split does not follow the old/modern line. (b) Rename
  `B737 FSRS Core (0n_200r)`, whose name promises 200 reviews/day against an actual 9999.

- [ ] **`query_anki_db.py` searches for `collection.db`**, a filename modern Anki has not
  used in years — it has probably never found a collection. Fix the path or delete it.

- [ ] **`gen_ch09_subsection.py` exercised end-to-end** against a real batch
  (built 2026-07-25, still untested — currently nothing left to run it against
  unless new ch-09+ content is added).

- [ ] **`в-` has no `UA_Verb` conjugation note** — noticed 2026-08-19 while mapping the
  PVOM prefix selection onto the verb corpus. `UA_Verb` covers
  `при/ви/під/до/про/пере/за/від` only; `входити`/`вʼїхати` exist solely as
  `ua-lexeme-0115`/`0124`. So the в-/у- alternation is drilled at PVOM and lexeme level
  but has no paradigm note. Not obviously wrong — prefixed paradigms are derivable from
  the leader — but it is the one gap in an otherwise symmetric set, and it compounds with
  the red flag above.

## B737 Domain

- [ ] **Phase A distractor authoring finished** for the 3 remaining systems:
  `engines` (39/41 drafted), `autoflight` (39/42 drafted), `pneumatics` (39/39
  drafted, needs review).

- [ ] **Decide whether to extend the Gruvbox palette to B737** note types
  (currently deliberately out of scope — B737 stays on Solarized).

---

# Archive — completed

Ticked items, moved here 2026-08-20 with their full text intact. Section headings
mirror the open list above. A ticked box means Craig confirmed it personally — in
Anki, in the repo, or against Горох — not that a log entry claimed it.

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

- [x] **Gruvbox palette holds up under the iOS red-tint Color Filter** on real
  content, not just the `Palette_Comparison_Demo` card. Log claims: A/B/C comparison
  done, Craig said "I'm pretty happy with the night mode" 2026-08-04. Check: the
  actual 3-pass Day/Night/red-tint walkthrough against live `UA_Lexeme`/`UA_Verb`
  cards specifically for red/orange legibility.

- [x] **`UA_PVOM_Infinitive` euphonic alternates are still capped below PERFECT**
  (bug (a), one-slot version — follow-up scoped by Craig 2026-08-19 as "UA_Lexeme now,
  PVOM as a follow-up"; deferred same day). **This does NOT need `_TypingSpec`** — an
  earlier draft of this item said it did, wrongly. `_TypingSpec` exists to remove
  *positional alignment* between two joined strings; PVOM has four card templates each
  testing exactly one form, so there is no join, no slot indexing, and nothing to align.
  The JSON would be pure overhead. The real defect is a single line in `FEEDBACK_SCRIPT`:

      } else if (typedAnswer !== null && euphonyAlts.indexOf(stripStress(typedAnswer).normalize('NFC')) !== -1) {

  It stress-strips both sides and the branch hardcodes `✓ CORRECT / Accepted alternate
  spelling`, so `уходити` and `ухо́дити` are indistinguishable and neither can reach
  PERFECT. Fix: compare stressed first and add a PERFECT branch above the existing
  CORRECT one. **No data migration and no `make ua-pvom`** — the stored `*_Euphony`
  values are already stressed under the 2026-08-18 authoring convention (enforced by
  `check_euphony_stress.py`), so it is a template change plus `make ua-setup-pvom`.
  `ua-pvom-0012` has all four euphony fields stressed and is the note to validate on.
  Two things worth folding in while there: (1) `normalizeTypeansText()` is a
  hand-maintained *copy* across the two setup scripts, kept honest only by a test
  comparing their bodies — the 2026-08-19 near-miss where the lexeme copy was silently
  deleted argues for a single shared source; (2) PVOM's template dict uses the key
  `name` where the lexeme script uses `Name`, harmless to AnkiConnect but it has already
  cost one guard a silent blind spot.

  **DONE AND VALIDATED ON-DEVICE 2026-08-20** (`fe4efcc`, PR #79). Both fold-ins landed
  too: `normalizeTypeansText()` now lives once in `tools/anki/lib/typeans_js.py` and is
  spliced into both scripts (with a test asserting each embeds the constant *verbatim*,
  so re-inlining fails even if the two inlined bodies agree), and the template dicts are
  unified on `"Name"`. Alternates are kept stressed and both stressed comparisons now run
  above both unstressed ones; the typed answer is also NFC-normalized, and the
  null-reconstruction check hoisted to the top. Template change only — `make
  ua-setup-pvom` was run, no `make ua-pvom` needed.

  Craig typed all four cases on `ua-pvom-0012` Walking (Multi):
    - `ухо́дити` → **✓ PERFECT**, "accepted variant form" (was CORRECT — this is the fix)
    - `уходити` → ~ CORRECT, "variant form, missing or misplaced stress"
    - `вхо́дити` → ✓ PERFECT, correctly with **no** "Primary form" line
    - `вхо́дит` → ✗ INCORRECT
  **The second is the load-bearing one** — it is the symmetric failure, and had it come
  back PERFECT the two variant tiers would have collapsed at the top instead of the
  bottom, which is no better than the bug. 18 tests in `test_pvom_euphony_grading.py`.

  **Scope, per Craig the same day: this moves the DESKTOP path only.** Stress marks can't
  be typed on his phone, so mobile study lands at CORRECT either way.

  Note the four cards were hand-unsuspended in the browser to test, because the red flag
  below suspends the whole note; the next `make ua-pvom` re-suspends them.
  **Box left for you**, per this file's rule.

- [x] **61 CNSF notes where `TypingAnswer` disagrees with the stress-stripped slot
  join** (found 2026-08-19 during the `_TypingSpec` rollout). e.g. ua-lexeme-0114 holds
  `приходити` where the note is a doublet needing `приходити / прийти`; ua-lexeme-0488
  holds the Perfective instead of the Lemma. **Not a live bug** — `import_note()`
  overwrites `TypingAnswer` from `compute_typing_target()[1]` for every doublet and
  triplet, so Anki has always had the right value. The drift is confined to the CNSF
  files, which matters only because CNSF is supposed to be the source of truth and a
  reader of 0114 would draw the wrong conclusion about what gets typed. Natural home is
  a `cnsf_canonicalize.py` pass, which already computes the same join for field-order
  purposes. Low priority, zero learner impact.
  **DONE 2026-08-20** (`fe4efcc`, PR #79) — and the count is **61**, not 62; the figure
  recorded here on 2026-08-19 was one high. `_sync_typing_answer()` in
  `cnsf_canonicalize.py`, run via the existing `make ua-lexeme-fix`;
  `compute_typing_target()`/`strip_stress()` moved to `tools/anki/lib/typing_target.py`
  so the canonicaliser can compute the same join **without** importing
  `ua_lexeme_import` — the `cnsf-canonical` hook runs in a pyyaml-only venv, and an
  import-free leaf module can't break it from a distance. `cmd_check()` reports
  `FAIL (TypingAnswer drift)` separately, checked before field-order drift.
  **Scoped strictly to the case the importer overwrites.** Singlets keep their authored
  value — every phrase and non-verb note is one, and those values are hand-written and
  not derivable from `Lemma` alone, so a broader pass would have turned a documentation
  problem into real data loss. Confirmed by all 113 ch-00 notes reporting `OK`. 15 tests
  in `test_typing_answer_sync.py`, most of them pinning that inverse case.
  **`ua-lexeme-0338` is the one note where the join legitimately collapses** —
  `виклика́ти` / `ви́кликати` is a stress-only pair, so `TypingAnswer` reads
  `викликати / викликати`. Settled per Craig, do not re-raise: the unstressed CORRECT
  tier is the everyday path and stress can't be typed on the phone. Pre-existing live
  behaviour that canonicalisation makes visible, not something it introduced.

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

- [x] **Two pre-existing `tests/ua/test_lexeme_import.py` failure groups resolved
  (2026-08-11).** `TestComputeTypingTarget` (8 failures — tested an abandoned
  2026-07-25 design) rewritten against the real, live `compute_typing_target()`
  behavior; all 6 rewritten tests pass. `TestPruneOrphansSafetyGate` (5 failures —
  referenced `prune_orphans`/`collect_all_corpus_note_ids`/`all_anki_note_ids`/
  `delete_notes`, none of which exist) deleted outright per Craig, rather than left
  failing for unbuilt code — see CLAUDE.md item 19 for the design to rebuild against
  whenever that feature actually gets built. Craig personally ran `make ua-test` and
  confirmed clean (246 passed, 0 failed).

- [x] **Compare-card "should be suspended" comment fixed** in
  `setup_ua_note_types.py` — the branch it describes is actually unreachable (Anki
  never generates an empty-front Compare card to begin with). Cosmetic, low
  priority.
  **DONE 2026-08-20** (`fe4efcc`). The misleading part was the user-facing warning text,
  not just the code comment: "this card should be suspended" reads as a live safeguard
  when nothing is suspending anything, because there is no card. Reworded on both front
  and back to describe the data gap and say plainly that seeing it at all would mean
  Anki's empty-card behaviour had changed. `make ua-setup-lexeme` run.

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

- [x] **Orange flag call-out isn't scoped to the note type being synced** (found
  2026-08-18 on the first live `make ua-pvom`). `FLAG_DECK_QUERY` is `deck:UA::*`, so a
  PVOM sync printed 26 orange-flagged notes of which **none were PVOM** — all
  `ua-lexeme-*` plus `ua-verb-0016`/`ua-visual-0001`. The suspend set is still
  intersected correctly, so nothing is wrong; but every UA import now prints the same
  26 unrelated notes, which is how a useful warning turns into scrollback. Scope the
  call-out to the notes actually being imported.
  **DONE 2026-08-20** (`fe4efcc`, PR #79). New `flag_query_for_model()` in
  `tsv_to_anki.py`; all five importers build `FLAG_DECK_QUERY` from it. Scoped by note
  type rather than by `--targets`, deliberately: a flagged sibling in the type you are
  syncing is worth seeing, a flagged `UA_Visual` note during a PVOM sync is not.
  `ua_flag_audit.py` keeps the whole-tree query on purpose — it enumerates the corpus for
  Phase 2 — and `test_flag_query_scope.py` pins that so a future "fix the flag scope"
  sweep does not narrow it by analogy. 19 tests. **Box left for you**, per this file's
  rule; the check is a `make ua-lexeme` or `make ua-pvom` printing only its own note
  type's orange notes.
  **Verified live 2026-08-20:** `make ua-pvom` printed no flag call-out at all — the
  26 unrelated notes are gone, and PVOM itself now has none since `ua-pvom-0012`'s red
  flag was cleared the same day.

- [x] **Flag counts in the docs are stale** — `CLAUDE-active-status.md` says 11 flagged
  notes, `flagged_cards_manifest.json` said 28. The live figure is **40** (14 red + 26
  orange), read straight off the 2026-08-18 `make ua-pvom` output, so no separate
  `ua_flag_audit.py --query` run is needed to know the number — only to get the note
  list for Phase 2.
  **DONE 2026-08-20** (`fe4efcc`). `CLAUDE-active-status.md` corrected to 40 (14 red + 26
  orange) with provenance, and it now says outright that the manifest's 28 is stale and
  wants a fresh `--query` before Phase 2. The manifest file itself is untouched —
  regenerating it is part of Phase 2, not of this item.

- [x] **`UA_Verb`'s `Source_Note` sparse-vs-always-present decision** — the last
  `STRICT=1` blocker for this note type. `Source_Note` is populated on **1 of 87** notes.
  Either backfill it corpus-wide (blank where unknown, per the always-present convention
  settled for `UA_Lexeme` in item 17) or declare it legitimately sparse and teach the
  checker so; ~~until one or the other, `make ua-check STRICT=1` cannot be turned on for
  `UA_Verb`.~~

  **DONE 2026-08-20** (`3a3c7f8`, PR #80) — **Option A per Craig**, blank-backfill
  corpus-wide. `make ua-verb-fix` wrote `Source_Note: ''` into 86 notes, one inserted line
  each and no other line touched; `make ua-check` now reports `All 25 canonical fields
  present (blank or populated) on all 87 notes`. Four of five note types are clean.
  `make ua-test` 442 passed. **Box left for you**, per this file's rule.

  **The two options were not equal weight, and the item's framing understated that.**
  Option A reuses machinery `cnsf_canonicalize.py` already has — per-note-type
  `setdefault` blocks. Option B would have meant *building* a per-field exemption
  mechanism `check_cnsf_field_schema.py` does not have: `--strict` there is one global
  boolean, not an allowlist. The new block is scoped to `note_type == "ua_verb"`, because
  a global `setdefault` would also inject `Source_Note` into B737 notes, which carry
  `Source Document`; two tests pin the scoping.

  **The 1-of-87 note was not evidence of a field in use.** It is `ua-verb-0001`, holding a
  planning to-do ("Verify all forms against Горох", plus a typo, `перейходити` for
  `переходити`) discharged by the 2026-08-19 re-sourcing pass. Craig corrected the typo;
  the text is otherwise kept as history.

  **Correction to this item's own goal, struck above:** `make ua-check STRICT=1` still
  cannot be turned on, and never could have been. The Makefile's `ua-check-fields` target
  passes a bare `$(if $(STRICT),--strict,)` with no `--note-type`, and `--strict` fails on
  *any* canonical field missing from *any* note in the scanned set. `UA_Lexeme` carries
  five fields at 0/585 — `_AspectLabel`, `_UA_EN_DisplayLemma`, `_IsHomograph`,
  `TypingTarget_UA`, `_TypingSpec` — that are computed at import and never authored in
  CNSF by design, so a global `--strict` is permanently unreachable. What works today is
  the per-note-type form, which now passes:

      python tools/anki/inspect/check_cnsf_field_schema.py --note-type UA_Verb --strict

  Wiring that into the Makefile is a separate open item, below.

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

- [x] **PVOM apostrophe in the typing target — RESOLVED 2026-08-18, no code change
  needed.** 12 of 52 PVOM cards carry U+02BC (ʼ) in their `*_Typing` field and neither
  feedback script normalises apostrophe variants, so the concern was that a keyboard
  emitting U+0027 or U+2019 would make those cards ungradeable. Tested live: typing
  `підʼї́хати` naturally graded **✓ PERFECT**, so Craig's layout emits U+02BC and the
  comparison matches. Left as an unticked item only so the finding is recorded — if the
  keyboard or platform ever changes, the fix is the same shape as the U+00A0 fix and
  belongs in the same `normalizeTypeansText()` helper.

- [x] **All 13 `UA_PVOM_Infinitive` notes stress-verified** — Craig's own Горох pass,
  2026-08-18, `stress:unverified` → `stress:verified` on every note. Confirmed in Anki
  after the tag-write fix: `tag:stress:verified` = 13, `tag:stress:unverified` = 0.

- [x] **All 52 PVOM cards unsuspended and drilling** — confirmed in Anki 2026-08-18:
  none suspended. `should_suspend()` re-asserts from the CNSF tags on every sync, so
  flipping the 13 notes to `stress:verified` released the whole prefix-drilling set,
  including the mutation-heavy prefixes (`підʼїхати`, `підійти`, `сходити`) the
  4-template split was built for. This set had been dormant since it was created.

## Cross-domain / infra

- [x] **`main` merged into `maint/verb-review`** — resolved 2026-08-19 by running the
  merge for real (`git merge --no-commit --no-ff main`) instead of predicting it.
  **15** conflicts, not the 14 previously recorded here:

      domains/ua/anki/notes/pvom/ua-pvom-0001.md … ua-pvom-0013.md   (all 13)
      domains/ua/anki/notes/verbs/ua-verb-0010.md
      CLAUDE-work-queue.md                                            (add/add)

  **No code conflicts.** `Makefile` and `ua_flag_audit.py` auto-merged;
  `compute_euphony_slots()` and `TestComputeEuphonySlots` stay deleted, as Option B
  requires. **Cause confirmed as the 2026-08-18 CNSF field-order canonicalisation**, not
  PR #77 — both sides rewrite the `fields:` block, so the hunks overlap.

  **The previous entry here was wrong on its central claim**, and is corrected for the
  record because acting on it would have discarded a commit. It read *"`main` already
  carries `status:draft` on all 13."* It does not — `git grep -l status:draft main --
  domains/ua/anki/notes/pvom/` returns **0**. What the three trees actually hold:

      base 60cf537   stress:unverified                       (all 13)
      main           stress:verified,  no status: tag        (all 13)
      branch         stress:unverified + status:draft        (0013: stress:verified)

  The two sides changed *different* tags, so these were real content conflicts, not the
  false ones claimed. The old entry's risk note also inverted the danger: it concluded
  "the tags happen to match, so the risk did not land." Both directions land — taking
  `main` wholesale drops `status:draft`, and keeping `status:draft` re-suspends the cards.

  **Resolution taken: `main`'s PVOM notes wholesale** (`git checkout main --
  domains/ua/anki/notes/pvom/`) — the same command the old entry gave, for the opposite
  reason, and confirmed by Craig 2026-08-19 as the verified, current content.
  `should_suspend()` in `ua_pvom_infinitive_import.py` is `"stress:unverified" in tags or
  "status:draft" in tags`, so the branch's `status:draft` and `main`'s `stress:verified`
  are the *same lever*, pulled opposite ways. `05d8e74` (2026-08-18) is Craig's own Горох
  pass and says outright that it unsuspends all 52 PVOM cards; `e53f14d` (2026-08-05)
  predates it by 13 days and was a **reporting** fix — its message is about
  `list_unverified.py` seeing PVOM notes in the "no status tag" bucket, not about
  suspension. It tripped a branch the importer had written only defensively ("no current
  PVOM note uses this tag, but checked for consistency … in case one ever does"). Keeping
  it would have silently re-dormanted the prefix set.

  **`ua-verb-0010.md`:** everything outside `Verification Notes` auto-merged correctly —
  `main`'s schema (`Participle_Passive_Past` consolidated, empty `UA_Example`/`EN_Example`
  dropped, space-form field name from `c020950`) plus the branch's `stress:verified`. Only
  the trailing paragraph conflicted; both sides kept, since the 2026-08-05 tag
  re-verification and the 2026-08-11 schema decision record different things.

  **Method note:** the wrong diagnosis came from `git merge-tree` plus a diff excerpt,
  which show *which* files collide but not what each tree holds. Reading the same file out
  of all three trees (`git show <ref>:<path>`) took one loop and contradicted it
  immediately. Prefer that — or just run the merge, since `--no-commit` is abortable.

  **Standing rule, restated after a violation in this session:** a `stress:verified` or
  `status:verified` tag is authoritative. Where one side of a merge has `verified` and the
  other `unverified` for the same note, the `verified` side wins and that is not a question
  to put to Craig. Claude proposed the opposite here — a resolution reverting 12 PVOM notes
  to `stress:unverified`, on the reasoning that a blanket flip was "a claim, not a fact."
  It was Craig's own Горох pass. Verification is set by Craig alone and is never re-opened,
  downgraded, or offered as a resolution option; no bulk or canonicalisation pass may emit
  `stress:unverified` as a default onto a note that already carried `verified`.

  **Do not resolve any future code conflict by taking the branch side wholesale**:
  `compute_euphony_slots()` and `TestComputeEuphonySlots` are *intentionally* deleted on
  `main`, and restoring them silently reverts Option B — exactly the failure mode that bit
  us twice on 2026-08-19.

- [x] **PVOM `status:` tag — APPLIED 2026-08-19, commit `53680f4`, needs only your tick.**
  Craig stated he was setting `status:verified`; all 13 notes tagged, one line each
  (`- status:verified`, after the existing `- stress:` tag), no field values or other tags
  touched. Confirmed working: PVOM no longer appears in `make ua-unverified` at all, and
  the 52 cards stay unsuspended — `should_suspend()` trips only on `stress:unverified` or
  `status:draft`. This closes `e53f14d`'s original goal (PVOM notes were falling into
  `list_unverified.py`'s "no status tag" bucket) without its side effect.

- [x] **`ua-verb-0017`–`0032` re-sourced from Горох — DONE 2026-08-19, Craig verified and
  tagged. Needs only your tick.** The unstressed Lemma that `make ua-unverified` surfaced
  was the visible symptom of a much larger defect: **182 of 224 conjugation fields were
  wrong**, not merely unmarked.

  **Root cause, `-ходити` group (`0017`–`0024`, 10/14 fields each):** Горох carries two
  homograph entries per spelling — a prefix-stressed imperfective (`прихо́дити`) and a
  stem-stressed perfective (`проходи́ти`). The stored paradigm was the **perfective** block
  while every note is tagged `Aspect: imperfective`. Same wrong-homograph-block failure as
  the `біг`/`Бог` bug. Three imperatives were not just mis-stressed but the wrong form
  outright: stored `приходи́`/`приході́м`/`приході́ть`, correct `прихо́дь`/`прихо́дьмо`/`прихо́дьте`.
  Per Craig: with the prefixes the stress is on `-хо́-`.

  **Root cause, `-їхати` group (`0025`–`0032`, 12–14 each):** wrong in its own way — stored
  `приїде́ш`/`приїде́м`/`приїдете́` against Горох's `приї́деш`/`приї́демо`/`приї́дете`, and
  `Imperative_1pl` stored as `приїдімте́`, a form Горох does not list. `0026` is the group's
  exception: `ви́їхати`, prefix-stressed, consistent with `ви́йти`.

  **Also fixed:** `0027`/`0032` were missing the U+02BC apostrophe in **all 14** fields, not
  just the Lemma — now `підʼї́хати` / `відʼї́хати`, confirmed by codepoint.

  **Watch on next `make ua-verb`:** these 16 were suspended via `stress:unverified`. With
  that cleared and no `status:` tag present — not a suspend reason for `ua_verb` — up to
  **64 cards** (16 × 4 templates) unsuspend on the next sync.

- [x] **`ua-verb-0001`–`0032` carry no `status:` tag at all** — the same gap PVOM had before
  `53680f4`. `0001`–`0032` are now all stress-verified but statusless, so they keep
  reporting under `[no status tag]` in `make ua-unverified` even though the data is sound.
  Same fix shape as PVOM: `status:verified` satisfies the report without changing suspension
  (for `ua_verb`, `should_suspend()` trips on `stress:unverified`, `status:draft`, or
  `conj:suspended` — never on absence). Craig's tag to set.

- [x] **`ua-lexeme-0116` lemma corrected to `вихо́дити` — DONE 2026-08-19 by Craig. Needs
  only your tick.** Surfaced while re-sourcing `ua-verb-0018`: the note had stored
  `ви́ходити` against the gloss "to go out, exit (on foot)". Горох's Тлумачення page carries
  three homographs — **ВИХО́ДИТИ**, imperfective, first sense "Іти звідки-небудь назовні, за
  межі чогось", with `ВИ́ЙТИ` as its perfective; plus two **ВИ́ХОДИТИ** entries that are bare
  cross-references to `вихо́джувати¹`/`²`. So the `-хо́-` form is the one that matches this
  note's gloss and its `Perfective: ви́йти`, and it now agrees with `ua-verb-0018`. Rechecked
  against Горох after the edit.

  ~~Two cosmetic leftovers on that note, not worth their own commit — fold them in next time
  it is touched:~~ **Both closed 2026-08-20** (PR #81). `Source_Note` had read "Stress
  verified 2026-07-06 via Горох" — boilerplate shared verbatim with 0114/0115 from the
  ch-09 batch, so not wrong as history, but on this note it implied the current lemma was
  checked then, when what was checked then was the superseded `ви́ходити`. It now records the
  2026-08-19 re-verification and keeps the earlier date as prior history; 0114 and 0115 keep
  the boilerplate untouched, since neither note's lemma changed. `Verification Notes` no
  longer ends "Needs your review" on a `status:verified` note — it carries the 2026-08-19
  correction record instead.

  **Still open on 0116, deliberately:** `Source_URL` points at the unstressed
  `goroh.pp.ua/Словозміна/виходити`, which does not distinguish the three homographs. Not
  wrong, but not evidence for the corrected lemma either — left for Craig, matching how
  0153/0379 were repointed by hand on 2026-08-19.

- [x] **`conj:` curation axis added to PVOM and applied to both corpora — DONE
  2026-08-19, verified live. Needs only your tick.** `UA_PVOM_Infinitive`'s
  `should_suspend()` had only two axes (`stress:unverified`, `status:draft`), so a note
  that was reviewed and correct could be kept out of the drilling rotation only by
  asserting it was unreviewed — which would pull it back into `list_unverified.py`'s
  report. Added `conj:suspended`, mirroring `ua_verb_import.py`. Three independent axes
  on both note types now: `stress:` = data confirmed, `status:` = content reviewed,
  `conj:` = drilled at all.

  Tagged per Craig's selection, chosen to cover the gamut of stress patterns (regular,
  prefix-stressed `ви́йти`/`ви́їхати`, `-ій-` epenthesis with apostrophe, and the в-/у-
  euphonic alternation): `conj:drill` on `при-`/`в-`/`ви-`/`під-` in PVOM and on
  `при-`/`ви-`/`під-` in both `UA_Verb` motion sets; `conj:suspended` on the rest.
  9 new tests pin the axis separation, including that `conj:drill` is not caught by a
  substring match. **Verified live:** `note:UA_PVOM_Infinitive -is:suspended` = 12 cards
  (not 16 — `ua-pvom-0012`'s red flag suspends the whole note regardless of tags).

- [x] **`ua-pvom-0012`'s red-flagged card** — `card_id 1784997131493`, `ord: 1`, the
  Walking (Uni) template (`ввійти́`). It is `conj:drill` and verified on both quality
  axes, so the red flag is the *only* thing keeping the в-/у- euphony note — the one note
  in the corpus with populated `*_Euphony` values — out of the rotation. Worth knowing why
  before clearing it: `05d8e74` flipped this note's Walking-Uni slot so в- became primary,
  and flagged `ухо́дити` as the weakest value with `NEEDS CRAIG DECISION`. A red flag on
  exactly that card looks like it motivated the flip rather than being unrelated. Find it
  with `flag:1 note:UA_PVOM_Infinitive`. If stale, clearing it in Anki is all that's
  needed — the next `make ua-pvom` unsuspends from the tags alone, no repo change.

  **DONE 2026-08-20. The guess above was right.** `flag:1 note:UA_PVOM_Infinitive`
  returned exactly one card, the Walking (Uni) `ввійти́` slot — the one `05d8e74` flipped.
  The flag marked the в-/у- primary-form question, which Shevchuk settled on 2026-08-18,
  so nothing was outstanding behind it.

  **Settled first, cleared second, and the order mattered.** The note's `Verification
  Notes` carried a standing `NEEDS CRAIG RE-CHECK` on its four `*_Euphony` stress
  placements. Clearing the flag puts all four cards into rotation, so a wrong mark would
  have gone straight into study. Craig checked the two Claude-drafted values against Горох
  — `ухо́дити` (`-хо́-`) and `увійти́` (`-йти́`), both confirmed; `уїжджа́ти`/`уї́хати` inherit
  `ua-lexeme-0124`. Then the flag was cleared and the record written (PR #82).

  **Verified live after `make ua-pvom`:** `note:UA_PVOM_Infinitive -is:suspended` = **16**
  (was 12), `is:suspended` = **36**. `ua-pvom-0012`'s four cards are drilling for the first
  time since the note type was built.

- [x] **Sweep the corpus for any other `ви́ходити`-shaped lemma** — the 0116 error was a
  prefix-stressed spelling standing in for a `-хо́-` imperfective, which is the same class of
  mistake as the `ua-verb-0017`–`0032` paradigm corruption. Worth one pass to confirm it was
  isolated rather than assuming:

      git grep -n "ви́ходити\|ви́хо" -- domains/ua/anki/notes/ | grep -v exported/

  **DONE 2026-08-20 — isolated, with one leftover, now fixed.** No other `Lemma` carried
  the prefix-stressed spelling. But `ua-lexeme-0115`'s `ConfusableSet` still named
  `ви́ходити` as входити's "directional opposite" — the homograph meaning *to wear out by
  prolonged walking*, not `вихо́дити`. The 0116 lemma correction had never reached the
  cross-reference pointing **at** 0116, so the Compare-card mnemonic named the wrong verb.
  Corrected in `fe4efcc`; see the tick item under Content verification below.
  A wider sweep for unstressed multisyllabic `Lemma`/`Perfective`/`*_UA` values across all
  five note types returned only the known `ua-verb-0033`–`0087` draft range plus
  `ua-lexeme-0151` (`триатлон`, a documented exception — Горох's declension table carries
  no mark on any form, per that note's own `Source_Note`).

---

See also: [CLAUDE-active-status.md](CLAUDE-active-status.md) for the narrative
status board, `CLAUDE.md`'s dated log for full context on any item above, and
`CLAUDE-ua-verb-qa-worklist.md` for the per-verb stress/participle breakdown.
