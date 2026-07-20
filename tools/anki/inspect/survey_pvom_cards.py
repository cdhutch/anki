#!/usr/bin/env python3
"""Survey PVOM card learning status via AnkiConnect."""

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


def get_deck_stats(deck_name):
    """Get deck statistics."""
    result = anki_request("deckStats", {"decks": [deck_name]})
    if result and not result.get("error"):
        return result.get("result", {}).get(deck_name, {})
    return None


def get_pvom_cards():
    """Find all PVOM cards."""
    result = anki_request("findCards", {"query": "deck:UA::Recognition::PVOM"})
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


def classify_card(card_info):
    """Classify card as new/learning/review."""
    queue = card_info.get("queue", -1)
    # Anki queue values: -1=suspended, 0=new, 1=learning, 2=review, 3=day learning
    if queue == 0:
        return "new"
    elif queue == 1:
        return "learning"
    elif queue == 2:
        return "review"
    elif queue == 3:
        return "day_learning"
    else:
        return "suspended"


def main():
    print("PVOM Card Learning Status Survey")
    print("=" * 60)

    # Get deck stats
    print("\nDeck Stats:")
    stats = get_deck_stats("UA::Recognition::PVOM")
    if stats:
        new_count = stats.get("newCount", 0)
        learning_count = stats.get("lrnCount", 0)
        review_count = stats.get("revCount", 0)
        print(f"  New: {new_count}")
        print(f"  Learning: {learning_count}")
        print(f"  Review: {review_count}")
    else:
        print("  Could not retrieve deck stats")

    # Get card details
    print("\nCard Details:")
    card_ids = get_pvom_cards()
    print(f"  Total PVOM cards: {len(card_ids)}")

    if card_ids:
        cards = get_cards_info(card_ids)

        # Classify cards
        new_cards = []
        learning_cards = []
        review_cards = []
        day_learning_cards = []
        suspended_cards = []

        for card in cards:
            card_type = classify_card(card)
            card_id = card.get("cardId", "unknown")
            note_id = card.get("noteId", "unknown")
            due = card.get("due", "")

            if card_type == "new":
                new_cards.append((card_id, note_id, due))
            elif card_type == "learning":
                learning_cards.append((card_id, note_id, due))
            elif card_type == "review":
                review_cards.append((card_id, note_id, due))
            elif card_type == "day_learning":
                day_learning_cards.append((card_id, note_id, due))
            else:
                suspended_cards.append((card_id, note_id, due))

        print(f"\n  New: {len(new_cards)}")
        print(f"  Learning: {len(learning_cards)}")
        print(f"  Review: {len(review_cards)}")
        print(f"  Day Learning: {len(day_learning_cards)}")
        print(f"  Suspended: {len(suspended_cards)}")

        # Show learning cards details
        if learning_cards:
            print(f"\n  Learning Cards (showing first 5):")
            for card_id, note_id, due in learning_cards[:5]:
                print(f"    Card {card_id}: due in {due} minutes")

        if review_cards:
            print(f"\n  Review Cards (showing first 5):")
            for card_id, note_id, due in review_cards[:5]:
                print(f"    Card {card_id}: due in {due} days")

        # Summary
        print("\n" + "=" * 60)
        print(f"Summary: {len(new_cards)} new, {len(learning_cards)} learning, {len(review_cards)} review")
        print(f"Ready to review today: {len(review_cards)} cards")


if __name__ == "__main__":
    main()
