#!/usr/bin/env python3
"""fix_anki_crew_role_tags.py — Standardize legacy crew_role/role/duty tags in Anki.

Queries Anki directly via AnkiConnect and replaces all legacy tag variants
with the four canonical crew_role tags. Run once after source-file
standardization to bring Anki's tag database in sync.

Usage:
    python tools/anki/sync/fix_anki_crew_role_tags.py --dry-run
    python tools/anki/sync/fix_anki_crew_role_tags.py
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# Tag mapping
# ---------------------------------------------------------------------------

# Maps legacy tag → canonical tag.  Empty string means remove the tag.
TAG_RENAMES: dict[str, str] = {
    "role:pf":            "crew_role:pilot_flying",
    "role:pm":            "crew_role:pilot_monitoring",
    "crew_role:pf":       "crew_role:pilot_flying",
    "crew_role:pm":       "crew_role:pilot_monitoring",
    "duty:pf":            "crew_role:pilot_flying",
    "duty:pm":            "crew_role:pilot_monitoring",
    "role:captain":       "crew_role:captain",
    "role:first_officer": "crew_role:first_officer",
    "crew_role:fo":       "crew_role:first_officer",
    "crew_role:all":      "",   # remove
    "role:crew":          "",   # remove
}

# Anki may split "crew_role: pf" (space after colon) into two separate tags.
# Handle both the compound form (if stored as-is) and the split form.
EXTRA_RENAMES: dict[str, str] = {
    "crew_role:":  "",   # orphaned half of "crew_role: pf" — remove
    "pf":          "",   # bare "pf" tag — remove (may be the other half)
    "pm":          "",   # bare "pm" tag — remove
}

# ---------------------------------------------------------------------------
# AnkiConnect helpers
# ---------------------------------------------------------------------------

def anki_request(action: str, params: dict | None = None) -> Any:
    payload = {"action": action, "version": 6, "params": params or {}}
    req = urllib.request.Request(
        ANKI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error [{action}]: {data['error']}")
    return data.get("result")


def get_all_tags() -> list[str]:
    return anki_request("getTags") or []


def find_notes_with_tag(tag: str) -> list[int]:
    return anki_request("findNotes", {"query": f"tag:{tag}"}) or []


def replace_tag_on_notes(note_ids: list[int], old_tag: str, new_tag: str) -> None:
    """Replace or remove a tag on a set of notes."""
    anki_request("replaceTags", {
        "notes": note_ids,
        "tag_to_replace": old_tag,
        "replace_with_tag": new_tag,
    })


def clear_unused_tags() -> None:
    anki_request("clearUnusedTags")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(dry_run: bool) -> None:
    print(f"{'DRY RUN — ' if dry_run else ''}Standardizing crew_role tags in Anki\n")

    all_tags = set(get_all_tags())
    all_renames = {**TAG_RENAMES, **EXTRA_RENAMES}

    total_notes_affected = 0

    for old_tag, new_tag in sorted(all_renames.items()):
        if old_tag not in all_tags:
            continue  # tag doesn't exist in Anki — skip silently

        note_ids = find_notes_with_tag(old_tag)
        if not note_ids:
            continue

        action = f"→ {new_tag}" if new_tag else "→ (remove)"
        print(f"  {old_tag!r:35s} {action}  [{len(note_ids)} note(s)]")

        if not dry_run:
            replace_tag_on_notes(note_ids, old_tag, new_tag)

        total_notes_affected += len(note_ids)

    if not dry_run:
        clear_unused_tags()
        print(f"\nDone. {total_notes_affected} note(s) updated. Unused tags cleared.")
    else:
        print(f"\nDry run complete. {total_notes_affected} note(s) would be updated.")
        print("Re-run without --dry-run to apply.")

    # Report any remaining unexpected role-related tags
    remaining = [
        t for t in get_all_tags()
        if any(t.startswith(p) for p in ("role:", "duty:"))
        or t in ("crew_role:fo", "crew_role:pf", "crew_role:pm", "crew_role:all")
    ]
    if remaining:
        print(f"\n⚠  Unexpected role-related tags still present in Anki:")
        for t in sorted(remaining):
            print(f"     {t!r}")
    else:
        print("\n✓  No unexpected role-related tags remaining.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Standardize legacy crew_role/role/duty tags in Anki."
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying Anki.",
    )
    args = ap.parse_args()

    try:
        run(dry_run=args.dry_run)
    except OSError as e:
        print(f"\nCannot reach AnkiConnect at {ANKI_URL}: {e}")
        print("Make sure Anki is open and the AnkiConnect add-on is active.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
