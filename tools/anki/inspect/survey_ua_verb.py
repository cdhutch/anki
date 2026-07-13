#!/usr/bin/env python3
"""
Survey UA_Verb notes and cards in Anki.
Shows note fields, card templates, and rendering details.
"""

import json
import urllib.request
import sys
from pathlib import Path

ANKI_URL = "http://localhost:8765"

def anki_request(action, params):
    """Make a request to AnkiConnect."""
    request_json = json.dumps({"action": action, "params": params, "version": 6})
    request = urllib.request.Request(
        ANKI_URL, data=request_json.encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 80)
    print("UA_VERB NOTE SURVEY")
    print("=" * 80)

    # Get all UA_Verb notes
    print("\n[1] Querying all UA_Verb notes...")
    result = anki_request("findNotes", {"query": 'note:"UA_Verb"'})
    if not result or "result" not in result:
        print("Error: Could not query notes")
        return

    note_ids = result["result"]
    print(f"Found {len(note_ids)} UA_Verb notes")

    if not note_ids:
        print("No notes found.")
        return

    # Get note details
    print("\n[2] Retrieving note details...")
    result = anki_request("notesInfo", {"notes": note_ids[:10]})  # First 10
    if not result or "result" not in result:
        print("Error: Could not get note info")
        return

    notes = result["result"]

    for i, note in enumerate(notes, 1):
        print(f"\n--- Note {i} ---")
        print(f"NoteID: {note.get('noteId')}")
        print(f"Model: {note.get('modelName')}")
        print(f"Tags: {', '.join(note.get('tags', []))}")

        print("\nFields:")
        fields = note.get("fields", {})
        for field_name, field_value in fields.items():
            value_preview = (field_value.get("value", "")[:60] + "...") if len(field_value.get("value", "")) > 60 else field_value.get("value", "")
            print(f"  {field_name}: {value_preview}")

        print("\nCards:")
        cards = note.get("cards", [])
        for card_id in cards:
            print(f"  Card ID: {card_id}")

    # Get model info
    print("\n" + "=" * 80)
    print("[3] UA_Verb Model Information")
    print("=" * 80)

    result = anki_request("modelFieldNames", {"modelName": "UA_Verb"})
    if result and "result" in result:
        print(f"\nModel Fields ({len(result['result'])}):")
        for i, field in enumerate(result["result"], 1):
            print(f"  {i:2}. {field}")

    # Get model templates
    print("\n[4] Card Templates")
    print("=" * 80)

    result = anki_request("modelTemplates", {"modelName": "UA_Verb"})
    if result and "result" in result:
        templates = result["result"]
        for template_name, template_data in templates.items():
            print(f"\n--- {template_name} ---")
            if "Front" in template_data:
                front = template_data["Front"][:200]
                print(f"Front (first 200 chars):\n{front}...")
            if "Back" in template_data:
                back = template_data["Back"][:300]
                print(f"Back (first 300 chars):\n{back}...")

    # Get rendered card
    print("\n" + "=" * 80)
    print("[5] Sample Rendered Card")
    print("=" * 80)

    if notes and notes[0].get("cards"):
        card_id = notes[0]["cards"][0]
        result = anki_request("guiSelectCard", {"card": card_id})
        print(f"Selected card {card_id} for viewing in Anki GUI")

    print("\n" + "=" * 80)
    print("Survey complete. Check Anki for the selected card.")
    print("=" * 80)

if __name__ == "__main__":
    main()
