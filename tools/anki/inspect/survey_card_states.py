#!/usr/bin/env python3
"""Survey card states (new, learning, review, suspended) by deck.

Shows learning queue status for all decks.
"""

import json
import urllib.request
import sys
from collections import defaultdict

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


def count_cards_by_state(deck_name):
    """Count cards in each state for a deck."""
    counts = {
        "new": 0,
        "learning": 0,
        "review": 0,
        "suspended": 0,
    }

    # Find new cards
    result = anki_request("findCards", {"query": f"deck:\"{deck_name}\" is:new"})
    if result and not result.get("error"):
        counts["new"] = len(result.get("result", []))

    # Find learning cards
    result = anki_request("findCards", {"query": f"deck:\"{deck_name}\" is:learning"})
    if result and not result.get("error"):
        counts["learning"] = len(result.get("result", []))

    # Find review cards
    result = anki_request("findCards", {"query": f"deck:\"{deck_name}\" is:review"})
    if result and not result.get("error"):
        counts["review"] = len(result.get("result", []))

    # Find suspended cards
    result = anki_request("findCards", {"query": f"deck:\"{deck_name}\" is:suspended"})
    if result and not result.get("error"):
        counts["suspended"] = len(result.get("result", []))

    return counts


def main():
    print("Card State Survey")
    print("=" * 120)

    # Test connection
    version_result = anki_request("version")
    if not version_result:
        print("Error: Cannot connect to AnkiConnect. Make sure Anki is running.")
        sys.exit(1)

    print(f"✓ Connected to AnkiConnect (version: {version_result.get('result')})\n")

    # Get all decks
    decks_result = anki_request("deckNames")
    if not decks_result or decks_result.get("error"):
        print(f"Error getting deck names: {decks_result.get('error') if decks_result else 'No response'}")
        sys.exit(1)

    all_decks = sorted(decks_result.get("result", []))

    # Collect stats
    deck_stats = {}
    totals = {"new": 0, "learning": 0, "review": 0, "suspended": 0}

    for deck_name in all_decks:
        counts = count_cards_by_state(deck_name)
        deck_stats[deck_name] = counts
        for key in totals:
            totals[key] += counts[key]

    # Print with hierarchy indentation
    print(f"{'Deck':<50} {'New':<8} {'Learning':<10} {'Review':<8} {'Suspended':<10} {'Total':<8}")
    print("-" * 120)

    for deck_name in all_decks:
        counts = deck_stats[deck_name]
        total = sum(counts.values())

        # Calculate indentation based on :: depth
        depth = deck_name.count("::") if deck_name != "Default" else 0
        indent = "  " * depth
        display_name = indent + deck_name.split("::")[-1]

        print(
            f"{display_name:<50} {counts['new']:<8} {counts['learning']:<10} "
            f"{counts['review']:<8} {counts['suspended']:<10} {total:<8}"
        )

    print("-" * 120)
    grand_total = sum(totals.values())
    print(
        f"{'TOTAL':<50} {totals['new']:<8} {totals['learning']:<10} "
        f"{totals['review']:<8} {totals['suspended']:<10} {grand_total:<8}"
    )


if __name__ == "__main__":
    main()
