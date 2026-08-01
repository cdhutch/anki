#!/usr/bin/env python3
"""tools/anki/inspect/audit_verb_aspect_forms.py — Scope the verb-aspect typing-target backfill.

New 2026-07-27. The EN→UA typing card for UA_Lexeme verb notes is being changed to require
the full stressed aspect set (e.g. "ходи́ти / йти / піти́" for a multidirectional/
unidirectional/perfective triplet, "перекида́ти / переки́нути" for an imperfective/perfective
doublet, or just "ма́ти" for an imperfective-only singlet with no counterpart) instead of just
`Lemma`. That join is computed at sync time in `ua_lexeme_import.py` from three existing
fields — `Lemma`, `ImperfectiveUnidirectional`, `Perfective` — so no note needs a new field
hand-authored. But `ImperfectiveUnidirectional` (the base unprefixed motion verb's
unidirectional form, e.g. "йти" for ходити/prefixed-ходити verbs, "їхати"'s own unidirectional
counterpart, etc.) has not been systematically populated across the corpus — a first pass
found it empty on every verb note sampled, including the prefixed motion-verb batch
(ua-lexeme-0114–0131) where `Perfective` is already Горох-verified and populated.

Extended 2026-07-30, Craig (originally raised as a `make ua-check` request during Ch-08
verification: "the script should flag verbs where the Perfective field is blank, unless there
is a tag designating imperfective-only form"). Added recognition of two hand-authored tags:

    aspect:imperfective-only   — Craig has confirmed via Горох this verb has no perfective
                                  counterpart (a genuine imperfectiva tantum, e.g. мати).
    aspect:perfective-only     — Craig has confirmed via Горох this verb has no imperfective
                                  counterpart (a genuine perfectiva tantum). Also flags that
                                  Lemma itself is exceptionally the perfective form, since the
                                  schema convention (CLAUDE.md "Aspect convention") is that
                                  Lemma is always imperfective — this tag is the documented
                                  exception to that rule.

IMPORTANT — this script NEVER applies either tag itself, and never will. Craig said explicitly
he wants to be directly involved in every decision that labels a verb as having no aspectual
counterpart, so this script only ever *reads* the tags if a human has already hand-authored
them into the note's CNSF file after checking Горох; it purely reports what still needs a
decision. Do not "helpfully" auto-tag singlets from this script or any future automation
without Craig's sign-off — that would defeat the point of the request.

This script does NOT modify anything. It scans every `ua-lexeme-*.md` tagged `pos:verb`,
reports what's already populated (ready for the join as-is) vs. what's missing, and prints a
classification per note so Craig can decide which need `ImperfectiveUnidirectional`/`Perfective`
looked up and Горох-verified before the new typing target renders correctly for them:

  triplet              — Lemma + ImperfectiveUnidirectional + Perfective all populated (ready)
  doublet              — Lemma + exactly one of {ImperfectiveUnidirectional, Perfective} (ready)
  confirmed-imperfective-only — singlet, but tagged aspect:imperfective-only (ready, no
                          action needed — Craig has already confirmed there's no counterpart)
  confirmed-perfective-only   — tagged aspect:perfective-only (ready, no action needed —
                          Craig has already confirmed the Lemma-is-perfective exception)
  singlet              — only Lemma populated, NOT tagged either aspect:*-only — needs Craig's
                          review/decision (may turn out to be genuinely imperfective-only, e.g.
                          мати, but that hasn't been confirmed and tagged yet)
  candidate            — Lemma + `VerbMotion_Pair` populated but ImperfectiveUnidirectional is
                          empty — VerbMotion_Pair already records e.g. "іти / ходити" as a
                          cross-reference note, a strong hint this note's own triplet is
                          incomplete, even though it doesn't by itself tell us the correct
                          unidirectional form/stress.

Craig runs this (see CLAUDE.md Big 3 Rules — Claude does not run scripts in this repo itself):

    python tools/anki/inspect/audit_verb_aspect_forms.py

Also wired into `make ua-check` (report-only; STRICT=1 to fail the build on anything still
needing review) alongside check_pending_confusables.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.cnsf_canonicalize import split_frontmatter  # noqa: E402

DEFAULT_LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"

TAG_IMPERFECTIVE_ONLY = "aspect:imperfective-only"
TAG_PERFECTIVE_ONLY = "aspect:perfective-only"

READY_CLASSIFICATIONS = (
    "triplet",
    "doublet",
    "confirmed-imperfective-only",
    "confirmed-perfective-only",
)
NEEDS_REVIEW_CLASSIFICATIONS = (
    "singlet",
    "candidate (has VerbMotion_Pair, missing ImperfectiveUnidirectional)",
)


def classify(lemma: str, impf_uni: str, perfective: str, verb_motion_pair: str, tags: list[str]) -> str:
    if not lemma:
        return "unknown (no Lemma)"
    if impf_uni and perfective:
        return "triplet"
    if impf_uni or perfective:
        return "doublet"
    # No counterpart populated. Check for Craig's hand-authored aspect-only tags before
    # falling through to "needs review" — these tags are never applied by this script.
    if TAG_IMPERFECTIVE_ONLY in tags:
        return "confirmed-imperfective-only"
    if TAG_PERFECTIVE_ONLY in tags:
        return "confirmed-perfective-only"
    if verb_motion_pair:
        return "candidate (has VerbMotion_Pair, missing ImperfectiveUnidirectional)"
    return "singlet"


def scan(lexeme_root: Path) -> list[dict[str, str]]:
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
        if "pos:verb" not in tags:
            continue

        fields = meta.get("fields", {}) or {}
        lemma = fields.get("Lemma", "") or ""
        impf_uni = fields.get("ImperfectiveUnidirectional", "") or ""
        perfective = fields.get("Perfective", "") or ""
        verb_motion_pair = fields.get("VerbMotion_Pair", "") or ""

        rows.append(
            {
                "NoteID": fields.get("NoteID", path.stem),
                "Lemma": lemma,
                "ImperfectiveUnidirectional": impf_uni,
                "Perfective": perfective,
                "VerbMotion_Pair": verb_motion_pair,
                "Classification": classify(lemma, impf_uni, perfective, verb_motion_pair, tags),
                "Path": str(path.resolve().relative_to(REPO_ROOT)),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lexeme-root", type=Path, default=DEFAULT_LEXEME_ROOT)
    parser.add_argument("--strict", action="store_true", help="Exit 1 if anything still needs review.")
    args = parser.parse_args()

    rows = scan(args.lexeme_root)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["Classification"]] = counts.get(r["Classification"], 0) + 1

    print(f"{len(rows)} verb notes (pos:verb) found.\n")
    print("By classification:")
    for cls, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>3}  {cls}")
    print()

    confirmed = [r for r in rows if r["Classification"] in ("confirmed-imperfective-only", "confirmed-perfective-only")]
    if confirmed:
        print(f"Confirmed aspect-only, Craig-tagged (no action needed) ({len(confirmed)}):")
        for r in confirmed:
            print(f"  {r['NoteID']:<18} {r['Lemma']:<22} {r['Classification']}")
        print()

    needs_review = [r for r in rows if r["Classification"] in NEEDS_REVIEW_CLASSIFICATIONS]
    print(f"Notes to review for a possible missing ImperfectiveUnidirectional/Perfective ({len(needs_review)}):")
    print("(A 'singlet' may be genuinely imperfective-only -- e.g. мати -- but Claude never")
    print(" tags that for you. Confirm via Горох yourself, then hand-add `aspect:imperfective-only`")
    print(" or `aspect:perfective-only` to the note's tags so future runs skip it.)\n")
    header = f"{'NoteID':<18} {'Lemma':<22} {'Perfective':<22} {'VerbMotion_Pair':<20} Classification"
    print(header)
    print("-" * len(header))
    for r in needs_review:
        print(f"{r['NoteID']:<18} {r['Lemma']:<22} {r['Perfective']:<22} {r['VerbMotion_Pair']:<20} {r['Classification']}")

    print(f"\nReady as-is (triplet/doublet/confirmed-aspect-only, no action needed for the sync-time join):")
    ready = [r for r in rows if r["Classification"] in ("triplet", "doublet")]
    for r in ready:
        print(f"  {r['NoteID']:<18} {r['Lemma']:<22} impf_uni={r['ImperfectiveUnidirectional'] or '-':<15} perfective={r['Perfective'] or '-'}")

    if args.strict and needs_review:
        print(f"\nSTRICT: {len(needs_review)} note(s) still need review.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
