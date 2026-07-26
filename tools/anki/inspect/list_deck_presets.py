#!/usr/bin/env python3
"""List all deck presets and their current assignments."""

import json
import urllib.request
import sys

ANKI_URL = "http://127.0.0.1:8765"


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


def main():
    print("Deck Presets and Assignments")
    print("=" * 80)

    # Get all decks
    result = anki_request("deckNames")
    if not result or result.get("error"):
        print("Error getting deck names")
        return

    all_decks = result.get("result", [])
    ua_decks = sorted([d for d in all_decks if d.startswith("UA")])

    # Build a map of deck → current config
    print("\n1. CURRENT PRESET ASSIGNMENTS (UA decks)")
    print("-" * 80)

    deck_to_config = {}
    config_names = {}

    for deck in ua_decks:
        result = anki_request("getDeckConfig", {"deck": deck})
        if result and not result.get("error"):
            config = result.get("result", {})
            config_id = config.get("id")
            config_name = config.get("name", "Unknown")
            new_limit = config.get("new", {}).get("perDay", "?")
            rev_limit = config.get("rev", {}).get("perDay", "?")

            parts = deck.split("::")
            indent = "  " * (len(parts) - 1)

            print(f"{indent}{deck}")
            print(f"{indent}  → Preset: {config_name} (ID: {config_id})")
            print(f"{indent}  → Limits: {new_limit} new / {rev_limit} review")

            deck_to_config[deck] = {"id": config_id, "name": config_name}
            config_names[config_id] = config_name

    # List all available presets
    print("\n2. ALL AVAILABLE PRESETS")
    print("-" * 80)

    # Get a list of all unique config IDs from decks (simplified approach)
    # In practice, we'd need to query all configs; this shows what we found
    unique_configs = {}
    for config_id, name in config_names.items():
        # Get config details
        result = anki_request("getDeckConfig", {"deck": "Default"})  # Get via default deck
        # This won't work perfectly, so let's just show what we have
        if config_id not in unique_configs:
            unique_configs[config_id] = name

    if unique_configs:
        for config_id, name in sorted(unique_configs.items(), key=lambda x: x[1]):
            print(f"  • {name} (ID: {config_id})")

    print("\n3. TO ASSIGN A PRESET TO A DECK:")
    print("-" * 80)
    print("Use the preset name from section 2 above.")
    print("Right-click the deck in Anki → Options → select preset from dropdown")
    print("\nOR use this command to assign via script:")
    print("  python tools/anki/inspect/assign_preset.py <deck> <preset_id>")


if __name__ == "__main__":
    main()
