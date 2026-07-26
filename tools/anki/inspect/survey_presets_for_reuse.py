#!/usr/bin/env python3
"""Survey existing presets to see which can be modified and reused."""

import json
import urllib.request

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
        print(f"AnkiConnect error: {e}")
        return None


def main():
    print("Survey: Existing Presets and Reuse Opportunities")
    print("=" * 80)

    # Get all decks
    result = anki_request("deckNames")
    if not result or result.get("error"):
        print("Error getting deck names")
        return

    all_decks = result.get("result", [])

    # Map presets to decks that use them
    preset_usage = {}

    for deck in all_decks:
        result = anki_request("getDeckConfig", {"deck": deck})
        if result and not result.get("error"):
            config = result.get("result", {})
            config_id = config.get("id")
            config_name = config.get("name", "Unknown")

            if config_id not in preset_usage:
                preset_usage[config_id] = {
                    "name": config_name,
                    "new": config.get("new", {}).get("perDay"),
                    "review": config.get("rev", {}).get("perDay"),
                    "decks": [],
                    "has_fsrs": bool(config.get("fsrs", False)),
                }

            preset_usage[config_id]["decks"].append(deck)

    # Display presets
    print("\nEXISTING PRESETS:")
    print("-" * 80)

    for config_id, info in sorted(preset_usage.items(), key=lambda x: x[1]["name"]):
        print(f"\nPreset: {info['name']} (ID: {config_id})")
        print(f"  Limits: {info['new']} new / {info['review']} review")
        print(f"  FSRS enabled: {info['has_fsrs']}")
        print(f"  Used by {len(info['decks'])} deck(s):")
        for deck in sorted(info["decks"]):
            print(f"    • {deck}")

    # Analysis
    print("\n" + "=" * 80)
    print("REUSE ANALYSIS:")
    print("-" * 80)

    print("\nPresets that can be SAFELY MODIFIED (used by non-critical or single decks):")
    for config_id, info in sorted(preset_usage.items(), key=lambda x: x[1]["name"]):
        if len(info["decks"]) == 1 or "Default" in info["name"]:
            deck_list = ", ".join(info["decks"][:3])
            if len(info["decks"]) > 3:
                deck_list += f", +{len(info['decks'])-3} more"
            print(f"  • {info['name']}: Currently {info['new']}/{info['review']}")
            print(f"    Used by: {deck_list}")

    print("\nPresets that are WIDELY USED (risky to modify):")
    for config_id, info in sorted(preset_usage.items(), key=lambda x: x[1]["name"]):
        if len(info["decks"]) > 1 and "Default" not in info["name"]:
            print(f"  • {info['name']}: Used by {len(info['decks'])} decks")
            print(f"    (Modifying would affect all these decks)")

    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("-" * 80)
    print("""
Option A: Modify existing presets
  - Identify which presets you don't need
  - Modify them to match your target limits
  - Less work, but risky if decks currently use them

Option B: Create new presets + keep existing ones
  - Create 6 new presets with exact names/limits needed
  - Keep existing presets for backward compatibility
  - Safest approach, but requires manual preset creation
    """)


if __name__ == "__main__":
    main()
