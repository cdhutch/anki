# Anki Migration Log — B737 SV Exam Cards

**Status**: Paused mid-execution (2026-05-25)

## Phase A: Distractor Authoring

All 29 SV systems converted to `systems_verification_exam_draft` MCQ format.

**Remaining queue** (3 systems, all status:draft):
- engines: 41 total, 39 draft
- autoflight: 42 total, 39 draft
- pneumatics: 39 total, 39 draft

**Completed** (all status:verified): acars, adverse, air_conditioning, apu, atc_tcas_trans, communications, electrical, emergency_equipment, fire_protection, flight_controls, flight_instrumentation, flight_warning, fuel, general, gpws, hud, hydraulics, ice_and_rain_protection, landing_gear, lighting, navigation, oxygen, performance, pressurization, weather_radar

**Partially complete**: fms (sv-fms-024 intentional 2-choice; all others verified)

Note: `status:draft` imports as suspended; `status:verified` imports as active.

## Phase B: Anki Migration Steps

✅ Step 1: Create note types (COMPLETED)
- `B737_SV_MCQ` fields: NoteID, Text, Source Document, OriginalNoteID, Choice1–4, CorrectChoice
- `B737_SV_TF` fields: NoteID, Text, Source Document, OriginalNoteID, CorrectAnswer
- Script: `tools/anki/setup/update_sv_exam_templates.py`

✅ Step 2: Create "B737 SV Exam" preset (COMPLETED)
- Script: `tools/anki/setup/create_sv_exam_preset.py`
- Settings: 100 new/day · 9999 reviews/day · FSRS on · 90% desired retention

⏳ Step 3: Delete legacy cloze notes (PENDING)
```bash
python tools/anki/setup/delete_sv_cloze.py --dry-run
python tools/anki/setup/delete_sv_cloze.py
```

✅ Step 4: Import new MCQ cards (COMPLETED)
- Command: `make sve`
- All systems imported; draft cards suspended; verified cards active

✅ Step 5: Verify in Anki (COMPLETED)
- `note:B737_SV_MCQ` confirmed in Anki
- "B737 SV Exam" preset applied to MCQ and TF decks

## Resolved Flags

| File | Issue | Resolution |
|---|---|---|
| `hydraulics/sv-hydraulics-037.md` | Blank source answer | Filled: 3000 psi |
| `autoflight/sv-autoflight-17.md` | "10 degrees nose down" — correct? | Confirmed correct (first ~90 kts of takeoff roll) |
