#!/usr/bin/env python3
"""
verify_review_randomization.py — Check if Anki is randomizing review cards
or ordering them predictably by due date/interval.

Queries cards due for review and analyzes their ordering to detect patterns
that enable pattern-based answering.

Requires: Anki open with AnkiConnect add-on active on port 8765.

Usage:
    python3 tools/anki/setup/verify_review_randomization.py
"""

import json
import urllib.request
import sys


def anki(action, **params):
    """Call AnkiConnect API."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    try:
        with urllib.request.urlopen("http://localhost:8765", payload) as r:
            result = json.loads(r.read())
        if result.get("error"):
            raise Exception(result["error"])
        return result["result"]
    except Exception as e:
        print(f"AnkiConnect error: {e}")
        sys.exit(1)


def main():
    print("=" * 80)
    print("REVIEW CARD RANDOMIZATION VERIFICATION")
    print("=" * 80)

    # Get all cards due for review
    due_cards = anki("findCards", query="is:due")
    print(f"\nCards due today: {len(due_cards)}")

    if not due_cards:
        print("No cards due. Cannot verify ordering.")
        return

    # Get details on first 30 due cards
    sample_size = min(30, len(due_cards))
    cards_info = anki("cardsInfo", cards=due_cards[:sample_size])

    print(f"\nFirst {sample_size} cards in Anki's review order:")
    print("-" * 80)
    print(f"{'#':3} | {'CardID':15} | {'Due':5} | {'Interval':8} | {'Ease':6}")
    print("-" * 80)

    for i, card in enumerate(cards_info, 1):
        print(f"{i:3d} | {card['cardId']:15d} | {card['due']:5d} | {card['interval']:8d} | {card['factor']:6.0f}")

    # Analyze ordering
    due_dates = [c['due'] for c in cards_info]
    intervals = [c['interval'] for c in cards_info]

    is_sorted_by_due = due_dates == sorted(due_dates)
    is_reverse_sorted = due_dates == sorted(due_dates, reverse=True)

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if is_sorted_by_due:
        print("\n⚠  CARDS ARE ORDERED BY DUE DATE (ascending)")
        print("   Pattern: Reviews appear in predictable sequence each day")
        print("   Risk: High — enables memorizing card position")
    elif is_reverse_sorted:
        print("\n⚠  CARDS ARE ORDERED BY DUE DATE (descending)")
        print("   Pattern: Reviews appear in predictable sequence each day")
        print("   Risk: High — enables memorizing card position")
    else:
        print("\n✓ Cards appear randomized (not sorted by due date)")
        print("   Pattern: Order varies between sessions")
        print("   Risk: Low — harder to memorize by position")

    # Check for interval-based sorting
    is_sorted_by_interval = intervals == sorted(intervals)
    if is_sorted_by_interval and not (is_sorted_by_due or is_reverse_sorted):
        print("\n⚠  CARDS MAY BE ORDERED BY INTERVAL")
        print("   Pattern: Shorter intervals reviewed first")
        print("   Risk: Medium — some predictability")

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("""
Review randomization is controlled by Anki's scheduler, not deck config.

To increase randomness:
1. Study at different times each day (different cards due)
2. Mix decks: don't review entire deck at once
3. Use custom shuffle add-ons (if available)
4. Study on irregular schedule
    """)


if __name__ == "__main__":
    main()
