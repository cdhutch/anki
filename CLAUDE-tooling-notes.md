# Tooling Notes & Key Paths

## Known Issues & Workarounds

- `make sve-fix` runs `cnsf_canonicalize.py --write` — fixes YAML formatting
- **YAML boolean coercion**: True/False → true/false; fixed in `_normalize_meta()` in `tools/anki/cnsf_canonicalize.py`
- **YAML colon-at-end-of-value**: any field ending in `:` must be quoted, e.g. `Question Stem: 'You must select ALTN, then:'`
- **AnkiConnect gotcha**: `getDeckConfigs` (plural) does NOT exist — use `cloneDeckConfigId` + `setDeckConfigId` (apply to temp deck) + `getDeckConfig` + `saveDeckConfig`
- `tools/anki/setup/fix_conflict_markers.py`: strips git conflict markers from working tree, keeping HEAD (ours) — created for post-merge cleanup
- `sv_exam_md_to_tsv.py`: per-note errors no longer crash; all failures reported at end with note path; exit code 1 if any errors
- `sv_exam_md_to_tsv.py`: `_s()` helper fixed to handle falsy non-None values (e.g. `0`)
- `delete_sv_cloze.py`: generalised with `--model` flag (default: B737_SV_Cloze)

---

## Key Paths

| Path | Purpose |
|---|---|
| `domains/b737/anki/notes/systems_verification/` | SV note source files |
| `domains/b737/anki/docs/systems_verification/sv_exam_mode_schema.md` | Full schema spec |
| `build/` | Generated TSV output files |
| `tools/anki/export/sv_exam_md_to_tsv.py` | Converts exam_draft notes → TSV |
| `tools/anki/sync/sv_exam_import_to_anki.py` | Imports TSV into Anki via AnkiConnect |
| `tools/anki/setup/create_sv_exam_preset.py` | Creates "B737 SV Exam" deck preset |
| `tools/anki/setup/delete_sv_cloze.py` | Deletes all legacy B737_SV_Cloze notes |
| `tools/anki/setup/update_sv_exam_templates.py` | Creates B737_SV_MCQ / B737_SV_TF note types |
| `tools/anki/sync/set_stage.py` | Activate/deactivate Core decks by study stage; seat filter; override tags |
| `tools/anki/sync/set_flow_detail.py` | Retired — superseded by set_stage.py override tags |
| `domains/b737/anki/notes/triggers_and_flows/*-bookends.md` | Flow bookend notes (first/last action; always_show) |

---

## Retired References

**set_flow_detail.py** — superseded by `set_stage.py` override tags (`always_show` / `always_hide`). Kept for reference but should not be used.
