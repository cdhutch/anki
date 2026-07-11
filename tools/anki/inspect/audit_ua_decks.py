#!/usr/bin/env python3
"""Audit current UA deck structure and FSRS config assignment.

Lists all decks, counts UA cards in each, and shows which config is assigned.

Usage
-----
  python tools/anki/inspect/audit_ua_decks.py
  python tools/anki/inspect/audit_ua_decks.py --url http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default="http://127.0.0.1:8765", help="AnkiConnect URL")
    args = ap.parse_args()

    url = args.url

    print("Auditing UA deck structure and FSRS config assignment...\n")

    # Get all decks
    try:
        all_decks = anki_request("deckNames", {}, url=url) or []
    except Exception as e:
        print(f"ERROR fetching deck names: {e}", file=sys.stderr)
        return 1

    # Filter to UA-related decks
    ua_decks = sorted([d for d in all_decks if "UA" in d or "Ukrainian" in d])

    if not ua_decks:
        print("No UA-related decks found.")
        return 0

    print(f"Found {len(ua_decks)} UA-related deck(s):\n")

    total_ua_cards = 0

    for deck in ua_decks:
        # Count cards in this deck
        try:
            card_ids = anki_request("findCards", {"query": f"deck:{deck}"}, url=url) or []
            card_count = len(card_ids)
        except Exception as e:
            print(f"  ERROR counting cards in '{deck}': {e}", file=sys.stderr)
            card_count = 0

        # Get deck config
        try:
            config = anki_request("getDeckConfig", {"deck": deck}, url=url)
            config_name = config.get("name", "UNKNOWN") if config else "NO CONFIG"
            config_id = config.get("id", "?") if config else "?"
            desired_retention = config.get("desiredRetention", "?") if config else "?"
        except Exception as e:
            print(f"  ERROR getting config for '{deck}': {e}", file=sys.stderr)
            config_name = "ERROR"
            config_id = "?"
            desired_retention = "?"

        print(f"Deck: {deck}")
        print(f"  Cards: {card_count}")
        print(f"  Config: '{config_name}' (id={config_id})")
        print(f"  Desired retention: {desired_retention}")
        print()

        total_ua_cards += card_count

    print(f"Total UA cards across all decks: {total_ua_cards}\n")

    # Summary of configs
    print("─" * 60)
    print("Summary: Decks and Assigned Configs")
    print("─" * 60)
    for deck in ua_decks:
        try:
            config = anki_request("getDeckConfig", {"deck": deck}, url=url)
            config_name = config.get("name", "?") if config else "?"
            print(f"{deck:50s} → {config_name}")
        except Exception:
            print(f"{deck:50s} → ERROR")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
