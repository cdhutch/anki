#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
import urllib.request


ANKI_CONNECT = "http://localhost:8765"


def invoke(action: str, params: dict):
    request = json.dumps(
        {
            "action": action,
            "version": 6,
            "params": params,
        }
    ).encode("utf-8")

    response = urllib.request.urlopen(
        urllib.request.Request(ANKI_CONNECT, request)
    )

    result = json.load(response)

    if result.get("error"):
        raise Exception(result["error"])

    return result["result"]


def validate_row(row: dict[str, str]):
    model = row.get("Model", "").strip()
    deck = row.get("Deck", "").strip()
    note_id = row.get("NoteID", "").strip()
    text = row.get("Text", "").strip()

    if not model:
        raise ValueError("Missing Model field")
    if not deck:
        raise ValueError("Missing Deck field")
    if not note_id:
        raise ValueError("Missing NoteID field")
    if not text:
        raise ValueError("Missing Text field")

    if not re.search(r"\{\{c\d+::", text):
        raise ValueError(f"Missing cloze deletion in Text: {text}")


def find_existing_note_id(model: str, note_id: str):
    query = f'note:"{model}" NoteID:{note_id}'
    result = invoke("findNotes", {"query": query})
    return result[0] if result else None


def replace_tags(note_id_num: int, tags_str: str):
    current = invoke("notesInfo", {"notes": [note_id_num]})[0].get("tags", []) or []
    if current:
        invoke("removeTags", {"notes": [note_id_num], "tags": " ".join(current)})

    new_tags = tags_str.split()
    if new_tags:
        invoke("addTags", {"notes": [note_id_num], "tags": " ".join(new_tags)})


def add_note(row: dict[str, str]):
    note = {
        "deckName": row["Deck"],
        "modelName": row["Model"],
        "fields": {
            "NoteID": row["NoteID"],
            "Text": row["Text"],
            "Source Document": row["Source Document"],
            "Source Location": row["Source Location"],
        },
        "tags": row["Tags"].split(),
        "options": {
            "allowDuplicate": False,
        },
    }
    return invoke("addNote", {"note": note})


def update_note(note_id_num: int, row: dict[str, str]):
    invoke(
        "updateNoteFields",
        {
            "note": {
                "id": note_id_num,
                "fields": {
                    "NoteID": row["NoteID"],
                    "Text": row["Text"],
                    "Source Document": row["Source Document"],
                    "Source Location": row["Source Location"],
                },
            }
        },
    )

    replace_tags(note_id_num, row["Tags"])


def main(tsv_file: str):
    with open(tsv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for i, row in enumerate(reader, start=1):
            validate_row(row)

            existing = find_existing_note_id(row["Model"], row["NoteID"])

            if existing:
                update_note(existing, row)
                print(f"Updated row {i}: {row['NoteID']}")
            else:
                nid = add_note(row)
                print(f"Added row {i}: {row['NoteID']} -> {nid}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: cloze_import_to_anki.py <tsv_file>")
    main(sys.argv[1])