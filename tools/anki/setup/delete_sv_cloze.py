#!/usr/bin/env python3
"""Delete all legacy B737_SV_Cloze notes from Anki.

This is a one-way, destructive operation. A confirmation prompt is shown
before deletion. Pass --yes to skip the prompt (e.g. in scripts).

Usage
-----
  python tools/anki/setup/delete_sv_cloze.py
  python tools/anki/setup/delete_sv_cloze.py --yes
  python tools/anki/setup/delete_sv_cloze.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

LEGACY_MODEL = "B737_SV_Cloze"
LEGACY_DECK  = "B737::Systems::SV"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    ap.add_argument("--dry-run", action="store_true",
                    help="Find notes and report count; do not delete")
    args = ap.parse_args()

    url = args.url

    # ── Find all legacy cloze notes ─────────────────────────────────────────
    query = f'note:"{LEGACY_MODEL}"'
    print(f"Searching: {query}")
    note_ids: list[int] = anki_request("findNotes", {"query": query}, url=url) or []

    if not note_ids:
        print("No B737_SV_Cloze notes found. Nothing to delete.")
        return 0

    print(f"Found {len(note_ids)} note(s) with model '{LEGACY_MODEL}'.")

    if args.dry_run:
        print("[Dry run] No notes deleted.")
        return 0

    # ── Confirm ─────────────────────────────────────────────────────────────
    if not args.yes:
        answer = input(f"\nPermanently delete {len(note_ids)} notes? [yes/N]: ").strip().lower()
        if answer != "yes":
            print("Aborted.")
            return 0

    # ── Delete ───────────────────────────────────────────────────────────────
    print("Deleting ...")
    anki_request("deleteNotes", {"notes": note_ids}, url=url)
    print(f"Deleted {len(note_ids)} legacy cloze note(s).")

    # ── Optionally remove the now-empty legacy deck ─────────────────────────
    # (Anki auto-removes empty decks on sync, but this is explicit.)
    try:
        remaining = anki_request("findNotes", {"query": f'deck:"{LEGACY_DECK}"'}, url=url) or []
        if not remaining:
            anki_request("deleteDecks",
                         {"decks": [LEGACY_DECK], "cardsToo": True},
                         url=url)
            print(f"Removed empty deck '{LEGACY_DECK}'.")
    except Exception:
        pass  # Non-fatal; deck removal is cosmetic

    print("\nDone. Run 'make sve' to import the new MCQ cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
