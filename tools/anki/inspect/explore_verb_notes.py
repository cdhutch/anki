#!/usr/bin/env python3
"""Explore existing UA_Verb and UA_Conjugation note types in Anki.

Shows model structure, field names, and sample notes.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/inspect/explore_verb_notes.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"


def explore_model(model_name: str):
    """Show model structure and sample notes."""
    print(f"\n{'='*80}")
    print(f"Model: {model_name}")
    print(f"{'='*80}")

    # Get model info
    try:
        models = anki_request("modelNames", url=ANKI_URL) or []
        if model_name not in models:
            print(f"  Model '{model_name}' not found in Anki.")
            return

        # Get fields
        fields = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL) or []
        print(f"\nFields ({len(fields)}):")
        for i, field in enumerate(fields, 1):
            print(f"  {i:2d}. {field}")

        # Get notes of this model
        notes = anki_request("findNotes", {"query": f'note:"{model_name}"'}, url=ANKI_URL) or []
        print(f"\nNotes: {len(notes)} total")

        if not notes:
            return

        # Show first 5 notes with full info
        print(f"\nFirst {min(5, len(notes))} notes:")
        for note_id in notes[:5]:
            info = anki_request("notesInfo", {"notes": [note_id]}, url=ANKI_URL)
            if not info:
                continue
            note = info[0]
            fields_dict = note.get("fields", {})

            # Extract values (AnkiConnect returns field metadata as dicts)
            def get_field_value(field_data):
                if isinstance(field_data, dict):
                    return field_data.get("value", "")
                return str(field_data) if field_data else ""

            note_id_val = get_field_value(fields_dict.get("NoteID", fields_dict.get("note_id", "")))
            lemma = get_field_value(fields_dict.get("Lemma", ""))
            aspect = get_field_value(fields_dict.get("Aspect", ""))
            tags = note.get("tags", [])

            print(f"\n  Lemma: {lemma}")
            if aspect:
                print(f"  Aspect: {aspect}")
            if note_id_val:
                print(f"  NoteID: {note_id_val}")
            if tags:
                print(f"  Tags: {', '.join(tags[:3])}")
            print(f"  Anki ID: {note_id}")

    except Exception as e:
        print(f"  Error exploring {model_name}: {e}")


def main():
    print("Exploring Ukrainian verb note types in Anki...\n")

    # List all models
    try:
        all_models = anki_request("modelNames", url=ANKI_URL) or []
        print(f"All models in Anki: {len(all_models)}")
        ua_models = [m for m in all_models if "UA" in m or "ua" in m or "Verb" in m or "verb" in m or "Conj" in m]
        print(f"Ukrainian/verb-related models: {len(ua_models)}")
        for m in sorted(ua_models):
            print(f"  - {m}")
    except Exception as e:
        print(f"Error listing models: {e}")
        return

    # Explore specific models
    for model_name in ["UA_Verb", "UA_Conjugation"]:
        explore_model(model_name)


if __name__ == "__main__":
    main()
