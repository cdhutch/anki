#!/usr/bin/env python3
"""Diagnose card states by inspecting actual queue values."""

import json
import urllib.request
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
        return json.loads(response.read())
    except Exception as e:
        print(f"AnkiConnect error: {e}")
        return None


def get_cards_in_deck(deck_name):
    """Find all cards in a deck."""
    result = anki_request("findCards", {"query": f"deck:\"{deck_name}\""})
    if result and not result.get("error"):
        return result.get("result", [])
    return []


def get_cards_info(card_ids):
    """Get detailed info about cards."""
    if not card_ids:
        return []
    result = anki_request("cardsInfo", {"cards": card_ids})
    if result and not result.get("error"):
        return result.get("result", [])
    return []


def main():
    print("Card State Diagnosis")
    print("=" * 70)

    # Check PVOM deck in detail
    print("\nUA::Recognition::PVOM Deck Diagnosis:")
    card_ids = get_cards_in_deck("UA::Recognition::PVOM")
    print(f"  Found {len(card_ids)} cards")

    if card_ids:
        cards = get_cards_info(card_ids)

        # Collect queue value counts
        queue_counts = defaultdict(int)
        queue_details = defaultdict(list)

        for card in cards:
            queue = card.get("queue", "unknown")
            note_id = card.get("noteId", "unknown")
            queue_counts[queue] += 1
            queue_details[queue].append(note_id)

        print("\n  Queue value distribution:")
        for queue in sorted(queue_counts.keys(), key=str):
            count = queue_counts[queue]
            print(f"    queue={queue}: {count} cards")

            # Map queue values
            if queue == 0:
                queue_type = "(NEW)"
            elif queue == 1:
                queue_type = "(LEARNING)"
            elif queue == 2:
                queue_type = "(REVIEW)"
            elif queue == 3:
                queue_type = "(DAY LEARNING)"
            elif queue == -1:
                queue_type = "(SUSPENDED)"
            else:
                queue_type = f"(UNKNOWN: {queue})"

            print(f"      {queue_type}")

            # Show first 3 card examples
            examples = queue_details[queue][:3]
            for note_id in examples:
                print(f"        - Note {note_id}")

        # Check for cards with no interval (brand new)
        print("\n  Card interval analysis (first 5 cards):")
        for card in cards[:5]:
            card_id = card.get("cardId")
            interval = card.get("interval", 0)
            due = card.get("due")
            mod = card.get("mod")
            print(f"    Card {card_id}: interval={interval}, due={due}, mod={mod}")

    # Check other decks
    print("\n" + "=" * 70)
    print("\nOther Recognition decks sample:")

    for deck_name in ["UA::Recognition::UA→EN", "UA::Recognition::Visual"]:
        card_ids = get_cards_in_deck(deck_name)
        if card_ids:
            cards = get_cards_info(card_ids[:3])  # Just first 3
            queue_counts = defaultdict(int)
            for card in cards:
                queue = card.get("queue")
                queue_counts[queue] += 1

            print(f"\n  {deck_name}:")
            print(f"    Sample queue values: {dict(queue_counts)}")


if __name__ == "__main__":
    main()
