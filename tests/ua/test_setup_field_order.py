"""
tests/ua/test_setup_field_order.py

Unit tests for sync_field_order() in tools/anki/setup/setup_ua_note_types.py
(and its mirror in setup_ua_pvom_note_type.py) -- the field-order enforcement
pass added 2026-08-18.

Why this exists: before that pass, the FIELDS-style constants in those two
setup scripts had no bearing on an already-created model's field order.
`inOrderFields` is only honoured by `createModel`; `update_model()` and its
siblings only ever called `modelFieldAdd` (which APPENDS) and
`modelFieldRemove`, and `modelFieldReposition` appeared nowhere in the repo.
So live field order was "whatever order fields happened to get added in",
which is exactly what `inspect_note_type_fields.py` found against live Anki on
2026-08-18 -- see sync_field_order()'s docstring and CLAUDE.md item 20.

These tests drive the function against a fake AnkiConnect that models Anki's
actual reposition semantics (remove the field from its current position,
re-insert it at the requested index), using the REAL live field orders
captured from Craig's collection on 2026-08-18. They assert two things the
implementation has to get right:

  1. Convergence -- an insertion sort that repositions desired[i] to index i,
     in ascending order, actually lands on the target order.
  2. The no-op guard -- when live order already matches, ZERO AnkiConnect
     calls are made. This one matters beyond tidiness: repositioning fields is
     a schema modification, so an unguarded pass would make Anki demand a full
     AnkiWeb upload on every single `make ua-setup-*` run.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.setup.setup_ua_note_types as setup  # noqa: E402
import tools.anki.setup.setup_ua_pvom_note_type as pvom_setup  # noqa: E402


# Real live field orders, captured 2026-08-18 via
# `python tools/anki/inspect/inspect_note_type_fields.py` against Craig's
# collection. Kept verbatim rather than synthesised: the drift these encode
# (the 2026-08-11 tail appended past `Verification Notes`, etc.) is the actual
# thing this function exists to repair.
#
# One deliberate deviation from the capture, 2026-08-19: the last entry was
# `_EuphonySlots`, renamed to `_TypingSpec` by the Option B refactor. It is
# updated here rather than left verbatim because sync_field_order() runs LAST
# in each update function, after the modelFieldAdd/modelFieldRemove passes --
# so the live list it actually sees already has the old field dropped and the
# new one appended. A verbatim-but-stale capture would be testing a state that
# can no longer reach the function.
LIVE_LEXEME = [
    "NoteID", "Lemma", "PartOfSpeech", "Gender", "Perfective",
    "ImperfectiveUnidirectional", "EN_Gloss", "Govt_Case", "IrregularForms",
    "CounterpartForm", "VerbMotion_Pair", "ConfusableSet", "CrossLang_Analog",
    "EuphonyNote", "TypingAnswer", "UA_Example", "EN_Example", "Tags_Ch",
    "Source_URL", "Source_Note", "Mnemonic_EN", "CompareA", "CompareB",
    "CompareScenario", "CompareC", "CompareD", "_IsHomograph",
    "Homograph_SenseA", "Homograph_SenseB", "AspectCue", "TypingTarget_UA",
    "_AspectLabel", "Verification Notes", "Lemma_Euphony", "Perfective_Euphony",
    "ImperfectiveUnidirectional_Euphony", "_UA_EN_DisplayLemma", "_TypingSpec",
]

LIVE_VERB = [
    "NoteID", "Lemma", "Aspect", "VerbClass", "FreqSource",
    "Pres_1sg", "Pres_2sg", "Pres_3sg", "Pres_1pl", "Pres_2pl", "Pres_3pl",
    "Imperative_2sg", "Imperative_1pl", "Imperative_2pl",
    "Past_1sg_m", "Past_1sg_f", "Past_1sg_n", "Past_3pl",
    "Participle_Active_Present", "Participle_Adverbial_Present",
    "Participle_Impersonal_Past", "Participle_Adverbial_Past",
    "Participle_Passive_Past",
    "Tags_Conj", "Source_Note", "Verification Notes",
]

LIVE_PVOM = [
    "NoteID", "Prefix", "Tags_Ch", "Source_Note", "Verification Notes",
    "Walking_Multi_UA", "Walking_Multi_Typing",
    "Walking_Uni_UA", "Walking_Uni_Typing",
    "Vehicle_Multi_UA", "Vehicle_Multi_Typing",
    "Vehicle_Uni_UA", "Vehicle_Uni_Typing",
    "Walking_Multi_Euphony", "Walking_Uni_Euphony",
    "Vehicle_Multi_Euphony", "Vehicle_Uni_Euphony",
]

LIVE_GRAMMAR = list(setup.GRAMMAR_FIELDS)   # already matches its constant
LIVE_VISUAL = list(setup.VISUAL_FIELDS)     # already matches its constant


class FakeAnki:
    """Stand-in for AnkiConnect that models Anki's reposition semantics.

    Anki's reposition_field removes the field from wherever it currently sits
    and re-inserts it at the given index -- NOT a swap. Getting that wrong is
    the difference between an insertion sort that converges and one that
    scrambles the model, so the fake implements the real behaviour rather than
    just recording calls.
    """

    def __init__(self, fields, envelope=False):
        self.fields = list(fields)
        self.calls = []
        # setup_ua_pvom_note_type.anki_request returns the raw AnkiConnect
        # envelope; setup_ua_note_types imports the unwrapping one from
        # tsv_to_anki. sync_field_order has to cope with both.
        self.envelope = envelope

    def __call__(self, action, params=None, **kwargs):
        params = params or {}
        self.calls.append((action, params))
        if action == "modelFieldNames":
            return {"result": list(self.fields)} if self.envelope else list(self.fields)
        if action == "modelFieldReposition":
            name = params["fieldName"]
            self.fields.remove(name)
            self.fields.insert(params["index"], name)
            return {"result": None} if self.envelope else None
        raise AssertionError(f"unexpected AnkiConnect action: {action}")

    @property
    def reposition_calls(self):
        return [p for a, p in self.calls if a == "modelFieldReposition"]


def _run(monkeypatch, module, live, desired, envelope=False, **call_kwargs):
    fake = FakeAnki(live, envelope=envelope)
    monkeypatch.setattr(module, "anki_request", fake)
    changed = module.sync_field_order(**call_kwargs, desired_fields=desired)
    return fake, changed


class TestConvergence:
    """After the pass, live order must equal the constant's order exactly."""

    def test_lexeme_reaches_constant_order(self, monkeypatch):
        fake, changed = _run(
            monkeypatch, setup, LIVE_LEXEME, setup.FIELDS,
            model_name=setup.MODEL_NAME,
        )
        assert changed is True
        assert fake.fields == list(setup.FIELDS)

    def test_verb_reaches_constant_order(self, monkeypatch):
        fake, changed = _run(
            monkeypatch, setup, LIVE_VERB, setup.VERB_FIELDS,
            model_name=setup.VERB_MODEL_NAME,
        )
        assert changed is True
        assert fake.fields == list(setup.VERB_FIELDS)

    def test_pvom_reaches_constant_order(self, monkeypatch):
        fake = FakeAnki(LIVE_PVOM, envelope=True)
        monkeypatch.setattr(pvom_setup, "anki_request", fake)
        changed = pvom_setup.sync_field_order(pvom_setup.FIELDS)
        assert changed is True
        assert fake.fields == list(pvom_setup.FIELDS)

    def test_no_field_is_lost_or_duplicated(self, monkeypatch):
        fake, _ = _run(
            monkeypatch, setup, LIVE_LEXEME, setup.FIELDS,
            model_name=setup.MODEL_NAME,
        )
        assert sorted(fake.fields) == sorted(LIVE_LEXEME)
        assert len(fake.fields) == len(set(fake.fields))


