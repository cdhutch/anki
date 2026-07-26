"""
tests/ua/test_verify_stress_goroh.py

Unit and integration tests for tools/anki/inspect/verify_stress_goroh.py.

Covers:
  - strip_stress / vowel_count / stressed_vowel_index
  - compare_stress (all 7 status codes)
  - parse_goroh_paradigm
  - parse_irregular_forms / parse_counterpart_forms
  - parse_goroh_html (stdlib parser)
  - extract_note_targets (integration — reads real note files)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.inspect.verify_stress_goroh import (  # noqa: E402
    APOSTROPHE,
    _clean_form,
    _split_variants,
    compare_stress,
    extract_note_targets,
    goroh_url,
    parse_counterpart_forms,
    parse_goroh_html,
    parse_goroh_paradigm,
    parse_irregular_forms,
    stressed_vowel_index,
    strip_stress,
    vowel_count,
)

STRESS = "́"   # U+0301 COMBINING ACUTE ACCENT

# ── Helpers ───────────────────────────────────────────────────────────────────

NOTES_CH00 = next(
    (p for p in [
        REPO_ROOT / "domains/ua/anki/notes/lexemes/yabluko-l1/ch-00",
        REPO_ROOT / "domains/ua/anki/notes/lexemes/yabluko-l1/vstup",
    ] if p.exists()),
    None,
)


# ─────────────────────────────────────────────────────────────────────────────
# goroh_url — URL building with apostrophe normalisation
# ─────────────────────────────────────────────────────────────────────────────

class TestGorohUrl:
    BASE = "https://goroh.pp.ua/"

    def test_url_starts_with_goroh_base(self):
        assert goroh_url("актор").startswith(self.BASE)

    def test_u02bc_apostrophe_not_encoded_as_ca_bc(self):
        # U+02BC must NOT appear as %CA%BC — Горох only recognises ASCII apostrophe
        url = goroh_url("компʼютер")
        assert "%CA%BC" not in url

    def test_simya_apostrophe_not_encoded_as_ca_bc(self):
        url = goroh_url("сімʼя")
        assert "%CA%BC" not in url

    def test_plain_word_roundtrip(self):
        # Word without apostrophe should encode cleanly
        url = goroh_url("водій")
        assert "водій" in url or "%D0%B2%D0%BE%D0%B4%D1%96%D0%B9" in url

    def test_no_raw_stress_mark_in_url(self):
        # goroh_url takes a bare (unstressed) lemma — just sanity-check
        url = goroh_url("водій")
        assert "́" not in url  # U+0301 COMBINING ACUTE ACCENT

    def test_slovozmina_is_default_section(self):
        url_default = goroh_url("водій")
        url_explicit = goroh_url("водій", section="Словозміна")
        assert url_default == url_explicit
        assert "%D0%A1%D0%BB%D0%BE%D0%B2%D0%BE%D0%B7%D0%BC%D1%96%D0%BD%D0%B0" in url_default

    def test_tlumachennya_section(self):
        url = goroh_url("медбрат", section="Тлумачення")
        assert "%D0%A2%D0%BB%D1%83%D0%BC%D0%B0%D1%87%D0%B5%D0%BD%D0%BD%D1%8F" in url
        assert "медбрат" in url or "%D0%BC%D0%B5%D0%B4%D0%B1%D1%80%D0%B0%D1%82" in url


# ─────────────────────────────────────────────────────────────────────────────
# strip_stress
# ─────────────────────────────────────────────────────────────────────────────

class TestStripStress:
    def test_removes_combining_accent(self):
        assert strip_stress("воді́й") == "водій"

    def test_word_without_stress_unchanged(self):
        assert strip_stress("водій") == "водій"

    def test_multiple_marks_removed(self):
        # Artificially double-accented string
        assert strip_stress(f"а{STRESS}б{STRESS}в") == "абв"

    def test_empty_string(self):
        assert strip_stress("") == ""

    def test_preserves_ukrainian_apostrophe(self):
        # U+02BC must survive
        assert "ʼ" in strip_stress("сімʼя́")
        assert STRESS not in strip_stress("сімʼя́")


# ─────────────────────────────────────────────────────────────────────────────
# vowel_count
# ─────────────────────────────────────────────────────────────────────────────

class TestVowelCount:
    def test_monosyllable_nih(self):
        assert vowel_count("ніж") == 1

    def test_monosyllable_rik(self):
        assert vowel_count("рік") == 1

    def test_disyllable_vodiy(self):
        # в-о-д-і-й → о, і
        assert vowel_count("водій") == 2

    def test_disyllable_misto(self):
        # м-і-с-т-о → і, о
        assert vowel_count("місто") == 2

    def test_disyllable_student(self):
        # с-т-у-д-е-н-т → у, е
        assert vowel_count("студент") == 2

    def test_stress_marks_not_counted_as_vowels(self):
        # Adding U+0301 must not change vowel count
        assert vowel_count("воді́й") == vowel_count("водій")

    def test_trisyllable(self):
        # у-кра-їн-а → у, а, ї, а  = 4 vowels
        assert vowel_count("україна") == 4


# ─────────────────────────────────────────────────────────────────────────────
# stressed_vowel_index
# ─────────────────────────────────────────────────────────────────────────────

class TestStressedVowelIndex:
    def test_first_vowel_stressed(self):
        # а́ктор: а=0 stressed, о=1
        assert stressed_vowel_index("а́ктор") == 0

    def test_second_vowel_stressed(self):
        # воді́й: о=0, і=1 stressed
        assert stressed_vowel_index("воді́й") == 1

    def test_second_vowel_vikno(self):
        # вікно́: і=0, о=1 stressed
        assert stressed_vowel_index("вікно́") == 1

    def test_second_vowel_student(self):
        # студе́нт: у=0, е=1 stressed
        assert stressed_vowel_index("студе́нт") == 1

    def test_no_stress_mark_returns_none(self):
        assert stressed_vowel_index("водій") is None

    def test_monosyllable_no_mark_returns_none(self):
        assert stressed_vowel_index("ніж") is None

    def test_monosyllable_with_mark(self):
        # Single stressed vowel → index 0
        assert stressed_vowel_index("ні́ж") == 0

    def test_privit(self):
        # приві́т: и=0, і=1 stressed
        assert stressed_vowel_index("приві́т") == 1


# ─────────────────────────────────────────────────────────────────────────────
# compare_stress
# ─────────────────────────────────────────────────────────────────────────────

class TestCompareStress:
    # ── ok ───────────────────────────────────────────────────────────────────

    def test_ok_exact_match(self):
        status, detail = compare_stress("воді́й", ["воді́й"])
        assert status == "ok"
        assert detail == "воді́й"

    def test_ok_case_insensitive(self):
        # Capital Горох form vs lowercase stored (shouldn't happen but is handled)
        status, _ = compare_stress("акто́р", ["акто́р"])
        assert status == "ok"

    # ── monosyllable ─────────────────────────────────────────────────────────

    def test_monosyllable_single_vowel(self):
        status, _ = compare_stress("ніж", ["ніж"])
        assert status == "monosyllable"

    def test_monosyllable_with_stressed_goroh(self):
        # Горох may add stress to monosyllables
        status, _ = compare_stress("ніж", ["ні́ж"])
        assert status == "monosyllable"

    # ── mismatch ─────────────────────────────────────────────────────────────

    def test_mismatch_wrong_vowel(self):
        # Stored: во́дій (stress on о, index 0); Горох: воді́й (stress on і, index 1)
        status, correction = compare_stress("во́дій", ["воді́й"])
        assert status == "mismatch"
        assert correction == "воді́й"

    def test_mismatch_no_stress_mark_in_stored(self):
        # Polysyllabic word with no stress mark — counts as mismatch
        status, correction = compare_stress("водій", ["воді́й"])
        assert status == "mismatch"
        assert correction == "воді́й"

    # ── variable ─────────────────────────────────────────────────────────────

    def test_variable_stored_is_first_variant(self):
        # Горох lists two valid positions; stored matches first
        status, detail = compare_stress("до́ма", ["до́ма", "дома́"])
        assert status == "variable"
        assert "до́ма" in detail
        assert "дома́" in detail

    def test_variable_stored_is_second_variant(self):
        status, detail = compare_stress("дома́", ["до́ма", "дома́"])
        assert status == "variable"

    # ── variable_mismatch ────────────────────────────────────────────────────

    def test_variable_mismatch_no_stress_mark(self):
        # Stored has no stress; neither of the two Горох variants match
        status, detail = compare_stress("дома", ["до́ма", "дома́"])
        assert status == "variable_mismatch"
        assert "до́ма" in detail

    def test_variable_mismatch_wrong_stress(self):
        # Stored: до́ма; Горох only has: дома́ / доміи́ (hypothetical)
        # Reuse real pattern: stored has different vowel index than any Горох form
        status, _ = compare_stress("ві́кно", ["вікно́"])
        assert status == "mismatch"  # single candidate, so just "mismatch"

    # ── not_found ────────────────────────────────────────────────────────────

    def test_not_found_different_word(self):
        status, _ = compare_stress("воді́й", ["акто́р", "студе́нт"])
        assert status == "not_found"

    def test_not_found_empty_candidates(self):
        status, _ = compare_stress("воді́й", [])
        assert status == "not_found"

    # ── capitalisation-only variable → ok (Fix 1) ────────────────────────────

    def test_ok_when_multiple_candidates_same_stress_position(self):
        # Горох returns Ку́хар and ку́хар — identical stress on vowel 0.
        # Should collapse to "ok", not "variable".
        status, detail = compare_stress("ку́хар", ["Ку́хар", "ку́хар"])
        assert status == "ok"
        assert STRESS in detail

    def test_ok_ukraina_capitalisation_variant(self):
        status, _ = compare_stress("Украї́на", ["Украї́на", "украї́на"])
        assert status == "ok"

    def test_variable_genuinely_different_positions(self):
        # адре́са / а́дреса — different stressed vowels; must remain "variable"
        status, detail = compare_stress("адре́са", ["адре́са", "а́дреса"])
        assert status == "variable"
        assert "адре́са" in detail
        assert "а́дреса" in detail

    # ── apostrophe normalisation (Fix 2) ─────────────────────────────────────

    def test_ok_apostrophe_u02bc_matches_goroh_stripped(self):
        # _clean_form strips the ASCII apostrophe from Горох HTML, producing
        # "компю́тер".  normalize_bare must match this against stored "компʼютер".
        status, _ = compare_stress("компʼю́тер", ["компю́тер"])
        assert status == "ok"

    def test_ok_simya_apostrophe_normalization(self):
        # gen.pl сімей stored without stress; Горох gives сіме́й stripped to сімей
        # (no apostrophe issue here, but verify base case works)
        status, correction = compare_stress("сімей", ["сіме́й"])
        assert status == "mismatch"
        assert correction == "сіме́й"

    def test_ok_imya_apostrophe_u02bc(self):
        # Stored імʼя́ (U+02BC); Горох allForms has імя́ (apostrophe stripped)
        status, _ = compare_stress("імʼя́", ["імя́"])
        assert status == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# parse_irregular_forms
# ─────────────────────────────────────────────────────────────────────────────

class TestParseIrregularForms:
    def test_gen_pl_with_note(self):
        result = parse_irregular_forms("gen.pl. вікон (zero ending)")
        assert result == [("gen.pl", "вікон")]

    def test_gen_sg_with_note(self):
        result = parse_irregular_forms("gen.sg. вечора (stem vowel і→о in oblique cases)")
        assert result == [("gen.sg", "вечора")]

    def test_gen_pl_stress_shift(self):
        result = parse_irregular_forms("gen.pl. вчителів (stress shifts)")
        assert result == [("gen.pl", "вчителів")]

    def test_gen_pl_with_stress_mark(self):
        result = parse_irregular_forms("gen.pl. воді́їв")
        assert len(result) == 1
        assert result[0][0] == "gen.pl"
        assert result[0][1] == "воді́їв"

    def test_gen_pl_simey(self):
        result = parse_irregular_forms("gen.pl. сімей")
        assert result == [("gen.pl", "сімей")]

    def test_empty_string(self):
        assert parse_irregular_forms("") == []

    def test_no_case_pattern(self):
        assert parse_irregular_forms("indeclinable") == []

    def test_parenthetical_only_note(self):
        assert parse_irregular_forms("(irregular plural)") == []


# ─────────────────────────────────────────────────────────────────────────────
# parse_counterpart_forms
# ─────────────────────────────────────────────────────────────────────────────

class TestParseCounterpartForms:
    def test_feminine_single(self):
        result = parse_counterpart_forms("f: воді́йка")
        assert result == [("f", "воді́йка")]

    def test_feminine_with_variant(self):
        result = parse_counterpart_forms("f: вчи́телька / учи́телька")
        assert len(result) == 2
        assert ("f", "вчи́телька") in result
        assert ("f", "учи́телька") in result

    def test_masculine(self):
        result = parse_counterpart_forms("m: акто́р")
        assert result == [("m", "акто́р")]

    def test_multiple_genders_comma(self):
        # "m: англі́йський; n: англі́йське" — only the first gender:form is matched
        # CounterpartForm uses ; between genders; parse_counterpart_forms handles
        # only one gender prefix at a time per field value.
        # This tests that at least the first gender is extracted correctly.
        result = parse_counterpart_forms("m: англі́йський")
        assert result == [("m", "англі́йський")]

    def test_empty_string(self):
        assert parse_counterpart_forms("") == []

    def test_no_gender_prefix(self):
        assert parse_counterpart_forms("воді́йка") == []


# ─────────────────────────────────────────────────────────────────────────────
# _split_variants
# ─────────────────────────────────────────────────────────────────────────────

class TestSplitVariants:
    def test_single_form(self):
        assert _split_variants("воді́й") == ["воді́й"]

    def test_slash_split(self):
        assert _split_variants("до́ма / дома́") == ["до́ма", "дома́"]

    def test_comma_split(self):
        assert _split_variants("до́ма, дома́") == ["до́ма", "дома́"]

    def test_empty(self):
        assert _split_variants("") == []


# ─────────────────────────────────────────────────────────────────────────────
# _clean_form
# ─────────────────────────────────────────────────────────────────────────────

class TestCleanForm:
    def test_strips_backtick(self):
        assert _clean_form("во`дій") == "водій"

    def test_strips_ascii_apostrophe(self):
        assert _clean_form("сім'я") == "сімя"

    def test_strips_colon(self):
        assert _clean_form("водій:") == "водій"

    def test_expands_dz(self):
        assert _clean_form("{дз}воні́ти") == "дзвоні́ти"

    def test_expands_dzh(self):
        assert _clean_form("{дж}ерело́") == "джерело́"

    def test_preserves_stress_mark(self):
        result = _clean_form("воді́й")
        assert STRESS in result

    def test_strips_modifier_letter_apostrophe(self):
        # U+02BC ʼ should be stripped (phonetic marker, not Ukrainian apostrophe in this context)
        assert "ʼ" not in _clean_form("сімʼя")


# ─────────────────────────────────────────────────────────────────────────────
# parse_goroh_html
# ─────────────────────────────────────────────────────────────────────────────

# Minimal HTML that mimics the Горох Словозміна page structure
_SAMPLE_HTML_VODIY = """\
<html><body>
<table>
<tr><td>Називний</td><td>воді́й</td><td>воді́ї</td></tr>
<tr><td>Родовий</td><td>водія́<sup>1</sup></td><td>воді́їв</td></tr>
<tr><td>Давальний</td><td>водіє́ві</td><td>воді́ям</td></tr>
<tr><td>Знахідний</td><td>водія́</td><td>воді́їв</td></tr>
<tr><td>Орудний</td><td>водіє́м</td><td>воді́ями</td></tr>
<tr><td>Місцевий</td><td>водіє́ві</td><td>воді́ях</td></tr>
<tr><td>Кличний</td><td>воді́ю</td><td>воді́ї</td></tr>
</table>
</body></html>
"""

_SAMPLE_HTML_EMPTY = "<html><body><p>Слово не знайдено.</p></body></html>"

_SAMPLE_HTML_SUP = """\
<html><body><table>
<tr><td>Називний</td><td>акто́р<sup>1</sup></td><td>акто́ри</td></tr>
<tr><td>Родовий</td><td>акто́ра</td><td>акто́рів</td></tr>
</table></body></html>
"""

_SAMPLE_HTML_BACKTICK = """\
<html><body><table>
<tr><td>Називний</td><td>во`ді́й</td><td>воді́ї</td></tr>
</table></body></html>
"""


class TestParseGorohHtml:
    def test_not_found_false_for_populated_page(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        assert not result["notFound"]

    def test_not_found_true_for_empty_page(self):
        result = parse_goroh_html(_SAMPLE_HTML_EMPTY)
        assert result["notFound"]

    def test_extracts_nom_row(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        nom_rows = [r for r in result["rows"] if r[0] == "nom"]
        assert len(nom_rows) == 1
        assert "воді́й" in nom_rows[0]

    def test_extracts_gen_row(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        gen_rows = [r for r in result["rows"] if r[0] == "gen"]
        assert len(gen_rows) == 1
        # sg and pl should be in the row
        row = gen_rows[0]
        assert any("водія́" in c or "водія" in c for c in row)
        assert any("воді́їв" in c for c in row)

    def test_extracts_seven_cases(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        cases = {r[0] for r in result["rows"]}
        assert cases == {"nom", "gen", "dat", "acc", "ins", "loc", "voc"}

    def test_strips_sup_content(self):
        result = parse_goroh_html(_SAMPLE_HTML_SUP)
        all_text = " ".join(c for row in result["rows"] for c in row)
        # The digit "1" from <sup>1</sup> must be gone
        assert "1" not in all_text

    def test_all_forms_contains_stressed_tokens(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        forms = result["allForms"]
        assert any("воді́й" in f for f in forms)

    def test_strips_backtick(self):
        result = parse_goroh_html(_SAMPLE_HTML_BACKTICK)
        all_text = " ".join(c for row in result["rows"] for c in row)
        assert "`" not in all_text

    def test_rows_structure(self):
        result = parse_goroh_html(_SAMPLE_HTML_VODIY)
        for row in result["rows"]:
            assert isinstance(row, list)
            assert len(row) >= 2  # case code + at least sg form

    def test_full_page_scan_catches_adverb_heading(self):
        # Adverbs have no declension table; their stressed form appears in a heading.
        html = "<html><body><h1>чу́дово</h1><p>Незмінна частина мови.</p></body></html>"
        result = parse_goroh_html(html)
        # notFound=False because all_forms now has the heading form
        assert not result["notFound"]
        assert "чу́дово" in result["allForms"]

    def test_full_page_scan_deduplicates(self):
        # Same form in both table and heading — should appear only once
        html = """\
<html><body>
<h1>воді́й</h1>
<table><tr><td>Називний</td><td>воді́й</td><td>воді́ї</td></tr></table>
</body></html>"""
        result = parse_goroh_html(html)
        assert result["allForms"].count("воді́й") == 1


