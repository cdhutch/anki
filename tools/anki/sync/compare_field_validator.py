"""
Validation for Compare field consistency with referenced cluster members.

Option C validation: CompareA-D values must exist as Lemma fields in ConfusableSet-referenced notes.
"""

import re
from typing import Dict, Tuple, List


def extract_note_ids_from_confusable(confusable_set_text):
    """Extract all note IDs from ConfusableSet text."""
    if not confusable_set_text:
        return []
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