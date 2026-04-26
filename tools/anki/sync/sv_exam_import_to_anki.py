#!/usr/bin/env python3
"""Import SV exam-mode TSV notes into Anki via AnkiConnect.

Supports B737_SV_MCQ and B737_SV_TF note types.
Reuses anki_request() from tsv_to_anki.py — that file is not modified.

Usage:
    python tools/anki/sync/sv_exam_import_to_anki.py --mcq build/sve-mcq-acars.tsv
    python tools/anki/sync/sv_exam_import_to_anki.py --tf  build/sve-tf-acars.tsv
    python tools/anki/sync/sv_exam_import_to_anki.py --mcq build/sve-mcq-acars.tsv --tf build/sve-tf-acars.tsv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Add repo root to sys.path so tools.anki.sync is importable when this
# script is run directly (e.g. from the Makefile as a plain script).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

DECK_MCQ = "B737::Systems_Verification::MCQ"
DECK_TF = "B737::Systems_Verification::TF"
MODEL_MCQ = "B737_SV_MCQ"
MODEL_TF = "B737_SV_TF"
ANKI_CONNECT_DEFAULT = "http://127.0.0.1:8765"

# Fields written to the Anki note (Tags excluded — sent as native Anki tags).
MCQ_FIELDS = [
    "NoteID", "Text", "Choice1", "Choice2", "Choice3", "Choice4",
    "CorrectChoice", "SourceDocument", "OriginalNoteID",
]
TF_FIELDS = [
    "NoteID", "Text", "CorrectAnswer", "SourceDocument", "OriginalNoteID",
]


# ---------------------------------------------------------------------------
# AnkiConnect helpers
# ---------------------------------------------------------------------------

def _find_existing(note_id: str, model_name: str, url: str) -> int | None:
    """Return the Anki numeric note ID for an existing note, or None."""
    query = f'note:"{model_name}" NoteID:"{note_id}"'
    result = anki_request("findNotes", {"query": query}, url=url)
    return int(result[0]) if result else None


def _set_tags(anki_id: int, tags: list[str], url: str) -> None:
    """Replace the tag set on an existing note."""
    current = anki_request("getNoteTags", {"note": anki_id}, url=url) or []
    if current:
        anki_request("removeTags", {"notes": [anki_id], "tags": " ".join(current)}, url=url)
    if tags:
        anki_request("addTags", {"notes": [anki_id], "tags": " ".join(tags)}, url=url)


def _upsert(row: dict[str, str], model_name: str, field_names: list[str], url: str) -> None:
    note_id = row.get("NoteID", "").strip()
    if not note_id:
        raise ValueError("Missing NoteID")

    fields = {k: row.get(k, "") for k in field_names}
    tags = [t for t in row.get("Tags", "").split() if t]

    existing = _find_existing(note_id, model_name, url)
    if existing:
        anki_request("updateNoteFields", {"note": {"id": existing, "fields": fields}}, url=url)
        _set_tags(existing, tags, url)
        print(f"  Updated : {note_id}")
    else:
        deck = DECK_MCQ if model_name == MODEL_MCQ else DECK_TF
        nid = anki_request(
            "addNote",
            {
                "note": {
                    "deckName": deck,
                    "modelName": model_name,
                    "fields": fields,
                    "tags": tags,
                    "options": {"allowDuplicate": False, "duplicateScope": "deck"},
                }
            },
            url=url,
        )
        print(f"  Added   : {note_id} → {nid}")


# ---------------------------------------------------------------------------
# TSV import
# ---------------------------------------------------------------------------

def _import_tsv(tsv_path: Path, model_name: str, field_names: list[str], url: str) -> None:
    with tsv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    if not rows:
        print(f"{model_name}: {tsv_path.name} has no data rows — skipping.")
        return

    print(f"Importing {len(rows)} {model_name} note(s) from {tsv_path.name} ...")
    for row in rows:
        _upsert(row, model_name, field_names, url)
    print(f"Done ({len(rows)} note(s)).\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Import SV exam-mode TSV notes into Anki via AnkiConnect."
    )
    ap.add_argument("--mcq", help="Path to MCQ TSV file")
    ap.add_argument("--tf", help="Path to T/F TSV file")
    ap.add_argument("--anki-url", default=ANKI_CONNECT_DEFAULT)
    args = ap.parse_args()

    if not args.mcq and not args.tf:
        raise SystemExit("Provide at least one of --mcq or --tf.")

    if args.mcq:
        _import_tsv(Path(args.mcq), MODEL_MCQ, MCQ_FIELDS, args.anki_url)
    if args.tf:
        _import_tsv(Path(args.tf), MODEL_TF, TF_FIELDS, args.anki_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
