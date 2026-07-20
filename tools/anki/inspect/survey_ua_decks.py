#!/usr/bin/env python3
"""Survey all UA::* decks learning status via AnkiConnect."""

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


def get_all_decks():
    """Get list of all decks."""
    result = anki_request("deckNames")
    if result and not result.get("error"):
        return result.get("result", [])
    return []


def get_deck_stats(deck_names):
    """Get stats for multiple decks."""
    if not deck_names:
        return {}
    result = anki_request("deckStats", {"decks": deck_names})
    if result and not result.get("error"):
        return result.get("result", {})
    return {}


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
    print("Ukrainian (UA::*) Decks Learning Status Survey")
    print("=" * 70)

    # Get all decks
    all_decks = get_all_decks()
    ua_decks = [d for d in all_decks if d.startswith("UA::")]

    if not ua_decks:
        print("No UA::* decks found")
        return

    print(f"\nFound {len(ua_decks)} UA decks:\n")

    # Get stats for all UA decks
    deck_stats = get_deck_stats(ua_decks)

    # Collect overall stats
    total_new = 0
    total_learning = 0
    total_review = 0
    total_suspended = 0
    deck_details = []

    for deck_name in sorted(ua_decks):
        stats = deck_stats.get(deck_name, {})
        new_count = stats.get("newCount", 0)
        learning_count = stats.get("lrnCount", 0)
        review_count = stats.get("revCount", 0)

        total_new += new_count
        total_learning += learning_count
        total_review += review_count

        # Get card details for suspended count
        card_ids = get_cards_in_deck(deck_name)
        if card_ids:
            cards = get_cards_info(card_ids)
            suspended_count = sum(1 for c in cards if classify_card(c) == "suspended")
            total_suspended += suspended_count
        else:
            suspended_count = 0

        deck_details.append({
            "name": deck_name,
            "new": new_count,
            "learning": learning_count,
            "review": review_count,
            "suspended": suspended_count,
            "total": len(card_ids),
        })

    # Print per-deck breakdown
    print(f"{'Deck':<40} {'New':>6} {'Learn':>6} {'Review':>6} {'Suspend':>7} {'Total':>6}")
    print("-" * 73)
    for detail in deck_details:
        print(
            f"{detail['name']:<40} {detail['new']:>6} {detail['learning']:>6} "
            f"{detail['review']:>6} {detail['suspended']:>7} {detail['total']:>6}"
        )

    print("-" * 73)
    total_cards = sum(d["total"] for d in deck_details)
    print(
        f"{'TOTAL':<40} {total_new:>6} {total_learning:>6} "
        f"{total_review:>6} {total_suspended:>7} {total_cards:>6}"
    )

    # Analysis
    print("\n" + "=" * 70)
    print("Analysis:")
    print(f"  New cards (not yet studied): {total_new}")
    print(f"  Learning cards (in progress): {total_learning}")
    print(f"  Review cards (scheduled): {total_review}")
    print(f"  Suspended cards: {total_suspended}")
    print(f"  Total cards: {total_cards}")

    if total_learning > 0:
        print(f"\n  Learning queue capacity: {total_learning} cards in active learning")
    else:
        print(f"\n  Learning queue: empty (no cards currently being learned)")

    if total_new > 0:
        daily_new_rate = 20  # Default Anki new cards per day
        days_to_review_all_new = (total_new + daily_new_rate - 1) // daily_new_rate
        print(
            f"  Time to introduce all new cards: ~{days_to_review_all_new} days "
            f"(at {daily_new_rate} new/day)"
        )

    # Recommendations
    print("\nFSRS Considerations:")
    if total_learning > 30:
        print(f"  ⚠ High learning queue ({total_learning} cards) - may slow review workflow")
    if total_new == 0 and total_review < 10:
        print(f"  ⚠ Low review load - consider increasing new card limit for better spacing")
    if total_review > 200:
        print(f"  ⚠ High review load ({total_review} cards) - FSRS working hard")


if __name__ == "__main__":
    main()