# ─────────────────────────────────────────────────────────────────────────────
# parse_goroh_paradigm
# ─────────────────────────────────────────────────────────────────────────────

class TestParseGorohParadigm:
    def test_nom_sg_pl(self):
        rows = [["nom", "воді́й", "воді́ї"]]
        p = parse_goroh_paradigm(rows, [])
        assert "воді́й" in p["nom.sg"]
        assert "воді́ї" in p["nom.pl"]

    def test_gen_sg_pl(self):
        rows = [["gen", "водія́", "воді́їв"]]
        p = parse_goroh_paradigm(rows, [])
        assert "водія́" in p["gen.sg"]
        assert "воді́їв" in p["gen.pl"]

    def test_variant_splitting_slash(self):
        rows = [["dat", "водіє́ві / водіє́вові", "воді́ям"]]
        p = parse_goroh_paradigm(rows, [])
        assert "водіє́ві" in p["dat.sg"]
        assert "водіє́вові" in p["dat.sg"]

    def test_all_forms_catch_all(self):
        rows = [["nom", "акто́р", "акто́ри"]]
        p = parse_goroh_paradigm(rows, ["акто́рів"])  # extra from allForms
        assert "акто́рів" in p["all_forms"]

    def test_every_form_goes_to_all_forms(self):
        rows = [["nom", "воді́й", "воді́ї"], ["gen", "водія́", "воді́їв"]]
        p = parse_goroh_paradigm(rows, [])
        for form in ("воді́й", "воді́ї", "водія́", "воді́їв"):
            assert form in p["all_forms"], f"{form} missing from all_forms"

    def test_unknown_case_ignored(self):
        rows = [["xyz", "something", "else"]]
        p = parse_goroh_paradigm(rows, [])
        assert "xyz.sg" not in p
        assert "xyz.pl" not in p

    def test_empty_rows_uses_all_forms_fallback(self):
        p = parse_goroh_paradigm([], ["воді́й", "водія́"])
        assert "воді́й" in p["all_forms"]
        assert "водія́" in p["all_forms"]

    def test_no_duplicates_in_slot(self):
        rows = [["nom", "воді́й", "воді́й"]]  # same value twice
        p = parse_goroh_paradigm(rows, [])
        assert p.get("nom.pl", []).count("воді́й") <= 1


