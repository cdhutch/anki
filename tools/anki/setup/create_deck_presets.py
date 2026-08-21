#!/usr/bin/env python3
"""tools/anki/setup/create_deck_presets.py — apply the managed deck presets.

Idempotent: run it twice and the second run reports no changes. Definitions come
from tools/anki/lib/deck_presets.py, which is the single source of truth;
DECK_PRESETS.md is its human-facing rendering.

WHY THIS WAS REWRITTEN (2026-08-20)
-----------------------------------
The previous version's create_or_update_preset() called cloneDeckConfigId
unconditionally -- there was no lookup anywhere in it. Anki permits duplicate
preset names, so every run minted a fresh set and abandoned the last. Six runs
left 53 orphan presets; the nine live UA presets ended up drawn from five
different batches. See DECK_PRESETS.md section 6.

Its JSON inputs were stale too, specifying review limits of 100/6/8/10/8 where
live Anki has 9999. Simply adding a lookup would have made the script reliably
revert the live state instead of accidentally preserving it.

HOW IDEMPOTENCE IS ACHIEVED
---------------------------
AnkiConnect cannot do this alone. Its deck-config actions are getDeckConfig (by
DECK, not by name), saveDeckConfig, setDeckConfigId, cloneDeckConfigId and
removeDeckConfigId -- there is no get-by-name and no list-all. The probe in
survey_deck_presets.py confirmed the latter empirically.

So the name -> id index is built from two sources at start:
  * AnkiConnect, by walking every deck -- authoritative but sees only presets
    that are currently ASSIGNED to something;
  * collection.anki2's deck_config table -- catches a preset that exists but is
    unassigned, which is exactly what a crashed earlier run leaves behind.

Without the second source, an unassigned preset is invisible and the next run
duplicates it. That is the bug this script exists to not have.

WHAT IT WILL NOT TOUCH
----------------------
Only MANAGED_KEYS are written. fsrsParams6 is excluded on purpose: FSRS
parameters are earned from a preset's own review history and are configuration
output, not input. Six B737 presets created by other means are left alone --
see UNMANAGED in the lib module.

Usage
-----
  python tools/anki/setup/create_deck_presets.py            # dry run
  python tools/anki/setup/create_deck_presets.py --apply
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.lib.deck_presets import (  # noqa: E402
    PRESETS, UNMANAGED, dig, put, wanted,
)

DEFAULT_URL = "http://127.0.0.1:8765"


def anki(action, params=None, *, url=DEFAULT_URL, timeout=15):
    body = {"action": action, "version": 6}
    if params:
        body["params"] = params
    req = urllib.request.Request(
        url, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read())
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload.get("result")


def presets_from_db():
    """{name: id} for every preset, including unassigned ones."""
    roots = [
        Path.home() / "Library/Application Support/Anki2",
        Path.home() / ".local/share/Anki2",
        Path.home() / "AppData/Roaming/Anki2",
    ]
    files = []
    for r in roots:
        if r.is_dir():
            files.extend(sorted(r.glob("*/collection.anki2")))
    if not files:
        return {}, "no collection.anki2 found"
    for uri in (f"file:{files[0]}?mode=ro", f"file:{files[0]}?mode=ro&immutable=1"):
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5)
            try:
                rows = conn.execute("SELECT id, name FROM deck_config").fetchall()
                return {r[1]: int(r[0]) for r in rows}, None
            finally:
                conn.close()
        except Exception as e:  # noqa: BLE001
            last = e
    return {}, f"could not read deck_config: {last}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--apply", action="store_true",
                    help="write changes; without this it is a dry run")
    args = ap.parse_args()

    try:
        anki("version", url=args.url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot reach AnkiConnect at {args.url}: {e}", file=sys.stderr)
        return 1

    decks = set(anki("deckNames", url=args.url) or [])

    # --- name -> id index, from both sources -------------------------------
    index, deck_of = {}, {}
    for deck in sorted(decks):
        try:
            cfg = anki("getDeckConfig", {"deck": deck}, url=args.url)
        except Exception:  # noqa: BLE001
            continue
        name, cid = cfg.get("name", "?"), int(cfg["id"])
        index.setdefault(name, cid)
        deck_of.setdefault(cid, deck)

    db_index, db_err = presets_from_db()
    if db_err:
        print(f"WARNING: {db_err}", file=sys.stderr)
        print("An existing but UNASSIGNED preset cannot be seen; this run could "
              "create a duplicate. Fix before using --apply.", file=sys.stderr)
        if args.apply:
            return 1
    for name, cid in db_index.items():
        index.setdefault(name, cid)

    print(f"{len(decks)} decks · {len(index)} presets known "
          f"({len(db_index)} from the collection file)\n")

    created, changed, unchanged, problems = [], [], [], []

    for name, spec in PRESETS.items():
        missing = [d for d in spec["decks"] if d not in decks]
        if missing:
            problems.append(f"{name}: deck(s) do not exist: {', '.join(missing)}")
        targets = [d for d in spec["decks"] if d in decks]

        cid = index.get(name)
        if cid is None:
            print(f"  {name}: NOT FOUND — would create")
            if args.apply:
                cid = anki("cloneDeckConfigId", {"name": name, "cloneFrom": 1},
                           url=args.url)
                if not cid:
                    problems.append(f"{name}: clone failed")
                    continue
                cid = int(cid)
                index[name] = cid
            created.append(name)
            if not args.apply:
                continue

        # assign first, so the config can be read back through a real deck
        for deck in targets:
            if args.apply:
                anki("setDeckConfigId", {"decks": [deck], "configId": cid},
                     url=args.url)
                deck_of[cid] = deck

        read_deck = deck_of.get(cid) or (targets[0] if targets else None)
        if not read_deck:
            problems.append(f"{name}: no deck to read its config through")
            continue
        cfg = anki("getDeckConfig", {"deck": read_deck}, url=args.url)
        if int(cfg["id"]) != cid:
            problems.append(f"{name}: {read_deck} uses {cfg.get('name')}, not this preset")
            continue

        deltas = {k: (dig(cfg, k), v) for k, v in wanted(name).items()
                  if dig(cfg, k) != v}
        if not deltas:
            unchanged.append(name)
            continue

        print(f"  {name}:")
        for k, (was, now) in sorted(deltas.items()):
            print(f"      {k:<22s} {json.dumps(was)} → {json.dumps(now)}")
        if args.apply:
            for k, (_, now) in deltas.items():
                put(cfg, k, now)
            anki("saveDeckConfig", {"config": cfg}, url=args.url)
        changed.append(name)

    print()
    print(f"  created:   {len(created)}   {', '.join(created) or '—'}")
    print(f"  changed:   {len(changed)}   {', '.join(changed) or '—'}")
    print(f"  unchanged: {len(unchanged)}")
    if UNMANAGED:
        print(f"  untouched by design: {len(UNMANAGED)} preset(s) — see "
              f"UNMANAGED in tools/anki/lib/deck_presets.py")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(f"  • {p}")

    if not args.apply:
        print("\nDry run. Nothing was changed.")
        if created or changed:
            print("Re-run with --apply to write these.")
    elif not (created or changed):
        print("\nAlready in the desired state.")
    else:
        print("\nRun again — a second run should report 0 created, 0 changed.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
