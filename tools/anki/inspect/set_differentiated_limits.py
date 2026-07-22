#!/usr/bin/env python3
"""Set differentiated deck limits based on cognitive load and UA study strategy."""

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


# Deck configurations by cognitive load
DECK_CONFIGS = {
    # High cognitive load (typing/recall)
    "UA Recognition - PVOM (Typing)": {
        "decks": ["UA::Recognition::PVOM"],
        "new": 18,  # Typing infinitives require recall
        "learning": 0,
        "review": 6,
        "reason": "Typing/production - requires spelling & recall",
    },
    # Medium-High cognitive load (production/typing)
    "UA Recognition - Lexeme EN→UA (Typing)": {
        "decks": ["UA::Recognition::UA→EN"],  # EN→UA is production (typing)
        "new": 15,
        "learning": 0,
        "review": 8,
        "reason": "Mixed: EN→UA typing (15), UA→EN recognition (carried over)",
    },
    # Low-Medium cognitive load (recognition/visual)
    "UA Recognition - Visual (Recognition)": {
        "decks": ["UA::Recognition::Visual"],
        "new": 25,
        "learning": 0,
        "review": 10,
        "reason": "Visual/diagram-based - pattern recognition",
    },
    # Medium cognitive load (grammar/rules)
    "UA Recognition - Grammar (Recognition)": {
        "decks": ["UA::Recognition::Grammar"],
        "new": 20,
        "learning": 0,
        "review": 8,
        "reason": "Grammar rules - recognition-based",
    },
    # Medium cognitive load (conjugation)
    "UA Verbs (Mixed)": {
        "decks": ["UA::Verbs"],
        "new": 20,
        "learning": 0,
        "review": 8,
        "reason": "Verb conjugation - mixed recognition/production",
    },
}

# Parent deck config (union of all)
PARENT_CONFIG = {
    "deck": "UA",
    "new": 50,  # Total daily budget
    "learning": 0,
    "review": 40,  # Allow high review load
    "reason": "Parent deck - union of child limits",
}


def create_or_update_config(config_name, new_limit, learning_limit, review_limit):
    """Create or update a deck configuration."""
    config = {
        "name": config_name,
        "new": {
            "perDay": new_limit,
            "delays": [1, 10],
            "ints": [1, 4],
            "initialFactor": 2500,
            "bury": False,
            "order": 0,
        },
        "lrn": {
            "delays": [10],
            "perDay": learning_limit,
        },
        "rev": {
            "perDay": review_limit,
            "ease4": 1.3,
            "bury": False,
            "hardPenalty": 1.2,
        },
        "timer": {
            "useCurrent": True,
            "maxTaken": 60000,
        },
        "autoplay": {
            "sounds": True,
            "replayQuestion": True,
        },
        "mod": 0,
        "usn": -1,
    }

    result = anki_request("saveDeckConfig", {"config": config})
    if result and not result.get("error"):
        config_id = result.get("result")
        return config_id
    else:
        return None


def main():
    print("Setting Differentiated Deck Limits for UA Domain")
    print("=" * 70)
    print("\nStrategy: 50 new cards/day across UA domain")
    print("  • High load (typing): 18 new/day (PVOM, Lexeme EN→UA)")
    print("  • Medium load (grammar): 20 new/day (Grammar, Verbs)")
    print("  • Low load (visual): 25 new/day (Visual)")
    print("  • Total: 50 new/day")
    print("\n" + "=" * 70)

    # Create/update parent deck config first
    print(f"\n1. Updating parent deck config (UA)")
    print(f"   Limits: {PARENT_CONFIG['new']}/{PARENT_CONFIG['learning']}/{PARENT_CONFIG['review']}")
    print(f"   Reason: {PARENT_CONFIG['reason']}")

    config_id = create_or_update_config(
        PARENT_CONFIG["deck"],
        PARENT_CONFIG["new"],
        PARENT_CONFIG["learning"],
        PARENT_CONFIG["review"],
    )

    if config_id:
        print(f"   ✓ Config created/updated (ID: {config_id})")
        # Try to apply to parent deck
        result = anki_request(
            "setDeckConfigId",
            {"decks": [PARENT_CONFIG["deck"]], "configId": config_id},
        )
        if result and not result.get("error"):
            print(f"   ✓ Applied to deck: UA")
    else:
        print(f"   ⚠ Could not create config (may need manual setup)")

    # Create/update child deck configs
    print(f"\n2. Creating child deck configs")
    config_map = {}

    for i, (config_name, config_spec) in enumerate(DECK_CONFIGS.items(), 1):
        new_limit = config_spec["new"]
        learning_limit = config_spec["learning"]
        review_limit = config_spec["review"]
        reason = config_spec["reason"]

        print(f"\n   {i}. {config_name}")
        print(f"      Limits: {new_limit}/{learning_limit}/{review_limit}")
        print(f"      Reason: {reason}")

        config_id = create_or_update_config(
            config_name, new_limit, learning_limit, review_limit
        )

        if config_id:
            print(f"      ✓ Config created (ID: {config_id})")
            config_map[config_name] = {
                "id": config_id,
                "decks": config_spec["decks"],
            }

            # Try to apply to each deck in this config
            for deck_name in config_spec["decks"]:
                result = anki_request(
                    "setDeckConfigId",
                    {"decks": [deck_name], "configId": config_id},
                )
                if result and not result.get("error"):
                    print(f"      ✓ Applied to deck: {deck_name}")
                else:
                    print(f"      ⚠ Could not apply to deck: {deck_name}")
        else:
            print(f"      ⚠ Could not create config")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    total_new = sum(s["new"] for s in DECK_CONFIGS.values())
    total_review = sum(s["review"] for s in DECK_CONFIGS.values())

    print(f"\nDeck Limits Set:")
    print(f"  • PVOM (typing): 18 new/day")
    print(f"  • Lexeme EN→UA (typing): 15 new/day")
    print(f"  • Grammar (recognition): 20 new/day")
    print(f"  • Verbs (mixed): 20 new/day")
    print(f"  • Visual (recognition): 25 new/day")
    print(f"  ────────────────────────")
    print(f"  • TOTAL: {total_new} new/day")
    print(f"  • Review capacity: {total_review}/day")

    print("\nNext Steps:")
    print("  1. Verify limits in Anki (right-click each deck → Options)")
    print("  2. Start reviewing PVOM cards to test typing template")
    print("  3. Monitor learning curve for 2-3 days")
    print("  4. Adjust limits if needed based on study load")

    print("\nNote: UA_Lexeme_Legacy is not included (holding queue for migrations)")


if __name__ == "__main__":
    main()
