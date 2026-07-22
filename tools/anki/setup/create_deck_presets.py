#!/usr/bin/env python3
"""Create deck presets for UA and B737 domains via AnkiConnect.

Reads preset definitions from JSON files and creates them in Anki.
Assigns created presets to specified decks.
"""

import json
import urllib.request
import sys
import time
from pathlib import Path

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


def load_preset_definitions(preset_file):
    """Load preset definitions from JSON file."""
    if not preset_file.exists():
        print(f"Error: Preset file not found: {preset_file}")
        return None

    with open(preset_file, 'r') as f:
        data = json.load(f)

    return data.get("presets", [])


def get_template_config():
    """Get a template config from the Default deck to use as a base."""
    result = anki_request("getDeckConfig", {"deck": "Default"})
    if not result or result.get("error"):
        print(f"Error getting template config: {result.get('error') if result else 'No response'}")
        return None

    return result.get("result")


def create_or_update_preset(preset_def):
    """Create or update a preset with the given definition using cloneDeckConfigId."""
    preset_name = preset_def["name"]
    new_per_day = preset_def["new_per_day"]
    review_per_day = preset_def["review_per_day"]

    print(f"\n  Creating/updating preset: {preset_name}")
    print(f"    Limits: {new_per_day} new / {review_per_day} review")

    # Step 1: Clone from Default preset (ID 1) to create a new preset
    clone_result = anki_request("cloneDeckConfigId",
                                {"name": preset_name, "cloneFrom": 1})

    if not clone_result:
        return None, "No response from cloneDeckConfigId"

    if isinstance(clone_result, dict) and clone_result.get("error"):
        return None, f"Clone error: {clone_result.get('error')}"

    # cloneDeckConfigId returns the new config ID
    new_config_id = clone_result.get("result") if isinstance(clone_result, dict) else clone_result

    if not new_config_id:
        return None, f"Failed to clone preset (got {clone_result})"

    # Step 2: Create a temporary deck and assign the new config to fetch full config
    tmp_deck = f"__tmp_preset_fetch_{int(time.time() * 1000)}__"
    anki_request("createDeck", {"deck": tmp_deck})
    anki_request("setDeckConfigId", {"decks": [tmp_deck], "configId": new_config_id})

    # Step 3: Get the full config object
    config_result = anki_request("getDeckConfig", {"deck": tmp_deck})
    if not config_result or config_result.get("error"):
        anki_request("deleteDecks", {"decks": [tmp_deck], "cardsToo": True})
        return None, f"Failed to get config: {config_result.get('error') if config_result else 'No response'}"

    config = config_result.get("result")

    # Step 4: Delete the temporary deck
    anki_request("deleteDecks", {"decks": [tmp_deck], "cardsToo": True})

    # Step 5: Modify the config with target limits
    config["new"]["perDay"] = new_per_day
    config["rev"]["perDay"] = review_per_day

    # Step 6: Save the modified config
    save_result = anki_request("saveDeckConfig", {"config": config})

    if not save_result or save_result.get("error"):
        return None, f"Failed to save config: {save_result.get('error') if save_result else 'No response'}"

    # Use the config object's ID (not saveDeckConfig's return value, which is just True/False)
    config_id = config.get("id")
    if not config_id:
        return None, f"Config object has no ID"

    print(f"    ✓ Created/updated (ID: {config_id})")
    return config_id, None


def assign_preset_to_decks(config_id, deck_names):
    """Assign a preset to one or more decks."""
    print(f"    Assigning to {len(deck_names)} deck(s)...")

    # Try to assign to each deck individually (safer than batch)
    failed = []
    for deck_name in deck_names:
        result = anki_request("setDeckConfigId", {"decks": [deck_name], "configId": config_id})

        if not result or result.get("error"):
            error_msg = result.get("error") if result else "No response"
            print(f"      ⚠ Failed to assign to {deck_name}: {error_msg}")
            failed.append(deck_name)
        else:
            print(f"      ✓ Assigned to {deck_name}")

    return len(failed) == 0


def main():
    print("Creating Deck Presets via AnkiConnect")
    print("=" * 80)

    # Test connection
    print("\nTesting AnkiConnect connection...")
    version_result = anki_request("version")
    if not version_result:
        print("Error: Cannot connect to AnkiConnect. Make sure Anki is running.")
        sys.exit(1)

    print(f"✓ Connected to AnkiConnect (version: {version_result.get('result')})")

    # Get list of domains to process
    # Path: tools/anki/setup/create_deck_presets.py → repo root is 4 levels up
    repo_root = Path(__file__).parent.parent.parent.parent
    domains = [
        ("UA", repo_root / "domains/ua/anki/presets/preset_definitions.json"),
        ("B737", repo_root / "domains/b737/anki/presets/preset_definitions.json"),
    ]

    total_presets = 0
    total_assigned = 0

    for domain_name, preset_file in domains:
        print(f"\n{'=' * 80}")
        print(f"Processing {domain_name} Domain")
        print(f"{'=' * 80}")

        presets = load_preset_definitions(preset_file)
        if not presets:
            print(f"No presets found for {domain_name}")
            continue

        for preset_def in presets:
            config_id, error = create_or_update_preset(preset_def)

            if error:
                print(f"    ✗ {error}")
                continue

            total_presets += 1

            # Assign to decks
            deck_names = preset_def.get("decks_to_assign", [])
            if deck_names:
                if assign_preset_to_decks(config_id, deck_names):
                    total_assigned += len(deck_names)

    print(f"\n{'=' * 80}")
    print("Summary")
    print(f"{'=' * 80}")
    print(f"Presets created/updated: {total_presets}")
    print(f"Deck assignments completed: {total_assigned}")
    print("\nVerification: Right-click each deck in Anki → Options to confirm")


if __name__ == "__main__":
    main()
