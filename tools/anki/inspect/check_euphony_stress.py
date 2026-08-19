#!/usr/bin/env python3
"""Flag CNSF `*_Euphony` values that are missing a stress mark.

Convention (decided by Craig, 2026-08-18): a populated `*_Euphony` field always
carries its stress mark, and there is deliberately NO `*_Euphony_Typing`
companion field -- the unstressed form is DERIVED by stripping U+0301 at
comparison time, never stored, so a stored pair cannot drift out of sync.

Why this checker exists rather than trusting authoring discipline: today the
stress mark in a euphony field is completely inert. Both feedback scripts
(`EN_UA_BACK` in setup_ua_note_types.py, `FEEDBACK_SCRIPT` in
setup_ua_pvom_note_type.py) stripStress() the stored alternates AND the typed
answer before comparing, so an unstressed euphony value grades identically to a
stressed one. Nothing anywhere would notice the convention being broken -- and
that is exactly how UA_PVOM_Infinitive came to store all four of its euphony
values unstressed while UA_Lexeme stored all of its stressed, with neither side
wrong by any check that existed.

That inertness ends with the planned Option B refactor (see
docs/ua-en-ua-euphony-aspect-refactor.md), where a fully-stressed euphonic
alternate earns PERFECT and the stressed form becomes load-bearing. Any value
authored unstressed before then has to be re-sourced. Catching it at authoring
time is the whole point.

Detection rule mirrors this project's existing data-quality principle (see
CLAUDE.md, "Language conventions"): a MULTISYLLABLE form with zero stress marks
is a red flag. Monosyllables are exempt -- Ukrainian does not mark stress on
them, so `й` or `з` carrying no mark is correct, not missing. Multi-word phrase
values are checked per word, and a value with two marks is fine (free/variant
stress is a legitimate outcome, also per CLAUDE.md -- do NOT "fix" those).

Report-only by default, like the other `make ua-check` audits. Pass --strict to
exit non-zero on findings.

Usage:
    python tools/anki/inspect/check_euphony_stress.py
    python tools/anki/inspect/check_euphony_stress.py --strict
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

NOTE_ROOTS = [
    ("UA_Lexeme", "domains/ua/anki/notes/lexemes", "**/ua-lexeme-*.md"),
    ("UA_PVOM_Infinitive", "domains/ua/anki/notes/pvom", "ua-pvom-*.md"),
    # UA_Verb / UA_Grammar / UA_Visual have no *_Euphony fields; listed here as
    # a deliberate omission rather than an oversight. If one ever grows them,
    # add it and the checker covers it with no other change.
]


def syllable_count(word: str) -> int:
    """Vowels == syllables in Ukrainian, which is what makes this rule cheap."""
    return sum(1 for ch in word if ch in UA_VOWELS)


def missing_stress(value: str) -> list[str]:
    """Return the multisyllabic words in `value` that carry no stress mark.

    Per-word rather than per-value: a phrase like "у порівня́нні" has a
    monosyllabic (in fact vowel-only) preposition that correctly carries no
    mark, and flagging the whole value because of it would train people to
    ignore this checker.
    """
    bad = []
    for word in value.split():
        if syllable_count(word) > 1 and STRESS not in word:
            bad.append(word)
    return bad


def scan() -> list[tuple[str, str, str, str, list[str]]]:
    findings = []
    for label, root, pattern in NOTE_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in sorted(base.glob(pattern)):
            try:
                meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            except Exception as exc:  # malformed note is someone else's checker's job
                print(f"  SKIP (unparseable): {path}  ({exc})")
                continue
            fields = (meta or {}).get("fields") or {}
            for key, value in fields.items():
                if not key.endswith("_Euphony"):
                    continue
                value = str(value or "").strip()
                if not value:
                    continue
                # Alternates are pipe-delimited within one field.
                for alt in value.split("|"):
                    alt = alt.strip()
                    if not alt:
                        continue
                    bad = missing_stress(alt)
                    if bad:
                        findings.append((label, path.name, key, alt, bad))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is flagged")
    args = ap.parse_args()

    findings = scan()
    if not findings:
        print("  All populated *_Euphony values carry stress marks.")
        return 0

    print(f"  {len(findings)} euphony value(s) missing a stress mark:")
    for label, name, key, value, bad in findings:
        print(f"    {label:20} {name:22} {key:36} {value!r}")
        print(f"      {'':20} unstressed multisyllable(s): {', '.join(bad)}")
    print()
    print("  Convention (Craig, 2026-08-18): *_Euphony values always carry stress; the")
    print("  unstressed form is derived by stripping, never stored -- so there is no")
    print("  *_Euphony_Typing field. This is inert today (both feedback scripts strip")
    print("  stress before comparing) but load-bearing after the Option B refactor, where")
    print("  a fully-stressed euphonic alternate earns PERFECT. See")
    print("  docs/ua-en-ua-euphony-aspect-refactor.md.")
    print()
    print("  Fix by sourcing the stressed form from Горох (or from an existing verified")
    print("  note carrying the same word) -- do NOT guess a stress position.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
