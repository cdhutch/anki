#!/usr/bin/env python3
"""Create (or update) the "B737 SV Exam" deck preset and apply it.

Settings applied
----------------
  new cards / day  : 50
  reviews / day    : 9999
  FSRS             : enabled
  desired retention: 0.90   (edit DESIRED_RETENTION below to taste)
  FSRS weights     : []     (use Anki's built-in defaults; replace with
                             your optimised weights after running the
                             FSRS optimiser in the Anki GUI)

Decks targeted
--------------
  B737::Systems::SV
  B737::Systems::SV::MCQ
  B737::Systems::SV::TF

Idempotent: if the first target deck already uses a preset named
"B737 SV Exam", that preset is updated in place — no duplicate is created.

Usage
-----
  python tools/anki/setup/create_sv_exam_preset.py
  python tools/anki/setup/create_sv_exam_preset.py --url http://127.0.0.1:8765
  python tools/anki/setup/create_sv_exam_preset.py --retention 0.92
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

PRESET_NAME       = "B737 SV Exam"
TARGET_DECKS      = ["B737::Systems::SV", "B737::Systems::SV::MCQ", "B737::Systems::SV::TF"]
NEW_PER_DAY       = 50
REV_PER_DAY       = 9999
DESIRED_RETENTION = 0.90
FSRS_WEIGHTS: list[float] = []   # empty → Anki default weights


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_preset(preset_name: str, url: str) -> dict:
    """Return the config dict for *preset_name*, creating it only if necessary.

    Strategy
    --------
    1. Call getDeckConfig on the first target deck.
       • If its 'name' already matches preset_name → the deck is already on the
         right preset; return that config for in-place update (no clone needed).
    2. Otherwise clone the Default preset, apply it to a temp deck to fetch the
       full config dict, then clean up the temp deck.
    """
    # ── Try to reuse the existing preset from the first target deck ──────────
    probe_deck = TARGET_DECKS[0]
    try:
        cfg = anki_request("getDeckConfig", {"deck": probe_deck}, url=url)
        if isinstance(cfg, dict) and cfg.get("name") == preset_name:
            print(f"Found existing preset '{preset_name}' (id={cfg['id']}) on '{probe_deck}' — updating in place.")
            return cfg
    except Exception:
        pass  # deck may not exist yet; fall through to clone

    # ── Preset not found on the target deck — clone from Default ─────────────
    new_id = anki_request("cloneDeckConfigId",
                          {"name": preset_name, "cloneFrom": 1},
                          url=url)
    print(f"Cloned new preset '{preset_name}' (id={new_id}).")

    # Temporarily assign the new config to a throwaway deck so we can fetch it.
    tmp = "__tmp_preset_fetch__"
    anki_request("createDeck", {"deck": tmp}, url=url)
    anki_request("setDeckConfigId", {"decks": [tmp], "configId": new_id}, url=url)
    cfg = anki_request("getDeckConfig", {"deck": tmp}, url=url)
    anki_request("deleteDecks", {"decks": [tmp], "cardsToo": True}, url=url)

    return cfg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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

    # ── 1. Get or create the preset ─────────────────────────────────────────
    cfg = _get_or_create_preset(PRESET_NAME, url)

    # ── 2. Apply our settings ───────────────────────────────────────────────
    cfg["new"]["perDay"]      = args.new_per_day
    cfg["rev"]["perDay"]      = args.rev_per_day
    cfg["fsrs"]               = True
    cfg["fsrsWeights"]        = FSRS_WEIGHTS
    cfg["desiredRetention"]   = args.retention

    # ── 3. Save ─────────────────────────────────────────────────────────────
    saved = anki_request("saveDeckConfig", {"config": cfg}, url=url)
    if not saved:
        print("ERROR: saveDeckConfig returned falsy — preset not saved.", file=sys.stderr)
        return 1
    print(f"Preset saved: new={args.new_per_day}/day  "
          f"rev={args.rev_per_day}/day  "
          f"FSRS=True  retention={args.retention}")

    # ── 4. Apply to target decks ─────────────────────────────────────────────
    config_id = int(cfg["id"])
    for deck in TARGET_DECKS:
        # Ensure deck exists first (createDeck is idempotent)
        anki_request("createDeck", {"deck": deck}, url=url)
        anki_request("setDeckConfigId",
                     {"decks": [deck], "configId": config_id},
                     url=url)
        print(f"  Applied '{PRESET_NAME}' → {deck}")

    print("\nDone. Verify in Anki: Tools → Manage Note Types / Deck Options.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
