"""
tests/ua/test_lexeme_dedup.py

Unit and integration tests for tools/anki/lib/lexeme_dedup.py.

Covers:
  - strip_stress / split_frontmatter
  - load_index / lookup
  - require_decision (AmbiguousMatch / InconsistentDecision)
  - patch_duplicate / patch_homograph_link (pure)
  - apply_duplicate_to_file / apply_homograph_to_file (file I/O)
  - create_or_link_lexeme — the three buckets end to end
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.lib.lexeme_dedup import (  # noqa: E402
    AmbiguousMatch,
    InconsistentDecision,
    apply_duplicate_to_file,
    apply_homograph_to_file,
    build_homograph_confusable_text,
    create_or_link_lexeme,
    load_index,
    lookup,
    patch_duplicate,
    patch_homograph_link,
    require_decision,
    split_frontmatter,
    strip_stress,
)

STRESS = "́"  # U+0301

_NOTE_TEMPLATE = """\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: {note_id}
tags:
- domain:ua
- topic:vocabulary
- ch:2.9.1
- pos:noun
- status:verified
fields:
  NoteID: {note_id}
  Lemma: {lemma}
  PartOfSpeech: noun
  Gender: f
  EN_Gloss: {gloss}
  ConfusableSet: {confusable}
  TypingAnswer: {typing}
  Tags_Ch: ch:2.9.1
  Verification Notes: ''
