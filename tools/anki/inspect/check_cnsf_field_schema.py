#!/usr/bin/env python3
"""tools/anki/inspect/check_cnsf_field_schema.py — CNSF field-key consistency
checker, per UA note type.

Written 2026-08-10 per CLAUDE.md "UA Domain -- YAML/CNSF schema consistency"
queue item. Verifies, for each of the 5 UA note types, that every CNSF `.md`
note's `fields:` mapping carries the same set of keys as this repo's own
FIELDS-style constant for that note type (imported directly from
setup_ua_note_types.py / setup_ua_pvom_note_type.py -- never a hardcoded
copy, so this script can't itself drift from them). Two kinds of drift:

  - MISSING: a canonical field key absent from some note's `fields:` dict
    (as opposed to present-but-blank, i.e. `Key: ''`). Whether this should
    ever be allowed (sparse optional fields) or always be a bug (every note
    always carries every key, blank when unused) is an open policy decision
    -- see CLAUDE-work-queue.md "Decide the convention for newer optional
    fields." This script only reports the gap; --strict makes it fail the
    exit code on missing keys, off by default until that policy is settled.
  - UNKNOWN: a key present on a note that isn't in the canonical set at all
    -- typo, abandoned experiment, or (just as likely) the canonical set
    itself is stale. This ALWAYS fails the exit code, since an unrecognized
    key is worth a look either way. Cross-check with
    inspect_note_type_fields.py (which compares the same constants against
    the LIVE Anki model, not just the CNSF files) before assuming an
    UNKNOWN key is a bug in the note rather than in the constant.

Read-only. Never edits a CNSF file or talks to AnkiConnect -- pure
filesystem + YAML frontmatter parsing, safe to run with Anki closed.

Usage:
    python tools/anki/inspect/check_cnsf_field_schema.py                    # all 5 note types
    python tools/anki/inspect/check_cnsf_field_schema.py --note-type UA_Lexeme
    python tools/anki/inspect/check_cnsf_field_schema.py --verbose          # list example note_ids for UNKNOWN keys
    python tools/anki/inspect/check_cnsf_field_schema.py --strict           # also fail on MISSING keys
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.cnsf_canonicalize import split_frontmatter  # noqa: E402
from tools.anki.setup.setup_ua_note_types import (  # noqa: E402
    FIELDS as LEXEME_FIELDS,
    GRAMMAR_FIELDS,
    VISUAL_FIELDS,
    VERB_FIELDS,
)
from tools.anki.setup.setup_ua_pvom_note_type import FIELDS as PVOM_FIELDS  # noqa: E402

# glob patterns mirror each note type's own import script's collect_files()
# exactly (see ua_*_import.py) -- e.g. UA_Verb's notes/ dir also contains a
# legacy notes/verbs/exported/ dump that the real sync never touches; a
# generic "*.md"/"**/*.md" glob here would silently vacuum that in too.
NOTE_TYPE_CONFIGS = [
    {
        "label": "UA_Lexeme",
        "root": REPO_ROOT / "domains/ua/anki/notes/lexemes",
        "glob": "**/ua-lexeme-*.md",
        "canonical_fields": LEXEME_FIELDS,
        "source": "setup_ua_note_types.py:FIELDS",
    },
    {
        "label": "UA_Grammar",
        "root": REPO_ROOT / "domains/ua/anki/notes/grammar",
        "glob": "ua-grammar-*.md",
        "canonical_fields": GRAMMAR_FIELDS,
        "source": "setup_ua_note_types.py:GRAMMAR_FIELDS",
    },
    {
        "label": "UA_Visual",
        "root": REPO_ROOT / "domains/ua/anki/notes/visual",
        "glob": "ua-visual-*.md",
        "canonical_fields": VISUAL_FIELDS,
        "source": "setup_ua_note_types.py:VISUAL_FIELDS",
    },
    {
        "label": "UA_Verb",
        "root": REPO_ROOT / "domains/ua/anki/notes/verbs",
        "glob": "ua-verb-*.md",
        "canonical_fields": VERB_FIELDS,
        "source": "setup_ua_note_types.py:VERB_FIELDS",
    },
    {
        "label": "UA_PVOM_Infinitive",
        "root": REPO_ROOT / "domains/ua/anki/notes/pvom",
        "glob": "ua-pvom-*.md",
        "canonical_fields": PVOM_FIELDS,
        "source": "setup_ua_pvom_note_type.py:FIELDS",
    },
]


def load_note_fields(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    try:
        fm = split_frontmatter(text, path)
        meta = yaml.safe_load(fm.yaml_text) or {}
    except Exception as e:
        print(f"  WARN: {path}: failed to parse frontmatter ({e})", file=sys.stderr)
        return None
    fields = meta.get("fields")
    if not isinstance(fields, dict):
        print(f"  WARN: {path}: no 'fields' mapping", file=sys.stderr)
        return None
    return fields


def check_note_type(config: dict, verbose: bool) -> dict:
    root: Path = config["root"]
    canonical = config["canonical_fields"]
    canonical_set = set(canonical)

    files = sorted(root.glob(config["glob"]))
    total = len(files)

    missing_counts = {f: 0 for f in canonical}  # canonical key -> # notes missing it
    extra_counts: dict[str, list[str]] = {}  # unknown key -> [note_ids that have it]

    for path in files:
        fields = load_note_fields(path)
        if fields is None:
            continue
        note_id = path.stem
        present = set(fields.keys())
        for key in canonical:
            if key not in present:
                missing_counts[key] += 1
        for key in present:
            if key not in canonical_set:
                extra_counts.setdefault(key, []).append(note_id)

    print(f"=== {config['label']}  ({total} notes, canonical set: {config['source']}, "
          f"{len(canonical)} fields) ===")

    any_missing = {k: v for k, v in missing_counts.items() if v > 0}
    if any_missing:
        print(f"  Fields not present on every note ({len(any_missing)} of {len(canonical)} "
              f"canonical fields):")
        for key, count in sorted(any_missing.items(), key=lambda kv: -kv[1]):
            present_count = total - count
            print(f"    {key:38s} {present_count:4d}/{total}")
    else:
        print(f"  All {len(canonical)} canonical fields present (blank or populated) on all "
              f"{total} notes.")

    if extra_counts:
        print(f"  UNKNOWN keys not in the canonical set ({len(extra_counts)}) -- typo, "
              f"abandoned experiment, or the canonical set is stale (cross-check with "
              f"inspect_note_type_fields.py before assuming these are bugs):")
        for key, note_ids in sorted(extra_counts.items(), key=lambda kv: -len(kv[1])):
            print(f"    {key:38s} {len(note_ids):4d}/{total}")
            if verbose:
                shown = note_ids[:10]
                more = f" (+{len(note_ids) - 10} more)" if len(note_ids) > 10 else ""
                print(f"        e.g. {', '.join(shown)}{more}")
    else:
        print("  No unknown keys found.")

    print()
    return {"missing": any_missing, "extra": extra_counts, "total": total}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check CNSF note field-key consistency per note type against this "
                    "repo's FIELDS constants. Read-only; reports only, never edits."
    )
    parser.add_argument(
        "--note-type",
        choices=[c["label"] for c in NOTE_TYPE_CONFIGS],
        help="Check only this note type (default: all 5)",
    )
    parser.add_argument("--verbose", action="store_true",
                         help="List example note_ids for UNKNOWN keys")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if ANY canonical field is missing from ANY note, not just on "
             "UNKNOWN keys. Off by default -- the always-vs-sparse convention for newer "
             "optional fields hasn't been decided yet; see CLAUDE-work-queue.md.",
    )
    args = parser.parse_args()

    targets = (
        [c for c in NOTE_TYPE_CONFIGS if c["label"] == args.note_type]
        if args.note_type
        else NOTE_TYPE_CONFIGS
    )

    any_extra = False
    any_missing = False
    for config in targets:
        result = check_note_type(config, args.verbose)
        if result["extra"]:
            any_extra = True
        if result["missing"]:
            any_missing = True

    if any_extra:
        print("FAIL: unknown field key(s) found -- see UNKNOWN keys above.")
        return 1
    if args.strict and any_missing:
        print("FAIL (--strict): some canonical fields are missing from some notes.")
        return 1
    suffix = " (missing-field gaps exist above but --strict not set)" if any_missing else ""
    print(f"OK: no unknown field keys found.{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
