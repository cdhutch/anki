"""
tests/ua/test_seed_mature_interval.py

Unit tests for tools/anki/seed_mature_interval.py's pure file-parsing and
selection logic (note_tags, note_id, gather_candidates). The AnkiConnect
calls (find_cards_by_template, the setDueDate writes in main()) aren't
practically unit-testable without a live Anki instance, same rationale as
test_pvom_infinitive_import.py's TestShouldSuspend docstring -- this covers
the one part that's pure decision logic and where a selection-criteria bug
would either seed a note that shouldn't be touched yet, or silently skip one
that should have been, neither of which AnkiConnect would ever surface as an
error.

Added 2026-08-29 alongside the relearn:pending -> relearn:seeded mature-
interval-seeding feature (see release_wave.py's `type: relearn` groups).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.seed_mature_interval import (  # noqa: E402
    gather_candidates,
    note_id,
    note_tags,
)

NOTE_TEMPLATE = """---
schema: cnsf/v0
note_type: ua_lexeme
note_id: {nid}
anki:
  model: UA_Lexeme
  deck: UA::Recognition::UA→EN
tags:
{tags}
fields:
  NoteID: {nid}
  Lemma: приклад
---
"""


def write_note(dir_: Path, nid: str, tags: list[str]) -> Path:
    tag_block = "\n".join(f"- {t}" for t in tags)
    fp = dir_ / f"{nid}.md"
    fp.write_text(NOTE_TEMPLATE.format(nid=nid, tags=tag_block), encoding="utf-8")
    return fp


class TestNoteTags:
    def test_parses_tag_list(self):
        text = NOTE_TEMPLATE.format(
            nid="ua-lexeme-0001",
            tags="- domain:ua\n- status:verified\n- release:active",
        )
        assert note_tags(text) == ["domain:ua", "status:verified", "release:active"]

    def test_no_tags_block_returns_empty(self):
        assert note_tags("schema: cnsf/v0\nfields:\n  NoteID: x\n") == []


class TestNoteId:
    def test_parses_note_id(self):
        text = NOTE_TEMPLATE.format(nid="ua-lexeme-0042", tags="- domain:ua")
        assert note_id(text, "fallback") == "ua-lexeme-0042"

    def test_falls_back_when_missing(self):
        assert note_id("no note_id line here", "ua-lexeme-9999") == "ua-lexeme-9999"


class TestGatherCandidates:
    def test_relearn_pending_and_active_is_eligible(self, tmp_path):
        write_note(
            tmp_path, "ua-lexeme-0001",
            ["domain:ua", "status:verified", "release:active", "relearn:pending"],
        )
        candidates = gather_candidates(tmp_path)
        assert [nid for _, nid, _ in candidates] == ["ua-lexeme-0001"]

    def test_already_seeded_is_excluded(self, tmp_path):
        write_note(
            tmp_path, "ua-lexeme-0002",
            ["domain:ua", "status:verified", "release:active", "relearn:seeded"],
        )
        assert gather_candidates(tmp_path) == []

    def test_no_relearn_tag_is_excluded(self, tmp_path):
        # Ordinary release:active note from a non-relearn group -- never
        # touched by this script.
        write_note(
            tmp_path, "ua-lexeme-0003",
            ["domain:ua", "status:verified", "release:active"],
        )
        assert gather_candidates(tmp_path) == []

    def test_relearn_pending_but_still_release_pending_is_excluded(self, tmp_path):
        # Shouldn't normally happen (release_wave.py sets both tags in the
        # same write), but the gate must fail closed if it ever does -- a
        # note not yet unsuspended in Anki has nothing to seed.
        write_note(
            tmp_path, "ua-lexeme-0004",
            ["domain:ua", "status:verified", "release:pending", "relearn:pending"],
        )
        assert gather_candidates(tmp_path) == []

    def test_release_active_but_still_status_draft_is_excluded(self, tmp_path):
        # Regression guard, added 2026-08-29 after a real release_wave.py
        # run promoted a still-draft note to release:active (it promotes
        # purely on tag-glob match, never checks status:) and the seeder
        # then seeded it anyway -- 21 notes affected in one run. A
        # release:active + status:draft note is still suspended in Anki
        # under the AND-gate, so seeding its due date would be wasted: the
        # interval may elapse before the note is ever verified and
        # actually unsuspended.
        write_note(
            tmp_path, "ua-lexeme-0008",
            ["domain:ua", "status:draft", "release:active", "relearn:pending"],
        )
        assert gather_candidates(tmp_path) == []

    def test_mixed_directory_only_returns_eligible_notes(self, tmp_path):
        write_note(
            tmp_path, "ua-lexeme-0005",
            ["domain:ua", "status:verified", "release:active", "relearn:pending"],
        )
        write_note(
            tmp_path, "ua-lexeme-0006",
            ["domain:ua", "status:verified", "release:active"],
        )
        write_note(
            tmp_path, "ua-lexeme-0007",
            ["domain:ua", "status:verified", "release:active", "relearn:seeded"],
        )
        candidates = gather_candidates(tmp_path)
        assert [nid for _, nid, _ in candidates] == ["ua-lexeme-0005"]
