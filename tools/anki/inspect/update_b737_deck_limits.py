#!/usr/bin/env python3
"""Update B737 deck limits by modifying existing deck configs via AnkiConnect.

Reads deck limit configuration from domains/b737/anki/config/deck_limits.yaml

Shared-config safety (2026-07-22): confirmed via verify_b737_deck_configs.py
that some B737 decks share an Anki "options group" (config) with OTHER decks
that want a DIFFERENT new/review target -- e.g. "B737 FSRS Core" is shared by
2 active decks wanting 0/200 and 4 suspended decks wanting 0/0. Naively
mutating a shared config in place (the old approach: getDeckConfig -> edit ->
saveDeckConfig) would silently change the limits for every deck on that
config, not just the one being processed -- see the AnkiConnect footgun on
shared deck configs already documented in CLAUDE-known-issues.md.

To avoid this: before writing anything, do a read-only pass to find config
ids shared by decks with conflicting targets. Any active deck whose current
config is conflicted gets moved to a freshly cloned, dedicated config
(cloneDeckConfigId + setDeckConfigId + getDeckConfig + saveDeckConfig -- the
same clone-based pattern already used elsewhere in this repo for shared
AnkiConnect config objects). Decks sharing the SAME target still share one
new config with each other -- only the conflicting group gets split off.
Decks whose config isn't shared, or is shared only by decks wanting the
identical target, are still updated in place. Suspended decks are still
never written to.
"""

import json
import sys
import urllib.request
from pathlib import Path

import yaml

ANKI_URL = "http://127.0.0.1:8765"
# Path: tools/anki/inspect/update_b737_deck_limits.py -> repo root is 4 levels up
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "domains/b737/anki/config/deck_limits.yaml"


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


def load_config():
    """Load deck limits from YAML config file."""
    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    return config.get("decks", {})


def find_conflicted_config_ids(deck_limits):
    """Read-only pass: which config ids are shared by decks that want
    different (new, review, suspended) targets? Mirrors the analysis in
    verify_b737_deck_configs.py. Returns (deck_name -> current config dict,
    set of conflicted config ids)."""
    deck_configs = {}
    signatures_by_config = {}

    for deck_name, limits in deck_limits.items():
        result = anki_request("getDeckConfig", {"deck": deck_name})
        if not result or result.get("error") or not result.get("result"):
            continue
        config = result["result"]
        config_id = config.get("id")
        deck_configs[deck_name] = config
        sig = (limits.get("new"), limits.get("review"), limits.get("suspended", False))
        signatures_by_config.setdefault(config_id, set()).add(sig)

    conflicted = {cid for cid, sigs in signatures_by_config.items() if len(sigs) > 1}
    return deck_configs, conflicted


def update_deck_limits():
    """Update limits for specified decks."""
    print("Updating B737 Deck Limits via AnkiConnect")
    print("=" * 70)

    deck_limits = load_config()

    print("\nChecking for shared configs with conflicting targets...")
    deck_configs, conflicted = find_conflicted_config_ids(deck_limits)
    if conflicted:
        print(f"  ⚠ {len(conflicted)} config(s) shared by decks wanting different limits --")
        print(f"    affected active decks will be moved to a dedicated cloned config.")
    else:
        print(f"  ✓ No conflicts -- safe to update configs in place.")

    # Cache: (new, review) target -> newly-cloned config id, so decks that
    # share the same target still share ONE new config with each other.
    cloned_config_cache = {}

    for deck_name, limits in deck_limits.items():
        # Skip suspended decks
        if limits.get("suspended", False):
            tags = limits.get("tags", [])
            tag_str = f" | tags: {', '.join(tags)}" if tags else ""
            print(f"\n{deck_name} [SUSPENDED - skipped]{tag_str}")
            continue

        print(f"\n{deck_name}")
        print(f"  Target: {limits['new']} new / {limits['review']} review")

        # Show tags if present
        tags = limits.get("tags", [])
        if tags:
            print(f"  Tags: {', '.join(tags)}")

        config = deck_configs.get(deck_name)
        if not config:
            print(f"  ✗ No config on file for this deck (check exact deck name)")
            continue

        # Show current limits
        current_new = config.get("new", {}).get("perDay", "?")
        current_rev = config.get("rev", {}).get("perDay", "?")
        print(f"  Current: {current_new} new / {current_rev} review")

        original_config_id = config.get("id")
        target_key = (limits["new"], limits["review"])

        if original_config_id in conflicted:
            # This deck's current config is shared with decks that want a
            # different target -- don't mutate it in place.
            if target_key in cloned_config_cache:
                new_config_id = cloned_config_cache[target_key]
                assign_result = anki_request("setDeckConfigId", {"decks": [deck_name], "configId": new_config_id})
                if assign_result and not assign_result.get("error"):
                    print(f"  → Shared config conflicts with other decks; applied existing cloned config (ID: {new_config_id})")
                else:
                    error = assign_result.get("error") if assign_result else "No response"
                    print(f"  ✗ Failed to apply cloned config: {error}")
                continue

            # First deck to need this target this run: clone + configure it.
            clone_name = f"{config.get('name')} ({limits['new']}n_{limits['review']}r)"
            clone_result = anki_request("cloneDeckConfigId", {"cloneFrom": original_config_id, "name": clone_name})
            if not clone_result or clone_result.get("error") or not clone_result.get("result"):
                err = clone_result.get("error") if clone_result else "No response"
                print(f"  ✗ Failed to clone config: {err}")
                continue
            new_config_id = clone_result["result"]

            assign_result = anki_request("setDeckConfigId", {"decks": [deck_name], "configId": new_config_id})
            if not assign_result or assign_result.get("error"):
                err = assign_result.get("error") if assign_result else "No response"
                print(f"  ✗ Failed to apply cloned config to deck: {err}")
                continue

            fresh = anki_request("getDeckConfig", {"deck": deck_name})
            if not fresh or fresh.get("error") or not fresh.get("result"):
                print(f"  ✗ Failed to re-fetch cloned config for edit")
                continue
            new_config = fresh["result"]
            new_config["new"]["perDay"] = limits["new"]
            new_config["rev"]["perDay"] = limits["review"]
            save_result = anki_request("saveDeckConfig", {"config": new_config})
            if save_result and not save_result.get("error"):
                cloned_config_cache[target_key] = new_config_id
                print(f"  → Shared config conflicts with other decks; cloned + applied new config '{clone_name}' (ID: {new_config_id})")
            else:
                error = save_result.get("error") if save_result else "No response"
                print(f"  ✗ Failed to save cloned config: {error}")
            continue

        # No conflict -- safe to edit this deck's current config in place.
        config["new"]["perDay"] = limits["new"]
        config["rev"]["perDay"] = limits["review"]

        save_result = anki_request("saveDeckConfig", {"config": config})

        if save_result and not save_result.get("error"):
            print(f"  ✓ Config saved (ID: {original_config_id})")

            apply_result = anki_request("setDeckConfigId", {"decks": [deck_name], "configId": original_config_id})
            if apply_result and not apply_result.get("error"):
                print(f"  ✓ Applied to deck")
            else:
                error = apply_result.get("error") if apply_result else "No response"
                print(f"  ⚠ Failed to apply config to deck: {error}")
        else:
            error = save_result.get("error") if save_result else "No response"
            print(f"  ✗ Failed to save: {error}")

    print("\n" + "=" * 70)
    print("Verification: Right-click each deck in Anki → Options to confirm")


if __name__ == "__main__":
    update_deck_limits()
