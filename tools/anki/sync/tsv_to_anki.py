#!/usr/bin/env python3
"""AnkiConnect bridge for syncing notes to Anki.

Provides anki_request() for programmatic Anki interaction via AnkiConnect,
plus helper functions for flag handling and note identification.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable

# Flag color constants -- in Anki's flag system, 1=red, 2=orange, 3=green, etc.
# Per Craig 2026-08-10: red suspends notes, orange does not (call-out only).
FLAG_RED = 1
FLAG_ORANGE = 2

# Flag suspension policy: only these flag colors force automatic suspension on sync.
# Orange flags call out in the log but don't suspend; red flags do.
SUSPEND_FLAG_COLORS = (FLAG_RED,)
# Ukrainian deck tree for scoping flag queries.
UA_DECK_TREE = "deck:UA::*"


def anki_request(action: str, params: Dict[str, Any] | None = None, url: str = "http://127.0.0.1:8765") -> Any:
    """Make a request to AnkiConnect.

    Args:
        action: AnkiConnect API action (e.g., "addNote", "createModel")
        params: Parameters for the action
        url: AnkiConnect server URL (default: localhost:8765)

    Returns:
        The result from AnkiConnect, or raises an exception on error.

    Raises:
        Exception: If AnkiConnect is not running or the action fails.
    """
    if params is None:
        params = {}

    request_obj = {"action": action, "params": params, "version": 6}
    request_json = json.dumps(request_obj).encode("utf-8")

    try:
        response = urllib.request.urlopen(urllib.request.Request(url, request_json))
        response_text = response.read().decode("utf-8")
        response_obj = json.loads(response_text)

        if response_obj.get("error") is not None:
            raise Exception(f"AnkiConnect error: {response_obj.get('error')}")

        return response_obj.get("result")

    except urllib.error.URLError:
        raise Exception(
            f"Failed to connect to AnkiConnect at {url}. "
            "Make sure Anki is running and AnkiConnect is installed."
        )
    except json.JSONDecodeError:
        raise Exception("AnkiConnect returned invalid JSON")


def flag_query_for_model(model_name: str, deck_query: str | None = None) -> str:
    """Build a scoped flag query for a specific note type.

    Returns a query string that targets cards belonging to notes of the
    specified model within a deck tree. Used to scope flag audits to a single
    note type rather than the whole deck tree.

    Args:
        model_name: The Anki note type name (e.g., "UA_Lexeme", "UA_Verb")
        deck_query: Deck query to scope to (default: UA_DECK_TREE)

    Returns:
        A query string like "deck:UA::* note:UA_Lexeme"
    """
    if deck_query is None:
        deck_query = UA_DECK_TREE
    return f"{deck_query} note:{model_name}"


def get_flagged_note_ids_by_color(deck_query: str, url: str) -> Dict[int, set[int]]:
    """Query Anki for flagged cards and return note IDs split by flag color.

    Fetches all cards matching the query, extracts their note IDs, and groups
    them by flag color (1=red, 2=orange). Used for the red/orange split
    introduced 2026-08-10 -- red flags force suspension, orange flags
    call out but don't suspend.

    Args:
        deck_query: An Anki card query string (e.g., "note:UA_Lexeme flag:1,2")
        url: AnkiConnect server URL

    Returns:
        A dict mapping flag colors (FLAG_RED, FLAG_ORANGE) to sets of note IDs.
        Both keys are always present; sets may be empty.
    """
    card_ids = anki_request("findCards", {"query": deck_query}, url)
    if not card_ids:
        return {FLAG_RED: set(), FLAG_ORANGE: set()}

    # Fetch card info for all flagged cards to get their note IDs and flags.
    card_info_list = anki_request("cardsInfo", {"cards": card_ids}, url)

    flags_by_color: Dict[int, set[int]] = {FLAG_RED: set(), FLAG_ORANGE: set()}
    for card_info in card_info_list:
        flag_color = card_info.get("flag", 0)
        if flag_color in flags_by_color:
            flags_by_color[flag_color].add(card_info["noteId"])

    return flags_by_color


def describe_note_ids(note_ids: set[int] | Iterable[int], url: str) -> list[str]:
    """Map note IDs to human-readable labels for logging.

    Fetches note info from Anki and builds descriptive labels showing
    the note ID and its key fields (varies by note type). Used to print
    flagged-note names in the sync log.

    Args:
        note_ids: Set or iterable of note IDs to describe
        url: AnkiConnect server URL

    Returns:
        A list of human-readable labels like "ua-lexeme-0115 вхо́дити".
    """
    if isinstance(note_ids, set):
        note_ids = sorted(note_ids)
    else:
        note_ids = sorted(note_ids)

    if not note_ids:
        return []

    notes = anki_request("notesInfo", {"notes": note_ids}, url)
    labels = []

    for note in notes:
        note_id = note.get("noteId", "?")
        fields = note.get("fields", {})

        # Try to extract a meaningful label -- NoteID + a key field.
        # For UA_Lexeme: use Lemma; for UA_Verb: use Lemma; for others: use first non-empty field.
        label_parts = [str(note_id)]

        if "NoteID" in fields:
            label_parts.append(fields["NoteID"]["value"])
        if "Lemma" in fields:
            lemma = fields["Lemma"]["value"]
            if lemma:
                label_parts.append(lemma)
        elif "Phoneme" in fields:
            phoneme = fields["Phoneme"]["value"]
            if phoneme:
                label_parts.append(phoneme)

        labels.append("  ".join(label_parts))

    return labels
