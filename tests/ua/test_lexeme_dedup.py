"""
tests/ua/test_lexeme_dedup.py

Unit and integration tests for tools/anki/lib/lexeme_dedup.py.

Covers:
  - strip_stress
  - load_corpus / check_dedup (index building, exact-spelling matching)
  - create_or_link_lexeme:
      * bucket "new"        — no collision, writes a new note
      * bucket "duplicate"  — collision, edits existing note(s) in place
      * bucket "homograph"  — collision, writes new note + cross-links existing
      * decision/corpus-state mismatches all raise DedupError
  - next_note_id
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.lib.lexeme_dedup import (  # noqa: E402
    DedupError,
    DedupMatch,
    check_dedup,
    create_or_link_lexeme,
    load_corpus,
    next_note_id,
    strip_stress,
)

STRESS = "́"  # U+0301 COMBINING ACUTE ACCENT


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures / helpers
# ─────────────────────────────────────────────────────────────────────────────


def _yaml_scalar(s: str) -> str:
    """Single-quoted YAML scalar, or '' for empty string. Only valid for
    single-line values — a raw embedded newline in a single-quoted scalar
    folds to a space on parse, it does not round-trip. Use _field_line() for
    any value that might contain "\\n"."""
    if not s:
        return "''"
    return "'" + s.replace("'", "''") + "'"


def _field_line(key: str, value: str, indent: str = "  ") -> str:
    """Render one `key: value` frontmatter line. Multi-line values use YAML
    literal-block (`|`) style so embedded newlines round-trip correctly —
    matches how lexeme_dedup.py's own _dump_yaml() forces literal-block style
    for multi-line strings."""
    if not value:
        return f"{indent}{key}: ''\n"
    if "\n" in value:
        body = "\n".join(f"{indent}  {line}" for line in value.split("\n"))
        return f"{indent}{key}: |-\n{body}\n"
    return f"{indent}{key}: {_yaml_scalar(value)}\n"


def _note_text(
    note_id: str,
    lemma: str,
    *,
    gloss: str = "test gloss",
    tags: list[str] | None = None,
    tags_ch: str = "ch:2.9.1",
    confusable: str = "",
    verification_notes: str = "",
    pos: str = "noun",
) -> str:
    tags = tags if tags is not None else ["domain:ua", "topic:vocabulary", "ch:2.9.1"]
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
        f"  PartOfSpeech: {pos}\n"
        "  Gender: m\n"
        "  Perfective: ''\n"
        f"  EN_Gloss: {gloss}\n"
        "  Govt_Case: ''\n"
        "  CounterpartForm: ''\n"
        "  IrregularForms: ''\n"
        "  VerbMotion_Pair: ''\n"
        f"{_field_line('ConfusableSet', confusable)}"
        "  Mnemonic_EN: ''\n"
        "  CrossLang_Analog: ''\n"
        "  EuphonyNote: ''\n"
        f"  TypingAnswer: {strip_stress(lemma)}\n"
        "  UA_Example: ''\n"
        "  EN_Example: ''\n"
        "  Verb_Conj_Table: ''\n"
        f"  Tags_Ch: {tags_ch}\n"
        f"  Source_URL: https://goroh.pp.ua/Словозміна/{strip_stress(lemma)}\n"
        "  Source_Note: ''\n"
        f"{_field_line('Verification Notes', verification_notes)}"
        "---\n"
    )


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """A small isolated lexeme corpus: two subfolders, three existing notes."""
    root = tmp_path / "lexemes"
    ch09 = root / "yabluko-l2" / "ch-09"
    ch09.mkdir(parents=True)

    (ch09 / "ua-lexeme-0001.md").write_text(
        _note_text("ua-lexeme-0001", "перего́ни", gloss="races, racing (competitive)", tags_ch="ch:2.9.1"),
        encoding="utf-8",
    )
    (ch09 / "ua-lexeme-0002.md").write_text(
        _note_text("ua-lexeme-0002", "коса́", gloss="braid (hair)", tags_ch="ch:2.9.1"),
        encoding="utf-8",
    )
    (ch09 / "ua-lexeme-0003.md").write_text(
        _note_text("ua-lexeme-0003", "велосипеди́ст", gloss="cyclist", tags_ch="ch:2.9.2"),
        encoding="utf-8",
    )
    return root


# ─────────────────────────────────────────────────────────────────────────────
# strip_stress
# ─────────────────────────────────────────────────────────────────────────────


class TestStripStress:
    def test_removes_accent(self):
        assert strip_stress("перего́ни") == "перегони"

    def test_no_accent_unchanged(self):
        assert strip_stress("перегони") == "перегони"

    def test_empty(self):
        assert strip_stress("") == ""

    def test_preserves_yi_and_i_short(self):
        # NFD-decomposes й/ї too; must not lose them since only U+0301 is stripped
        assert strip_stress("ї́жак") == "їжак"
        assert "й" in strip_stress("вода́й")

    def test_double_stress_preserved(self):
        # Free/variant stress: two accent marks is valid, not garbled data
        assert strip_stress("му́зи́ка") == "музика"


# ─────────────────────────────────────────────────────────────────────────────
# load_corpus / check_dedup
# ─────────────────────────────────────────────────────────────────────────────


class TestLoadCorpus:
    def test_finds_all_notes_recursively(self, corpus):
        index = load_corpus(corpus)
        assert sum(len(v) for v in index.values()) == 3

    def test_keys_are_stress_stripped(self, corpus):
        index = load_corpus(corpus)
        assert "перегони" in index
        assert "перего́ни" not in index

    def test_match_fields_populated(self, corpus):
        index = load_corpus(corpus)
        m = index["велосипедист"][0]
        assert isinstance(m, DedupMatch)
        assert m.note_id == "ua-lexeme-0003"
        assert m.gloss == "cyclist"
        assert m.tags_ch == "ch:2.9.2"
        assert m.pos == "noun"

    def test_empty_corpus(self, tmp_path):
        empty_root = tmp_path / "empty"
        empty_root.mkdir()
        index = load_corpus(empty_root)
        assert index == {}


class TestCheckDedup:
    def test_no_match(self, corpus):
        index = load_corpus(corpus)
        result = check_dedup("нови́й", index)
        assert result.has_match is False
        assert result.matches == []

    def test_exact_match_stress_insensitive(self, corpus):
        index = load_corpus(corpus)
        result = check_dedup("перегони", index)  # candidate given without stress
        assert result.has_match is True
        assert result.matches[0].note_id == "ua-lexeme-0001"

    def test_match_with_stress_in_candidate(self, corpus):
        index = load_corpus(corpus)
        result = check_dedup("перего́ни", index)
        assert result.has_match is True

    def test_key_is_stress_stripped(self, corpus):
        index = load_corpus(corpus)
        result = check_dedup("перего́ни", index)
        assert result.key == "перегони"


# ─────────────────────────────────────────────────────────────────────────────
# create_or_link_lexeme — bucket "new"
# ─────────────────────────────────────────────────────────────────────────────


class TestCreateNew:
    def test_writes_new_file_no_collision(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-0004", "озеро", gloss="lake", tags_ch="ch:2.9.3")
        outcome = create_or_link_lexeme(
            "озеро", content, new_path, lexeme_root=corpus
        )
        assert outcome.bucket == "new"
        assert new_path.exists()
        assert outcome.written == [new_path]
        assert outcome.modified == []

    def test_explicit_new_decision_no_collision(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-0004", "озеро", gloss="lake")
        outcome = create_or_link_lexeme(
            "озеро", content, new_path, dedup_decision="new", lexeme_root=corpus
        )
        assert outcome.bucket == "new"

    def test_refuses_to_overwrite_existing_file(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0099.md"
        new_path.write_text("placeholder", encoding="utf-8")
        content = _note_text("ua-lexeme-0099", "озеро")
        with pytest.raises(DedupError):
            create_or_link_lexeme("озеро", content, new_path, lexeme_root=corpus)

    def test_note_id_mismatch_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-9999", "озеро")  # wrong note_id for path
        with pytest.raises(DedupError):
            create_or_link_lexeme("озеро", content, new_path, lexeme_root=corpus)

    def test_malformed_note_content_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        with pytest.raises(DedupError):
            create_or_link_lexeme("озеро", "not valid cnsf", new_path, lexeme_root=corpus)

    def test_reuses_prebuilt_index(self, corpus):
        index = load_corpus(corpus)
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-0004", "озеро")
        outcome = create_or_link_lexeme("озеро", content, new_path, index=index)
        assert outcome.bucket == "new"

    def test_collision_with_no_decision_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-0004", "перегони", gloss="something else")
        with pytest.raises(DedupError, match="already exists"):
            create_or_link_lexeme("перегони", content, new_path, lexeme_root=corpus)

    def test_collision_with_new_decision_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text("ua-lexeme-0004", "перегони", gloss="something else")
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "перегони", content, new_path, dedup_decision="new", lexeme_root=corpus
            )


# ─────────────────────────────────────────────────────────────────────────────
# create_or_link_lexeme — bucket "duplicate"
# ─────────────────────────────────────────────────────────────────────────────


class TestCreateDuplicate:
    def test_does_not_write_new_file(self, corpus):
        outcome = create_or_link_lexeme(
            "перегони",
            "",
            corpus / "unused.md",
            dedup_decision="duplicate",
            new_chapter_tag="ch:2.9.3",
            dated_note="2026-07-24: reused in ch.9.3, same meaning.",
            lexeme_root=corpus,
        )
        assert outcome.bucket == "duplicate"
        assert outcome.written == []
        assert not (corpus / "unused.md").exists()

    def test_appends_tag_to_tags_list(self, corpus):
        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        create_or_link_lexeme(
            "перегони",
            "",
            corpus / "unused.md",
            dedup_decision="duplicate",
            new_chapter_tag="ch:2.9.3",
            dated_note="2026-07-24: reused in ch.9.3.",
            lexeme_root=corpus,
        )
        meta = yaml.safe_load(target.read_text(encoding="utf-8").split("---")[1])
        assert "ch:2.9.3" in meta["tags"]

    def test_appends_to_tags_ch_field(self, corpus):
        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        create_or_link_lexeme(
            "перегони",
            "",
            corpus / "unused.md",
            dedup_decision="duplicate",
            new_chapter_tag="ch:2.9.3",
            dated_note="2026-07-24: reused.",
            lexeme_root=corpus,
        )
        meta = yaml.safe_load(target.read_text(encoding="utf-8").split("---")[1])
        assert meta["fields"]["Tags_Ch"] == "ch:2.9.1, ch:2.9.3"

    def test_appends_dated_verification_note(self, corpus):
        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        create_or_link_lexeme(
            "перегони",
            "",
            corpus / "unused.md",
            dedup_decision="duplicate",
            new_chapter_tag="ch:2.9.3",
            dated_note="2026-07-24: reused in ch.9.3, same meaning.",
            lexeme_root=corpus,
        )
        meta = yaml.safe_load(target.read_text(encoding="utf-8").split("---")[1])
        assert "2026-07-24: reused in ch.9.3, same meaning." in meta["fields"]["Verification Notes"]

    def test_no_duplicate_tag_if_already_present(self, corpus):
        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        # First call adds ch:2.9.3
        create_or_link_lexeme(
            "перегони", "", corpus / "u1.md",
            dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
            dated_note="first reuse.", lexeme_root=corpus,
        )
        # Second call with the same chapter tag should not duplicate it
        create_or_link_lexeme(
            "перегони", "", corpus / "u2.md",
            dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
            dated_note="second reuse note.", lexeme_root=corpus,
        )
        meta = yaml.safe_load(target.read_text(encoding="utf-8").split("---")[1])
        assert meta["tags"].count("ch:2.9.3") == 1
        assert meta["fields"]["Tags_Ch"] == "ch:2.9.1, ch:2.9.3"
        # But both dated notes should be recorded
        assert "first reuse." in meta["fields"]["Verification Notes"]
        assert "second reuse note." in meta["fields"]["Verification Notes"]

    def test_missing_chapter_tag_raises(self, corpus):
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "перегони", "", corpus / "unused.md",
                dedup_decision="duplicate", dated_note="note.",
                lexeme_root=corpus,
            )

    def test_missing_dated_note_raises(self, corpus):
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "перегони", "", corpus / "unused.md",
                dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
                lexeme_root=corpus,
            )

    def test_no_match_but_duplicate_decision_raises(self, corpus):
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "неіснуюче", "", corpus / "unused.md",
                dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
                dated_note="note.", lexeme_root=corpus,
            )

    def test_multiple_matches_all_modified(self, corpus):
        # Add a second note with the same lemma spelling as an existing one
        dup_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0010.md"
        dup_path.write_text(
            _note_text("ua-lexeme-0010", "перего́ни", gloss="races, racing (competitive)"),
            encoding="utf-8",
        )
        outcome = create_or_link_lexeme(
            "перегони", "", corpus / "unused.md",
            dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
            dated_note="note.", lexeme_root=corpus,
        )
        assert len(outcome.modified) == 2

    def test_file_stays_canonicalizable(self, corpus):
        """After the edit, the file should be stable under cnsf_canonicalize --check
        (i.e. this module's own writer already produced canonical output)."""
        from tools.anki.cnsf_canonicalize import canonicalized_file_text

        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        create_or_link_lexeme(
            "перегони", "", corpus / "unused.md",
            dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
            dated_note="note.", lexeme_root=corpus,
        )
        new_text, _ = canonicalized_file_text(target)
        assert new_text == target.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# create_or_link_lexeme — bucket "homograph"
# ─────────────────────────────────────────────────────────────────────────────


class TestCreateHomograph:
    def test_writes_new_note_with_own_note_id(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe (farm tool)")
        outcome = create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="коса (braid, hair) — ua-lexeme-0002 — homograph, unrelated meaning",
            homograph_confusable_existing="коса (scythe, farm tool) — homograph, unrelated meaning",
            lexeme_root=corpus,
        )
        assert outcome.bucket == "homograph"
        assert new_path.exists()

    def test_new_note_tagged_homograph_true(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe (farm tool)")
        create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="cross-link to braid sense",
            homograph_confusable_existing="cross-link to scythe sense",
            lexeme_root=corpus,
        )
        meta = yaml.safe_load(new_path.read_text(encoding="utf-8").split("---")[1])
        assert "homograph:true" in meta["tags"]
        assert "cross-link to braid sense" in meta["fields"]["ConfusableSet"]

    def test_existing_note_tagged_and_cross_linked(self, corpus):
        existing_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0002.md"
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe (farm tool)")
        create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="cross-link to braid sense",
            homograph_confusable_existing="cross-link to scythe sense",
            lexeme_root=corpus,
        )
        meta = yaml.safe_load(existing_path.read_text(encoding="utf-8").split("---")[1])
        assert "homograph:true" in meta["tags"]
        assert "cross-link to scythe sense" in meta["fields"]["ConfusableSet"]

    def test_existing_note_confusable_appended_not_clobbered(self, tmp_path):
        root = tmp_path / "lexemes"
        d = root / "ch-x"
        d.mkdir(parents=True)
        (d / "ua-lexeme-0001.md").write_text(
            _note_text("ua-lexeme-0001", "коса́", gloss="braid", confusable="pre-existing note"),
            encoding="utf-8",
        )
        new_path = d / "ua-lexeme-0002.md"
        content = _note_text("ua-lexeme-0002", "коса́", gloss="scythe")
        create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="new side note",
            homograph_confusable_existing="existing side note",
            lexeme_root=root,
        )
        meta = yaml.safe_load((d / "ua-lexeme-0001.md").read_text(encoding="utf-8").split("---")[1])
        assert "pre-existing note" in meta["fields"]["ConfusableSet"]
        assert "existing side note" in meta["fields"]["ConfusableSet"]

    def test_missing_confusable_new_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe")
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "коса́", content, new_path,
                dedup_decision="homograph",
                homograph_confusable_existing="existing side note",
                lexeme_root=corpus,
            )

    def test_missing_confusable_existing_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe")
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "коса́", content, new_path,
                dedup_decision="homograph",
                homograph_confusable_new="new side note",
                lexeme_root=corpus,
            )

    def test_no_match_but_homograph_decision_raises(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "неіснуюче", gloss="doesn't exist")
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "неіснуюче", content, new_path,
                dedup_decision="homograph",
                homograph_confusable_new="x", homograph_confusable_existing="y",
                lexeme_root=corpus,
            )

    def test_refuses_overwrite_of_new_note_path(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        new_path.write_text("placeholder", encoding="utf-8")
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe")
        with pytest.raises(DedupError):
            create_or_link_lexeme(
                "коса́", content, new_path,
                dedup_decision="homograph",
                homograph_confusable_new="x", homograph_confusable_existing="y",
                lexeme_root=corpus,
            )

    def test_multiple_existing_matches_all_cross_linked(self, corpus):
        dup_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0011.md"
        dup_path.write_text(
            _note_text("ua-lexeme-0011", "коса́", gloss="spit of land (geography)"),
            encoding="utf-8",
        )
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe")
        outcome = create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="new side note",
            homograph_confusable_existing="existing side note",
            lexeme_root=corpus,
        )
        assert len(outcome.modified) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Multi-line field values (regression: literal-block YAML style, no blank lines)
