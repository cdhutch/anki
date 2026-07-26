"""
tests/ua/test_backfill_source_url.py

Unit and integration tests for tools/anki/inspect/backfill_source_url.py.

Covers:
  - strip_stress
  - goroh_url
  - extract_lemma
  - already_has_source_url
  - inject_source_fields
  - process_file (integration — tmp note files)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.inspect.backfill_source_url import (  # noqa: E402
    already_has_source_url,
    extract_lemma,
    goroh_url,
    inject_source_fields,
    process_file,
    strip_stress,
)

GOROH_BASE = "https://goroh.pp.ua/Словозміна/"
STRESS = "́"  # U+0301

# ─────────────────────────────────────────────────────────────────────────────
# strip_stress
# ─────────────────────────────────────────────────────────────────────────────

class TestStripStress:
    def test_removes_accent(self):
        assert strip_stress("воді́й") == "водій"

    def test_no_accent_unchanged(self):
        assert strip_stress("водій") == "водій"

    def test_empty(self):
        assert strip_stress("") == ""


# ─────────────────────────────────────────────────────────────────────────────
# goroh_url
# ─────────────────────────────────────────────────────────────────────────────

class TestGorohUrl:
    def test_strips_stress_in_url(self):
        url = goroh_url("воді́й")
        assert STRESS not in url
        assert url == GOROH_BASE + "водій"

    def test_no_stress_mark(self):
        url = goroh_url("водій")
        assert url == GOROH_BASE + "водій"

    def test_multi_word_returns_empty(self):
        # Phrases have no goroh page
        url = goroh_url("добрий день")
        assert url == ""

    def test_multi_word_with_stress_returns_empty(self):
        url = goroh_url("до́брий де́нь")
        assert url == ""

    def test_single_word(self):
        url = goroh_url("акто́р")
        assert url == GOROH_BASE + "актор"

    def test_preserves_ukrainian_chars(self):
        url = goroh_url("їжа́к")
        assert "їжак" in url


# ─────────────────────────────────────────────────────────────────────────────
# extract_lemma
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractLemma:
    def test_plain_value(self):
        content = "  Lemma: акто́р\n"
        assert extract_lemma(content) == "акто́р"

    def test_quoted_value(self):
        content = "  Lemma: 'акто́р'\n"
        assert extract_lemma(content) == "акто́р"

    def test_double_quoted_value(self):
        content = '  Lemma: "акто́р"\n'
        assert extract_lemma(content) == "акто́р"

    def test_missing_returns_none(self):
        assert extract_lemma("  PartOfSpeech: noun\n") is None

    def test_leading_whitespace_stripped(self):
        assert extract_lemma("  Lemma:  акто́р  \n") == "акто́р"


# ─────────────────────────────────────────────────────────────────────────────
# already_has_source_url
# ─────────────────────────────────────────────────────────────────────────────

class TestAlreadyHasSourceUrl:
    def test_true_when_present(self):
        content = "  Source_URL: 'https://goroh.pp.ua/Словозміна/актор'\n"
        assert already_has_source_url(content) is True

    def test_false_when_absent(self):
        content = "  Lemma: акто́р\n  PartOfSpeech: noun\n"
        assert already_has_source_url(content) is False

    def test_empty_source_url_still_true(self):
        content = "  Source_URL: ''\n"
        assert already_has_source_url(content) is True


# ─────────────────────────────────────────────────────────────────────────────
# inject_source_fields
# ─────────────────────────────────────────────────────────────────────────────

# Minimal note template without Source_URL
_NOTE_WITHOUT_SOURCE = """\
---
schema: cnsf/v0
note_id: ua-lexeme-test
tags:
- domain:ua
fields:
  NoteID: ua-lexeme-test
  Lemma: акто́р
  Verification Notes: ''
---
"""

# Note without "Verification Notes" line (fallback insertion path)
_NOTE_NO_VN = """\
---
schema: cnsf/v0
note_id: ua-lexeme-test
fields:
  NoteID: ua-lexeme-test
  Lemma: акто́р
