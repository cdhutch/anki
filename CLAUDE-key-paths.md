# Key Paths Reference

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
| `domains/b737/anki/notes/triggers_and_flows/*-bookends.md` | Flow bookend notes (first/last action; always_show) |
