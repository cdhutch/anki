#!/usr/bin/env python3
"""Promote release:pending notes to release:active in controlled batches.

Reads domains/ua/anki/config/release_plan.yaml, a small set of named groups
(each a list of tag glob patterns + a per-run batch size). For each group,
finds every note under --root (default: domains/ua/anki/notes/lexemes) that
is release:pending and has at least one tag matching the group's patterns,
sorts the matches by NoteID, and flips up to `batch_size` of them from
release:pending to release:active -- oldest NoteID first, one flip per note.

This is the "config stored in the repo" pacing lever: status:draft/verified
(content quality) and release:pending/active (study-pacing, see
tools/anki/sync/ua_lexeme_import.py's AND-gate) are independent, so a whole
chapter can be fully authored and verified while still sitting suspended,
released into rotation a batch at a time as you're ready for more.

A group with nothing left pending is a safe no-op -- leave it in the file or
delete it, either way. Re-run this script whenever you want the next slice.
After running, re-canonicalize the touched files and run the normal Anki
sync (cnsf_to_anki.sh) so the AND-gate's unsuspend logic picks up the newly
released notes.

A group with `type: relearn` set is re-releasing material you already know
rather than brand-new vocabulary: every note promoted from such a group also
gets a `relearn:pending` tag (in addition to the release:active flip). After
the sync unsuspends those notes' cards, run
`python tools/anki/seed_mature_interval.py` to seed them with a mature FSRS
interval via AnkiConnect instead of re-earning it from a fresh Learning card.

Usage:
    python tools/anki/release_wave.py                      # apply, using the plan
    python tools/anki/release_wave.py --dry-run             # show what would change
    python tools/anki/release_wave.py --plan path/to.yaml   # use a different plan file
    python tools/anki/release_wave.py --root domains/ua/anki/notes/verbs  # other note type
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("Missing dependency: PyYAML. Install with: pip install pyyaml") from e

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = REPO_ROOT / "domains/ua/anki/config/release_plan.yaml"
DEFAULT_ROOT = REPO_ROOT / "domains/ua/anki/notes/lexemes"

TAG_LIST_RE = re.compile(r"^tags:\s*\n((?:- .*\n)+)", re.M)
NOTE_ID_RE = re.compile(r"^note_id:\s*(\S+)\s*$", re.M)
PENDING_LINE = "- release:pending\n"
ACTIVE_LINE = "- release:active\n"
RELEARN_LINE = "- relearn:pending\n"


def load_plan(plan_path: Path) -> list[dict]:
    if not plan_path.exists():
        raise SystemExit(f"Release plan not found: {plan_path}")
    with plan_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        raise SystemExit(f"{plan_path}: 'groups' must be a list")
    for g in groups:
        if "name" not in g or "match" not in g or "batch_size" not in g:
            raise SystemExit(f"{plan_path}: each group needs name, match, batch_size: {g}")
        if not isinstance(g["match"], list) or not g["match"]:
            raise SystemExit(f"{plan_path}: group {g['name']!r} 'match' must be a non-empty list")
        if not isinstance(g["batch_size"], int) or g["batch_size"] < 0:
            raise SystemExit(f"{plan_path}: group {g['name']!r} 'batch_size' must be a non-negative int")
        if "type" in g and g["type"] not in (None, "relearn"):
            raise SystemExit(
                f"{plan_path}: group {g['name']!r} has unknown type {g['type']!r} "
                f"-- only 'relearn' is currently supported (or omit the field entirely)"
            )
    return groups


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


def matches_group(tags: list[str], patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(tag, pat) for tag in tags for pat in patterns)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", type=Path, default=DEFAULT_PLAN, help="Path to release_plan.yaml")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Note directory to scan (recursive)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be promoted; touch nothing")
    args = ap.parse_args()

    groups = load_plan(args.plan)
    if not groups:
        print(f"{args.plan}: no groups defined -- nothing to do.")
        return 0

    files = sorted(args.root.rglob("*.md"))
    if not files:
        print(f"No .md files found under {args.root}")
        return 1

    # Pre-parse every file once.
    parsed = []
    for fp in files:
        text = read(fp)
        tags = note_tags(text)
        if not tags:
            continue
        nid = note_id(text, fp.stem)
        parsed.append((fp, nid, tags, text))

    total_promoted = 0
    total_relearn_tagged = 0
    any_zero_match_group = False
    already_promoted_paths: set[Path] = set()  # across groups within this run --
    # a note can carry tags from more than one group's patterns (e.g. a word
    # reused across an L1 and an L2 chapter), and it must only be promoted once
    # per run, by whichever group processes it first.

    for g in groups:
        name = g["name"]
        patterns = g["match"]
        batch_size = g["batch_size"]
        group_type = g.get("type")

        candidates = [
            (fp, nid, text)
            for fp, nid, tags, text in parsed
            if fp not in already_promoted_paths
            and "release:pending" in tags
            and matches_group(tags, patterns)
        ]
        candidates.sort(key=lambda t: t[1])  # by NoteID

        already_active = sum(
            1
            for _, _, tags, _ in parsed
            if "release:active" in tags and matches_group(tags, patterns)
        )
        total_matching = len(candidates) + already_active

        if total_matching == 0:
            any_zero_match_group = True
            print(f"[{name}] no notes match {patterns!r} at all -- check for a typo?")
            continue

        to_promote = candidates[:batch_size] if batch_size else []
        print(
            f"[{name}] {len(candidates)} pending / {total_matching} total match "
            f"-- promoting {len(to_promote)} this run"
        )

        for fp, nid, text in to_promote:
            if PENDING_LINE not in text:
                print(f"  WARNING: {fp} matched but has no bare '- release:pending' line -- skipped", file=sys.stderr)
                continue
            new_text = text.replace(PENDING_LINE, ACTIVE_LINE, 1)
            relearn_tagged = False
            if group_type == "relearn" and RELEARN_LINE not in new_text:
                new_text = new_text.replace(ACTIVE_LINE, ACTIVE_LINE + RELEARN_LINE, 1)
                relearn_tagged = True
            if not args.dry_run:
                write(fp, new_text)
            already_promoted_paths.add(fp)
            marker = "(dry-run) " if args.dry_run else ""
            suffix = " [relearn:pending]" if relearn_tagged else ""
            print(f"  {marker}promoted {nid}{suffix}  ({fp.relative_to(REPO_ROOT)})")
            total_promoted += 1
            if relearn_tagged:
                total_relearn_tagged += 1

    print()
    if args.dry_run:
        print(f"Dry run: would promote {total_promoted} note(s). Re-run without --dry-run to apply.")
        if total_relearn_tagged:
            print(f"({total_relearn_tagged} of those would be tagged relearn:pending.)")
    else:
        print(f"Promoted {total_promoted} note(s).")
        if total_promoted:
            print(
                "Next: canonicalize the touched files, run the test suite, then re-run "
                "the normal Anki sync (cnsf_to_anki.sh) to unsuspend them."
            )
        if total_relearn_tagged:
            print(
                f"{total_relearn_tagged} of those were tagged relearn:pending. After the "
                "sync above, run `python tools/anki/seed_mature_interval.py` to seed them "
                "with a mature interval instead of a fresh Learning card."
            )
    if any_zero_match_group:
        print("Note: one or more groups matched zero notes -- see warnings above.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
