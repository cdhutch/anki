#!/usr/bin/env python3
"""Diagnostic: dump a live Anki note type's field names/templates, and
optionally one note's raw field content + rendered card question HTML.

Useful for troubleshooting a card that's rendering blank/wrong -- confirms
whether the live model's fields/templates actually match what the setup
script intends, and whether a specific note's data made it across correctly.

Usage:
    # Just dump the model's fields + templates
    python tools/anki/inspect/debug_model_note.py UA_Grammar

    # Also dump one note's raw fields + its cards' rendered question HTML
    python tools/anki/inspect/debug_model_note.py UA_Grammar ua-grammar-0008
    python tools/anki/inspect/debug_model_note.py UA_Lexeme ua-lexeme-0120
"""
import argparse
import json
import sys
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"


def anki_request(action, params=None):
    body = {"action": action, "version": 6}
    if params:
        body["params"] = params
    resp = urllib.request.urlopen(
        urllib.request.Request(ANKI_URL, data=json.dumps(body).encode("utf-8"))
    )
    result = json.loads(resp.read())
    if result.get("error"):
        print(f"AnkiConnect error for {action}: {result['error']}", file=sys.stderr)
        sys.exit(1)
    return result.get("result")


def main():
    parser = argparse.ArgumentParser(
        description="Dump a live Anki model's fields/templates, and optionally one note's raw content/cards."
    )
    parser.add_argument("model", help="Anki model/note-type name, e.g. UA_Grammar, UA_Lexeme, UA_Visual")
    parser.add_argument("note_id", nargs="?", default=None, help="CNSF NoteID to inspect (optional -- omit to just dump the model)")
    args = parser.parse_args()

    model_name = args.model

    print(f"=== Model field names (live in Anki, in order) ===")
    field_names = anki_request("modelFieldNames", {"modelName": model_name})
    print(field_names)

    print(f"\n=== Model templates (live in Anki) ===")
    templates = anki_request("modelTemplates", {"modelName": model_name})
    for tname, sides in (templates or {}).items():
        print(f"--- Template: {tname} ---")
        print("Front:", repr(sides.get("Front", ""))[:400])
        print("Back:", repr(sides.get("Back", ""))[:400])

    if not args.note_id:
        print("\nNo note_id given -- skipping note/card dump.")
        return

    note_id = args.note_id
    print(f"\n=== Note {note_id}: raw fields ===")
    query = f'note:"{model_name}" NoteID:"{note_id}"'
    note_ids = anki_request("findNotes", {"query": query})
    if not note_ids:
        print(f"No note found for query: {query}")
        return
    notes_info = anki_request("notesInfo", {"notes": note_ids})
    for note in notes_info:
        print(f"noteId={note['noteId']}  modelName={note['modelName']}")
        for fname, fval in note["fields"].items():
            val = fval.get("value", "")
            print(f"  [{fname}] order={fval.get('order')} len={len(val)}")
            print(f"    {val[:300]!r}")

    print(f"\n=== Cards for this note ===")
    card_ids = anki_request("findCards", {"query": f"nid:{note_ids[0]}"})
    cards_info = anki_request("cardsInfo", {"cards": card_ids})
    for c in cards_info:
        print(f"cardId={c['cardId']} ord={c.get('ord')} queue={c.get('queue')} deck={c.get('deckName')}")
        q = c.get("question", "")
        print(f"  question (first 400 chars): {q[:400]!r}")


if __name__ == "__main__":
    main()
