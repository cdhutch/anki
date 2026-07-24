#!/usr/bin/env python3
"""tools/anki/extract/gen_ch09_subsection.py — Dedup-wired driver for Ch-09
vocabulary-appendix subsection sourcing.

This is the "generator script" CLAUDE.md item 0 asked to have the dedup/homograph
check wired into. Per `tools/anki/lib/lexeme_dedup.py`'s own docstring: it is "the
entry point future `gen_ua_lexemes_*.py`-style batch scripts should call instead of
writing a new `ua-lexeme-NNNN.md` file directly." This module is that batch script
for the Ch-09 vocabulary appendix specifically (subsections 9.1-9.7), per the process
documented in CLAUDE-ch09-vocab-workflow.md.

What this does NOT automate
----------------------------
The Ch-09 sourcing workflow is inherently judgment-driven, not a pure data pipeline:
Горох verification happens interactively via Claude in Chrome, phrase/component
decomposition requires reading the source PDF, and — critically — the new/duplicate/
homograph call (bucket 2 vs. 3) requires comparing meanings, which `lexeme_dedup.py`'s
own docstring is explicit cannot be automated. So this script does not decide buckets;
it takes a batch of already-drafted candidates (lemma + fields + an explicit
`dedup_decision` already made by whoever ran the Горох/corpus check) and pushes every
one of them through `create_or_link_lexeme()`, so no candidate reaches the corpus by
a hand-written-file path that skips the dedup/homograph check.

Input: a JSON file (see `process_batch`'s docstring for the exact candidate shape) or,
when imported, a Python list of the same dicts.

Output: writes/updates the corresponding `ua-lexeme-*.md` files under
`domains/ua/anki/notes/lexemes/yabluko-l2/ch-09/`, and returns/prints one bucket
result per candidate for review — same "present the full batch for Craig's review"
step the workflow doc already requires, just backed by the dedup library instead of
manual file writes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from tools.anki.lib.lexeme_dedup import (  # noqa: E402
    DedupError,
    DedupOutcome,
    create_or_link_lexeme,
    load_corpus,
    next_note_id,
)

CH09_DIR_NAME = Path("yabluko-l2") / "ch-09"

# UA_Lexeme fields in canonical semantic order (matches CLAUDE.md's documented
# schema / existing ua-lexeme-*.md files). NoteID is assigned by this script, not
# supplied by the caller.
FIELD_ORDER = [
    "Lemma",
    "PartOfSpeech",
    "Gender",
    "Perfective",
    "EN_Gloss",
    "Govt_Case",
    "CounterpartForm",
    "IrregularForms",
    "VerbMotion_Pair",
    "ConfusableSet",
    "Mnemonic_EN",
    "CrossLang_Analog",
    "EuphonyNote",
    "TypingAnswer",
    "UA_Example",
    "EN_Example",
    "Verb_Conj_Table",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]


class BatchError(Exception):
    """Raised for malformed candidate dicts (missing required keys, bad shape) —
    distinct from DedupError, which signals a real dedup/corpus-state problem."""


def _build_note_content(note_id: str, fields: dict[str, Any], tags: list[str]) -> str:
    """Render a full CNSF note file's text for a new note. Final formatting is
    handled by cnsf_canonicalize.py inside create_or_link_lexeme() — this only
    needs to produce YAML that parses, in a reasonable field order for readability
    before canonicalization normalizes it."""
    ordered_fields = {"NoteID": note_id}
    for key in FIELD_ORDER:
        ordered_fields[key] = fields.get(key, "")
    # Preserve any caller-supplied fields outside the standard schema instead of
    # silently dropping them (e.g. a future field not yet in FIELD_ORDER).
    for key, value in fields.items():
        if key not in ordered_fields:
            ordered_fields[key] = value

    meta = {
        "schema": "cnsf/v0",
        "note_type": "ua_lexeme",
        "note_id": note_id,
        "anki": {"model": "UA_Lexeme", "deck": "UA::Recognition::UA→EN"},
        "tags": tags,
        "fields": ordered_fields,
    }
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n"


def process_candidate(
    candidate: dict[str, Any],
    *,
    lexeme_root: Path | None,
    index: dict,
) -> dict[str, Any]:
    """Process one candidate dict through create_or_link_lexeme(). Candidate shape:

    {
      "lemma": "...",                    # required, all buckets
      "dedup_decision": "new" | "duplicate" | "homograph",  # required
      "chapter_tag": "ch:2.9.3",          # required, all buckets
      "fields": {...UA_Lexeme fields...}, # required for new/homograph
      "tags": [...],                      # required for new/homograph
                                           #   (chapter_tag is added automatically
                                           #   if not already present)
      "dated_note": "...",                # required for duplicate
      "homograph_confusable_new": "...",  # required for homograph
      "homograph_confusable_existing": "...",  # required for homograph
    }

    Returns a dict: {"lemma", "bucket", "written": [str, ...], "modified": [str, ...]}
    on success. Raises DedupError (propagated from lexeme_dedup) if the decision is
    inconsistent with corpus state, or BatchError for a malformed candidate dict.
    """
    lemma = candidate.get("lemma")
    decision = candidate.get("dedup_decision")
    if not lemma:
        raise BatchError("candidate missing required key 'lemma'")
    if decision not in ("new", "duplicate", "homograph"):
        raise BatchError(
            f"candidate {lemma!r}: dedup_decision must be 'new', 'duplicate', or "
            f"'homograph', got {decision!r}"
        )
    chapter_tag = candidate.get("chapter_tag")
    if not chapter_tag:
        raise BatchError(f"candidate {lemma!r} missing required key 'chapter_tag'")

    root = lexeme_root
    if decision == "duplicate":
        outcome = create_or_link_lexeme(
            lemma,
            "",
            REPO_ROOT / "_unused.md",
            dedup_decision="duplicate",
            new_chapter_tag=chapter_tag,
            dated_note=candidate.get("dated_note"),
            lexeme_root=root,
            index=index,
        )
    else:
        fields = candidate.get("fields")
        if not fields:
            raise BatchError(f"candidate {lemma!r} missing required key 'fields'")
        tags = list(candidate.get("tags") or [])
        if chapter_tag not in tags:
            tags.append(chapter_tag)
        note_id = candidate.get("note_id") or next_note_id(lexeme_root=root)
        note_dir = (root or (REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes")) / CH09_DIR_NAME
        new_path = note_dir / f"{note_id}.md"
        content = _build_note_content(note_id, fields, tags)

        if decision == "new":
            outcome = create_or_link_lexeme(
                lemma, content, new_path,
                dedup_decision="new",
                lexeme_root=root, index=index,
            )
        else:  # homograph
            outcome = create_or_link_lexeme(
                lemma, content, new_path,
                dedup_decision="homograph",
                homograph_confusable_new=candidate.get("homograph_confusable_new"),
                homograph_confusable_existing=candidate.get("homograph_confusable_existing"),
                lexeme_root=root, index=index,
            )

    return {
        "lemma": lemma,
        "bucket": outcome.bucket,
        "written": [str(p) for p in outcome.written],
        "modified": [str(p) for p in outcome.modified],
    }


def process_batch(
    candidates: list[dict[str, Any]],
    lexeme_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Process a whole subsection's candidates. Builds the corpus index once and
    reuses it across all candidates in the batch (including ones just written by
    an earlier candidate in the same batch — e.g. a phrase's component created
    earlier in the same call) by reloading the index between candidates, since
    load_corpus() is cheap (~180 small files) relative to the value of catching
    within-batch duplicates."""
    results = []
    for candidate in candidates:
        # Reload per-candidate rather than once up front: a candidate can create
        # a new note (e.g. a phrase component) that a later candidate in the same
        # batch needs to see as an existing match.
        index = load_corpus(lexeme_root)
        results.append(process_candidate(candidate, lexeme_root=lexeme_root, index=index))
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("batch_json", help="Path to a JSON file: a list of candidate dicts")
    ap.add_argument("--lexeme-root", default=None, help="Override corpus root (for testing)")
    args = ap.parse_args()

    candidates = json.loads(Path(args.batch_json).read_text(encoding="utf-8"))
    lexeme_root = Path(args.lexeme_root) if args.lexeme_root else None

    results = process_batch(candidates, lexeme_root=lexeme_root)
    for r in results:
        target = r["written"] or r["modified"]
        print(f"{r['bucket']:>10}  {r['lemma']:<20}  {target}")


if __name__ == "__main__":
    main()
