#!/usr/bin/env python3
"""Create (or update) the "B737 Checklists" deck preset and apply it.

Settings applied
----------------
  new cards / day  : 10
  reviews / day    : 9999
  FSRS             : enabled
  desired retention: 0.90
  FSRS weights     : []  (Anki defaults; replace after optimising)

Deck targeted
-------------
  B737::Core::Checklists

Idempotent: if the target deck already uses a preset named
"B737 Checklists", that preset is updated in place.

Usage
-----
  python tools/anki/setup/create_checklists_preset.py
  python tools/anki/setup/create_checklists_preset.py --retention 0.92
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

PRESET_NAME       = "B737 Checklists"
TARGET_DECKS      = ["B737::Core::Checklists"]
NEW_PER_DAY       = 10
REV_PER_DAY       = 9999
DESIRED_RETENTION = 0.90
FSRS_WEIGHTS: list[float] = []


def _get_or_create_preset(preset_name: str, url: str) -> dict:
    probe_deck = TARGET_DECKS[0]
    try:
        cfg = anki_request("getDeckConfig", {"deck": probe_deck}, url=url)
        if isinstance(cfg, dict) and cfg.get("name") == preset_name:
            print(f"Found existing preset '{preset_name}' (id={cfg['id']}) on '{probe_deck}' — updating in place.")
            return cfg
    except Exception:
        pass

    new_id = anki_request("cloneDeckConfigId",
                          {"name": preset_name, "cloneFrom": 1},
                          url=url)
    print(f"Cloned new preset '{preset_name}' (id={new_id}).")

    tmp = "__tmp_preset_fetch__"
    anki_request("createDeck", {"deck": tmp}, url=url)
    anki_request("setDeckConfigId", {"decks": [tmp], "configId": new_id}, url=url)
    cfg = anki_request("getDeckConfig", {"deck": tmp}, url=url)
    anki_request("deleteDecks", {"decks": [tmp], "cardsToo": True}, url=url)

    return cfg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8765", help="AnkiConnect URL")
    ap.add_argument("--retention", type=float, default=DESIRED_RETENTION,
                    help="FSRS desired retention (default %(default)s)")
    ap.add_argument("--new-per-day", type=int, default=NEW_PER_DAY)
    ap.add_argument("--rev-per-day", type=int, default=REV_PER_DAY)
    args = ap.parse_args()

    url = args.url

    cfg = _get_or_create_preset(PRESET_NAME, url)

    cfg["new"]["perDay"]    = args.new_per_day
    cfg["rev"]["perDay"]    = args.rev_per_day
    cfg["fsrs"]             = True
    cfg["fsrsWeights"]      = FSRS_WEIGHTS
    cfg["desiredRetention"] = args.retention

    saved = anki_request("saveDeckConfig", {"config": cfg}, url=url)
    if not saved:
        print("ERROR: saveDeckConfig returned falsy — preset not saved.", file=sys.stderr)
        return 1
    print(f"Preset saved: new={args.new_per_day}/day  "
          f"rev={args.rev_per_day}/day  "
          f"FSRS=True  retention={args.retention}")

    config_id = int(cfg["id"])
    for deck in TARGET_DECKS:
        anki_request("createDeck", {"deck": deck}, url=url)
        anki_request("setDeckConfigId",
                     {"decks": [deck], "configId": config_id},
                     url=url)
        print(f"  Applied '{PRESET_NAME}' → {deck}")

    print("\nDone. Verify in Anki: Deck Options.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
