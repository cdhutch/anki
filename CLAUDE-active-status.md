# Active Status — Phase A Distractor Authoring

**Overall progress**: 26 of 29 systems verified ✅

**Last session**: 2026-07-10 (B737 paused; UA domain active — see below)

## Current Queue (3 remaining, smallest first)

| System | Total | Draft | Notes |
|--------|-------|-------|-------|
| engines | 41 | 39 | — |
| autoflight | 42 | 39 | — |
| pneumatics | 39 | 39 | — |

## Workflow per system

1. Author distractors in `.md` files
2. Call Claude for review, grammar, typo fixes
3. Run `make sve-fix` to canonicalize
4. Claude provides `git add` + `git commit`
5. Move to next system

## Import status notes

- `status:draft` imports as **suspended**
- `status:verified` imports as **active**

## Completed systems (all verified)

acars, adverse, air_conditioning, apu, atc_tcas_trans, communications, electrical, emergency_equipment, fire_protection, flight_controls, flight_instrumentation, flight_warning, fuel, general, gpws, hud, hydraulics, ice_and_rain_protection, landing_gear, lighting, navigation, oxygen, performance, pressurization, weather_radar

## Partial

- **fms**: sv-fms-024 intentional 2-choice; all others verified

---

## FSRS Deck Configuration (2026-07-10)

**Status:** Recommended parameters drafted for all three decks.

**Next:** Implement in Anki:
1. Create three deck configs: "B737 FSRS", "UA FSRS", "Legacy FSRS"
2. Assign to top-level decks (deck tree inherits config)
3. Verify isolation: card history completely disjoint across trees
4. Monitor actual retention after 2–3 weeks; adjust if needed

**Focus:** UA FSRS (0.85–0.90 desired retention) for language learning.

See **[CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md)** for specifications and implementation steps.

---

## Ukrainian Domain — Active Work (2026-07-10)

**Branch:** `feature/ua-l2-ch09-motion-verbs` (off `feature/ua-domain`)

### Template fix completed ✅ (2026-07-10)

**Root cause:** All three `update_*_model()` functions were calling `updateModelTemplates` in a loop
(once per template) instead of bundling all templates in a single call. AnkiConnect expects one
call with all templates.

**Fix:** Changed `update_model()`, `update_grammar_model()`, `update_visual_model()` to build a
single `templates_dict`, then call `updateModelTemplates` once per model.

**Status:** Templates now update correctly via `make ua-setup-visual`.

### UA_Lexeme field architecture finalized (2026-07-10)

**Completed:**
- Removed `Verb_Conj_Table` field from UA_Lexeme (moved to UA_Verb note type)
- Added `ImperfectiveUnidirectional` field for motion verbs (іти, їхати directional forms)
- Reorganized fields in semantic order (20 fields total):
  * Identity, Core Lemma, Aspect, Semantics, Grammar, Relations, Examples, Metadata
- Clarified `EuphonyNote` purpose: alternate spellings (уже/вже, всі/усі)
- Confirmed aspect convention: Lemma is imperfective (base); Perfective is counterpart
- Removed template references to deleted Verb_Conj_Table field

**Future work:**
- UA_Confusables note type for false friends (e.g., different verbs for "draw/paint")
- UA_Verb note type implementation + Phase 2a conjugations (~60–70 notes)
- Ch-09 import pipeline (lexemes → visual → grammar → verbs)

**Rationale:** Before importing ch-09 lexemes, we need the conjugation note type ready so prefixed motion verbs (18 lexemes) can link to base conjugations via tags, avoiding 1:1 coupling.

**Work:**
1. Define UA_Verb note type in `setup_ua_note_types.py` (20 fields + 2 card templates)
2. Author/batch-import Phase 2a verbs (~60–70: class leaders + irregulars)
3. Create 2 base verb notes for ch-09 (ходити, їхати) with class:leader + ch:2.9 tags
4. Tag ch-09 lexemes with `conj:motion-walking-ходити` / `conj:motion-vehicle-їхати`
5. Then proceed to ch-09 import pipeline

See **[CLAUDE-ua-verb-design.md](CLAUDE-ua-verb-design.md)** for full specification.

### ch-09 content status (held pending UA_Verb implementation)

