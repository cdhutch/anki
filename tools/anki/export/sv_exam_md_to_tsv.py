#!/usr/bin/env python3
"""Convert SV exam-draft CNSF markdown notes into Anki TSV files.

Produces two TSV files per invocation:
  --out-mcq  MCQ notes  → NoteID, Text, Choice1-4, CorrectChoice, SourceDocument, OriginalNoteID, Tags
  --out-tf   T/F notes  → NoteID, Text, CorrectAnswer, SourceDocument, OriginalNoteID, Tags

Choice shuffling (when Shuffle Choices: true) is deterministic, seeded by note_id.
Both TSV files are always written; an empty input produces a header-only TSV.

Only processes notes with note_type: systems_verification_exam_draft.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
from pathlib import Path
from typing import Any

import yaml

NOTE_TYPE = "systems_verification_exam_draft"

MCQ_FIELDNAMES = [
    "NoteID", "Text", "Choice1", "Choice2", "Choice3", "Choice4",
    "CorrectChoice", "Source Document", "OriginalNoteID", "Tags",
]
TF_FIELDNAMES = [
    "NoteID", "Text", "CorrectAnswer", "Source Document", "OriginalNoteID", "Tags",
]

_LETTER_IDX: dict[str, int] = {"A": 0, "B": 1, "C": 2, "D": 3}


# ---------------------------------------------------------------------------
# CNSF parsing utilities (mirrors sv_md_to_tsv.py)
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.DOTALL)
    if not m:
        raise ValueError(f"{path}: malformed YAML front matter")
    return m.group(1), m.group(2)


def _load_note(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    yaml_text, _ = _split_frontmatter(text, path)
    meta = yaml.safe_load(yaml_text) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: YAML must be a mapping")
    return meta


def _normalize_tags(tags: Any) -> str:
    if tags is None:
        return ""
    if isinstance(tags, list):
        return " ".join(str(t).strip() for t in tags if str(t).strip())
    if isinstance(tags, str):
        return tags.strip()
    return str(tags).strip()


# ---------------------------------------------------------------------------
# Shuffle logic
# ---------------------------------------------------------------------------

def _deterministic_shuffle(
    note_id: str, choices: list[str], correct_letter: str
) -> tuple[list[str], int]:
    """Return (shuffled_choices, correct_1based_position).

    Seed is derived from note_id via MD5 for reproducibility across runs.
    """
    seed = int(hashlib.md5(note_id.encode()).hexdigest(), 16) % (2 ** 32)
    rng = random.Random(seed)
    indexed = list(enumerate(choices))
    rng.shuffle(indexed)
    shuffled = [text for _, text in indexed]
    orig_idx = _LETTER_IDX[correct_letter.upper()]
    new_pos = next(i for i, (oi, _) in enumerate(indexed) if oi == orig_idx)
    return shuffled, new_pos + 1  # 1-based


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------

def _s(fields: dict[str, Any], key: str) -> str:
    return str(fields.get(key) or "").strip()


def _build_mcq_row(path: Path, meta: dict[str, Any]) -> dict[str, str]:
    fields = meta.get("fields") or {}
    note_id = str(meta.get("note_id") or "").strip()
    if not note_id:
        raise ValueError(f"{path}: note_id is required")

    stem = _s(fields, "Question Stem")
    if not stem:
        raise ValueError(f"{path}: Question Stem is required")

    choices = [
        _s(fields, "Choice A"),
        _s(fields, "Choice B"),
        _s(fields, "Choice C"),
        _s(fields, "Choice D"),
    ]
    correct_letter = _s(fields, "Correct Choice")
    if correct_letter not in _LETTER_IDX:
        raise ValueError(
            f"{path}: Correct Choice must be A, B, C, or D; got {correct_letter!r}"
        )

    if fields.get("Shuffle Choices", False):
        ordered, correct_pos = _deterministic_shuffle(note_id, choices, correct_letter)
    else:
        ordered = choices
        correct_pos = _LETTER_IDX[correct_letter.upper()] + 1  # 1-based

    correct_text = ordered[correct_pos - 1]

    return {
        "NoteID": note_id,
        "Text": stem,
        "Choice1": ordered[0],
        "Choice2": ordered[1],
        "Choice3": ordered[2],
        "Choice4": ordered[3],
        "CorrectChoice": f"{correct_pos} — {correct_text}",
        "Source Document": _s(fields, "Source Document"),
        "OriginalNoteID": _s(fields, "Original Note ID"),
        "Tags": _normalize_tags(meta.get("tags")),
    }


def _build_tf_row(path: Path, meta: dict[str, Any]) -> dict[str, str]:
    fields = meta.get("fields") or {}
    note_id = str(meta.get("note_id") or "").strip()
    if not note_id:
        raise ValueError(f"{path}: note_id is required")

    stem = _s(fields, "Question Stem")
    if not stem:
        raise ValueError(f"{path}: Question Stem is required")

    correct = _s(fields, "Correct Choice")
    if correct not in ("True", "False"):
        raise ValueError(
            f"{path}: Correct Choice for T/F must be 'True' or 'False'; got {correct!r}"
        )

    return {
        "NoteID": note_id,
        "Text": stem,
        "CorrectAnswer": correct,
        "Source Document": _s(fields, "Source Document"),
        "OriginalNoteID": _s(fields, "Original Note ID"),
        "Tags": _normalize_tags(meta.get("tags")),
    }


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect_rows(root: Path) -> tuple[list[dict], list[dict]]:
    mcq_rows: list[dict] = []
    tf_rows: list[dict] = []

    for path in sorted(root.rglob("*.md")):
        meta = _load_note(path)
        if meta.get("note_type") != NOTE_TYPE:
            continue

        fields = meta.get("fields") or {}
        exam_format = str(fields.get("Exam Format") or "").strip().lower()

        if exam_format == "mcq":
            mcq_rows.append(_build_mcq_row(path, meta))
        elif exam_format == "tf":
            tf_rows.append(_build_tf_row(path, meta))
        else:
            raise ValueError(
                f"{path}: Exam Format must be 'mcq' or 'tf'; got {exam_format!r}"
            )

    return mcq_rows, tf_rows


# ---------------------------------------------------------------------------
# TSV output
# ---------------------------------------------------------------------------

def _write_tsv(rows: list[dict], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert SV exam-draft CNSF notes to Anki TSV files (MCQ and T/F)."
    )
    ap.add_argument(
        "--in", dest="input_dir", required=True,
        help="Directory containing exam-draft markdown notes",
    )
    ap.add_argument("--out-mcq", required=True, help="Output TSV for MCQ notes")
    ap.add_argument("--out-tf", required=True, help="Output TSV for T/F notes")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"Input directory not found: {input_dir}")

    mcq_rows, tf_rows = collect_rows(input_dir)

    _write_tsv(mcq_rows, MCQ_FIELDNAMES, Path(args.out_mcq))
    _write_tsv(tf_rows, TF_FIELDNAMES, Path(args.out_tf))

    print(f"MCQ rows : {len(mcq_rows):>4}  →  {args.out_mcq}")
    print(f"T/F rows : {len(tf_rows):>4}  →  {args.out_tf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
