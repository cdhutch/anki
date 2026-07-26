#!/usr/bin/env python3
"""List (never deletes) the old single-form PVOM notes left orphaned by the
2026-07-21 4-template consolidation (NoteID field values ua-pvom-0012 through
ua-pvom-0022 -- these had no corresponding file after the rewrite, so they
were never updated, yet still generate cards for the 4 new templates)."""

import json
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"
ORPHAN_NOTE_IDS = [f"ua-pvom-{n:04d}" for n in range(12, 23)]

def anki_request(action, params=None):
    body = {"action": action, "version": 6}
    if params:
        body["params"] = params
    resp = urllib.request.urlopen(
        urllib.request.Request(ANKI_URL, data=json.dumps(body).encode("utf-8"))
    )
    return json.loads(resp.read())

def main():
    all_ids = []
    for noteid in ORPHAN_NOTE_IDS:
        result = anki_request(
            "findNotes",
            {"query": f'"note:UA_PVOM_Infinitive" "NoteID:{noteid}"'},
        )
        ids = result.get("result", []) if result else []
        if not ids:
            print(f"{noteid}: not found (already gone)")
            continue
        info = anki_request("notesInfo", {"notes": ids})
        for note in info.get("result", []):
            f = note["fields"]
            base = f.get("Base_Form_Label", {}).get("value", "?")
            inf = f.get("Infinitive_UA", {}).get("value", "?")
            prefix = f.get("Prefix", {}).get("value", "?")
            print(f"{noteid}: anki_id={note['noteId']} prefix={prefix!r} base={base!r} infinitive={inf!r}")
            all_ids.append(note["noteId"])

    print()
    print(f"Total orphaned notes found: {len(all_ids)}")
    print("Anki note IDs:", all_ids)
    print()
    print("If this list looks right (11 old single-form notes, none of them")
    print("cards you actually study), delete them with:")
    print(f"  python3 tools/anki/inspect/delete_orphaned_pvom_notes.py")

if __name__ == "__main__":
    main()
