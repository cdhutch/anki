#!/usr/bin/env python3
"""tools/anki/inspect/list_unverified_b737.py — Report every B737 note not yet fully verified.

Scans all B737 note-root corpora (QRC, Triggers/Flows, Cats and Dogs, Mnemonics,
Checklists, Procedures [normal/non-normal/inflight], Limits, Systems Verification)
for notes carrying any of these "not verified" signals:
  - status:unverified tag — content not yet reviewed
  - status:draft tag       — content still in draft (e.g. SV exam-bank conversions)
  - no status tag at all   — neither status:draft/unverified nor status:verified
    present; flagged separately so it's never silently conflated with a
    deliberate status:draft

B737 has no stress-verification axis (that's a UA-only concept for Ukrainian
pronunciation marks) — status is the only signal here.

Usage:
    python -m tools.anki.inspect.list_unverified_b737
    python -m tools.anki.inspect.list_unverified_b737 --type limits
    make b737-unverified
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
B737_ROOT = REPO_ROOT / "domains" / "b737" / "anki" / "notes"

NOTE_ROOTS: dict[str, tuple[Path, str]] = {
    "qrc_recall": (B737_ROOT / "qrc_recall", "*.md"),
    "triggers_and_flows": (B737_ROOT / "triggers_and_flows", "*.md"),
    "cats_and_dogs": (B737_ROOT / "cats_and_dogs", "*.md"),
    "mnemonics": (B737_ROOT / "mnemonics", "*.md"),
    "checklists": (B737_ROOT / "checklists", "*.md"),
    "procedures_normal": (B737_ROOT / "procedures" / "normal", "*.md"),
    "procedures_non_normal": (B737_ROOT / "procedures" / "non_normal", "*.md"),
    "procedures_inflight": (B737_ROOT / "procedures" / "inflight_maneuvers", "*.md"),
    "limits": (B737_ROOT / "limits", "*.md"),
    "systems_verification": (B737_ROOT / "systems_verification", "*.md"),
}


def _read_doc(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, ""
    try:
        doc = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None, ""
    return (doc if isinstance(doc, dict) else None), parts[2]


def _front_md_preview(body: str, limit: int = 70) -> str:
    """Pull a short preview from the '# front_md' section of the note body."""
    marker = "# front_md"
    idx = body.find(marker)
    if idx == -1:
        return ""
    rest = body[idx + len(marker) :]
    next_heading = rest.find("\n# ")
    if next_heading != -1:
        rest = rest[:next_heading]
    text = " ".join(rest.split())
    text = text.replace("**", "").replace("*", "").replace("`", "")
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def _reasons(tags: list[str]) -> list[str]:
    reasons = []
    if "status:unverified" in tags:
        reasons.append("status:unverified")
    elif "status:draft" in tags:
        reasons.append("status:draft")
    elif "status:verified" not in tags:
        reasons.append("no status tag")
    return reasons


def find_unverified(note_type: str, root: Path, pattern: str) -> list[dict[str, Any]]:
    results = []
    if not root.exists():
        return results
    for path in sorted(root.rglob(pattern)):
        if path.name.startswith("_"):
            continue
        meta, body = _read_doc(path)
        if meta is None:
            continue
        tags = meta.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        reasons = _reasons(tags)
        if not reasons:
            continue

        fields = meta.get("fields") or {}
        label = (
            _front_md_preview(body)
            or fields.get("Question Stem")
            or fields.get("Source Location")
            or ""
        )

        results.append(
            {
                "note_type": note_type,
                "note_id": meta.get("note_id", path.stem),
                "label": label,
                "reasons": reasons,
                "path": path,
            }
        )
    return results


def collect(types: list[str]) -> list[dict[str, Any]]:
    all_results: list[dict[str, Any]] = []
    for note_type in types:
        root, pattern = NOTE_ROOTS[note_type]
        all_results.extend(find_unverified(note_type, root, pattern))
    return all_results


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def print_report(results: list[dict[str, Any]]) -> None:
    if not results:
        print("Nothing unverified — every scanned B737 note is status:verified.")
        return

    by_type: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        by_type.setdefault(r["note_type"], []).append(r)

    for note_type in sorted(by_type):
        rows = by_type[note_type]
        print(f"\n{note_type}  ({len(rows)} unverified)")
        print("-" * 70)
        for r in rows:
            reasons = ", ".join(r["reasons"])
            label = r["label"] or r["note_id"]
            print(f"  {r['note_id']:<28} {label:<30} [{reasons}]  {_relpath(r['path'])}")

    print(f"\nTotal: {len(results)} unverified note(s) across {len(by_type)} note type(s).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--type",
        action="append",
        dest="types",
        choices=sorted(NOTE_ROOTS),
        help="Restrict to one or more note types (default: all)",
    )
    args = ap.parse_args()

    types = args.types or sorted(NOTE_ROOTS)
    results = collect(types)
    print_report(results)


if __name__ == "__main__":
    main()
