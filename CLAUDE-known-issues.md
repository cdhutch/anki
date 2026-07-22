# Known Issues & Workarounds

| Issue | Workaround |
|-------|-----------|
| `make sve-fix` formatting | Runs `cnsf_canonicalize.py --write` — fixes YAML formatting automatically |
| YAML boolean coercion | True/False → true/false; fixed in `_normalize_meta()` in `tools/anki/cnsf_canonicalize.py` |
| YAML colon-at-end-of-value | Any field ending in `:` must be quoted, e.g. `Question Stem: 'You must select ALTN, then:'` |
| AnkiConnect `getDeckConfigs` | (plural) does NOT exist — use `cloneDeckConfigId` + `setDeckConfigId` (apply to temp deck) + `getDeckConfig` + `saveDeckConfig` |
| Git conflict markers | Use `tools/anki/setup/fix_conflict_markers.py` — strips markers, keeps HEAD (ours) |
| `sv_exam_md_to_tsv.py` error handling | Per-note errors no longer crash; all failures reported at end with note path; exit code 1 if any errors |
| `sv_exam_md_to_tsv.py` falsy values | `_s()` helper fixed to handle falsy non-None values (e.g. `0`) |
| `delete_sv_cloze.py` generalization | Generalised with `--model` flag (default: B737_SV_Cloze) |

| ✓ `UA_Visual` card templates not updating | **RESOLVED (2026-07-10)** — Root cause: all three `update_*_model()` functions called `updateModelTemplates` in a loop (one per template) instead of bundling all templates in a single call. Fixed by building single `templates_dict` and calling once per model. |

## AnkiConnect Footguns (learned 2026-07-20 through 2026-07-22)

| # | Footgun | Fix / workaround |
|---|---------|-------------------|
| 1 | `updateModelTemplates` silently no-ops for a template NAME that doesn't already exist on the model | Call `modelTemplateAdd` first for any brand-new template name (this auto-generates the card for every existing note of that model — expected Anki behavior, not a bug) |
| 2 | `updateModelTemplates`/`modelTemplateAdd` reject a template referencing a `{{Field}}` not yet on the model (`Field 'X' not found`) | In `setup_ua_note_types.py`, sync fields (additions) before any template call in all four `update_*_model()` functions; field *removal* stays last |
| 3 | `cardsInfo` result fields (e.g. `cardType`) are not reliable for identifying a card's template name — matches silently fail | Use `findCards` with a `"card:TemplateName"` search-query filter instead; Anki's own search parser resolving the name is the one mechanism proven reliable for deck routing / bulk actions (`changeDeck`, etc.) |
| 4 | The same `findCards` + `card:"Name"` technique verified correctly in dry-run but did NOT reliably `suspend` a *subset* of a note's cards in live Anki (whole-note `set_suspended()` does work) | Unresolved — don't reuse the targeted-suspend approach without re-verifying; whole-note suspend via `status:draft`/`status:verified` is the only proven-working suspend path |
| 5 | A model's cloze-vs-regular type is fixed at creation (`isCloze` in `createModel`) and **cannot be changed afterward via AnkiConnect** | If a model name already exists as the wrong type, no template fix helps — delete the note type in the Anki GUI (Tools → Manage Note Types → Delete; no AnkiConnect action exists for this) and let `create_*_model()` rebuild it fresh. Symptom: a note with N cloze numbers generates a card count matching the model's *existing template count*, not N |

## Retired Tools

**set_flow_detail.py** — superseded by `set_stage.py` override tags (`always_show` / `always_hide`). Do not use.
