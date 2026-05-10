#!/usr/bin/env python3
"""set_stage.py — Activate/deactivate B737 Core decks by study stage.

Works by suspending new (unseen) cards in inactive decks and unsuspending
them in active decks. Does not touch review or learning cards.

After staging, a seat filter suspends all cards tagged for the opposite
crew seat across all B737 decks (including review/learning cards).

Usage:
    python tools/anki/sync/set_stage.py --stage 1            # FO seat (default)
    python tools/anki/sync/set_stage.py --stage 2 --seat fo  # explicit FO
    python tools/anki/sync/set_stage.py --stage 2 --seat captain
    python tools/anki/sync/set_stage.py --dry-run --stage 2

Stage definitions
-----------------
Stage 1 — Foundation
    Active  : Limits::Non-Trivia (all sub-decks), QRC, Triggers_and_Flows::Triggers
    Inactive: Limits::Trivia, Flows, Supplemental, all Procedures

Stage 2 — Flows + Supplemental
    Active  : Stage 1 + Triggers_and_Flows::Flows + Triggers_and_Flows::Supplemental
    Inactive: Limits::Trivia, all Procedures

Stage 3 — Normal Procedures
    Active  : Stage 2 + Procedures::Normal
    Inactive: Limits::Trivia, Procedures::Non_Normal, Procedures::Inflight_Maneuvers

Stage 4 — Full Procedures
    Active  : Stage 3 + Procedures::Non_Normal + Procedures::Inflight_Maneuvers
    Inactive: Limits::Trivia

Stage 5 — Full Core
    Active  : all B737::Core decks (+ Limits::Trivia)

Seat filter
-----------
crew_role:captain and crew_role:first_officer tags drive seat-specific
suspension. crew_role:pilot_flying and crew_role:pilot_monitoring are
never suppressed — both seats need to know both roles.

Cards with crew_role tags outside Procedures or Triggers_and_Flows are
flagged as likely tagging mistakes.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANKI_URL = "http://127.0.0.1:8765"

# Deck prefix for all Core pool decks.
CORE_ROOT = "B737::Core"

# Root prefix for all B737 decks (used by seat filter queries).
B737_ROOT = "B737"

# Deck prefixes where crew_role tags are expected.
# Cards with crew_role tags outside these prefixes are flagged as warnings.
CREW_ROLE_EXPECTED_PREFIXES = [
    "B737::Core::Procedures",
    "B737::Core::Triggers_and_Flows",
]

# Seat filter: maps seat name to the tag that should be suppressed.
# pilot_flying / pilot_monitoring are intentionally excluded — both seats
# need to know both roles and they are never suppressed.
SEAT_SUPPRESS_TAG: dict[str, str] = {
    "fo":      "crew_role:captain",
    "captain": "crew_role:first_officer",
}
SEAT_REVEAL_TAG: dict[str, str] = {
    "fo":      "crew_role:first_officer",
    "captain": "crew_role:captain",
}

# Each entry lists the *additional* decks activated at that stage.
# Matching is by prefix: "B737::Core::Limits" also covers
# "B737::Core::Limits::Trivia", "B737::Core::Limits::Non-Trivia", etc.
STAGE_ADDITIONS: dict[int, list[str]] = {
    1: [
        "B737::Core::Limits::Non-Trivia",
        "B737::Core::QRC",
        "B737::Core::Triggers_and_Flows::Triggers",
    ],
    2: [
        "B737::Core::Triggers_and_Flows::Flows",
        "B737::Core::Triggers_and_Flows::Supplemental",
    ],
    3: [
        "B737::Core::Procedures::Normal",
    ],
    4: [
        "B737::Core::Procedures::Non_Normal",
        "B737::Core::Procedures::Inflight_Maneuvers",
    ],
    5: [
        "B737::Core::Limits::Trivia",
    ],
}


def active_prefixes(stage: int) -> list[str]:
    """Return all deck prefixes that should be active at *stage*."""
    prefixes: list[str] = []
    for s in range(1, stage + 1):
        prefixes.extend(STAGE_ADDITIONS.get(s, []))
    return prefixes


# ---------------------------------------------------------------------------
# AnkiConnect
# ---------------------------------------------------------------------------

def anki_request(action: str, params: dict | None = None, url: str = ANKI_URL) -> Any:
    payload = {"action": action, "version": 6, "params": params or {}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error [{action}]: {data['error']}")
    return data.get("result")


# ---------------------------------------------------------------------------
# Deck helpers
# ---------------------------------------------------------------------------

def all_core_decks(url: str) -> dict[str, int]:
    """Return {deck_name: deck_id} for all B737::Core decks."""
    all_decks: dict[str, int] = anki_request("deckNamesAndIds", url=url)
    return {
        name: did
        for name, did in all_decks.items()
        if name == CORE_ROOT or name.startswith(CORE_ROOT + "::")
    }


def is_active(deck_name: str, active_pfx: list[str]) -> bool:
    """True if deck_name should be active given the list of active prefixes."""
    for pfx in active_pfx:
        if deck_name == pfx or deck_name.startswith(pfx + "::"):
            return True
    return False


# ---------------------------------------------------------------------------
# Card operations
# ---------------------------------------------------------------------------

def find_suspended_new_cards(deck_name: str, url: str) -> list[int]:
    """Return IDs of suspended new (never reviewed) cards in a deck."""
    query = f'"deck:{deck_name}" is:new is:suspended'
    return anki_request("findCards", {"query": query}, url=url) or []


def find_unsuspended_new_cards(deck_name: str, url: str) -> list[int]:
    """Return IDs of new cards that are not suspended."""
    query = f'"deck:{deck_name}" is:new -is:suspended'
    return anki_request("findCards", {"query": query}, url=url) or []


def suspend_cards(card_ids: list[int], url: str) -> None:
    if card_ids:
        anki_request("suspend", {"cards": card_ids}, url=url)


def unsuspend_cards(card_ids: list[int], url: str) -> None:
    if card_ids:
        anki_request("unsuspend", {"cards": card_ids}, url=url)


def find_cards_by_tag(tag: str, url: str) -> list[int]:
    """Return all B737 card IDs carrying *tag* (any state)."""
    query = f'tag:{tag} "deck:{B737_ROOT}"'
    return anki_request("findCards", {"query": query}, url=url) or []


def find_suspended_cards_by_tag_in_decks(
    tag: str, deck_prefixes: list[str], url: str
) -> list[int]:
    """Return suspended cards with *tag* that live in any of *deck_prefixes*."""
    if not deck_prefixes:
        return []
    deck_clause = " OR ".join(f'"deck:{p}"' for p in deck_prefixes)
    query = f'tag:{tag} is:suspended ({deck_clause})'
    return anki_request("findCards", {"query": query}, url=url) or []


def find_crew_role_cards_outside_expected(url: str) -> list[int]:
    """Return cards with any crew_role tag that are outside expected decks."""
    tag_clause = (
        "tag:crew_role:captain OR tag:crew_role:first_officer "
        "OR tag:crew_role:pilot_flying OR tag:crew_role:pilot_monitoring"
    )
    exclude_clause = " ".join(
        f'-"deck:{p}"' for p in CREW_ROLE_EXPECTED_PREFIXES
    )
    query = f'({tag_clause}) {exclude_clause} "deck:{B737_ROOT}"'
    return anki_request("findCards", {"query": query}, url=url) or []


# ---------------------------------------------------------------------------
# Seat filter
# ---------------------------------------------------------------------------

def apply_seat_filter(
    seat: str, active_pfx: list[str], dry_run: bool, url: str
) -> None:
    """Suspend opposite-seat cards; reveal active-seat cards in active decks.

    Runs after staging so the seat filter always has the final word.
    crew_role:pilot_flying and crew_role:pilot_monitoring are never touched.
    """
    suppress_tag = SEAT_SUPPRESS_TAG[seat]
    reveal_tag   = SEAT_REVEAL_TAG[seat]

    print(f"\n{'DRY RUN — ' if dry_run else ''}Seat filter: studying as {seat.upper()}")

    # 1. Suspend ALL cards (any state) tagged for the opposite seat.
    suppress_ids = find_cards_by_tag(suppress_tag, url)
    print(f"  [SUPPRESS]  tag:{suppress_tag}")
    print(f"               → suspend {len(suppress_ids)} card(s)")
    if suppress_ids and not dry_run:
        suspend_cards(suppress_ids, url)

    # 2. Unsuspend active-seat cards that are suspended and in active stage decks.
    reveal_ids = find_suspended_cards_by_tag_in_decks(reveal_tag, active_pfx, url)
    print(f"  [REVEAL]    tag:{reveal_tag} in active stage decks")
    print(f"               → unsuspend {len(reveal_ids)} card(s)")
    if reveal_ids and not dry_run:
        unsuspend_cards(reveal_ids, url)

    # 3. Warn about crew_role tags on cards outside expected decks.
    unexpected_ids = find_crew_role_cards_outside_expected(url)
    if unexpected_ids:
        print(
            f"\n  ⚠  {len(unexpected_ids)} card(s) with crew_role tags found "
            f"outside Procedures / Triggers_and_Flows — likely tagging errors:"
        )
        if not dry_run:
            info = anki_request(
                "cardsInfo", {"cards": unexpected_ids[:50]}, url=url
            )
            for card in (info or []):
                note_id_field = card.get("fields", {}).get("Note ID", {})
                note_id = (
                    note_id_field.get("value", "")
                    if isinstance(note_id_field, dict) else ""
                )
                print(f"     [{card['cardId']}]  {card.get('deckName', '?')}"
                      + (f"  ({note_id})" if note_id else ""))
            if len(unexpected_ids) > 50:
                print(f"     … and {len(unexpected_ids) - 50} more")
        else:
            print("     (run without --dry-run to see card details)")


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def set_stage(stage: int, seat: str, dry_run: bool, url: str) -> None:
    active_pfx = active_prefixes(stage)
    core_decks = all_core_decks(url)

    if not core_decks:
        print("No B737::Core decks found — is Anki open with AnkiConnect running?")
        sys.exit(1)

    print(f"\n{'DRY RUN — ' if dry_run else ''}Setting stage {stage}")
    print(f"Active prefixes: {active_pfx}\n")

    total_suspended = 0
    total_unsuspended = 0

    # Only operate on the explicit leaf prefixes defined in STAGE_ADDITIONS.
    # Parent aggregator decks (e.g. B737::Core::Procedures) are skipped to
    # avoid double-counting cards that also appear in their child decks.
    all_known_pfx = [pfx for pfxs in STAGE_ADDITIONS.values() for pfx in pfxs]

    for pfx in sorted(all_known_pfx):
        deck_active = pfx in active_pfx

        if deck_active:
            suspended = find_suspended_new_cards(pfx, url)
            status = "ACTIVATE"
            action_str = f"unsuspend {len(suspended)} new card(s)"
            if suspended and not dry_run:
                unsuspend_cards(suspended, url)
            total_unsuspended += len(suspended)
        else:
            unsuspended = find_unsuspended_new_cards(pfx, url)
            status = "DEACTIVATE"
            action_str = f"suspend {len(unsuspended)} new card(s)"
            if unsuspended and not dry_run:
                suspend_cards(unsuspended, url)
            total_suspended += len(unsuspended)

        print(f"  [{status:>10}]  {pfx}")
        print(f"               → {action_str}")

    print()

    # Flag any Anki decks not accounted for by any known prefix.
    # A deck is covered if it is a known prefix, a sub-deck of one, or a
    # parent aggregator of one.
    unknown_decks: list[str] = []
    for deck_name in sorted(core_decks):
        if deck_name == CORE_ROOT:
            continue
        covered = any(
            deck_name == pfx
            or deck_name.startswith(pfx + "::")   # sub-deck of known prefix
            or pfx.startswith(deck_name + "::")   # parent aggregator of known prefix
            for pfx in all_known_pfx
        )
        if not covered:
            unknown_decks.append(deck_name)

    if unknown_decks:
        print("⚠  Decks in Anki not assigned to any stage — update STAGE_ADDITIONS:")
        for d in unknown_decks:
            print(f"     {d}")
        print()

    if dry_run:
        print(f"DRY RUN complete. Would suspend {total_suspended} card(s), "
              f"unsuspend {total_unsuspended} card(s).")
        print("Re-run without --dry-run to apply.")
    else:
        print(f"Stage {stage} applied. "
              f"Suspended {total_suspended} new card(s), "
              f"unsuspended {total_unsuspended} new card(s).")

    # Apply seat filter after staging so it always has the final word.
    apply_seat_filter(seat=seat, active_pfx=active_pfx, dry_run=dry_run, url=url)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Activate/deactivate B737 Core decks by study stage."
    )
    ap.add_argument(
        "--stage", type=int, choices=[1, 2, 3, 4, 5], required=True,
        help=(
            "Study stage to apply: "
            "1=Limits::Non-Trivia+QRC+Triggers, "
            "2=+Flows+Supplemental, "
            "3=+Procedures::Normal, "
            "4=+Procedures::Non_Normal+Inflight_Maneuvers, "
            "5=+Limits::Trivia"
        ),
    )
    ap.add_argument(
        "--seat", choices=["fo", "captain"], default="fo",
        help=(
            "Crew seat being studied. The opposite seat's cards are suspended. "
            "'fo' (default) suppresses crew_role:captain cards; "
            "'captain' suppresses crew_role:first_officer cards."
        ),
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying Anki.",
    )
    ap.add_argument(
        "--anki-url", default=ANKI_URL,
        help=f"AnkiConnect base URL (default: {ANKI_URL}).",
    )
    args = ap.parse_args()

    try:
        set_stage(stage=args.stage, seat=args.seat, dry_run=args.dry_run, url=args.anki_url)
    except OSError as e:
        print(f"\nCannot reach AnkiConnect at {args.anki_url}: {e}")
        print("Make sure Anki is open and the AnkiConnect add-on is active.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
