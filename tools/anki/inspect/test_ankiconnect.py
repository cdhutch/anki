#!/usr/bin/env python3
"""Test AnkiConnect connectivity and config API."""

import json
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"

def anki_request(action, params=None):
    """Send request to AnkiConnect."""
    request_body = {"action": action, "version": 6}
    if params:
        request_body["params"] = params

    print(f"Request: {action}")
    print(f"  Params: {params}")

    try:
        response = urllib.request.urlopen(
            urllib.request.Request(
                ANKI_URL,
                data=json.dumps(request_body).encode("utf-8"),
            )
        )
        result = json.loads(response.read())
        print(f"  Response: {result}\n")
        return result
    except Exception as e:
        print(f"  ERROR: {e}\n")
        return None

print("Testing AnkiConnect\n")

# Test 1: Check version
print("1. Testing version...")
anki_request("version")

# Test 2: Get all deck names
print("2. Getting all deck names...")
result = anki_request("deckNames")
deck_names = result.get("result", []) if result and not result.get("error") else []

# Test 3: Get config for UA deck
if "UA" in deck_names:
    print("3. Getting config for UA deck...")
    result = anki_request("getDeckConfig", {"deck": "UA"})
    if result and not result.get("error"):
        config = result.get("result")
        print(f"UA deck config structure:")
        print(json.dumps(config, indent=2))

# Test 4: List all UA decks
print("4. All UA-related decks:")
ua_decks = sorted([d for d in deck_names if d.startswith("UA")])
for deck in ua_decks:
    print(f"  - {deck}")
