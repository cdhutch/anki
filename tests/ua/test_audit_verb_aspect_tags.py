"""
tests/ua/test_audit_verb_aspect_tags.py

Unit + integration tests for tools/anki/inspect/audit_verb_aspect_tags.py.

Craig, 2026-08-28 (яблуко-l2 chapter 11 vocab-expansion pass): "Update the
testing suite to identify verbs that only contain one aspect which also don't
have specific properties identifying the verb as specifically single-aspect"
-- then: "Decide whether this would be a code testing process or a data
validation process then implement it" -- then: "This process should be a
prerequisite for committing tranches of lexeme YAML files."

Decision (recorded here since it's the answer to that second message): this
is fundamentally a *data validation* concern -- it validates corpus content,
not code logic -- but this repo's established pattern (see
test_confusable_clusters.py, test_confusable_integration.py) is to express
corpus-wide data validation AS pytest tests that scan the real note tree
directly. That makes the check a native part of `pytest tests/ua/ -q`, which
is already run before every commit in this project's pipeline -- satisfying
the third message ("prerequisite for committing") with no extra pipeline step.

Covers:
  - TANTUM_SIGNAL_RE / claims_tantum(): the prose-signal detector, including
    the false-positive guards (a populated Perfective field, or a "no direct
    English counterpart"-style gloss, must not trip it)
  - has_tantum_tag(): recognizes both structured tags
  - scan(): fixture corpus -- clean notes excluded, violations found, scope
    correctly limited to ua_verb notes and pos:verb-tagged ua_lexeme notes
  - print_report(): smoke test
  - REAL-CORPUS GATE: scan() against the live domains/ua/anki/notes tree
    must return zero rows. This is the actual commit prerequisite -- if a
    future note's Verification Notes claims tantum status without the tag,
    this test fails and blocks the commit.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.inspect.audit_verb_aspect_tags import (  # noqa: E402
    KNOWN_NOT_TANTUM,
    claims_tantum,
    has_tantum_tag,
    print_report,
    scan,
)


def _note(note_id: str, note_type: str, tags: list[str], fields: dict[str, str]) -> str:
    tags_yaml = "\n".join(f"- {t}" for t in tags)
    fields_yaml = "\n".join(f"  {k}: {v!r}" for k, v in fields.items())
    model = "UA_Verb" if note_type == "ua_verb" else "UA_Lexeme"
    return (
        "---\n"
        "schema: cnsf/v0\n"
        f"note_type: {note_type}\n"
        f"note_id: {note_id}\n"
        "anki:\n"
        f"  model: {model}\n"
        "  deck: UA::Verbs\n"
        "tags:\n"
        f"{tags_yaml}\n"
        "fields:\n"
        f"  NoteID: {note_id}\n"
        f"{fields_yaml}\n"
        "---\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# claims_tantum / has_tantum_tag
# ─────────────────────────────────────────────────────────────────────────────


class TestClaimsTantum:
    def test_bare_tantum_word(self):
        assert claims_tantum({"Verification Notes": "Imperfectiva tantum, confirmed via Горох."})

    def test_no_perfective_counterpart_phrase(self):
        assert claims_tantum({"Source_Note": "This verb has no perfective counterpart."})

    def test_no_listed_perfective_phrase(self):
        assert claims_tantum({"Verification Notes": "Checked against the verb dictionary: no listed perfective."})

    def test_reflexivum_tantum_still_matches_bare_word(self):
        assert claims_tantum({"Verification Notes": "Effectively reflexivum tantum (no attested perfective partner)."})

    def test_clean_note_does_not_match(self):
        assert not claims_tantum({"Verification Notes": "New. Regular 1st-conj verb, paired with звучати."})

    def test_unrelated_no_counterpart_phrasing_does_not_match(self):
        # A translation gloss saying "no direct English counterpart" must NOT
        # be mistaken for an aspect claim -- this is why the regex requires
        # "perfective"/"imperfective"/"aspectual" counterpart, not bare "counterpart".
        assert not claims_tantum({"EN_Gloss": "roughly 'coziness' -- no direct English counterpart"})

    def test_empty_fields_no_match(self):
        assert not claims_tantum({})

    def test_case_insensitive(self):
        assert claims_tantum({"Verification Notes": "IMPERFECTIVA TANTUM."})


class TestHasTantumTag:
    def test_imperfective_only_recognized(self):
        assert has_tantum_tag(["domain:ua", "aspect:imperfective-only"])

    def test_perfective_only_recognized(self):
        assert has_tantum_tag(["aspect:perfective-only"])

    def test_neither_tag_present(self):
        assert not has_tantum_tag(["domain:ua", "status:draft"])

    def test_empty_tags(self):
        assert not has_tantum_tag([])


# ─────────────────────────────────────────────────────────────────────────────
# scan() -- fixture corpus
# ─────────────────────────────────────────────────────────────────────────────


class TestScanFixtureCorpus:
    def _corpus(self, tmp_path: Path) -> tuple[Path, Path]:
        lex_root = tmp_path / "lexemes" / "ch-01"
        lex_root.mkdir(parents=True)
        verb_root = tmp_path / "verbs"
        verb_root.mkdir()

        # 1. Lexeme, pos:verb, tantum prose, NO tag -- should be flagged.
        (lex_root / "ua-lexeme-0001.md").write_text(
            _note(
                "ua-lexeme-0001", "ua_lexeme", ["domain:ua", "pos:verb", "status:draft"],
                {"Lemma": "вважати", "Verification Notes": "Imperfectiva tantum, confirmed via Горох."},
            ),
            encoding="utf-8",
        )
        # 2. Same tantum prose, but correctly tagged -- clean.
        (lex_root / "ua-lexeme-0002.md").write_text(
            _note(
                "ua-lexeme-0002", "ua_lexeme",
                ["domain:ua", "pos:verb", "aspect:imperfective-only", "status:verified"],
                {"Lemma": "намагатися", "Verification Notes": "Imperfectiva tantum, confirmed via Горох."},
            ),
            encoding="utf-8",
        )
        # 3. Normal paired verb, no tantum claim -- clean (nothing to flag).
        (lex_root / "ua-lexeme-0003.md").write_text(
            _note(
                "ua-lexeme-0003", "ua_lexeme", ["domain:ua", "pos:verb", "status:verified"],
                {"Lemma": "малювати", "Perfective": "намалювати", "Verification Notes": "Paired, regular."},
            ),
            encoding="utf-8",
        )
        # 4. Non-verb lexeme with unrelated "no counterpart" gloss text -- must
        #    NOT be flagged (out of scope: no pos:verb tag at all).
        (lex_root / "ua-lexeme-0004.md").write_text(
            _note(
                "ua-lexeme-0004", "ua_lexeme", ["domain:ua", "pos:noun", "status:verified"],
                {"Lemma": "затишок", "EN_Gloss": "coziness -- no direct English counterpart"},
            ),
            encoding="utf-8",
        )
        # 5. ua_verb note, tantum prose, no tag -- should be flagged.
        (verb_root / "ua-verb-0001.md").write_text(
            _note(
                "ua-verb-0001", "ua_verb", ["domain:ua", "status:draft"],
                {"Lemma": "вважати", "Aspect": "imperfective", "Verification Notes": "No perfective counterpart -- imperfectivum tantum."},
            ),
            encoding="utf-8",
        )
        # 6. exported/ stub -- must be skipped regardless of content.
        exported = verb_root / "exported"
        exported.mkdir()
        (exported / "ua-verb-9999.md").write_text(
            _note(
                "ua-verb-9999", "ua_verb", ["domain:ua"],
                {"Lemma": "тест", "Verification Notes": "Imperfectiva tantum."},
            ),
            encoding="utf-8",
        )
        return lex_root.parent, verb_root

    def test_untagged_tantum_lexeme_flagged(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-lexeme-0001" in ids

    def test_tagged_tantum_lexeme_excluded(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-lexeme-0002" not in ids

    def test_normal_paired_verb_excluded(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-lexeme-0003" not in ids

    def test_non_verb_lexeme_out_of_scope(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-lexeme-0004" not in ids

    def test_untagged_tantum_verb_note_flagged(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-verb-0001" in ids

    def test_exported_stub_skipped(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        ids = {r["note_id"] for r in rows}
        assert "ua-verb-9999" not in ids

    def test_exact_flagged_count(self, tmp_path):
        lex_root, verb_root = self._corpus(tmp_path)
        rows = scan(lex_root, verb_root)
        assert len(rows) == 2  # ua-lexeme-0001, ua-verb-0001

    def test_missing_roots_return_empty(self, tmp_path):
        assert scan(tmp_path / "no-such-lexemes", tmp_path / "no-such-verbs") == []

    def test_known_not_tantum_allowlist_entry_excluded(self, tmp_path):
        # A note whose prose matches the tantum signal but is a documented
        # false positive (negation, or describing a different lemma) must be
        # excluded even without the structured tag -- this is what keeps the
        # real-corpus gate exact instead of chasing regex edge cases forever.
        assert KNOWN_NOT_TANTUM, "allowlist should not be empty at this point in the corpus"
        allowlisted_id = next(iter(KNOWN_NOT_TANTUM))
        lex_root = tmp_path / "lexemes" / "ch-01"
        lex_root.mkdir(parents=True)
        verb_root = tmp_path / "verbs"
        verb_root.mkdir()
        (lex_root / f"{allowlisted_id}.md").write_text(
            _note(
                allowlisted_id, "ua_lexeme", ["domain:ua", "pos:verb", "status:verified"],
                {"Lemma": "тест", "Verification Notes": "so this is not imperfectiva tantum, paired."},
            ),
            encoding="utf-8",
        )
        rows = scan(lex_root.parent, verb_root)
        ids = {r["note_id"] for r in rows}
        assert allowlisted_id not in ids


# ─────────────────────────────────────────────────────────────────────────────
# print_report -- smoke test
# ─────────────────────────────────────────────────────────────────────────────


class TestPrintReport:
    def test_empty_rows_prints_clean_message(self, capsys):
        print_report([])
        out = capsys.readouterr().out
        assert "Clean" in out

    def test_nonempty_rows_lists_each_note(self, capsys, tmp_path):
        rows = [
            {
                "note_type": "ua_lexeme",
                "note_id": "ua-lexeme-0001",
                "lemma": "вважати",
                "path": tmp_path / "ua-lexeme-0001.md",
            }
        ]
        print_report(rows)
        out = capsys.readouterr().out
        assert "ua-lexeme-0001" in out
        assert "вважати" in out


# ─────────────────────────────────────────────────────────────────────────────
# REAL-CORPUS GATE -- this is the actual commit prerequisite.
# ─────────────────────────────────────────────────────────────────────────────


class TestRealCorpusGate:
    def test_no_untagged_tantum_verb_notes_in_corpus(self):
        rows = scan()
        if rows:
            offenders = "\n".join(
                f"  {r['note_id']} ({r['lemma']}) -- {r['path']}" for r in rows
            )
            raise AssertionError(
                "The following verb note(s) claim single-aspect (tantum) status in "
                "their own Verification Notes/Source_Note prose but are missing the "
                "structured aspect:imperfective-only/aspect:perfective-only tag. Add "
                "the correct tag (matching what the note's own prose already says) "
                "before committing:\n" + offenders
            )
