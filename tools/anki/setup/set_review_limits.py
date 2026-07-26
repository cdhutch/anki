#!/usr/bin/env python3
"""
set_review_limits.py — Raise the daily review limit to 9999 for every Anki
deck config preset via AnkiConnect.

Surveys every deck in the collection, prints the current new-cards/day and
reviews/day limits for each config preset, shows the proposed values, asks
for confirmation, and then applies the review-limit change.

New-card limits are shown for reference only and are NOT modified.

Requires: Anki open with AnkiConnect add-on active on port 8765.

Usage:
    python3 tools/anki/set_review_limits.py
"""

import collections
import json
import urllib.request

NEW_REVIEW_LIMIT = 9999


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen("http://localhost:8765", payload) as r:
        result = json.loads(r.read())
    if result.get("error"):
        raise Exception(result["error"])
    return result["result"]


def survey():
    """Return {config_id: (config_obj, [deck_names])} for every deck."""
    all_decks = anki("deckNames")

    configs = {}
    deck_to_config = {}
    for deck in all_decks:
        cfg = anki("getDeckConfig", deck=deck)
        cid = cfg["id"]
        configs[cid] = cfg
        deck_to_config[deck] = cid

    by_config = collections.defaultdict(list)
    for deck, cid in deck_to_config.items():
        by_config[cid].append(deck)

    return {cid: (configs[cid], sorted(decks)) for cid, decks in by_config.items()}


def main():
    try:
        by_config = survey()
    except Exception as e:
        print(f"Could not reach AnkiConnect: {e}")
        print("Make sure Anki is open and the AnkiConnect add-on is installed.")
        return

    if not by_config:
        print("No decks found.")
        return

    to_update = []  # (cid, config, decks, old_rev)
    print("=" * 72)
    print("Current state, by config preset:")
    print("=" * 72)
    for cid, (cfg, decks) in sorted(by_config.items()):
        new_perday = cfg.get("new", {}).get("perDay", "n/a")
        rev_perday = cfg.get("rev", {}).get("perDay", "n/a")
        needs_update = isinstance(rev_perday, int) and rev_perday != NEW_REVIEW_LIMIT

        print(f"\nPreset: \"{cfg['name']}\" (id: {cid})")
        print(f"  Decks using this preset ({len(decks)}):")
        for d in decks:
            print(f"    - {d}")
        print(f"  New cards/day:  current = {new_perday}   proposed = {new_perday} (unchanged)")
        status = "" if needs_update else "  (already at target)"
        print(f"  Reviews/day:    current = {rev_perday}   proposed = {NEW_REVIEW_LIMIT}{status}")

        if needs_update:
            to_update.append((cid, cfg, decks, rev_perday))

    print("\n" + "=" * 72)
    if not to_update:
        print(f"Every preset already has a review limit of {NEW_REVIEW_LIMIT}. Nothing to do.")
        return

    print(f"{len(to_update)} preset(s) will have their review limit raised to {NEW_REVIEW_LIMIT}:")
    for cid, cfg, decks, old_rev in to_update:
        print(f"  \"{cfg['name']}\": {old_rev} -> {NEW_REVIEW_LIMIT}  ({len(decks)} deck(s))")

    answer = input("\nProceed with these changes? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted. No changes made.")
        return

    for cid, cfg, decks, old_rev in to_update:
        cfg["rev"]["perDay"] = NEW_REVIEW_LIMIT
        anki("saveDeckConfig", config=cfg)
        print(f"Updated \"{cfg['name']}\": {old_rev} -> {NEW_REVIEW_LIMIT}")

    print("\nDone.")


if __name__ == "__main__":
    main()
