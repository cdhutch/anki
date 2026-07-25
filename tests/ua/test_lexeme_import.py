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
# ---------------------------------------------------------------------------


class TestComputeTypingTarget:
    def test_singlet_returns_none(self):
        # Imperfective-only verb, e.g. мати -- no aspectual counterpart.
        assert li.compute_typing_target("ма́ти", "", "") is None

    def test_doublet_lemma_and_perfective(self):
        result = li.compute_typing_target("перекида́ти", "", "переки́нути")
        assert result is not None
        stressed, unstressed = result
        assert stressed == "перекида́ти / переки́нути"
        assert unstressed == "перекидати / перекинути"

    def test_doublet_lemma_and_impf_uni_no_double_slash(self):
        # Middle slot (impf_uni) populated, perfective empty -- must not leave
        # a trailing " / " artifact.
        result = li.compute_typing_target("ходи́ти", "йти", "")
        assert result is not None
        stressed, unstressed = result
        assert stressed == "ходи́ти / йти"
        assert "//" not in stressed
        assert not stressed.endswith("/")

    def test_triplet_all_three_slots_in_order(self):
        result = li.compute_typing_target("ходи́ти", "йти", "піти́")
        assert result is not None
        stressed, unstressed = result
        assert stressed == "ходи́ти / йти / піти́"
        assert unstressed == "ходити / йти / піти"

    def test_missing_lemma_still_joins_remaining_two(self):
        # Defensive case -- Lemma should always be populated in practice, but
        # the function only counts populated slots, order-preserving.
        result = li.compute_typing_target("", "йти", "піти́")
        assert result is not None
        stressed, _ = result
        assert stressed == "йти / піти́"


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
