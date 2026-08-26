# Active Status

Quick-reference status board — what's done, what's active, what's next, by domain. For
the full dated narrative log, decision rationale, and technical detail, see `CLAUDE.md`;
this file exists to answer "what's done and what's next" at a glance, not to replace that
log. Everything here traces back to specific `CLAUDE.md` log entries (dated) if you need
the full story.

**For a checkbox-per-item list Craig checks off himself after personally verifying in
Anki/the repo (not from what this file or the CLAUDE.md log claims), see
[CLAUDE-work-queue.md](CLAUDE-work-queue.md).** This file and the CLAUDE.md log have both
drifted stale before (see CLAUDE-work-queue.md's intro) — treat the work-queue checkboxes
as the more trustworthy signal of what's actually confirmed done.

**Reorganized and refreshed 2026-08-01** (previous version was last substantively updated
2026-07-22, and its content was reorganized under the old structure without being brought
current — this pass pulls forward everything material from `CLAUDE.md`'s log since then).
**Corrected 2026-08-02:** the 2026-08-01 refresh still carried forward a stale claim
("ch-09.3+ not yet sourced") — see the dated `CLAUDE.md` log entry for 2026-08-02. Fixed
below (Summary line, Next Actions #2–#3).
Both domains share one CNSF-markdown-source → AnkiConnect-sync pipeline and the same
`status:draft` (imports suspended) / `status:verified` (imports active) convention.

---

# UA Domain

## Summary of domain

Formal Ukrainian language learning content (Galician/Lviv register), sourced from the
Яблуко textbook (Level 1 + Level 2) and Горох-verified. Five live Anki note types —
`UA_Lexeme`, `UA_Grammar`, `UA_Visual`, `UA_Verb`, `UA_PVOM_Infinitive` — built from CNSF
markdown source files under `domains/ua/anki/notes/` and synced via AnkiConnect
(`tools/anki/setup/setup_ua_note_types.py` / `setup_ua_pvom_note_type.py`, `make ua-setup`
family of targets). Level 1 ch-00 (Вступ) is complete and verified; Level 2 is in progress
chapter by chapter (ch-09 imported and polished; ch-08 verification in progress). Ch-09
vocabulary (subsections 9.1–9.7, all of it) is fully sourced and `UA_Lexeme`-verified —
only `ua-lexeme-0369`/`0584`/`0585` remain draft. The linked `UA_Verb` conjugation notes
are the real gap: **50** of them (`ua-verb-0038`–`0085`, plus `0086`/`0087`) are still
`status:draft` and `stress:unverified`, missing participles/examples.
**NEEDS CRAIG — the draft-verb counts do not reconcile across the docs (noticed
2026-08-20).** Three labels are in play for the same set: this line's **50**
(`0038`–`0085` = 48, plus `0086`/`0087`); Next Action #3's **55** for the range
`0033`–`0085`, which actually contains **53** and only reaches 55 by silently pulling in
`0086`/`0087`; and the work queue's "55 draft … **48** still `stress:unverified`", whose
48 matches `0038`–`0085` alone. The underlying facts look consistent — `0033`–`0037`
stress-verified, `0038`–`0085` = 48 unverified, `0086`/`0087` = 2 more — but the labels
are not, and the scope of `0086`/`0087` shifts line to line. Left unresolved on purpose
rather than picking a number and making it look settled. `0033`–`0037` moved
to `status:verified` 2026-08-19 (they were already stress-verified); they stay suspended
via `conj:suspended`, which is now a separate axis from review state. `0001`–`0032` are
fully verified on both axes as of 2026-08-19.

## Current Projects

### Current Findings

- **Gruvbox palette rollout** — code complete, merged to `main` (2026-08-01) via
  `feature/anki-mobile-night-mode` (merge commit, branch kept alive on purpose). `make
  ua-setup` / `make ua-setup-pvom` have been run successfully. **Not yet confirmed:**
  the actual on-device three-pass visual check (Day / Night / Night + red-tint filter),
  especially whether the `palette-compare-status` demo card's red/orange status colors
  hold up under the red-tint filter. Treat this as "shipped, not yet validated" until
  that's reported back.
- **Per-slot euphony tolerance/display + EN→UA example sentence** (structural queue items
  #3/#4/#5) — code complete and unit-tested on `feature/ua-lexeme-aspect-euphony-cards`
  (2026-08-04): new `Lemma_Euphony`/`ImperfectiveUnidirectional_Euphony`/
  `Perfective_Euphony`/`_EuphonySlots`/`_UA_EN_DisplayLemma` fields, per-slot tolerance in
  `EN_UA_BACK`'s feedback script, `EN_Example` added to `EN_UA_FRONT`. 12/12 new tests pass
  (`tests/ua/test_lexeme_import.py`, `TestComputeEuphonySlots`/`TestComputeUaEnDisplay`).
  ~~**Not yet confirmed:** `make ua-setup-lexeme`/`make ua-lexeme` haven't been run and no
  card has been eyeballed in Anki yet~~ — **stale; both were run and spot-checked
  2026-08-18** (work queue, `make ua-lexeme` 585 updated / 0 errors). Superseded outright
  by the 2026-08-19 Option B refactor, which replaced `_EuphonySlots` with `_TypingSpec`.
- **~~Two pre-existing `tests/ua/test_lexeme_import.py` failure groups found 2026-08-04,
  parked~~ — RESOLVED 2026-08-11** (unrelated to the euphony work above): `TestComputeTypingTarget` (8 failures)
  tests the shelved 2026-07-25 `Lemma_Euphony` redesign (`881ac25`/`2e93202`, dict-returning
  `compute_typing_target()`) that was reverted back to the simpler `a5b4a15` design by
  2026-07-28 — the test file was never updated to match. `TestPruneOrphansSafetyGate`
  (5 failures) references `prune_orphans`/`collect_all_corpus_note_ids`/
  `all_anki_note_ids`/`delete_notes`, none of which exist anywhere in the repo
  (grep-confirmed) — the same "`prune_orphans` gap" already flagged in passing on
  2026-07-31 (see the `Verb_Conj_Table` Removal Plan section in `CLAUDE.md`). Both branch
  and `main` sit at the `maint/lexeme-review` merge (PR #63) — likely source of both
  mismatches, not yet investigated.
- **Ch-08 lexeme verification** (started 2026-07-30, ua-lexeme-044x–049x range) is
  mid-flight: a punch list of 6 confusable-set candidates, 1 aspect-pairing gap
  (0482 дотримуватися missing its `Perfective`), and 1 open usage question were raised.
  Of these: the 0484 (впасти→впадати) correction is done; the confusable-set candidates
  whose partner word isn't sourced yet are watchlist-tagged (`pending-confusable:<lemma>`)
  for automatic pickup once that word is added, not yet written into `ConfusableSet` or added
  as a member to `domains/ua/anki/confusable_clusters.yaml` (the `CompareA-D` mechanism this
  used to name was removed 2026-08-26); the 0482 aspect-pairing gap and the раз-counting/мандрівка-vs-подорож questions were
  discussed and answered in conversation but not yet written into any field.
- **40 flagged notes** exist in the corpus — **14 red + 26 orange**, read straight off
  the 2026-08-18 `make ua-pvom` output. The "11 flagged notes" figure this file carried
  until 2026-08-20 was stale, and so is `flagged_cards_manifest.json`, which holds 28
  from an older `--query` run; re-run `python tools/anki/inspect/ua_flag_audit.py --query`
  to refresh the manifest before Phase 2, which needs the note list rather than the count.
  The audit/fix tooling (`ua_flag_audit.py`, Phase 1 query + Phase 3 apply) is built and
  tested; Phase 2 (the actual interactive walkthrough with Claude) hasn't happened yet.
- **Dangling branch `archive/ua-verb-participle-merge-and-stress-pass` found 2026-08-04**
  (see CLAUDE.md item 13 under "Remaining Work"). A locally-deleted branch, still live as
  `origin/chore/ua-verb-participle-merge-and-stress-pass` (`f907726`), holds a real
  stress-verification pass across all 87 `ua-verb-*.md` notes plus a
  `Participle_Passive_Past_m`/`_f` → single-field schema consolidation, none of it merged
  to `main`. Per Craig, its verified content is truth — already applied to `ua-verb-0009`/
  `0010` (see Completed Projects). Tag command given to Craig, not yet run:
  `git tag archive/ua-verb-participle-merge-and-stress-pass f907726 && git push origin
  archive/ua-verb-participle-merge-and-stress-pass`. Full reconciliation (0086/0087's
  -мо-only sweep, the participle-field schema migration, the remaining 0002–0087 data) is
  still open — see Future Projects.
- **~~Two-branch plan for today's #3/#4/#5 + conjugation work (per Craig)~~ — superseded;
  this was 2026-08-04 and both branches merged long since.** structure and
  content stay on separate branches, not just separate commits.
  `feature/ua-lexeme-aspect-euphony-cards` stays scoped to the #3/#4/#5 code/tests only;
  a second, stacked branch (working name
  `content/ua-motion-verb-euphony-and-conjugation-fixes`) carries `ua-lexeme-0581`/`0584`,
  `ua-verb-0009`/`0010`, and the matching CLAUDE.md/CLAUDE-active-status.md doc hunks.
  Exact commands given to Craig; not yet run.
- **CLAUDE.md item 10**: `UA_Grammar` 0001–0007 predate the 2026-07-22 atomicity/no-leak
  cloze principles and haven't been audited against them. Also two small 2026-07-22 loose
  ends that were never explicitly closed out in the log since: (a) none of the 18 ch-09
  lexemes ever got their `conj:motion-walking-*` / `conj:motion-vehicle-*` linking tags
  (confirmed 0/18 as of 2026-07-22, no later confirmation found); (b) the
  `UA::Production::EN→UA` ch-00 deck-routing count was flagged as "likely fixed, not yet
  verified" and never explicitly re-checked.

### Next Actions

1. ~~Confirm the Gruvbox on-device validation (three-pass walkthrough,
   `palette-compare-status` card specifically) and report back.~~ **Done — ticked in the
   work queue**, confirmed against live `UA_Lexeme`/`UA_Verb` cards.
2. **Corrected 2026-08-02 — no longer accurate, see below.** ~~Continue sourcing Yabluko
   L2 ch.9.3 onward~~ — all of ch:2.9.1–2.9.7 is already sourced and lexeme-verified.
   `gen_ch09_subsection.py` remains unexercised on a real batch, but there's no more ch-09
   vocabulary left to run it against unless a new subsection/chapter is added.
3. Finish the 55 draft `UA_Verb` conjugation notes (`ua-verb-0033`–`0085`, spanning
   ch:2.9.2–2.9.7 and a ch:2.8.x batch): Craig is running the Горох stress-verification
   pass directly (only 0033–0037 are currently `stress:verified` — **corrected 2026-08-20**,
   this line used to include 0086/0087, which are in fact still `stress:unverified` +
   `status:draft`; confirmed by reading their tags, and by an unstressed-multisyllabic-Lemma
   sweep that surfaced both alongside the 0033–0085 range); once
   that lands, fill the required `Participle_Adverbial_Past` field (currently blank on
   all 55) plus other participles/examples where findable, then flip to `status:verified`
   and re-sync with `make ua-verb`.
4. Continue the ch-08 verification pass — write the confirmed confusable-set/aspect-pairing
   decisions into fields once Craig signs off on each.
5. Work through the **40** flagged notes with Claude (Phase 2 of the flagged-card
   workflow) whenever you're ready. **Corrected 2026-08-20** — this line said 11, which
   contradicted the "40 flagged notes" finding above in this same file. The live figure is
   14 red + 26 orange; `flagged_cards_manifest.json`'s 28 is also stale. Re-run
   `ua_flag_audit.py --query` for the note list before starting.
6. ~~Apply the ua-verb-0009/0010 conjugation-table fix~~ — **Done 2026-08-04.** See
   Completed Projects below.
7. Review `status:draft` content pending verification: ua-lexeme-0581–0585 (motion-verb
   triplets), ua-verb-0086/0087 (плисти/поплисти).
8. Decide whether to revisit `UA_Grammar` 0001–0007 against the atomicity principles, and
   whether the two 2026-07-22 loose ends above (motion-verb tagging, EN→UA deck-routing
   count) still need checking.
9. ~~Confirm the #3/#4/#5 on-device validation (per-slot euphony tolerance/display + EN→UA
   example sentence).~~ **Done 2026-08-18**, and the mechanism it describes no longer
   exists — `_EuphonySlots` was replaced by `_TypingSpec` in the 2026-08-19 Option B
   refactor, validated across 14 typed cases. The `EN_UA_FRONT` example sentence is
   confirmed working and ticked.
10. ~~Troubleshoot the two pre-existing `tests/ua/test_lexeme_import.py` failure groups
    parked 2026-08-04.~~ **Done 2026-08-11** — `TestComputeTypingTarget` rewritten against
    the live behaviour, `TestPruneOrphansSafetyGate` deleted per Craig. Ticked in the work
    queue.
11. ~~Run the two-branch commit sequence for today's #3/#4/#5 + conjugation work~~ —
    superseded (2026-08-04; both merged). **The `archive/ua-verb-participle-merge-and-stress-pass`
    tag + push is still outstanding** and is the part worth keeping: it is the only thing
    protecting `f907726` from garbage collection.
12. Plan and execute the full reconciliation of `archive/ua-verb-participle-merge-and-stress-pass`
    into `main` — see CLAUDE.md item 13 under "Remaining Work" for the three open pieces
    (0086/0087 -мо-only sweep, `Participle_Passive_Past` schema migration, remaining
    0002–0087 conjugation-data check).

## Future Projects

- **Per-slot euphony tolerance + verb-phrase aspect defaulting** — fully scoped with Craig
  2026-07-29. **Item 1 (per-slot tolerance) code-complete 2026-08-04**, see Current Findings
  above and Next Action #9 — not yet on-device validated. Item 2 (verb-phrase aspect
  defaulting) is authoring guidance only ("no new field"), still not acted on. See "Card
  Template Techniques" in `CLAUDE.md`.
- **Extending the Gruvbox palette to B737** — explicitly out of scope for the 2026-08-01
  rollout (UA-only, CSS-only per Craig's instruction); an open decision if wanted later.
- **`domains/ua/anki/docs/design.md` refresh** — stale relative to the live schema
  (predates `CounterpartForm`/`AspectCue`/`TypingTarget_UA` and others). Bigger task, not
  urgent.
- **`UA_Confusables` note type for false friends** — listed as future work back on
  2026-07-10, before the `ConfusableSet`/Compare-card (CompareA-D) mechanism existed.
  That mechanism now appears to cover this need directly; flagging here rather than
  silently dropping it, in case Craig still wants a dedicated note type for some case the
  Compare card doesn't handle.
- **Confusable set — motion-lexeme cluster** (added 2026-08-03): Craig flagged three
  related groups needing a Compare-card pass — the `-правлятися`/`-правитися` reflexive
  verbs together with their `-правлення` noun counterparts, `вирушати`, and the PVOM
  (Prefixed Verbs of Motion) set. All cluster around similar "set off / depart / direct
  oneself" motion vocabulary that's easy to confuse.
- **EN→UA card front — show the English sentence** (added 2026-08-03). **Code-complete
  2026-08-04** — confirmed this was genuinely missing (not already-true); `EN_UA_FRONT` now
  shows `EN_Example`, see Current Findings above and Next Action #9. Not yet on-device
  validated.
- **ua-lexeme-0106 ("goodbye") needs a Compare Card** (added 2026-08-03): several other UA
  words also translate to "goodbye" (Craig named папа/бувай as examples) that aren't
  currently distinguished from `ua-lexeme-0106`. Needs a confusable-set / Compare Card
  pass to help learners tell them apart.
- **Compare cards don't need a complete confusable set to start** (design note, added
  2026-08-03): Craig confirmed it's fine to build a Compare Card from a partial set of
  lexemes when the genuinely tricky members of a cluster are already known, rather than
  waiting until every member is sourced first.
- **UA→EN lexeme verb cards — show multiple aspects per euphonic slot** (added
  2026-08-03). **Code-complete 2026-08-04**, reconciled with the "Per-slot euphony
  tolerance" item above via a new, deliberately separate `_UA_EN_DisplayLemma` field (kept
  apart from `TypingTarget_UA` so the EN→UA typing target never grows parentheticals) — see
  Current Findings above and Next Action #9. The parenthetical display format
  (`"primary (euphonic)"`) was Claude's naming/format call, not yet confirmed by Craig — flag
  for feedback during the on-device spot-check.
- **Motion verb classes — add an "arriving" category** (added 2026-08-03): incorporate
  прибува́ти / прибу́ти into the set of "arriving" verbs of motion that need to be tracked
  and managed like the existing walking/vehicle/swimming/running/flying classes (see the
  `VerbClass` tags on `ua-verb-*`, e.g. `motion-walking-new`, `motion-vehicle-prefixed`).
  `ua-verb-0064` (прибувати) currently has `VerbClass: regular-1` — not yet part of that
  taxonomy — and the perfective прибу́ти doesn't have its own `UA_Verb` note yet.

## Completed Projects

- **`ua-pvom-0012` verification record + red flag cleared** (2026-08-20, PR #82). The
  flag sat on the Walking (Uni) `ввійти́` card — the slot `05d8e74` flipped — and marked the
  в-/у- primary-form question Shevchuk settled 2026-08-18, so nothing was outstanding
  behind it. **Settled before cleared, deliberately:** the note carried a standing
  `NEEDS CRAIG RE-CHECK` on its four `*_Euphony` stress placements, and clearing the flag
  activates all four cards. Craig confirmed `ухо́дити` (`-хо́-`) and `увійти́` (`-йти́`)
  against Горох; `уїжджа́ти`/`уї́хати` inherit `ua-lexeme-0124`. Two stale lines in that
  field also corrected. Live after `make ua-pvom`: `-is:suspended` = **16** (was 12),
  `is:suspended` = 36 — the note is drilling for the first time since the type was built.

- **`ua-lexeme-0116` stale verification leftovers closed** (2026-08-20, PR #81), flagged
  2026-08-19 as "fold in next time this note is touched." `Source_Note` no longer implies
  the current lemma was checked 2026-07-06 (what was checked then was the superseded
  `ви́ходити`); `Verification Notes` no longer ends "Needs your review" on a
  `status:verified` note. `Source_URL` deliberately left for Craig — the unstressed URL
  does not distinguish the homographs. 0114/0115 keep the shared boilerplate, their lemmas
  being unchanged.

- **`Source_Note` joins the always-present set for `UA_Verb`** (2026-08-20, `3a3c7f8`,
  PR #80) — the last item under YAML/CNSF schema consistency. Option A per Craig:
  blank-backfill, 86 notes, one inserted line each. `make ua-check` now reports all 25
  canonical fields present on all 87 notes, and **four of five note types are clean**. The
  1-of-87 note holding the field turned out to be a discharged planning to-do, not a source
  record. Scoped to `ua_verb` so B737's `Source Document` is untouched. `make ua-test` 442.
  Note the item's own goal — "turn on `make ua-check STRICT=1`" — was never reachable:
  `--strict` is global and `UA_Lexeme`'s five computed fields can never be present. The
  per-note-type form passes; wiring it into the Makefile is a new work-queue item.

- **PVOM euphony PERFECT tier + two shared-code hoists + flag scoping + `TypingAnswer`
  canonicalization** (2026-08-20, commit `fe4efcc`, PR #79, merged and live-validated).
  Five work-queue items in one commit — they are import-coupled, so any split leaves an
  unimportable intermediate commit, and `.githooks/pre-commit` runs `--all-files` on top
  of that (the `1baf0c2` constraint again). (1) PVOM euphonic alternates could not reach
  PERFECT: `euphonyAlts` was stress-stripped on the way in and the typed answer stripped
  again at the comparison, so `ухо́дити` and `уходити` were the same string. Alternates are
  now stored stressed and both stressed comparisons run above both unstressed ones —
  validated by Craig across four typed cases, with `уходити → ~ CORRECT` as the
  load-bearing one (the symmetric failure). **Desktop-only in effect:** stress marks
  cannot be typed on the phone, so mobile study lands at CORRECT either way. (2)
  `normalizeTypeansText()` hoisted to `tools/anki/lib/typeans_js.py` — one body instead of
  two hand-synced copies, which came within one test of failing on 2026-08-19. (3) The
  orange flag call-out is scoped to the note type being synced; `ua_flag_audit.py`
  deliberately stays whole-tree. (4) 61 CNSF notes' `TypingAnswer` brought in line with
  the aspect-slot join (the count logged 2026-08-19 as 62 was one high); scoped strictly
  to doublets/triplets, since singlets are authored and not derivable. (5) The unreachable
  Compare-card suspend warning reworded. Also: `ua-lexeme-0115`'s `ConfusableSet`
  corrected `ви́ходити` → `вихо́дити`, found by the sweep confirming the 0116 error was
  otherwise isolated — **wants Craig's tick**, being a content change on a
  `status:verified` note. `make ua-test` 437 passed (was 384). `make ua-setup-pvom` and
  `make ua-setup-lexeme` both clean with `sync_field_order()` making zero calls. Full
  detail in `CLAUDE.md`'s 2026-08-20 entry.

- **ua-verb-0017–0032 re-sourced from Горох + `conj:` curation axis** (2026-08-19,
  commits `0c12a5a`/`53680f4`/`7657034`, all synced live). `make ua-unverified` flagged an
  unstressed multisyllabic `Lemma` on all 16 prefixed motion verbs — the documented
  signature of a bad extraction. It turned out **182 of 224 conjugation fields were
  wrong**: for the `-ходити` group, Горох carries two homographs per spelling and the
  stored paradigm was the stem-stressed **perfective** block on notes tagged
  `Aspect: imperfective` (the `біг`/`Бог` failure again); three imperatives were the wrong
  form outright. The `-їхати` group had its own variant of the same problem, and
  `0027`/`0032` were missing the U+02BC apostrophe in all 14 fields. Claude sourced and
  drafted; Craig verified all 16 against Горох and set `stress:verified`. Also in this
  pass: `conj:suspended` added to PVOM's `should_suspend()` so curation is a third axis
  independent of `stress:`/`status:` (9 new tests); `status:verified` filled in across
  `ua-verb-0001`–`0037`; `Tags_Conj` deleted in favour of Anki's built-in `{{Tags}}`;
  `ua-lexeme-0116` corrected to `вихо́дити`. `make ua-test` 384 passed. Live: `ua-verb`
  87/87, `ua-pvom` 13/13, `ua-lexeme` 585/585, 0 errors; PVOM active card count confirmed
  at 12. Full detail in `CLAUDE.md`'s 2026-08-19 (later session) entry.

- **ua-verb-0009/0010 conjugation-table fix** (2026-08-04): both notes were populated with
  a different verb's paradigm (`0009`/пливти had плинути's forms; `0010`/попливти had
  попити's) — found 2026-07-31, fixed today. `0009` used the already-Горох-verified
  paradigm sourced alongside `ua-verb-0086` (плисти) on 2026-07-31; `0010` needed its own
  fresh Горох lookup (попливти́, goroh.pp.ua/Словозміна/попливти), fetched live via Claude
  in Chrome since `ua-verb-0087`'s 2026-07-31 sourcing only covered поплисти itself, not
  попливти. Both now `stress:verified`. Confirms the same present/imperative-identical,
  past-divergent pattern holds for попливти/поплисти as for пливти/плисти. **Reconciled
  further, same day**, against a dangling commit (`f907726`,
  `archive/ua-verb-participle-merge-and-stress-pass`, see Current Findings below) treated
  as source of truth per Craig: added missing `Lemma` stress marks, and simplified
  `Pres_1pl`/`Imperative_1pl` to the -мо-only form (project convention now — both -м/-мо
  free variants are Горох-valid, this is a "one canonical form" choice, not a correctness
  fix). `0009` also picked up `Participle_Adverbial_Present: пливучи́` from the same source.
- Ch-00 (Вступ, Level 1): 113 notes, `status:verified`.
- Ch-09 (Level 2) motion-verb polish: full 7-item punch list complete, imported, synced
  (18 `UA_Lexeme`, 9 `UA_Grammar`, 9 `UA_Visual`, 11 `UA_PVOM_Infinitive` × 4 templates,
  32 `UA_Verb`).
- `UA_Visual` redesign — single "Prefix + Government" template (was 2 templates).
- `UA_PVOM_Infinitive` rework — 22 single-form notes → 11 notes × 4 templates.
- Vocabulary dedup/homograph audit tooling, built and run against the full corpus.
- Compare-card CompareA-D/CompareScenario redesign, plus the `compute_compare_options()`
  clobbering-bug fix and the тепло Compare-card content-gap fix + corpus-wide sweep.
- EN→UA aspect+euphony typing restoration (recovered the `a5b4a15` design via git
  archaeology).
- UA→EN front aspect display (`_AspectLabel`).
- Compare-card suspend mechanism — tested and confirmed working via 3 disposable scratch
  notes.
- Flagged Card Fix Workflow tooling (Phase 1 query + Phase 3 apply) — built and tested.
- `Verb_Conj_Table` field removal — fully complete (model + all 584 CNSF source files),
  merged via PR #58.
- CSS single-source-of-truth decision (`setup_ua_note_types.py` for all four live UA note
  types) and the `UA_Visual` `.night_mode` → `.nightMode` selector fix — both merged to
  `main`. (The Gruvbox palette itself stays under Current Projects until on-device
  validation is confirmed — see above.)

---

# B737 Domain

## Summary of domain

Type-rating study content (systems knowledge, checklists, mnemonics, SV cards) — CNSF
markdown → TSV → AnkiConnect import pipeline. High-stakes professional content. Work here
has been paused since 2026-07-10 in favor of UA domain work; the active initiative
whenever it resumes is Phase A distractor authoring.

## Current Projects

### Current Findings

- **Phase A distractor authoring: 26 of 29 systems verified.** 3 remain, all with
  distractors drafted but not yet reviewed: `engines` (39/41 items drafted), `autoflight`
  (39/42), `pneumatics` (39/39, fully drafted). `fms` is a documented partial: sv-fms-024
  is intentionally 2-choice, everything else in that system is verified.
- B737 CSS was audited 2026-07-30/31 as part of the UA palette work and found already
  correct — `B737_Checklist`/`Mnemonic`/`Structured`/`SV_MCQ`/`SV_TF` all already use
  `.nightMode` with real Solarized colors, and `update_legacy_css.py`'s B737 blocks
  (`SV_CLOZE_CSS`, `B737_SYSTEMS_CSS`) were untouched by the Gruvbox rollout — B737 stayed
  on Solarized throughout, deliberately.

### Next Actions

1. Resume Phase A distractor authoring on the 3 remaining systems (`engines` →
   `autoflight` → `pneumatics`, smallest first): author distractors in the `.md` files,
   Claude reviews for grammar/typos, `make sve-fix` to canonicalize, Claude provides
   `git add`/`git commit`, move to the next system.
2. No other B737-specific work is currently queued — everything else in this domain is
   paused pending Phase A completion or a decision to resume it.

## Future Projects

- Decide whether to extend the Gruvbox palette rollout to B737 note types (see UA
  Domain's Future Projects — same open decision, noted once there).

## Completed Projects

- 24 of 29 systems fully verified: acars, adverse, air_conditioning, apu, atc_tcas_trans,
  communications, electrical, emergency_equipment, fire_protection, flight_controls,
  flight_instrumentation, flight_warning, fuel, general, gpws, hud, hydraulics,
  ice_and_rain_protection, landing_gear, lighting, navigation, oxygen, performance,
  pressurization, weather_radar.
- `.nightMode`/Solarized CSS confirmed correct across all 5 legacy B737 note types
  (audited 2026-07-30/31, no fix needed).

---

# FSRS Deck Configuration (cross-domain)

**Status 2026-08-20: the three-preset plan is dead; the repo now mirrors Anki instead.**
[DECK_PRESETS.md](DECK_PRESETS.md) is the single authority, with one file per preset under
`presets/`. ~~[CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md)~~ is superseded and
bannered as history.

What actually happened: `UA FSRS` and `B737 FSRS` were created but never assigned to
anything, sat on **zero decks**, and were pruned as orphans along with 51 others. The
collection went from 85 presets to 32. `Legacy FSRS` survives on one deck. No preset was
ever "assigned to its top-level deck" as the plan below described — the UA tree runs on
nine per-deck presets and B737 on seven, which is a different architecture entirely.

**Still open, and genuinely unresolved:**

1. **Retention is 0.9 everywhere.** The superseded file argued 0.93–0.95 for B737 as
   safety-critical and 0.85–0.90 for UA. UA's 0.9 sits at the top of its band; B737 is
   below its. Worth deciding on its own merits — see DECK_PRESETS.md section 5.
2. **Nine presets carry FSRS parameters optimized for other content.** Eight UA presets and
   `B737` share one bit-identical `fsrsParams6` vector, which can only be a clone artifact;
   `B737 Checklists` is on stock defaults. Wants a re-optimization pass.
3. **15 Legacy presets are unspecified** — DECK_PRESETS.md section 4.

**Isolation, the plan's original goal, is already satisfied** — the UA and B737 preset sets
are disjoint, so no preset is shared across trees. It did not need three dedicated presets
to achieve.
