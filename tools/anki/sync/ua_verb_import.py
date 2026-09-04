#!/usr/bin/env python3
"""Import ua_verb CNSF notes into Anki via AnkiConnect.

Upsert logic: adds new notes, updates fields on existing notes (matched by NoteID).

Deck layout:
    UA::Verbs    ← All verb conjugation paradigm cards

Suspension policy:
    - status:draft OR release:pending → suspend cards after import
      (inactive / not yet released)
    - status:verified AND release:active → unsuspend cards (active verbs,
      used in current chapters; release: added 2026-08-29 per Craig as a
      second, independent gate -- see should_suspend())
    - (conj:drill/conj:suspended curation axis removed 2026-08-27, per Craig --
      all verified verbs are now active for drilling, not just class leaders,
      since class leaders trickle in gradually as older chapters are backfilled)
    - note has a red-flagged card → keep suspended (added 2026-07-31, per Craig
      -- see get_flagged_note_ids_by_color in tsv_to_anki.py). Only checked
      for existing notes; a brand-new note can't already have a flagged card.
    - note has an orange-flagged card, no red → NOT suspended. Called out in
      the sync log instead (2026-08-10, per Craig -- orange means "confusing/
      unclear", not "wrong"; see CLAUDE-flag-audit.md).
    - per-category card suspension (added 2026-09-03, per Craig; see
      CLAUDE.md "Remaining Work" item 21): independent of the whole-note
      suspend decision above, each of the four Production cards (Present /
      Past / Imperative / Participles) is suspended on its own if every
      field in that card's own category is blank on this note -- e.g.
      стосуватися (ua-verb-0076, a defective 3rd-person-only verb) has no
      Imperative_* forms at all, so only its Imperative card suspends; its
      Present card stays active (Pres_3sg/Pres_3pl are populated). This
      replaces the old suspend_participles_card(), which blanket-suspended
      every note's Participles card regardless of whether participles were
      actually populated -- see sync_card_suspension().
      Deletion (Craig's other option) isn't practical per note: an AnkiConnect
      card belongs to its note type's template, so removing a template
      removes that category for every verb, including ones that do have
      those forms -- suspension is the only per-note mechanism available.
      Participles is the one exception to the content check: it's flagged
      force_suspend=True in CARD_FIELD_CATEGORIES (added same day, per
      Craig -- "I want the participles to be suspended, since I haven't
      gotten to learning how to form them yet") and stays suspended
      regardless of content, a curriculum-pacing call, not a data-quality
      one. Present/Past/Imperative are unaffected.

Usage (with Anki open + AnkiConnect running):
    # Dry run — show what would be added/updated, touch nothing
    python tools/anki/sync/ua_verb_import.py --dry-run domains/ua/anki/notes/verbs/

    # Import a single file
    python tools/anki/sync/ua_verb_import.py domains/ua/anki/notes/verbs/ua-verb-0001.md

    # Import all verb files
    python tools/anki/sync/ua_verb_import.py domains/ua/anki/notes/verbs/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import (  # noqa: E402
    FLAG_ORANGE,
    FLAG_RED,
    anki_request,
    describe_note_ids,
    flag_query_for_model,
    get_flagged_note_ids_by_color,
)

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Verb"
DECK_NAME = "UA::Verbs"

# Flag-query scope for the red/orange-flag check -- scoped to this note type
# (2026-08-20); see flag_query_for_model() in tsv_to_anki.py.
FLAG_DECK_QUERY = flag_query_for_model(MODEL_NAME)

# Which CNSF fields belong to each Production card, in the same order as
# VERB_CARD_TEMPLATES in tools/anki/setup/setup_ua_note_types.py (added
# 2026-09-03, per Craig -- see sync_card_suspension()). findCards
# returns a note's cards in creation order, so index N here must keep
# matching template index N there; if VERB_CARD_TEMPLATES is ever reordered
# or a 5th card added, update this list to match.
#
# Third element (force_suspend): when True, this card is suspended
# unconditionally regardless of content -- a curriculum-pacing decision, not
# a content-completeness one. Participles is force_suspend=True (2026-09-03,
# per Craig: "I want the participles to be suspended, since I haven't gotten
# to learning how to form them yet") -- this deliberately reverts the
# same-day content-based unsuspend for Participles specifically (see item 21
# in CLAUDE.md) back to the original suspend_participles_card() behavior,
# while keeping the new content-based check for Present/Past/Imperative. Flip
# this to False once participle drilling is actually underway.
CARD_FIELD_CATEGORIES = [
    ("Production (Present)", ["Pres_1sg", "Pres_2sg", "Pres_3sg", "Pres_1pl", "Pres_2pl", "Pres_3pl"], False),
    ("Production (Past)", ["Past_1sg_m", "Past_1sg_f", "Past_1sg_n", "Past_3pl"], False),
    ("Production (Imperative)", ["Imperative_2sg", "Imperative_1pl", "Imperative_2pl"], False),
    (
        "Production (Participles)",
        [
            "Participle_Active_Present",
            "Participle_Adverbial_Present",
            "Participle_Passive_Past",
            "Participle_Impersonal_Past",
            "Participle_Adverbial_Past",
        ],
        True,
    ),
]


# ---------------------------------------------------------------------------
# AnkiConnect helpers
# ---------------------------------------------------------------------------


def ensure_deck(deck_name: str, dry_run: bool):
    if dry_run:
        return
    anki_request("createDeck", {"deck": deck_name}, url=ANKI_URL)


def find_note_by_id(note_id: str) -> int | None:
    query = f'note:"{MODEL_NAME}" NoteID:"{note_id}"'
    results = anki_request("findNotes", {"query": query}, url=ANKI_URL)
    return int(results[0]) if results else None


def add_note(fields: dict, tags: list[str], dry_run: bool) -> int | None:
    if dry_run:
        return None
    return anki_request(
        "addNote",
        {
            "note": {
                "modelName": MODEL_NAME,
                "deckName": DECK_NAME,
                "fields": fields,
                "tags": tags,
                "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            }
        },
        url=ANKI_URL,
    )


def update_note(anki_id: int, fields: dict, tags: list[str], dry_run: bool):
    if dry_run:
        return
    anki_request("updateNoteFields", {"note": {"id": anki_id, "fields": fields}}, url=ANKI_URL)
    existing_tags = anki_request("getNoteTags", {"note": anki_id}, url=ANKI_URL) or []
    if existing_tags:
        anki_request("removeTags", {"notes": [anki_id], "tags": " ".join(existing_tags)}, url=ANKI_URL)
    if tags:
        anki_request("addTags", {"notes": [anki_id], "tags": " ".join(tags)}, url=ANKI_URL)


def category_is_empty(fields: dict, field_names: list[str]) -> bool:
    """True if every one of field_names is blank/whitespace-only in fields.

    Pure logic, no AnkiConnect -- unit-tested directly in
    tests/ua/test_ua_verb_import.py.
    """
    return all(not (fields.get(name) or "").strip() for name in field_names)


def category_should_suspend(fields: dict, field_names: list[str], force_suspend: bool) -> bool:
    """Decision for a single Production card: force_suspend (a curriculum-
    pacing override, e.g. Participles -- see CARD_FIELD_CATEGORIES) always
    wins; otherwise falls back to the content check (category_is_empty).

    Pure logic, no AnkiConnect -- unit-tested directly in
    tests/ua/test_ua_verb_import.py.
    """
    if force_suspend:
        return True
    return category_is_empty(fields, field_names)


def compute_card_suspension_targets(fields: dict, note_suspend: bool) -> list[bool]:
    """The target suspended state for each of the four Production cards, in
    CARD_FIELD_CATEGORIES order.

    note_suspend is the whole-note gate (should_suspend()/red-flag override)
    -- when True it wins outright and every card suspends, matching the old
    blanket set_suspended(True) behavior. Otherwise each card gets its own
    category_should_suspend() decision (added 2026-09-03, per Craig -- see
    CLAUDE.md "Remaining Work" item 21).

    Pure logic, no AnkiConnect -- unit-tested directly in
    tests/ua/test_ua_verb_import.py.
    """
    if note_suspend:
        return [True] * len(CARD_FIELD_CATEGORIES)
    return [
        category_should_suspend(fields, field_names, force_suspend)
        for _name, field_names, force_suspend in CARD_FIELD_CATEGORIES
    ]


def sync_card_suspension(anki_note_id: int, fields: dict, note_suspend: bool, dry_run: bool):
    """Suspend or unsuspend all four Production cards for a note in one pass.

    Replaces the old two-step set_suspended() + sync_category_card_suspension()
    pairing (2026-09-03 same-day fix, per Craig's report of a misleading
    "changed" log). That pairing's final suspended states were always
    correct -- confirmed twice via Craig's own AnkiConnect spot-checks -- but
    its "changed" print was not: set_suspended() unconditionally unsuspended
    every card first (when note_suspend was False), and only then did the
    old function read cardsInfo to compute its "was this card previously
    suspended" baseline for the print, so that baseline was always
    post-reset (False) rather than the true prior persisted state. Every
    empty/force-suspended category (Participles chief among them) logged a
    false "-> suspended" flip on every single sync as a result, even when
    nothing had actually changed since the last run.

    This version reads cardsInfo exactly once, before issuing any
    suspend/unsuspend calls, via compute_card_suspension_targets() -- so the
    "changed" print now reflects genuine flips only.
    """
    if dry_run:
        return
    card_ids = anki_request("findCards", {"query": f"nid:{anki_note_id}"}, url=ANKI_URL)
    if not card_ids:
        return
    targets = compute_card_suspension_targets(fields, note_suspend)
    cards_info = anki_request("cardsInfo", {"cards": card_ids}, url=ANKI_URL) or []
    to_suspend = []
    to_unsuspend = []
    changed = []
    for idx, card_id in enumerate(card_ids):
        should_be_suspended = targets[idx] if idx < len(targets) else note_suspend
        was_suspended = cards_info[idx].get("queue") == -1 if idx < len(cards_info) else None
        (to_suspend if should_be_suspended else to_unsuspend).append(card_id)
        if was_suspended is not None and was_suspended != should_be_suspended and idx < len(CARD_FIELD_CATEGORIES):
            name = CARD_FIELD_CATEGORIES[idx][0]
            changed.append(f"{name} -> {'suspended' if should_be_suspended else 'unsuspended'}")
    if to_suspend:
        anki_request("suspend", {"cards": to_suspend}, url=ANKI_URL)
    if to_unsuspend:
        anki_request("unsuspend", {"cards": to_unsuspend}, url=ANKI_URL)
    if changed:
        lemma = fields.get("Lemma", "")
        print(f"    {lemma}: {', '.join(changed)}")


# ---------------------------------------------------------------------------
# CNSF parsing
# ---------------------------------------------------------------------------


def parse_note_file(path: Path) -> dict | None:
    """Parse a CNSF .md file and return its frontmatter as a dict."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        print(f"  SKIP {path.name}: no frontmatter")
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"  SKIP {path.name}: malformed frontmatter")
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"  SKIP {path.name}: YAML error — {e}")
        return None


