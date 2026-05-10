#!/usr/bin/env python3
import csv
import json
import urllib.request
import sys


ANKI_CONNECT = "http://localhost:8765"


def invoke(action, params):
    request = json.dumps({
        "action": action,
        "version": 6,
        "params": params
    }).encode("utf-8")

    response = urllib.request.urlopen(
        urllib.request.Request(ANKI_CONNECT, request)
    )

    result = json.load(response)

    if result.get("error"):
        raise Exception(result["error"])

    return result["result"]


def validate_row(row):
    text = row.get("Text", "")
    if not text:
        raise ValueError("Missing Text field")
    if "{{c1::" not in text and "{{c2::" not in text and "{{c3::" not in text:
        raise ValueError(f"Missing cloze deletion in Text: {text}")
    if not row.get("NoteID", "").strip():
        raise ValueError("Missing NoteID")


def find_existing_note_id(note_id):
    query = f'note:"B737_SV_Cloze" NoteID:{note_id}'
    result = invoke("findNotes", {"query": query})
    return result[0] if result else None


def add_note(row):
    note = {
        "deckName": "B737::Systems::SV",
        "modelName": "B737_SV_Cloze",
        "fields": {
            "NoteID": row["NoteID"],
            "Text": row["Text"],
            "Source Document": row["Source Document"],
            "Source Location": row["Source Location"],
        },
        "tags": row["Tags"].split(),
        "options": {
            "allowDuplicate": False
        }
    }
    return invoke("addNote", {"note": note})


def update_note(note_id_num, row):
    invoke("updateNoteFields", {
        "note": {
            "id": note_id_num,
            "fields": {
                "NoteID": row["NoteID"],
                "Text": row["Text"],
                "Source Document": row["Source Document"],
                "Source Location": row["Source Location"],
            }
        }
    })

    # Replace tags with the canonical set from TSV

def main(tsv_file):
    with open(tsv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for i, row in enumerate(reader, start=1):
            validate_row(row)

            existing = find_existing_note_id(row["NoteID"])

            if existing:
                update_note(existing, row)
                print(f"Updated row {i}: {row['NoteID']}")
            else:
                nid = add_note(row)
                print(f"Added row {i}: {row['NoteID']} -> {nid}")


if __name__ == "__main__":
    main(sys.argv[1])