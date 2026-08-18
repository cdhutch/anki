"""
tests/ua/test_cnsf_field_order.py

Unit tests for CNSF `fields:` key-order canonicalization in
tools/anki/cnsf_canonicalize.py (_canonical_field_order / CANON_FIELD_ORDER),
added 2026-08-18.

Why this exists: `cnsf_canonicalize.py` canonicalized only the SEVEN top-level
keys (CANON_TOP_KEYS). Key order *inside* `fields:` was whatever each file
happened to be authored with, and every setdefault()-style backfill appended
new keys wherever that file ended -- the same drift the live Anki models had
(see sync_field_order() in setup_ua_note_types.py), just on the file side.
A 12-note sample across ch-00/ch-08/ch-09 turned up THREE distinct orders,
none matching the model's. cmd_check() couldn't catch it, because
_top_level_key_order() only ever looked at the top level.

Per Craig 2026-08-18 ("Option A"): field order is driven by the SAME FIELDS
constants that drive the live Anki models, imported directly rather than
duplicated here -- so the two can't drift apart. These tests pin the parts of
that behaviour which are easy to break silently:

  - the CNSF key set is deliberately a SUBSET of the Anki field set (computed
    fields are never authored), so "correct" means matching RELATIVE order of
    the authored subset, not equality with the constant;
  - non-UA note types (B737) must pass through untouched;
  - nothing may be added, dropped, or have its value changed -- order only.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.cnsf_canonicalize as cc  # noqa: E402


def _lexeme_fields(order):
    """Build a fields dict in the given key order, with traceable values."""
    return {k: f"value-of-{k}" for k in order}


class TestReordering:
    def test_scrambled_lexeme_fields_land_in_constant_order(self):
        const = list(cc.CANON_FIELD_ORDER["ua_lexeme"])
        authored = [k for k in reversed(const)]
        out = cc._canonical_field_order("ua_lexeme", _lexeme_fields(authored))
        assert list(out.keys()) == const

    def test_subset_of_keys_keeps_constant_relative_order(self):
        """The real corpus case: CNSF omits the computed fields entirely."""
        const = list(cc.CANON_FIELD_ORDER["ua_lexeme"])
        authored_set = [k for k in const if not k.startswith("_")]
        scrambled = list(reversed(authored_set))
        out = cc._canonical_field_order("ua_lexeme", _lexeme_fields(scrambled))
        assert list(out.keys()) == authored_set

    def test_every_ua_note_type_reorders(self):
        for note_type, const in cc.CANON_FIELD_ORDER.items():
            scrambled = list(reversed(list(const)))
            out = cc._canonical_field_order(note_type, _lexeme_fields(scrambled))
            assert list(out.keys()) == list(const), note_type

    def test_already_ordered_is_unchanged(self):
        const = list(cc.CANON_FIELD_ORDER["ua_verb"])
        fields = _lexeme_fields(const)
        assert list(cc._canonical_field_order("ua_verb", fields).keys()) == const

    def test_idempotent(self):
        const = list(cc.CANON_FIELD_ORDER["ua_lexeme"])
        once = cc._canonical_field_order("ua_lexeme", _lexeme_fields(reversed(const)))
        twice = cc._canonical_field_order("ua_lexeme", once)
        assert list(once.keys()) == list(twice.keys())


class TestUnknownKeys:
    def test_unknown_key_trails_rather_than_being_dropped(self):
        const = list(cc.CANON_FIELD_ORDER["ua_lexeme"])
        fields = _lexeme_fields(["Experimental_Key"] + const)
        out = cc._canonical_field_order("ua_lexeme", fields)
        assert list(out.keys()) == const + ["Experimental_Key"]

    def test_multiple_unknown_keys_keep_their_relative_order(self):
        const = list(cc.CANON_FIELD_ORDER["ua_grammar"])
        fields = _lexeme_fields(["Zeta_Extra"] + const + ["Alpha_Extra"])
        out = cc._canonical_field_order("ua_grammar", fields)
        # Not alphabetised, not reversed -- authored order among unknowns.
        assert list(out.keys()) == const + ["Zeta_Extra", "Alpha_Extra"]


class TestNonUaNoteTypesUntouched:
    def test_b737_note_type_passes_through_unchanged(self):
        authored = ["Back", "Front", "NoteID", "Source"]
        out = cc._canonical_field_order("b737_structured", _lexeme_fields(authored))
        assert list(out.keys()) == authored

    def test_empty_note_type_passes_through_unchanged(self):
        authored = ["Zebra", "Apple"]
        out = cc._canonical_field_order("", _lexeme_fields(authored))
        assert list(out.keys()) == authored


class TestNoDataLoss:
    """Order only -- never add, drop, or alter a value."""

    def test_key_set_and_values_preserved(self):
        const = list(cc.CANON_FIELD_ORDER["ua_lexeme"])
        fields = _lexeme_fields(list(reversed(const)) + ["Unknown_Key"])
        out = cc._canonical_field_order("ua_lexeme", fields)
        assert set(out.keys()) == set(fields.keys())
        assert len(out) == len(fields)
        for k, v in fields.items():
            assert out[k] == v

    def test_missing_optional_keys_are_not_invented(self):
        """Reordering must not backfill -- that's _normalize_meta's job."""
        fields = _lexeme_fields(["Verification Notes", "EN_Gloss", "Lemma", "NoteID"])
        out = cc._canonical_field_order("ua_lexeme", fields)
        assert list(out.keys()) == ["NoteID", "Lemma", "EN_Gloss", "Verification Notes"]
        assert len(out) == 4


class TestDriftDetection:
    """cmd_check() must name field-order drift specifically -- it's always
    fixable by --write and never needs a content decision, unlike an
    apostrophe or boolean-coercion fix."""

    def _note(self, keys):
        lines = ["---", "schema: cnsf/v0", "domain: ua", "note_type: ua_grammar",
                 "note_id: ua-grammar-0001",
                 "anki:", "  model: UA_Grammar", "  deck: UA::Test",
                 "tags:", "  - status:draft", "fields:"]
        lines += [f"  {k}: 'x'" for k in keys]
        lines += ["---", "", "body", ""]
        return "\n".join(lines)

    def test_drift_detected_when_order_wrong(self):
        const = list(cc.CANON_FIELD_ORDER["ua_grammar"])
        text = self._note(list(reversed(const)))
        assert cc._has_field_order_drift(text, Path("ua-grammar-0001.md")) is True

    def test_no_drift_when_order_correct(self):
        const = list(cc.CANON_FIELD_ORDER["ua_grammar"])
        text = self._note(const)
        assert cc._has_field_order_drift(text, Path("ua-grammar-0001.md")) is False

    def test_missing_optional_key_is_not_reported_as_order_drift(self):
        """A note merely missing a key is a field-SET issue for
        check_cnsf_field_schema.py, not an ordering one."""
        const = [k for k in cc.CANON_FIELD_ORDER["ua_grammar"] if k != "Extra"]
        text = self._note(const)
        assert cc._has_field_order_drift(text, Path("ua-grammar-0001.md")) is False

    def test_unparseable_text_returns_false_not_raises(self):
        assert cc._has_field_order_drift("not a cnsf file", Path("x.md")) is False


class TestSingleSourceOfTruth:
    """Option A's whole point: one list drives both Anki and CNSF order."""

    def test_constants_are_the_same_objects_the_setup_scripts_use(self):
        from tools.anki.setup.setup_ua_note_types import (
            FIELDS, GRAMMAR_FIELDS, VISUAL_FIELDS, VERB_FIELDS,
        )
        from tools.anki.setup.setup_ua_pvom_note_type import FIELDS as PVOM_FIELDS

        assert cc.CANON_FIELD_ORDER["ua_lexeme"] is FIELDS
        assert cc.CANON_FIELD_ORDER["ua_grammar"] is GRAMMAR_FIELDS
        assert cc.CANON_FIELD_ORDER["ua_visual"] is VISUAL_FIELDS
        assert cc.CANON_FIELD_ORDER["ua_verb"] is VERB_FIELDS
        assert cc.CANON_FIELD_ORDER["ua_pvom_infinitive"] is PVOM_FIELDS

    def test_all_five_ua_note_types_are_covered(self):
        assert set(cc.CANON_FIELD_ORDER) == {
            "ua_lexeme", "ua_grammar", "ua_visual", "ua_verb", "ua_pvom_infinitive",
        }

    def test_import_chain_stays_stdlib_only(self):
        """The cnsf-canonical pre-commit hook runs in an isolated venv that
        declares only pyyaml. If anything in the imported chain grows a
        third-party dependency, the hook breaks at commit time rather than
        here -- so assert it here instead."""
        import tools.anki.setup.setup_ua_note_types as s
        import tools.anki.setup.setup_ua_pvom_note_type as p
        import tools.anki.sync.tsv_to_anki as t

        stdlib = set(sys.stdlib_module_names)
        for mod in (s, p, t):
            src = Path(mod.__file__).read_text(encoding="utf-8")
            for line in src.splitlines():
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    root = line.split()[1].split(".")[0]
                    if root in ("__future__", "tools"):
                        continue
                    assert root in stdlib, f"{mod.__name__} imports non-stdlib {root!r}"
