"""
tests/ua/test_pvom_infinitive_import.py

Unit tests for tools/anki/sync/ua_pvom_infinitive_import.py's anki_fields_from
(the CNSF fields dict -> Anki field mapping) and should_suspend (the
suspension policy). Everything else in this module
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

from tools.anki.sync.ua_pvom_infinitive_import import (  # noqa: E402
    ANKI_FIELDS,
    anki_fields_from,
    should_suspend,
)

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


class TestShouldSuspend:
    """Two independent suspend axes: status:draft and conj:suspended.

    Per Option A refactoring (2026-08-25), stress:unverified is decoupled from
    suspension logic. It is tracked as documentation but does not trigger
    suspension.

    conj:suspended was added 2026-08-19 as a third independent axis, but
    stress:unverified is no longer one. Before it, curation had no lever on
    this note type: holding a note out of the drilling rotation meant tagging
    it status:draft, which asserts "unreviewed" and pulls a verified note back
    into list_unverified.py's report. These tests pin the separation so a
    future simplification can't quietly re-merge the axes.
    """

    def test_verified_no_flags_unsuspends(self):
        assert should_suspend(["domain:ua", "status:verified"]) is False

    def test_status_draft_suspends(self):
        assert should_suspend(["domain:ua", "status:draft"]) is True

    def test_stress_unverified_does_not_suspend(self):
        # Option A: stress:unverified is for documentation, not suspension.
        assert should_suspend(["stress:unverified"]) is False

    def test_conj_suspended_suspends(self):
        assert should_suspend(["domain:ua", "status:verified", "conj:suspended"]) is True

    def test_conj_suspended_wins_over_full_verification(self):
        # The whole point of the axis: a note can be correct on both quality
        # axes and still be reference-only. This is the state of the nine
        # non-selected prefixes as of 2026-08-19.
        assert should_suspend(
            ["domain:ua", "stress:verified", "status:verified", "conj:suspended"]
        ) is True

    def test_conj_drill_does_not_suspend(self):
        # The four Craig keeps active (при-, в/у-, ви-, під-) carry conj:drill,
        # which must not be confused for conj:suspended by a substring check.
        assert should_suspend(
            ["domain:ua", "stress:verified", "status:verified", "conj:drill"]
        ) is False

    def test_status_verified_and_stress_unverified_does_not_suspend(self):
        # Option A: stress:unverified does not suspend even alongside status:verified.
        assert should_suspend(["status:verified", "stress:unverified"]) is False

    def test_no_tags_unsuspends(self):
        assert should_suspend([]) is False

    def test_multiple_suspend_reasons_still_suspends(self):
        # status:draft alone suspends; stress:unverified no longer does (Option A).
        assert should_suspend(
            ["status:draft", "stress:unverified", "conj:suspended"]
        ) is True
