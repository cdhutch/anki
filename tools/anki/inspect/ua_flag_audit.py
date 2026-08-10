#!/usr/bin/env python3
"""Flagged Card Fix Workflow -- Phase 1 (query) and Phase 3 (apply) tooling.

See CLAUDE-flag-audit.md for the full three-phase workflow. Phase 2 (interactive
review/fix with Claude, one flagged note at a time) is a conversation, not
something this script automates -- this script brackets that conversation:
it produces the manifest that kicks Phase 2 off (--query) and re-syncs +
clears flags once Phase 2's fixes have been written into the CNSF files
(--apply).

Usage:
    # Phase 1: find every red/orange-flagged card in the UA deck tree, print
    # a summary, and write a manifest mapping each flagged note to its
    # canonical CNSF file path.
    python tools/anki/inspect/ua_flag_audit.py --query

    # Phase 3: after Phase 2's fixes are written into the CNSF files listed
    # in the manifest, re-import each corrected note via the right per-type
    # import script, then remove flags from every card in the manifest.
    python tools/anki/inspect/ua_flag_audit.py --apply

    # Custom manifest location (default: flagged_cards_manifest.json in the
    # repo root -- transient working state, not meant to be committed):
    python tools/anki/inspect/ua_flag_audit.py --query --manifest my.json
    python tools/anki/inspect/ua_flag_audit.py --apply --manifest my.json

    # Re-import without removing flags yet (e.g. to sanity-check a fix before
    # clearing its flag):
    python tools/anki/inspect/ua_flag_audit.py --apply --no-unmark
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request, FLAG_RED, FLAG_ORANGE  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# Same deck-tree scope as the sync scripts' red/orange flag check
# (get_flagged_note_ids_by_color in tsv_to_anki.py) -- kept as a literal here
# rather than imported, since that helper returns bare sets of Anki note IDs
# per color and this tool needs per-card flag color + template info that
# helper discards.
FLAG_DECK_QUERY = "deck:UA::*"

FLAG_NAMES = {FLAG_RED: "red", FLAG_ORANGE: "orange"}

REPO_ROOT = Path(__file__).resolve().parents[3]
NOTES_ROOT = REPO_ROOT / "domains/ua/anki/notes"

# NoteID prefix -> (search root, recursive?, import script relative to repo root).
# lexemes are nested by textbook/chapter (not derivable from the ID alone, so
# recursive search is required -- same reasoning as LEXEME_ROOT in
# ua_lexeme_import.py); verbs/grammar/visual are flat single-level directories.
NOTE_TYPE_MAP = {
    "ua-lexeme": (NOTES_ROOT / "lexemes", True, "tools/anki/sync/ua_lexeme_import.py"),
    "ua-verb": (NOTES_ROOT / "verbs", False, "tools/anki/sync/ua_verb_import.py"),
    "ua-grammar": (NOTES_ROOT / "grammar", False, "tools/anki/sync/ua_grammar_import.py"),
    "ua-visual": (NOTES_ROOT / "visual", False, "tools/anki/sync/ua_visual_import.py"),
}


def _note_type_entry(note_id: str):
    for prefix, entry in NOTE_TYPE_MAP.items():
        if note_id.startswith(prefix + "-"):
            return entry
    return None


def find_cnsf_path(note_id: str) -> Path | None:
    """Map a CNSF NoteID (e.g. 'ua-lexeme-0042') to its canonical .md file path."""
    entry = _note_type_entry(note_id)
    if entry is None:
        return None
    root, recursive, _script = entry
    pattern = f"{note_id}.md"
    matches = list(root.rglob(pattern)) if recursive else list(root.glob(pattern))
    return matches[0] if matches else None


def import_script_for(note_id: str) -> str | None:
    entry = _note_type_entry(note_id)
    return entry[2] if entry else None


def query_flagged_cards() -> list[dict]:
    """Query every red/orange-flagged card in the UA deck tree, grouped by
    note (a note with two flagged cards -- e.g. UA->EN red, Compare orange --
    is one manifest entry recording both flag colors), each with its CNSF
    file path resolved.
    """
    flag_clause = " OR ".join(f"flag:{f}" for f in (FLAG_RED, FLAG_ORANGE))
    card_ids = anki_request("findCards", {"query": f"{FLAG_DECK_QUERY} ({flag_clause})"}, url=ANKI_URL) or []
    if not card_ids:
        return []
    cards_info = anki_request("cardsInfo", {"cards": card_ids}, url=ANKI_URL) or []

    by_note: dict[int, dict] = {}
    for c in cards_info:
        nid = c["note"]
        entry = by_note.setdefault(nid, {
            "anki_note_id": nid,
            "note_id": c["fields"].get("NoteID", {}).get("value", ""),
            "model": c["modelName"],
            "flag_values": set(),
            "cards": [],
        })
        entry["flag_values"].add(c["flags"])
        entry["cards"].append({
            "card_id": c["cardId"],
            "ord": c["ord"],
            "flag": c["flags"],
            "flag_name": FLAG_NAMES.get(c["flags"], f"flag{c['flags']}"),
        })

    results = []
    for entry in by_note.values():
        note_id = entry["note_id"]
        path = find_cnsf_path(note_id) if note_id else None
        results.append({
            "anki_note_id": entry["anki_note_id"],
            "note_id": note_id,
            "model": entry["model"],
            "flag_colors": sorted(FLAG_NAMES.get(f, f"flag{f}") for f in entry["flag_values"]),
            "cnsf_path": str(path.relative_to(REPO_ROOT)) if path else None,
            "cards": entry["cards"],
        })
    results.sort(key=lambda r: r["note_id"])
    return results


def cmd_query(args):
    results = query_flagged_cards()
    if not results:
        print("No flagged cards found in the UA deck tree.")
        return

    red = sum(1 for r in results if "red" in r["flag_colors"])
    orange = sum(1 for r in results if "orange" in r["flag_colors"])
    overlap_note = " (some notes have both)" if red + orange != len(results) else ""
    print(f"{len(results)} flagged note(s): {red} red, {orange} orange{overlap_note}\n")

    unresolved = [r for r in results if r["cnsf_path"] is None]
    for r in results:
        path = r["cnsf_path"] or "!! NO CNSF FILE FOUND -- fix manually !!"
        print(f"  [{'/'.join(r['flag_colors']):>11}] {r['note_id']:<20} {path}")
    if unresolved:
        print(f"\nWarning: {len(unresolved)} flagged note(s) could not be mapped to a CNSF file --"
              " check manually (deleted from CNSF but not Anki? NoteID typo? wrong note type prefix?).")

    out_path = Path(args.manifest)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nManifest written to {out_path}")
    print("Next: work through each note in Phase 2 (fix the CNSF file for each), "
          "then run --apply once fixes are made.")


def cmd_apply(args):
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path} -- run --query first.")
        sys.exit(1)
    results = json.loads(manifest_path.read_text(encoding="utf-8"))

    paths_by_script: dict[str, list[str]] = {}
    skipped = []
    for r in results:
        if not r["cnsf_path"]:
            skipped.append(r["note_id"])
            continue
        script = import_script_for(r["note_id"])
        if not script:
            skipped.append(r["note_id"])
            continue
        paths_by_script.setdefault(script, []).append(r["cnsf_path"])

    if skipped:
        print(f"Skipping {len(skipped)} note(s) with no resolvable CNSF path/script: {skipped}")

    def resync():
        for script, paths in paths_by_script.items():
            print(f"\nRe-importing {len(paths)} note(s) via {script}:")
            cmd = [sys.executable, script, *paths]
            print("  " + " ".join(cmd))
            subprocess.run(cmd, check=True)

    # Pass 1: sync corrected content. The suspend policy inside each import
    # script still sees these notes as flagged at this point (flags haven't
    # been cleared yet), so red-flagged notes stay suspended here -- expected,
    # not a bug. Orange-only notes were never suspended by the flag check
    # (2026-08-10, per Craig -- see SUSPEND_FLAG_COLORS in tsv_to_anki.py), so
    # there's nothing to preserve for those; they just get their content fixed.
    print("--- Pass 1: sync corrected content ---")
    resync()

    if args.no_unmark:
        print("\n--no-unmark set: flags left in place, notes remain suspended "
              "(their content is fixed, but a future --apply run -- or any "
              "other re-sync -- won't unsuspend them until flags are cleared).")
        return

    # There is no batch "unmark"/"setFlag" action in AnkiConnect (verified
    # 2026-08-01 -- an earlier draft of this script called a nonexistent
    # "unmark" action, taken from CLAUDE-flag-audit.md's aspirational,
    # never-tested sketch). The real mechanism is setSpecificValueOfCard,
    # which takes ONE card id at a time and requires newValues as actual
    # ints, not strings -- ["0"] silently no-ops (returns True but leaves
    # the flag unchanged), [0] actually clears it. Confirmed against a live
    # flagged card before wiring this in.
    card_ids = [c["card_id"] for r in results for c in r["cards"]]
    if card_ids:
        print(f"\nRemoving flags from {len(card_ids)} card(s)...")
        failed = []
        for cid in card_ids:
            ok = anki_request(
                "setSpecificValueOfCard",
                {"card": cid, "keys": ["flags"], "newValues": [0]},
                url=ANKI_URL,
            )
            if not (ok and ok[0]):
                failed.append(cid)
        if failed:
            print(f"WARNING: failed to clear flag on {len(failed)} card(s): {failed}")
        else:
            print("Done.")

    # Pass 2: re-sync the same notes now that flags are cleared. Each import
    # script's suspend policy is declarative -- computed fresh from current
    # tags + a fresh flag query every run -- so this pass is what actually
    # unsuspends them (assuming status:verified), rather than leaving that to
    # whatever the next unrelated sync happens to be. Deliberately a second
    # call into the same import scripts rather than duplicating their suspend
    # logic here, so there's one source of truth for the suspend policy.
    print("\n--- Pass 2: re-sync to pick up cleared flags (unsuspends fixed notes) ---")
    resync()


def main():
    parser = argparse.ArgumentParser(description="Flagged Card Fix Workflow tooling (see CLAUDE-flag-audit.md).")
    parser.add_argument("--query", action="store_true", help="Phase 1: query flagged cards, print summary, write manifest")
    parser.add_argument("--apply", action="store_true", help="Phase 3: re-import corrected notes and remove flags")
    parser.add_argument("--manifest", default="flagged_cards_manifest.json",
                         help="Manifest file path (default: flagged_cards_manifest.json in repo root; transient, not meant to be committed)")
    parser.add_argument("--no-unmark", action="store_true", help="With --apply, skip removing flags")
    args = parser.parse_args()

    if args.query == args.apply:  # both False or both True
        parser.error("specify exactly one of --query or --apply")

    if args.query:
        cmd_query(args)
    else:
        cmd_apply(args)


if __name__ == "__main__":
    main()
