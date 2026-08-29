"""
tests/ua/test_release_wave.py

Unit tests for tools/anki/release_wave.py's pure logic: release_plan.yaml
validation (load_plan), tag-glob matching (matches_group), CNSF tag/id
parsing (note_tags/note_id), and the promotion transform (apply_promotion).

Added 2026-08-29 alongside the `type: relearn` field and relearn:pending
tagging -- this script previously had no automated coverage at all (only
manual --dry-run verification), so a future edit to the promotion or
relearn-tagging logic could regress silently. The actual file-scanning and
promotion loop in main() (glob the note tree, sort, slice by batch_size,
write files) stays untested here for the same reason release_wave.py's own
top-level flow always has been -- it's thin glue around the functions below,
which is where the real risk of a silent bug lives.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.release_wave import (  # noqa: E402
    apply_promotion,
    count_blocked_on_verification,
    eligible_candidates,
    load_plan,
    matches_group,
    note_id,
    note_tags,
)

NOTE_TEXT = """---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-0001
tags:
- domain:ua
- status:verified
- release:pending
fields:
  NoteID: ua-lexeme-0001
---
"""


class TestNoteTagsAndId:
    def test_note_tags_parses_list(self):
        assert note_tags(NOTE_TEXT) == ["domain:ua", "status:verified", "release:pending"]

    def test_note_tags_no_block_returns_empty(self):
        assert note_tags("schema: cnsf/v0\n") == []

    def test_note_id_parses(self):
        assert note_id(NOTE_TEXT, "fallback") == "ua-lexeme-0001"

    def test_note_id_falls_back(self):
        assert note_id("no id here", "ua-lexeme-9999") == "ua-lexeme-9999"


class TestMatchesGroup:
    def test_exact_tag_matches(self):
        assert matches_group(["ch:1.5.2"], ["ch:1.5.*"]) is True

    def test_no_match(self):
        assert matches_group(["ch:2.5.2"], ["ch:1.5.*"]) is False

    def test_matches_any_of_multiple_patterns(self):
        assert matches_group(["ch:2.3.1"], ["ch:1.*", "ch:2.3.*"]) is True

    def test_matches_any_of_multiple_tags(self):
        assert matches_group(["domain:ua", "ch:1.5.2"], ["ch:1.5.*"]) is True


class TestApplyPromotion:
    def test_plain_promotion_flips_pending_to_active(self):
        new_text, relearn_tagged = apply_promotion(NOTE_TEXT, relearn=False)
        assert "- release:pending\n" not in new_text
        assert "- release:active\n" in new_text
        assert "relearn:pending" not in new_text
        assert relearn_tagged is False

    def test_relearn_promotion_also_tags_relearn_pending(self):
        new_text, relearn_tagged = apply_promotion(NOTE_TEXT, relearn=True)
        assert "- release:active\n" in new_text
        assert "- relearn:pending\n" in new_text
        assert relearn_tagged is True

    def test_relearn_tag_lands_immediately_after_active(self):
        new_text, _ = apply_promotion(NOTE_TEXT, relearn=True)
        lines = new_text.splitlines()
        active_idx = lines.index("- release:active")
        assert lines[active_idx + 1] == "- relearn:pending"

    def test_relearn_promotion_is_idempotent_if_already_tagged(self):
        # Simulates a note that somehow already carries relearn:pending
        # (shouldn't happen via the normal flow, but must not double-tag).
        already_tagged = NOTE_TEXT.replace(
            "- release:pending\n", "- release:pending\n- relearn:pending\n"
        )
        new_text, relearn_tagged = apply_promotion(already_tagged, relearn=True)
        assert new_text.count("relearn:pending") == 1
        assert relearn_tagged is False


class TestLoadPlan:
    def _write_plan(self, tmp_path: Path, body: str) -> Path:
        p = tmp_path / "release_plan.yaml"
        p.write_text(body, encoding="utf-8")
        return p

    def test_valid_plan_loads(self, tmp_path):
        p = self._write_plan(tmp_path, """
groups:
  - name: "L1"
    match: ["ch:1.*"]
    batch_size: 10
""")
        groups = load_plan(p)
        assert len(groups) == 1
        assert groups[0]["name"] == "L1"

    def test_valid_relearn_type_loads(self, tmp_path):
        p = self._write_plan(tmp_path, """
groups:
  - name: "L2 backlog"
    type: relearn
    match: ["ch:2.1.*"]
    batch_size: 0
