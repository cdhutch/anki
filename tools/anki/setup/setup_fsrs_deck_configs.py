#!/usr/bin/env python3
"""Create and apply isolated FSRS deck configs for B737, UA, and Legacy top-level decks.

Each top-level deck gets its own FSRS config with completely disjoint card history and
scheduling. Cards in B737 do not influence UA algorithm and vice versa.

Settings
--------
  B737 (Professional Type Rating):
    - Desired retention: 0.93-0.95 (safety-critical, high recall)
    - Learning steps: 1m 10m
    - Relearning steps: 10m
    - Maximum interval: 365-730 days (optional cap for procedure currency)

  UA (Language Learning):
    - Desired retention: 0.85-0.90 (language with context, sustainable)
    - Learning steps: 1m 10m
    - Relearning steps: 10m
    - Maximum interval: 36500 days (no cap; long spacing is beneficial)

  Legacy (Archive/Reference):
    - Desired retention: 0.80-0.85 (not actively studied, conservative)
    - Learning steps: 10m 1d
    - Relearning steps: 1d
    - Maximum interval: 180-365 days (short cap for archived material)

Usage
-----
  python tools/anki/setup/setup_fsrs_deck_configs.py
  python tools/anki/setup/setup_fsrs_deck_configs.py --url http://127.0.0.1:8765
  python tools/anki/setup/setup_fsrs_deck_configs.py --b737-retention 0.94 --ua-retention 0.88
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

# ---------------------------------------------------------------------------
# Deck Config Specs
# ---------------------------------------------------------------------------

CONFIGS = {
    "B737 FSRS": {
        "deck": "B737",
        "new_per_day": 50,
        "rev_per_day": 200,
        "desired_retention": 0.94,
        "learning_steps": [1, 10],  # 1m, 10m
        "relearning_steps": [10],    # 10m
        "max_interval": 730,  # 2 years, optional cap for currency
    },
    "UA FSRS": {
        "deck": "UA",
        "new_per_day": 20,
        "rev_per_day": 200,
        "desired_retention": 0.88,
        "learning_steps": [1, 10],  # 1m, 10m
        "relearning_steps": [10],    # 10m
        "max_interval": 36500,  # ~100 years, no cap
    },
    "Legacy FSRS": {
        "deck": "Legacy",
        "new_per_day": 10,
        "rev_per_day": 50,
        "desired_retention": 0.82,
        "learning_steps": [10, 1440],  # 10m, 1d
        "relearning_steps": [1440],  # 1d
        "max_interval": 365,  # 1 year, short cap
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_config(preset_name: str, url: str) -> dict:
    """Return the config dict for *preset_name*, creating if necessary.

    Idempotent: if the preset already exists, return it for in-place update.
    Otherwise, clone from Default and fetch the full config.
    """
    # Try to find existing preset by name
    try:
        all_configs = anki_request("deckConfigNames", {}, url=url) or []
        for cfg_name in all_configs:
            if cfg_name == preset_name:
                # Found it; fetch the config dict
                cfg = anki_request("getDeckConfigId", {"configName": preset_name}, url=url)
                if cfg:
                    print(f"Found existing config '{preset_name}' (id={cfg}) — updating in place.")
                    # Now fetch the full config dict
                    cfg_dict = anki_request("getConfig", {"key": "decksWithConfigs"}, url=url)
                    # Actually, use saveDeckConfig approach: clone and fetch
                    tmp_deck = f"__tmp_{preset_name.replace(' ', '_')}__"
                    anki_request("createDeck", {"deck": tmp_deck}, url=url)
                    anki_request("setDeckConfigId", {"decks": [tmp_deck], "configId": int(cfg)}, url=url)
                    cfg_dict = anki_request("getDeckConfig", {"deck": tmp_deck}, url=url)
                    anki_request("deleteDecks", {"decks": [tmp_deck], "cardsToo": True}, url=url)
                    return cfg_dict
    except Exception:
        pass

    # Preset not found — clone from Default
    print(f"Creating new config '{preset_name}'...")
    new_id = anki_request("cloneDeckConfigId",
                          {"name": preset_name, "cloneFrom": 1},
                          url=url)
    print(f"  Cloned (id={new_id})")

    # Temporarily assign to a deck so we can fetch the full config dict
    tmp_deck = f"__tmp_{preset_name.replace(' ', '_')}__"
    anki_request("createDeck", {"deck": tmp_deck}, url=url)
    anki_request("setDeckConfigId", {"decks": [tmp_deck], "configId": new_id}, url=url)
    cfg = anki_request("getDeckConfig", {"deck": tmp_deck}, url=url)
    anki_request("deleteDecks", {"decks": [tmp_deck], "cardsToo": True}, url=url)

    return cfg


def _apply_fsrs_settings(cfg: dict, spec: dict) -> dict:
    """Apply FSRS settings from spec to config dict."""
    cfg["new"]["perDay"] = spec["new_per_day"]
    cfg["rev"]["perDay"] = spec["rev_per_day"]
    cfg["fsrs"] = True
    cfg["fsrsWeights"] = []  # Empty → use Anki's built-in defaults
    cfg["desiredRetention"] = spec["desired_retention"]
    cfg["newSpread"] = 0  # 0 = distribute new cards, 1 = show in today's review

    # Learning and relearning steps (in minutes)
    cfg["new"]["delays"] = spec["learning_steps"]
    cfg["lapse"]["delays"] = spec["relearning_steps"]

    # Maximum interval (in days)
    cfg["rev"]["maxIvl"] = spec["max_interval"]

    return cfg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8765", help="AnkiConnect URL")
    ap.add_argument("--b737-retention", type=float, help="B737 FSRS desired retention")
    ap.add_argument("--ua-retention", type=float, help="UA FSRS desired retention")
    ap.add_argument("--legacy-retention", type=float, help="Legacy FSRS desired retention")
    args = ap.parse_args()

    url = args.url

    # Apply retention overrides if provided
    if args.b737_retention:
        CONFIGS["B737 FSRS"]["desired_retention"] = args.b737_retention
    if args.ua_retention:
        CONFIGS["UA FSRS"]["desired_retention"] = args.ua_retention
    if args.legacy_retention:
        CONFIGS["Legacy FSRS"]["desired_retention"] = args.legacy_retention

    print("Setting up isolated FSRS deck configs...\n")

    for preset_name, spec in CONFIGS.items():
        print(f"━━ {preset_name} ━━")

        # 1. Get or create the config
        cfg = _get_or_create_config(preset_name, url)

        # 2. Apply FSRS settings
        cfg = _apply_fsrs_settings(cfg, spec)

        # 3. Save
        saved = anki_request("saveDeckConfig", {"config": cfg}, url=url)
        if not saved:
            print(f"  ERROR: saveDeckConfig returned falsy — {preset_name} not saved.", file=sys.stderr)
            return 1

        config_id = int(cfg["id"])
        print(f"  Saved: retention={spec['desired_retention']:.2f}  "
              f"new={spec['new_per_day']}/day  "
              f"rev={spec['rev_per_day']}/day  "
              f"maxIvl={spec['max_interval']}d")

        # 4. Apply to top-level deck
        target_deck = spec["deck"]
        anki_request("createDeck", {"deck": target_deck}, url=url)
        anki_request("setDeckConfigId",
                     {"decks": [target_deck], "configId": config_id},
                     url=url)
        print(f"  Applied to deck '{target_deck}'")
        print()

    print("✓ Done. All three decks now have isolated FSRS configs.")
    print("\nVerify in Anki:")
    print("  • Tools → Preferences → Scheduling (should show FSRS active)")
    print("  • Right-click each top-level deck (B737, UA, Legacy) → Options")
    print("    (should show different desired retention for each)")
    print("\nMonitor after 2–3 weeks of real study data; adjust retention if needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
