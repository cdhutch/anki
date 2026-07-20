#!/usr/bin/env python3
"""Update deck limits by modifying existing deck configs via AnkiConnect.

Reads deck limit configuration from domains/ua/anki/config/deck_limits.yaml
"""

import json
import urllib.request
import sys
import yaml
from pathlib import Path

ANKI_URL = "http://127.0.0.1:8765"
CONFIG_FILE = Path(__file__).parent.parent.parent / "domains/ua/anki/config/deck_limits.yaml"


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


def load_config():
    """Load deck limits from YAML config file."""
    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    return config.get("decks", {})


def update_deck_limits():
    """Update limits for specified decks."""
    print("Updating Deck Limits via AnkiConnect")
    print("=" * 70)

    deck_limits = load_config()

    for deck_name, limits in deck_limits.items():
        # Skip suspended decks
        if limits.get("suspended", False):
            print(f"\n{deck_name} [SUSPENDED - skipped]")
            continue

        print(f"\n{deck_name}")
        print(f"  Target: {limits['new']} new / {limits['review']} review")

        # Get existing config for this deck
        result = anki_request("getDeckConfig", {"deck": deck_name})

        if not result or result.get("error"):
            print(f"  ✗ Failed to get config: {result.get('error') if result else 'No response'}")
            continue

        config = result.get("result")
        if not config:
            print(f"  ✗ No config returned")
            continue

        # Show current limits
        current_new = config.get("new", {}).get("perDay", "?")
        current_rev = config.get("rev", {}).get("perDay", "?")
        print(f"  Current: {current_new} new / {current_rev} review")

        # Modify the config
        config["new"]["perDay"] = limits["new"]
        config["rev"]["perDay"] = limits["review"]

        # Save the modified config back
        save_result = anki_request("saveDeckConfig", {"config": config})

        if save_result and not save_result.get("error"):
            print(f"  ✓ Updated successfully")
        else:
            error = save_result.get("error") if save_result else "No response"
            print(f"  ✗ Failed to save: {error}")

    print("\n" + "=" * 70)
    print("Verification: Right-click each deck in Anki → Options to confirm")


if __name__ == "__main__":
    update_deck_limits()
