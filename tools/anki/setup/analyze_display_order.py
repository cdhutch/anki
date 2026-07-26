#!/usr/bin/env python3
"""
analyze_display_order.py — Analyze and optimize card display order to prevent
pattern-based answering in Anki.

Polls display order settings via AnkiConnect:
1. Field order in each note type
2. Card template field display order
3. Deck shuffle/ordering settings

Requires: Anki open with AnkiConnect add-on active on port 8765.

Usage:
    python3 tools/anki/setup/analyze_display_order.py
"""

import collections
import json
import urllib.request
from typing import Dict, List, Any
import re


def anki(action, **params):
    """Call AnkiConnect API."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen("http://localhost:8765", payload) as r:
        result = json.loads(r.read())
    if result.get("error"):
        raise Exception(result["error"])
    return result["result"]


def get_all_models() -> Dict[int, Dict[str, Any]]:
    """Get all note types (models) from Anki."""
    model_names = anki("modelNames")
    models = {}
    for name in model_names:
        model_id = anki("modelId", modelName=name)
        model_fields = anki("modelFieldNames", modelName=name)
        models[model_id] = {"name": name, "fields": model_fields}
    return models


def get_model_templates(model_name: str) -> Dict[str, Dict]:
    """Get card templates for a note type."""
    try:
        templates = anki("modelTemplates", modelName=model_name)
        return templates
    except:
        return {}


def extract_fields_from_template(template_text: str) -> List[str]:
    """Extract field names from template ({{fieldname}} syntax)."""
    fields = re.findall(r'{{[^}]*?(\w+)[^}]*?}}', template_text)
    return list(dict.fromkeys(fields))  # Remove duplicates, preserve order


def survey_decks():
    """Get deck structure and configurations."""
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
        print("=" * 80)
        print("ANKI DISPLAY ORDER ANALYSIS")
        print("=" * 80)

        # === NOTE TYPES / FIELD ORDER ===
        print("\n" + "=" * 80)
        print("1. NOTE TYPE FIELD ORDER")
        print("=" * 80)
        models = get_all_models()

        for model_id, model_info in sorted(models.items()):
            name = model_info["name"]
            fields = model_info["fields"]
            print(f"\n{name} (id: {model_id})")
            print(f"  Field order: {fields}")

            # Get templates for this model
            templates = get_model_templates(name)
            if templates:
                print(f"  Templates:")
                for card_name, card_content in templates.items():
                    front_fields = extract_fields_from_template(card_content.get("Front", ""))
                    back_fields = extract_fields_from_template(card_content.get("Back", ""))
                    print(f"    {card_name}:")
                    print(f"      Front: {front_fields if front_fields else '[none]'}")
                    print(f"      Back:  {back_fields if back_fields else '[none]'}")

        # === DECK SHUFFLE/ORDER SETTINGS ===
        print("\n" + "=" * 80)
        print("2. DECK CONFIGURATION & CARD ORDER SETTINGS")
        print("=" * 80)

        by_config = survey_decks()
        for cid, (cfg, decks) in sorted(by_config.items()):
            print(f"\nPreset: \"{cfg['name']}\" (id: {cid})")
            print(f"  Decks using this preset: {len(decks)}")

            new_cfg = cfg.get("new", {})
            new_order = new_cfg.get("order", 0)
            order_names = {0: "Order added", 1: "Random"}
            print(f"  New card order: {order_names.get(new_order, f'Unknown ({new_order})')}")
            print(f"  New cards/day: {new_cfg.get('perDay', 'n/a')}")

            rev_cfg = cfg.get("rev", {})
            rev_perday = rev_cfg.get("perDay", "n/a")
            print(f"  Review cards/day: {rev_perday}")

        # === RECOMMENDATIONS ===
        print("\n" + "=" * 80)
        print("3. RECOMMENDATIONS TO PREVENT PATTERN-BASED ANSWERING")
        print("=" * 80)
        print("""
Issues that enable pattern-based answering:

✓ New card order = "Order added" (predictable sequence)
✓ Fixed field display order in templates (same order every time)
✓ Consistent study time/order (brain memorizes position, not content)

Mitigation strategies:
1. Set new card order to "Random" for all deck presets
2. Randomize template field display with JavaScript/styling
3. Vary study sessions (time, number of cards, deck order)
4. Use interleaving: mix decks and card types in single session
        """)

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Anki is open with AnkiConnect on port 8765.")


if __name__ == "__main__":
    main()
