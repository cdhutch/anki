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

This script only answers "does this spelling already exist, and if so
where/what does it currently mean" — it does not (and cannot reliably)
decide bucket 2 vs. 3 for you. That judgment call still needs a human (or
Claude) to compare the candidate's intended meaning against the existing
note's EN_Gloss, informed by Горох's homograph blocks where relevant.

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
import unicodedata
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"

COMBINING_ACUTE = "́"


def strip_stress(s: str) -> str:
    """Remove stress marks only (NFD-decompose, drop U+0301, recompose NFC).

    Naive Mn-category stripping is WRONG here: it also destroys letters like
    й/ї that decompose under NFD. Only the combining acute (U+0301) should
    be removed.
    """
    decomposed = unicodedata.normalize("NFD", s)
    stripped = decomposed.replace(COMBINING_ACUTE, "")
    return unicodedata.normalize("NFC", stripped)


def split_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def load_corpus() -> dict[str, list[dict]]:
    """Map stress-stripped Lemma -> list of {note_id, path, gloss, tags_ch}."""
    index: dict[str, list[dict]] = {}
    for path in sorted(LEXEME_ROOT.rglob("ua-lexeme-*.md")):
        text = path.read_text(encoding="utf-8")
        yaml_text = split_frontmatter(text)
        if yaml_text is None:
            print(f"Warning: {path} has no YAML frontmatter — skipping", file=sys.stderr)
            continue
        doc = yaml.safe_load(yaml_text) or {}
        fields = doc.get("fields", {}) or {}
        lemma = fields.get("Lemma", "")
        if not lemma:
            continue
        key = strip_stress(lemma)
        index.setdefault(key, []).append(
            {
                "note_id": fields.get("NoteID", path.stem),
                "path": path.relative_to(REPO_ROOT),
                "lemma": lemma,
                "gloss": fields.get("EN_Gloss", ""),
                "tags_ch": fields.get("Tags_Ch", ""),
                "pos": fields.get("PartOfSpeech", ""),
            }
        )
    return index


def check(candidates: list[str], index: dict[str, list[dict]]) -> bool:
    """Print a report for each candidate. Returns True if any matches found."""
    any_match = False
    for raw in candidates:
        key = strip_stress(raw.strip())
        if not key:
            continue
        matches = index.get(key, [])
        print(f"\n=== {raw} ===")
        if not matches:
            print("  NO MATCH — bucket 1: brand new vocabulary. Create a new note as usual.")
            continue
        any_match = True
        print(f"  {len(matches)} existing note(s) with this spelling — review meaning before deciding:")
        for m in matches:
            print(f"    {m['note_id']}  ({m['pos']})  {m['lemma']}  —  \"{m['gloss']}\"")
            print(f"      {m['path']}")
            print(f"      Tags_Ch: {m['tags_ch']}")
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

    index = load_corpus()
    print(f"Loaded {sum(len(v) for v in index.values())} existing lexeme notes from {LEXEME_ROOT.relative_to(REPO_ROOT)}")
    check(candidates, index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
