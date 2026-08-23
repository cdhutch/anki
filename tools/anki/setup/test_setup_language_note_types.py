#!/usr/bin/env python3
"""Unit tests for setup_language_note_types.py (parameterized setup).

Tests template generation, domain config loading, field handling, and model setup
without touching actual Anki data (mocked AnkiConnect).

Usage:
    pytest tools/anki/setup/test_setup_language_note_types.py -v
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.setup.setup_language_note_types import (
    build_alphabet_templates,
    build_lexeme_templates,
    build_phoneme_templates,
    generate_templates,
    get_domain_example_field,
    get_foreign_glosses,
    load_domain_config,
)


@pytest.fixture
def cs_config():
    return load_domain_config("cs")


@pytest.fixture
def sk_config():
    return load_domain_config("sk")


@pytest.fixture
def de_config():
    return load_domain_config("de")


@pytest.fixture
def ipa_config():
    return load_domain_config("ipa")


class TestDomainConfigLoading:
    """Test loading domain configurations from YAML."""

    def test_load_cs_config(self, cs_config):
        assert cs_config["domain"] == "cs"
        assert cs_config["display_name"] == "Czech"
        assert "cs_lexeme" in cs_config["note_types"]
        assert "cs_alphabet" in cs_config["note_types"]

    def test_load_sk_config(self, sk_config):
        assert sk_config["domain"] == "sk"
        assert "sk_lexeme" in sk_config["note_types"]

    def test_load_de_config(self, de_config):
        assert de_config["domain"] == "de"
        assert "de_lexeme" in de_config["note_types"]
        assert "Article" in de_config["note_types"]["de_lexeme"]["fields"]

    def test_load_ipa_config(self, ipa_config):
        assert ipa_config["domain"] == "ipa"
        assert "ipa_phoneme" in ipa_config["note_types"]


class TestForeignGlosses:
    """Test foreign gloss detection and filtering."""

    def test_cs_glosses_excludes_ua(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        glosses = get_foreign_glosses("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        assert "UA_Gloss" not in glosses

    def test_cs_glosses_includes_available(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        glosses = get_foreign_glosses("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        assert "DE_Gloss" in glosses
        assert "SK_Gloss" in glosses


class TestDomainExampleField:
    """Test domain-specific example field name generation."""

    def test_cs_example_field(self):
        assert get_domain_example_field("cs") == "CS_Example"

    def test_sk_example_field(self):
        assert get_domain_example_field("sk") == "SK_Example"

    def test_de_example_field(self):
        assert get_domain_example_field("de") == "DE_Example"


class TestLexemeTemplates:
    """Test bidirectional lexeme template generation."""

    def test_cs_lexeme_templates(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        templates = build_lexeme_templates("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        assert len(templates) == 2
        assert templates[0]["Name"] == "CS→EN"
        assert templates[1]["Name"] == "EN→CS"

    def test_cs_lexeme_front_contains_lemma(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        templates = build_lexeme_templates("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        cs_to_en = templates[0]
        assert "{{Lemma}}" in cs_to_en["Front"]

    def test_cs_lexeme_back_contains_gloss(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        templates = build_lexeme_templates("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        cs_to_en = templates[0]
        assert "{{EN_Gloss}}" in cs_to_en["Back"]
        assert "DE:" in cs_to_en["Back"]

    def test_de_lexeme_includes_article(self, de_config):
        de_lexeme_fields = de_config["note_types"]["de_lexeme"]["fields"]
        templates = build_lexeme_templates("de_lexeme", de_lexeme_fields, "de", de_config)
        de_to_en = templates[0]
        assert "{{#Article}}" in de_to_en["Front"]


class TestAlphabetTemplates:
    """Test alphabet recognition template generation."""

    def test_cs_alphabet_template(self, cs_config):
        cs_alphabet_fields = cs_config["note_types"]["cs_alphabet"]["fields"]
        templates = build_alphabet_templates("cs_alphabet", cs_alphabet_fields, "cs", cs_config)
        assert len(templates) == 1
        assert templates[0]["Name"] == "Recognition"

    def test_alphabet_front_shows_letter(self, cs_config):
        cs_alphabet_fields = cs_config["note_types"]["cs_alphabet"]["fields"]
        templates = build_alphabet_templates("cs_alphabet", cs_alphabet_fields, "cs", cs_config)
        template = templates[0]
        assert "{{Letter}}" in template["Front"]
        assert "{{IPA_Symbol}}" in template["Front"]


class TestPhonemeTemplates:
    """Test IPA phoneme recognition template generation."""

    def test_ipa_phoneme_template(self, ipa_config):
        ipa_phoneme_fields = ipa_config["note_types"]["ipa_phoneme"]["fields"]
        templates = build_phoneme_templates("ipa_phoneme", ipa_phoneme_fields, "ipa", ipa_config)
        assert len(templates) == 1
        assert templates[0]["Name"] == "Recognition"

    def test_phoneme_back_shows_articulation(self, ipa_config):
        ipa_phoneme_fields = ipa_config["note_types"]["ipa_phoneme"]["fields"]
        templates = build_phoneme_templates("ipa_phoneme", ipa_phoneme_fields, "ipa", ipa_config)
        template = templates[0]
        assert "Manner" in template["Back"]
        assert "Place" in template["Back"]


class TestGenerateTemplates:
    """Test template generation dispatcher."""

    def test_lexeme_dispatch(self, cs_config):
        cs_lexeme_fields = cs_config["note_types"]["cs_lexeme"]["fields"]
        templates = generate_templates("cs_lexeme", cs_lexeme_fields, "cs", cs_config)
        assert len(templates) == 2
        assert templates[0]["Name"] == "CS→EN"

    def test_alphabet_dispatch(self, cs_config):
        cs_alphabet_fields = cs_config["note_types"]["cs_alphabet"]["fields"]
        templates = generate_templates("cs_alphabet", cs_alphabet_fields, "cs", cs_config)
        assert len(templates) == 1
        assert templates[0]["Name"] == "Recognition"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
