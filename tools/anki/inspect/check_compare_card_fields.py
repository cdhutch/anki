#!/usr/bin/env python3
"""tools/anki/inspect/check_compare_card_fields.py — Audit UA_Lexeme Compare/homograph fields.

The Compare card (`UA_Lexeme`'s 3rd template) renders two genuinely different card
designs off the same field set, routed by `_IsHomograph` (computed by the importer
from the `homograph:true` tag — see CLAUDE-compare-card-field-mapping.md for the full
spec). Getting a note's fields into the wrong shape for its mode produces a card that
*renders* but is wrong — an all-English front with nothing to recognize (ua-lexeme-0181),
or the raw `ConfusableSet` paragraph rendered as a fake answer chip (ua-lexeme-0305),
both found 2026-07-28. This script codifies those two bugs plus related defect classes
into a repeatable corpus-wide check, so new instances surface at `make ua-fix` time
instead of after a live sync.

Checks performed (see `audit_notes()`):
  DUP   Same NoteID authored in more than one file — a genuine identity collision.
        AnkiConnect matches on NoteID, so whichever file syncs last silently overwrites
        the other's fields on the *same* live Anki note. Found once already (ua-lexeme-0143,
        2026-07-28) via manual inspection — the naive dict-keyed version of this audit
        masked it by construction, so this check is deliberately the first one run.
  YAML  File doesn't parse as a CNSF note at all (malformed `---` markers or invalid YAML).
  A     Non-homograph note: ConfusableSet populated, but CompareA/CompareB not BOTH
        authored. Triggers ua_lexeme_import.py's compute_compare_options() legacy
        auto-derive fallback, which stuffs the raw ConfusableSet prose into CompareA
        and leaves the card unsuspended — a live prose-leak risk (ua-lexeme-0305).
  B     homograph:true note: ConfusableSet + CompareA populated, but Homograph_SenseA/B
        missing — a note that's been given Shape 1's front but not its back.
  C     homograph:true note: CompareA holds no Cyrillic — the pre-dual-mode legacy
        format where Compare fields held English sense descriptions instead of
        Ukrainian example sentences (ua-lexeme-0181 before its 2026-07-28 fix).
  D     Non-homograph note: CompareA/B/C/D looks like a full sentence instead of a bare
        word/lemma — wrong content type for confusables mode.
  E     ConfusableSet text mentions "homograph" but the homograph:true tag is missing —
        usually a false positive (a bucket-4 convergent-synonym note explicitly saying
        "not a homograph"), but worth a human glance each time it fires.
  F     homograph:true tag present but ConfusableSet is blank — never authored at all.
  G     Homograph sibling pairs (cross-referenced by NoteID in ConfusableSet) whose
        CompareA/CompareB content doesn't match between the two notes, in either order.

Usage:
    python -m tools.anki.inspect.check_compare_card_fields
    python -m tools.anki.inspect.check_compare_card_fields --strict   # exit 1 if any findings
    make ua-compare-check
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"

CYRILLIC = re.compile(r"[Ѐ-ӿ]")
SIBLING_REF = re.compile(r"ua-lexeme-(\d{4})")


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def has_cyrillic(s: str | None) -> bool:
    return bool(CYRILLIC.search(s or ""))


def looks_like_sentence(s: str | None) -> bool:
    if not s:
        return False
    s = s.strip()
    return len(s.split()) >= 3 and s[-1] in ".!?"


def _load_note(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    body = text.strip()
    if not (body.startswith("---") and body.endswith("---")):
        return None, "malformed --- markers"
    inner = body[3:-3]
    try:
        data = yaml.safe_load(inner)
    except yaml.YAMLError as e:
        return None, f"YAML error: {e}"
    if not isinstance(data, dict) or "fields" not in data:
        return None, "no fields dict"
    return data, None


def collect_notes(root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    """Returns (notes-by-id, parse-errors, duplicate-id records).

    `notes` holds one entry per NoteID (last file wins, matching AnkiConnect's own
    last-sync-wins behavior) — but every duplicate is also captured separately in
    the returned duplicates list, so a NoteID collision is never silently swallowed
    the way a plain dict-build would swallow it.
    """
    notes: dict[str, dict[str, Any]] = {}
    seen_paths: dict[str, list[Path]] = {}
    errors: list[dict[str, str]] = []

    for path in sorted(root.rglob("ua-lexeme-*.md")):
        data, err = _load_note(path)
        if err:
            errors.append({"path": _relpath(path), "error": err})
            continue

        fields = data["fields"]
        tags = data.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        note_id = fields.get("NoteID", "") or path.stem

        seen_paths.setdefault(note_id, []).append(path)
        notes[note_id] = {
            "path": path,
            "tags": tags,
            "is_homograph": "homograph:true" in tags,
            "lemma": fields.get("Lemma", ""),
            "confusable_set": (fields.get("ConfusableSet") or "").strip(),
            "compare_scenario": (fields.get("CompareScenario") or "").strip(),
            "compare_a": (fields.get("CompareA") or "").strip(),
            "compare_b": (fields.get("CompareB") or "").strip(),
            "compare_c": (fields.get("CompareC") or "").strip(),
            "compare_d": (fields.get("CompareD") or "").strip(),
            "sense_a": (fields.get("Homograph_SenseA") or "").strip(),
            "sense_b": (fields.get("Homograph_SenseB") or "").strip(),
        }

    duplicates: list[dict[str, str]] = []
    for note_id, paths in seen_paths.items():
        if len(paths) > 1:
            duplicates.append({"note_id": note_id, "paths": [_relpath(p) for p in paths]})

    return notes, errors, duplicates


def audit_notes(notes: dict[str, dict[str, Any]]) -> dict[str, list[Any]]:
    findings: dict[str, list[Any]] = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": [], "G": []}

    for note_id, n in notes.items():
        if not n["is_homograph"]:
            if n["confusable_set"] and not (n["compare_a"] and n["compare_b"]):
                findings["A"].append(note_id)
            if "homograph" in n["confusable_set"].lower():
                findings["E"].append(note_id)
            for label, val in (
                ("A", n["compare_a"]),
                ("B", n["compare_b"]),
                ("C", n["compare_c"]),
                ("D", n["compare_d"]),
            ):
                if val and looks_like_sentence(val):
                    findings["D"].append((note_id, label))
        else:
            if not n["confusable_set"]:
                findings["F"].append(note_id)
            if n["confusable_set"] and n["compare_a"] and not (n["sense_a"] and n["sense_b"]):
                findings["B"].append(note_id)
            if n["compare_a"] and not has_cyrillic(n["compare_a"]):
                findings["C"].append(note_id)

    checked_pairs: set[tuple[str, str]] = set()
    for note_id, n in notes.items():
        if not n["is_homograph"]:
            continue
        for ref in SIBLING_REF.findall(n["confusable_set"]):
            sib_id = f"ua-lexeme-{ref}"
            if sib_id not in notes or sib_id == note_id:
                continue
            pair_key = tuple(sorted([note_id, sib_id]))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)
            sib = notes[sib_id]
            if not sib["is_homograph"]:
                continue
            pair_ok = (n["compare_a"], n["compare_b"]) in (
                (sib["compare_a"], sib["compare_b"]),
                (sib["compare_b"], sib["compare_a"]),
            )
            if not pair_ok:
                findings["G"].append(pair_key)

    return findings


FINDING_LABELS = {
    "A": "non-homograph note, ConfusableSet populated, CompareA/B not both authored (prose-leak risk)",
    "B": "homograph:true note missing Homograph_SenseA/B (Shape 1 back not authored)",
    "C": "homograph:true note, CompareA not Cyrillic (legacy English-chip format)",
    "D": "non-homograph note, CompareA-D looks like a sentence instead of a bare word",
    "E": "ConfusableSet mentions 'homograph' but tag is missing (verify — may be a bucket-4 false positive)",
    "F": "homograph:true tag present but ConfusableSet is blank (never authored)",
    "G": "homograph sibling pair with mismatched CompareA/B content",
}


def print_report(
    notes: dict[str, dict[str, Any]],
    errors: list[dict[str, str]],
    duplicates: list[dict[str, str]],
    findings: dict[str, list[Any]],
) -> bool:
    """Returns True if anything worth Craig's attention was found."""
    any_findings = False

    print(f"Scanned {len(notes) + sum(len(d['paths']) - 1 for d in duplicates)} file(s), "
          f"{len(notes)} unique NoteID(s).")

    if errors:
        any_findings = True
        print(f"\n=== YAML parse errors ({len(errors)}) ===")
        for e in errors:
            print(f"  {e['path']}: {e['error']}")

    if duplicates:
        any_findings = True
        print(f"\n=== DUP: duplicate NoteID across files ({len(duplicates)}) ===")
        print("  Same identity in >1 file — AnkiConnect sync order decides which wins.")
        for d in duplicates:
            print(f"  {d['note_id']}:")
            for p in d["paths"]:
                print(f"      {p}")

    for cls, label in FINDING_LABELS.items():
        rows = findings.get(cls, [])
        if not rows:
            continue
        any_findings = True
        print(f"\n=== {cls}: {label} ({len(rows)}) ===")
        for row in rows:
            if isinstance(row, tuple) and len(row) == 2 and cls == "D":
                note_id, chip = row
                n = notes[note_id]
                print(f"  {note_id} ({n['lemma']}) Compare{chip}: {_relpath(n['path'])}")
            elif isinstance(row, tuple):
                a, b = row
                print(f"  {a} <-> {b}")
                print(f"      {a}: A={notes[a]['compare_a']!r} B={notes[a]['compare_b']!r}")
                print(f"      {b}: A={notes[b]['compare_a']!r} B={notes[b]['compare_b']!r}")
            else:
                n = notes[row]
                print(f"  {row} ({n['lemma']}): {_relpath(n['path'])}")

    print("\n=== SUMMARY ===")
    print(f"YAML parse errors: {len(errors)}")
    print(f"Duplicate NoteIDs: {len(duplicates)}")
    for cls, label in FINDING_LABELS.items():
        print(f"Class {cls}: {len(findings.get(cls, []))}  ({label})")

    if not any_findings:
        print("\nNothing to report — every scanned note's Compare/homograph fields match "
              "the documented shape (see CLAUDE-compare-card-field-mapping.md).")

    return any_findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=LEXEME_ROOT, help="Lexeme notes root (default: repo's ua-lexeme tree)")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any findings are reported (default: always exit 0, matching ua-unverified)")
    args = ap.parse_args()

    if not args.root.exists():
        print(f"Lexeme root not found: {args.root}", file=sys.stderr)
        return 2

    notes, errors, duplicates = collect_notes(args.root)
    findings = audit_notes(notes)
    any_findings = print_report(notes, errors, duplicates, findings)

    if args.strict and any_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
