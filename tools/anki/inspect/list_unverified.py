#!/usr/bin/env python3
"""tools/anki/inspect/list_unverified.py — Report every UA note not yet fully verified.

Scans all UA note-type corpora (lexemes, verbs, grammar, visual, pvom) for notes
carrying any of these "not verified" signals:
  - stress:unverified tag — stress marks not yet confirmed against Горох
  - status:draft tag       — content not yet reviewed by Craig
  - no status tag at all   — neither status:draft nor status:verified present; flagged
    separately so it's never silently conflated with a deliberate status:draft

A note can have more than one reason at once (e.g. status:verified content whose
stress is still stress:unverified — see ua_verb_import.py's should_suspend()).

Usage:
    python -m tools.anki.inspect.list_unverified
    python -m tools.anki.inspect.list_unverified --type ua_verb
    make ua-unverified
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

NOTE_ROOTS: dict[str, tuple[Path, str]] = {
    "ua_lexeme": (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes", "ua-lexeme-*.md"),
    "ua_verb": (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "verbs", "ua-verb-*.md"),
    "ua_grammar": (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "grammar", "ua-grammar-*.md"),
    "ua_visual": (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "visual", "ua-visual-*.md"),
    "ua_pvom": (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "pvom", "ua-pvom-*.md"),
}


def _read_meta(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        doc = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def _reasons(tags: list[str]) -> list[str]:
    reasons = []
    if "stress:unverified" in tags:
        reasons.append("stress:unverified")
    if "status:draft" in tags:
        reasons.append("status:draft")
    elif "status:verified" not in tags:
        reasons.append("no status tag")
    return reasons


def find_unverified(note_type: str, root: Path, pattern: str) -> list[dict[str, Any]]:
    results = []
    if not root.exists():
        return results
    for path in sorted(root.rglob(pattern)):
        meta = _read_meta(path)
        if meta is None:
            continue
        tags = meta.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        reasons = _reasons(tags)
        if not reasons:
            continue

        fields = meta.get("fields") or {}
        label = fields.get("Lemma") or fields.get("Prefix") or ""

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
        print("Nothing unverified — every scanned note has confirmed stress and status:verified.")
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
            print(f"  {r['note_id']:<20} {label:<25} [{reasons}]  {_relpath(r['path'])}")

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
