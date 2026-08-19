"""
tests/ua/test_lexeme_import.py

Unit tests for tools/anki/sync/ua_lexeme_import.py's pure decision logic:
compute_typing_target() (the EN->UA aspect-join builder) plus
compute_ua_en_display() (UA->EN display with euphonic parentheticals).
Everything else in this module talks to AnkiConnect directly and isn't
practically unit-testable without a live Anki instance. This module had zero
test coverage before 2026-07-25.

Removed 2026-08-19: the TestComputeEuphonySlots class. compute_euphony_slots()
no longer exists -- Option B of docs/ua-en-ua-euphony-aspect-refactor.md
replaced its position-aligned " / "-joined `_EuphonySlots` string with
compute_typing_spec()'s structured `_TypingSpec` JSON, where each slot carries
its own alternates. Its replacement coverage lives in test_typing_spec.py,
including a guard (TestEmptyCases::test_legacy_euphony_note_fallback_is_gone)
that the removed EuphonyNote fallback stays removed.

Removed 2026-08-11 (per Craig): the TestPruneOrphansSafetyGate class, which
tested a prune_orphans()/collect_all_corpus_note_ids()/all_anki_note_ids()/
delete_notes() safety gate that was never actually built (CLAUDE.md item 19,
CLAUDE-work-queue.md "Two pre-existing test_lexeme_import.py failure groups").
Craig wants `make ua-test` to run clean rather than carry known-failing specs
for unbuilt code -- new tests get written alongside that feature if/when it's
actually implemented, not kept failing in the meantime as a to-do list.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.sync.ua_lexeme_import as li  # noqa: E402


# ---------------------------------------------------------------------------
# compute_typing_target
#
# Corrected 2026-08-11: this class previously tested the 2026-07-25
# Lemma_Euphony redesign (881ac25/2e93202 -- dict-returning, "full"/"base"/
# "alt" keys, euphony-aware kwargs, requiring BOTH primary and euphonic forms
# typed together). That redesign was reverted 2026-07-28 (git archaeology,
# commit a5b4a15) back to this simpler, tolerance-only design -- see
# compute_typing_target()'s own docstring in ua_lexeme_import.py. 7 of these
# 8 tests kept asserting on the abandoned dict/kwarg shape and had been
# failing ever since (flagged in passing 2026-07-31/08-04, confirmed and
# fixed here -- see CLAUDE.md's "Per-slot euphony tolerance" section). Per-
# slot euphony tolerance itself is real and live -- it's just implemented
# elsewhere: compute_typing_spec() (test_typing_spec.py) and
# compute_ua_en_display() (TestComputeUaEnDisplay below) populate the data, and
# the EN_UA_BACK card template's feedback script does the actual per-slot
# PERFECT/CORRECT/INCORRECT tolerance check at review time -- not this
# function, which stays deliberately euphony-unaware.
# ---------------------------------------------------------------------------


class TestComputeTypingTarget:
    def test_singlet_returns_none(self):
        # Imperfective-only verb, e.g. мати -- no aspectual counterpart.
        assert li.compute_typing_target("ма́ти", "", "") is None

    def test_doublet_lemma_and_perfective(self):
        result = li.compute_typing_target("перекида́ти", "", "переки́нути")
        assert result == ("перекида́ти / переки́нути", "перекидати / перекинути")

    def test_doublet_lemma_and_impf_uni_no_double_slash(self):
        # Middle slot (impf_uni) populated, perfective empty -- must not leave
        # a trailing " / " artifact.
        stressed, _ = li.compute_typing_target("ходи́ти", "йти", "")
        assert stressed == "ходи́ти / йти"
        assert "//" not in stressed
        assert not stressed.endswith("/")

    def test_triplet_all_three_slots_in_order(self):
        result = li.compute_typing_target("ходи́ти", "йти", "піти́")
        assert result == ("ходи́ти / йти / піти́", "ходити / йти / піти")

    def test_missing_lemma_still_joins_remaining_two(self):
        # Defensive case -- Lemma should always be populated in practice, but
        # the function only counts populated slots, order-preserving.
        stressed, _ = li.compute_typing_target("", "йти", "піти́")
        assert stressed == "йти / піти́"

    def test_unstressed_variant_strips_stress_from_all_slots(self):
        _, unstressed = li.compute_typing_target("ходи́ти", "йти", "піти́")
        assert unstressed == "ходити / йти / піти"


# ---------------------------------------------------------------------------
# compute_ua_en_display
#
# Added 2026-08-04 (UA->EN display, CLAUDE.md "UA->EN lexeme verb cards -- show
# multiple aspects per euphonic slot"). Positionally aligned with
# compute_typing_target's " / " join order (Lemma, ImperfectiveUnidirectional,
# Perfective, each only if populated) -- see the function's own docstring in
# ua_lexeme_import.py. Untouched by the 2026-08-19 _TypingSpec refactor: this
# builds a human-readable string for the UA->EN direction and never feeds the
# grader, so it has no reason to become structured.
# ---------------------------------------------------------------------------


class TestComputeUaEnDisplay:
    def test_no_slots_populated_returns_blank(self):
        assert li.compute_ua_en_display("", "", "", "", "", "") == ""

    def test_triplet_no_euphony_matches_typing_target_join(self):
        result = li.compute_ua_en_display("ходи́ти", "йти", "піти́", "", "", "")
        assert result == "ходи́ти / йти / піти́"

    def test_doublet_euphony_only_on_perfective_slot(self):
        # Only the Perfective slot gets a parenthetical; the Lemma slot is
        # printed bare. (Shape taken from ua-lexeme-0115 before its 2026-08-18
        # в-/у- flip -- the note now has euphony on both slots, which the next
        # test covers, but this one-sided case is still the one worth pinning.)
        result = li.compute_ua_en_display("вхо́дити", "", "ввійти́", "", "", "увійти́")
        assert result == "вхо́дити / ввійти́ (увійти́)"

    def test_doublet_euphony_on_both_slots(self):
        # ua-lexeme-0115 as it stands after the 2026-08-18 flip: в- forms are
        # the headwords (per Shevchuk), у- forms the euphonic partners.
        result = li.compute_ua_en_display(
            "вхо́дити", "", "ввійти́", "ухо́дити", "", "увійти́",
        )
        assert result == "вхо́дити (ухо́дити) / ввійти́ (увійти́)"

    def test_singlet_with_euphony_gets_parenthetical(self):
        result = li.compute_ua_en_display("вболіва́льник", "", "", "уболіва́льник", "", "")
        assert result == "вболіва́льник (уболіва́льник)"

    def test_euphony_ignored_when_primary_slot_empty(self):
        result = li.compute_ua_en_display("вболіва́ти", "", "", "", "", "щось")
        assert "щось" not in result
