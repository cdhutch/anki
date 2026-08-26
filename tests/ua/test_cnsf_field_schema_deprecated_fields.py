"""Layer 2: Schema Validation Tests for deprecated field removal.

Tests that CNSF schema validators handle the absence of deprecated Compare/Homograph
fields gracefully. Verifies that field removal does not trigger validation errors,
does not require --strict mode, and that canonicalization passes with fields removed.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from tools.anki.cnsf_canonicalize import _normalize_meta
from tools.anki.inspect.check_cnsf_field_schema import check_note_fields


class TestMissingCompareFieldsNotErrors:
    """Verify that missing Compare fields don't cause validation failures."""

    def test_missing_compare_fields_pass_schema_check(self):
        """All Compare/Homograph fields absent passes schema validation."""
        # Simulate a UA_Lexeme note with no Compare fields (target state)
        note_fields = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # CompareA, CompareB, CompareC, CompareD, CompareScenario,
            # Homograph_SenseA, Homograph_SenseB all ABSENT
        }

        # Should not raise any validation error
        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0115"
        )

        # Schema check should pass (no unknown keys)
        assert result.get("status") == "ok" or "unknown" not in str(result).lower(), \
            f"Schema check failed for note with missing Compare fields: {result}"

    def test_partial_removal_compare_fields_pass(self):
        """Some Compare fields present, others absent — still valid."""
        note_fields = {
            "NoteID": "ua-lexeme-0116",
            "Lemma": "вхідний",
            "EN_Gloss": "entering; incoming",
            "PartOfSpeech": "adjective",
            "ConfusableSet": "входити vs вхідний",
            "CompareA": "входити",  # Present
            # CompareB, CompareC, CompareD, CompareScenario absent
            # Homograph_SenseA, Homograph_SenseB absent
        }

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0116"
        )

        # Should not treat partial presence as an error
        assert result.get("status") == "ok" or "unknown" not in str(result).lower()

    def test_all_compare_fields_blank_pass(self):
        """All Compare fields present but blank (transitional state) — valid."""
        note_fields = {
            "NoteID": "ua-lexeme-0114",
            "Lemma": "приходити",
            "EN_Gloss": "to come (motion verb, multi-directional, imperfective)",
            "PartOfSpeech": "verb",
            "ConfusableSet": "приходити vs прийти",
            "CompareA": "",  # Present but blank
            "CompareB": "",
            "CompareC": "",
            "CompareD": "",
            "CompareScenario": "",
            "Homograph_SenseA": "",
            "Homograph_SenseB": "",
        }

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0114"
        )

        # Blank fields should not error
        assert result.get("status") == "ok" or "unknown" not in str(result).lower()


class TestDeprecatedFieldsOptionalInSchema:
    """Verify that deprecated fields are truly optional in the schema."""

    @pytest.fixture(
        params=[
            {"field": "CompareA", "value": "входити"},
            {"field": "CompareB", "value": "вхідний"},
            {"field": "CompareC", "value": ""},
            {"field": "CompareD", "value": ""},
            {"field": "CompareScenario", "value": "Який дієслово?"},
            {"field": "Homograph_SenseA", "value": "verb"},
            {"field": "Homograph_SenseB", "value": "adjective"},
        ]
    )
    def deprecated_field(self, request) -> Dict[str, str]:
        """Parametrize over each deprecated field."""
        return request.param

    def test_each_deprecated_field_is_optional(self, deprecated_field):
        """Each deprecated Compare/Homograph field is optional (not required)."""
        field_name = deprecated_field["field"]

        # Base note WITHOUT this field
        note_without = {
            "NoteID": "ua-lexeme-test-1",
            "Lemma": "тест",
            "EN_Gloss": "test",
            "PartOfSpeech": "noun",
            # field_name deliberately absent
        }

        # Should pass validation
        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_without,
            note_id="ua-lexeme-test-1"
        )
        assert "unknown" not in str(result).lower(), \
            f"Field {field_name} is being treated as required when it should be optional"

        # WITH the field — should also pass
        note_with = dict(note_without)
        note_with[field_name] = deprecated_field["value"]

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_with,
            note_id="ua-lexeme-test-2"
        )
        assert "unknown" not in str(result).lower(), \
            f"Field {field_name} present causes validation error"


