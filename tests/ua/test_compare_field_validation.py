"""
Unit tests for Compare field validation (Option C).

Tests:
1. Validation bypassed for pending-confusable tagged notes
2. Validation skipped for old-format ConfusableSet (bare lemmas only)
3. Validation checks each CompareA-D against referenced Lemma values
4. Error reporting with note ID descriptions
5. New-format ConfusableSet detection (note ID pattern)
"""

import pytest
from typing import Dict, Tuple, List


def extract_note_ids_from_confusable(confusable_set_text):
    """Extract all note IDs from ConfusableSet text."""
    if not confusable_set_text:
        return []
    import re
    note_id_pattern = r'ua-lexeme-\d+'
    return re.findall(note_id_pattern, confusable_set_text)


def get_referenced_lemmas(note_ids: List[str], all_notes_by_id: Dict) -> set:
    """
    Get all Lemma values from referenced notes.

    Args:
        note_ids: List of note IDs to look up
        all_notes_by_id: Dict mapping note_id → note_data

    Returns:
        Set of Lemma strings from referenced notes
    """
    lemmas = set()
    for note_id in note_ids:
        if note_id in all_notes_by_id:
            note_data = all_notes_by_id[note_id]
            lemma = note_data.get('fields', {}).get('Lemma', '').strip()
            if lemma:
                lemmas.add(lemma)
    return lemmas


def validate_compare_fields(
    note_id: str,
    note_data: Dict,
    all_notes_by_id: Dict
) -> Tuple[bool, List[str]]:
    """
    Validate Compare fields against referenced notes.

    Args:
        note_id: The note ID being validated
        note_data: The note's data (fields, tags, etc.)
        all_notes_by_id: Dict mapping all note IDs → note data

    Returns:
        (is_valid, error_messages)
        - is_valid: True if validation passed
        - error_messages: List of error messages if validation failed

    Behavior:
        - Skips validation for notes tagged pending-confusable:*
        - Requires new-format ConfusableSet (contains note IDs)
        - If ConfusableSet is empty or old-format only, skips validation
        - For new-format, validates each CompareA-D against referenced lemmas
    """
    errors = []

    # Check if note is pending-confusable tagged
    tags = note_data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]

    is_pending = any(t.startswith('pending-confusable:') for t in tags)
    if is_pending:
        return True, []  # Skip validation for pending-confusable notes

    # Get ConfusableSet
    confusable_set = note_data.get('fields', {}).get('ConfusableSet', '').strip()
    if not confusable_set:
        return True, []  # No ConfusableSet, nothing to validate

    # Extract referenced note IDs (new format)
    referenced_ids = extract_note_ids_from_confusable(confusable_set)
    if not referenced_ids:
        # Old format only (bare lemmas) — skip for now, will be migrated
        return True, []

    # Get referenced lemmas
    referenced_lemmas = get_referenced_lemmas(referenced_ids, all_notes_by_id)
    if not referenced_lemmas:
        errors.append(f"ConfusableSet references note IDs {referenced_ids} but none exist in corpus")
        return False, errors

    # Validate each Compare field
    compare_fields = ['CompareA', 'CompareB', 'CompareC', 'CompareD']
    for field_name in compare_fields:
        field_value = note_data.get('fields', {}).get(field_name, '').strip()
        if not field_value:
            # Empty is ok for optional fields (CompareC/D)
            continue

        if field_value not in referenced_lemmas:
            errors.append(
                f"{field_name}='{field_value}' not found in referenced Lemma values: "
                f"{', '.join(sorted(referenced_lemmas))}"
            )

    return len(errors) == 0, errors


def describe_note_ids(note_ids: List[str], all_notes_by_id: Dict) -> str:
    """
    Convert note IDs to readable descriptions for error messages.

    Returns string like: "ua-lexeme-0100 (непога́но), ua-lexeme-0101 (норма́льно)"
    """
    descriptions = []
    for note_id in sorted(note_ids):
        if note_id in all_notes_by_id:
            lemma = all_notes_by_id[note_id].get('fields', {}).get('Lemma', 'unknown')
            descriptions.append(f"{note_id} ({lemma})")
        else:
            descriptions.append(note_id)
    return ', '.join(descriptions)