---
"""


def _write_note(root: Path, note_id: str, lemma: str, gloss: str, confusable: str = "''") -> Path:
    path = root / f"{note_id}.md"
    path.write_text(
        _NOTE_TEMPLATE.format(
            note_id=note_id, lemma=lemma, gloss=gloss, confusable=confusable,
            typing=strip_stress(lemma),
        ),
        encoding="utf-8",
    )
    return path


# ─────────────────────────────────────────────────────────────────────────────
# strip_stress / split_frontmatter
# ─────────────────────────────────────────────────────────────────────────────


class TestStripStress:
    def test_removes_accent(self):
        assert strip_stress("перего́ни") == "перегони"

    def test_no_accent_unchanged(self):
        assert strip_stress("перегони") == "перегони"

    def test_preserves_yi_and_i_short(self):
        # NFD decomposition of й/ї must survive stripping
        assert strip_stress("ї́зда") == "їзда"
        assert strip_stress("бойови́й") == "бойовий"

    def test_double_stress_preserved(self):
        # Free/variant stress: both marks are meaningful, not garbage.
        result = strip_stress("алфа́ві́т")
        assert STRESS not in result
        assert result == "алфавіт"


class TestSplitFrontmatter:
    def test_extracts_yaml_block(self):
        text = "---\nfoo: bar\n---\n"
        assert split_frontmatter(text).strip() == "foo: bar"

    def test_missing_frontmatter_returns_none(self):
        assert split_frontmatter("no frontmatter here") is None

    def test_malformed_returns_none(self):
        assert split_frontmatter("---\nfoo: bar") is None


# ─────────────────────────────────────────────────────────────────────────────
# load_index / lookup
# ─────────────────────────────────────────────────────────────────────────────


class TestLoadIndex:
    def test_finds_notes_in_nested_dirs(self, tmp_path):
        sub = tmp_path / "yabluko-l2" / "ch-09"
        sub.mkdir(parents=True)
        _write_note(sub, "ua-lexeme-0144", "перего́ни", "races, racing")

        index = load_index(tmp_path)
        assert "перегони" in index
        assert len(index["перегони"]) == 1
        assert index["перегони"][0].note_id == "ua-lexeme-0144"

    def test_stress_stripped_key(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0023", "алфа́ві́т", "alphabet")
        index = load_index(tmp_path)
        assert "алфавіт" in index

    def test_empty_dir_empty_index(self, tmp_path):
        assert load_index(tmp_path) == {}

    def test_multiple_records_same_key(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        _write_note(tmp_path, "ua-lexeme-0002", "ко́са", "scythe")
        index = load_index(tmp_path)
        assert len(index["коса"]) == 2


class TestLookup:
    def test_match_found(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        index = load_index(tmp_path)
        matches = lookup("перегони", index)
        assert len(matches) == 1
        assert matches[0].note_id == "ua-lexeme-0144"

    def test_lookup_with_stress_in_query(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        index = load_index(tmp_path)
        matches = lookup("пере́гони", index)  # different (wrong) stress placement
        assert len(matches) == 1  # still matches — spelling only, stress-agnostic

    def test_no_match(self, tmp_path):
        index = load_index(tmp_path)
        assert lookup("щосьновеслово", index) == []


# ─────────────────────────────────────────────────────────────────────────────
# require_decision
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireDecision:
    def test_no_match_no_decision_ok(self, tmp_path):
        index = load_index(tmp_path)
        assert require_decision("нове́слово", index, None) == []

    def test_match_no_decision_raises(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        index = load_index(tmp_path)
        with pytest.raises(AmbiguousMatch):
            require_decision("перегони", index, None)

    def test_decision_without_match_raises(self, tmp_path):
        index = load_index(tmp_path)
        with pytest.raises(InconsistentDecision):
            require_decision("нове́слово", index, "duplicate")

    def test_match_with_duplicate_decision_ok(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        index = load_index(tmp_path)
        matches = require_decision("перегони", index, "duplicate")
        assert len(matches) == 1

    def test_match_with_homograph_decision_ok(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        index = load_index(tmp_path)
        matches = require_decision("коса", index, "homograph")
        assert len(matches) == 1


# ─────────────────────────────────────────────────────────────────────────────
# patch_duplicate / patch_homograph_link (pure)
# ─────────────────────────────────────────────────────────────────────────────


class TestPatchDuplicate:
    def _fields(self, **overrides):
        base = {"Lemma": "перего́ни", "Tags_Ch": "ch:2.9.1", "Verification Notes": ""}
        base.update(overrides)
        return base

    def test_appends_new_chapter_tag(self):
        fields, tags = patch_duplicate(
            self._fields(), ["ch:2.9.1"], new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3"
        )
        assert "ch:2.9.3" in tags
        assert "ch:2.9.1" in tags

    def test_no_duplicate_tag(self):
        fields, tags = patch_duplicate(
            self._fields(), ["ch:2.9.1"], new_chapter_tag="ch:2.9.1", reuse_context="ch.9.1 again"
        )
        assert tags.count("ch:2.9.1") == 1

    def test_tags_ch_field_updated(self):
        fields, _ = patch_duplicate(
            self._fields(), [], new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3"
        )
        assert fields["Tags_Ch"] == "ch:2.9.1, ch:2.9.3"

    def test_tags_ch_no_duplicate_entry(self):
        fields, _ = patch_duplicate(
            self._fields(), [], new_chapter_tag="ch:2.9.1", reuse_context="ch.9.1 again"
        )
        assert fields["Tags_Ch"] == "ch:2.9.1"

    def test_verification_notes_appended(self):
        fields, _ = patch_duplicate(
            self._fields(), [], new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3 ('gear')",
            today="2026-07-24",
        )
        assert "ch.9.3" in fields["Verification Notes"]
        assert "2026-07-24" in fields["Verification Notes"]

    def test_verification_notes_preserves_existing(self):
        fields, _ = patch_duplicate(
            self._fields(**{"Verification Notes": "Originally sourced 2026-07-01."}),
            [], new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3",
        )
        assert "Originally sourced 2026-07-01." in fields["Verification Notes"]
        assert "Reused in ch.9.3" in fields["Verification Notes"]

    def test_does_not_mutate_input(self):
        original_fields = self._fields()
        original_tags = ["ch:2.9.1"]
        patch_duplicate(original_fields, original_tags, new_chapter_tag="ch:2.9.3", reuse_context="x")
        assert original_fields["Tags_Ch"] == "ch:2.9.1"
        assert original_tags == ["ch:2.9.1"]


class TestPatchHomographLink:
    def test_build_confusable_text(self):
        text = build_homograph_confusable_text("ко́са", "scythe")
        assert "ко́са" in text
        assert "scythe" in text
        assert "homograph" in text.lower()

    def test_sets_confusable_set(self):
        fields, tags = patch_homograph_link(
            {"ConfusableSet": ""}, [], other_lemma="ко́са", other_gloss="scythe"
        )
        assert "ко́са" in fields["ConfusableSet"]
        assert "scythe" in fields["ConfusableSet"]

    def test_preserves_existing_confusable_set(self):
        fields, tags = patch_homograph_link(
            {"ConfusableSet": "абе́тка — near-synonym"}, [],
            other_lemma="ко́са", other_gloss="scythe",
        )
        assert "абе́тка" in fields["ConfusableSet"]
        assert "ко́са" in fields["ConfusableSet"]

    def test_adds_homograph_tag(self):
        _, tags = patch_homograph_link(
            {"ConfusableSet": ""}, ["domain:ua"], other_lemma="ко́са", other_gloss="scythe"
        )
        assert "homograph:true" in tags

    def test_no_duplicate_homograph_tag(self):
        _, tags = patch_homograph_link(
            {"ConfusableSet": ""}, ["homograph:true"], other_lemma="ко́са", other_gloss="scythe"
        )
        assert tags.count("homograph:true") == 1

    def test_no_duplicate_link_text_on_reapply(self):
        fields, tags = patch_homograph_link(
            {"ConfusableSet": ""}, [], other_lemma="ко́са", other_gloss="scythe"
        )
        fields2, _ = patch_homograph_link(
            fields, tags, other_lemma="ко́са", other_gloss="scythe"
        )
        assert fields2["ConfusableSet"].count("ко́са") == 1


# ─────────────────────────────────────────────────────────────────────────────
# File-level wrappers
# ─────────────────────────────────────────────────────────────────────────────


class TestApplyDuplicateToFile:
    def test_patches_file_in_place(self, tmp_path):
        path = _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        apply_duplicate_to_file(path, new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3")

        doc = yaml.safe_load(split_frontmatter(path.read_text(encoding="utf-8")))
        assert "ch:2.9.3" in doc["tags"]
        assert doc["fields"]["Tags_Ch"] == "ch:2.9.1, ch:2.9.3"

    def test_dry_run_does_not_write(self, tmp_path):
        path = _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        original = path.read_text(encoding="utf-8")
        apply_duplicate_to_file(path, new_chapter_tag="ch:2.9.3", reuse_context="ch.9.3", dry_run=True)
        assert path.read_text(encoding="utf-8") == original


class TestApplyHomographToFile:
    def test_patches_file_in_place(self, tmp_path):
        path = _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        apply_homograph_to_file(path, other_lemma="ко́са", other_gloss="scythe")

        doc = yaml.safe_load(split_frontmatter(path.read_text(encoding="utf-8")))
        assert "homograph:true" in doc["tags"]
        assert "scythe" in doc["fields"]["ConfusableSet"]


# ─────────────────────────────────────────────────────────────────────────────
# create_or_link_lexeme — end-to-end, all three buckets
# ─────────────────────────────────────────────────────────────────────────────


def _new_doc(note_id: str, lemma: str, gloss: str) -> dict:
    return {
        "schema": "cnsf/v0",
        "note_type": "ua_lexeme",
        "note_id": note_id,
        "tags": ["domain:ua", "ch:2.9.3", "pos:noun", "status:draft"],
        "fields": {
            "NoteID": note_id,
            "Lemma": lemma,
            "EN_Gloss": gloss,
            "ConfusableSet": "",
            "Tags_Ch": "ch:2.9.3",
        },
    }


class TestCreateOrLinkLexeme:
    def test_bucket1_brand_new(self, tmp_path):
        index = load_index(tmp_path)
        new_path = tmp_path / "ua-lexeme-0200.md"
        resolution = create_or_link_lexeme(
            index=index,
            lemma="нове́слово",
            new_note_path=new_path,
            new_note_doc=_new_doc("ua-lexeme-0200", "нове́слово", "new word"),
            chapter_tag="ch:2.9.3",
            reuse_context="ch.9.3",
        )
        assert resolution.action == "created"
        assert new_path.exists()

    def test_bucket3_duplicate_creates_no_file(self, tmp_path):
        existing = _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races, racing")
        index = load_index(tmp_path)
        new_path = tmp_path / "ua-lexeme-0200.md"

        resolution = create_or_link_lexeme(
            index=index,
            lemma="перего́ни",
            new_note_path=new_path,
            new_note_doc=_new_doc("ua-lexeme-0200", "перего́ни", "races, racing"),
            chapter_tag="ch:2.9.3",
            reuse_context="ch.9.3 ('outdoor gear')",
            dedup_decision="duplicate",
        )

        assert resolution.action == "linked_duplicate"
        assert resolution.note_id == "ua-lexeme-0144"
        assert not new_path.exists()  # no new file created

        doc = yaml.safe_load(split_frontmatter(existing.read_text(encoding="utf-8")))
        assert "ch:2.9.3" in doc["tags"]
        assert "ch.9.3" in doc["fields"]["Verification Notes"]

    def test_bucket2_homograph_creates_file_and_crosslinks(self, tmp_path):
        existing = _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        index = load_index(tmp_path)
        new_path = tmp_path / "ua-lexeme-0201.md"

        resolution = create_or_link_lexeme(
            index=index,
            lemma="ко́са",
            new_note_path=new_path,
            new_note_doc=_new_doc("ua-lexeme-0201", "ко́са", "scythe"),
            chapter_tag="ch:2.9.3",
            reuse_context="ch.9.3",
            dedup_decision="homograph",
        )

        assert resolution.action == "created_homograph"
        assert new_path.exists()
        assert resolution.linked_note_ids == ["ua-lexeme-0001"]

        new_doc = yaml.safe_load(split_frontmatter(new_path.read_text(encoding="utf-8")))
        assert "homograph:true" in new_doc["tags"]
        assert "braid" in new_doc["fields"]["ConfusableSet"]

        old_doc = yaml.safe_load(split_frontmatter(existing.read_text(encoding="utf-8")))
        assert "homograph:true" in old_doc["tags"]
        assert "scythe" in old_doc["fields"]["ConfusableSet"]

    def test_no_decision_with_match_raises(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        index = load_index(tmp_path)
        with pytest.raises(AmbiguousMatch):
            create_or_link_lexeme(
                index=index,
                lemma="перего́ни",
                new_note_path=tmp_path / "ua-lexeme-0200.md",
                new_note_doc=_new_doc("ua-lexeme-0200", "перего́ни", "races"),
                chapter_tag="ch:2.9.3",
                reuse_context="ch.9.3",
            )

    def test_duplicate_decision_multiple_matches_needs_target(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        _write_note(tmp_path, "ua-lexeme-0002", "ко́са", "scythe")
        index = load_index(tmp_path)
        with pytest.raises(InconsistentDecision):
            create_or_link_lexeme(
                index=index,
                lemma="коса",
                new_note_path=tmp_path / "ua-lexeme-0200.md",
                new_note_doc=_new_doc("ua-lexeme-0200", "коса", "braid"),
                chapter_tag="ch:2.9.3",
                reuse_context="ch.9.3",
                dedup_decision="duplicate",
            )

    def test_duplicate_decision_with_target_note_id(self, tmp_path):
        _write_note(tmp_path, "ua-lexeme-0001", "коса́", "braid")
        target = _write_note(tmp_path, "ua-lexeme-0002", "ко́са", "scythe")
        index = load_index(tmp_path)

        resolution = create_or_link_lexeme(
            index=index,
            lemma="коса",
            new_note_path=tmp_path / "ua-lexeme-0200.md",
            new_note_doc=_new_doc("ua-lexeme-0200", "коса", "scythe"),
            chapter_tag="ch:2.9.3",
            reuse_context="ch.9.3",
            dedup_decision="duplicate",
            target_note_id="ua-lexeme-0002",
        )
        assert resolution.note_id == "ua-lexeme-0002"
        assert resolution.path == target

    def test_dry_run_creates_nothing(self, tmp_path):
        existing = _write_note(tmp_path, "ua-lexeme-0144", "перего́ни", "races")
        original = existing.read_text(encoding="utf-8")
        index = load_index(tmp_path)
        new_path = tmp_path / "ua-lexeme-0200.md"

        create_or_link_lexeme(
            index=index,
            lemma="перего́ни",
            new_note_path=new_path,
            new_note_doc=_new_doc("ua-lexeme-0200", "перего́ни", "races"),
            chapter_tag="ch:2.9.3",
            reuse_context="ch.9.3",
            dedup_decision="duplicate",
            dry_run=True,
        )
        assert not new_path.exists()
        assert existing.read_text(encoding="utf-8") == original