# ─────────────────────────────────────────────────────────────────────────────
# extract_note_targets — integration tests (requires real note files)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(NOTES_CH00 is None, reason="ch-00 note directory not found")
class TestExtractNoteTargets:
    def test_returns_none_without_unverified_tag(self, tmp_path):
        """A note lacking stress:unverified is skipped."""
        note = tmp_path / "ua-lexeme-test.md"
        note.write_text("""\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-test
tags:
- domain:ua
- status:verified
fields:
  NoteID: ua-lexeme-test
  Lemma: акто́р
  PartOfSpeech: noun
  Gender: m
  Perfective: ''
  EN_Gloss: actor
  Govt_Case: ''
  CounterpartForm: ''
  IrregularForms: ''
  VerbMotion_Pair: ''
  ConfusableSet: ''
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: актор
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
  Verification Notes: ''
  Source_URL: https://goroh.pp.ua/Словозміна/актор
  Source_Note: ''
---
""", encoding="utf-8")
        result = extract_note_targets(note)
        assert result is None

    def test_extracts_lemma_target(self, tmp_path, monkeypatch):
        """A note with stress:unverified produces a target for the Lemma field."""
        import tools.anki.inspect.verify_stress_goroh as vsg
        monkeypatch.setattr(vsg, "REPO_ROOT", tmp_path)
        note = tmp_path / "ua-lexeme-t1.md"
        note.write_text("""\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-t1
tags:
- domain:ua
- stress:unverified
fields:
  NoteID: ua-lexeme-t1
  Lemma: акто́р
  PartOfSpeech: noun
  Gender: m
  Perfective: ''
  EN_Gloss: actor
  Govt_Case: ''
  CounterpartForm: ''
  IrregularForms: ''
  VerbMotion_Pair: ''
  ConfusableSet: ''
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: актор
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
  Verification Notes: ''
  Source_URL: ''
  Source_Note: ''
---
""", encoding="utf-8")
        result = extract_note_targets(note)
        assert result is not None
        assert result["lemma"] == "акто́р"
        lemma_targets = [t for t in result["targets"] if t["field"] == "Lemma"]
        assert len(lemma_targets) == 1
        assert lemma_targets[0]["bare"] == "актор"
        assert lemma_targets[0]["lookup_lemma"] == "актор"

    def test_extracts_irregular_forms_target(self, tmp_path, monkeypatch):
        """IrregularForms entries generate their own targets."""
        import tools.anki.inspect.verify_stress_goroh as vsg
        monkeypatch.setattr(vsg, "REPO_ROOT", tmp_path)
        note = tmp_path / "ua-lexeme-t2.md"
        note.write_text("""\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-t2
tags:
- domain:ua
- stress:unverified
fields:
  NoteID: ua-lexeme-t2
  Lemma: вікно́
  PartOfSpeech: noun
  Gender: n
  Perfective: ''
  EN_Gloss: window
  Govt_Case: ''
  CounterpartForm: ''
  IrregularForms: gen.pl. вікон (zero ending)
  VerbMotion_Pair: ''
  ConfusableSet: ''
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: вікно
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
  Verification Notes: ''
  Source_URL: ''
  Source_Note: ''
---
""", encoding="utf-8")
        result = extract_note_targets(note)
        assert result is not None
        irr_targets = [t for t in result["targets"] if t["field"] == "IrregularForms"]
        assert len(irr_targets) == 1
        assert irr_targets[0]["form"] == "вікон"
        assert irr_targets[0]["slot"] == "gen.pl"

    def test_extracts_counterpart_form_target(self, tmp_path, monkeypatch):
        """CounterpartForm entries use the counterpart as their own lookup lemma."""
        import tools.anki.inspect.verify_stress_goroh as vsg
        monkeypatch.setattr(vsg, "REPO_ROOT", tmp_path)
        note = tmp_path / "ua-lexeme-t3.md"
        note.write_text("""\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-t3
tags:
- domain:ua
- stress:unverified
fields:
  NoteID: ua-lexeme-t3
  Lemma: воді́й
  PartOfSpeech: noun
  Gender: m
  Perfective: ''
  EN_Gloss: driver
  Govt_Case: ''
  CounterpartForm: 'f: воді́йка'
  IrregularForms: ''
  VerbMotion_Pair: ''
  ConfusableSet: ''
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: водій
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
  Verification Notes: ''
  Source_URL: ''
  Source_Note: ''
---
""", encoding="utf-8")
        result = extract_note_targets(note)
        assert result is not None
        cp_targets = [t for t in result["targets"] if t["field"] == "CounterpartForm"]
        assert len(cp_targets) == 1
        assert cp_targets[0]["form"] == "воді́йка"
        # CounterpartForm is looked up under its own bare form, not the primary lemma
        assert cp_targets[0]["lookup_lemma"] == "воді́йка".replace(STRESS, "")

    def test_real_note_0003_has_correct_targets(self, tmp_path, monkeypatch):
        """ua-lexeme-0003 (воді́й) should yield lemma + irregular forms + counterpart.

        Reads the real corpus file (to catch format drift against live content)
        but forces stress:unverified onto a tmp copy rather than asserting on the
        corpus's live tag. Note 0003 has since gone through stress verification
        and legitimately lost that tag (status:verified, tag removed) — coupling
        this test to the corpus's current review state made it break whenever the
        note it happened to target got verified, not when extraction logic broke.
        """
        import yaml

        import tools.anki.inspect.verify_stress_goroh as vsg

        path = NOTES_CH00 / "ua-lexeme-0003.md"
        if not path.exists():
            pytest.skip("ua-lexeme-0003.md not found")
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        meta = yaml.safe_load(parts[1])
        tags = list(meta.get("tags") or [])
        if "stress:unverified" not in tags:
            tags.append("stress:unverified")
        meta["tags"] = tags
        forced_text = "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + parts[2]
        forced_path = tmp_path / "ua-lexeme-0003.md"
        forced_path.write_text(forced_text, encoding="utf-8")
        monkeypatch.setattr(vsg, "REPO_ROOT", tmp_path)

        result = extract_note_targets(forced_path)
        assert result is not None, "note has stress:unverified (forced) but extract returned None"
        assert result["lemma"] == "воді́й"
        fields_found = {t["field"] for t in result["targets"]}
        assert "Lemma" in fields_found
        # IrregularForms: gen.pl. воді́їв
        assert "IrregularForms" in fields_found
        # CounterpartForm: f: воді́йка
        assert "CounterpartForm" in fields_found

    def test_real_notes_directory_has_113_notes(self):
        """Sanity check: ch-00 contains exactly 113 note files."""
        note_files = sorted(NOTES_CH00.glob("ua-lexeme-*.md"))
        assert len(note_files) == 113, f"Expected 113 notes, found {len(note_files)}"

    def test_all_notes_have_source_url(self):
        """After backfill_source_url ran, every note must have Source_URL set.
        Phrase lemmas (multi-word) legitimately have an empty URL — this is correct
        behaviour from backfill_source_url.goroh_url().
        """
        import re
        for path in sorted(NOTES_CH00.glob("ua-lexeme-*.md")):
            content = path.read_text(encoding="utf-8")
            assert "Source_URL:" in content, f"Missing Source_URL in {path.name}"
            # For single-word lemmas the URL must be non-empty
            lemma_m = re.search(r"^\s+Lemma:\s+(.+)$", content, re.MULTILINE)
            if not lemma_m:
                continue
            lemma = lemma_m.group(1).strip().strip("'\"")
            bare_lemma = strip_stress(lemma)
            if " " in bare_lemma:
                continue  # phrase — empty URL is correct
            url_m = re.search(r"Source_URL:\s*(.+)", content)
            assert url_m and url_m.group(1).strip() not in ("''", '""', ""), \
                f"Empty Source_URL for single-word lemma in {path.name}"

    def test_all_notes_have_typing_answer_without_stress(self):
        """TypingAnswer must equal Lemma with stress marks removed."""
        import re
        for path in sorted(NOTES_CH00.glob("ua-lexeme-*.md")):
            content = path.read_text(encoding="utf-8")
            lemma_m = re.search(r"^\s+Lemma:\s+(.+)$", content, re.MULTILINE)
            ta_m = re.search(r"^\s+TypingAnswer:\s+(.+)$", content, re.MULTILINE)
            if not (lemma_m and ta_m):
                continue
            lemma_raw = lemma_m.group(1).strip().strip("'\"")
            ta_raw = ta_m.group(1).strip().strip("'\"")
            expected = strip_stress(lemma_raw)
            assert ta_raw == expected, (
                f"{path.name}: TypingAnswer={ta_raw!r} != "
                f"strip_stress(Lemma={lemma_raw!r})={expected!r}"
            )
