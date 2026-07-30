#!/usr/bin/env python3
"""tools/anki/inspect/check_pending_confusables.py — Watchlist for not-yet-sourced
confusable-set partners.

New 2026-07-30, Craig. Several times during Ch-08 verification, Craig named a confusable-set
partner for a note under review that doesn't have its own ua-lexeme note yet (e.g. "0463 (рух)
will be in a confusable set with затор" when затор hasn't been sourced). Rather than trying to
remember these across sessions, or re-discovering them by accident, the anchor note gets tagged

    pending-confusable:<bare-spelling-of-the-not-yet-sourced-word>

(stress marks optional in the tag — matching is always stress-stripped, same rule as
tools/anki/lib/lexeme_dedup.py). This script scans the whole corpus for those tags and checks
whether a note with that spelling now exists. It does NOT edit anything and does NOT decide
what the ConfusableSet/CompareA-D content should say — same division of labor as
check_lexeme_dedup.py: this only answers "does the spelling exist now," a human (or Claude)
still writes the actual Compare-card content once it does.

For a same-root/different-prefix family without one single known target spelling (e.g.
ua-lexeme-0321 перепрошувати eventually clustering with other -прошувати/-просити forms),
tag the note `needs-confusable-set` instead (the pre-existing generic marker, see
ua-lexeme-0436/0440) — this script only tracks exact pending spellings, not open-ended families.
`make ua-check` also reports a plain count of `needs-confusable-set` notes as a reminder, but
does not try to resolve them.

Usage (Craig runs this — see CLAUDE.md Big 3 Rules):

    python tools/anki/inspect/check_pending_confusables.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.cnsf_canonicalize import split_frontmatter  # noqa: E402
from tools.anki.lib.lexeme_dedup import DEFAULT_LEXEME_ROOT, load_corpus, strip_stress  # noqa: E402

PENDING_PREFIX = "pending-confusable:"
FAMILY_TAG = "needs-confusable-set"


def find_pending(lexeme_root: Path) -> list[dict[str, str]]:
    """Return one row per `pending-confusable:<lemma>` tag found in the corpus."""
    rows: list[dict[str, str]] = []
    for path in sorted(lexeme_root.resolve().rglob("ua-lexeme-*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            fm = split_frontmatter(text, path)
        except ValueError as e:
            print(f"WARNING: skipping {path} — {e}", file=sys.stderr)
            continue
        meta = yaml.safe_load(fm.yaml_text) or {}
        if not isinstance(meta, dict):
            continue

        tags = meta.get("tags", []) or []
        fields = meta.get("fields", {}) or {}
        anchor_id = fields.get("NoteID", path.stem)
        anchor_lemma = fields.get("Lemma", "")

        for tag in tags:
            if isinstance(tag, str) and tag.startswith(PENDING_PREFIX):
                target = tag[len(PENDING_PREFIX):].strip()
                if target:
                    rows.append(
                        {
                            "anchor_id": anchor_id,
                            "anchor_lemma": anchor_lemma,
                            "anchor_path": str(path.resolve().relative_to(REPO_ROOT)),
                            "target": target,
                        }
                    )
    return rows


def count_family_markers(lexeme_root: Path) -> int:
    n = 0
    for path in sorted(lexeme_root.resolve().rglob("ua-lexeme-*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            fm = split_frontmatter(text, path)
        except ValueError:
            continue
        meta = yaml.safe_load(fm.yaml_text) or {}
        if not isinstance(meta, dict):
            continue
        if FAMILY_TAG in (meta.get("tags", []) or []):
            n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lexeme-root", type=Path, default=DEFAULT_LEXEME_ROOT)
    args = parser.parse_args()

    pending = find_pending(args.lexeme_root)
    index = load_corpus(args.lexeme_root)

    resolved = []
    still_pending = []
    for row in pending:
        key = strip_stress(row["target"])
        matches = [m for m in index.get(key, []) if m.note_id != row["anchor_id"]]
        if matches:
            resolved.append((row, matches))
        else:
            still_pending.append(row)

    print(f"{len(pending)} pending-confusable tag(s) found across the corpus.\n")

    if resolved:
        print(f"RESOLVED — target spelling now exists, ready to link ({len(resolved)}):")
        for row, matches in resolved:
            for m in matches:
                print(
                    f"  {row['anchor_id']:<16} ({row['anchor_lemma']}) was waiting on "
                    f"'{row['target']}' -> now exists as {m.note_id} ({m.lemma}, \"{m.gloss}\") "
                    f"at {m.path}"
                )
        print(
            "  Action: hand-author ConfusableSet/Mnemonic_EN/CompareScenario/CompareA-D on both "
            "notes per the usual Compare-card shape, then remove the pending-confusable tag from "
            "the anchor note.\n"
        )
    else:
        print("RESOLVED: none yet.\n")

    if still_pending:
        print(f"Still pending ({len(still_pending)}):")
        for row in still_pending:
            print(f"  {row['anchor_id']:<16} ({row['anchor_lemma']}) waiting on '{row['target']}'")
        print()

    family_count = count_family_markers(args.lexeme_root)
    print(f"Also {family_count} note(s) tagged `{FAMILY_TAG}` (open-ended family, no exact spelling to watch for).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