class TestNoOpGuard:
    """Reordering is a schema mod -- an unguarded pass would make Anki demand a
    full AnkiWeb upload on every routine `make ua-setup-*` run."""

    def test_grammar_already_ordered_makes_no_reposition_calls(self, monkeypatch):
        fake, changed = _run(
            monkeypatch, setup, LIVE_GRAMMAR, setup.GRAMMAR_FIELDS,
            model_name=setup.GRAMMAR_MODEL_NAME,
        )
        assert changed is False
        assert fake.reposition_calls == []

    def test_visual_already_ordered_makes_no_reposition_calls(self, monkeypatch):
        fake, changed = _run(
            monkeypatch, setup, LIVE_VISUAL, setup.VISUAL_FIELDS,
            model_name=setup.VISUAL_MODEL_NAME,
        )
        assert changed is False
        assert fake.reposition_calls == []

    def test_second_run_is_a_no_op(self, monkeypatch):
        """The pass must be idempotent -- run it twice, second run does nothing."""
        fake, first = _run(
            monkeypatch, setup, LIVE_LEXEME, setup.FIELDS,
            model_name=setup.MODEL_NAME,
        )
        assert first is True
        monkeypatch.setattr(setup, "anki_request", fake)
        fake.calls.clear()
        again = setup.sync_field_order(setup.MODEL_NAME, setup.FIELDS)
        assert again is False
        assert fake.reposition_calls == []


class TestPartialOverlap:
    """Only fields present on BOTH sides get moved."""

    def test_field_in_constant_but_not_live_is_skipped(self, monkeypatch):
        live = [f for f in setup.GRAMMAR_FIELDS if f != "Extra"]
        fake, changed = _run(
            monkeypatch, setup, live, setup.GRAMMAR_FIELDS,
            model_name=setup.GRAMMAR_MODEL_NAME,
        )
        # Nothing to do: the survivors are already in constant-relative order,
        # and the absent field must not be conjured into a reposition call.
        assert changed is False
        assert "Extra" not in fake.fields

    def test_unknown_live_field_settles_at_the_end(self, monkeypatch):
        """A field the remove pass deliberately left in place must not block the
        reorder -- it just ends up after everything the constant knows about."""
        live = ["Legacy_Orphan"] + LIVE_GRAMMAR
        fake, changed = _run(
            monkeypatch, setup, live, setup.GRAMMAR_FIELDS,
            model_name=setup.GRAMMAR_MODEL_NAME,
        )
        assert changed is True
        assert fake.fields == list(setup.GRAMMAR_FIELDS) + ["Legacy_Orphan"]
