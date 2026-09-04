#!/usr/bin/env python3
"""tools/anki/inspect/audit_verb_aspect_tags.py — Flag verb notes whose own prose
claims single-aspect (tantum) status but never got the machine-readable tag.

Background (Craig, 2026-08-28, during the яблуко-l2 chapter 11 vocab-expansion
pass): "Make sure that your including the perfective aspect verbs with the
imperfective lemmas" + "Update the testing suite to identify verbs that only
contain one aspect which also don't have specific properties identifying the
verb as specifically single-aspect."

Two existing structured tags already carry this meaning for `ua_lexeme` notes
(see `audit_verb_aspect_forms.py`, added 2026-07-30):

    aspect:imperfective-only  — confirmed imperfectiva tantum (no perfective)
    aspect:perfective-only    — confirmed perfectiva tantum (no imperfective)

Those tags are the "specific property" this script checks for. The gap this
script closes: many notes across the corpus (both `ua_lexeme` and `ua_verb`)
already document tantum status in free-text `Verification Notes` / `Source_Note`
prose (e.g. "imperfectiva tantum", "no perfective counterpart") but were never
given the structured tag -- meaning nothing queryable actually marks them as
single-aspect, and a careless future edit could silently treat the missing
Perfective/partner as an oversight rather than a confirmed linguistic fact.

This script is intentionally narrow and text-driven rather than trying to
algorithmically infer, corpus-wide, whether an aspectual partner exists for
every verb (the яблуко-l2 project draws that conclusion for each verb during
drafting, via Горох + `yabluko-l2-verb-dictionary.pdf`, per the note's own
Verification Notes -- this script only checks that the conclusion, once
stated in prose, is *also* recorded as a structured tag). It is scoped to
verb notes only: `ua_verb` notes, and `ua_lexeme` notes tagged `pos:verb`.

    python -m tools.anki.inspect.audit_verb_aspect_tags
    make ua-check   (wired in alongside the other aspect/confusable audits)
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
VERB_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "verbs"

TAG_IMPERFECTIVE_ONLY = "aspect:imperfective-only"
TAG_PERFECTIVE_ONLY = "aspect:perfective-only"
ASPECT_TANTUM_TAGS = (TAG_IMPERFECTIVE_ONLY, TAG_PERFECTIVE_ONLY)

# Prose signals that a verb note is claiming single-aspect (tantum) status.
# Deliberately verb-aspect-specific ("no perfective counterpart", not just
# "no counterpart") to avoid false positives from unrelated fields (e.g. a
# noun's CrossLang_Analog gloss saying "no direct English counterpart").
TANTUM_SIGNAL_RE = re.compile(
    r"\btantum\b"
    r"|no perfective counterpart"
    r"|no imperfective counterpart"
    r"|no aspectual partner"
    r"|no listed perfective"
    r"|no attested perfective",
    re.IGNORECASE,
)

PROSE_FIELDS = ("Verification Notes", "Source_Note")


def _read_meta(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        doc = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


# The prose-signal regex is a plain substring/keyword match -- it cannot parse
# negation ("this is NOT imperfectiva tantum") or tell whether a "tantum"
# mention in a note's own Verification Notes is describing *this* lemma or a
# *different* one it happens to discuss (e.g. a correction narrative). Both
# cases occur for real in this corpus. Rather than build a fragile NLP layer,
# each confirmed false positive is documented here by hand, once, with the
# reason -- this keeps the corpus-wide gate exact (zero false failures) while
# staying auditable. Do not add an entry here without re-reading the note's
# full Verification Notes/Source_Note and confirming it is genuinely paired
# (has an attested aspectual partner), not actually tantum.
# звучати -- Perfective: прозвучати is populated; VN explicitly says "so this is
#   not imperfectiva tantum" -- the word 'tantum' only appears inside that negation.
# казати -- Perfective: сказати is populated; VN's tantum discussion is about a
#   DIFFERENT lemma (говорити), quoted while explaining why казати's Lemma was
#   corrected away from говорити -- not a claim about казати itself.
# виписати -- VN's stale first sentence ("No imperfective counterpart... drafted
#   this pass") is superseded by its own next sentence: the imperfective partner
#   випи́сувати was added 2026-08-28 (aspect-pairing review). Genuinely paired now.
# виглянути -- VN's tantum mention describes ua-lexeme-0550's stative sense of
#   вигляда́ти (a different lemma/note), quoted while explaining which sense
#   ви́глянути pairs with -- not a claim about ви́глянути itself, whose own
#   imperfective partner (вигляда́ти / ua-verb-0083) is named in the same sentence.
KNOWN_NOT_TANTUM: dict[str, str] = {
    "ua-lexeme-0551": "звучати: negated tantum mention (Perfective прозвучати populated)",
    "ua-lexeme-0317": "казати: tantum text describes говорити, not казати (Perfective сказати populated)",
    "ua-lexeme-0769": "виписати: stale first sentence, superseded within the same note (paired now)",
    "ua-verb-0637": "виглянути: tantum text describes ua-lexeme-0550's stative sense, not виглянути (Imperfective вигляда́ти/ua-verb-0083 populated)",
}


def claims_tantum(fields: dict[str, Any]) -> bool:
    """True if the note's own prose asserts single-aspect (tantum) status."""
    blob = " ".join(str(fields.get(k, "") or "") for k in PROSE_FIELDS)
    return bool(TANTUM_SIGNAL_RE.search(blob))


