#!/usr/bin/env python3
"""Generic domain-aware CNSF importer for multi-language Anki sync.

Imports CNSF notes into Anki via AnkiConnect. Works for any domain
(UA, CS, DE, SK, IPA) and any note type defined in the domain config.

Each note's own `anki: {model, deck}` frontmatter decides where it goes;
--model/--deck are only a fallback for notes that omit one. By default,
every subdirectory under the note type's category folder is scanned (not
just test/), so a generated corpus (e.g. phonemes/round1/) is picked up
alongside hand-authored test notes. Pass --subdir to restrict to one.

Usage:
    # Sync everything under domains/ipa/anki/notes/phonemes/ (test/, round1/, ...);
    # each note's own anki.deck sends it to IPA::Consonants / IPA::Vowels / etc.
    python tools/anki/sync/generic_domain_import.py --domain ipa --note-type ipa_phoneme

    # Restrict to just the hand-authored test note, overriding its deck:
    python tools/anki/sync/generic_domain_import.py \\
        --domain cs --note-type cs_lexeme --subdir test --deck "CS::Test"

Reads CNSF files from domains/{domain}/anki/notes/{category}/**/*.md
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
# __file__ is <repo_root>/tools/anki/sync/generic_domain_import.py, so
# parents[3] is <repo_root> (parents[2] was "tools" -- a pre-existing
# off-by-one that meant this script could never find real files or configs).
_REPO_ROOT = Path(__file__).resolve().parents[3]
DOMAINS_DIR = _REPO_ROOT / "config" / "domains"
NOTES_DIR = _REPO_ROOT / "domains"

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


def find_cnsf_files(domain: str, category: str, subdir: str | None = None) -> List[Path]:
    """Find CNSF files for a domain/category.

    By default, scans every subdirectory under the category (test/, round1/,
    chapter folders, etc.) -- not just test/ -- so generated corpora are
    picked up alongside hand-authored test notes. Pass --subdir to restrict
    to one specific subdirectory (e.g. "test" for the old behavior).
    """
    category_dir = NOTES_DIR / domain / "anki" / "notes" / category
    if not category_dir.exists():
        print(f"Category directory not found: {category_dir}")
        return []

    if subdir:
        target_dir = category_dir / subdir
        if not target_dir.exists():
            print(f"Subdirectory not found: {target_dir}")
            return []
        files = sorted(target_dir.glob("*.md"))
        print(f"Found {len(files)} file(s) in {target_dir.relative_to(NOTES_DIR)}/")
        return files

    files = sorted(category_dir.glob("**/*.md"))
    print(f"Found {len(files)} file(s) under {category_dir.relative_to(NOTES_DIR)}/ (all subdirectories)")
    return files


# Backward-compatible alias for the old test-only finder.
def find_test_cnsf_files(domain: str, category: str) -> List[Path]:
    return find_cnsf_files(domain, category, subdir="test")


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


def resolve_model_and_deck(
    cnsf_data: Dict[str, Any], default_model: str, default_deck: str | None
) -> tuple[str, str | None]:
    """A note's own `anki: {model, deck}` frontmatter wins; CLI --model/--deck
    are only a fallback for notes that don't specify one."""
    anki_meta = cnsf_data.get("anki") or {}
    model_name = anki_meta.get("model") or default_model
    deck_name = anki_meta.get("deck") or default_deck
    return model_name, deck_name


