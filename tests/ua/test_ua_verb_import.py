"""
tests/ua/test_ua_verb_import.py

Unit tests for tools/anki/sync/ua_verb_import.py's suspension policy
(should_suspend). Everything else in this module talks to AnkiConnect directly
and isn't practically unit-testable without a live Anki instance -- this is the
one piece of pure decision logic worth covering.

Per Option A refactoring (2026-08-25), stress:unverified is decoupled from
suspension logic. The conj:drill/conj:suspended curation axis was removed
2026-08-27 (per Craig): all status:verified verbs are now meant to be actively
drillable, not just a hand-picked set of class leaders, since class leaders
trickle in gradually as older chapters get backfilled. Suspension is now based
purely on status:draft.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.sync.ua_verb_import import should_suspend  # noqa: E402


class TestShouldSuspend:
    """Test the should_suspend() decision logic.

    Single suspend axis as of 2026-08-27: status:draft. stress:unverified
    no longer suspends (Option A, 2026-08-25); conj:suspended no longer
    suspends (2026-08-27 removal of the conj: curation axis).
    """

    def test_verified_no_flags_unsuspends(self):
        assert should_suspend(["domain:ua", "status:verified"]) is False

    def test_status_draft_suspends(self):
        assert should_suspend(["domain:ua", "status:draft"]) is True

    def test_conj_suspended_tag_no_longer_suspends(self):
        # The conj:drill/conj:suspended axis was removed 2026-08-27 -- a
        # verified verb stays active for drilling even if a stray
        # conj:suspended tag is still present on the note.
        assert should_suspend(["domain:ua", "status:verified", "conj:suspended"]) is False

    def test_status_verified_and_stress_unverified_does_not_suspend(self):
        # A verb can carry unconfirmed stress marks but still be content-verified --
        # status:draft alone suspends; stress:unverified no longer does (Option A).
        assert should_suspend(["domain:ua", "status:verified", "stress:unverified"]) is False

    def test_stress_unverified_does_not_suspend(self):
        # Per Option A refactoring, stress:unverified is decoupled from suspension.
        assert should_suspend(["stress:unverified"]) is False

    def test_no_tags_unsuspends(self):
        assert should_suspend([]) is False

    def test_status_draft_suspends_regardless_of_other_tags(self):
        assert should_suspend(["status:draft", "stress:unverified", "conj:drill"]) is True