class TestPendingConfusableBypass:
    """Test that pending-confusable tagged notes skip validation."""

    def test_pending_confusable_bypasses_validation(self):
        """
        Notes tagged pending-confusable:* skip validation entirely.

        This allows forward references to cluster members not yet created.
        """
        # A note with ConfusableSet populated but pending reference
        note_data = {
            'fields': {
                'Lemma': 'рух',
                'ConfusableSet': 'ua-lexeme-0464'  # затор doesn't exist yet
            },
            'tags': ['pending-confusable:затор']
        }

        all_notes_by_id = {}  # затор doesn't exist

        is_valid, errors = validate_compare_fields('ua-lexeme-0463', note_data, all_notes_by_id)

        # Validation skipped, no errors
        assert is_valid is True
        assert errors == []

    def test_non_pending_requires_validation(self):
        """
        Non-pending notes with ConfusableSet require validation.
        """
        note_data = {
            'fields': {
                'Lemma': 'слово1',
                'ConfusableSet': 'ua-lexeme-0200',
                'CompareA': 'invalid_value'  # Not in referenced lemmas
            },
            'tags': []  # Not pending
        }

        all_notes_by_id = {
            'ua-lexeme-0200': {
                'fields': {
                    'Lemma': 'слово2'
                }
            }
        }

        is_valid, errors = validate_compare_fields('ua-lexeme-0199', note_data, all_notes_by_id)

        # Validation runs, finds error
        assert is_valid is False
        assert len(errors) > 0
        assert 'invalid_value' in errors[0]


class TestOldFormatSkipping:
    """Test that old-format ConfusableSet (bare lemmas only) skips validation."""

    def test_bare_lemma_only_skips_validation(self):
        """
        ConfusableSet with only bare lemmas (no note IDs) skips validation.

        This allows old-format notes to coexist during migration.
        """
        note_data = {
            'fields': {
                'Lemma': 'добре́',
                'ConfusableSet': 'непога́но, нормально́, чудово́'  # Bare lemmas, no IDs
            },
            'tags': []
        }

        all_notes_by_id = {}

        is_valid, errors = validate_compare_fields('ua-lexeme-0099', note_data, all_notes_by_id)

        # Old format, validation skipped
        assert is_valid is True
        assert errors == []

    def test_new_format_detection(self):
        """
        ConfusableSet with note IDs triggers validation.
        """
        note_data = {
            'fields': {
                'Lemma': 'добре́',
                'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101'  # New format with IDs
            },
            'tags': []
        }

        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}},
            'ua-lexeme-0101': {'fields': {'Lemma': 'норма́льно'}}
        }

        # Should detect new format and attempt validation
        is_valid, errors = validate_compare_fields('ua-lexeme-0099', note_data, all_notes_by_id)

        # No Compare fields provided, but validation ran (new format detected)
        # Validation passes because Compare fields are optional for unaudited clusters
        assert is_valid is True


class TestCompareFieldValidation:
    """Test Compare field validation against referenced Lemma values."""

    def test_valid_compare_a_b(self):
        """
        CompareA and CompareB match referenced Lemma values.
        """
        note_data = {
            'fields': {
                'Lemma': 'добре́',
                'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101',
                'CompareA': 'добре́',
                'CompareB': 'непога́но'
            },
            'tags': []
        }

        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}},
            'ua-lexeme-0101': {'fields': {'Lemma': 'норма́льно'}}
        }

        is_valid, errors = validate_compare_fields('ua-lexeme-0099', note_data, all_notes_by_id)

        assert is_valid is True
        assert errors == []

    def test_invalid_compare_a(self):
        """
        CompareA value not in referenced Lemma values.
        """
        note_data = {
            'fields': {
                'Lemma': 'добре́',
                'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101',
                'CompareA': 'invalid_word'
            },
            'tags': []
        }

        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}},
            'ua-lexeme-0101': {'fields': {'Lemma': 'норма́льно'}}
        }

        is_valid, errors = validate_compare_fields('ua-lexeme-0099', note_data, all_notes_by_id)

        assert is_valid is False
        assert len(errors) == 1
        assert 'CompareA' in errors[0]
        assert 'invalid_word' in errors[0]

    def test_optional_compare_c_d(self):
        """
        CompareC and CompareD are optional.

        A 3-item cluster with CompareA/B but not CompareC is valid.
        A 4-item cluster with CompareA/B but not CompareC/D is valid (optional fields).
        """
        note_data = {
            'fields': {
                'Lemma': 'добре́',
                'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101, ua-lexeme-0102',
                'CompareA': 'добре́',
                'CompareB': 'непога́но',
                'CompareC': '',  # Empty is ok
                'CompareD': ''   # Empty is ok
            },
            'tags': []
        }

        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}},
            'ua-lexeme-0101': {'fields': {'Lemma': 'норма́льно'}},
            'ua-lexeme-0102': {'fields': {'Lemma': 'чудово́'}}
        }

        is_valid, errors = validate_compare_fields('ua-lexeme-0099', note_data, all_notes_by_id)

        assert is_valid is True
        assert errors == []

    def test_missing_referenced_notes(self):
        """
        ConfusableSet references note IDs that don't exist.
        """
        note_data = {
            'fields': {
                'Lemma': 'слово1',
                'ConfusableSet': 'ua-lexeme-9999, ua-lexeme-8888'  # Don't exist
            },
            'tags': []
        }

        all_notes_by_id = {}  # Empty corpus

        is_valid, errors = validate_compare_fields('ua-lexeme-0001', note_data, all_notes_by_id)

        assert is_valid is False
        assert 'does not exist in corpus' in errors[0]


