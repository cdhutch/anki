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
    - status:draft tag → suspend (inactive/unreviewed)
    - conj:suspended tag → always suspend (added 2026-08-19, per Craig --
      reference only, not for drilling). Mirrors ua_verb_import.py, where the
      same tag separates the motion-verb cores that get drilled from the
      predictable derivatives kept only as reference. PVOM needed its own copy
      because curation had no lever here at all: the only way to hold a note
      out of the rotation was status:draft, which asserts "unreviewed" and
      would drag a fully-verified note back into list_unverified.py's report.
      Craig keeps при-, в/у-, ви- and під- active because between them they
      cover the gamut of stress patterns -- regular, prefix-stressed
      (ви́йти/ви́їхати), -ій- epenthesis with apostrophe, and the в-/у- euphonic
      alternation -- and suspends the other nine, whose behaviour follows from
      those four.
    - no suspend tag present → unsuspend
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
    flag_query_for_model,
    get_flagged_note_ids_by_color,
)

# Named here for the first time 2026-08-20. Every other UA importer already had
# a MODEL_NAME constant; this one only ever spelled the model inline, as
# anki_config.get("model", "UA_PVOM_Infinitive") in build_note(). That default
# still reads from the note's own `anki.model`, which stays the authority for
# what gets WRITTEN -- this constant scopes flag QUERIES, which are per-run
# rather than per-note.
MODEL_NAME = "UA_PVOM_Infinitive"

# Flag-query scope for the red/orange-flag check -- scoped to this note type
# (2026-08-20); see flag_query_for_model() in tsv_to_anki.py. This importer is
# where the problem was first seen: its first live run printed 26 orange-flagged
# notes, not one of which was PVOM.
FLAG_DECK_QUERY = flag_query_for_model(MODEL_NAME)

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
    """Suspension policy for UA_PVOM_Infinitive cards -- see module docstring.

    Two independent axes, matching ua_verb_import.py:
        - status:draft      → content not reviewed
        - conj:suspended    → reviewed and correct, but deliberately not drilled
    Any one of them suspends. Keeping them separate is what lets a note be
    verified on quality axis and still held out of the rotation without
    lying about its review state.
    """
    return (
        "status:draft" in tags
        or "conj:suspended" in tags
    )


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
        for update, tags in zip(updates, update_tags):
            result = anki_connect("updateNoteFields", {"note": update})
            if result and not result.get("error"):
                updated += 1
            else:
                print(f"✗ Update failed for note {update['id']}: {result}", file=sys.stderr)
                return False

            # Tags, separately -- AnkiConnect's updateNoteFields touches FIELDS
            # ONLY and silently leaves tags alone. Fixed 2026-08-18: this script
            # was the odd one out of the five UA importers (ua_lexeme_import.py,
            # ua_verb_import.py, ua_grammar_import.py and ua_visual_import.py
            # all already did this), so PVOM tags in Anki had been frozen at
            # whatever each note was CREATED with, and no CNSF tag edit had ever
            # reached Anki on the update path.
            #
            # It hid well: `tags` was already being collected here, and IS used
            # for the suspend decision below -- but that decision reads the CNSF
            # tags directly, never Anki's. So suspend/unsuspend behaved perfectly
            # correctly off fresh tags while the tags shown in Anki went stale.
            # That is why Craig's 13-note stress:unverified -> stress:verified
            # pass unsuspended all 52 cards on 2026-08-18 and yet the browser
            # still showed stress:unverified.
            #
            # remove-then-add rather than add-only, matching the other four: an
            # add-only pass cannot clear a tag that was REMOVED from the CNSF
            # file, which is precisely the stress:unverified case.
            anki_id = update["id"]
            existing = anki_connect("getNoteTags", {"note": anki_id})
            existing_tags = (existing or {}).get("result") or []
            if existing_tags:
                anki_connect("removeTags",
                             {"notes": [anki_id], "tags": " ".join(existing_tags)})
            if tags:
                anki_connect("addTags", {"notes": [anki_id], "tags": " ".join(tags)})

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
