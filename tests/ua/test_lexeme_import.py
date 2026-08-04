"""
tests/ua/test_lexeme_import.py

Unit tests for tools/anki/sync/ua_lexeme_import.py's pure decision logic:
compute_typing_target() (the EN->UA aspect-join builder) and prune_orphans()'s
safety gate (the FSRS-history-protecting refuse-if-dirty check). Everything
else in this module talks to AnkiConnect directly and isn't practically
unit-testable without a live Anki instance -- these two pieces are worth
covering on their own, especially the safety gate, since a regression there
means a single unrelated YAML typo could silently wipe review history on an
unrelated note. This module had zero test coverage before 2026-07-25.
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
# Redesigned 2026-07-25: returns a dict of three (stressed, unstressed) pairs
# -- "full" (euphony nested in per-slot, e.g. "primary ; euphonic"), "base"
# (primary forms only, the pre-redesign behavior), "alt" (euphonic form in
# place of primary where populated, else primary; blank pair when no slot has
# any euphony). See CLAUDE.md "Lemma_Euphony / aspect+euphony recognition
# testing" for the full design.
# ---------------------------------------------------------------------------


class TestComputeTypingTarget:
    def test_singlet_no_euphony_returns_none(self):
        # Imperfective-only verb, e.g. мати -- no aspectual counterpart, no
        # euphony either.
        assert li.compute_typing_target("ма́ти", "", "") is None

    def test_doublet_lemma_and_perfective(self):
        result = li.compute_typing_target("перекида́ти", "", "переки́нути")
        assert result is not None
        assert result["full"] == ("перекида́ти / переки́нути", "перекидати / перекинути")
        assert result["base"] == result["full"]
        assert result["alt"] == ("", "")

    def test_doublet_lemma_and_impf_uni_no_double_slash(self):
        # Middle slot (impf_uni) populated, perfective empty -- must not leave
        # a trailing " / " artifact.
        stressed, _ = li.compute_typing_target("ходи́ти", "йти", "")["full"]
        assert stressed == "ходи́ти / йти"
        assert "//" not in stressed
        assert not stressed.endswith("/")

    def test_triplet_all_three_slots_in_order(self):
        result = li.compute_typing_target("ходи́ти", "йти", "піти́")
        assert result["full"] == ("ходи́ти / йти / піти́", "ходити / йти / піти")

    def test_missing_lemma_still_joins_remaining_two(self):
        # Defensive case -- Lemma should always be populated in practice, but
        # the function only counts populated slots, order-preserving.
        stressed, _ = li.compute_typing_target("", "йти", "піти́")["full"]
        assert stressed == "йти / піти́"

    def test_singlet_with_euphony_does_not_return_none(self):
        # вболівати (ua-lexeme-0211): no aspect partner at all, but Lemma has
        # a euphonic alternate -- must NOT early-return None like a plain
        # aspectless singlet would.
        result = li.compute_typing_target(
            "вболіва́ти", "", "", lemma_euphony="уболіва́ти",
        )
        assert result is not None
        assert result["full"] == ("вболіва́ти ; уболіва́ти", "вболівати ; уболівати")
        assert result["base"] == ("вболіва́ти", "вболівати")
        assert result["alt"] == ("уболіва́ти", "уболівати")

    def test_euphony_on_one_slot_only(self):
        # учити/вчити -> вивчити: euphony only on the imperfective slot.
        result = li.compute_typing_target(
            "учи́ти", "", "ви́вчити", lemma_euphony="вчи́ти",
        )
        assert result["full"] == ("учи́ти ; вчи́ти / ви́вчити", "учити ; вчити / вивчити")
        assert result["base"] == ("учи́ти / ви́вчити", "учити / вивчити")
        assert result["alt"] == ("вчи́ти / ви́вчити", "вчити / вивчити")

    def test_no_euphony_on_any_slot_alt_is_blank(self):
        result = li.compute_typing_target("ходи́ти", "йти", "піти́")
        assert result["alt"] == ("", "")

    def test_euphony_ignored_when_primary_slot_empty(self):
        # Defensive: a *_Euphony value on an unpopulated slot shouldn't leak
        # into the join (shouldn't happen given the CNSF authoring contract,
        # but the function must not blow up or silently include it).
        result = li.compute_typing_target(
            "вболіва́ти", "", "", lemma_euphony="уболіва́ти",
            perfective_euphony="щось",
        )
        assert "щось" not in result["full"][0]
        assert "щось" not in result["alt"][0]


# ---------------------------------------------------------------------------
# compute_euphony_slots / compute_ua_en_display
#
# Added 2026-08-04 (per-slot euphony tolerance + UA->EN display, CLAUDE.md
# "Per-slot euphony tolerance" and "UA->EN lexeme verb cards -- show multiple
# aspects per euphonic slot"). Both are positionally aligned with
# compute_typing_target's " / " join order (Lemma, ImperfectiveUnidirectional,
# Perfective, each only if populated) -- see the functions' own docstrings in
# ua_lexeme_import.py. Test data mirrors real corpus notes where noted.
# ---------------------------------------------------------------------------


class TestComputeEuphonySlots:
    def test_no_slots_populated_returns_blank(self):
        assert li.compute_euphony_slots("", "", "", "", "", "", "") == ""

    def test_triplet_no_euphony_anywhere_returns_blank(self):
        # ua-lexeme-0581-style triplet (ходити/йти/піти) -- no euphony data.
        result = li.compute_euphony_slots("ходи́ти", "йти", "піти́", "", "", "", "")
        assert result == ""

    def test_doublet_euphony_only_on_perfective_slot(self):
        # ua-lexeme-0115 (входити/увійти): Perfective_Euphony populated,
        # Lemma_Euphony blank. The empty Lemma segment must stay a real
        # (empty) slot, not be dropped, so positions still line up with
        # TypingTarget_UA's own " / " split on the JS side.
        result = li.compute_euphony_slots("вхо́дити", "", "уві́йти", "", "", "ввійти́", "")
        assert result == " / ввійти́"

    def test_doublet_euphony_on_both_slots(self):
        # ua-lexeme-0124 (уїжджати/уїхати): both Lemma_Euphony and
        # Perfective_Euphony populated.
        result = li.compute_euphony_slots(
            "уїжджа́ти", "", "уї́хати", "уїжджа́ти", "", "уї́хати", "",
        )
        assert result == "уїжджа́ти / уї́хати"

    def test_singlet_legacy_euphony_note_fallback(self):
        # A singlet authored before the per-slot fields existed (old-style
        # bare EuphonyNote, e.g. ua-lexeme-0211/0377 вболівати) must keep
        # its tolerance.
        result = li.compute_euphony_slots("вболіва́ти", "", "", "", "", "", "уболіва́ти")
        assert result == "уболіва́ти"

    def test_singlet_with_own_field_ignores_legacy_note(self):
        # Once a singlet has its own Lemma_Euphony populated (e.g.
        # ua-lexeme-0153 вболівальник), that's authoritative -- the
        # EuphonyNote fallback only applies when the one populated slot has
        # nothing of its own.
        result = li.compute_euphony_slots(
            "вболіва́льник", "", "", "уболіва́льник", "", "", "якесь інше пояснення",
        )
        assert result == "уболіва́льник"

    def test_euphony_ignored_when_primary_slot_empty(self):
        # Defensive: a *_Euphony value on an unpopulated slot must not leak
        # into the join.
        result = li.compute_euphony_slots("вболіва́ти", "", "", "", "", "щось", "")
        assert "щось" not in result


class TestComputeUaEnDisplay:
    def test_no_slots_populated_returns_blank(self):
        assert li.compute_ua_en_display("", "", "", "", "", "") == ""

    def test_triplet_no_euphony_matches_typing_target_join(self):
        result = li.compute_ua_en_display("ходи́ти", "йти", "піти́", "", "", "")
        assert result == "ходи́ти / йти / піти́"

    def test_doublet_euphony_only_on_perfective_slot(self):
        # ua-lexeme-0115: only the Perfective slot gets a parenthetical.
        result = li.compute_ua_en_display("вхо́дити", "", "уві́йти", "", "", "ввійти́")
        assert result == "вхо́дити / уві́йти (ввійти́)"

    def test_singlet_with_euphony_gets_parenthetical(self):
        result = li.compute_ua_en_display("вболіва́льник", "", "", "уболіва́льник", "", "")
        assert result == "вболіва́льник (уболіва́льник)"

    def test_euphony_ignored_when_primary_slot_empty(self):
        result = li.compute_ua_en_display("вболіва́ти", "", "", "", "", "щось")
        assert "щось" not in result


# ---------------------------------------------------------------------------
# prune_orphans safety gate
# ---------------------------------------------------------------------------


def _forbid_call(*args, **kwargs):
    raise AssertionError("should not be called when the safety gate aborts")


class TestPruneOrphansSafetyGate:
    def test_aborts_when_sync_errors_nonzero(self, monkeypatch):
        monkeypatch.setattr(li, "collect_all_corpus_note_ids", _forbid_call)
        monkeypatch.setattr(li, "all_anki_note_ids", _forbid_call)
        monkeypatch.setattr(li, "delete_notes", _forbid_call)
        assert li.prune_orphans(dry_run=True, sync_errors=1) == 0

    def test_aborts_when_corpus_has_parse_failures(self, monkeypatch):
        monkeypatch.setattr(
            li, "collect_all_corpus_note_ids",
            lambda: ({"ua-lexeme-0001"}, [Path("bad.md")]),
        )
        monkeypatch.setattr(li, "all_anki_note_ids", _forbid_call)
        monkeypatch.setattr(li, "delete_notes", _forbid_call)
        assert li.prune_orphans(dry_run=True, sync_errors=0) == 0

    def test_no_orphans_deletes_nothing(self, monkeypatch):
        monkeypatch.setattr(
            li, "collect_all_corpus_note_ids",
            lambda: ({"ua-lexeme-0001", "ua-lexeme-0002"}, []),
        )
        monkeypatch.setattr(
            li, "all_anki_note_ids",
            lambda: {"ua-lexeme-0001": 111, "ua-lexeme-0002": 222},
        )
        calls = []
        monkeypatch.setattr(li, "delete_notes", lambda ids, dry_run: calls.append((ids, dry_run)))
        assert li.prune_orphans(dry_run=False, sync_errors=0) == 0
        assert calls == []

    def test_orphan_present_dry_run_reports_but_does_not_delete(self, monkeypatch):
        monkeypatch.setattr(
            li, "collect_all_corpus_note_ids",
            lambda: ({"ua-lexeme-0001"}, []),
        )
        monkeypatch.setattr(
            li, "all_anki_note_ids",
            lambda: {"ua-lexeme-0001": 111, "ua-lexeme-0225": 225},
        )
        calls = []
        monkeypatch.setattr(li, "delete_notes", lambda ids, dry_run: calls.append((ids, dry_run)))
        result = li.prune_orphans(dry_run=True, sync_errors=0)
        assert result == 1
        assert calls == [([225], True)]

    def test_orphan_present_real_run_deletes_mapped_anki_id(self, monkeypatch):
        monkeypatch.setattr(
            li, "collect_all_corpus_note_ids",
            lambda: ({"ua-lexeme-0001"}, []),
        )
        monkeypatch.setattr(
            li, "all_anki_note_ids",
            lambda: {"ua-lexeme-0001": 111, "ua-lexeme-0225": 225},
        )
        calls = []
        monkeypatch.setattr(li, "delete_notes", lambda ids, dry_run: calls.append((ids, dry_run)))
        result = li.prune_orphans(dry_run=False, sync_errors=0)
        assert result == 1
        assert calls == [([225], False)]
