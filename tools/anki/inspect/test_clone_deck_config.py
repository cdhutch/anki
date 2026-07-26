#!/usr/bin/env python3
"""Diagnostic: Test what cloneDeckConfigId actually returns."""

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
    print("Testing cloneDeckConfigId return value")
    print("=" * 80)

    # Test connection
    version_result = anki_request("version")
    print(f"AnkiConnect version: {version_result}")

    # Test cloneDeckConfigId
    print("\nCalling cloneDeckConfigId...")
    clone_result = anki_request("cloneDeckConfigId",
                                {"name": "TEST_Diagnostic", "cloneFrom": 1})

    print(f"\nRaw response:")
    print(f"  Type: {type(clone_result)}")
    print(f"  Value: {clone_result}")

    if isinstance(clone_result, dict):
        print(f"\nResponse fields:")
        print(f"  result: {clone_result.get('result')}")
        print(f"  error: {clone_result.get('error')}")

        config_id = clone_result.get("result")
        print(f"\nExtracted config_id: {config_id}")
        print(f"  Type: {type(config_id)}")

        if isinstance(config_id, int):
            print(f"  ✓ Valid numeric ID")
        else:
            print(f"  ✗ NOT a numeric ID!")


if __name__ == "__main__":
    main()
