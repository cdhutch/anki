#!/usr/bin/env python3
"""Delete the old single-form PVOM notes orphaned by the 2026-07-21
consolidation (NoteID field values ua-pvom-0012 through ua-pvom-0022).
Run list_orphaned_pvom_notes.py first and review its output -- this is
destructive and not undoable via AnkiConnect."""

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
        all_ids.extend(ids)

    if not all_ids:
        print("Nothing to delete -- no orphaned notes found.")
        return

    print(f"Deleting {len(all_ids)} notes: {all_ids}")
    result = anki_request("deleteNotes", {"notes": all_ids})
    if result and not result.get("error"):
        print("✓ Deleted.")
    else:
        print(f"✗ Delete failed: {result}")

if __name__ == "__main__":
    main()
