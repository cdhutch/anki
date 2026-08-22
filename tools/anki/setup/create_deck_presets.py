#!/usr/bin/env python3
"""tools/anki/setup/create_deck_presets.py — apply presets/*.json to Anki.

Idempotent: run twice and the second run reports nothing to do. The repo files
are the source of truth; export_deck_presets.py produces them from live Anki.

WHY THIS WAS REWRITTEN (2026-08-20)
-----------------------------------
The previous version's create_or_update_preset() called cloneDeckConfigId
unconditionally -- there was no lookup anywhere in it. Anki permits duplicate
preset names, so every run minted a fresh set and abandoned the last. Six runs
left 53 orphan presets, and the nine live UA presets ended up drawn from five
different batches. See DECK_PRESETS.md section 6.

Its JSON inputs were stale as well, specifying review limits of 100/6/8/10/8
against a live 9999. Adding a lookup alone would have made the script reliably
revert live state rather than accidentally preserve it, so the values now come
from an export of Anki itself.

HOW IDEMPOTENCE IS ACHIEVED
---------------------------
AnkiConnect cannot do this alone. Its deck-config actions are getDeckConfig (by
DECK, not by name), saveDeckConfig, setDeckConfigId, cloneDeckConfigId and
removeDeckConfigId. There is no get-by-name and no list-all -- the probe in
survey_deck_presets.py confirmed the latter empirically.

So the name -> id index comes from two sources:
  * AnkiConnect, walking every deck -- authoritative, but sees only presets that
    are currently ASSIGNED to something;
  * collection.anki2's deck_config table -- catches a preset that exists but is
    unassigned, which is exactly what a crashed earlier run leaves behind.

Without the second source an unassigned preset is invisible and the next run
duplicates it. That is the bug this script exists not to have.

SCOPE
-----
Writes every key in the file's `config` block. FSRS parameters are absent from
those files by construction (see EXCLUDE in the lib module), so an apply can
never clobber an optimization.

--only NAME restricts the run to one preset, which is how the write path gets
proven on a throwaway before it is pointed at real decks.

Usage
-----
  python tools/anki/setup/create_deck_presets.py                       # dry run, all
  python tools/anki/setup/create_deck_presets.py --only "ZZ Test"      # dry run, one
  python tools/anki/setup/create_deck_presets.py --only "ZZ Test" --apply
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
    EXCLUDE, dig, flatten, load_presets, put,
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
    last = None
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
    ap.add_argument("--dir", default="presets", help="directory of preset files")
    ap.add_argument("--only", action="append", default=None,
                    help="apply just this preset name; repeatable")
    ap.add_argument("--apply", action="store_true",
                    help="write changes; without this it is a dry run")
    args = ap.parse_args()

    try:
        anki("version", url=args.url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot reach AnkiConnect at {args.url}: {e}", file=sys.stderr)
        return 1

    try:
        files = load_presets(args.dir)
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if not files:
        print(f"ERROR: no preset files in {args.dir}/", file=sys.stderr)
        return 1

    if args.only:
        unknown = [n for n in args.only if n not in files]
        if unknown:
            print(f"ERROR: no file defines: {', '.join(unknown)}", file=sys.stderr)
            print(f"Known: {', '.join(sorted(files))}", file=sys.stderr)
            return 1
        files = {n: files[n] for n in args.only}

    decks = set(anki("deckNames", url=args.url) or [])

    index, deck_of = {}, {}
    for deck in sorted(decks):
        try:
            cfg = anki("getDeckConfig", {"deck": deck}, url=args.url)
        except Exception:  # noqa: BLE001
            continue
        index.setdefault(cfg.get("name", "?"), int(cfg["id"]))
        deck_of.setdefault(int(cfg["id"]), deck)

    db_index, db_err = presets_from_db()
    if db_err:
        print(f"WARNING: {db_err}", file=sys.stderr)
        print("An existing but UNASSIGNED preset cannot be seen, so this run could "
              "create a duplicate. Refusing to --apply.", file=sys.stderr)
        if args.apply:
            return 1
    for name, cid in db_index.items():
        index.setdefault(name, cid)

    print(f"{len(decks)} decks · {len(index)} presets known · "
          f"{len(files)} file(s) selected\n")

    created, changed, unchanged, problems = [], [], [], []

    for name, doc in files.items():
        want = {k: v for k, v in flatten(doc["config"]).items()
                if k.split(".")[0] not in EXCLUDE}
        targets = [d for d in doc["meta"].get("decks", []) if d in decks]
        absent = [d for d in doc["meta"].get("decks", []) if d not in decks]
        if absent:
            problems.append(f"{name}: deck(s) do not exist: {', '.join(absent)}")

        cid = index.get(name)
        if cid is None:
            print(f"  {name}: NOT FOUND — would create")
            created.append(name)
            if not args.apply:
                continue
            cid = anki("cloneDeckConfigId", {"name": name, "cloneFrom": 1},
                       url=args.url)
            if not cid:
                problems.append(f"{name}: clone failed")
                continue
            cid = int(cid)
            index[name] = cid

        if args.apply:
            for deck in targets:
                anki("setDeckConfigId", {"decks": [deck], "configId": cid},
                     url=args.url)
                deck_of[cid] = deck

        read_deck = deck_of.get(cid) or (targets[0] if targets else None)
        if not read_deck:
            problems.append(f"{name}: no existing deck to read its config through")
            continue
        live = anki("getDeckConfig", {"deck": read_deck}, url=args.url)
        if int(live["id"]) != cid:
            problems.append(
                f"{name}: {read_deck} uses {live.get('name')!r}, not this preset")
            continue

        deltas = {k: (dig(live, k), v) for k, v in want.items() if dig(live, k) != v}
        if not deltas:
            if name not in created:
                unchanged.append(name)
            continue

        print(f"  {name}:")
        for k, (was, now) in sorted(deltas.items()):
            print(f"      {k:<26s} {json.dumps(was)} → {json.dumps(now)}")
        if args.apply:
            for k, (_, now) in deltas.items():
                put(live, k, now)
            anki("saveDeckConfig", {"config": live}, url=args.url)
        if name not in created:
            changed.append(name)

    print()
    print(f"  created:   {len(created)}   {', '.join(created) or '—'}")
    print(f"  changed:   {len(changed)}   {', '.join(changed) or '—'}")
    print(f"  unchanged: {len(unchanged)}")
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
