#!/usr/bin/env python3
"""Set UA::Recognition::PVOM deck limits to 22/0/6."""

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
        if result and result.get("error"):
            print(f"AnkiConnect error: {result['error']}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def main():
    print("Setting UA::Recognition::PVOM deck limits to 22/0/6")
    print("=" * 60)

    deck_name = "UA::Recognition::PVOM"

    # Get current deck configuration
    result = anki_request("getDeckConfig")
    if not result or result.get("error"):
        print("Could not retrieve deck config", file=sys.stderr)
        return False

    configs = result.get("result", [])
    if not configs:
        print("No deck configs found", file=sys.stderr)
        return False

    # Find or use default config
    print(f"\nAvailable configs: {len(configs)}")
    default_config = configs[0]  # Usually the default

    print(f"Using config: {default_config.get('name', 'Unknown')}")

    # Create modified config for PVOM
    new_config = {
        "name": "PVOM Testing",
        "new": {
            "perDay": 22,  # 22 new cards per day
            "delays": [1, 10],
            "ints": [1, 4],
            "initialFactor": 2500,
            "bury": False,
            "order": 0,
        },
        "lrn": {
            "delays": [10],
            "perDay": 0,  # 0 learning cards per day
            "perDay": 0,
        },
        "rev": {
            "perDay": 6,  # 6 review cards per day
            "ease4": 1.3,
            "bury": False,
            "hardPenalty": 1.2,
        },
        "timer": {
            "useCurrent": True,
            "maxTaken": 60000,
        },
        "autoplay": {
            "sounds": True,
            "replayQuestion": True,
        },
        "maxTaken": 60000,
        "mod": 0,  # Will be set by Anki
        "usn": -1,
    }

    # Try to save config for the deck
    print(f"\nAttempting to set limits for {deck_name}...")

    # Method 1: Try saveDeckConfig (might work with newer AnkiConnect)
    result = anki_request("saveDeckConfig", {"config": new_config})
    if result and not result.get("error"):
        print("✓ Config created/updated")
        config_id = result.get("result")
        print(f"  Config ID: {config_id}")

        # Now associate this config with the deck
        result = anki_request(
            "setDeckConfigId",
            {"decks": [deck_name], "configId": config_id},
        )
        if result and not result.get("error"):
            print(f"✓ Applied to deck: {deck_name}")
        else:
            print(f"Note: Could not apply config to deck")
            print("  You may need to manually set limits in Anki")

    else:
        # Fallback: Use getDecks and modify manually
        print("\nFallback: Manual limit setting instructions")
        print("=" * 60)
        print(f"In Anki:")
        print(f"1. Right-click on deck: {deck_name}")
        print(f"2. Select 'Options'")
        print(f"3. Set limits to:")
        print(f"   - New cards/day: 22")
        print(f"   - Learning cards/day: 0")
        print(f"   - Reviews/day: 6")
        print(f"4. Save")

    print("\n" + "=" * 60)
    print("After limit adjustment:")
    print("- All 22 PVOM cards can be reviewed in one session")
    print("- No learning queue delays (tests go straight to review)")
    print("- Max 6 reviews/day after initial exposure")


if __name__ == "__main__":
    main()