# ---------------------------------------------------------------------------
# Import logic
# ---------------------------------------------------------------------------


def should_suspend(tags: list[str]) -> bool:
    """Suspension policy for UA_Verb cards (see module docstring):
        - status:draft OR release:pending     → suspend (inactive/not released)
        - status:verified AND release:active  → unsuspend, ready for drilling

    The conj:drill/conj:suspended curation axis was removed 2026-08-27 (per
    Craig): all verified verbs are meant to be actively drillable, not just a
    hand-picked set of class leaders, since class leaders will keep arriving
    gradually as earlier chapters are backfilled into the corpus.

    release: added 2026-08-29 (per Craig) as a second, independent gate --
    status tracks content-quality/review state; release tracks study-pacing
    (whether this note has been let into rotation yet). Both axes must clear
    for a note to be active; either one suspends.
    """
    return not (("status:verified" in tags) and ("release:active" in tags))


def import_note(data: dict, dry_run: bool, flagged_note_ids: set | None = None) -> str:
    """Import a single parsed note. Returns 'added', 'updated', or 'skipped'.

    flagged_note_ids: Anki note IDs with a red-flagged card (orange is a
    call-out only, not a suspend reason -- see main()), from
    get_flagged_note_ids_by_color()[FLAG_RED] -- see module docstring's
    suspension policy.
    """
    flagged_note_ids = flagged_note_ids or set()
    note_id = data.get("note_id", "")
    if not note_id:
        return "skipped"

    raw_fields = data.get("fields", {})
    if not raw_fields:
        return "skipped"

    # Coerce all field values to strings (YAML may parse numbers/booleans)
    fields = {k: ("" if v is None else str(v)) for k, v in raw_fields.items()}

    # Tags: from CNSF frontmatter
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    suspend = should_suspend(tags)

    existing_id = find_note_by_id(note_id)

    if existing_id is None:
        anki_id = add_note(fields, tags, dry_run)
        if anki_id and not dry_run:
            sync_card_suspension(anki_id, fields, suspend, dry_run)
        return "added"
    else:
        # Red-flag override -- see module docstring. Only meaningful here
        # (existing-note path); a note can't have a flagged card in Anki
        # before this sync creates it. Orange never reaches flagged_note_ids
        # -- main() only puts FLAG_RED note ids in it.
        note_suspend = suspend or (existing_id in flagged_note_ids)
        update_note(existing_id, fields, tags, dry_run)
        if not dry_run:
            sync_card_suspension(existing_id, fields, note_suspend, dry_run)
        return "updated"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def collect_files(targets: list[str]) -> list[Path]:
    files = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            files.extend(sorted(p.glob("ua-verb-*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: {t} is not a file or directory — skipping")
    return files


def main():
    parser = argparse.ArgumentParser(description="Import ua_verb notes into Anki.")
    parser.add_argument("targets", nargs="+", help="Files or directories to import")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; touch nothing")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no changes will be made to Anki.\n")

    ensure_deck(DECK_NAME, args.dry_run)

    files = collect_files(args.targets)
    if not files:
        print("No ua-verb-*.md files found.")
        sys.exit(1)

    # One bulk query for the whole sync run -- see get_flagged_note_ids_by_color.
    # Red still forces suspension; orange is a call-out only (2026-08-10, per
    # Craig -- see SUSPEND_FLAG_COLORS in tsv_to_anki.py).
    flags_by_color = get_flagged_note_ids_by_color(FLAG_DECK_QUERY, ANKI_URL)
    flagged_note_ids = flags_by_color[FLAG_RED]
    if flagged_note_ids:
        print(f"Found {len(flagged_note_ids)} note(s) with a red-flagged card -- keeping suspended.\n")
    orange_flagged_note_ids = flags_by_color[FLAG_ORANGE]
    if orange_flagged_note_ids:
        print(f"⚠ {len(orange_flagged_note_ids)} note(s) have an orange-flagged card "
              f"(confusing/unclear) -- NOT suspended, flagged for review:")
        for label in describe_note_ids(orange_flagged_note_ids, ANKI_URL):
            print(f"    {label}")
        print()

    added = updated = skipped = errors = 0

    for f in files:
        data = parse_note_file(f)
        if data is None:
            skipped += 1
            continue
        try:
            result = import_note(data, args.dry_run, flagged_note_ids)
            note_id = data.get("note_id", f.name)
            lemma = (data.get("fields") or {}).get("Lemma", "")
            label = f"{note_id}  {lemma}"
            if result == "added":
                print(f"  ADD     {label}")
                added += 1
            elif result == "updated":
                print(f"  UPDATE  {label}")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR   {f.name}: {e}")
            errors += 1

    print(f"\nDone: {added} added, {updated} updated, {skipped} skipped, {errors} errors.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
