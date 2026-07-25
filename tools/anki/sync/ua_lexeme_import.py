#!/usr/bin/env python3
"""Import ua_lexeme CNSF notes into Anki via AnkiConnect.

Upsert logic: adds new notes, updates fields on existing notes (matched by NoteID).
Run rename_ua_legacy.py first to move legacy cards out of the UA:: namespace.

Deck layout:
    UA::Recognition::UA→EN    ← UA→EN recognition card
    UA::Production::EN→UA     ← EN→UA typing card

Suspension policy (applied on every import, add or update -- declarative and
self-healing, so a re-import always converges to this state regardless of
prior manual suspend/unsuspend actions taken outside this script):
    - status:draft    → suspend every card on the note
    - status:verified → unsuspend every card on the note

(2026-07-22: this previously also suspended just the EN→UA card for
motion:prefixed + status:verified notes, on the theory that PVOM's
UA_PVOM_Infinitive templates already drill EN→UA production for these verbs.
Dropped -- in practice the EN→UA cards were not ending up suspended in Anki,
and Craig is fine with both directions staying active. See project memory
for the fuller discussion.)

Usage (with Anki open + AnkiConnect running):
    # Dry run — show what would be added/updated, touch nothing
    python tools/anki/sync/ua_lexeme_import.py --dry-run domains/ua/anki/notes/lexemes/yabluko-l1/vstup/

    # Import a single file
    python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/vstup/ua-lexeme-0001.md

    # Import a whole directory
    python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/vstup/

    # Hard-delete Anki notes whose CNSF file was removed (2026-07-25, opt-in,
    # irreversible -- preview with --dry-run first)
    python tools/anki/sync/ua_lexeme_import.py --dry-run --prune-orphans domains/ua/anki/notes/lexemes/
    python tools/anki/sync/ua_lexeme_import.py --prune-orphans domains/ua/anki/notes/lexemes/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402
from tools.anki.lib.lexeme_dedup import strip_stress  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

# Full CNSF root, independent of whatever `targets` a given invocation passes
# (e.g. a single file or one subdirectory) -- orphan detection (--prune-orphans,
# added 2026-07-25) must always compare against every note_id that exists
# ANYWHERE in the corpus, not just the files this particular run touched, or
# it would falsely flag every note outside `targets` as orphaned and delete it.
LEXEME_ROOT = Path(__file__).resolve().parents[3] / "domains/ua/anki/notes/lexemes"

DECK_RECOGNITION = "UA::Recognition::UA→EN"
DECK_PRODUCTION  = "UA::Production::EN→UA"

# Cards that go to the production deck (by template name).
# All others land in the recognition deck.
PRODUCTION_TEMPLATES = {"EN→UA"}


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
                "deckName": DECK_RECOGNITION,
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


def route_cards_to_decks(anki_note_id: int, dry_run: bool):
    """Move each card to its canonical deck based on template name.

    EN→UA cards → DECK_PRODUCTION
    All other cards (UA→EN, Compare) → DECK_RECOGNITION

    Matched per template via Anki's own `card:"Name"` search filter, not a
    cardsInfo field lookup -- card.get("cardType") was silently never
    matching (empty/wrong field name), so every card including EN→UA was
    landing in DECK_RECOGNITION regardless of template. Found + fixed
    2026-07-22.
    """
    if dry_run:
        return
    for template_name in PRODUCTION_TEMPLATES:
        prod_ids = anki_request(
            "findCards", {"query": f'nid:{anki_note_id} "card:{template_name}"'}, url=ANKI_URL
        )
        if prod_ids:
            anki_request("changeDeck", {"cards": prod_ids, "deck": DECK_PRODUCTION}, url=ANKI_URL)

    prod_query = " OR ".join(f'"card:{t}"' for t in PRODUCTION_TEMPLATES)
    non_prod_ids = anki_request("findCards", {"query": f"nid:{anki_note_id} -({prod_query})"}, url=ANKI_URL) or []
    if non_prod_ids:
        anki_request("changeDeck", {"cards": non_prod_ids, "deck": DECK_RECOGNITION}, url=ANKI_URL)


def set_suspended(anki_note_id: int, suspend: bool, dry_run: bool):
    if dry_run:
        return
    card_ids = anki_request("findCards", {"query": f"nid:{anki_note_id}"}, url=ANKI_URL)
    if not card_ids:
        return
    action = "suspend" if suspend else "unsuspend"
    anki_request(action, {"cards": card_ids}, url=ANKI_URL)


def all_anki_note_ids() -> dict[str, int]:
    """Map every live UA_Lexeme note's NoteID field -> Anki note id.

    Used by --prune-orphans to find Anki notes whose CNSF source file has
    been deleted (hard-delete decision, 2026-07-25 -- see Verification
    Notes/CLAUDE.md: reusing a note_id slot for unrelated new content must
    NOT inherit a stale note's FSRS scheduling/review history, which a
    suspend-only approach would silently do via updateNoteFields).
    """
    ids = anki_request("findNotes", {"query": f'note:"{MODEL_NAME}"'}, url=ANKI_URL) or []
    if not ids:
        return {}
    infos = anki_request("notesInfo", {"notes": ids}, url=ANKI_URL) or []
    result = {}
    for info in infos:
        note_id_field = (info.get("fields", {}).get("NoteID", {}) or {}).get("value", "")
        if note_id_field:
            result[note_id_field] = info["noteId"]
    return result


def delete_notes(anki_note_ids: list[int], dry_run: bool):
    if dry_run or not anki_note_ids:
        return
    anki_request("deleteNotes", {"notes": anki_note_ids}, url=ANKI_URL)


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


def compute_typing_target(
    lemma: str, impf_uni: str, perfective: str,
    lemma_euphony: str = "", impf_uni_euphony: str = "", perfective_euphony: str = "",
) -> dict[str, tuple[str, str]] | None:
    """Build the EN->UA typing target(s) for a verb's aspect set, with euphony
    pairing nested in per redesign 2026-07-25.

    Base behavior (added 2026-07-27): for verb notes, the EN->UA card requires
    typing the entire aspect singlet/couplet/triplet, not just Lemma alone --
    e.g. "ходи́ти / йти / піти́" (multidirectional-imperfective / unidirectional-
    imperfective / perfective triplet) or "перекида́ти / переки́нути" (imperfective/
    perfective doublet). Order is always Lemma, then ImperfectiveUnidirectional (if
    populated), then Perfective (if populated). Any missing slot is dropped, not
    left blank, so a doublet renders as "Lemma / Perfective", never
    "Lemma / / Perfective".

    Euphony (redesigned 2026-07-25, see CLAUDE.md "Lemma_Euphony / aspect+euphony
    recognition testing"): each slot may carry its own stressed euphonic
    alternate (e.g. Lemma_Euphony). A populated alternate makes that slot's FULL
    unit "primary ; euphonic" instead of just "primary" -- e.g.
    "учи́ти ; вчи́ти / ви́вчити" (euphony only on the imperfective slot). Three
    variants are computed and returned:
      - "full":  every slot as "primary ; euphonic" where it has one, else
                 just "primary" -- the target for full/PERFECT credit.
      - "base":  every slot as "primary" only, regardless of euphony -- the
                 pre-redesign join, kept for PARTIAL-credit grading.
      - "alt":   every slot as its euphonic form where it has one, else
                 "primary" -- the other PARTIAL-credit variant. Empty string
                 pair when no slot has any euphony at all (nothing to offer).

    Returns None when there's nothing to compute at all: fewer than two aspect
    slots populated AND no euphony on the sole slot (a plain non-verb note, or
    an aspectless/imperfectiva-tantum verb with no euphonic variant either) --
    callers should leave TypingTarget_UA/TypingAnswer as Lemma-only in that
    case, same behavior as before this feature existed.

    Computed here (at sync time) rather than hand-authored into a new CNSF
    field, by design: Lemma/ImperfectiveUnidirectional/Perfective/*_Euphony are
    already the authored source of truth, and deriving the join avoids a
    second, independently-authored field silently drifting out of sync with --
    or being clobbered relative to -- the fields it's derived from.
    """
    slots = [
        (lemma, lemma_euphony),
        (impf_uni, impf_uni_euphony),
        (perfective, perfective_euphony),
    ]
    populated = [(primary, euphony) for primary, euphony in slots if primary]
    has_any_euphony = any(euphony for _, euphony in populated)

    if len(populated) < 2 and not has_any_euphony:
        return None

    full_stressed = " / ".join(
        f"{primary} ; {euphony}" if euphony else primary for primary, euphony in populated
    )
    base_stressed = " / ".join(primary for primary, _ in populated)

    result = {
        "full": (full_stressed, strip_stress(full_stressed)),
        "base": (base_stressed, strip_stress(base_stressed)),
        "alt": ("", ""),
    }
    if has_any_euphony:
        alt_stressed = " / ".join(euphony or primary for primary, euphony in populated)
        result["alt"] = (alt_stressed, strip_stress(alt_stressed))
    return result


def import_note(data: dict, dry_run: bool) -> str:
    """Import a single parsed note. Returns 'added', 'updated', or 'skipped'."""
    note_id = data.get("note_id", "")
    if not note_id:
        return "skipped"

    raw_fields = data.get("fields", {})
    if not raw_fields:
        return "skipped"

    # Coerce all field values to strings (YAML may parse numbers/booleans)
    fields = {k: ("" if v is None else str(v)) for k, v in raw_fields.items()}

    # EN->UA typing target: full stressed aspect join (with euphony nested per
    # slot, see compute_typing_target docstring) for verbs with a populated
    # counterpart or any euphony; Lemma alone otherwise.
    typing_target = compute_typing_target(
        fields.get("Lemma", ""),
        fields.get("ImperfectiveUnidirectional", ""),
        fields.get("Perfective", ""),
        fields.get("Lemma_Euphony", ""),
        fields.get("ImperfectiveUnidirectional_Euphony", ""),
        fields.get("Perfective_Euphony", ""),
    )
    if typing_target:
        fields["TypingTarget_UA"], fields["TypingAnswer"] = typing_target["full"]
        fields["TypingTarget_UA_Base"], fields["TypingAnswer_Base"] = typing_target["base"]
        fields["TypingTarget_UA_AltOnly"], fields["TypingAnswer_AltOnly"] = typing_target["alt"]
    else:
        fields["TypingTarget_UA"] = fields.get("Lemma", "")
        fields["TypingTarget_UA_Base"] = ""
        fields["TypingAnswer_Base"] = ""
        fields["TypingTarget_UA_AltOnly"] = ""
        fields["TypingAnswer_AltOnly"] = ""
        # TypingAnswer left as authored in the CNSF file for singlets.

    # NOTE (2026-07-27 bug fix): this function used to overwrite fields["CompareA"]
    # / fields["CompareB"] here with a parity-based swap of (Lemma, raw ConfusableSet
    # text) -- leftover from the original Compare-card design where the whole
    # ConfusableSet paragraph was one of the two options shown. The 2026-07-24
    # CompareScenario/CompareA-D redesign replaced that with hand-authored short-word
    # chips written directly into each note's CNSF fields, but this override was never
    # removed, so every sync silently clobbered the authored CompareA/CompareB (and, for
    # even note IDs, always CompareB; for odd, always CompareA) with the full
    # ConfusableSet text. Found via Craig reviewing rendered cards (0058/0101/0145) where
    # one chip showed the whole ConfusableSet paragraph instead of a short distractor --
    # the even/odd note-ID pattern matched exactly. Removed: CompareA/B/C/D now just pass
    # through from raw_fields like every other authored field, which is what the
    # redesigned template expects.

    # Tags: from CNSF frontmatter
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    # Suspension policy -- see module docstring.
    suspend = "status:draft" in tags

    existing_id = find_note_by_id(note_id)

    if existing_id is None:
        anki_id = add_note(fields, tags, dry_run)
        if anki_id and not dry_run:
            route_cards_to_decks(anki_id, dry_run)
            if suspend:
                set_suspended(anki_id, True, dry_run)
        return "added"
    else:
        update_note(existing_id, fields, tags, dry_run)
        if not dry_run:
            route_cards_to_decks(existing_id, dry_run)
            set_suspended(existing_id, suspend, dry_run)
        return "updated"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def collect_files(targets: list[str]) -> list[Path]:
    files = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            files.extend(sorted(p.rglob("ua-lexeme-*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: {t} is not a file or directory — skipping")
    return files


def collect_all_corpus_note_ids() -> tuple[set[str], list[Path]]:
    """Every note_id in the full CNSF corpus, regardless of this run's `targets`,
    plus the list of files that failed to parse.

    Deliberately walks LEXEME_ROOT rather than args.targets -- see the
    LEXEME_ROOT comment above. Returns failures explicitly rather than
    silently skipping them (parse_note_file() already prints a SKIP line and
    returns None) -- a single unparseable file must never be treated as "this
    note_id doesn't exist," since that would make prune_orphans() delete a
    perfectly live Anki note over what might be a one-line YAML typo.
    """
    note_ids = set()
    failed = []
    for path in LEXEME_ROOT.rglob("ua-lexeme-*.md"):
        data = parse_note_file(path)
        if data is None:
            failed.append(path)
            continue
        note_id = data.get("note_id", "")
        if note_id:
            note_ids.add(note_id)
        else:
            failed.append(path)
    return note_ids, failed


def prune_orphans(dry_run: bool, sync_errors: int) -> int:
    """Hard-delete Anki notes whose CNSF source file no longer exists.

    2026-07-25, Craig: hard delete, not suspend -- if a retired note_id slot
    gets reused for unrelated new content later, find_note_by_id() would
    match the orphan by NoteID field and updateNoteFields() would silently
    inherit its old FSRS scheduling/review history onto the new, unrelated
    note. Hard-deleting means the next sync's find_note_by_id() finds
    nothing and add_note() creates a fresh note with clean scheduling
    instead, which is what a genuinely new/different note should get.

    Safety gate (2026-07-25, Craig): refuses to prune at all unless this
    run's own add/update pass was clean (sync_errors == 0) AND the full
    corpus parses cleanly (no failed files from collect_all_corpus_note_ids).
    A minor YAML slip in even one unrelated file must not be able to wipe
    another note's FSRS history -- fail loud and prune nothing instead.
    """
    if sync_errors:
        print(f"  PRUNE   aborted: {sync_errors} error(s) in this run's own sync pass -- fix those first.")
        return 0

    corpus_ids, failed = collect_all_corpus_note_ids()
    if failed:
        print(f"  PRUNE   aborted: {len(failed)} file(s) in the corpus failed to parse -- fix those first:")
        for path in failed:
            print(f"            {path}")
        return 0

    anki_ids = all_anki_note_ids()
    orphan_note_ids = sorted(set(anki_ids) - corpus_ids)
    if not orphan_note_ids:
        return 0
    label = "Would delete" if dry_run else "Deleting"
    for note_id in orphan_note_ids:
        print(f"  PRUNE   {label.lower()} {note_id} (no matching CNSF file)")
    delete_notes([anki_ids[nid] for nid in orphan_note_ids], dry_run)
    return len(orphan_note_ids)


def main():
    parser = argparse.ArgumentParser(description="Import ua_lexeme notes into Anki.")
    parser.add_argument("targets", nargs="+", help="Files or directories to import")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; touch nothing")
    parser.add_argument(
        "--prune-orphans",
        action="store_true",
        help=(
            "Hard-delete Anki notes whose CNSF source file no longer exists anywhere in the "
            "corpus. Off by default -- irreversible (loses FSRS/review history), opt in "
            "explicitly. Combine with --dry-run to preview first."
        ),
    )
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no changes will be made to Anki.\n")

    ensure_deck(DECK_RECOGNITION, args.dry_run)
    ensure_deck(DECK_PRODUCTION, args.dry_run)

    files = collect_files(args.targets)
    if not files:
        print("No ua-lexeme-*.md files found.")
        sys.exit(1)

    added = updated = skipped = errors = 0

    for f in files:
        data = parse_note_file(f)
        if data is None:
            skipped += 1
            continue
        try:
            result = import_note(data, args.dry_run)
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

    pruned = 0
    if args.prune_orphans:
        pruned = prune_orphans(args.dry_run, errors)

    summary = f"\nDone: {added} added, {updated} updated, {skipped} skipped, {errors} errors"
    if args.prune_orphans:
        summary += f", {pruned} pruned"
    print(summary + ".")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
