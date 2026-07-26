"""
tests/ua/test_list_unverified.py

Unit tests for tools/anki/inspect/list_unverified.py.

Covers:
  - _reasons(): the three signals (stress:unverified, status:draft, no status tag)
    and their combinations
  - find_unverified(): scanning a fixture corpus, verified-clean notes excluded
  - collect(): multiple note types aggregated
  - print_report(): smoke test that it runs without error and mentions expected notes
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.inspect.list_unverified import (  # noqa: E402
    _reasons,
    collect,
    find_unverified,
    print_report,
)


def _note(note_id: str, tags: list[str], lemma: str = "тест") -> str:
    tags_yaml = "\n".join(f"- {t}" for t in tags)
    return (
        "---\n"
        "schema: cnsf/v0\n"
        "note_type: ua_lexeme\n"
        f"note_id: {note_id}\n"
        "anki:\n"
        "  model: UA_Lexeme\n"
        "  deck: UA::Recognition::UA→EN\n"
        "tags:\n"
        f"{tags_yaml}\n"
        "fields:\n"
        f"  NoteID: {note_id}\n"
        f"  Lemma: {lemma}\n"
        "  EN_Gloss: test\n"
        "---\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# _reasons
# ─────────────────────────────────────────────────────────────────────────────


class TestReasons:
    def test_verified_no_stress_flag_is_clean(self):
        assert _reasons(["domain:ua", "status:verified"]) == []

    def test_stress_unverified_flagged(self):
        assert _reasons(["status:verified", "stress:unverified"]) == ["stress:unverified"]

    def test_status_draft_flagged(self):
        assert _reasons(["status:draft"]) == ["status:draft"]

    def test_no_status_tag_flagged(self):
        assert _reasons(["domain:ua"]) == ["no status tag"]

    def test_both_stress_and_draft_flagged_together(self):
        assert _reasons(["status:draft", "stress:unverified"]) == ["stress:unverified", "status:draft"]

    def test_draft_and_verified_both_present_prefers_draft_not_no_status(self):
        # Malformed/legacy data with both tags -- status:draft still wins the
        # "which reason" label; it should not also claim "no status tag".
        result = _reasons(["status:draft", "status:verified"])
        assert result == ["status:draft"]
        assert "no status tag" not in result


# ─────────────────────────────────────────────────────────────────────────────
# find_unverified / collect
# ─────────────────────────────────────────────────────────────────────────────


class TestFindUnverified:
    def _corpus(self, tmp_path: Path) -> Path:
        root = tmp_path / "lexemes" / "ch-09"
        root.mkdir(parents=True)
        (root / "ua-lexeme-0001.md").write_text(
            _note("ua-lexeme-0001", ["status:verified"], lemma="добре"), encoding="utf-8"
        )
        (root / "ua-lexeme-0002.md").write_text(
            _note("ua-lexeme-0002", ["status:verified", "stress:unverified"], lemma="непогано"),
            encoding="utf-8",
        )
        (root / "ua-lexeme-0003.md").write_text(
            _note("ua-lexeme-0003", ["status:draft"], lemma="чудово"), encoding="utf-8"
        )
        (root / "ua-lexeme-0004.md").write_text(
            _note("ua-lexeme-0004", ["domain:ua"], lemma="нормально"), encoding="utf-8"
        )
        return tmp_path / "lexemes"

    def test_verified_clean_note_excluded(self, tmp_path):
        root = self._corpus(tmp_path)
        results = find_unverified("ua_lexeme", root, "ua-lexeme-*.md")
        ids = {r["note_id"] for r in results}
        assert "ua-lexeme-0001" not in ids

    def test_three_unverified_notes_found(self, tmp_path):
        root = self._corpus(tmp_path)
        results = find_unverified("ua_lexeme", root, "ua-lexeme-*.md")
        assert len(results) == 3
        ids = {r["note_id"] for r in results}
        assert ids == {"ua-lexeme-0002", "ua-lexeme-0003", "ua-lexeme-0004"}

    def test_reasons_attached_correctly(self, tmp_path):
        root = self._corpus(tmp_path)
        results = {r["note_id"]: r for r in find_unverified("ua_lexeme", root, "ua-lexeme-*.md")}
        assert results["ua-lexeme-0002"]["reasons"] == ["stress:unverified"]
        assert results["ua-lexeme-0003"]["reasons"] == ["status:draft"]
        assert results["ua-lexeme-0004"]["reasons"] == ["no status tag"]

    def test_lemma_label_populated(self, tmp_path):
        root = self._corpus(tmp_path)
        results = {r["note_id"]: r for r in find_unverified("ua_lexeme", root, "ua-lexeme-*.md")}
        assert results["ua-lexeme-0002"]["label"] == "непогано"

    def test_missing_root_returns_empty(self, tmp_path):
        assert find_unverified("ua_lexeme", tmp_path / "does-not-exist", "*.md") == []

    def test_collect_scopes_to_requested_types(self, tmp_path, monkeypatch):
        import tools.anki.inspect.list_unverified as lu

        lexeme_root = self._corpus(tmp_path)
        verb_root = tmp_path / "verbs"
        verb_root.mkdir()
        (verb_root / "ua-verb-0001.md").write_text(
            _note("ua-verb-0001", ["stress:unverified"], lemma="ходити"), encoding="utf-8"
        )
        monkeypatch.setitem(lu.NOTE_ROOTS, "ua_lexeme", (lexeme_root, "ua-lexeme-*.md"))
        monkeypatch.setitem(lu.NOTE_ROOTS, "ua_verb", (verb_root, "ua-verb-*.md"))

        lexeme_only = collect(["ua_lexeme"])
        assert {r["note_type"] for r in lexeme_only} == {"ua_lexeme"}

        both = collect(["ua_lexeme", "ua_verb"])
        assert {r["note_type"] for r in both} == {"ua_lexeme", "ua_verb"}
        assert len(both) == 4  # 3 lexeme + 1 verb


# ─────────────────────────────────────────────────────────────────────────────
# print_report — smoke test
# ─────────────────────────────────────────────────────────────────────────────


class TestPrintReport:
    def test_empty_results_prints_clean_message(self, capsys):
        print_report([])
        out = capsys.readouterr().out
        assert "Nothing unverified" in out

    def test_nonempty_results_lists_each_note(self, capsys, tmp_path):
        results = [
            {
                "note_type": "ua_lexeme",
                "note_id": "ua-lexeme-0002",
                "label": "непогано",
                "reasons": ["stress:unverified"],
                "path": tmp_path / "ua-lexeme-0002.md",
            }
        ]
        print_report(results)
        out = capsys.readouterr().out
        assert "ua-lexeme-0002" in out
        assert "непогано" in out
        assert "stress:unverified" in out
        assert "Total: 1 unverified" in out
