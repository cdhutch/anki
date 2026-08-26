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
    - note has a red-flagged card (any card) → suspend every card on the
      note, including the Compare card (added 2026-07-31, per Craig -- see
      get_flagged_note_ids_by_color in tsv_to_anki.py). Only checked for
      existing notes; a brand-new note can't already have a flagged card in
      Anki.
    - note has an orange-flagged card, no red → NOT suspended. Called out in
      the sync log instead (2026-08-10, per Craig: orange means "confusing/
      unclear", not "wrong" -- see CLAUDE-flag-audit.md -- so it shouldn't
      silently pull the card out of review the way red does).

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
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from typing import List  # noqa: E402

from tools.anki.lib.typing_target import (  # noqa: E402,F401
    compute_typing_target,
    strip_stress,
)
from tools.anki.lib.confusable_clusters import ClusterRegistry  # noqa: E402,F401
from tools.anki.sync.tsv_to_anki import (  # noqa: E402
    FLAG_ORANGE,
    FLAG_RED,
    anki_request,
    describe_note_ids,
    flag_query_for_model,
    get_flagged_note_ids_by_color,
)

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

# Flag-query scope for the red/orange-flag check. Scoped to THIS note type
# as of 2026-08-20 -- it used to be the bare UA deck tree, which made every
# import print the whole corpus's orange call-out. See flag_query_for_model()
# in tsv_to_anki.py for the symptom and the reasoning.
FLAG_DECK_QUERY = flag_query_for_model(MODEL_NAME)

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


# strip_stress() and compute_typing_target() moved to tools/anki/lib/
# typing_target.py on 2026-08-20 and are re-exported here, unchanged, so every
# existing caller and test keeps working. They moved because
# cnsf_canonicalize.py needs the same join to keep CNSF's authored
# `TypingAnswer` from drifting away from what import_note() actually sends --
# and it runs under a pre-commit hook whose venv declares only pyyaml, so it
# cannot safely import this module. See typing_target.py's docstring.


def compute_typing_spec(
    lemma: str,
    impf_uni: str,
    perfective: str,
    lemma_euphony: str,
    impf_uni_euphony: str,
    perfective_euphony: str,
) -> str:
    """Build `_TypingSpec` -- the structured grading input for EN_UA_BACK.

    Added 2026-08-19, replacing `_EuphonySlots` (Option B of
    docs/ua-en-ua-euphony-aspect-refactor.md; decisions in its section 7).

    Emits compact JSON, one object per POPULATED aspect slot, in the same
    Lemma -> ImperfectiveUnidirectional -> Perfective order every other
    computed field uses:

        {"slots":[{"primary":"вхо́дити","alts":["ухо́дити"]},
                  {"primary":"ввійти́","alts":["увійти́"]}]}

    **Why this replaces `_EuphonySlots`.** That field was a `" / "`-joined
    string that had to stay index-aligned with `TypingTarget_UA`'s own
    `" / "` join, by convention, with nothing enforcing it and nothing able
    to detect a break. The JS then had to reconstruct the slot structure by
    splitting both strings and trusting the positions to correspond. Here the
    slot IS the unit: primary and alternates travel together, so the entire
    class of alignment bugs stops being possible rather than being avoided.

    **Why it carries STRESSED alternates.** The old mechanism stress-stripped
    the stored alternates AND the typed answer before comparing, so it could
    not distinguish "euphonic alternate, perfectly stressed" from "euphonic
    alternate, no stress at all" -- both landed in CORRECT, and a fully
    correct dictionary-attested answer could never reach PERFECT. That was
    the bug this refactor exists to fix (Craig's decision: a fully-stressed
    euphonic alternate DOES earn PERFECT). Values are emitted exactly as
    authored, stress intact; the JS derives the unstressed form by stripping,
    which is why there is deliberately no `*_Euphony_Typing` field to store a
    second copy that could drift (see the *_Euphony authoring convention in
    CLAUDE.md).

    A slot with no alternate emits `"alts":[]` rather than being omitted --
    slot count must match `TypingTarget_UA`'s, since the JS still splits the
    typed answer on the separator to know which slot each answer belongs to.

    The legacy whole-note `EuphonyNote` fallback that `compute_euphony_slots()`
    carried is deliberately NOT reproduced here. An audit on 2026-08-19 found
    exactly ONE note reaching it corpus-wide (ua-lexeme-0353, вве́чері), and
    its `EuphonyNote` was explanatory prose rather than a bare alternate --
    so the fallback was producing silent dead tolerance: prose compared as a
    spelling, matching nothing, warning about nothing. 0353 was given a
    proper `Lemma_Euphony` in the same commit, leaving the fallback with zero
    users. Authored euphony belongs in a `*_Euphony` field; `EuphonyNote` is
    prose for humans.

    Returns "" when no slot has an alternate -- the grading script treats a
    missing/empty spec as "no euphony on this note" and uses its plain
    whole-string comparison, so blank costs nothing and keeps the field out
    of the way on the ~577 notes with no euphony data at all.
    """
    slots = [
        (lemma, lemma_euphony),
        (impf_uni, impf_uni_euphony),
        (perfective, perfective_euphony),
    ]
    populated = [(base, alt) for base, alt in slots if base]
    if not populated or not any(alt for _, alt in populated):
        return ""

    spec = {
        "slots": [
            {
                "primary": base,
                # '|'-delimited within a slot, matching how *_Euphony fields
                # have always been authored for multiple alternates.
                "alts": [a.strip() for a in alt.split("|") if a.strip()],
            }
            for base, alt in populated
        ]
    }
    # Compact separators: this lands in an Anki field and is re-parsed by the
    # card template, so bytes matter more than readability.
    return json.dumps(spec, ensure_ascii=False, separators=(",", ":"))


