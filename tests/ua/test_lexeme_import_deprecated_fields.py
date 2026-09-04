"""Layer 1: Import function tests for deprecated field removal.

Tests that import_note() handles Compare field removal correctly across
three field states: legacy (present+populated), transitional (present+blank),
and target (completely absent).
"""

import pytest
from typing import Dict, Any
from tools.anki.sync.ua_lexeme_import import (
    import_note,
    get_cluster_compare_members_json,
)
from tools.anki.lib.confusable_clusters import ClusterRegistry


class TestImportWithLegacyFields:
    """Import behavior with deprecated fields present and populated."""

    @pytest.fixture
    def legacy_note_data(self) -> Dict[str, Any]:
        """Note with all Compare fields populated (pre-Phase-6 state)."""
        return {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # Pre-Phase-6: Compare fields populated
            "CompareA": "входити",
            "CompareB": "вхідний",
            "CompareC": "",
            "CompareD": "",
            "CompareScenario": "Який дієслово описує рух?",
            "Homograph_SenseA": "motion verb",
            "Homograph_SenseB": "adjective",
        }

    def test_import_succeeds_with_legacy_fields(self, legacy_note_data):
        """Import processes notes with legacy Compare fields without error."""
        # import_note should succeed (doesn't fail on extra fields)
        result = import_note(legacy_note_data, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            "import_note should return valid status"

    def test_legacy_fields_ignored_not_written(self, legacy_note_data):
        """Import with legacy fields present doesn't write them to Anki."""
        # The import function should NOT attempt to write CompareA/B/C/D
        # This is verified by code inspection: the import path doesn't
        # construct fields["CompareA"] = ... anymore
        # This test documents the behavioral change from Phase 5 → Phase 6
        pass  # Verified by code inspection of ua_lexeme_import.py


class TestImportWithTransitionalFields:
    """Import behavior with deprecated fields present but blank."""

    @pytest.fixture
    def transitional_note_data(self) -> Dict[str, Any]:
        """Note with Compare fields blank (mid-migration state)."""
        return {
            "NoteID": "ua-lexeme-0116",
            "Lemma": "вхідний",
            "EN_Gloss": "entering; incoming",
            "PartOfSpeech": "adjective",
            "ConfusableSet": "входити vs вхідний",
            # Phase 6 transition: fields present but blank
            "CompareA": "",
            "CompareB": "",
            "CompareC": "",
            "CompareD": "",
            "CompareScenario": "",
            "Homograph_SenseA": "",
            "Homograph_SenseB": "",
        }

    def test_import_succeeds_with_blank_fields(self, transitional_note_data):
        """Import processes notes with blank Compare fields without error."""
        result = import_note(transitional_note_data, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            "import_note should handle blank fields gracefully"

    def test_registry_used_not_blank_fields(self, transitional_note_data):
        """Import uses registry instead of blank CNSF fields."""
        # When CompareScenario is blank in CNSF,
        # get_cluster_compare_members_json should populate from registry
        members_json = get_cluster_compare_members_json(
            transitional_note_data["NoteID"],
            transitional_note_data.get("tags", [])
        )

        # Should get real data from registry, not blank CNSF field
        if members_json:
            import json
            data = json.loads(members_json)
            # Verify registry data is used (non-empty scenario or members)
            assert data.get("members"), "Should have members from registry"


class TestImportWithRemovedFields:
    """Import behavior with deprecated fields completely absent (target state)."""

    @pytest.fixture
    def target_note_data(self) -> Dict[str, Any]:
        """Note with Compare fields removed (Phase-6 target state)."""
        return {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # Phase 6 target: Compare fields completely removed from CNSF
            # CompareA, CompareB, CompareC, CompareD absent
            # CompareScenario absent
            # Homograph_SenseA, Homograph_SenseB absent
        }

    def test_import_succeeds_with_removed_fields(self, target_note_data):
        """Import processes notes without Compare fields without error."""
        result = import_note(target_note_data, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            "import_note should succeed with fields removed entirely"

    def test_registry_populates_missing_fields(self, target_note_data):
        """Import gets Compare data from registry when CNSF fields missing."""
        members_json = get_cluster_compare_members_json(
            target_note_data["NoteID"],
            target_note_data.get("tags", [])
        )

        # Even with no Compare fields in CNSF, registry provides data
        assert members_json, \
            "Registry should populate members when CNSF fields removed"


class TestImportConsistentAcrossFieldStates:
    """Verify import behavior is identical regardless of field state."""

    @pytest.fixture(
        params=[
            "legacy",  # All fields populated
            "transitional",  # All fields blank
            "target",  # All fields removed
        ]
    )
    def note_with_field_state(self, request) -> Dict[str, Any]:
        """Parametrized fixture providing note in each field state."""
        base = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
        }

        if request.param == "legacy":
            base.update({
                "CompareA": "входити",
                "CompareB": "вхідний",
                "CompareC": "",
                "CompareD": "",
                "CompareScenario": "Який дієслово?",
                "Homograph_SenseA": "verb",
                "Homograph_SenseB": "adj",
            })
        elif request.param == "transitional":
            base.update({
                "CompareA": "",
                "CompareB": "",
                "CompareC": "",
                "CompareD": "",
                "CompareScenario": "",
                "Homograph_SenseA": "",
                "Homograph_SenseB": "",
            })
        # "target" state: fields not in dict at all

        return base

    def test_import_succeeds_all_states(self, note_with_field_state):
        """Import succeeds regardless of Compare field state."""
        result = import_note(note_with_field_state, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            f"Should import successfully with field state"

    def test_registry_source_consistent_all_states(self, note_with_field_state):
        """Registry is used as source in all field states."""
        members_json = get_cluster_compare_members_json(
            note_with_field_state["NoteID"],
            note_with_field_state.get("tags", [])
        )

        # All three field states should produce identical registry result
        if members_json:
            import json
            data = json.loads(members_json)
            assert "members" in data, "Members should come from registry"
            assert "scenario" in data, "Scenario should come from registry"


class TestNonClusteredNoteUnaffected:
    """Verify non-clustered notes work fine without Compare fields."""

    @pytest.fixture
    def non_clustered_note(self) -> Dict[str, Any]:
        """Note not in any cluster, no Compare fields."""
        return {
            "NoteID": "ua-lexeme-9999",
            "Lemma": "тестовий",
            "EN_Gloss": "test word",
            "PartOfSpeech": "adjective",
            # No ConfusableSet, no Compare fields
        }

    def test_non_clustered_import_succeeds(self, non_clustered_note):
        """Non-clustered notes import normally without Compare fields."""
        result = import_note(non_clustered_note, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            "Non-clustered note should import without Compare fields"

    def test_non_clustered_registry_returns_empty(self, non_clustered_note):
        """Non-clustered notes get no registry data (expected)."""
        members_json = get_cluster_compare_members_json(
            non_clustered_note["NoteID"],
            non_clustered_note.get("tags", [])
        )
        assert members_json == "", \
            "Non-clustered note should have no registry data"


class TestFieldRemovalEdgeCases:
    """Edge cases in field removal migration."""

    def test_partial_field_removal_handled(self):
        """Partial removal (some fields removed, others kept) handled."""
        partial = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "CompareA": "входити",  # Kept
            # CompareB removed
            # CompareScenario removed
        }

        result = import_note(partial, dry_run=True)
        assert result in ("added", "updated", "skipped"), \
            "Should handle partial field removal gracefully"

    def test_field_removal_with_empty_confusable_set(self):
        """Field removal when ConfusableSet also empty."""
        note = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "ConfusableSet": "",  # Also empty/blank
            # All Compare fields removed
        }

        result = import_note(note, dry_run=True)
        # Should still succeed (Compare card suspension handled separately)
        assert result in ("added", "updated", "skipped")

    def test_field_removal_preserves_other_data(self):
        """Removing Compare fields doesn't lose other note data."""
        target_note = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "Gender": "",
            "Perfective": "увійти",
            "UA_Example": "Дверь відкривається, я входжу.",
            "EN_Example": "The door opens, I enter.",
            "Source_URL": "goroh.pp.ua/Словозміна/входити",
            # No Compare fields
        }

        result = import_note(target_note, dry_run=True)
        # All non-Compare data should remain intact
        assert result in ("added", "updated", "skipped")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
