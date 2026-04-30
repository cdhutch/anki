#!/usr/bin/env python3
"""
deck_config_summary.py — Summarise Anki deck config presets via AnkiConnect.

Usage:
    python3 tools/anki/deck_config_summary.py

At the prompt, press Enter to survey every deck, or type a deck name
(e.g. "B737") to survey that deck and all of its children.

Requires: Anki open with AnkiConnect add-on active on port 8765.
"""

import json
import collections
import urllib.request


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen("http://localhost:8765", payload) as r:
        result = json.loads(r.read())
    if result.get("error"):
        raise Exception(result["error"])
    return result["result"]


def main():
    root = input("Deck name to survey (Enter for all decks): ").strip()

    all_decks = anki("deckNames")

    if root:
        # Include exact match and all children (prefix match with "::")
        target_decks = [
            d for d in all_decks
            if d == root or d.startswith(root + "::")
        ]
        if not target_decks:
            print(f'No decks found matching "{root}".')
            return
    else:
        target_decks = all_decks

    configs = {}       # config_id -> config object
    deck_to_config = {}

    for deck in target_decks:
        cfg = anki("getDeckConfig", deck=deck)
        cid = cfg["id"]
        configs[cid] = cfg
        deck_to_config[deck] = cid

    by_config = collections.defaultdict(list)
    for deck, cid in deck_to_config.items():
        by_config[cid].append(deck)

    for cid, decks in sorted(by_config.items()):
        c = configs[cid]
        new = c.get("new", {})
        rev = c.get("rev", {})
        lapse = c.get("lapse", {})
        print(f"\n{'='*60}")
        print(f"Preset: \"{c['name']}\"  (id: {cid})")
        print(f"  Decks using this preset ({len(decks)}):")
        for d in sorted(decks):
            print(f"    • {d}")
        print(f"  New cards/day:       {new.get('perDay', 'n/a')}")
        print(f"  Reviews/day:         {rev.get('perDay', 'n/a')}")
        print(f"  FSRS enabled:        {c.get('fsrs', False)}")
        print(f"  Desired retention:   {c.get('desiredRetention', 'n/a')}")
        print(f"  FSRS weights:        {'set' if c.get('fsrsWeights') else 'default/empty'}")
        print(f"  Max interval (days): {rev.get('maxIvl', 'n/a')}")
        print(f"  Relearn steps:       {lapse.get('delays', 'n/a')}")
        print(f"  Leech threshold:     {lapse.get('leechFails', 'n/a')}")


if __name__ == "__main__":
    main()
