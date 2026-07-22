#!/usr/bin/env python3
"""Import UA_PVOM_Infinitive CNSF notes to Anki via AnkiConnect.

Each note carries one prefix and all four verb-of-motion base forms:
Walking_Multi_{UA,Typing}, Walking_Uni_{UA,Typing}, Vehicle_Multi_{UA,Typing},
Vehicle_Uni_{UA,Typing}, plus NoteID/Prefix/Tags_Ch/Source_Note/Verification_Notes.
CNSF field names match the Anki field names exactly -- no renaming/derivation
needed, unlike the old single-form schema this replaced.
"""

import json
import urllib.request
import sys
from pathlib import Path
import yaml

ANKI_FIELDS = [
    "NoteID",
    "Prefix",
    "Walking_Multi_UA",
    "Walking_Multi_Typing",
    "Walking_Uni_UA",
    "Walking_Uni_Typing",
    "Vehicle_Multi_UA",
    "Vehicle_Multi_Typing",
    "Vehicle_Uni_UA",
    "Vehicle_Uni_Typing",
    "Tags_Ch",
    "Source_Note",
    "Verification_Notes",
]


def anki_connect(action, params=None):
    """Send request to AnkiConnect."""
    request_body = {"action": action, "version": 6}
    if params:
        request_body["params"] = params

    try:
        response = urllib.request.urlopen(
            urllib.request.Request(
                "http://localhost:8765",
                data=json.dumps(request_body).encode("utf-8"),
            )
        )
        return json.loads(response.read())
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def load_note_from_cnsf(filepath):
    """Load note from CNSF markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            yaml_content = parts[1]
            try:
                data = yaml.safe_load(yaml_content)
                return data
            except yaml.YAMLError as e:
                print(f"YAML parse error in {filepath}: {e}", file=sys.stderr)
                return None
    return None


def anki_fields_from(fields):
    """Map CNSF fields dict straight through to the Anki field set."""
    return {name: fields.get(name, "") for name in ANKI_FIELDS}


def build_anki_note(note_data):
    """Build Anki note from CNSF data."""
    fields = note_data.get("fields", {})
    anki_config = note_data.get("anki", {})
    tags = note_data.get("tags", [])

    return {
        "deckName": anki_config.get("deck", "UA::Recognition::PVOM"),
        "modelName": anki_config.get("model", "UA_PVOM_Infinitive"),
        "fields": anki_fields_from(fields),
        "tags": tags,
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    }


def find_note_by_noteid(noteid, deck_name="UA::Recognition::PVOM"):
    """Find a note ID by NoteID field value."""
    result = anki_connect(
        "findNotes",
        {"query": f'"NoteID:{noteid}" deck:"{deck_name}"'},
    )
    if result and not result.get("error"):
        note_ids = result.get("result", [])
        return note_ids[0] if note_ids else None
    return None


def upsert_notes(pvom_dir):
    """Upsert all PVOM infinitive notes (update if exists, create if new)."""
    pvom_path = Path(pvom_dir)

    if not pvom_path.is_dir():
        print(f"Error: {pvom_dir} is not a directory", file=sys.stderr)
        return False

    notes_to_create = []
    updates = []

    for filepath in sorted(pvom_path.glob("ua-pvom-*.md")):
        note_data = load_note_from_cnsf(filepath)
        if not note_data:
            print(f"⚠ Skipped {filepath.name}", file=sys.stderr)
            continue

        fields = note_data.get("fields", {})
        noteid = fields.get("NoteID", "")

        existing_note_id = find_note_by_noteid(noteid)

        if existing_note_id:
            updates.append({
                "id": existing_note_id,
                "fields": anki_fields_from(fields),
            })
        else:
            notes_to_create.append(build_anki_note(note_data))

    created = 0
    if notes_to_create:
        result = anki_connect("addNotes", {"notes": notes_to_create})
        if result and not result.get("error"):
            note_ids = result.get("result", [])
            created = len([nid for nid in note_ids if nid is not None])
        else:
            print(f"✗ Create failed: {result}", file=sys.stderr)
            return False

    updated = 0
    if updates:
        for update in updates:
            result = anki_connect("updateNoteFields", {"note": update})
            if result and not result.get("error"):
                updated += 1
            else:
                print(f"✗ Update failed for note {update['id']}: {result}", file=sys.stderr)
                return False

    total = len(notes_to_create) + len(updates)
    print(f"✓ Processed {total} PVOM infinitive notes ({created} created, {updated} updated)")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python ua_pvom_infinitive_import.py <pvom_notes_dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    pvom_dir = sys.argv[1]
    if upsert_notes(pvom_dir):
        sys.exit(0)
    else:
        sys.exit(1)
