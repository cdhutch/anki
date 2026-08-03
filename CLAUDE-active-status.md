# Active Status

Quick-reference status board — what's done, what's active, what's next, by domain. For
the full dated narrative log, decision rationale, and technical detail, see `CLAUDE.md`;
this file exists to answer "what's done and what's next" at a glance, not to replace that
log. Everything here traces back to specific `CLAUDE.md` log entries (dated) if you need
the full story.

**Reorganized and refreshed 2026-08-01** (previous version was last substantively updated
2026-07-22, and its content was reorganized under the old structure without being brought
current — this pass pulls forward everything material from `CLAUDE.md`'s log since then).
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
chapter by chapter (ch-09 imported and polished; ch-08 verification in progress; ch-09.2
sourced but not yet reviewed; ch-09.3+ not yet sourced).

## Current Projects

### Current Findings

- **Gruvbox palette rollout** — code complete, merged to `main` (2026-08-01) via
  `feature/anki-mobile-night-mode` (merge commit, branch kept alive on purpose). `make
  ua-setup` / `make ua-setup-pvom` have been run successfully. **Not yet confirmed:**
  the actual on-device three-pass visual check (Day / Night / Night + red-tint filter),
  especially whether the `palette-compare-status` demo card's red/orange status colors
  hold up under the red-tint filter. Treat this as "shipped, not yet validated" until
  that's reported back.
- **Ch-08 lexeme verification** (started 2026-07-30, ua-lexeme-044x–049x range) is
  mid-flight: a punch list of 6 confusable-set candidates, 1 aspect-pairing gap
  (0482 дотримуватися missing its `Perfective`), and 1 open usage question were raised.
  Of these: the 0484 (впасти→впадати) correction is done; the confusable-set candidates
  whose partner word isn't sourced yet are watchlist-tagged (`pending-confusable:<lemma>`)
  for automatic pickup once that word is added, not written into `ConfusableSet`/`CompareA-D`
  yet; the 0482 aspect-pairing gap and the раз-counting/мандрівка-vs-подорож questions were
  discussed and answered in conversation but not yet written into any field.
- **11 flagged notes** exist in the corpus. The audit/fix tooling (`ua_flag_audit.py`,
  Phase 1 query + Phase 3 apply) is built and tested; Phase 2 (the actual interactive
  walkthrough with Claude) hasn't happened yet.
- **ua-verb-0009/0010** have conjugation-table data that belongs to a different verb
  family than their own Lemma — found 2026-07-31, correct paradigms already sit in
  ua-verb-0086/0087's Verification Notes, fix held for a separate pass per Craig.
  Same for **CLAUDE.md item 10**: `UA_Grammar` 0001–0007 predate the 2026-07-22
  atomicity/no-leak cloze principles and haven't been audited against them.
  Same for two small 2026-07-22 loose ends that were never explicitly closed out in the
  log since: (a) none of the 18 ch-09 lexemes ever got their `conj:motion-walking-*` /
  `conj:motion-vehicle-*` linking tags (confirmed 0/18 as of 2026-07-22, no later
  confirmation found); (b) the `UA::Production::EN→UA` ch-00 deck-routing count was
  flagged as "likely fixed, not yet verified" and never explicitly re-checked.

### Next Actions

1. Confirm the Gruvbox on-device validation (three-pass walkthrough, `palette-compare-status`
   card specifically) and report back. Any fixes go on `feature/anki-mobile-night-mode`
   (kept alive for exactly this), then PR into `main` again.
2. Continue sourcing Yabluko L2 ch.9.3 onward (`gen_ch09_subsection.py` is built for this,
   just not yet exercised on a real batch).
3. Review/verify the ch.9.2 batch (18 lexemes ua-lexeme-0163–0180 + 5 conjugation notes
   ua-verb-0033–0037, currently `status:draft`) → flip to `status:verified`, re-sync.
4. Continue the ch-08 verification pass — write the confirmed confusable-set/aspect-pairing
   decisions into fields once Craig signs off on each.
5. Work through the 11 flagged notes with Claude (Phase 2 of the flagged-card workflow)
   whenever you're ready.
6. Apply the ua-verb-0009/0010 conjugation-table fix using the paradigms already sourced
   on ua-verb-0086/0087.
7. Review `status:draft` content pending verification: ua-lexeme-0581–0585 (motion-verb
   triplets), ua-verb-0086/0087 (плисти/поплисти).
8. Decide whether to revisit `UA_Grammar` 0001–0007 against the atomicity principles, and
   whether the two 2026-07-22 loose ends above (motion-verb tagging, EN→UA deck-routing
   count) still need checking.

## Future Projects

- **Per-slot euphony tolerance + verb-phrase aspect defaulting** — fully scoped with Craig
  2026-07-29, not built. See "Card Template Techniques" in `CLAUDE.md`.
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
- **EN→UA card front — show the English sentence** (added 2026-08-03): if not already the
  case, EN→UA cards should show the English example sentence on the front rather than just
  the bare word, so learners can disambiguate EN words that map to multiple distinct UA
  translations. Needs a check against the current live template to see if this is already
  true.
- **ua-lexeme-0106 ("goodbye") needs a Compare Card** (added 2026-08-03): several other UA
  words also translate to "goodbye" (Craig named папа/бувай as examples) that aren't
  currently distinguished from `ua-lexeme-0106`. Needs a confusable-set / Compare Card
  pass to help learners tell them apart.
- **Compare cards don't need a complete confusable set to start** (design note, added
  2026-08-03): Craig confirmed it's fine to build a Compare Card from a partial set of
  lexemes when the genuinely tricky members of a cluster are already known, rather than
  waiting until every member is sourced first.
- **UA→EN lexeme verb cards — show multiple aspects per euphonic slot** (added
  2026-08-03): cards should be able to display more than one aspect form (imperfective/
  perfective) per euphonic-variant slot, not just one. Relates to the existing "Per-slot
  euphony tolerance + verb-phrase aspect defaulting" item above — worth reconciling the
  two when either gets picked up.

## Completed Projects

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

**Status (2026-07-10, no later update found):** recommended FSRS parameters drafted for
all three top-level decks (B737, UA, Legacy). Full specs in
[CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md).

**Next Actions:**
1. Create three deck configs in Anki: "B737 FSRS", "UA FSRS", "Legacy FSRS".
2. Assign each to its top-level deck (the deck tree inherits the config).
3. Verify isolation — card history should be completely disjoint across the three trees.
4. Monitor actual retention after 2–3 weeks and adjust if needed. Focus area: UA FSRS
   (0.85–0.90 desired retention), since that's the domain with active daily use.

No confirmation found in `CLAUDE.md`'s log that this was actually implemented in Anki —
treat as still outstanding unless you know otherwise.
