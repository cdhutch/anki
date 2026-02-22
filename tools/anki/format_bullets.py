#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

TARGET_TAGS = {"format_bullets", "special-formatting"}

def should_format(tag_str):
    tags = set(tag_str.split())
    return bool(tags & TARGET_TAGS)

def to_bullets(text):
    parts = [p.strip() for p in text.split(";") if p.strip()]
    return "\n".join(f"• {p}" for p in parts)

def main():
    if len(sys.argv) != 2:
        print("Usage: format_bullets.py <input.tsv>")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    output_path = input_path.with_name(input_path.stem + "__formatted.tsv")
    review_path = input_path.with_name(input_path.stem + "__review.md")

    rows = []
    changes = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            original = row["answer"]

            if should_format(row["tags"]) and ";" in original:
                formatted = to_bullets(original)
                row["answer"] = formatted

                changes.append((row["note_id"], original, formatted))

            rows.append(row)

    # Write formatted TSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    # Write review markdown
    with open(review_path, "w", encoding="utf-8") as f:
        f.write("# Formatting Review\n\n")

        for note_id, before, after in changes:
            f.write(f"## {note_id}\n\n")
            f.write("### BEFORE\n")
            f.write(before + "\n\n")
            f.write("### AFTER\n")
            f.write(after + "\n\n---\n\n")

    print("✔ Done")
    print("Formatted TSV:", output_path)
    print("Review file:", review_path)

if __name__ == "__main__":
    main()