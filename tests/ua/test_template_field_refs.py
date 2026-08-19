"""
tests/ua/test_template_field_refs.py

Every {{...}} replacement in every card template must resolve to a field that
actually exists on that note type (or to one of Anki's built-in specials).

Why this exists (2026-08-19): `make ua-setup-lexeme` died mid-run with

    AnkiConnect error for updateModelTemplates: Card template 2 in note type
    'UA_Lexeme' has a problem.<br>Field '...' not found.

The offending "field" was literally named `...`. Nothing referenced a missing
field on purpose -- a comment inside EN_UA_BACK described the typing target by
writing a `type:...` example WITH braces around it. Anki scans the entire
template body for replacements and has no concept of a comment: not JS `//`,
not HTML `<!-- -->`. A doubled curly brace is a field reference wherever it
appears, so prose about templates becomes template code.

Three things make this worth a permanent test rather than a one-line fix:

  1. It is invisible in review. The line reads as documentation, and the
     surrounding syntax is a comment in both languages a reader is thinking in.
  2. It fails at AnkiConnect, not at import, so no amount of Python-level
     testing sees it -- and it fails PARTWAY THROUGH update_model(), after
     modelFieldAdd has already run, leaving the live model in a half-migrated
     state that has to be re-converged by re-running.
  3. An identical brace-wrapped example had been sitting in UA_EN_FRONT since
     2026-08-04 (the `_UA_EN_DisplayLemma` writeup) without ever tripping
     anything -- Anki appears to tolerate an unresolvable type-replacement on
     a FRONT while rejecting it on a BACK. So the corpus already contained a
     dormant instance of this bug, and only the second one was ever noticed.
     This test finds them regardless of which side they land on.

Scope is deliberately every template list in both setup modules, not just the
one that broke, since the hazard is a property of Anki's parser rather than of
any particular template.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.setup.setup_ua_note_types as setup  # noqa: E402
import tools.anki.setup.setup_ua_pvom_note_type as pvom_setup  # noqa: E402

# Anki's built-in replacements -- valid in a template without being fields.
# https://docs.ankiweb.net/templates/fields.html
SPECIAL = {
    "FrontSide", "Tags", "Type", "Deck", "Subdeck", "Card", "CardFlag",
    "Subject", "TopDeck",
}

# (label, templates, fields) for every model these two scripts manage.
MODELS = [
    ("UA_Lexeme", setup.CARD_TEMPLATES, setup.FIELDS),
    ("UA_Grammar", setup.GRAMMAR_CARD_TEMPLATES, setup.GRAMMAR_FIELDS),
    ("UA_Visual", setup.VISUAL_CARD_TEMPLATES, setup.VISUAL_FIELDS),
    ("UA_Verb", setup.VERB_CARD_TEMPLATES, setup.VERB_FIELDS),
    ("UA_PVOM_Infinitive", pvom_setup.CARD_TEMPLATES, pvom_setup.FIELDS),
]

# Non-greedy and DOTALL: a replacement never spans lines in practice, but the
# malformed ones we are hunting might, and we would rather see them than not.
REPLACEMENT = re.compile(r"\{\{(.*?)\}\}", re.S)


def _refs(body: str):
    """Yield (raw, field_name) for each replacement in a template body.

    Strips filters (`text:`, `type:`, `furigana:`, `cloze:`, chained ones like
    `text:nc:Foo`) and the section markers `#`/`^`/`/`, leaving the bare field
    name Anki has to resolve.
    """
    for m in REPLACEMENT.finditer(body):
        raw = m.group(1)
        name = raw.split(":")[-1].lstrip("#^/").strip()
        yield raw, name


def _tmpl_name(tmpl: dict) -> str:
    """setup_ua_note_types spells the key "Name"; setup_ua_pvom_note_type
    spells it "name". Both are fed to AnkiConnect, which accepts either, so
    neither is wrong -- but a guard that assumes one silently skips the other
    note type's templates, which is the failure mode this whole file exists to
    prevent."""
    return tmpl.get("Name") or tmpl["name"]


def _cases():
    for label, templates, fields in MODELS:
        for i, tmpl in enumerate(templates, 1):
            for side in ("Front", "Back"):
                yield pytest.param(
                    label, i, _tmpl_name(tmpl), side, tmpl[side], set(fields),
                    id=f"{label}-{i}-{_tmpl_name(tmpl)}-{side}",
                )


@pytest.mark.parametrize("label,index,name,side,body,fields", list(_cases()))
class TestEveryReplacementResolves:
    def test_all_field_refs_exist(self, label, index, name, side, body, fields):
        bad = [
            (raw, field)
            for raw, field in _refs(body)
            if field not in fields and field not in SPECIAL
        ]
        assert not bad, (
            f"{label} template {index} ({name}) {side} references "
            f"{[f for _, f in bad]}, which is not a field on {label} nor an "
            f"Anki special. Full replacement(s): {[r for r, _ in bad]}. "
            f"If this came from prose, the braces are the bug -- Anki parses "
            f"replacements inside comments too."
        )

    def test_no_empty_or_ellipsis_placeholder(self, label, index, name, side, body, fields):
        """The specific shape that broke ua-setup-lexeme on 2026-08-19: a
        placeholder written as if it were illustrative. Called out separately
        from the general check so the failure message names the cause instead
        of just reporting a field nobody ever meant to create."""
        placeholders = {"", "...", "…", "Field", "FieldName"}
        bad = [raw for raw, field in _refs(body) if field in placeholders]
        assert not bad, (
            f"{label} template {index} ({name}) {side} contains a placeholder "
            f"replacement {bad} -- almost certainly documentation prose that "
            f"Anki will read as a field reference and reject. Write the "
            f"example without doubled curly braces."
        )


class TestGuardCoversEverything:
    def test_every_model_in_both_setup_scripts_is_listed(self):
        """If someone adds a sixth note type, this test should start failing
        rather than the guard silently not covering it."""
        found = set()
        for module in (setup, pvom_setup):
            for attr in dir(module):
                value = getattr(module, attr)
                if (
                    isinstance(value, list)
                    and value
                    and isinstance(value[0], dict)
                    and {"Front", "Back"} <= set(value[0])
                    and ("Name" in value[0] or "name" in value[0])
                ):
                    found.add((module.__name__, attr))
        covered = {
            ("tools.anki.setup.setup_ua_note_types", "CARD_TEMPLATES"),
            ("tools.anki.setup.setup_ua_note_types", "GRAMMAR_CARD_TEMPLATES"),
            ("tools.anki.setup.setup_ua_note_types", "VISUAL_CARD_TEMPLATES"),
            ("tools.anki.setup.setup_ua_note_types", "VERB_CARD_TEMPLATES"),
            ("tools.anki.setup.setup_ua_pvom_note_type", "CARD_TEMPLATES"),
        }
        assert found == covered, (
            f"template lists present but not covered by MODELS: {found - covered}; "
            f"listed but no longer present: {covered - found}"
        )

    def test_the_2026_08_19_regression_would_be_caught(self):
        """Sanity-check the detector itself against the exact broken text,
        so a future refactor of _refs() cannot quietly stop catching it."""
        broken = '<div>{{Lemma}}</div>\n<script>\n// what {{type:...}} shows\n</script>'
        assert [f for _, f in _refs(broken)] == ["Lemma", "..."]
