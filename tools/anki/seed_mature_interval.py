#!/usr/bin/env python3
"""Seed a mature FSRS interval for notes newly released from a `type: relearn`
release_plan.yaml group, via AnkiConnect's setDueDate -- so Craig doesn't have
to re-earn a practical review interval from a fresh Learning card on
vocabulary he already knows.

Selection: every ua_lexeme note that is release:active AND relearn:pending
AND not yet relearn:seeded. release_wave.py stamps relearn:pending on every
note it promotes from a `type: relearn` group; a note can also become
eligible via a direct one-time backfill (e.g. ch:1.0/vstup, which was
already release:active before this system existed and so never goes through
release_wave.py's promotion path).

Deliberately a separate tag namespace from release: -- release:pending/active
is the single-value study-pacing gate; relearn:pending/seeded is an
independent single-value marker answering "has this note's mature interval
been seeded yet?" Never both use the release: prefix at once (Craig,
2026-08-29: multiple release:* tags on one note reads as ambiguous).

Must run AFTER the note has actually been synced to Anki and unsuspended
(make ua-lexeme) -- there's nothing to seed until the card exists and is
live; notes not yet synced are skipped with a warning, not silently marked
done. Safe to re-run: a note is seeded at most once, ever, because a
successful seed immediately flips its tag from relearn:pending to
relearn:seeded in the note's own .md file (git-tracked, same pattern as
release:pending -> release:active), and this script only ever looks at
notes still carrying relearn:pending.

Per-card interval (per Craig, 2026-08-29): the EN→UA (Production/typing)
card is harder and more likely to have actually decayed, so it gets a
shorter seed than the UA→EN (Recognition) card. FSRS takes over scheduling
from the first real review after that -- these are a starting point, not a
permanent interval.

    EN→UA (typing/production):    14 days  (--typing-days)
    UA→EN (recognition):          21 days  (--recognition-days)

The Compare card (card 3, homograph/confusable drilling) is deliberately
NOT seeded -- Craig's answer only covered the two vocabulary-recall card
types, and the Compare card's own suspend state is already governed
independently by ConfusableSet (see ua_lexeme_import.py). Note also: the
EN→UA template is configured in Anki as "Dependent on" UA→EN reaching Easy
(see setup_ua_note_types.py) -- if that's still in effect, a seeded EN→UA
card may not surface in study until its UA→EN sibling clears that gate,
even though its due date is set correctly underneath. Worth a live
spot-check the first time this runs.

Requires Anki open with AnkiConnect running (even for --dry-run, so the
preview can show real per-note card counts rather than guessing).

Usage:
    python tools/anki/seed_mature_interval.py                 # apply
    python tools/anki/seed_mature_interval.py --dry-run        # preview, touch nothing
    python tools/anki/seed_mature_interval.py --typing-days 10 --recognition-days 18
    python tools/anki/seed_mature_interval.py --root domains/ua/anki/notes/lexemes/yabluko-l1/ch-00
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

DEFAULT_ROOT = REPO_ROOT / "domains/ua/anki/notes/lexemes"

TAG_LIST_RE = re.compile(r"^tags:\s*\n((?:- .*\n)+)", re.M)
NOTE_ID_RE = re.compile(r"^note_id:\s*(\S+)\s*$", re.M)

RELEARN_PENDING_LINE = "- relearn:pending\n"
RELEARN_SEEDED_LINE = "- relearn:seeded\n"

PRODUCTION_TEMPLATE = "EN→UA"
RECOGNITION_TEMPLATE = "UA→EN"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, c: str) -> None:
    p.write_text(c, encoding="utf-8")


def note_tags(text: str) -> list[str]:
    m = TAG_LIST_RE.search(text)
    if not m:
        return []
    return [line[2:].strip() for line in m.group(1).splitlines()]


def note_id(text: str, fallback: str) -> str:
    m = NOTE_ID_RE.search(text)
    return m.group(1) if m else fallback


def gather_candidates(root: Path) -> list[tuple[Path, str, str]]:
    """(file_path, note_id, file_text) for every note eligible to seed."""
    candidates = []
    for fp in sorted(root.rglob("ua-lexeme-*.md")):
        text = read(fp)
        tags = note_tags(text)
        if not tags:
            continue
        if (
            "relearn:pending" in tags
            and "release:active" in tags
            and "relearn:seeded" not in tags
        ):
            candidates.append((fp, note_id(text, fp.stem), text))
    return candidates


def find_cards_by_template(nid: str, template: str) -> list[int]:
    query = f'note:"{MODEL_NAME}" NoteID:"{nid}" "card:{template}"'
    return anki_request("findCards", {"query": query}, url=ANKI_URL) or []


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Note directory to scan (recursive)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be seeded; touch nothing")
    ap.add_argument("--typing-days", type=int, default=14, help="Seed interval (days) for the EN→UA typing/production card")
    ap.add_argument("--recognition-days", type=int, default=21, help="Seed interval (days) for the UA→EN recognition card")
    args = ap.parse_args()

    if args.typing_days <= 0 or args.recognition_days <= 0:
        raise SystemExit("--typing-days / --recognition-days must be positive")

    version = anki_request("version", {}, url=ANKI_URL)
    if version is None:
        print(
            "Could not reach AnkiConnect -- is Anki open with the AnkiConnect "
            "add-on running?",
            file=sys.stderr,
        )
        return 1

    candidates = gather_candidates(args.root)
    if not candidates:
        print(
            f"No notes eligible for seeding under {args.root} (need relearn:pending "
            "+ release:active, not yet relearn:seeded)."
        )
        return 0

    seeded = 0
    skipped_no_cards: list[str] = []

    for fp, nid, text in candidates:
        prod_ids = find_cards_by_template(nid, PRODUCTION_TEMPLATE)
        recog_ids = find_cards_by_template(nid, RECOGNITION_TEMPLATE)

        if not prod_ids and not recog_ids:
            skipped_no_cards.append(nid)
            print(
                f"  SKIP {nid}: no matching cards found in Anki -- has it been "
                "synced yet? (run make ua-lexeme first)",
                file=sys.stderr,
            )
            continue

        marker = "(dry-run) " if args.dry_run else ""
        parts = []
        if prod_ids:
            parts.append(f"{len(prod_ids)} typing card(s) -> {args.typing_days}d")
        if recog_ids:
            parts.append(f"{len(recog_ids)} recognition card(s) -> {args.recognition_days}d")
        print(f"  {marker}seeding {nid}: " + ", ".join(parts))

        if not args.dry_run:
            if prod_ids:
                anki_request(
                    "setDueDate", {"cards": prod_ids, "days": str(args.typing_days)}, url=ANKI_URL
                )
            if recog_ids:
                anki_request(
                    "setDueDate",
                    {"cards": recog_ids, "days": str(args.recognition_days)},
                    url=ANKI_URL,
                )
            new_text = text.replace(RELEARN_PENDING_LINE, RELEARN_SEEDED_LINE, 1)
            write(fp, new_text)

        seeded += 1

    print()
    if args.dry_run:
        print(
            f"Dry run: would seed {seeded} note(s) "
            f"({len(skipped_no_cards)} skipped -- not yet synced to Anki). "
            "Re-run without --dry-run to apply."
        )
    else:
        print(f"Seeded {seeded} note(s) ({len(skipped_no_cards)} skipped -- not yet synced to Anki).")
        if seeded:
            print(
                "Next: canonicalize the touched files and commit -- relearn:seeded "
                "is now git-tracked, so a re-run of this script will skip these notes."
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