def sync_notes_to_anki(
    domain: str,
    note_type: str,
    model_name: str,
    deck_name: str | None,
    cnsf_files: List[Path],
    config: DomainConfig,
) -> None:
    """Sync CNSF notes to Anki via AnkiConnect.

    Each note's own `anki: {model, deck}` frontmatter determines where it
    goes; model_name/deck_name here are only the fallback for notes that
    don't specify one (e.g. --model/--deck on the CLI).
    """
    nt_config = config.note_types.get(note_type)
    if not nt_config:
        print(f"ERROR: Note type '{note_type}' not found in {domain} config")
        return

    fields_list = nt_config.fields

    existing_models = anki_request("modelNames", url=ANKI_URL) or []

    # Pre-parse to discover every deck this run will need, and create them
    # up front (createDeck is idempotent -- a no-op for decks that already
    # exist). AnkiConnect's addNote does NOT auto-create missing decks.
    parsed: List[tuple[Path, Dict[str, Any]]] = []
    needed_decks: set[str] = set()
    for cnsf_path in cnsf_files:
        cnsf_data = parse_cnsf_file(cnsf_path)
        if not cnsf_data:
            continue
        parsed.append((cnsf_path, cnsf_data))
        _, resolved_deck = resolve_model_and_deck(cnsf_data, model_name, deck_name)
        if resolved_deck:
            needed_decks.add(resolved_deck)

    for deck in sorted(needed_decks):
        anki_request("createDeck", {"deck": deck}, url=ANKI_URL)
    if needed_decks:
        print(f"Ensured {len(needed_decks)} deck(s) exist: {', '.join(sorted(needed_decks))}")

    print(f"\nSyncing {len(cnsf_files)} note(s)...")

    synced = 0
    by_deck: Dict[str, int] = {}
    for cnsf_path, cnsf_data in parsed:
        resolved_model, resolved_deck = resolve_model_and_deck(cnsf_data, model_name, deck_name)
        if not resolved_deck:
            print(f"  \u2717 {cnsf_path.name}: no deck in note frontmatter and no --deck fallback given")
            continue
        if resolved_model not in existing_models:
            print(f"  \u2717 {cnsf_path.name}: model '{resolved_model}' not found in Anki")
            continue

        anki_note = build_anki_note(cnsf_data, resolved_model, fields_list)

        try:
            anki_request(
                "addNote",
                {
                    "note": {
                        **anki_note,
                        "deckName": resolved_deck,
                    }
                },
                url=ANKI_URL,
            )
            print(f"  \u2713 {cnsf_path.name} -> {resolved_deck}")
            synced += 1
            by_deck[resolved_deck] = by_deck.get(resolved_deck, 0) + 1
        except Exception as e:
            print(f"  \u2717 {cnsf_path.name}: {e}")

    print(f"\nSynced {synced}/{len(cnsf_files)} note(s).")
    for deck, count in sorted(by_deck.items()):
        print(f"  {deck}: {count}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True, choices=["cs", "de", "sk", "ipa"],
                        help="Domain code")
    parser.add_argument("--note-type", required=True,
                        help="Note type (e.g., cs_lexeme, ipa_phoneme)")
    parser.add_argument("--deck",
                        help="Fallback deck name for notes that don't set anki.deck "
                             "themselves (e.g. 'CS::Test'). Most generated notes carry "
                             "their own deck and don't need this.")
    parser.add_argument("--model",
                        help="Fallback Anki model name for notes that don't set anki.model "
                             "(default when needed: uppercase note type, underscores->capitals)")
    parser.add_argument("--subdir",
                        help="Restrict to one subdirectory under the note-type's category "
                             "folder (e.g. 'test'). Default: scan all subdirectories.")
    args = parser.parse_args()

    # Load domain config
    config = DomainConfig.load(args.domain, DOMAINS_DIR)

    # Determine fallback model name
    model_name = args.model
    if not model_name:
        # Default: CS_Lexeme, SK_Alphabet, IPA_Phoneme, etc.
        parts = args.note_type.split("_")
        model_name = "_".join(p.capitalize() for p in parts)

    # Determine category
    category = get_category_for_note_type(args.note_type)

    # Find files
    cnsf_files = find_cnsf_files(args.domain, category, subdir=args.subdir)
    if not cnsf_files:
        print("No files found.")
        return

    # Sync to Anki
    sync_notes_to_anki(args.domain, args.note_type, model_name, args.deck, cnsf_files, config)


if __name__ == "__main__":
    main()
