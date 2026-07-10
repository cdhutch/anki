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

## Ukrainian Domain — Active Work (2026-07-10)

**Branch:** `feature/ua-l2-ch09-motion-verbs` (off `feature/ua-domain`)

### Template fix completed ✅ (2026-07-10)

**Root cause:** All three `update_*_model()` functions were calling `updateModelTemplates` in a loop
(once per template) instead of bundling all templates in a single call. AnkiConnect expects one
call with all templates.

**Fix:** Changed `update_model()`, `update_grammar_model()`, `update_visual_model()` to build a
single `templates_dict`, then call `updateModelTemplates` once per model.

**Status:** Templates now update correctly via `make ua-setup-visual`.

### Immediate next task: import ch-09 content

All three note types ready. Stresses Горох-verified; `Verb_Conj_Table` populated.

### ch-09 content status
| Type | Count | IDs | Status |
|------|-------|-----|--------|
| UA_Lexeme | 18 | ua-lexeme-0114–0131 | draft, not yet imported |
| UA_Grammar | 7 | ua-grammar-0001–0007 | draft, not yet imported |
| UA_Visual | 9 | ua-visual-0001–0009 | draft, not yet imported |

All stresses Горох-verified. `Verb_Conj_Table` populated for all 18 lexemes.
