#!/usr/bin/env python3
"""
strip_operator_refs.py — Remove operator-specific branding from an exported .apkg.

Usage:
    python tools/anki/export/strip_operator_refs.py \
        --in  releases/B737-v1.1.0.apkg \
        --out releases/B737-v1.1.0-public.apkg

What it does:
    - Unpacks the .apkg (which is a zip)
    - Opens the Anki SQLite database (collection.anki2 / collection.anki21)
    - Replaces operator strings in note fields (flds column)
    - Repacks the .apkg

Replacements applied:
    "American Airlines B737 Aircraft Operating Manual"
        → "B737 Aircraft Operating Manual"
    "American Airlines B737 Takeoff Card"
        → "B737 Takeoff Card"
    "American Airlines "
        → "" (catch-all for any remaining references)
"""

import argparse
import os
import shutil
import sqlite3
import tempfile
import zipfile


REPLACEMENTS = [
    ("American Airlines B737 Aircraft Operating Manual", "B737 Aircraft Operating Manual"),
    ("American Airlines B737 Takeoff Card", "B737 Takeoff Card"),
    ("American Airlines ", ""),  # catch-all
]

DB_NAMES = ["collection.anki21", "collection.anki2"]


def apply_replacements(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def process_db(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, flds FROM notes")
    rows = cur.fetchall()

    updated = 0
    for note_id, flds in rows:
        new_flds = apply_replacements(flds)
        if new_flds != flds:
            cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, note_id))
            updated += 1

    conn.commit()
    conn.close()
    return updated


def main():
    parser = argparse.ArgumentParser(description="Strip operator references from an Anki .apkg file.")
    parser.add_argument("--in", dest="infile", required=True, help="Input .apkg path")
    parser.add_argument("--out", dest="outfile", required=True, help="Output .apkg path")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Unpack
        with zipfile.ZipFile(args.infile, "r") as zf:
            zf.extractall(tmpdir)

        # Process whichever DB is present
        total_updated = 0
        for db_name in DB_NAMES:
            db_path = os.path.join(tmpdir, db_name)
            if os.path.exists(db_path):
                n = process_db(db_path)
                print(f"  {db_name}: {n} note(s) updated")
                total_updated += n

        if total_updated == 0:
            print("No operator references found — output will be identical to input.")

        # Repack
        out_path = args.outfile
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tmpdir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmpdir)
                    zf.write(fpath, arcname)

        print(f"\nWrote: {out_path}")
        print(f"Total notes modified: {total_updated}")


if __name__ == "__main__":
    main()
