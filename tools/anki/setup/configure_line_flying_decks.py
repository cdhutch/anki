#!/usr/bin/env python3
"""Configure Anki decks for line flying (non-training mode).

Enables only the specified decks and suspends all others.
Additionally suspends any notes tagged with 'always_hide'.

Usage:
  python tools/anki/setup/configure_line_flying_decks.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402


# Decks to enable for line flying (full B737-prefixed paths)
ENABLED_DECKS = [
    "B737::Core::Limits",  # will match all subdecks
    "B737::Core::Mnemonics",
    "B737::Core::QRC",
    "B737::Core::Procedures::Inflight_Maneuvers",
]


def main() -> int:
    url = "http://127.0.0.1:8765"

    print("Configuring B737 decks for line flying (non-training mode)...\n")

    # Fetch all decks
    try:
        decks_response = anki_request("deckNames", {}, url=url)
    except Exception as e:
        print(f"Error fetching decks: {e}", file=sys.stderr)
        return 1

    if not decks_response:
        print("No decks found", file=sys.stderr)
        return 1

    # Filter to only B737 decks
    b737_decks = [d for d in decks_response if d == "B737" or d.startswith("B737::")]
    print(f"B737 decks: {len(b737_decks)}\n")

    # Determine which decks to enable/suspend
    decks_to_enable = set()
    decks_to_suspend = set()

    for deck_name in b737_decks:
        should_enable = False
        for enabled_pattern in ENABLED_DECKS:
            if deck_name == enabled_pattern or deck_name.startswith(enabled_pattern + "::"):
                should_enable = True
                break

        if should_enable:
            decks_to_enable.add(deck_name)
        else:
            decks_to_suspend.add(deck_name)

    # Remove parent decks from suspension list if any of their children are enabled
    # (This prevents suspending all cards when suspending a parent deck)
    decks_to_suspend_filtered = set()
    for deck in decks_to_suspend:
        # Check if this deck is a parent of any enabled deck
        has_enabled_child = False
        for enabled_deck in decks_to_enable:
            if enabled_deck.startswith(deck + "::"):
                has_enabled_child = True
                break

        # Only suspend if it has no enabled children
        if not has_enabled_child:
            decks_to_suspend_filtered.add(deck)

    decks_to_suspend = decks_to_suspend_filtered

    print("Decks to enable:")
    for deck in sorted(decks_to_enable):
        print(f"  ✓ {deck}")

    print(f"\nDecks to suspend ({len(decks_to_suspend)}):")
    for deck in sorted(decks_to_suspend):
        print(f"  ✗ {deck}")

    # Step 1: Unsuspend all B737 cards (clean slate)
    print("\nStep 1: Unsuspending all B737 cards (clean slate)...")
    try:
        all_b737_cards = anki_request("findCards", {"query": "deck:B737"}, url=url)
        if all_b737_cards:
            print(f"  Found {len(all_b737_cards)} B737 cards")
            # Batch unsuspend in chunks to avoid hitting API limits
            batch_size = 200
            total_unsuspended = 0
            for i in range(0, len(all_b737_cards), batch_size):
                batch = all_b737_cards[i : i + batch_size]
                anki_request("unsuspend", {"cards": batch}, url=url)
                total_unsuspended += len(batch)
                print(f"  Unsuspended {total_unsuspended}/{len(all_b737_cards)} cards...")
            print(f"  ✓ Unsuspended all {len(all_b737_cards)} B737 cards")
        else:
            print("  No B737 cards found")
    except Exception as e:
        print(f"Error unsuspending B737 cards: {e}", file=sys.stderr)
        return 1

    # Step 2: Suspend non-enabled B737 decks
    print("\nStep 2: Suspending non-enabled B737 decks...")
    try:
        total_to_suspend = 0
        for deck_name in decks_to_suspend:
            cards_response = anki_request("findCards", {"query": f"deck:\"{deck_name}\""}, url=url)
            if cards_response:
                card_ids = cards_response
                if card_ids:
                    total_to_suspend += len(card_ids)
                    # Batch suspend in chunks
                    batch_size = 200
                    for i in range(0, len(card_ids), batch_size):
                        batch = card_ids[i : i + batch_size]
                        anki_request("suspend", {"cards": batch}, url=url)
                    print(f"  Suspended {len(card_ids)} cards in: {deck_name}")
        print(f"  ✓ Suspended {total_to_suspend} cards in non-enabled decks")
    except Exception as e:
        print(f"Error suspending B737 decks: {e}", file=sys.stderr)
        return 1

    # Step 3: Suspend notes tagged 'always_hide' within B737 decks
    print("\nStep 3: Suspending notes tagged 'always_hide' (B737 scope only)...")
    try:
        always_hide_cards = anki_request("findCards", {"query": "deck:B737 tag:always_hide"}, url=url)
        if always_hide_cards:
            # Batch suspend
            batch_size = 200
            for i in range(0, len(always_hide_cards), batch_size):
                batch = always_hide_cards[i : i + batch_size]
                anki_request("suspend", {"cards": batch}, url=url)
            print(f"  ✓ Suspended {len(always_hide_cards)} cards with 'always_hide' tag")
        else:
            print("  No cards found with 'always_hide' tag in B737")
    except Exception as e:
        print(f"Error suspending 'always_hide' cards: {e}", file=sys.stderr)
        return 1

    print("\n✓ Configuration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
