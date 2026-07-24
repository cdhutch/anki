"""
tests/ua/test_gen_ch09_subsection.py

Unit and integration tests for tools/anki/extract/gen_ch09_subsection.py — the
dedup-wired driver script for Ch-09 subsection sourcing (CLAUDE.md item 0: "wire
dedup/homograph check into the vocabulary-generation workflow").

Covers:
  - process_candidate: all three buckets (new/duplicate/homograph), routed through
    create_or_link_lexeme() exactly like a hand-run call would be
  - malformed candidates raise BatchError (missing lemma/decision/chapter_tag/fields)
  - a real dedup collision with no decision (or a decision inconsistent with corpus
    state) still raises DedupError — confirms this driver cannot be used to bypass
    the dedup check, only to invoke it uniformly
  - process_batch: multiple candidates, including a within-batch dependency (a
    candidate created earlier in the batch is visible to a later duplicate-decision
    candidate in the same call)
  - main(): CLI JSON-file entry point end to end
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.lib.lexeme_dedup import DedupError, load_corpus, strip_stress  # noqa: E402
from tools.anki.extract.gen_ch09_subsection import (  # noqa: E402
    BatchError,
    main,
    process_batch,
    process_candidate,
)

CH09_REL = Path("yabluko-l2") / "ch-09"


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures / helpers
# ─────────────────────────────────────────────────────────────────────────────


def _note_text(note_id: str, lemma: str, *, gloss: str = "test gloss", tags_ch: str = "ch:2.9.1") -> str:
    return (
        "---\n"
        "schema: cnsf/v0\n"
        "note_type: ua_lexeme\n"
        f"note_id: {note_id}\n"
        "anki:\n"
        "  model: UA_Lexeme\n"
        "  deck: UA::Recognition::UA→EN\n"
        "tags:\n"
        "- domain:ua\n"
        f"- {tags_ch}\n"
        "fields:\n"
        f"  NoteID: {note_id}\n"
        f"  Lemma: {lemma}\n"
        "  PartOfSpeech: noun\n"
        "  Gender: m\n"
        "  Perfective: ''\n"
        f"  EN_Gloss: {gloss}\n"
        "  Govt_Case: ''\n"
        "  CounterpartForm: ''\n"
        "  IrregularForms: ''\n"
        "  VerbMotion_Pair: ''\n"
        "  ConfusableSet: ''\n"
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
        "  Verification Notes: ''\n"
        "---\n"
    )


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "lexemes"
    ch09 = root / "yabluko-l2" / "ch-09"
    ch09.mkdir(parents=True)
    (ch09 / "ua-lexeme-0144.md").write_text(
        _note_text("ua-lexeme-0144", "перего́ни", gloss="races, racing (competitive)"),
        encoding="utf-8",
    )
    return root


def _new_candidate(lemma: str, **overrides) -> dict:
    base = {
        "lemma": lemma,
        "dedup_decision": "new",
        "chapter_tag": "ch:2.9.3",
        "fields": {"Lemma": lemma, "PartOfSpeech": "noun", "Gender": "m", "EN_Gloss": "test word"},
        "tags": ["domain:ua", "topic:vocabulary"],
    }
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# process_candidate — bucket "new"
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessCandidateNew:
    def test_writes_new_note(self, corpus):
        result = process_candidate(_new_candidate("озеро"), lexeme_root=corpus, index=load_corpus(corpus))
        assert result["bucket"] == "new"
        assert len(result["written"]) == 1
        written_path = Path(result["written"][0])
        assert written_path.exists()
        text = written_path.read_text(encoding="utf-8")
        meta = yaml.safe_load(text.split("---")[1])
        assert meta["fields"]["Lemma"] == "озеро"
        assert meta["fields"]["EN_Gloss"] == "test word"

    def test_chapter_tag_auto_added(self, corpus):
        result = process_candidate(_new_candidate("озеро"), lexeme_root=corpus, index=load_corpus(corpus))
        text = Path(result["written"][0]).read_text(encoding="utf-8")
        meta = yaml.safe_load(text.split("---")[1])
        assert "ch:2.9.3" in meta["tags"]

    def test_note_id_assigned_sequentially(self, corpus):
        # corpus fixture's highest existing ID is ua-lexeme-0144
        result = process_candidate(_new_candidate("озеро"), lexeme_root=corpus, index=load_corpus(corpus))
        assert Path(result["written"][0]).stem == "ua-lexeme-0145"

    def test_collision_without_decision_raises(self, corpus):
        # 'перегони' already exists in the corpus fixture — this driver must not
        # silently create a duplicate note just because the caller said "new".
        with pytest.raises(DedupError):
            process_candidate(_new_candidate("перего́ни"), lexeme_root=corpus, index=load_corpus(corpus))


# ─────────────────────────────────────────────────────────────────────────────
# process_candidate — bucket "duplicate"
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessCandidateDuplicate:
    def test_appends_chapter_tag_no_new_file(self, corpus):
        before = set((corpus / "yabluko-l2" / "ch-09").glob("*.md"))
        result = process_candidate(
            {
                "lemma": "перего́ни",
                "dedup_decision": "duplicate",
                "chapter_tag": "ch:2.9.3",
                "dated_note": "2026-07-25: reused in 9.3.",
            },
            lexeme_root=corpus, index=load_corpus(corpus),
        )
        after = set((corpus / "yabluko-l2" / "ch-09").glob("*.md"))
        assert before == after  # no new file written
        assert result["bucket"] == "duplicate"
        existing = (corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0144.md").read_text(encoding="utf-8")
        meta = yaml.safe_load(existing.split("---")[1])
        assert "ch:2.9.3" in meta["fields"]["Tags_Ch"]
        assert "2026-07-25" in meta["fields"]["Verification Notes"]

    def test_missing_dated_note_raises_dedup_error(self, corpus):
        with pytest.raises(DedupError):
            process_candidate(
                {"lemma": "перего́ни", "dedup_decision": "duplicate", "chapter_tag": "ch:2.9.3"},
                lexeme_root=corpus, index=load_corpus(corpus),
            )


# ─────────────────────────────────────────────────────────────────────────────
# process_candidate — bucket "homograph"
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessCandidateHomograph:
    def test_cross_links_both_notes(self, corpus):
        result = process_candidate(
            {
                "lemma": "перего́ни",
                "dedup_decision": "homograph",
                "chapter_tag": "ch:2.9.3",
                "fields": {"Lemma": "перего́ни", "PartOfSpeech": "noun", "EN_Gloss": "unrelated sense"},
                "tags": ["domain:ua"],
                "homograph_confusable_new": "перегони (racing sense) — see ua-lexeme-0144",
                "homograph_confusable_existing": "перегони (unrelated sense) — see new note",
            },
            lexeme_root=corpus, index=load_corpus(corpus),
        )
        assert result["bucket"] == "homograph"
        new_text = Path(result["written"][0]).read_text(encoding="utf-8")
        new_meta = yaml.safe_load(new_text.split("---")[1])
        assert "homograph:true" in new_meta["tags"]

        existing_text = (corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0144.md").read_text(encoding="utf-8")
        existing_meta = yaml.safe_load(existing_text.split("---")[1])
        assert "homograph:true" in existing_meta["tags"]
        assert "unrelated sense" in existing_meta["fields"]["ConfusableSet"]


# ─────────────────────────────────────────────────────────────────────────────
# Malformed candidates
# ─────────────────────────────────────────────────────────────────────────────


class TestMalformedCandidates:
    def test_missing_lemma_raises_batch_error(self, corpus):
        with pytest.raises(BatchError):
            process_candidate({"dedup_decision": "new", "chapter_tag": "ch:2.9.3"}, lexeme_root=corpus, index=load_corpus(corpus))

    def test_missing_decision_raises_batch_error(self, corpus):
        with pytest.raises(BatchError):
            process_candidate({"lemma": "озеро", "chapter_tag": "ch:2.9.3"}, lexeme_root=corpus, index=load_corpus(corpus))

    def test_invalid_decision_raises_batch_error(self, corpus):
        with pytest.raises(BatchError):
            process_candidate(
                {"lemma": "озеро", "dedup_decision": "maybe", "chapter_tag": "ch:2.9.3"},
                lexeme_root=corpus, index=load_corpus(corpus),
            )

    def test_missing_chapter_tag_raises_batch_error(self, corpus):
        with pytest.raises(BatchError):
            process_candidate({"lemma": "озеро", "dedup_decision": "new"}, lexeme_root=corpus, index=load_corpus(corpus))

    def test_missing_fields_for_new_raises_batch_error(self, corpus):
        with pytest.raises(BatchError):
            process_candidate(
                {"lemma": "озеро", "dedup_decision": "new", "chapter_tag": "ch:2.9.3"},
                lexeme_root=corpus, index=load_corpus(corpus),
            )


# ─────────────────────────────────────────────────────────────────────────────
# process_batch
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessBatch:
    def test_multiple_candidates(self, corpus):
        results = process_batch(
            [_new_candidate("озеро"), _new_candidate("ставок")],
            lexeme_root=corpus,
        )
        assert [r["bucket"] for r in results] == ["new", "new"]
        assert len(list((corpus / "yabluko-l2" / "ch-09").glob("*.md"))) == 3  # 1 existing + 2 new

    def test_within_batch_dependency_visible_to_later_candidate(self, corpus):
        # First candidate creates 'озеро' as new; second candidate treats it as a
        # duplicate seen again in the same subsection — must see the first
        # candidate's write, not a stale pre-batch index snapshot.
        results = process_batch(
            [
                _new_candidate("озеро"),
                {
                    "lemma": "озеро",
                    "dedup_decision": "duplicate",
                    "chapter_tag": "ch:2.9.3",
                    "dated_note": "2026-07-25: appears twice in 9.3 word list.",
                },
            ],
            lexeme_root=corpus,
        )
        assert results[0]["bucket"] == "new"
        assert results[1]["bucket"] == "duplicate"
        assert len(list((corpus / "yabluko-l2" / "ch-09").glob("*.md"))) == 2  # 1 existing + 1 new (not 2 new)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────


class TestMain:
    def test_cli_json_round_trip(self, corpus, tmp_path, monkeypatch, capsys):
        batch_path = tmp_path / "batch.json"
        batch_path.write_text(json.dumps([_new_candidate("озеро")]), encoding="utf-8")

        monkeypatch.setattr(
            sys, "argv",
            ["gen_ch09_subsection.py", str(batch_path), "--lexeme-root", str(corpus)],
        )
        main()
        out = capsys.readouterr().out
        assert "new" in out
        assert "озеро" in out
        assert (corpus / "yabluko-l2" / "ch-09" / "ua-lexeme-0145.md").exists()
