#!/usr/bin/env python3
"""check_lexeme_dedup.py — Exact-spelling dedup lookup for UA_Lexeme sourcing.

Before drafting a new ua-lexeme note, check whether the spelling already
exists in the corpus. Every candidate falls into one of three buckets:

  1. No match          -> brand new vocabulary, create a new note as usual.
  2. Match, different
     meaning            -> homograph. Create a new note, but cross-link both
                            via ConfusableSet and tag both `homograph:true`.
                            See CLAUDE.md "Vocabulary dedup & homograph
                            handling" for the full procedure.
  3. Match, same
     meaning            -> true duplicate. Do NOT create a new note — append
                            the new chapter tag to the existing note's
                            Tags_Ch/tags and a dated line to
                            "Verification Notes" instead.

This is the manual, read-only checker for ad hoc use. The per-batch
generator scripts should instead call
`tools.anki.lib.lexeme_dedup.create_or_link_lexeme(...)` directly so the
check and the resulting file edits happen as one step — see that module
and CLAUDE.md "Vocabulary dedup & homograph handling" for details. This
script shares its lookup primitives (`strip_stress`, `load_index`) with
that module rather than duplicating them.

Usage:
    python tools/anki/inspect/check_lexeme_dedup.py <lemma> [<lemma> ...]
    python tools/anki/inspect/check_lexeme_dedup.py --file candidates.txt

Lemmas may be given with or without stress marks; comparison is always
stress-stripped. Matching is exact-spelling only (post stress-strip) — it
will not catch inflected forms or near-misses, only the bare lemma spelling.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"

sys.path.insert(0, str(REPO_ROOT))

from tools.anki.lib.lexeme_dedup import (  # noqa: E402
    LexemeRecord,
    load_index,
    lookup,
    strip_stress,
)


def check(candidates: list[str], index: dict[str, list[LexemeRecord]]) -> bool:
    """Print a report for each candidate. Returns True if any matches found."""
    any_match = False
    for raw in candidates:
        stripped = raw.strip()
        if not stripped:
            continue
        matches = lookup(stripped, index)
        print(f"\n=== {raw} ===")
        if not matches:
            print("  NO MATCH — bucket 1: brand new vocabulary. Create a new note as usual.")
            continue
        any_match = True
        print(f"  {len(matches)} existing note(s) with this spelling — review meaning before deciding:")
        for m in matches:
            print(f"    {m.note_id}  ({m.pos})  {m.lemma}  —  \"{m.gloss}\"")
            print(f"      {m.path.relative_to(REPO_ROOT) if m.path.is_absolute() else m.path}")
            print(f"      Tags_Ch: {m.tags_ch}")
        print(
            "  If the intended meaning MATCHES an existing note above -> bucket 3: "
            "true duplicate. Do NOT create a new note; append the new chapter tag "
            "instead (see CLAUDE.md)."
        )
        print(
            "  If the intended meaning is UNRELATED to all notes above -> bucket 2: "
            "homograph. Create a new note, then cross-link via ConfusableSet and tag "
            "both `homograph:true` (see CLAUDE.md)."
        )
    return any_match


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lemmas", nargs="*", help="Candidate lemma(s) to check")
    parser.add_argument("--file", help="Path to a file with one candidate lemma per line")
    args = parser.parse_args()

    candidates = list(args.lemmas)
    if args.file:
        file_path = Path(args.file)
        candidates.extend(
            line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()
        )

    if not candidates:
        parser.error("Provide at least one lemma (positionally or via --file)")

    index = load_index(LEXEME_ROOT)
    print(f"Loaded {sum(len(v) for v in index.values())} existing lexeme notes from {LEXEME_ROOT.relative_to(REPO_ROOT)}")
    check(candidates, index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
