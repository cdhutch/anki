# Deck to Preset Mapping

## UA Domain

| Deck | Preset | New | Review | Notes |
|------|--------|-----|--------|-------|
| UA | UA | 50 | 100 | Senior parent - throttles all UA |
| UA::Production | (pass-through) | 9999 | 9999 | Middle parent - no throttling |
| UA::Production::EN→UA | UA Lexeme EN→UA | 15 | 8 | High load: production/typing |
| UA::Recognition | (pass-through) | 9999 | 9999 | Middle parent - no throttling |
| UA::Recognition::PVOM | UA PVOM | 18 | 6 | High load: infinitive typing |
| UA::Recognition::UA→EN | UA->EN | 20 | 9999 | Medium load: recognition (unlimited reviews) |
| UA::Recognition::Visual | UA Visual | 25 | 10 | Low load: visual/diagram recognition |
| UA::Recognition::Grammar | UA Grammar | 20 | 8 | Medium load: grammar rules |
| UA::Verbs | UA Verbs | 20 | 8 | Medium load: verb conjugation |

## B737 Domain

| Deck | Preset | New | Review | Notes |
|------|--------|-----|--------|-------|
| B737 | B737 | 0 | 200 | Review-only, type rating |
| B737::FO Procedures | B737 | 0 | 200 | (inherits from parent) |
| B737::FO Systems | B737 | 0 | 200 | (inherits from parent) |
| B737::FO Challenges | B737 | 0 | 200 | (inherits from parent) |

## Notes

- **Pass-through presets** (9999/9999) allow child decks with explicit presets to set their own limits
- **Senior parent** (UA) sets overall budget cap
- Child decks must have explicit preset assignments to override parent/middle parent
- Verify assignments with: `python tools/anki/inspect/list_deck_presets.py`
