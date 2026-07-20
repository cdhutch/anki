#!/usr/bin/env python3
"""Debug saveDeckConfig to see what's happening with preset creation."""

import json
import urllib.request
import sys
import time

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
    print("Debugging saveDeckConfig")
    print("=" * 80)

    # Step 1: Get the UA FSRS config as a template
    print("\n1. Getting UA FSRS config as template...")
    result = anki_request("getDeckConfig", {"deck": "UA"})

    if not result or result.get("error"):
        print(f"Error: {result.get('error') if result else 'No response'}")
        return

    template_config = result.get("result")
    print(f"   Config name: {template_config.get('name')}")
    print(f"   Config ID: {template_config.get('id')}")
    print(f"   Current limits: {template_config.get('new', {}).get('perDay')} new / {template_config.get('rev', {}).get('perDay')} review")

    # Step 2: Create a new config based on the template with a new unique ID
    print("\n2. Creating new test preset...")
    new_config = template_config.copy()
    # Generate a new unique ID (Anki uses millisecond timestamps)
    new_config_id = int(time.time() * 1000)
    new_config["id"] = new_config_id
    new_config["name"] = "TEST_Preset_Creation"
    new_config["new"]["perDay"] = 99
    new_config["rev"]["perDay"] = 99

    print(f"   Sending config with name: {new_config['name']}")
    print(f"   New config ID: {new_config_id}")
    print(f"   Target limits: 99 new / 99 review")
    print(f"   Config has 'id' field: {'id' in new_config}")

    save_result = anki_request("saveDeckConfig", {"config": new_config})
    print(f"\n   saveDeckConfig result: {save_result}")

    if save_result and not save_result.get("error"):
        new_config_id = save_result.get("result")
        print(f"   ✓ Created with ID: {new_config_id}")

        # Step 3: Verify the preset was created
        print("\n3. Verifying preset was created...")
        result = anki_request("getDeckConfig", {"deck": "Default"})
        if result and not result.get("error"):
            verify_config = result.get("result")
            print(f"   Config name: {verify_config.get('name')}")
            print(f"   Config ID: {verify_config.get('id')}")
            print(f"   Limits: {verify_config.get('new', {}).get('perDay')} new / {verify_config.get('rev', {}).get('perDay')} review")

        # Step 4: List all presets to see if new one appears
        print("\n4. Listing all presets after creation...")
        all_decks = anki_request("deckNames").get("result", [])
        presets_found = {}
        for deck in ["Default", "UA"]:
            if deck in all_decks:
                result = anki_request("getDeckConfig", {"deck": deck})
                if result and not result.get("error"):
                    config = result.get("result", {})
                    config_id = config.get("id")
                    config_name = config.get("name")
                    if config_id not in presets_found:
                        presets_found[config_id] = config_name
                        print(f"   • {config_name} (ID: {config_id})")

    else:
        error = save_result.get("error") if save_result else "No response"
        print(f"   ✗ Error: {error}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