#
# cnsf_canonicalize's own "no blank lines inside frontmatter" check will reject
# any file where a multi-line field got serialized with a style that folds
# embedded newlines into blank physical lines (PyYAML's default heuristic for
# quoted scalars). These tests exercise that path directly, since none of the
# tests above happen to pass multi-line ConfusableSet/dated_note text.
# ─────────────────────────────────────────────────────────────────────────────


class TestMultilineFields:
    def test_multiline_confusable_set_on_new_note_is_canonicalizable(self, corpus):
        from tools.anki.cnsf_canonicalize import canonicalized_file_text

        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text(
            "ua-lexeme-0004", "озеро", gloss="lake",
            confusable="ставок (pond)\nScenario A: a large body of water\n-> Use: озеро\nScenario B: a small body of water\n-> Use: ставок",
        )
        create_or_link_lexeme("озеро", content, new_path, lexeme_root=corpus)
        # Must not raise — a blank-line violation would raise ValueError here.
        new_text, _ = canonicalized_file_text(new_path)
        assert new_text == new_path.read_text(encoding="utf-8")

    def test_multiline_confusable_set_no_blank_lines(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text(
            "ua-lexeme-0004", "озеро", gloss="lake",
            confusable="line one\nline two\nline three",
        )
        create_or_link_lexeme("озеро", content, new_path, lexeme_root=corpus)
        text = new_path.read_text(encoding="utf-8")
        frontmatter = text.split("---")[1]
        assert all(line.strip() for line in frontmatter.splitlines() if line != "")

    def test_multiline_dated_note_on_duplicate_is_canonicalizable(self, corpus):
        from tools.anki.cnsf_canonicalize import canonicalized_file_text

        target = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0001.md"
        create_or_link_lexeme(
            "перегони", "", corpus / "unused.md",
            dedup_decision="duplicate", new_chapter_tag="ch:2.9.3",
            dated_note="2026-07-24: line one.\nline two of the same dated note.",
            lexeme_root=corpus,
        )
        new_text, _ = canonicalized_file_text(target)
        assert new_text == target.read_text(encoding="utf-8")

    def test_multiline_confusable_set_on_homograph_existing_note_is_canonicalizable(self, corpus):
        from tools.anki.cnsf_canonicalize import canonicalized_file_text

        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0020.md"
        content = _note_text("ua-lexeme-0020", "коса́", gloss="scythe")
        create_or_link_lexeme(
            "коса́", content, new_path,
            dedup_decision="homograph",
            homograph_confusable_new="new side note\nsecond line",
            homograph_confusable_existing="existing side note\nsecond line",
            lexeme_root=corpus,
        )
        existing = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0002.md"
        for p in (new_path, existing):
            new_text, _ = canonicalized_file_text(p)
            assert new_text == p.read_text(encoding="utf-8")

    def test_multiline_value_round_trips_through_reparse(self, corpus):
        new_path = corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0004.md"
        content = _note_text(
            "ua-lexeme-0004", "озеро", gloss="lake",
            confusable="Scenario A: text\n-> Use: озеро\nKey distinction: explanation",
        )
        create_or_link_lexeme("озеро", content, new_path, lexeme_root=corpus)
        meta = yaml.safe_load(new_path.read_text(encoding="utf-8").split("---")[1])
        assert meta["fields"]["ConfusableSet"] == "Scenario A: text\n-> Use: озеро\nKey distinction: explanation"


# ─────────────────────────────────────────────────────────────────────────────
# next_note_id
# ─────────────────────────────────────────────────────────────────────────────


class TestNextNoteId:
    def test_increments_past_max(self, corpus):
        assert next_note_id(lexeme_root=corpus) == "ua-lexeme-0004"

    def test_empty_corpus_starts_at_one(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert next_note_id(lexeme_root=empty) == "ua-lexeme-0001"

    def test_respects_prefix(self, tmp_path):
        root = tmp_path / "verbs"
        root.mkdir()
        (root / "ua-verb-0005.md").write_text("x", encoding="utf-8")
        assert next_note_id(prefix="ua-verb", lexeme_root=root) == "ua-verb-0006"

    def test_accounts_for_new_notes_after_write(self, corpus):
        first = next_note_id(lexeme_root=corpus)
        assert first == "ua-lexeme-0004"
        path = corpus / "yabluko-l2" / "ch-09" / f"{first}.md"
        content = _note_text(first, "нове слово")
        create_or_link_lexeme("нове слово", content, path, lexeme_root=corpus)
        assert next_note_id(lexeme_root=corpus) == "ua-lexeme-0005"
