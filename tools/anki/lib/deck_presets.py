"""tools/anki/lib/deck_presets.py — shared helpers for the deck-preset tools.

The preset VALUES live in presets/<slug>.json, one file per preset, exported
from live Anki. Per Craig 2026-08-20: every preset in Anki is represented by a
file carrying all parameters except the FSRS ones. This module deliberately
holds no preset data of its own -- an earlier draft did, and that made it a
second copy of the same values, which is the drift this whole exercise removed.

Shared by:
  tools/anki/inspect/export_deck_presets.py   Anki  -> files
  tools/anki/setup/create_deck_presets.py     files -> Anki
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Never round-tripped. FSRS parameters are earned from a preset's own review
# history -- configuration output, not input -- so writing them back could
# overwrite a real optimization with a stale vector. id/mod/usn are
# collection-local; the live id is resolved by name at apply time.
EXCLUDE = ("fsrsParams6", "fsrsParams5", "fsrsWeights", "id", "mod", "usn")


def slug(name: str) -> str:
    """Filename-safe stem for a preset name. Names carry →, ->, spaces, brackets
    and parentheses; the true name is kept inside the file, never inferred back
    from the filename."""
    s = name.replace("→", "-to-").replace("->", "-to-")
    s = re.sub(r"[^0-9A-Za-zЀ-ӿ]+", "-", s).strip("-").lower()
    return s or "preset"


def dig(cfg: dict, dotted: str):
    """Read a dotted key from a nested config dict; None if any hop is absent."""
    cur = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def put(cfg: dict, dotted: str, value) -> None:
    """Write a dotted key into a nested config dict, creating intermediate dicts."""
    parts = dotted.split(".")
    cur = cfg
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def flatten(cfg: dict, prefix: str = ""):
    """Nested config -> {dotted key: scalar}. Lists are leaves, not descended."""
    out = {}
    for k, v in cfg.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        else:
            out[key] = v
    return out


def load_presets(directory) -> dict:
    """{preset name: {"path", "meta", "config"}} from presets/*.json.

    Keyed by the name inside the file, not by filename -- the slug is lossy and
    exists only to be a legal filename.
    """
    out = {}
    for path in sorted(Path(directory).glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        meta, config = doc.get("_meta", {}), doc.get("config", {})
        name = meta.get("name") or config.get("name")
        if not name:
            raise ValueError(f"{path}: no preset name in _meta or config")
        if name in out:
            raise ValueError(
                f"{path}: preset name {name!r} also defined in {out[name]['path']}"
            )
        out[name] = {"path": path, "meta": meta, "config": config}
    return out
