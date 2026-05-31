#!/usr/bin/env python3
"""Import ua_lexeme CNSF notes into Anki via AnkiConnect.

Cards land in UA::Canonical::* decks, fully separate from legacy UA cards.
Upsert logic: adds new notes, updates fields on existing notes (matched by NoteID).

Deck layout:
    UA::Canonical::Recognition::UA→EN    ← UA→EN recognition card
    UA::Canonical::Production::EN→UA     ← EN→UA typing card

Usage (with Anki open + AnkiConnect running):
    # Dry run — show what would be added/updated, touch nothing
    python tools/anki/sync/ua_lexeme_import.py --dry-run domains/ua/anki/notes/lexemes/yabluko-l1/vstup/

    # Import a single file
    python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/vstup/ua-lexeme-0001.md

    # Import a whole directory
    python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/vstup/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

DECK_RECOGNITION = "UA::Canonical::Recognition::UA→EN"
DECK_PRODUCTION  = "UA::Canonical::Production::EN→UA"

# Cards that go to the production deck (by template name).
# All others land in the recognition deck.
PRODUCTION_TEMPLATES = {"EN→UA"}


# ---------------------------------------------------------------------------
# AnkiConnect helpers
# ---------------------------------------------------------------------------


def ensure_deck(deck_name: str, dry_run: bool):
    if dry_run:
        return
    anki_request("createDeck", {"deck": deck_name}, url=ANKI_URL)


def find_note_by_id(note_id: str) -> int | None:
    query = f'note:"{MODEL_NAME}" NoteID:"{note_id}"'
    results = anki_request("findNotes", {"query": query}, url=ANKI_URL)
    return int(results[0]) if results else None


def add_note(fields: dict, tags: list[str], dry_run: bool) -> int | None:
    if dry_run:
        return None
    return anki_request(
        "addNote",
        {
            "note": {
                "modelName": MODEL_NAME,
                "deckName": DECK_RECOGNITION,
                "fields": fields,
                "tags": tags,
                "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            }
        },
        url=ANKI_URL,
    )


def update_note(anki_id: int, fields: dict, tags: list[str], dry_run: bool):
    if dry_run:
        return
    anki_request("updateNoteFields", {"note": {"id": anki_id, "fields": fields}}, url=ANKI_URL)
    existing_tags = anki_request("getNoteTags", {"note": anki_id}, url=ANKI_URL) or []
    if existing_tags:
        anki_request("removeTags", {"notes": [anki_id], "tags": " ".join(existing_tags)}, url=ANKI_URL)
    if tags:
        anki_request("addTags", {"notes": [anki_id], "tags": " ".join(tags)}, url=ANKI_URL)


def move_card_to_production_deck(anki_note_id: int, dry_run: bool):
    """Move EN→UA cards to the production deck."""
    if dry_run:
        return
    card_ids = anki_request("findCards", {"query": f"nid:{anki_note_id}"}, url=ANKI_URL)
    if not card_ids:
        return
    cards_info = anki_request("cardsInfo", {"cards": card_ids}, url=ANKI_URL)
    for card in cards_info:
        if card.get("templateOrd") is not None:
            template_name = card.get("cardType", "")
            if template_name in PRODUCTION_TEMPLATES:
                anki_request(
                    "changeDeck",
                    {"cards": [card["cardId"]], "deck": DECK_PRODUCTION},
                    url=ANKI_URL,
                )


def set_suspended(anki_note_id: int, suspend: bool, dry_run: bool):
    if dry_run:
        return
    card_ids = anki_request("findCards", {"query": f"nid:{anki_note_id}"}, url=ANKI_URL)
    if not card_ids:
        return
    action = "suspend" if suspend else "unsuspend"
    anki_request(action, {"cards": card_ids}, url=ANKI_URL)


# ---------------------------------------------------------------------------
# CNSF parsing
# ---------------------------------------------------------------------------


def parse_note_file(path: Path) -> dict | None:
    """Parse a CNSF .md file and return its frontmatter as a dict."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        print(f"  SKIP {path.name}: no frontmatter")
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"  SKIP {path.name}: malformed frontmatter")
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"  SKIP {path.name}: YAML error — {e}")
        return None


# ---------------------------------------------------------------------------
# Import logic
# ---------------------------------------------------------------------------


def import_note(data: dict, dry_run: bool) -> str:
    """Import a single parsed note. Returns 'added', 'updated', or 'skipped'."""
    note_id = data.get("note_id", "")
    if not note_id:
        return "skipped"

    raw_fields = data.get("fields", {})
    if not raw_fields:
        return "skipped"

    # Coerce all field values to strings (YAML may parse numbers/booleans)
    fields = {k: ("" if v is None else str(v)) for k, v in raw_fields.items()}

    # Tags: from CNSF frontmatter
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    # status:draft → suspend cards after import
    suspend = "status:draft" in tags

    existing_id = find_note_by_id(note_id)

    if existing_id is None:
        anki_id = add_note(fields, tags, dry_run)
        if anki_id and not dry_run:
            move_card_to_production_deck(anki_id, dry_run)
            if suspend:
                set_suspended(anki_id, True, dry_run)
        return "added"
    else:
        update_note(existing_id, fields, tags, dry_run)
        if not dry_run:
            move_card_to_production_deck(existing_id, dry_run)
            set_suspended(existing_id, suspend, dry_run)
        return "updated"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def collect_files(targets: list[str]) -> list[Path]:
    files = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            files.extend(sorted(p.glob("ua-lexeme-*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: {t} is not a file or directory — skipping")
    return files


def main():
    parser = argparse.ArgumentParser(description="Import ua_lexeme notes into Anki.")
    parser.add_argument("targets", nargs="+", help="Files or directories to import")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; touch nothing")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no changes will be made to Anki.\n")

    ensure_deck(DECK_RECOGNITION, args.dry_run)
    ensure_deck(DECK_PRODUCTION, args.dry_run)

    files = collect_files(args.targets)
    if not files:
        print("No ua-lexeme-*.md files found.")
        sys.exit(1)

    added = updated = skipped = errors = 0

    for f in files:
        data = parse_note_file(f)
        if data is None:
            skipped += 1
            continue
        try:
            result = import_note(data, args.dry_run)
            note_id = data.get("note_id", f.name)
            lemma = (data.get("fields") or {}).get("Lemma", "")
            label = f"{note_id}  {lemma}"
            if result == "added":
                print(f"  ADD     {label}")
                added += 1
            elif result == "updated":
                print(f"  UPDATE  {label}")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR   {f.name}: {e}")
            errors += 1

    print(f"\nDone: {added} added, {updated} updated, {skipped} skipped, {errors} errors.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
