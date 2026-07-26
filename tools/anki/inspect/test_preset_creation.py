#!/usr/bin/env python3
"""Test different approaches to creating deck presets via AnkiConnect."""

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
    print("Testing Preset Creation Approaches")
    print("=" * 80)

    # Get a template config
    print("\n1. Getting template config from UA deck...")
    result = anki_request("getDeckConfig", {"deck": "UA"})
    if not result or result.get("error"):
        print(f"   Error: {result.get('error') if result else 'No response'}")
        return

    template_config = result.get("result")
    print(f"   ✓ Got config: {template_config.get('name')} (ID: {template_config.get('id')})")

    # Approach 1: Remove id field entirely
    print("\n2. Approach 1: Remove 'id' field, set new name, try saveDeckConfig...")
    config1 = template_config.copy()
    del config1["id"]
    config1["name"] = "TEST_No_ID"
    config1["new"]["perDay"] = 50
    config1["rev"]["perDay"] = 100

    print(f"   Config has 'id' field: {'id' in config1}")
    result1 = anki_request("saveDeckConfig", {"config": config1})
    print(f"   Result: {result1}")

    # Approach 2: Set id to 0 or 1
    print("\n3. Approach 2: Set 'id' to 0, set new name, try saveDeckConfig...")
    config2 = template_config.copy()
    config2["id"] = 0
    config2["name"] = "TEST_ID_Zero"
    config2["new"]["perDay"] = 50
    config2["rev"]["perDay"] = 100

    result2 = anki_request("saveDeckConfig", {"config": config2})
    print(f"   Result: {result2}")

    # Approach 3: Use a very large timestamp
    print("\n4. Approach 3: Use large timestamp ID, set new name, try saveDeckConfig...")
    config3 = template_config.copy()
    config3["id"] = int(time.time() * 1000) + 10000000
    config3["name"] = "TEST_Large_Timestamp"
    config3["new"]["perDay"] = 50
    config3["rev"]["perDay"] = 100

    print(f"   New ID: {config3['id']}")
    result3 = anki_request("saveDeckConfig", {"config": config3})
    print(f"   Result: {result3}")

    # Approach 4: Check if there's a different action for cloning
    print("\n5. Approach 4: Check for alternative AnkiConnect actions...")
    # Try to see if version action works to confirm connection
    version_result = anki_request("version")
    print(f"   AnkiConnect version: {version_result.get('result') if version_result else 'No response'}")

    # Try some hypothetical actions
    for action in ["cloneDeckConfig", "newDeckConfig", "addDeckConfig", "duplicateDeckConfig"]:
        test_result = anki_request(action, {"name": "TEST"})
        if test_result and not test_result.get("error"):
            print(f"   ✓ Action exists: {action}")
        elif test_result and "not implemented" not in str(test_result.get("error", "")).lower():
            print(f"   ~ Action {action} returned: {test_result.get('error', 'unknown')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
