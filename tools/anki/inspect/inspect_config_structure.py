#!/usr/bin/env python3
"""Inspect the full structure of the UA FSRS deck config.

This helps us understand what keys are available and how to set sibling burying.

Usage
-----
  python tools/anki/inspect/inspect_config_structure.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default="http://127.0.0.1:8765", help="AnkiConnect URL")
    args = ap.parse_args()

    url = args.url

    print("Fetching UA FSRS deck config structure...\n")

    try:
        config = anki_request("getDeckConfig", {"deck": "UA"}, url=url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not config:
        print("No config found", file=sys.stderr)
        return 1

    print("Full UA FSRS config structure:")
    print("=" * 80)
    print(json.dumps(config, indent=2, default=str))
    print("=" * 80)

    print("\nLooking for sibling-related settings...\n")

    # Search for any keys containing "sibling", "bury", etc.
    search_terms = ["sibling", "bury", "suspend", "block", "dependent"]
    found = False

    def search_dict(d, path=""):
        global found
        if isinstance(d, dict):
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key
                if any(term in key.lower() for term in search_terms):
                    print(f"  ✓ Found: {full_path} = {value}")
                    found = True
                search_dict(value, full_path)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                search_dict(item, f"{path}[{i}]")

    search_dict(config)

    if not found:
        print("  No sibling/bury-related settings found in deck config.")
        print("\nNote: Sibling burying might be a global preference in Anki 26.")
        print("Check: Tools → Preferences → Scheduling → 'Bury sibling cards'")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
