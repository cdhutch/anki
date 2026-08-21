#!/usr/bin/env python3
"""tools/anki/inspect/export_deck_presets.py — one file per Anki deck preset.

Writes every preset in the collection to presets/<slug>.json so the repo mirrors
Anki. Per Craig 2026-08-20: every preset gets a file, with all parameters EXCEPT
the FSRS parameters, which Anki derives and updates itself.

Read-only with respect to Anki. Only writes files under --out.

WHY NO TIMESTAMP IN THE OUTPUT
------------------------------
Re-running this produces byte-identical files unless Anki actually changed, so
`export + git diff` is a drift detector: if a preset was hand-tweaked in the GUI,
the diff shows exactly which parameter moved. A timestamp would make every export
churn and destroy that property.

WHAT IS EXCLUDED, AND WHY
-------------------------
  fsrsParams6, fsrsParams5, fsrsWeights
      FSRS parameters are earned from a preset's own review history. They are
      configuration OUTPUT, not input -- committing them would mean an apply
      could overwrite an optimization with a stale vector. Worth knowing: eight
      UA presets and B737 currently share one bit-identical fsrsParams6, which
      can only be a clone artifact rather than a real optimization.
  id, mod, usn
      Collection-local. `id` is recorded in _meta for reference, but apply must
      resolve the live id by name -- a rebuilt collection assigns different ones.

Filtered decks are skipped. getDeckConfig on a filtered deck returns the DECK
where a config would be; those ids never appear in deck_config, which is how
they are told apart.

Usage
-----
  python tools/anki/inspect/export_deck_presets.py
  python tools/anki/inspect/export_deck_presets.py --out presets --url http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:8765"
EXCLUDE = ("fsrsParams6", "fsrsParams5", "fsrsWeights", "id", "mod", "usn")


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


def real_preset_ids():
    """{id: name} straight from deck_config -- the set that are genuinely presets."""
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
                return {int(r[0]): r[1] for r in rows}, None
            finally:
                conn.close()
        except Exception as e:  # noqa: BLE001
            last = e
    return {}, f"could not read deck_config: {last}"


def slug(name):
    s = name.replace("→", "-to-").replace("->", "-to-")
    s = re.sub(r"[^0-9A-Za-zЀ-ӿ]+", "-", s).strip("-").lower()
    return s or "preset"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--out", default="presets", help="output directory")
    args = ap.parse_args()

    try:
        anki("version", url=args.url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot reach AnkiConnect at {args.url}: {e}", file=sys.stderr)
        return 1

    real, err = real_preset_ids()
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        print("Cannot distinguish presets from filtered decks without it.",
              file=sys.stderr)
        return 1

    decks = sorted(anki("deckNames", url=args.url) or [])
    configs, usage, skipped = {}, {}, set()
    for deck in decks:
        try:
            cfg = anki("getDeckConfig", {"deck": deck}, url=args.url)
        except Exception as e:  # noqa: BLE001
            print(f"WARNING: {deck} would not return a config ({e})", file=sys.stderr)
            continue
        cid = int(cfg["id"])
        if cid not in real:
            skipped.add(deck)
            continue
        configs.setdefault(cid, cfg)
        usage.setdefault(cid, []).append(deck)

    missing = sorted(set(real) - set(configs))
    if missing:
        print(f"WARNING: {len(missing)} preset(s) exist but no deck uses them, so "
              f"their parameters cannot be read through AnkiConnect:", file=sys.stderr)
        for cid in missing:
            print(f"    {cid}  {real[cid]}", file=sys.stderr)
        print("Assign each to a deck and re-run, or prune them.", file=sys.stderr)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    used_slugs, written = {}, []
    for cid, cfg in sorted(configs.items(), key=lambda kv: kv[1].get("name", "").lower()):
        name = cfg.get("name", "?")
        base = slug(name)
        if base in used_slugs:                      # distinct names, same slug
            base = f"{base}-{cid}"
        used_slugs[base] = cid

        body = {k: v for k, v in cfg.items() if k not in EXCLUDE}
        doc = {
            "_meta": {
                "name": name,
                "anki_config_id": cid,
                "decks": sorted(usage.get(cid, [])),
                "excluded_keys": list(EXCLUDE),
                "note": "FSRS parameters are omitted on purpose -- Anki derives them "
                        "from this preset's own review history. id/mod/usn are "
                        "collection-local; apply resolves the live id by name.",
            },
            "config": body,
        }
        path = out / f"{base}.json"
        path.write_text(json.dumps(doc, indent=2, sort_keys=True,
                                   ensure_ascii=False) + "\n", encoding="utf-8")
        written.append((path.name, name, len(usage.get(cid, []))))

    print(f"{len(decks)} decks · {len(real)} presets in deck_config · "
          f"{len(written)} exported")
    if skipped:
        print(f"({len(skipped)} filtered deck(s) skipped -- not presets)")
    print()
    for fn, name, ndecks in written:
        print(f"  {fn:<44s} {name:<34s} {ndecks} deck(s)")
    print(f"\nWritten to {out}/")
    print("Re-running produces identical files unless Anki changed -- "
          "`git diff` after an export shows drift.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
