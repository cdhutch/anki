#!/usr/bin/env python3
"""Update note_id fields in ua-verb CNSF files from 5-digit to 4-digit format."""

import re
from pathlib import Path

def update_noteids():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    # Find all ua-verb files
    verb_files = sorted(verbs_dir.glob("ua-verb-????.md"))

    if not verb_files:
        print("No 4-digit ua-verb files found.")
        return

    print(f"Updating note_id fields in {len(verb_files)} files:\n")

    for file_path in verb_files:
        content = file_path.read_text(encoding="utf-8")

        # Extract the ID from filename
        file_id = file_path.stem.split("-")[-1]  # "0062"

        # Replace 5-digit note_id with 4-digit in content
        # e.g., note_id: "ua-verb-00062" → note_id: "ua-verb-0062"
        old_pattern = rf'note_id: "ua-verb-{file_id}"'
        new_pattern = f'note_id: "ua-verb-{file_id}"'

        # Actually, let's be more general and find any 5-digit ua-verb note_id
        updated_content = re.sub(
            r'note_id: "ua-verb-\d{5}"',
            f'note_id: "ua-verb-{file_id}"',
            content
        )

        if updated_content != content:
            file_path.write_text(updated_content, encoding="utf-8")
            print(f"  ✓ {file_path.name}")
        else:
            print(f"  - {file_path.name} (no changes needed)")

    print(f"\n✓ Updated note_id fields in {len(verb_files)} files.")

if __name__ == "__main__":
    update_noteids()