def has_tantum_tag(tags: list[str]) -> bool:
    return any(t in tags for t in ASPECT_TANTUM_TAGS)


def _is_scoped_verb_note(meta: dict[str, Any], tags: list[str]) -> bool:
    note_type = meta.get("note_type")
    if note_type == "ua_verb":
        return True
    if note_type == "ua_lexeme" and "pos:verb" in tags:
        return True
    return False


def scan(lexeme_root: Path = LEXEME_ROOT, verb_root: Path = VERB_ROOT) -> list[dict[str, Any]]:
    """Scan both note roots; return one row per verb note whose prose claims
    tantum status but which lacks the corresponding structured tag."""
    rows: list[dict[str, Any]] = []
    for root in (lexeme_root, verb_root):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if "exported" in path.parts:
                continue
            meta = _read_meta(path)
            if meta is None:
                continue
            tags = meta.get("tags") or []
            if not isinstance(tags, list):
                tags = []
            if not _is_scoped_verb_note(meta, tags):
                continue

            fields = meta.get("fields") or {}
            if not claims_tantum(fields):
                continue
            if has_tantum_tag(tags):
                continue
            note_id = meta.get("note_id", path.stem)
            if note_id in KNOWN_NOT_TANTUM:
                continue

            rows.append(
                {
                    "note_type": meta.get("note_type"),
                    "note_id": meta.get("note_id", path.stem),
                    "lemma": fields.get("Lemma", ""),
                    "path": path,
                }
            )
    return rows


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def print_report(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print(
            "Clean -- every verb note whose prose claims single-aspect (tantum) status "
            "also carries a structured aspect:imperfective-only/aspect:perfective-only tag."
        )
        return
    print(f"{len(rows)} verb note(s) claim tantum status in prose but lack the structured tag:\n")
    header = f"{'NoteID':<18} {'Type':<10} {'Lemma':<22} Path"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['note_id']:<18} {r['note_type']:<10} {r['lemma']:<22} {_relpath(r['path'])}")
    print(
        "\nEach of these needs either `aspect:imperfective-only` or `aspect:perfective-only` "
        "added to its tags (matching what its own Verification Notes/Source_Note already say)."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lexeme-root", type=Path, default=LEXEME_ROOT)
    ap.add_argument("--verb-root", type=Path, default=VERB_ROOT)
    ap.add_argument("--strict", action="store_true", help="Exit 1 if anything is flagged.")
    args = ap.parse_args()

    rows = scan(args.lexeme_root, args.verb_root)
    print_report(rows)

    if args.strict and rows:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