""")
        groups = load_plan(p)
        assert groups[0]["type"] == "relearn"

    def test_missing_plan_file_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            load_plan(tmp_path / "nope.yaml")

    def test_missing_required_field_exits(self, tmp_path):
        p = self._write_plan(tmp_path, """
groups:
  - name: "L1"
    match: ["ch:1.*"]
""")
        with pytest.raises(SystemExit):
            load_plan(p)

    def test_empty_match_list_exits(self, tmp_path):
        p = self._write_plan(tmp_path, """
groups:
  - name: "L1"
    match: []
    batch_size: 10
""")
        with pytest.raises(SystemExit):
            load_plan(p)

    def test_negative_batch_size_exits(self, tmp_path):
        p = self._write_plan(tmp_path, """
groups:
  - name: "L1"
    match: ["ch:1.*"]
    batch_size: -1
""")
        with pytest.raises(SystemExit):
            load_plan(p)

    def test_unknown_type_value_exits(self, tmp_path):
        # Regression guard for the type-field validation added 2026-08-29 --
        # a typo like `type: relearning` should fail loudly, not silently
        # behave like an ordinary (non-relearn) group.
        p = self._write_plan(tmp_path, """
groups:
  - name: "L1"
    type: relearning
    match: ["ch:1.*"]
    batch_size: 10
""")
        with pytest.raises(SystemExit):
            load_plan(p)

    def test_no_groups_key_returns_empty_list(self, tmp_path):
        p = self._write_plan(tmp_path, "{}\n")
        assert load_plan(p) == []


class TestEligibleCandidates:
    """status:verified is required for promotion, added 2026-08-29 after a
    real run promoted 21 still-draft notes to release:active. Regression
    coverage for that gate.
    """

    def _row(self, path, note_id_, tags, text=NOTE_TEXT):
        return (Path(path), note_id_, tags, text)

    def test_verified_and_pending_is_eligible(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:verified", "ch:1.1.1"])]
        result = eligible_candidates(parsed, ["ch:1.1.*"], set())
        assert [nid for _, nid, _ in result] == ["ua-lexeme-0001"]

    def test_pending_but_draft_is_excluded(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:draft", "ch:1.1.1"])]
        assert eligible_candidates(parsed, ["ch:1.1.*"], set()) == []

    def test_verified_but_not_pending_is_excluded(self):
        # Already active -- nothing to promote.
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:active", "status:verified", "ch:1.1.1"])]
        assert eligible_candidates(parsed, ["ch:1.1.*"], set()) == []

    def test_non_matching_tags_excluded(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:verified", "ch:2.1.1"])]
        assert eligible_candidates(parsed, ["ch:1.1.*"], set()) == []

    def test_already_promoted_this_run_excluded(self):
        fp = Path("a.md")
        parsed = [(fp, "ua-lexeme-0001", ["release:pending", "status:verified", "ch:1.1.1"], NOTE_TEXT)]
        assert eligible_candidates(parsed, ["ch:1.1.*"], {fp}) == []

    def test_sorted_by_note_id(self):
        parsed = [
            self._row("b.md", "ua-lexeme-0099", ["release:pending", "status:verified", "ch:1.1.1"]),
            self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:verified", "ch:1.1.1"]),
        ]
        result = eligible_candidates(parsed, ["ch:1.1.*"], set())
        assert [nid for _, nid, _ in result] == ["ua-lexeme-0001", "ua-lexeme-0099"]


class TestCountBlockedOnVerification:
    def _row(self, path, note_id_, tags, text=NOTE_TEXT):
        return (Path(path), note_id_, tags, text)

    def test_counts_pending_draft_matches(self):
        parsed = [
            self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:draft", "ch:1.1.1"]),
            self._row("b.md", "ua-lexeme-0002", ["release:pending", "status:draft", "ch:1.1.2"]),
        ]
        assert count_blocked_on_verification(parsed, ["ch:1.1.*"]) == 2

    def test_verified_notes_not_counted(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:verified", "ch:1.1.1"])]
        assert count_blocked_on_verification(parsed, ["ch:1.1.*"]) == 0

    def test_already_active_not_counted(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:active", "status:draft", "ch:1.1.1"])]
        assert count_blocked_on_verification(parsed, ["ch:1.1.*"]) == 0

    def test_non_matching_not_counted(self):
        parsed = [self._row("a.md", "ua-lexeme-0001", ["release:pending", "status:draft", "ch:2.1.1"])]
        assert count_blocked_on_verification(parsed, ["ch:1.1.*"]) == 0