class TestErrorReporting:
    """Test error message generation and note ID descriptions."""

    def test_describe_note_ids_with_lemmas(self):
        """
        Convert note IDs to readable descriptions with lemmas.
        """
        note_ids = ['ua-lexeme-0100', 'ua-lexeme-0101']
        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}},
            'ua-lexeme-0101': {'fields': {'Lemma': 'норма́льно'}}
        }

        description = describe_note_ids(note_ids, all_notes_by_id)

        assert 'ua-lexeme-0100' in description
        assert 'непога́но' in description
        assert 'ua-lexeme-0101' in description
        assert 'норма́льно' in description

    def test_describe_note_ids_with_missing_lemmas(self):
        """
        Handle missing Lemma gracefully in descriptions.
        """
        note_ids = ['ua-lexeme-0100', 'ua-lexeme-0999']
        all_notes_by_id = {
            'ua-lexeme-0100': {'fields': {'Lemma': 'непога́но'}}
            # ua-lexeme-0999 missing
        }

        description = describe_note_ids(note_ids, all_notes_by_id)

        assert 'ua-lexeme-0100' in description
        assert 'непога́но' in description
        assert 'ua-lexeme-0999' in description


class TestValidationIntegration:
    """Integration tests for full validation workflow."""

    def test_добре_cluster_validation(self):
        """
        Integration test: validate all four notes in добре́/непога́но/норма́льно/чудово́ cluster.

        Each note's CompareA-D values must exist as Lemma in the other notes.
        """
        cluster_notes = {
            'ua-lexeme-0099': {
                'fields': {
                    'Lemma': 'добре́',
                    'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101, ua-lexeme-0104',
                    'CompareA': 'добре́',
                    'CompareB': 'непога́но',
                    'CompareC': 'норма́льно',
                    'CompareD': 'чудово́'
                },
                'tags': []
            },
            'ua-lexeme-0100': {
                'fields': {
                    'Lemma': 'непога́но',
                    'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0101, ua-lexeme-0104',
                    'CompareA': 'непога́но',
                    'CompareB': 'добре́',
                    'CompareC': 'норма́льно',
                    'CompareD': 'чудово́'
                },
                'tags': []
            },
            'ua-lexeme-0101': {
                'fields': {
                    'Lemma': 'норма́льно',
                    'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0104',
                    'CompareA': 'норма́льно',
                    'CompareB': 'добре́',
                    'CompareC': 'непога́но',
                    'CompareD': 'чудово́'
                },
                'tags': []
            },
            'ua-lexeme-0104': {
                'fields': {
                    'Lemma': 'чудово́',
                    'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0101',
                    'CompareA': 'чудово́',
                    'CompareB': 'добре́',
                    'CompareC': 'непога́но',
                    'CompareD': 'норма́льно'
                },
                'tags': []
            }
        }

        # Validate each note
        for note_id, note_data in cluster_notes.items():
            is_valid, errors = validate_compare_fields(note_id, note_data, cluster_notes)
            assert is_valid is True, f"{note_id} validation failed: {errors}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])