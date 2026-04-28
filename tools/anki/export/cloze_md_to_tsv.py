#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

import yaml


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    """
    Split a markdown file into YAML front matter and remaining body.
    Expects:
    ---
    <yaml>
    ---
    """
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter")

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.DOTALL)
    if not m:
        raise ValueError(f"{path}: malformed YAML front matter")

    return m.group(1), m.group(2)


def extract_text_section(body: str, path: Path) -> str:
    """
    Extract the contents of a '# text' section from the markdown body.
    Everything after '# text' until the next top-level heading is included.
    """
    lines = body.splitlines()
    in_text = False
    out: list[str] = []

    for line in lines:
        stripped = line.strip()

        if not in_text:
            if stripped.lower() == "# text":
                in_text = True
            continue

        # Stop at next top-level heading
        if stripped.startswith("# "):
            break

        out.append(line)

    return "\n".join(out).strip()

def load_note(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    yaml_text, body = split_frontmatter(text, path)
    meta = yaml.safe_load(yaml_text) or {}

    if not isinstance(meta, dict):
        raise ValueError(f"{path}: YAML must be a mapping")

    meta["_body"] = body
    return meta

def normalize_tags(tags: Any) -> str:
    if tags is None:
        return ""
    if isinstance(tags, list):
        return " ".join(str(t).strip() for t in tags if str(t).strip())
    if isinstance(tags, str):
        return tags.strip()
    return str(tags).strip()


def collect_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for path in sorted(root.rglob("*.md")):
        meta = load_note(path)

        anki = meta.get("anki") or {}
        if not isinstance(anki, dict):
            raise ValueError(f"{path}: anki must be a mapping")

        model = str(anki.get("model", "") or "").strip()
        deck = str(anki.get("deck", "") or "").strip()

        # Skip non-cloze notes entirely
        if not model:
            continue
        if "Cloze" not in model:
            continue

        if not deck:
            raise ValueError(f"{path}: anki.deck is required")

        fields = meta.get("fields") or {}
        if not isinstance(fields, dict):
            raise ValueError(f"{path}: fields must be a mapping")

        body = str(meta.get("_body", "") or "")
        text = str(fields.get("Text", "") or "").strip()

        # Fallback to # text section in markdown body
        if not text:
            text = extract_text_section(body, path)

        source_doc = str(fields.get("Source Document", "") or "").strip()
        source_loc = str(fields.get("Source Location", "") or "").strip()
        tags = normalize_tags(meta.get("tags"))
        note_id = str(meta.get("note_id", "") or "").strip()

        if not note_id:
            raise ValueError(f"{path}: note_id is required")
        if not text:
            raise ValueError(f"{path}: missing Text field and no '# text' section found")

        rows.append(
            {
                "Model": model,
                "Deck": deck,
                "NoteID": note_id,
                "Text": text,
                "Source Document": source_doc,
                "Source Location": source_loc,
                "Tags": tags,
            }
        )

    return rows

def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Model",
        "Deck",
        "NoteID",
        "Text",
        "Source Document",
        "Source Location",
        "Tags",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert cloze-style CNSF markdown notes into an Anki TSV."
    )
    ap.add_argument(
        "--in",
        dest="input_dir",
        required=True,
        help="Root directory containing markdown cloze files",
    )
    ap.add_argument(
        "--out",
        required=True,
        help="Output TSV path",
    )
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    out_path = Path(args.out)

    if not input_dir.exists():
        raise SystemExit(f"Input directory not found: {input_dir}")

    rows = collect_rows(input_dir)
    write_tsv(rows, out_path)

    print(f"Rows: {len(rows)}")
    print(f"Output: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())