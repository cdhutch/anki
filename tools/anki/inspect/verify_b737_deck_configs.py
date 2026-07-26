#!/usr/bin/env python3
"""Read-only check: which config (options group) does each B737 deck use today?

Prints deck -> config id/name for every deck listed in
domains/b737/anki/config/deck_limits.yaml, then flags any config id that's
shared by more than one deck -- especially when those decks are supposed to
end up with DIFFERENT new/review limits (e.g. one active, one suspended).

update_b737_deck_limits.py mutates a deck's CURRENT config in place
(getDeckConfig -> edit -> saveDeckConfig, no clone step) -- if two decks with
different target limits share a config id, running that script would make
whichever deck it processes last win, silently leaving the other deck wrong.
This script makes no writes; it's safe to run any time.
"""

import json
import sys
import urllib.request
from pathlib import Path

import yaml

ANKI_URL = "http://127.0.0.1:8765"
# Path: tools/anki/inspect/verify_b737_deck_configs.py -> repo root is 4 levels up
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "domains/b737/anki/config/deck_limits.yaml"


def anki_request(action, params=None):
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
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def load_deck_limits():
    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config.get("decks", {})


def main():
    print("B737 Deck -> Config (Preset) Mapping")
    print("=" * 70)

    deck_limits = load_deck_limits()

    # deck_name -> {config_id, config_name, target_new, target_review, suspended}
    rows = []
    for deck_name, limits in deck_limits.items():
        result = anki_request("getDeckConfig", {"deck": deck_name})
        if not result or result.get("error"):
            err = result.get("error") if result else "No response"
            print(f"\n{deck_name}\n  ✗ Failed to get config: {err}")
            continue

        config = result.get("result")
        if not config:
            print(f"\n{deck_name}\n  ✗ No config returned (deck may not exist -- check exact name)")
            continue

        rows.append({
            "deck": deck_name,
            "config_id": config.get("id"),
            "config_name": config.get("name"),
            "target_new": limits.get("new"),
            "target_review": limits.get("review"),
            "suspended": limits.get("suspended", False),
        })

    # Print per-deck table
    print(f"\n{'Deck':<45} {'Config ID':<12} {'Config Name':<20} {'Target N/R':<12} {'Suspended?'}")
    print("-" * 110)
    for row in rows:
        target = f"{row['target_new']}/{row['target_review']}"
        print(f"{row['deck']:<45} {str(row['config_id']):<12} {str(row['config_name']):<20} {target:<12} {row['suspended']}")

    # Group by config_id, flag conflicts
    by_config = {}
    for row in rows:
        by_config.setdefault(row["config_id"], []).append(row)

    print("\n" + "=" * 70)
    print("Shared-config analysis")
    print("=" * 70)

    any_conflict = False
    for config_id, members in by_config.items():
        if len(members) <= 1:
            continue
        targets = {(m["target_new"], m["target_review"], m["suspended"]) for m in members}
        conflict = len(targets) > 1
        if conflict:
            any_conflict = True
        flag = "⚠ CONFLICT -- decks want different limits but share this config" if conflict else "same target, sharing is harmless"
        print(f"\nConfig ID {config_id} ({members[0]['config_name']}) is shared by {len(members)} decks -- {flag}")
        for m in members:
            print(f"    {m['deck']}  ->  target {m['target_new']}/{m['target_review']}, suspended={m['suspended']}")

    print("\n" + "=" * 70)
    if any_conflict:
        print("RESULT: at least one shared config has decks with CONFLICTING target limits.")
        print("Running update_b737_deck_limits.py as-is would leave some of these decks wrong")
        print("(whichever deck in the group is processed last determines the final shared value).")
        print("Fix needed before running: clone a dedicated config per deck (or per target-limit")
        print("group) instead of mutating the shared config in place.")
    else:
        print("RESULT: no conflicting shared configs found. Safe to run update_b737_deck_limits.py.")


if __name__ == "__main__":
    main()
