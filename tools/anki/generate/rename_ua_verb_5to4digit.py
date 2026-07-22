#!/usr/bin/env python3
"""Rename ua-verb files from 5-digit to 4-digit format (ua-verb-00062 → ua-verb-0062)."""

import sys
from pathlib import Path

def rename_files():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    # Find all 5-digit ua-verb files
    five_digit_files = sorted(verbs_dir.glob("ua-verb-?????.md"))

    if not five_digit_files:
        print("No 5-digit ua-verb files found to rename.")
        return

    print(f"Found {len(five_digit_files)} files to rename:\n")

    for old_file in five_digit_files:
        # Extract the numeric part and convert to 4-digit
        stem = old_file.stem  # "ua-verb-00062"
        parts = stem.split("-")
        five_digit_id = int(parts[-1])  # "00062" → 62
        four_digit_id = f"{five_digit_id:04d}"  # 62 → "0062"

        new_stem = f"ua-verb-{four_digit_id}"
        new_file = old_file.parent / f"{new_stem}.md"

        print(f"  {old_file.name} → {new_file.name}")
        old_file.rename(new_file)

    print(f"\n✓ Renamed {len(five_digit_files)} files to 4-digit format.")

if __name__ == "__main__":
    rename_files()