def compute_ua_en_display(
    lemma: str,
    impf_uni: str,
    perfective: str,
    lemma_euphony: str,
    impf_uni_euphony: str,
    perfective_euphony: str,
) -> str:
    """Build _UA_EN_DisplayLemma for the UA->EN Recognition card front
    (added 2026-08-04, CLAUDE.md "UA->EN lexeme verb cards -- show multiple
    aspects per euphonic slot").

    Same populated-slot join as compute_typing_target() (Lemma, then
    ImperfectiveUnidirectional, then Perfective, each only if populated), but
    each slot's own *_Euphony alternate -- if that specific slot has one --
    is shown inline in parentheses, e.g. "ввійти́ (увійти́)". Deliberately
    kept separate from TypingTarget_UA/compute_typing_target(): that field
    must stay a pure, exact-match typing target for the EN->UA card's
    {{type:...}}, so it can never grow parentheticals. When no slot has a
    euphonic alternate, this renders identically to TypingTarget_UA's own
    stressed join -- i.e. no visible change on notes without per-slot
    euphony data.
    """
    slots = [
        (lemma, lemma_euphony),
        (impf_uni, impf_uni_euphony),
        (perfective, perfective_euphony),
    ]
    parts = []
    for base, alt in slots:
        if not base:
            continue
        parts.append(f"{base} ({alt})" if alt else base)
    return " / ".join(parts)


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


