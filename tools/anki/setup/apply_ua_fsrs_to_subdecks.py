#!/usr/bin/env python3
"""Apply UA FSRS config to all UA subdeck tree.

Finds the UA FSRS config and applies it to all decks under UA:: hierarchy.
This ensures all 280+ UA cards use the same isolated FSRS scheduling.

Usage
-----
  python tools/anki/setup/apply_ua_fsrs_to_subdecks.py
  python tools/anki/setup/apply_ua_fsrs_to_subdecks.py --url http://127.0.0.1:8765
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

    print("Applying UA FSRS config to all UA subdecks...\n")

    # 1. Find UA FSRS config ID
    try:
        ua_config = anki_request("getDeckConfig", {"deck": "UA"}, url=url)
        if not ua_config or ua_config.get("name") != "UA FSRS":
            print("ERROR: UA deck is not using 'UA FSRS' config.", file=sys.stderr)
            print(f"  Current config: {ua_config.get('name') if ua_config else 'None'}", file=sys.stderr)
            return 1
        config_id = int(ua_config["id"])
        print(f"✓ Found UA FSRS config (id={config_id}, retention={ua_config.get('desiredRetention')})\n")
    except Exception as e:
        print(f"ERROR getting UA FSRS config: {e}", file=sys.stderr)
        return 1

    # 2. Get all decks
    try:
        all_decks = anki_request("deckNames", {}, url=url) or []
    except Exception as e:
        print(f"ERROR fetching deck names: {e}", file=sys.stderr)
        return 1

    # 3. Filter to UA subdecks (UA:: hierarchy, excluding root UA itself)
    ua_subdecks = sorted([d for d in all_decks if d.startswith("UA::") and d != "UA"])

    if not ua_subdecks:
        print("No UA subdecks found to update.")
        return 0

    print(f"Found {len(ua_subdecks)} UA subdeck(s) to update:\n")

    applied_count = 0
    for deck in ua_subdecks:
        try:
            anki_request("setDeckConfigId",
                         {"decks": [deck], "configId": config_id},
                         url=url)
            print(f"  ✓ {deck}")
            applied_count += 1
        except Exception as e:
            print(f"  ✗ {deck} — ERROR: {e}", file=sys.stderr)

    print(f"\n✓ Applied UA FSRS config to {applied_count} subdeck(s).")
    print("\nVerify in Anki:")
    print("  • Right-click each UA:: subdeck → Options")
    print("  • Should show 'UA FSRS' with 0.88 desired retention")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