| Type | Count | IDs | Status |
|------|-------|-----|--------|
| UA_Lexeme | 18 | ua-lexeme-0114–0131 | draft, not yet imported |
| UA_Grammar | 7 | ua-grammar-0001–0007 | draft, not yet imported |
| UA_Visual | 9 | ua-visual-0001–0009 | draft, not yet imported |
| UA_Verb (base motion) | 2 | (ходити, їхати) | TBD pending UA_Verb implementation |

All lexeme stresses Горох-verified. `Verb_Conj_Table` populated for all 18 lexemes.

### Updated import pipeline (post-UA_Verb)

```
1. Implement UA_Verb note type (20 fields, 2 templates)
2. Create & import Phase 2a base conjugations (~60–70 notes: class leaders + irregulars)
3. Create 2 ch-09 motion verb notes (ходити, їхати) tagged class:leader + ch:2.9 + conj:drill
4. Tag all 18 ch-09 lexemes with conj:motion-walking-* / conj:motion-vehicle-* linking tags
5. make ua-setup  (syncs all four note types to Anki)
6. make ua-batch BATCH=yabluko-l2/ch-09
7. make ua-grammar
8. make ua-visual
9. make ua-verb  (import conjugation notes)
```


---

## 2026-07-22 update — ch-09 punch list complete, ready for push + PR

Everything below the "Updated import pipeline (post-UA_Verb)" block above is now historical
context for HOW ch-09 got imported; here's where it landed.

### ch-09 content status (current)

| Type | Count | IDs | Status |
|------|-------|-----|--------|
| UA_Lexeme | 18 | ua-lexeme-0114–0131 | `status:verified`, imported, both UA→EN + EN→UA active |
| UA_Grammar | 9 | ua-grammar-0001–0009 | `status:draft`/suspended; 0008/0009 new (2026-07-22) |
| UA_Visual | 9 | ua-visual-0001–0009 | `status:verified`, imported, 1 template ("Prefix + Government") |
| UA_PVOM_Infinitive | 11 | ua-pvom-0001–0011 | imported, 4 templates/note = 44 cards |
| UA_Verb (base motion) | 32 | ua-verb-0001–0032 | imported (see project memory `project_ua_verb_phase2a`) |

### Import pipeline — all steps done

```
1. Implement UA_Verb note type          ✓ done
2. Import Phase 2a base conjugations    ✓ done (32 files in domains/ua/anki/notes/verbs/)
3. Create 2 ch-09 motion verb notes     ✓ done (ходити, їхати)
4. Tag ch-09 lexemes conj:motion-*      ✗ still not done — checked, 0/18 have the tag
5. make ua-setup                        ✓ done (all 4 note types synced, all footguns above fixed)
6. make ua-batch BATCH=yabluko-l2/ch-09 ✓ done 2026-07-22
7. make ua-grammar                      ✓ done 2026-07-22 (model rebuilt as real Cloze, footgun #5)
8. make ua-visual                       ✓ done — single-template redesign live
9. make ua-verb                         ✓ done
```

### 7-item PVOM polish punch list — all done

Full write-up with commit hashes lives in project memory (`project_ua_verb_phase2a.md`).
Summary: (1) PVOM reworked to 4 templates/note; (2/6) UA_Visual redesigned to single
template + Solarized palette; (3) UA_Visual↔UA_Lexeme EN_Gloss cross-check; (4) EN→UA
motion-verb suspend logic tried, found not to actually suspend in live Anki, reverted —
both directions active by design; (5) про-/пере- mnemonic via new `Mnemonic_EN` +
`CompareA`/`CompareB` fields, found and fixed 2 AnkiConnect bugs along the way; (7)
до/в-у/на + від/з-із-зі grammar notes (0008/0009), found and fixed the model-cloze-type
footgun (#5 above) along the way.

### Next steps (in order)

1. Push `feature/ua-verb-phase2a` + PR to main (Craig runs; Claude provides commands)
2. Check `UA::Production::EN→UA` deck-routing count for ch-00 (likely fixed as a side
   effect of the 2026-07-22 ch-00 re-import; not yet verified)
3. Decide on flipping UA_Grammar notes 0001–0009 from `status:draft` to `status:verified`
   (0008/0009 have real sourced citations already; 0001–0007 need a review pass)
4. Re-run `list_deck_presets.py` / `survey_card_states.py` to confirm counts

**New branch after this:** ch-09 vocabulary appendix parsing (Яблуко 2, chapter "9 Рух -
це життя") — separate from the motion-verb grammar work above; see
`domains/ua/anki/sources/yabluko/level-2/yabluko-l2-vocabulary.pdf`.
