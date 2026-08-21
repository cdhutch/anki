#!/usr/bin/env python3
"""tools/anki/inspect/survey_deck_presets.py — full deck/preset survey, both domains.

Written 2026-08-20 for the deck-preset cleanup. Answers three questions the
existing tools cannot:

  1. Which preset does every deck use?  (all domains -- list_deck_presets.py
     covers UA only, inspect_deck_configs.py filters to B737)
  2. Which presets exist but are used by NO deck?  Neither existing tool can
     see one: both enumerate presets by iterating decks and collecting what
     they point at, so a zero-deck preset is structurally invisible. That is
     exactly how `UA FSRS` sat unnoticed on 0 decks for six weeks.
  3. What is the live deck tree?  Four repo documents describe four different
     B737 architectures; only Anki knows which one exists.

AnkiConnect is the primary instrument, per Craig: deck->preset association and
preset parameters both come from it. The collection file is touched only if
AnkiConnect cannot enumerate presets on its own, and only to read id+name.

Read-only. Never writes to Anki and never writes to the collection.

Usage
-----
  python tools/anki/inspect/survey_deck_presets.py
  python tools/anki/inspect/survey_deck_presets.py --json build/deck_preset_survey.json
  python tools/anki/inspect/survey_deck_presets.py --url http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:8765"

# Candidate AnkiConnect actions that would enumerate every preset directly.
# Probed rather than assumed -- if any works we never open the collection.
LIST_ALL_CANDIDATES = ("getDeckConfigs", "getDeckConfigIds", "deckConfigs")

# Parameters worth showing per preset. Everything else stays in the JSON.
SUMMARY_KEYS = [
    ("new.perDay", "new/day"),
    ("rev.perDay", "rev/day"),
    ("desiredRetention", "retention"),
    ("fsrsWeights", "fsrs weights"),
    ("new.delays", "learn steps"),
    ("lapse.delays", "relearn steps"),
    ("lapse.leechFails", "leech at"),
    ("maxIvl", "max ivl"),
]


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


def dig(cfg, dotted):
    """cfg['new']['perDay'] from 'new.perDay'; None if any hop is missing."""
    cur = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def fmt(value):
    if value is None:
        return "—"
    if isinstance(value, list):
        if not value:
            return "[]"
        if len(value) > 4:
            return f"[{len(value)} values]"
        return "[" + " ".join(str(v) for v in value) + "]"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def find_collection():
    """Locate collection.anki2. Note query_anki_db.py looks for 'collection.db',
    which modern Anki has not used in years -- that script may never have found
    a collection at all."""
    roots = [
        Path.home() / "Library/Application Support/Anki2",   # macOS
        Path.home() / ".local/share/Anki2",                  # Linux
        Path.home() / "AppData/Roaming/Anki2",               # Windows
    ]
    found = []
    for root in roots:
        if root.is_dir():
            found.extend(sorted(root.glob("*/collection.anki2")))
    return found


def presets_from_db(path):
    """Return {id: name} for every preset. Schema 18+ keeps the parameters in a
    protobuf blob, so only id and name are read -- which is all orphan
    detection needs. Tries a plain read-only open first; falls back to
    immutable, which takes no locks but can see a torn view if Anki is mid-write.
    """
    for uri, mode in (
        (f"file:{path}?mode=ro", "read-only"),
        (f"file:{path}?mode=ro&immutable=1", "immutable"),
    ):
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5)
            try:
                rows = conn.execute("SELECT id, name FROM deck_config").fetchall()
                return {int(r[0]): r[1] for r in rows}, mode, None
            except sqlite3.OperationalError:
                # Pre-schema-18: configs live in a JSON blob on the col row.
                row = conn.execute("SELECT dconf FROM col").fetchone()
                blob = json.loads(row[0]) if row and row[0] else {}
                return ({int(k): v.get("name", "?") for k, v in blob.items()},
                        f"{mode} (legacy dconf)", None)
            finally:
                conn.close()
        except Exception as e:  # noqa: BLE001 - report, try next mode
            last = e
    return {}, None, last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL, help="AnkiConnect URL")
    ap.add_argument("--json", default="build/deck_preset_survey.json",
                    help="where to write the machine-readable survey")
    ap.add_argument("--no-db", action="store_true",
                    help="skip the collection-file fallback entirely")
    args = ap.parse_args()

    try:
        api = anki("version", url=args.url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot reach AnkiConnect at {args.url}: {e}", file=sys.stderr)
        print("Is Anki running with the AnkiConnect add-on enabled?", file=sys.stderr)
        return 1
    print(f"AnkiConnect API version {api}  ({args.url})\n")

    # ---- 1. deck -> preset, via AnkiConnect (authoritative) ----------------
    decks = sorted(anki("deckNames", url=args.url) or [])
    print(f"{len(decks)} deck(s) found.\n")

    deck_to_cfg = {}
    configs = {}
    failures = {}
    for deck in decks:
        try:
            cfg = anki("getDeckConfig", {"deck": deck}, url=args.url)
        except Exception as e:  # noqa: BLE001
            failures[deck] = str(e)
            continue
        cid = int(cfg["id"])
        deck_to_cfg[deck] = cid
        configs.setdefault(cid, cfg)

    if failures:
        print(f"WARNING: {len(failures)} deck(s) would not return a config:")
        for d, e in list(failures.items())[:10]:
            print(f"    {d}  --  {e}")
        print()

    # ---- 2. every preset, including unused --------------------------------
    all_presets = {cid: cfg.get("name", "?") for cid, cfg in configs.items()}
    source = "AnkiConnect (decks only -- unused presets NOT visible)"
    degraded = True

    for action in LIST_ALL_CANDIDATES:
        try:
            res = anki(action, url=args.url)
        except Exception:  # noqa: BLE001 - unsupported action, keep probing
            continue
        if isinstance(res, list) and res and isinstance(res[0], dict):
            all_presets = {int(c["id"]): c.get("name", "?") for c in res}
            for c in res:
                configs.setdefault(int(c["id"]), c)
            source, degraded = f"AnkiConnect '{action}'", False
            break

    db_note = None
    if degraded and not args.no_db:
        found = find_collection()
        if not found:
            db_note = "no collection.anki2 found in the standard locations"
        else:
            names, mode, err = presets_from_db(found[0])
            if names:
                for cid, name in names.items():
                    all_presets.setdefault(cid, name)
                source = f"collection.anki2 ({mode})"
                degraded = False
                db_note = f"read {found[0]}"
                if len(found) > 1:
                    db_note += f"  [{len(found)} profiles present; used the first]"
            else:
                db_note = f"could not read deck_config: {err}"

    print(f"Preset list source: {source}")
    if db_note:
        print(f"  {db_note}")
    if degraded:
        print("  ⚠ DEGRADED: presets used by zero decks cannot be reported in this mode.")
    print()

    # ---- 3. preset -> decks ------------------------------------------------
    usage = {cid: [] for cid in all_presets}
    for deck, cid in deck_to_cfg.items():
        usage.setdefault(cid, []).append(deck)

    print("=" * 78)
    print("  PRESETS")
    print("=" * 78)
    orphans = []
    for cid in sorted(all_presets, key=lambda c: (-len(usage.get(c, [])), all_presets[c])):
        name, used = all_presets[cid], sorted(usage.get(cid, []))
        tag = "  ← ORPHAN, no deck uses it" if not used else ""
        print(f"\n  {name}   [id={cid}]   {len(used)} deck(s){tag}")
        cfg = configs.get(cid)
        if cfg:
            bits = [f"{label}={fmt(dig(cfg, key))}" for key, label in SUMMARY_KEYS
                    if dig(cfg, key) is not None]
            if bits:
                print("      " + " · ".join(bits))
        elif not used:
            print("      (parameters unavailable — name read from the collection file)")
        for d in used:
            print(f"      {d}")
        if not used:
            orphans.append(name)

    # ---- 4. live deck tree -------------------------------------------------
    print("\n" + "=" * 78)
    print("  LIVE DECK TREE  (this is the ground truth the docs disagree about)")
    print("=" * 78)
    for deck in decks:
        depth = deck.count("::")
        leaf = deck.split("::")[-1]
        cid = deck_to_cfg.get(deck)
        pname = all_presets.get(cid, "?") if cid else "NO CONFIG"
        print(f"  {'  ' * depth}{leaf:<44s} → {pname}")

    # ---- 5. summary --------------------------------------------------------
    print("\n" + "=" * 78)
    print(f"  {len(decks)} decks · {len(all_presets)} presets · {len(orphans)} orphan(s)")
    if orphans:
        print("  Orphans: " + ", ".join(sorted(orphans)))
    print("=" * 78)

    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "ankiconnect_version": api,
        "preset_list_source": source,
        "degraded": degraded,
        "db_note": db_note,
        "decks": decks,
        "deck_to_config_id": deck_to_cfg,
        "config_id_to_name": all_presets,
        "usage": {str(k): sorted(v) for k, v in usage.items()},
        "orphans": sorted(orphans),
        "configs": {str(k): v for k, v in configs.items()},
        "deck_config_failures": failures,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
