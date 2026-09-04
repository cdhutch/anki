"""Typing target and stress manipulation utilities for UA_Lexeme.

Moved to a separate module 2026-08-20 so cnsf_canonicalize.py can import
them without depending on the full ua_lexeme_import.py module (which imports
AnkiConnect and other heavy dependencies that the pre-commit hook's venv
doesn't have).

Functions here are re-exported by ua_lexeme_import.py so existing callers
continue to work unchanged.
"""

import re
from typing import Optional, Tuple


def strip_stress(text: str) -> str:
    """Remove combining stress marks (U+0301) from text.

    Returns text with all U+0301 combining grave accents removed.
    """
    if not text:
        return text
    return text.replace('́', '')


def compute_typing_target(
    lemma: str,
    impf_uni: str,
    perfective: str,
) -> Optional[Tuple[str, str]]:
    """Build TypingTarget_UA and TypingAnswer for EN->UA typing card.

    Joins populated aspect slots (Lemma, ImperfectiveUnidirectional, Perfective)
    with " / " separator. Returns None (fall back to Lemma alone) when fewer
    than two slots are populated -- a true singlet, or a non-verb note.

    Returns:
        Tuple of (TypingTarget_UA_stressed, TypingAnswer_unstressed) or None

    Example:
        - Triplet (ходити / йти / піти):
          ("ходи́ти / йти / піти́", "ходити / йти / піти")
        - Doublet (перекида́ти / переки́нути):
          ("перекида́ти / переки́нути", "перекидати / перекинути")
        - Singlet (ма́ти) → None (caller falls back to Lemma)
    """
    slots = [s for s in [lemma, impf_uni, perfective] if s]

    # Need at least 2 slots (doublet or triplet) to form a join
    if len(slots) < 2:
        return None

    # Stressed join is the typing target; unstressed is the typed answer
    stressed_join = " / ".join(slots)
    unstressed_join = " / ".join(strip_stress(s) for s in slots)

    return (stressed_join, unstressed_join)
