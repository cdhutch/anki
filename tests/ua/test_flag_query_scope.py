"""
tests/ua/test_flag_query_scope.py

Guards the flag-query scoping added 2026-08-20.

Every UA importer used to pass the bare UA deck tree ("deck:UA::*") when
querying red/orange card flags. For the red set that was harmless -- an
importer only consults it for notes it is actually touching, so the
intersection happened anyway. The orange set is different: it is printed
unconditionally as a call-out, so every UA sync printed every orange-flagged
note in the whole corpus.

The symptom, from the first live `make ua-pvom` (2026-08-18): 26 orange-flagged
notes listed, not one of them PVOM -- all ua-lexeme-* plus ua-verb-0016 and
ua-visual-0001. Nothing was wrong, which is exactly why it is worth a test:
a call-out that is always the same 26 irrelevant lines is one you stop reading,
and then the day it says something real you miss it.

This is a scope test, not a behaviour test. It cannot reach Anki, so it asserts
the query STRINGS each importer builds. That is the layer the defect lived at.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.sync.ua_grammar_import as grammar  # noqa: E402
import tools.anki.sync.ua_lexeme_import as lexeme  # noqa: E402
import tools.anki.sync.ua_pvom_infinitive_import as pvom  # noqa: E402
import tools.anki.sync.ua_verb_import as verb  # noqa: E402
import tools.anki.sync.ua_visual_import as visual  # noqa: E402
from tools.anki.sync.tsv_to_anki import UA_DECK_TREE, flag_query_for_model  # noqa: E402

# Every importer, with the note type it is responsible for.
IMPORTERS = [
    ("ua_lexeme_import", lexeme, "UA_Lexeme"),
    ("ua_verb_import", verb, "UA_Verb"),
    ("ua_visual_import", visual, "UA_Visual"),
    ("ua_grammar_import", grammar, "UA_Grammar"),
    ("ua_pvom_infinitive_import", pvom, "UA_PVOM_Infinitive"),
]


class TestFlagQueryForModel:
    def test_constrains_by_note_type(self):
        q = flag_query_for_model("UA_Lexeme")
        assert "note:UA_Lexeme" in q

    def test_keeps_the_deck_tree(self):
        """Narrowing to the note type must not widen past the UA tree -- a
        UA_Lexeme note filed outside UA:: would be a different bug, and this
        query is not the place to discover it."""
        assert flag_query_for_model("UA_Lexeme").startswith(UA_DECK_TREE)

    def test_deck_query_is_overridable(self):
        assert flag_query_for_model("UA_Verb", "deck:Scratch") == (
            "deck:Scratch note:UA_Verb"
        )


@pytest.mark.parametrize("label,module,model", IMPORTERS, ids=[i[0] for i in IMPORTERS])
class TestEveryImporterIsScoped:
    def test_flag_query_names_its_own_note_type(self, label, module, model):
        assert f"note:{model}" in module.FLAG_DECK_QUERY, (
            f"{label}: FLAG_DECK_QUERY is {module.FLAG_DECK_QUERY!r} -- it will "
            f"report flags from note types this importer never touches"
        )

    def test_flag_query_is_not_the_bare_deck_tree(self, label, module, model):
        """The exact regression: FLAG_DECK_QUERY = "deck:UA::*"."""
        assert module.FLAG_DECK_QUERY != UA_DECK_TREE, (
            f"{label}: FLAG_DECK_QUERY reverted to the unscoped deck tree"
        )

    def test_model_name_matches_the_query(self, label, module, model):
        """MODEL_NAME is what the query is built from, so a typo there would
        silently scope the call-out to a note type that does not exist -- which
        reports nothing at all, the quietest possible failure."""
        assert module.MODEL_NAME == model


class TestAuditToolStaysWide:
    """ua_flag_audit.py deliberately keeps the whole-tree query: its job is to
    enumerate every flagged note in the corpus for the Phase 2 walkthrough, not
    to report on one sync run. Pinned so a future sweep of "fix the flag scope"
    does not narrow it by analogy."""

    def test_flag_audit_queries_the_whole_ua_tree(self):
        import tools.anki.inspect.ua_flag_audit as audit

        assert audit.FLAG_DECK_QUERY == UA_DECK_TREE
