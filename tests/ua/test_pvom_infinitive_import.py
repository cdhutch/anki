"""
tests/ua/test_pvom_infinitive_import.py

Unit tests for tools/anki/sync/ua_pvom_infinitive_import.py's anki_fields_from
(the CNSF fields dict -> Anki field mapping). Everything else in this module
talks to AnkiConnect directly and isn't practically unit-testable without a
live Anki instance -- this is the one piece of pure decision logic worth
covering, and it's exactly the kind of function where a field added to
ANKI_FIELDS without the surrounding CNSF data (or vice versa) silently drops
data instead of erroring. Added 2026-07-25 alongside the *_Euphony fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.sync.ua_pvom_infinitive_import import ANKI_FIELDS, anki_fields_from  # noqa: E402

EUPHONY_BASES = ("Walking_Multi", "Walking_Uni", "Vehicle_Multi", "Vehicle_Uni")


class TestAnkiFieldsFrom:
    def test_all_anki_fields_present_in_output(self):
        fields = anki_fields_from({"NoteID": "ua-pvom-0012", "Prefix": "в"})
        assert set(fields.keys()) == set(ANKI_FIELDS)

    def test_missing_field_defaults_to_empty_string(self):
        fields = anki_fields_from({"NoteID": "ua-pvom-0012"})
        assert fields["Vehicle_Multi_Euphony"] == ""

    def test_populated_euphony_field_passes_through(self):
        fields = anki_fields_from({
            "NoteID": "ua-pvom-0012",
            "Vehicle_Multi_Euphony": "уїжджати",
            "Vehicle_Uni_Euphony": "уїхати",
        })
        assert fields["Vehicle_Multi_Euphony"] == "уїжджати"
        assert fields["Vehicle_Uni_Euphony"] == "уїхати"

    def test_unknown_field_silently_dropped(self):
        # Documents existing behavior (anki_fields_from only looks up names
        # listed in ANKI_FIELDS) rather than asserting it's ideal -- a typo'd
        # CNSF field name currently fails silently, not loudly.
        fields = anki_fields_from({"NotARealField": "x"})
        assert "NotARealField" not in fields


class TestEuphonyFieldCoverage:
    def test_every_base_form_has_a_euphony_field(self):
        # Regression guard: *_Euphony was added per-base-form (2026-07-25),
        # mirroring the existing *_UA/*_Typing pattern. If a future base form
        # is added to this note type without its *_Euphony counterpart, this
        # should fail rather than silently shipping an inconsistent schema.
        for base in EUPHONY_BASES:
            assert f"{base}_Euphony" in ANKI_FIELDS, f"missing {base}_Euphony"

    def test_every_euphony_field_has_a_stress_and_typing_sibling(self):
        for base in EUPHONY_BASES:
            assert f"{base}_UA" in ANKI_FIELDS
            assert f"{base}_Typing" in ANKI_FIELDS
