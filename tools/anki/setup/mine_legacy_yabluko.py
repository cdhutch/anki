#!/usr/bin/env python3
"""
mine_legacy_yabluko.py — Pull every note from the legacy
"Legacy::Ukrainian Active::Яблуко" deck via AnkiConnect and dump it to a
searchable datafile (JSON + a flat grep-friendly text file).

Purpose: before drafting a new CNSF lexeme note, or when flagging a
confusable-candidate tag on a note, search this datafile for prior
exposure to a word -- the old Front/Back gloss, and (for Cloze notes)
whatever confusable-distinction context you already wrote there. Cloze
notes are the richest source for this, since that's reportedly where the
most-confused word pairs got called out directly.

Requires: Anki open with AnkiConnect add-on active on port 8765.

Usage:
    python3 tools/anki/setup/mine_legacy_yabluko.py [output_dir]

Default output directory: tools/anki/setup/
  legacy_yabluko_notes.json  -- structured, one record per note
  legacy_yabluko_notes.txt   -- flat, human-grep-friendly dump
"""

import json
import sys
import urllib.request
from pathlib import Path

DECK = "Legacy::Ukrainian Active::Яблуко"
SCRIPT_DIR = Path(__file__).parent


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen("http://localhost:8765", payload) as r:
        result = json.loads(r.read())
    if result.get("error"):
        raise Exception(result["error"])
    return result["result"]


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "legacy_yabluko_notes.json"
    txt_path = out_dir / "legacy_yabluko_notes.txt"

    try:
        # deck:"X" matches the deck and all of its subdecks in Anki's
        # search syntax, so this covers everything under Яблуко.
        note_ids = anki("findNotes", query=f'deck:"{DECK}"')
    except Exception as e:
        print(f"Could not reach AnkiConnect: {e}")
        print("Make sure Anki is open and the AnkiConnect add-on is installed.")
        return

    if not note_ids:
        print(f'No notes found in deck "{DECK}". Check the deck name (case/spelling).')
        return

    print(f"Found {len(note_ids)} notes. Fetching fields...")
    notes = anki("notesInfo", notes=note_ids)

    records = []
    by_model = {}
    for n in notes:
        model = n["modelName"]
        by_model[model] = by_model.get(model, 0) + 1
        fields = {k: v["value"] for k, v in n["fields"].items()}
        records.append({
            "noteId": n["noteId"],
            "modelName": model,
            "tags": n["tags"],
            "fields": fields,
        })

    records.sort(key=lambda r: r["modelName"])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(f"=== Note {r['noteId']} ({r['modelName']}) ===\n")
            if r["tags"]:
                f.write(f"Tags: {', '.join(r['tags'])}\n")
            for fname, fval in r["fields"].items():
                if fval.strip():
                    f.write(f"{fname}: {fval}\n")
            f.write("\n")

    print(f"\nWrote {len(records)} notes to:")
    print(f"  {json_path}")
    print(f"  {txt_path}")
    print("\nNote types found:")
    for model, count in sorted(by_model.items()):
        print(f"  {model}: {count}")


if __name__ == "__main__":
    main()
