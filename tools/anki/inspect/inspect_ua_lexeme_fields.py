#!/usr/bin/env python3
"""Inspect UA_Lexeme field names and propose semantic ordering.

Usage
-----
  python tools/anki/inspect/inspect_ua_lexeme_fields.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402


def main() -> int:
    url = "http://127.0.0.1:8765"

    print("Fetching UA_Lexeme field names from Anki...\n")

    try:
        fields = anki_request("modelFieldNames", {"modelName": "UA_Lexeme"}, url=url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not fields:
        print("No fields found", file=sys.stderr)
        return 1

    print("Current UA_Lexeme fields (in current order):")
    print("=" * 80)
    for i, field in enumerate(fields, 1):
        print(f"{i:2d}. {field}")

    print("\n" + "=" * 80)
    print("\nProposed semantic ordering:")
    print("=" * 80)

    proposed_order = [
        # Identity & Metadata
        ("NoteID", "Unique identifier"),

        # Core Lemma & Morphology
        ("Lemma", "Headword (typically IPFV for verbs)"),
        ("PartOfSpeech", "POS: noun, verb, adj, etc."),
        ("Gender", "Grammatical gender (m/f/n)"),

        # Aspect (Motion Verbs)
        ("Perfective", "PFV counterpart (if verb)"),
        ("ImperfectiveUnidirectional", "Directional IPFV (motion verbs: іти, їхати)"),

        # Semantic Content
        ("EN_Gloss", "English translation/meaning"),

        # Grammatical Properties
        ("Govt_Case", "Case government (if applicable)"),
        ("IrregularForms", "Irregular plurals, genitive, etc."),
        ("CounterpartForm", "Cross-gender pair (e.g., f: акто́рка)"),

        # Verb-Specific Relations
        ("VerbMotion_Pair", "Base unprefixed motion verb pair"),

        # Semantic Relations & Notes
        ("ConfusableSet", "Related/confusable words"),
        ("CrossLang_Analog", "Cross-linguistic analog"),
        ("EuphonyNote", "Pronunciation/euphony notes"),

        # Typing & Examples
        ("TypingAnswer", "Lemma without stress marks (for typing)"),
        ("UA_Example", "Ukrainian example sentence"),
        ("EN_Example", "English translation of example"),

        # Metadata & Sources
        ("Tags_Ch", "Chapter/topic tags"),
        ("Source_URL", "Горох/dictionary URL"),
        ("Source_Note", "Verification notes, corrections, etc."),
    ]

    for i, (field, description) in enumerate(proposed_order, 1):
        status = "✓" if field in fields else "✗"
        print(f"{i:2d}. {status} {field:35s} — {description}")

    print("\n" + "=" * 80)
    print("\nSummary:")
    print(f"  Total fields: {len(fields)}")
    print(f"  Proposed order fields: {len(proposed_order)}")

    missing = set(fields) - {f for f, _ in proposed_order}
    if missing:
        print(f"  Missing from proposal: {missing}")

    extra = {f for f, _ in proposed_order} - set(fields)
    if extra:
        print(f"  Extra in proposal: {extra}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
