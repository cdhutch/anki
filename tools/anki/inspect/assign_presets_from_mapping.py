#!/usr/bin/env python3
"""Assign presets to decks based on DECK_PRESET_MAPPING.md

This script reads the deck-to-preset mapping and assigns the correct preset
to each deck via AnkiConnect. It does NOT modify preset limits.

Usage:
  python tools/anki/inspect/assign_presets_from_mapping.py
"""

import json
import urllib.request
import sys
from pathlib import Path

ANKI_URL = "http://127.0.0.1:8765"

# Deck to preset mapping
# Format: "deck_name": ("preset_name", new_limit, review_limit)
DECK_PRESET_MAP = {
    # UA Domain
    "UA": ("UA", 50, 100),
    "UA::Production": (None, 9999, 9999),  # Pass-through (no explicit preset)
    "UA::Production::EN→UA": ("UA Lexeme EN→UA", 15, 8),
    "UA::Recognition": (None, 9999, 9999),  # Pass-through (no explicit preset)
    "UA::Recognition::PVOM": ("UA PVOM", 18, 6),
    "UA::Recognition::UA→EN": ("UA->EN", 20, 9999),
    "UA::Recognition::Visual": ("UA Visual", 25, 10),
    "UA::Recognition::Grammar": ("UA Grammar", 20, 8),
    "UA::Verbs": ("UA Verbs", 20, 8),
    # B737 Domain
    "B737": ("B737", 0, 200),
    "B737::FO Procedures": ("B737", 0, 200),
    "B737::FO Systems": ("B737", 0, 200),
    "B737::FO Challenges": ("B737", 0, 200),
}


def anki_request(action, params=None):
    """Send request to AnkiConnect."""
    request_body = {"action": action, "version": 6}
    if params:
        request_body["params"] = params

    try:
        response = urllib.request.urlopen(
            urllib.request.Request(
                ANKI_URL,
                data=json.dumps(request_body).encode("utf-8"),
            )
        )
        result = json.loads(response.read())
        return result
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def get_preset_id_by_name(preset_name):
    """Get the config ID for a preset by name."""
    # Get all deck names to query
    result = anki_request("deckNames")
    if not result or result.get("error"):
        return None

    all_decks = result.get("result", [])

    # Try to find the preset by checking decks
    seen_presets = {}
    for deck in all_decks:
        config_result = anki_request("getDeckConfig", {"deck": deck})
        if config_result and not config_result.get("error"):
            config = config_result.get("result", {})
            config_name = config.get("name")
            config_id = config.get("id")

            if config_name == preset_name and config_id not in seen_presets:
                seen_presets[config_id] = config_name
                return config_id

    return None


def main():
    print("Assigning Presets to Decks")
    print("=" * 80)

    # Test connection
    print("\nTesting AnkiConnect connection...")
    version_result = anki_request("version")
    if not version_result:
        print("Error: Cannot connect to AnkiConnect. Make sure Anki is running.")
        sys.exit(1)

    print(f"✓ Connected to AnkiConnect (version: {version_result.get('result')})")

    # Process each deck
    print("\n" + "=" * 80)
    print("Assigning Presets")
    print("=" * 80)

    total_assigned = 0
    total_skipped = 0

    for deck_name, (preset_name, new_limit, review_limit) in DECK_PRESET_MAP.items():
        # Create deck if it doesn't exist
        anki_request("createDeck", {"deck": deck_name})

        # Skip pass-through decks (no explicit preset)
        if preset_name is None:
            print(f"\n{deck_name}")
            print(f"  (pass-through, no preset assignment needed)")
            total_skipped += 1
            continue

        # Get preset ID
        preset_id = get_preset_id_by_name(preset_name)
        if not preset_id:
            print(f"\n{deck_name}")
            print(f"  ✗ Preset '{preset_name}' not found")
            continue

        # Assign preset to deck
        assign_result = anki_request("setDeckConfigId",
                                     {"decks": [deck_name], "configId": preset_id})

        if not assign_result or assign_result.get("error"):
            print(f"\n{deck_name}")
            print(f"  ✗ Failed to assign: {assign_result.get('error') if assign_result else 'No response'}")
            continue

        print(f"\n{deck_name}")
        print(f"  ✓ Assigned preset '{preset_name}' (ID: {preset_id})")
        print(f"  Limits: {new_limit} new / {review_limit} review")
        total_assigned += 1

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Presets assigned: {total_assigned}")
    print(f"Pass-through decks (no assignment): {total_skipped}")
    print("\nVerification: Right-click each deck in Anki → Options to confirm")


if __name__ == "__main__":
    main()
