"""
tests/ua/test_build_lexeme_index.py

Unit tests for tools/anki/inspect/build_lexeme_index.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.inspect.build_lexeme_index import (  # noqa: E402
    COLUMNS,
    build_rows,
    write_tsv,
)


def _note(note_id: str, lemma: str, gloss: str, *, confusable="", extra_tags=None, homograph=False) -> str:
    tags = ["domain:ua", "ch:2.9.1"] + (extra_tags or [])
    if homograph:
        tags.append("homograph:true")
    tags_yaml = "\n".join(f"- {t}" for t in tags)
    return (
        "---\n"
        "schema: cnsf/v0\n"
        "note_type: ua_lexeme\n"
        f"note_id: {note_id}\n"
        "anki:\n  model: UA_Lexeme\n  deck: UA::Recognition::UA→EN\n"
        f"tags:\n{tags_yaml}\n"
        "fields:\n"
        f"  NoteID: {note_id}\n"
        f"  Lemma: {lemma}\n"
        "  PartOfSpeech: noun\n"
        "  Gender: m\n"
        f"  EN_Gloss: {gloss}\n"
        f"  ConfusableSet: '{confusable}'\n"
        "  Tags_Ch: ch:2.9.1\n"
        "---\n"
    )


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "lexemes" / "ch-x"
    root.mkdir(parents=True)
    (root / "ua-lexeme-0001.md").write_text(_note("ua-lexeme-0001", "перего́ни", "races"), encoding="utf-8")
    (root / "ua-lexeme-0002.md").write_text(
        _note("ua-lexeme-0002", "коса́", "braid", homograph=True, confusable="scythe cross-link"),
        encoding="utf-8",
    )
    (root / "ua-lexeme-0003.md").write_text(
        _note("ua-lexeme-0003", "коса́", "scythe", homograph=True, confusable="braid cross-link"),
        encoding="utf-8",
    )
    return root.parent


class TestBuildRows:
    def test_row_count_matches_notes(self, corpus):
        rows = build_rows(corpus)
        assert len(rows) == 3

    def test_lemma_stripped_computed(self, corpus):
        rows = build_rows(corpus)
        by_id = {r["NoteID"]: r for r in rows}
        assert by_id["ua-lexeme-0001"]["LemmaStripped"] == "перегони"

    def test_homograph_flag_set(self, corpus):
        rows = build_rows(corpus)
        by_id = {r["NoteID"]: r for r in rows}
        assert by_id["ua-lexeme-0002"]["Homograph"] == "yes"
        assert by_id["ua-lexeme-0001"]["Homograph"] == ""

    def test_gloss_captured(self, corpus):
        rows = build_rows(corpus)
        by_id = {r["NoteID"]: r for r in rows}
        assert by_id["ua-lexeme-0003"]["EN_Gloss"] == "scythe"

    def test_two_notes_share_stripped_lemma(self, corpus):
        rows = build_rows(corpus)
        stripped = [r["LemmaStripped"] for r in rows]
        assert stripped.count("коса") == 2

    def test_malformed_note_skipped_not_fatal(self, tmp_path):
        root = tmp_path / "lexemes"
        root.mkdir()
        (root / "ua-lexeme-0001.md").write_text("not valid cnsf at all", encoding="utf-8")
        (root / "ua-lexeme-0002.md").write_text(_note("ua-lexeme-0002", "слово", "word"), encoding="utf-8")
        rows = build_rows(root)
        assert len(rows) == 1
        assert rows[0]["NoteID"] == "ua-lexeme-0002"

    def test_empty_corpus(self, tmp_path):
        root = tmp_path / "empty"
        root.mkdir()
        assert build_rows(root) == []


class TestWriteTsv:
    def test_header_matches_columns(self, corpus, tmp_path):
        rows = build_rows(corpus)
        out = tmp_path / "idx.tsv"
        write_tsv(rows, out)
        header = out.read_text(encoding="utf-8").splitlines()[0]
        assert header.split("\t") == COLUMNS

    def test_row_count_plus_header(self, corpus, tmp_path):
        rows = build_rows(corpus)
        out = tmp_path / "idx.tsv"
        write_tsv(rows, out)
        lines = out.read_text(encoding="utf-8").splitlines()
        assert len(lines) == len(rows) + 1

    def test_embedded_newline_collapsed(self, tmp_path):
        rows = [
            {c: "" for c in COLUMNS} | {"NoteID": "x", "EN_Gloss": "line1\nline2"}
        ]
        out = tmp_path / "idx.tsv"
        write_tsv(rows, out)
        text = out.read_text(encoding="utf-8")
        assert "\n\n" not in text  # no stray blank-line-producing raw newline mid-cell
        assert "line1 \\n line2" in text

    def test_creates_parent_dir(self, corpus, tmp_path):
        rows = build_rows(corpus)
        out = tmp_path / "nested" / "dir" / "idx.tsv"
        write_tsv(rows, out)
        assert out.exists()
