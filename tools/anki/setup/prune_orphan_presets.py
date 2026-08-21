#!/usr/bin/env python3
"""tools/anki/setup/prune_orphan_presets.py — delete deck presets no deck uses.

Written 2026-08-20. The collection accumulated 53 orphan presets because
create_deck_presets.py creates rather than finds-or-creates: six runs each
minted the same set of names and abandoned the previous one. See DECK_PRESETS.md
section 6.

DESTRUCTIVE. Dry-run by default; --apply is required to delete anything.

Safety rules, all enforced at run time against live Anki rather than against a
saved survey:

  * A preset is deleted only if ZERO decks currently use it. Usage is recomputed
    here; the survey JSON is never trusted as input.
  * Deletion is by config id, never by name. Six names -- B737, UA Grammar,
    UA PVOM, UA Visual, UA Verbs, UA Lexeme EN->UA -- exist BOTH as a live
    preset and as one or more orphans. A name-keyed delete would hit the wrong
    one.
  * The Default preset (id 1) is never touched; Anki does not allow it.
  * Filtered decks cannot appear here at all. They live in the `decks` table,
    never in `deck_config`, so reading the preset list from the DB excludes
    them structurally. An earlier draft skipped any config whose NAME matched a
    deck name, which was both unnecessary and wrong: `B737` and `UA` are real
    deck names AND real preset names, so that rule silently protected ten
    genuine orphans. Deck names are never consulted now.
  * --expect N aborts unless exactly N presets are up for deletion, so a
    surprise (someone reassigned a deck; a new preset appeared) stops the run
    instead of being silently swept along.

Take a collection backup before --apply. Deleting a preset cannot be undone
from inside Anki.

Usage
-----
  python tools/anki/setup/prune_orphan_presets.py                 # dry run
  python tools/anki/setup/prune_orphan_presets.py --expect 53     # dry run, guarded
  python tools/anki/setup/prune_orphan_presets.py --expect 53 --apply
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:8765"
DEFAULT_CONFIG_ID = 1


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


def find_collection():
    roots = [
        Path.home() / "Library/Application Support/Anki2",
        Path.home() / ".local/share/Anki2",
        Path.home() / "AppData/Roaming/Anki2",
    ]
    out = []
    for r in roots:
        if r.is_dir():
            out.extend(sorted(r.glob("*/collection.anki2")))
    return out


def all_presets_from_db(path):
    for uri in (f"file:{path}?mode=ro", f"file:{path}?mode=ro&immutable=1"):
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5)
            try:
                rows = conn.execute("SELECT id, name FROM deck_config").fetchall()
                return {int(r[0]): r[1] for r in rows}
            except sqlite3.OperationalError:
                row = conn.execute("SELECT dconf FROM col").fetchone()
                blob = json.loads(row[0]) if row and row[0] else {}
                return {int(k): v.get("name", "?") for k, v in blob.items()}
            finally:
                conn.close()
        except Exception:  # noqa: BLE001
            continue
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--apply", action="store_true",
                    help="actually delete; without this it is a dry run")
    ap.add_argument("--expect", type=int, default=None,
                    help="abort unless exactly this many presets are up for deletion")
    args = ap.parse_args()

    try:
        anki("version", url=args.url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot reach AnkiConnect at {args.url}: {e}", file=sys.stderr)
        return 1

    # --- live usage, recomputed now ---------------------------------------
    decks = sorted(anki("deckNames", url=args.url) or [])
    in_use, live_names = set(), {}
    for deck in decks:
        try:
            cfg = anki("getDeckConfig", {"deck": deck}, url=args.url)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: {deck} would not return a config ({e}).", file=sys.stderr)
            print("Refusing to run with an incomplete usage picture.", file=sys.stderr)
            return 1
        cid = int(cfg["id"])
        in_use.add(cid)
        live_names[cid] = cfg.get("name", "?")

    # --- every preset ------------------------------------------------------
    found = find_collection()
    if not found:
        print("ERROR: no collection.anki2 found; cannot enumerate unused presets.",
              file=sys.stderr)
        return 1
    everything = all_presets_from_db(found[0])
    if not everything:
        print("ERROR: could not read deck_config from the collection.", file=sys.stderr)
        return 1

    # --- classify ----------------------------------------------------------
    # in_use can contain ids that are NOT presets: getDeckConfig on a filtered
    # deck returns the deck itself, so its id lands here. Those ids are absent
    # from deck_config, which is how we count them.
    real_in_use = {cid for cid in in_use if cid in everything}
    filtered = sorted(cid for cid in in_use if cid not in everything)

    doomed = [(cid, name)
              for cid, name in sorted(everything.items(),
                                      key=lambda kv: (kv[1].lower(), kv[0]))
              if cid not in in_use and cid != DEFAULT_CONFIG_ID]

    print(f"{len(decks)} decks · {len(everything)} presets · "
          f"{len(real_in_use)} in use · {len(doomed)} orphaned")
    if filtered:
        print(f"({len(filtered)} filtered deck(s) reported a pseudo-config; "
              f"they are not presets and are not counted above)")
    print()

    if not doomed:
        print("Nothing to delete.")
        return 0

    collide = {n for _, n in doomed} & set(live_names.values())
    if collide:
        print("NOTE: these names exist BOTH live and orphaned — deleting by id, "
              "not name:")
        for n in sorted(collide):
            print(f"    {n}")
        print()

    print("Presets that would be deleted:" if not args.apply else "Deleting:")
    for cid, name in doomed:
        print(f"    {cid}  {name}")
    print()

    if args.expect is not None and len(doomed) != args.expect:
        print(f"ABORT: expected {args.expect} orphan(s), found {len(doomed)}.",
              file=sys.stderr)
        print("Re-run the survey and reconcile before proceeding.", file=sys.stderr)
        return 1

    if not args.apply:
        print("Dry run. Nothing was changed.")
        print(f"To delete: --expect {len(doomed)} --apply   (take a backup first)")
        return 0

    ok, failed = 0, []
    for cid, name in doomed:
        try:
            anki("removeDeckConfigId", {"configId": cid}, url=args.url)
            ok += 1
        except Exception as e:  # noqa: BLE001
            failed.append((cid, name, str(e)))

    print(f"Deleted {ok} preset(s).")
    if failed:
        print(f"{len(failed)} failed:", file=sys.stderr)
        for cid, name, err in failed:
            print(f"    {cid}  {name}  --  {err}", file=sys.stderr)
        return 1

    # Deliberately NOT re-reading the collection file here. The deletions went
    # into Anki's live collection over AnkiConnect; Anki does not flush them to
    # collection.anki2 immediately, so a re-read at this moment reports the OLD
    # count and reads as a failed delete. An earlier version did exactly that
    # and printed "remaining: 84 (was 84)" after 52 successful deletions.
    print(f"Expected remaining: {len(everything) - ok} (was {len(everything)}).")
    print()
    print("Verify in Anki now — open any deck's Options and count the preset")
    print("dropdown; that reads the live collection. The survey tool reads the")
    print("file and will not agree until Anki has flushed, which a sync forces.")
    print()
    print("Then sync, so the deletions reach your other devices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
