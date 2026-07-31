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
    - ConfusableSet empty/blank → suspend the Compare card (card #3)
    - ConfusableSet populated   → unsuspend the Compare card (card #3)

The Compare card suspension is independent of status flags -- a status:verified
note with no ConfusableSet will have all other cards active but the Compare card
suspended. This prevents blank Compare cards from appearing in study.

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
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

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


def set_compare_card_suspended(anki_note_id: int, suspend: bool, dry_run: bool):
    """Conditionally suspend/unsuspend just the Compare card (card #3) by template name.

    Called after status-based suspension to enforce Compare-card-specific logic:
    - Compare card should be suspended if ConfusableSet is empty (no confusables/homographs)
    - Compare card should be unsuspended if ConfusableSet is populated (has data to test)

    This prevents blank Compare cards from appearing in study while keeping other cards
    (UA→EN recognition, EN→UA production) active regardless of ConfusableSet status.
    """
    if dry_run:
        return
    compare_ids = anki_request(
        "findCards", {"query": f'nid:{anki_note_id} "card:Compare"'}, url=ANKI_URL
    ) or []
    if not compare_ids:
        return
    action = "suspend" if suspend else "unsuspend"
    anki_request(action, {"cards": compare_ids}, url=ANKI_URL)


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


def strip_stress(s: str) -> str:
    """Remove the combining acute accent (U+0301) used for stress marks."""
    return s.replace("́", "")


def compute_typing_target(lemma: str, impf_uni: str, perfective: str) -> tuple[str, str] | None:
    """Build the EN->UA typing target for a verb's full stressed aspect set.

    Restored 2026-07-28 (git archaeology, commit a5b4a15 -- the last version
    before the 2026-07-25 Lemma_Euphony redesign made this require typing
    both a primary and euphonic form together; see setup_ua_note_types.py's
    EN_UA_FRONT/EN_UA_BACK for the template side of this restoration).

    For verb notes, the EN->UA card should require typing the entire aspect
    singlet/couplet/triplet, not just Lemma alone -- e.g. "ходи́ти / йти /
    піти́" (multidirectional-imperfective / unidirectional-imperfective /
    perfective triplet) or "перекида́ти / переки́нути" (imperfective/perfective
    doublet). Order is always Lemma, then ImperfectiveUnidirectional (if
    populated), then Perfective (if populated) -- matching the multi-imp ->
    uni-imp -> perfective progression. Any missing slot is dropped, not left
    blank, so a doublet renders as "Lemma / Perfective", never
    "Lemma / / Perfective".

    Returns None when fewer than two forms are populated (a plain singlet,
    e.g. an imperfective-only verb like мати with no aspectual counterpart,
    or any non-verb note where Perfective/ImperfectiveUnidirectional are
    simply not applicable) -- callers should leave TypingTarget_UA/
    TypingAnswer as Lemma-only in that case.

    Computed here (at sync time) rather than hand-authored into a new CNSF
    field, by design: Lemma/ImperfectiveUnidirectional/Perfective are already
    the authored source of truth, and deriving the join avoids a second,
    independently-authored field silently drifting out of sync with -- or
    being clobbered relative to -- the fields it's derived from.
    """
    parts = [p for p in (lemma, impf_uni, perfective) if p]
    if len(parts) < 2:
        return None
    stressed = " / ".join(parts)
    unstressed = " / ".join(strip_stress(p) for p in parts)
    return stressed, unstressed


def compute_compare_options(note_id: str, lemma: str, confusable: str) -> tuple[str, str]:
    """Decide display order for the Compare card's "X or Y?" prompt.

    Deterministically varies which word -- this note's own Lemma vs its
    ConfusableSet alternative -- appears first (CompareA) vs second
    (CompareB), based on the note ID's parity. Without this, the Compare
    template always named Lemma explicitly in the prompt text ("...or the
    alternative?"), which gave away the correct answer every time. Per
    Craig 2026-07-22: phrase it as "<a> or <b>?" with both real words shown,
    order varied by even/odd ID so the wording itself can't be gamed.
    """
    if not confusable:
        return "", ""
    digits = "".join(ch for ch in note_id if ch.isdigit())
    num = int(digits) if digits else 0
    if num % 2 == 0:
        return lemma, confusable
    return confusable, lemma


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

    # Tags: from CNSF frontmatter (needed before Compare card logic)
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    # Populate _IsHomograph field based on homograph:true tag.
    # Used by Compare card template to decide UA→EN (homographs) vs EN→UA (confusables) mode.
    is_homograph = "homograph:true" in tags
    fields["_IsHomograph"] = "1" if is_homograph else ""

    # EN->UA typing target: full stressed aspect join for verbs with a
    # populated counterpart (see compute_typing_target docstring); Lemma
    # alone otherwise. Restored 2026-07-28 (git archaeology, commit a5b4a15).
    typing_target = compute_typing_target(
        fields.get("Lemma", ""),
        fields.get("ImperfectiveUnidirectional", ""),
        fields.get("Perfective", ""),
    )
    if typing_target:
        fields["TypingTarget_UA"] = typing_target[0]
        fields["TypingAnswer"] = typing_target[1]
    else:
        fields["TypingTarget_UA"] = fields.get("Lemma", "")
        # TypingAnswer left as authored in the CNSF file for singlets.

    # UA->EN front aspect label: for a verb note that's a true singlet (no
    # ImperfectiveUnidirectional, no Perfective -- so TypingTarget_UA above is
    # just Lemma alone), show a small "(pf.)"/"(impf.)" tag next to the word
    # on the Recognition card front. Doublets/triplets never get a label --
    # the slash-joined TypingTarget_UA already shows the aspectual range, so
    # a tag would be redundant there. Per Craig 2026-07-31.
    #
    # Aspect of a bare singlet is derived the same way compute_typing_target's
    # docstring and the "Aspect convention" section of CLAUDE.md already
    # define it, not re-decided here: Lemma is imperfective by schema
    # convention UNLESS the note is tagged aspect:perfective-only (the
    # perfectiva tantum exception, in which case Lemma holds the perfective
    # form instead). This does not require the tag to exist to label a verb
    # "(impf.)" -- only "(pf.)" requires the explicit tag, since imperfective
    # is the schema's default and untagged singlets (most of the corpus,
    # since aspect:*-only tags are hand-applied by Craig only after checking
    # Горох) are still correctly "(impf.)" by that same convention.
    is_verb = fields.get("PartOfSpeech", "").strip().lower() == "verb"
    is_singlet = not fields.get("ImperfectiveUnidirectional", "").strip() and not fields.get(
        "Perfective", ""
    ).strip()
    if is_verb and is_singlet:
        fields["_AspectLabel"] = "(pf.)" if "aspect:perfective-only" in tags else "(impf.)"
    else:
        fields["_AspectLabel"] = ""

    # Compare card prompt: vary which word (Lemma vs ConfusableSet) is named first
    # (confusables only). For homographs, CompareA/B are authored Ukrainian sentences
    # that shouldn't be reordered -- use them as-is from the YAML.
    #
    # Only auto-derive when the note hasn't been hand-authored with explicit
    # CompareA/CompareB values. Found 2026-07-28 (ua-lexeme-0022/0023,
    # алфавіт/абетка): this used to run unconditionally, so it silently
    # overwrote authored short chip labels (e.g. CompareA: абетка / CompareB:
    # алфавіт) with (Lemma, raw ConfusableSet text) on every re-import.
    # ConfusableSet holds long discriminator prose, not a short alternate
    # word -- once the 2026-07-24 CompareScenario/CompareA/CompareB redesign
    # landed, treating it as the "confusable" arg here meant the full
    # explanation (which names the other word) ended up rendered as a front-
    # side chip via {{CompareB}}, leaking the answer. compute_compare_options
    # is now only a fallback for notes that predate that redesign and have
    # never had CompareA/CompareB authored.
    already_authored = fields.get("CompareA", "").strip() and fields.get("CompareB", "").strip()
    if not is_homograph and not already_authored:
        compare_a, compare_b = compute_compare_options(
            note_id, fields.get("Lemma", ""), fields.get("ConfusableSet", "")
        )
        fields["CompareA"] = compare_a
        fields["CompareB"] = compare_b

    # Suspension policy -- see module docstring.
    suspend = "status:draft" in tags

    # Compare card suspension: suspend if ConfusableSet is empty (no confusables/
    # homographs), OR if it's populated but CompareA never got authored --
    # CompareA is "always required" by the Compare template's own design
    # (CompareB/C/D optional; see comment above CARD_TEMPLATES in
    # setup_ua_note_types.py), so a blank CompareA here means the actual
    # chip content is missing even though ConfusableSet has text (e.g. a
    # homograph:true note where CompareA/B were never authored -- those
    # aren't auto-derived above, unlike the confusables case). Without this,
    # such a note would generate an active Compare card whose front shows
    # the scenario prompt with no answer chips. Found 2026-07-28 alongside
    # the CompareA/CompareB clobbering bug; the template itself now also
    # shows a "should be suspended" notice in this state as a defensive
    # fallback, but suspending here is the primary safeguard so it's never
    # actually seen in study.
    confusable_set = fields.get("ConfusableSet", "").strip()
    compare_a_content = fields.get("CompareA", "").strip()
    suspend_compare_card = not confusable_set or not compare_a_content

    existing_id = find_note_by_id(note_id)

    if existing_id is None:
        anki_id = add_note(fields, tags, dry_run)
        if anki_id and not dry_run:
            route_cards_to_decks(anki_id, dry_run)
            if suspend:
                set_suspended(anki_id, True, dry_run)
            set_compare_card_suspended(anki_id, suspend_compare_card, dry_run)
        return "added"
    else:
        update_note(existing_id, fields, tags, dry_run)
        if not dry_run:
            route_cards_to_decks(existing_id, dry_run)
            set_suspended(existing_id, suspend, dry_run)
            set_compare_card_suspended(existing_id, suspend_compare_card, dry_run)
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


def main():
    parser = argparse.ArgumentParser(description="Import ua_lexeme notes into Anki.")
    parser.add_argument("targets", nargs="+", help="Files or directories to import")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; touch nothing")
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

    print(f"\nDone: {added} added, {updated} updated, {skipped} skipped, {errors} errors.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
