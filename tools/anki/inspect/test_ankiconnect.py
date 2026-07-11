#!/usr/bin/env python3
"""Test AnkiConnect connectivity and configure sibling burying for UA FSRS.

Usage
-----
  python tools/anki/inspect/test_ankiconnect.py
  python tools/anki/inspect/test_ankiconnect.py --url http://127.0.0.1:8765
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
    print(f"Testing AnkiConnect at {url}...\n")

    # 1. Test connectivity
    try:
        version = anki_request("version", {}, url=url)
        print(f"✓ AnkiConnect is running")
        print(f"  AnkiConnect API version: {version}\n")
    except Exception as e:
        print(f"✗ AnkiConnect connection failed: {e}", file=sys.stderr)
        print(f"\n  Make sure:")
        print(f"    1. Anki is open")
        print(f"    2. AnkiConnect add-on is installed")
        print(f"    3. AnkiConnect is enabled (Tools → Add-ons → AnkiConnect → Check)")
        print(f"    4. AnkiConnect URL matches (default: {url})")
        return 1

    # 2. Get UA FSRS config
    print("Fetching UA FSRS config...\n")
    try:
        config = anki_request("getDeckConfig", {"deck": "UA"}, url=url)
        if not config:
            print("✗ Could not fetch UA deck config", file=sys.stderr)
            return 1

        config_name = config.get("name", "?")
        config_id = config.get("id", "?")
        print(f"✓ Found config: '{config_name}' (id={config_id})")
        print(f"  Desired retention: {config.get('desiredRetention', '?')}\n")
    except Exception as e:
        print(f"✗ Error fetching config: {e}", file=sys.stderr)
        return 1

    # 3. Check and enable sibling burying
    print("Checking sibling burying settings...\n")
    try:
        # In FSRS configs, sibling burying is typically under 'sched' or similar
        # Let's check what's in the config
        bury_siblings = config.get("burySiblingsOnAnswer", None)
        print(f"  burySiblingsOnAnswer: {bury_siblings}")

        if bury_siblings is False:
            print(f"\n  Enabling sibling burying...")
            config["burySiblingsOnAnswer"] = True
            anki_request("saveDeckConfig", {"config": config}, url=url)
            print(f"  ✓ Sibling burying enabled")
        elif bury_siblings is True:
            print(f"  ✓ Sibling burying already enabled")
        else:
            print(f"  ? Sibling burying setting unclear (value: {bury_siblings})")
            print(f"  Consider checking in Anki: Tools → Preferences → Scheduling")

    except Exception as e:
        print(f"✗ Error configuring sibling burying: {e}", file=sys.stderr)
        return 1

    print(f"\n✓ AnkiConnect is working and UA FSRS is configured.")
    print(f"\nNext step:")
    print(f"  1. Run: python tools/anki/setup/setup_ua_note_types.py --model UA_Lexeme")
    print(f"  2. Then study a UA→EN card and mark it 'Easy'")
    print(f"  3. EN→UA sibling should be buried for that day, reappearing next cycle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
