#!/usr/bin/env python3
"""Check deck hierarchy and config inheritance for UA decks."""

import json
import urllib.request

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
        print(f"AnkiConnect error: {e}")
        return None


def get_deck_info():
    """Get all deck info from Anki."""
    # Unfortunately AnkiConnect doesn't directly expose deck config hierarchy
    # We'll need to inspect the Anki database directly or use workarounds

    # Get all decks
    result = anki_request("deckNames")
    decks = result.get("result", []) if result else []

    print("Deck Hierarchy for UA::")
    print("=" * 70)

    ua_decks = [d for d in decks if d.startswith("UA")]
    ua_decks.sort()

    for deck in ua_decks:
        # Calculate indentation based on :: levels
        parts = deck.split("::")
        indent = "  " * (len(parts) - 1)
        deck_name = parts[-1]

        print(f"{indent}├─ {deck_name}")

    print("\n" + "=" * 70)
    print("Deck Config Issue Analysis:")
    print("=" * 70)

    # The concern: parent deck limits might constrain child decks
    print("\nPotential hierarchy constraints:")
    print("  UA (root)")
    print("    ├─ UA::Recognition")
    print("    │   └─ UA::Recognition::PVOM  ← TESTING HERE")
    print("    │   └─ UA::Recognition::UA→EN")
    print("    │   └─ UA::Recognition::Visual")
    print("    │   └─ UA::Recognition::Grammar")
    print("    └─ UA::Production")

    print("\nThe issue:")
    print("  • If UA::Recognition has limits of 18/0/6")
    print("  • Then PVOM with limits of 22/0/6 will be capped at 18 new cards")
    print("  • Child deck limits cannot exceed parent limits")

    print("\nTo verify config inheritance, check in Anki:")
    print("  1. Right-click UA → Options → check limits")
    print("  2. Right-click UA::Recognition → Options → check limits")
    print("  3. Right-click UA::Recognition::PVOM → Options → check limits")
    print("\nIf PVOM shows 'Use parent config', sibling limits apply.")


def main():
    get_deck_info()

    print("\n" + "=" * 70)
    print("Solution:")
    print("=" * 70)
    print("1. Make sure UA::Recognition::PVOM has its OWN config (not inherited)")
    print("2. If UA::Recognition is capped at 18, increase it to accommodate PVOM")
    print("3. Or set PVOM to use independent limits separate from parent")
    print("\nIn Anki:")
    print("  • Each deck can have independent config or inherit from parent")
    print("  • Set PVOM to have its own independent config with 22/0/6")
    print("  • Check that parent decks don't have stricter limits")


if __name__ == "__main__":
    main()
