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
trickle in gradually as older chapters get backfilled.

release: added 2026-08-29 (per Craig) as a second, independent gate alongside
status. status tracks content-quality/review state; release tracks study-
pacing -- whether a verified note has actually been let into rotation yet, so
a large freshly-authored backlog can sit verified-but-suspended until Craig
releases it in controlled batches. Unsuspending now requires BOTH
status:verified AND release:active (AND gate); either one missing suspends,
so a note with no release tag at all fails closed (suspended).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.sync.ua_verb_import import should_suspend  # noqa: E402


class TestShouldSuspend:
    """Test the should_suspend() decision logic.

    Two-axis AND gate as of 2026-08-29: status:verified AND release:active
    both required to unsuspend. stress:unverified no longer suspends
    (Option A, 2026-08-25); conj:suspended no longer suspends (2026-08-27
    removal of the conj: curation axis).
    """

    def test_verified_and_active_unsuspends(self):
        assert should_suspend(["domain:ua", "status:verified", "release:active"]) is False

    def test_verified_without_release_tag_suspends(self):
        # AND gate fails closed: verified content not yet released stays suspended.
        assert should_suspend(["domain:ua", "status:verified"]) is True

    def test_verified_with_release_pending_suspends(self):
        assert should_suspend(["domain:ua", "status:verified", "release:pending"]) is True

    def test_status_draft_suspends(self):
        assert should_suspend(["domain:ua", "status:draft"]) is True

    def test_status_draft_suspends_even_with_release_active(self):
        # Both axes must clear; status:draft alone still suspends.
        assert should_suspend(["domain:ua", "status:draft", "release:active"]) is True

    def test_conj_suspended_tag_no_longer_suspends(self):
        # The conj:drill/conj:suspended axis was removed 2026-08-27 -- a
        # verified, released verb stays active for drilling even if a stray
        # conj:suspended tag is still present on the note.
        assert should_suspend(
            ["domain:ua", "status:verified", "release:active", "conj:suspended"]
        ) is False

    def test_status_verified_and_stress_unverified_does_not_suspend(self):
        # A verb can carry unconfirmed stress marks but still be content-verified
        # and released -- stress:unverified never suspends (Option A).
        assert should_suspend(
            ["domain:ua", "status:verified", "release:active", "stress:unverified"]
        ) is False

    def test_stress_unverified_alone_suspends(self):
        # Per Option A refactoring, stress:unverified is decoupled from suspension --
        # but with no status:verified/release:active present, the AND gate still fails.
        assert should_suspend(["stress:unverified"]) is True

    def test_no_tags_suspends(self):
        # Fail closed: nothing asserts verified+active, so a bare/untagged note
        # stays suspended rather than defaulting to active.
        assert should_suspend([]) is True

    def test_status_draft_suspends_regardless_of_other_tags(self):
        assert should_suspend(["status:draft", "stress:unverified", "conj:drill"]) is True
