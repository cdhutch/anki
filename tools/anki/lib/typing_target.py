#!/usr/bin/env python3
"""The EN→UA typing target join, in one stdlib-only place.

Hoisted out of `ua_lexeme_import.py` on 2026-08-20 so `cnsf_canonicalize.py`
can compute the same value the importer does. It used to live only in the
importer, which meant the canonicaliser had no way to check `TypingAnswer`
against the fields it is derived from -- and 62 CNSF notes had quietly drifted
away from it (found during the `_TypingSpec` rollout, 2026-08-19). Nothing was
ever wrong in Anki: `import_note()` overwrites `TypingAnswer` from
`compute_typing_target()[1]` on every doublet and triplet, so the live cards
have always been right. The drift was confined to the files -- which matters
only because CNSF is meant to be the source of truth, and a reader of
`ua-lexeme-0114` would conclude the card asks for `приходити` when it asks for
`приходити / прийти`.

**Why this module and not an import of ua_lexeme_import.** `cnsf_canonicalize`
runs under the `cnsf-canonical` pre-commit hook in an isolated venv declaring
only pyyaml, and its module docstring asks that the chain it pulls in stay
stdlib-only. `ua_lexeme_import` imports yaml itself -- survivable, since the
hook declares it -- but it also opens the door to that module growing a real
dependency later and breaking the hook from a distance. A leaf module with no
imports at all cannot do that.

`ua_lexeme_import` re-exports both names, so `li.compute_typing_target` and
`li.strip_stress` keep working for every existing caller and test.
"""
from __future__ import annotations

STRESS_MARK = "́"  # combining acute


def strip_stress(s: str) -> str:
    """Remove the combining acute accent (U+0301) used for stress marks."""
    return s.replace(STRESS_MARK, "")


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

    Computed here rather than hand-authored into a new CNSF field, by design:
    Lemma/ImperfectiveUnidirectional/Perfective are already the authored
    source of truth, and deriving the join avoids a second, independently-
    authored field silently drifting out of sync with -- or being clobbered
    relative to -- the fields it's derived from.

    That last sentence describes exactly what then happened to `TypingAnswer`,
    which is authored and NOT derived at authoring time. See this module's own
    docstring, and `_sync_typing_answer()` in cnsf_canonicalize.py, which now
    closes the loop on the file side.
    """
    parts = [p for p in (lemma, impf_uni, perfective) if p]
    if len(parts) < 2:
        return None
    stressed = " / ".join(parts)
    unstressed = " / ".join(strip_stress(p) for p in parts)
    return stressed, unstressed
