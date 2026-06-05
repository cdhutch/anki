# Active Status — Phase A Distractor Authoring

**Overall progress**: 26 of 29 systems verified ✅

**Last session**: 2026-05-25 (paused mid-execution)

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
