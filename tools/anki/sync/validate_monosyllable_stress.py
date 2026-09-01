#!/usr/bin/env python3
"""validate_monosyllable_stress.py — flag monosyllabic Lemma values that still
carry a stress mark.

Ukrainian does not mark stress on a monosyllabic word: with only one syllable
there is no ambiguity to disambiguate, so a stray U+0301 combining acute on a
single-syllable Lemma is simply wrong, not "extra precision." This is the
data-quality mirror of the existing, documented CLAUDE.md rule that a
*missing* stress mark on a MULTIsyllable Lemma is a red flag
(tools/anki/inspect/check_euphony_stress.py enforces that direction for
*_Euphony fields) -- this script enforces the opposite direction for Lemma.

Why this matters beyond spelling purity: for the overwhelming majority of
UA_Lexeme notes ("singlets" -- everything that isn't a verb-aspect doublet/
triplet), `TypingTarget_UA` is `Lemma` verbatim (ua_lexeme_import.py) --
`TypingAnswer` is a separately hand-authored unstressed field and is NOT
derived from Lemma for singlets. So a monosyllabic Lemma with a stray stress
mark means Anki's built-in {{type:Field}} grading is compared against a
target the correct answer (typed without stress, as it should be) can never
exactly match -- the custom feedback JS in setup_ua_note_types.py only reaches
its "~ correct, missing stress" tier instead of a clean match. Confirmed
2026-09-01 on 7 real notes (ра́к x2, сма́к, сті́л, лі́тр, стре́с, зли́й) after
Craig reported not getting full credit typing monosyllabic answers.

Detection rule: Ukrainian has no silent vowels and no true diphthongs, so
vowel-letter count == syllable count reliably, with no exceptions worth
special-casing here. Verb lemmas are never monosyllabic (every infinitive
ends -ти/-тись, itself a syllable), and verb doublets/triplets go through a
separate code path (compute_typing_target()) that already strips stress
correctly regardless -- so this check needs no verb-vs-noun branching, and
no cross-reference against Горох: a single-vowel Lemma is monosyllabic by
construction, full stop.

Multi-word Lemma values (rare) are skipped rather than guessed at -- this
checker only ever looks at a single bare word.

Run as a hard prerequisite of `make ua-lexeme` (see the
ua-monosyllable-validate / _ua-lexeme Makefile targets), same as
validate_clusters.py, so a stray monosyllable stress mark fails the sync
loudly instead of silently shipping a typing-grade bug.

Usage:
    python tools/anki/sync/validate_monosyllable_stress.py [--root PATH]

Exit code 0: no findings.
Exit code 1: one or more monosyllabic Lemma values still carry a stress mark.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

STRESS = "́"
UA_VOWELS = set("аеєиіїоуюяАЕЄИІЇОУЮЯ")
DEFAULT_ROOT = REPO_ROOT / "domains/ua/anki/notes/lexemes"


def syllable_count(word: str) -> int:
    """Vowels == syllables in Ukrainian -- see module docstring."""
    return sum(1 for ch in word if ch in UA_VOWELS)


def scan(root: Path) -> list[tuple[Path, str]]:
    findings = []
    for path in sorted(root.glob("**/ua-lexeme-*.md")):
        try:
            meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        except Exception as exc:  # malformed note is a different checker's job
            print(f"  SKIP (unparseable): {path}  ({exc})", file=sys.stderr)
            continue
        fields = (meta or {}).get("fields") or {}
        lemma = str(fields.get("Lemma") or "").strip()
        if not lemma or " " in lemma:
            continue
        if syllable_count(lemma) == 1 and STRESS in lemma:
            findings.append((path, lemma))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None, help="Lexeme notes root (default: domains/ua/anki/notes/lexemes)")
    args = ap.parse_args()

    root = Path(args.root) if args.root else DEFAULT_ROOT
    if not root.exists():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2

    findings = scan(root)
    if not findings:
        print("OK: no monosyllabic Lemma values carry a stray stress mark.", file=sys.stderr)
        return 0

    print(f"\n{len(findings)} monosyllabic Lemma value(s) with a stress mark that shouldn't be there:", file=sys.stderr)
    for path, lemma in findings:
        print(f"  - {path.relative_to(REPO_ROOT)}: {lemma!r}", file=sys.stderr)
    print(
        "\nUkrainian does not mark stress on a monosyllabic word -- a single syllable has no "
        "ambiguity to disambiguate. This also feeds a typing-grading bug: TypingTarget_UA is "
        "Lemma verbatim for non-verb notes, so a stray mark here means the correct unstressed "
        "answer never earns a clean match. Fix by removing the U+0301 combining acute from "
        "Lemma (and from any confusable_clusters.yaml member `lemma:` copy of the same word).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