---
"""


class TestInjectSourceFields:
    def test_inserts_source_url(self):
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        assert "Source_URL:" in result

    def test_inserts_source_note(self):
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        assert "Source_Note:" in result

    def test_url_value_in_result(self):
        url = GOROH_BASE + "актор"
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, url)
        assert url in result

    def test_source_note_blank(self):
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        # Source_Note should be blank
        import re
        m = re.search(r"Source_Note:\s*(.*)", result)
        assert m
        assert m.group(1).strip() in ("''", '""', "")

    def test_inserted_after_verification_notes(self):
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        vn_pos = result.index("Verification Notes:")
        url_pos = result.index("Source_URL:")
        assert url_pos > vn_pos, "Source_URL should appear after Verification Notes"

    def test_fallback_insertion_before_closing_dashes(self):
        result = inject_source_fields(_NOTE_NO_VN, GOROH_BASE + "актор")
        assert "Source_URL:" in result
        # Must appear before the closing ---
        url_pos = result.index("Source_URL:")
        close_pos = result.rindex("---")
        assert url_pos < close_pos

    def test_result_starts_with_opening_dashes(self):
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        assert result.startswith("---")

    def test_idempotent_structure(self):
        # Injecting once and checking that the note is still valid YAML-ish
        result = inject_source_fields(_NOTE_WITHOUT_SOURCE, GOROH_BASE + "актор")
        # The result should still contain the original fields
        assert "Lemma: акто́р" in result
        assert "Verification Notes:" in result


# ─────────────────────────────────────────────────────────────────────────────
# process_file — integration
# ─────────────────────────────────────────────────────────────────────────────

_FULL_NOTE_TEMPLATE = """\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: {note_id}
tags:
- domain:ua
- stress:unverified
fields:
  NoteID: {note_id}
  Lemma: {lemma}
  PartOfSpeech: noun
  Gender: m
  Perfective: ''
  EN_Gloss: test
  Govt_Case: ''
  CounterpartForm: ''
  IrregularForms: ''
  VerbMotion_Pair: ''
  ConfusableSet: ''
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: {typing}
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
  Verification Notes: ''
---
"""


class TestProcessFile:
    def test_injects_source_url_into_note(self, tmp_path):
        note = tmp_path / "ua-lexeme-p1.md"
        content = _FULL_NOTE_TEMPLATE.format(
            note_id="ua-lexeme-p1", lemma="акто́р", typing="актор"
        )
        note.write_text(content, encoding="utf-8")

        changed = process_file(note, dry_run=False)
        assert changed is True

        new_content = note.read_text(encoding="utf-8")
        assert "Source_URL:" in new_content
        assert GOROH_BASE + "актор" in new_content

    def test_skips_note_already_has_source_url(self, tmp_path):
        note = tmp_path / "ua-lexeme-p2.md"
        content = _FULL_NOTE_TEMPLATE.format(
            note_id="ua-lexeme-p2", lemma="акто́р", typing="актор"
        ) + f"  Source_URL: '{GOROH_BASE}актор'\n"
        note.write_text(content, encoding="utf-8")
        # Manually inject so already_has_source_url returns True
        note.write_text(content.replace(
            "  Verification Notes: ''",
            f"  Verification Notes: ''\n  Source_URL: '{GOROH_BASE}актор'"
        ), encoding="utf-8")

        changed = process_file(note, dry_run=False)
        assert changed is False

    def test_dry_run_does_not_write(self, tmp_path):
        note = tmp_path / "ua-lexeme-p3.md"
        content = _FULL_NOTE_TEMPLATE.format(
            note_id="ua-lexeme-p3", lemma="акто́р", typing="актор"
        )
        note.write_text(content, encoding="utf-8")

        changed = process_file(note, dry_run=True)
        assert changed is True  # "would be" changed

        # File must not have been modified
        new_content = note.read_text(encoding="utf-8")
        assert "Source_URL:" not in new_content

    def test_phrase_lemma_gets_empty_url(self, tmp_path):
        note = tmp_path / "ua-lexeme-p4.md"
        content = _FULL_NOTE_TEMPLATE.format(
            note_id="ua-lexeme-p4", lemma="добрий ранок", typing="добрий ранок"
        )
        note.write_text(content, encoding="utf-8")

        process_file(note, dry_run=False)
        new_content = note.read_text(encoding="utf-8")
        assert "Source_URL: ''" in new_content