def get_cluster_compare_members_json(note_id: str, tags: List[str]) -> str:
    """Serialize cluster scenario + members to JSON for Compare card rendering.

    Returns JSON string of {"scenario": ..., "members": [...]} if note is a
    cluster member, empty string otherwise. Only includes sourced (active)
    members. The scenario comes from this note's own compare_scenario field
    in the registry (Phase 6: confusable_clusters.yaml is now 100% backfilled
    with compare_scenario per member, so CompareScenario no longer needs to
    be hand-authored per CNSF note).

    Args:
        note_id: The note's ID (e.g., 'ua-lexeme-0467')
        tags: List of tags from the note (used only for _IsHomograph flag)

    Returns:
        JSON string like '{"scenario": "...", "members": ["значно", "набагато"]}'
        or '' if not clustered
    """
    try:
        registry = ClusterRegistry()
        # Query by note_id to see if this note is in any cluster
        cluster = registry.get_cluster_by_note_id(note_id)
        if not cluster:
            return ""

        # Get compare card members (hub shows all; satellites show hub + self)
        members = registry.get_compare_card_members(note_id)
        if not members:
            return ""

        # Get scenario from the member of this cluster matching this note_id
        scenario = ""
        for member in cluster.members:
            if member.note_id == note_id:
                scenario = member.compare_scenario
                break

        data = {
            "scenario": scenario,
            "members": [member.lemma for member in members],
        }
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        # Log warning but don't fail import
        print(f"Warning: Failed to load cluster members for {note_id}: {e}")
        return ""


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

    # Structured grading input for EN_UA_BACK's answer-side script. Replaced
    # the positionally-aligned _EuphonySlots string 2026-08-19 -- see
    # compute_typing_spec() and docs/ua-en-ua-euphony-aspect-refactor.md.
    fields["_TypingSpec"] = compute_typing_spec(
        fields.get("Lemma", ""),
        fields.get("ImperfectiveUnidirectional", ""),
        fields.get("Perfective", ""),
        fields.get("Lemma_Euphony", ""),
        fields.get("ImperfectiveUnidirectional_Euphony", ""),
        fields.get("Perfective_Euphony", ""),
    )

    # UA->EN Recognition card front display (added 2026-08-04, CLAUDE.md
    # "UA->EN lexeme verb cards -- show multiple aspects per euphonic slot").
    # Same aspect-slot join as TypingTarget_UA, but with per-slot euphonic
    # alternates shown inline -- see compute_ua_en_display docstring. Always
    # computed, even for non-verb/singlet notes, where it just renders as
    # Lemma (optionally with Lemma_Euphony), matching TypingTarget_UA's own
    # fallback for those notes.
    fields["_UA_EN_DisplayLemma"] = compute_ua_en_display(
        fields.get("Lemma", ""),
        fields.get("ImperfectiveUnidirectional", ""),
        fields.get("Perfective", ""),
        fields.get("Lemma_Euphony", ""),
        fields.get("ImperfectiveUnidirectional_Euphony", ""),
        fields.get("Perfective_Euphony", ""),
    )

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
    # Handle Compare field logic: only registry-driven clusters
    # (Phase 6: CompareA/B/C/D/CompareScenario/Homograph_SenseA/B removed from
    # schema; legacy auto-derive fallback removed. The confusable cluster
    # registry -- confusable_clusters.yaml, 100% backfilled as of Phase 2 --
    # is now the single source of truth for every Compare card.)
    cluster_members_json = get_cluster_compare_members_json(note_id, tags)
    fields["CompareMembers"] = cluster_members_json if cluster_members_json else ""

    # Suspension policy -- see module docstring.
    suspend = "status:draft" in tags

    # Compare card suspension: suspend if ConfusableSet is empty (no confusables/
    # homographs), OR if it's populated but CompareA never got authored --
    # CompareA is "always required" by the Compare template's own design
    # (CompareB/C/D optional; see comment above CARD_TEMPLATES in
    # setup_ua_note_types.py), so a blank CompareA here means the actual
    # chip content is missing even though ConfusableSet has text (e.g. a
    # homograph:true note where CompareA/B were never authored -- those
    # aren't auto-derived above, unlike the confusables case). Found 2026-07-28
    # alongside the CompareA/CompareB clobbering bug. Tested 2026-08-01 (see
    # CLAUDE.md item 6): this suspend call is actually a no-op in the blank-
    # CompareA-from-creation case -- the template's "should be suspended"
    # notice is pure static text with no field substitution, so Anki's own
    # empty-card-generation rule never creates the card in the first place.
    # This suspend call earns its keep in a different, real scenario instead:
    # a note whose Compare card was already generated with valid data, then
    # later has that data retracted (ConfusableSet/CompareA/CompareB cleared)
    # -- confirmed working end-to-end via a two-phase test (see CLAUDE.md
    # item 6), so the already-existing card does get suspended on re-sync.
    # Compare card suspension: suspend if no cluster members
    # (Phase 6: CompareA/B logic removed; registry is single source of truth)
    compare_members = fields.get("CompareMembers", "").strip()
    suspend_compare_card = not compare_members

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
        # Red-flag override -- see module docstring and
        # get_flagged_note_ids_by_color in tsv_to_anki.py. Only meaningful
        # here (the existing-note path): a note can't have a flagged card in
        # Anki before this sync creates it. Orange doesn't reach this point
        # at all -- main() only puts FLAG_RED note ids into flagged_note_ids.
        flagged = existing_id in flagged_note_ids
        note_suspend = suspend or flagged
        compare_suspend = suspend_compare_card or flagged
        update_note(existing_id, fields, tags, dry_run)
        if not dry_run:
            route_cards_to_decks(existing_id, dry_run)
            set_suspended(existing_id, note_suspend, dry_run)
            set_compare_card_suspended(existing_id, compare_suspend, dry_run)
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
