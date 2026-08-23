#!/usr/bin/env python3
"""Generic domain-aware CNSF importer for multi-language Anki sync.

Imports CNSF notes from test directories into Anki via AnkiConnect.
Works for any domain (UA, CS, DE, SK, IPA) and any note type defined in
the domain config.

Usage:
    python tools/anki/import/generic_domain_import.py \\
        --domain cs --note-type cs_lexeme --deck "CS::Test"

    python tools/anki/import/generic_domain_import.py \\
        --domain sk --note-type sk_alphabet --deck "SK::Test"

    python tools/anki/import/generic_domain_import.py \\
        --domain ipa --note-type ipa_phoneme --deck "IPA::Test"

Reads CNSF files from domains/{domain}/anki/notes/{category}/test/*.md
where category is derived from the note type (e.g., cs_lexeme -> lexemes).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.lib.domain_config import DomainConfig  # noqa: E402
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
DOMAINS_DIR = Path(__file__).resolve().parents[1] / "config" / "domains"
NOTES_DIR = Path(__file__).resolve().parents[3] / "domains"

# Mapping from note type to directory category
NOTE_TYPE_CATEGORIES = {
    "cs_lexeme": "lexemes",
    "cs_alphabet": "alphabet",
    "de_lexeme": "lexemes",
    "sk_lexeme": "lexemes",
    "sk_alphabet": "alphabet",
    "ipa_phoneme": "phonemes",
}


def get_category_for_note_type(note_type: str) -> str:
    """Return the directory category for a note type (e.g., cs_lexeme -> lexemes)."""
    if note_type in NOTE_TYPE_CATEGORIES:
        return NOTE_TYPE_CATEGORIES[note_type]
    # Fallback: extract category from note type suffix
    suffix = note_type.split("_", 1)[1] if "_" in note_type else note_type
    if suffix == "phoneme":
        return "phonemes"
    elif suffix in ("alphabet", "alphabets"):
        return "alphabet"
    else:
        return suffix + "s"  # Pluralize


def find_test_cnsf_files(domain: str, category: str) -> List[Path]:
    """Find all test CNSF files for a domain/category."""
    test_dir = NOTES_DIR / domain / "anki" / "notes" / category / "test"
    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return []

    files = sorted(test_dir.glob("*.md"))
    print(f"Found {len(files)} test file(s) in {test_dir.name}/")
    return files


def parse_cnsf_file(path: Path) -> Dict[str, Any] | None:
    """Parse a CNSF file (YAML frontmatter + optional markdown body)."""
    content = path.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    if not content.startswith("---"):
        print(f"  WARNING: {path.name} does not start with ---")
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"  WARNING: {path.name} missing closing ---")
        return None

    try:
        yaml_content = yaml.safe_load(parts[1])
        if not isinstance(yaml_content, dict):
            print(f"  WARNING: {path.name} YAML is not a dict")
            return None
        return yaml_content
    except yaml.YAMLError as e:
        print(f"  WARNING: {path.name} YAML parse error: {e}")
        return None


def build_anki_note(cnsf_data: Dict[str, Any], model_name: str, fields_list: List[str]) -> Dict[str, Any]:
    """Build an Anki note from CNSF data.

    Maps CNSF fields dict to Anki's ordered field list.
    """
    cnsf_fields = cnsf_data.get("fields", {})

    # Build Anki note with fields in canonical order
    anki_fields = {}
    for field_name in fields_list:
        anki_fields[field_name] = cnsf_fields.get(field_name, "")

    return {
        "modelName": model_name,
        "fields": anki_fields,
        "tags": cnsf_data.get("tags", []),
    }


def sync_notes_to_anki(
    domain: str,
    note_type: str,
    model_name: str,
    deck_name: str,
    cnsf_files: List[Path],
    config: DomainConfig,
) -> None:
    """Sync CNSF test notes to Anki via AnkiConnect."""
    nt_config = config.note_types.get(note_type)
    if not nt_config:
        print(f"ERROR: Note type '{note_type}' not found in {domain} config")
        return

    fields_list = nt_config.fields

    # Check that model exists in Anki
    existing_models = anki_request("modelNames", url=ANKI_URL) or []
    if model_name not in existing_models:
        print(f"ERROR: Model '{model_name}' not found in Anki")
        print(f"       Available models: {existing_models}")
        return

    print(f"\nSyncing {len(cnsf_files)} note(s) to deck '{deck_name}'...")

    synced = 0
    for cnsf_path in cnsf_files:
        cnsf_data = parse_cnsf_file(cnsf_path)
        if not cnsf_data:
            continue

        anki_note = build_anki_note(cnsf_data, model_name, fields_list)
        note_id = cnsf_data.get("note_id", "")

        try:
            # Check if note already exists by NoteID
            existing_anki_id = None
            if note_id:
                print(f"  DEBUG: Looking for existing note with NoteID={note_id}")
                query = f'note:"{model_name}" NoteID:"{note_id}"'
                results = anki_request("findNotes", {"query": query}, url=ANKI_URL) or []
                if results:
                    print(f"  DEBUG: Found existing note ID {results[0]}")
                    existing_anki_id = int(results[0])

            if existing_anki_id:
                # Update existing note
                print(f"  DEBUG: Updating note {existing_anki_id} with fields: {anki_note['fields']}")
                anki_request(
                    "updateNoteFields",
                    {"note": {"id": existing_anki_id, "fields": anki_note["fields"]}},
                    url=ANKI_URL,
                )
                # Update tags if present
                if anki_note.get("tags"):
                    existing_tags = anki_request("getNoteTags", {"note": existing_anki_id}, url=ANKI_URL) or []
                    if existing_tags:
                        anki_request("removeTags", {"notes": [existing_anki_id], "tags": " ".join(existing_tags)}, url=ANKI_URL)
                    anki_request("addTags", {"notes": [existing_anki_id], "tags": " ".join(anki_note["tags"])}, url=ANKI_URL)
            else:
                # Create new note
                anki_request(
                    "addNote",
                    {
                        "note": {
                            **anki_note,
                            "deckName": deck_name,
                            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
                        }
                    },
                    url=ANKI_URL,
                )
            print(f"  ✓ {cnsf_path.name}")
            synced += 1
        except Exception as e:
            print(f"  ✗ {cnsf_path.name}: {e}")

    print(f"\nSynced {synced}/{len(cnsf_files)} note(s).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True, choices=["cs", "de", "sk", "ipa"],
                        help="Domain code")
    parser.add_argument("--note-type", required=True,
                        help="Note type (e.g., cs_lexeme, ipa_phoneme)")
    parser.add_argument("--deck", required=True,
                        help="Target deck name (e.g., 'CS::Test')")
    parser.add_argument("--model",
                        help="Anki model name (default: uppercase note type with underscores→capitals)")
    args = parser.parse_args()

    # Load domain config
    config = DomainConfig.load(args.domain, DOMAINS_DIR)

    # Determine model name
    model_name = args.model
    if not model_name:
        # Default: CS_Lexeme, SK_Alphabet, IPA_Phoneme, etc.
        parts = args.note_type.split("_")
        model_name = "_".join([parts[0].upper()] + [p.capitalize() for p in parts[1:]])

    # Determine category
    category = get_category_for_note_type(args.note_type)

    # Find test files
    cnsf_files = find_test_cnsf_files(args.domain, category)
    if not cnsf_files:
        print("No test files found.")
        return

    # Sync to Anki
    sync_notes_to_anki(args.domain, args.note_type, model_name, args.deck, cnsf_files, config)


if __name__ == "__main__":
    main()
