#!/usr/bin/env python3
"""Export UA_Verb and UA_Conjugation notes from Anki to CNSF canonical format.

Preserves all field data and tags for version control + future re-import.
Generates .md files ready for review, migration, or re-import via ua_verb_import.py.

Output locations:
  - UA_Verb exports: domains/ua/anki/notes/verbs/exported/ua-verb-*.md
  - UA_Conjugation exports: domains/ua/anki/notes/verbs/exported/ua-conj-*.md

Usage (with Anki open + AnkiConnect running):
    python tools/anki/sync/ua_verb_export.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
EXPORT_DIR = Path(__file__).resolve().parents[3] / "domains/ua/anki/notes/verbs/exported"


class PlainStringDumper(yaml.SafeDumper):
    """Custom YAML dumper that avoids unnecessary quotes."""
    pass


def _str_representer(dumper, data):
    """Represent strings without quotes unless necessary."""
    if any(c in data for c in "#{}[]'\"@`|&*!") or data.startswith(("!", "&", "*", "-", "?", ":")):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")


PlainStringDumper.add_representer(str, _str_representer)


def export_note(note_id: int, model_name: str, fields_info: dict, tags: list[str]) -> str:
    """Generate CNSF markdown for a single note.

    Returns the markdown text (frontmatter + body).
    """
    # Extract note_id from fields (usually 'NoteID' or 'VerbForm_ID')
    note_id_field = None
    for key in ["NoteID", "note_id", "VerbForm_ID"]:
        if key in fields_info:
            val = fields_info[key]
            if isinstance(val, dict):
                val = val.get("value", "")
            if val and val.strip():
                note_id_field = val.strip()
                break

    if not note_id_field:
        note_id_field = f"anki-{note_id}"

    # Build fields dict
    fields = {}
    for key, field_data in fields_info.items():
        if isinstance(field_data, dict):
            val = field_data.get("value", "")
        else:
            val = field_data
        # Normalize: convert None to empty string
        fields[key] = "" if val is None else str(val).strip()

    # Build frontmatter
    frontmatter = {
        "schema": "cnsf/v0",
        "domain": "ua",
        "note_type": model_name.lower().replace("_", "_"),
        "note_id": note_id_field,
        "anki": {
            "model": model_name,
            "deck": "UA::Verbs",  # Default; may need override
        },
        "tags": tags or [],
        "fields": fields,
    }

    # Dump YAML
    yaml_text = yaml.dump(
        frontmatter,
        Dumper=PlainStringDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=88,
    ).strip("\n")

    # Combine
    markdown = f"---\n{yaml_text}\n---\n"
    return markdown


def export_model(model_name: str, output_prefix: str):
    """Export all notes of a given model to CNSF files."""
    print(f"\nExporting {model_name}...")

    # Find all notes of this model
    query = f'note:"{model_name}"'
    note_ids = anki_request("findNotes", {"query": query}, url=ANKI_URL) or []
    print(f"  Found {len(note_ids)} notes")

    if not note_ids:
        return 0

    # Get full note info
    notes_info = anki_request("notesInfo", {"notes": note_ids}, url=ANKI_URL) or []

    exported = 0
    for note_info in notes_info:
        try:
            anki_id = note_info.get("noteId")
            fields = note_info.get("fields", {})
            tags = note_info.get("tags", [])

            # Generate CNSF markdown
            markdown = export_note(anki_id, model_name, fields, tags)

            # Determine output filename
            # Try to use NoteID field if present and meaningful
            note_id_val = None
            for key in ["NoteID", "note_id", "VerbForm_ID"]:
                if key in fields:
                    val = fields[key]
                    if isinstance(val, dict):
                        val = val.get("value", "")
                    if val and val.strip() and not val.startswith("anki-"):
                        note_id_val = val.strip()
                        break

            if not note_id_val:
                note_id_val = f"{output_prefix}-{anki_id}"

            # Sanitize filename
            filename = note_id_val.replace("/", "_").replace(" ", "_").lower() + ".md"
            output_path = EXPORT_DIR / filename

            # Write file
            output_path.write_text(markdown, encoding="utf-8")
            print(f"  ✓ {filename}")
            exported += 1

        except Exception as e:
            print(f"  ✗ Error exporting note {anki_id}: {e}")

    return exported


def main():
    """Export UA_Verb and UA_Conjugation notes to CNSF."""
    print("Exporting Ukrainian verb notes to CNSF format...\n")

    # Create export directory
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Export directory: {EXPORT_DIR}\n")

    total = 0

    # Export UA_Verb
    count = export_model("UA_Verb", "ua-verb")
    total += count

    # Export UA_Conjugation
    count = export_model("UA_Conjugation", "ua-conj")
    total += count

    print(f"\n✓ Exported {total} notes total")
    print(f"\nNext steps:")
    print(f"  1. Review exported files in: {EXPORT_DIR}")
    print(f"  2. Migrate UA_Conjugation notes to UA_Verb format (use ua_conjugation_to_verb.py)")
    print(f"  3. Commit canonical CNSF files to git")


if __name__ == "__main__":
    main()
