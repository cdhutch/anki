#!/usr/bin/env python3
"""Import UA_PVOM_Infinitive CNSF notes to Anki via AnkiConnect.

Each note carries one prefix and all four verb-of-motion base forms:
Walking_Multi_{UA,Typing}, Walking_Uni_{UA,Typing}, Vehicle_Multi_{UA,Typing},
Vehicle_Uni_{UA,Typing}, plus NoteID/Prefix/Tags_Ch/Source_Note/Verification Notes.
CNSF field names match the Anki field names exactly -- no renaming/derivation
needed, unlike the old single-form schema this replaced.

Suspension policy (added 2026-07-31 -- this script previously had none at
all, so a card suspended by accident here, e.g. a mistyped Command-1/Alt-1
during review, stayed suspended forever; nothing ever re-asserted a state):
    - stress:unverified tag → suspend (every PVOM note currently carries
      this tag; none has been Горох-re-verified since the prefix drilling
      set was built, matching the same "not ready for drilling until
      confirmed" rationale used in ua_verb_import.py)
    - status:draft tag → suspend (no current PVOM note uses this tag, but
      checked for consistency with every other UA note type in case one
      ever does)
    - neither tag present → unsuspend
    - note has a red-flagged card → suspend, regardless of tags above (per
      Craig -- see get_flagged_note_ids_by_color in tsv_to_anki.py). Only
      checked for existing notes; a brand-new note can't already have a
      flagged card in Anki.
    - note has an orange-flagged card, no red → NOT suspended (does not
      override the tag-based decision above). Called out in the sync log
      instead (2026-08-10, per Craig -- orange means "confusing/unclear",
      not "wrong"; see CLAUDE-flag-audit.md).
Applied on every import, add or update -- declarative and self-healing like
every other UA note type, not just a one-time default at creation.
"""

import argparse
import json
import urllib.request
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import (  # noqa: E402
    FLAG_ORANGE,
    FLAG_RED,
    anki_request,
    describe_note_ids,
    get_flagged_note_ids_by_color,
)

# Deck query scope for the red/orange-flag suspend check -- same query
# string used across every UA sync script; see ua_lexeme_import.py.
FLAG_DECK_QUERY = "deck:UA::*"

ANKI_FIELDS = [
    "NoteID",
    "Prefix",
    "Walking_Multi_UA",
    "Walking_Multi_Typing",
    "Walking_Multi_Euphony",
    "Walking_Uni_UA",
    "Walking_Uni_Typing",
    "Walking_Uni_Euphony",
    "Vehicle_Multi_UA",
    "Vehicle_Multi_Typing",
    "Vehicle_Multi_Euphony",
    "Vehicle_Uni_UA",
    "Vehicle_Uni_Typing",
    "Vehicle_Uni_Euphony",
    "Tags_Ch",
    "Source_Note",
    "Verification Notes",  # unified 2026-08-11, per Craig -- was underscore-only
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


def should_suspend(tags):
    """Suspension policy for UA_PVOM_Infinitive cards -- see module docstring."""
    return "stress:unverified" in tags or "status:draft" in tags


def set_suspended(anki_note_id, suspend, dry_run=False):
    """Suspend or unsuspend every card belonging to an Anki note ID."""
    if dry_run:
        return
    result = anki_connect("findCards", {"query": f"nid:{anki_note_id}"})
    card_ids = (result or {}).get("result") or []
    if not card_ids:
        return
    action = "suspend" if suspend else "unsuspend"
    anki_connect(action, {"cards": card_ids})


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


def upsert_notes(pvom_dir, dry_run=False):
    """Upsert all PVOM infinitive notes (update if exists, create if new)."""
    pvom_path = Path(pvom_dir)

    if not pvom_path.is_dir():
        print(f"Error: {pvom_dir} is not a directory", file=sys.stderr)
        return False

    # One bulk query for the whole sync run -- see get_flagged_note_ids_by_color.
    # Red still forces suspension; orange is a call-out only (2026-08-10, per
    # Craig -- see SUSPEND_FLAG_COLORS in tsv_to_anki.py).
    flags_by_color = get_flagged_note_ids_by_color(FLAG_DECK_QUERY)
    flagged_note_ids = flags_by_color[FLAG_RED]
    if flagged_note_ids:
        print(f"Found {len(flagged_note_ids)} note(s) with a red-flagged card -- keeping suspended.")
    orange_flagged_note_ids = flags_by_color[FLAG_ORANGE]
    if orange_flagged_note_ids:
        print(f"⚠ {len(orange_flagged_note_ids)} note(s) have an orange-flagged card "
              f"(confusing/unclear) -- NOT suspended, flagged for review:")
        for label in describe_note_ids(orange_flagged_note_ids):
            print(f"    {label}")

    notes_to_create = []
    updates = []
    # Tags carried alongside updates/creates so suspend state can be applied
    # after add/update succeeds -- updateNoteFields/addNotes only touch
    # fields, never suspend state, so that's a separate pass below.
    update_tags = []  # parallel to `updates`, same index
    create_tags = []  # parallel to `notes_to_create`, same index

    for filepath in sorted(pvom_path.glob("ua-pvom-*.md")):
        note_data = load_note_from_cnsf(filepath)
        if not note_data:
            print(f"⚠ Skipped {filepath.name}", file=sys.stderr)
            continue

        fields = note_data.get("fields", {})
        noteid = fields.get("NoteID", "")
        tags = note_data.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        existing_note_id = find_note_by_noteid(noteid)

        if existing_note_id:
            updates.append({
                "id": existing_note_id,
                "fields": anki_fields_from(fields),
            })
            update_tags.append(tags)
        else:
            notes_to_create.append(build_anki_note(note_data))
            create_tags.append(tags)

    if dry_run:
        for note, tags in zip(notes_to_create, create_tags):
            note_id = note["fields"]["NoteID"]
            print(f"  ADD (dry-run)     {note_id}  suspend={should_suspend(tags)}")
        for update, tags in zip(updates, update_tags):
            note_suspend = should_suspend(tags) or (update["id"] in flagged_note_ids)
            print(f"  UPDATE (dry-run)  id={update['id']}  suspend={note_suspend}")
        total = len(notes_to_create) + len(updates)
        print(f"\nDRY RUN: would process {total} PVOM infinitive notes "
              f"({len(notes_to_create)} create, {len(updates)} update). No changes made.")
        return True

    created = 0
    created_ids = []
    if notes_to_create:
        result = anki_connect("addNotes", {"notes": notes_to_create})
        if result and not result.get("error"):
            created_ids = result.get("result", [])
            created = len([nid for nid in created_ids if nid is not None])
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

    # Suspend policy pass -- see module docstring. A brand-new note can't
    # already have a flagged card in Anki, so the flag check only applies
    # to the update path.
    for note_id, tags in zip(created_ids, create_tags):
        if note_id is not None and should_suspend(tags):
            set_suspended(note_id, True)

    for update, tags in zip(updates, update_tags):
        note_suspend = should_suspend(tags) or (update["id"] in flagged_note_ids)
        set_suspended(update["id"], note_suspend)

    total = len(notes_to_create) + len(updates)
    print(f"✓ Processed {total} PVOM infinitive notes ({created} created, {updated} updated)")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import ua_pvom_infinitive notes into Anki.")
    parser.add_argument("pvom_dir", help="Directory of ua-pvom-*.md files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; touch nothing")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no changes will be made to Anki.\n")

    if upsert_notes(args.pvom_dir, dry_run=args.dry_run):
        sys.exit(0)
    else:
        sys.exit(1)
