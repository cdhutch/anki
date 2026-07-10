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

## Retired Tools

**set_flow_detail.py** — superseded by `set_stage.py` override tags (`always_show` / `always_hide`). Do not use.
