"""
tests/ua/test_euphony_stress.py

Unit tests for tools/anki/inspect/check_euphony_stress.py -- the guard on the
2026-08-18 convention that a populated `*_Euphony` value always carries its
stress mark, with no `*_Euphony_Typing` companion (the unstressed form is
derived by stripping, never stored).

The convention needs a checker precisely because breaking it is invisible: both
feedback scripts stripStress() the stored alternates and the typed answer before
comparing, so an unstressed euphony value grades identically to a stressed one
today. That's how PVOM ended up storing all four of its values unstressed while
UA_Lexeme stored all of its stressed, with neither side failing any check.

These tests pin the detection rule rather than the corpus, so they don't go
stale as notes are authored.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.inspect.check_euphony_stress as chk  # noqa: E402

AC = chr(0x0301)


class TestSyllableCount:
    def test_monosyllables(self):
        for w in ("й", "з", "йти", "в"):
            assert chk.syllable_count(w) <= 1, w

    def test_polysyllables(self):
        assert chk.syllable_count("уходити") == 4
        assert chk.syllable_count("увійти") == 3
        assert chk.syllable_count(f"ухо{AC}дити") == 4  # the mark is not a vowel

    def test_yi_counts_as_one_vowel(self):
        """ї is a single vowel letter, not a digraph, so уїхати is 4 not 5."""
        assert chk.syllable_count("уїхати") == 4


class TestMissingStress:
    def test_unstressed_multisyllable_is_flagged(self):
        assert chk.missing_stress("уходити") == ["уходити"]

    def test_stressed_multisyllable_is_clean(self):
        assert chk.missing_stress(f"ухо{AC}дити") == []

    def test_monosyllable_without_a_mark_is_clean(self):
        """Ukrainian doesn't mark stress on monosyllables -- flagging them would
        train people to ignore this checker."""
        assert chk.missing_stress("йти") == []
        assert chk.missing_stress("з") == []

    def test_double_stress_is_clean(self):
        """Two marks means free/variant stress -- a legitimate outcome per
        CLAUDE.md, explicitly NOT to be 'corrected'."""
        assert chk.missing_stress(f"за{AC}вжди{AC}") == []

    def test_phrase_checked_per_word(self):
        """'у порівня́нні' -- the preposition correctly carries no mark, so only
        a genuinely unstressed multisyllable should trip it."""
        assert chk.missing_stress(f"у порівня{AC}нні") == []
        assert chk.missing_stress("у порівнянні") == ["порівнянні"]

    def test_phrase_flags_only_the_offending_word(self):
        got = chk.missing_stress(f"розве{AC}дення овець")
        assert got == ["овець"]

    def test_empty_and_whitespace(self):
        assert chk.missing_stress("") == []
        assert chk.missing_stress("   ") == []


class TestRealCorpusValues:
    """The four values this convention was decided over."""

    def test_the_pvom_0012_values_after_the_fix_are_clean(self):
        for v in (f"ухо{AC}дити", f"увійти{AC}", f"уїжджа{AC}ти", f"уї{AC}хати"):
            assert chk.missing_stress(v) == [], v

    def test_the_pvom_0012_values_before_the_fix_were_all_flagged(self):
        for v in ("уходити", "увійти", "уїжджати", "уїхати"):
            assert chk.missing_stress(v) == [v], v


class TestScanCoverage:
    def test_only_note_types_that_have_euphony_fields_are_scanned(self):
        """UA_Verb/UA_Grammar/UA_Visual have no *_Euphony fields. Their absence
        is deliberate, not an oversight -- see the comment in NOTE_ROOTS."""
        labels = {label for label, _, _ in chk.NOTE_ROOTS}
        assert labels == {"UA_Lexeme", "UA_PVOM_Infinitive"}

    def test_scan_runs_against_the_real_corpus_without_raising(self):
        chk.scan()