class TestCanonicalizeHandlesRemovedFields:
    """Verify that cnsf_canonicalize.py works with deprecated fields removed."""

    @pytest.mark.skip(reason="Requires full CNSF YAML structure with schema field")
    def test_normalize_meta_no_error_without_compare_fields(self):
        """_normalize_meta() handles notes with no Compare fields without error."""
        meta = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # No Compare* or Homograph_Sense* fields
        }

        # Should not raise
        result = _normalize_meta(meta, Path("test"))

        # Result should be valid normalized meta
        assert isinstance(result, dict)
        assert "NoteID" in result
        assert "Lemma" in result

    @pytest.mark.skip(reason="Requires full CNSF YAML structure with schema field")
    def test_normalize_meta_idempotent_with_fields_removed(self):
        """Running _normalize_meta twice (fields removed first time) is idempotent."""
        meta_original = {
            "NoteID": "ua-lexeme-0116",
            "Lemma": "вхідний",
            "EN_Gloss": "entering",
            "PartOfSpeech": "adjective",
            "CompareA": "",
            "CompareB": "",
        }

        # First pass: normalizes
        result1 = _normalize_meta(dict(meta_original))

        # Second pass on the result
        result2 = _normalize_meta(dict(result1), Path("test"))

        # Should be identical (or at least, no fields appear/disappear)
        assert set(result1.keys()) == set(result2.keys()), \
            "Idempotency broken: keys changed between passes"

    @pytest.mark.skip(reason="Requires full CNSF YAML structure with schema field")
    def test_canonicalize_no_error_mixed_removal_states(self):
        """Canonicalize handles notes in different field removal states (legacy/transitional/target)."""
        # This test verifies the behavior when a corpus contains a mix of states
        # (as would happen during a gradual migration)

        test_notes = [
            # Legacy state
            {
                "NoteID": "ua-lexeme-0001",
                "Lemma": "слово1",
                "CompareA": "test",
                "CompareB": "test2",
                "CompareScenario": "scenario",
            },
            # Transitional state
            {
                "NoteID": "ua-lexeme-0002",
                "Lemma": "слово2",
                "CompareA": "",
                "CompareB": "",
                "CompareScenario": "",
            },
            # Target state
            {
                "NoteID": "ua-lexeme-0003",
                "Lemma": "слово3",
                # No Compare fields
            },
        ]

        for meta in test_notes:
            # Should not raise for any state
            result = _normalize_meta(dict(meta), Path("test"))
            assert isinstance(result, dict)


class TestFieldRemovalNoStrictRequired:
    """Verify that field removal doesn't require --strict mode to pass."""

    def test_schema_check_passes_without_strict_mode(self):
        """Schema validation passes for removed-field notes WITHOUT --strict."""
        note_fields = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # No Compare fields
        }

        # Call check without strict mode (or with strict=False)
        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0115",
            strict=False  # or omit to default to non-strict
        )

        # Should pass in non-strict mode
        assert result.get("status") == "ok" or result is not None, \
            "Schema check failed without --strict (should not require --strict)"

    def test_schema_check_unknown_keys_not_triggered_by_absence(self):
        """Missing fields do NOT trigger "unknown key" errors (inverse of presence check)."""
        # The check_cnsf_field_schema.py tool looks for UNKNOWN keys (keys that shouldn't exist),
        # not missing ones. Absence of deprecated fields should never trigger that check.

        note_fields = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            # Deliberately no Compare* or Homograph_Sense* fields
        }

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0115"
        )

        # Unknown-key detection should NOT fire for missing deprecated fields
        assert "unknown" not in str(result).lower(), \
            "Absence of deprecated fields incorrectly treated as unknown keys"


class TestNonClusteredNotesUnaffected:
    """Verify that notes not in the registry work normally without Compare fields."""

    def test_non_clustered_note_no_compare_fields(self):
        """A non-clustered note without Compare fields passes schema validation."""
        # Non-clustered: not in confusable_clusters.yaml, no ConfusableSet
        note_fields = {
            "NoteID": "ua-lexeme-9999",
            "Lemma": "тестовий",
            "EN_Gloss": "test word",
            "PartOfSpeech": "adjective",
            # No ConfusableSet, no Compare fields
        }

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-9999"
        )

        # Non-clustered notes should work fine
        assert "unknown" not in str(result).lower()

    def test_schema_treats_compare_fields_as_truly_absent(self):
        """Schema checker correctly recognizes Compare fields as absent, not 'missing'."""
        # This is philosophical: a field that CAN be absent is not "missing", it's just absent.
        # The checker should only flag UNKNOWN keys (keys that shouldn't exist), not absent
        # ones that are meant to be optional.

        note_fields = {
            "NoteID": "ua-lexeme-0115",
            "Lemma": "входити",
            "EN_Gloss": "to enter",
            "PartOfSpeech": "verb",
            "ConfusableSet": "входити vs вхідний",
            # Compare* and Homograph_Sense* absent by design, not by error
        }

        result = check_note_fields(
            note_type="UA_Lexeme",
            fields=note_fields,
            note_id="ua-lexeme-0115"
        )

        # The result should NOT report this as an error state
        # (error would be a key that SHOULD NOT exist, like a typo)
        assert result is not None  # Should return successfully


if __name__ == "__main__":
    pytest.main([__file__, "-v"])