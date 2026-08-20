"""
tests/ua/test_typing_answer_sync.py

Guards _sync_typing_answer() in cnsf_canonicalize.py, added 2026-08-20.

The drift: 62 CNSF notes held a `TypingAnswer` that disagreed with the
stress-stripped slot join their own fields imply. ua-lexeme-0114 stored
`приходити` where the note is a doublet whose card asks for
`приходити / прийти`; ua-lexeme-0488 stored the Perfective instead of the
Lemma. Found during the `_TypingSpec` rollout, 2026-08-19.

Not a live bug, and the tests below are written to keep it that way rather
than to fix a symptom: `import_note()` recomputes `TypingAnswer` from
`compute_typing_target()[1]` for every doublet and triplet and overwrites
whatever the file said, so Anki has always had the right value. What was wrong
was CNSF's standing as the source of truth -- the file is what a person reads,
and a reader of 0114 would draw the wrong conclusion about what gets typed.

The risk this file mostly exists to pin is the INVERSE of the drift. For
singlets `compute_typing_target()` returns None and the importer leaves
`TypingAnswer` exactly as authored, so for those the file is authoritative and
a canonicalisation pass must not touch it. Every phrase note and every non-verb
note is a singlet, and their values are hand-written and not derivable from
`Lemma` alone -- a pass that "helpfully" rewrote them would turn a
documentation problem into real data loss across most of the corpus.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.cnsf_canonicalize as canon  # noqa: E402
import tools.anki.sync.ua_lexeme_import as li  # noqa: E402
from tools.anki.lib.typing_target import compute_typing_target  # noqa: E402

AC = chr(0x0301)  # combining acute


class TestSharedImplementation:
    """compute_typing_target() moved to tools/anki/lib/typing_target.py so the
    canonicaliser and the importer compute the same join. If they ever diverge
    the drift comes straight back, silently."""

    def test_importer_reexports_the_shared_function(self):
        assert li.compute_typing_target is compute_typing_target

    def test_canonicaliser_uses_the_shared_function(self):
        assert canon.compute_typing_target is compute_typing_target

    def test_strip_stress_is_shared_too(self):
        from tools.anki.lib.typing_target import strip_stress

        assert li.strip_stress is strip_stress


class TestDoubletsAndTriplets:
    """The case the importer overwrites -- and therefore the case the file is
    allowed to be corrected to match."""

    def test_doublet_drift_is_corrected(self):
        """ua-lexeme-0114's shape: a doublet storing only the Lemma."""
        fields = {
            "Lemma": f"прихо{AC}дити",
            "ImperfectiveUnidirectional": "",
            "Perfective": f"прийти{AC}",
            "TypingAnswer": "приходити",
        }
        assert canon._sync_typing_answer(fields) is True
        assert fields["TypingAnswer"] == "приходити / прийти"

    def test_the_perfective_standing_in_for_the_lemma_is_corrected(self):
        """ua-lexeme-0488's shape: the wrong one of the two forms stored."""
        fields = {
            "Lemma": f"дозволя{AC}ти",
            "ImperfectiveUnidirectional": "",
            "Perfective": f"дозво{AC}лити",
            "TypingAnswer": "дозволити",
        }
        assert canon._sync_typing_answer(fields) is True
        assert fields["TypingAnswer"] == "дозволяти / дозволити"

    def test_triplet_join_keeps_slot_order(self):
        """Lemma -> ImperfectiveUnidirectional -> Perfective, the same order
        every other computed field uses. A join in the wrong order would still
        "match" a naive set comparison, so assert the string."""
        fields = {
            "Lemma": f"ходи{AC}ти",
            "ImperfectiveUnidirectional": "йти",
            "Perfective": f"піти{AC}",
            "TypingAnswer": "wrong",
        }
        canon._sync_typing_answer(fields)
        assert fields["TypingAnswer"] == "ходити / йти / піти"

    def test_stress_is_stripped_from_the_answer_form(self):
        """`TypingAnswer` is the no-stress tier; `TypingTarget_UA` keeps the
        marks. Storing a stressed value here would silently demote every
        unstressed answer."""
        fields = {
            "Lemma": f"ходи{AC}ти",
            "ImperfectiveUnidirectional": "",
            "Perfective": f"піти{AC}",
            "TypingAnswer": "",
        }
        canon._sync_typing_answer(fields)
        assert AC not in fields["TypingAnswer"]

    def test_an_already_correct_note_is_left_alone(self):
        """585 of 585 lexeme notes run through this on every `make ua-lexeme-fix`.
        Reporting a change when there isn't one would make --check permanently
        red."""
        fields = {
            "Lemma": f"ходи{AC}ти",
            "ImperfectiveUnidirectional": "",
            "Perfective": f"піти{AC}",
            "TypingAnswer": "ходити / піти",
        }
        assert canon._sync_typing_answer(fields) is False


class TestSingletsAreNeverTouched:
    """The inverse risk, and the more expensive one to get wrong."""

    def test_a_plain_singlet_keeps_its_authored_value(self):
        fields = {
            "Lemma": f"ма{AC}ти",
            "ImperfectiveUnidirectional": "",
            "Perfective": "",
            "TypingAnswer": "мати",
        }
        assert canon._sync_typing_answer(fields) is False
        assert fields["TypingAnswer"] == "мати"

    def test_a_phrase_note_is_not_rewritten_from_its_lemma(self):
        """ua-lexeme-0532: a multi-word phrase whose TypingAnswer is authored,
        not derived. This is the case that would lose real content."""
        fields = {
            "Lemma": f"розве{AC}дення ове{AC}ць",
            "ImperfectiveUnidirectional": "",
            "Perfective": "",
            "TypingAnswer": "розведення овець",
        }
        assert canon._sync_typing_answer(fields) is False
        assert fields["TypingAnswer"] == "розведення овець"

    def test_a_noun_with_an_unrelated_typing_answer_survives(self):
        """Deliberately an odd value: the point is that nothing derives it, so
        nothing may overwrite it."""
        fields = {
            "Lemma": f"ви{AC}бір",
            "TypingAnswer": "вибір",
        }
        assert canon._sync_typing_answer(fields) is False
        assert fields["TypingAnswer"] == "вибір"

    def test_missing_aspect_keys_do_not_raise(self):
        """Non-verb notes may not carry the aspect keys at all."""
        fields = {"Lemma": f"сту{AC}л", "TypingAnswer": "стул"}
        assert canon._sync_typing_answer(fields) is False

    def test_none_valued_fields_are_treated_as_blank(self):
        """A YAML key present with no value loads as None, not ''. Passing that
        into a join would raise, and the canonicaliser runs under a pre-commit
        hook where a traceback blocks the commit."""
        fields = {
            "Lemma": f"ма{AC}ти",
            "ImperfectiveUnidirectional": None,
            "Perfective": None,
            "TypingAnswer": "мати",
        }
        assert canon._sync_typing_answer(fields) is False


class TestScoping:
    """Only UA_Lexeme carries these fields; the other four note types must pass
    through the canonicaliser untouched."""

    def test_only_ua_lexeme_notes_are_synced(self):
        meta = {
            "schema": "cnsf/v0",
            "note_id": "ua-verb-0001",
            "anki": {"model": "UA_Verb", "deck": "UA::Verbs"},
            "note_type": "ua_verb",
            "tags": [],
            "fields": {
                "Lemma": f"ходи{AC}ти",
                "Perfective": f"піти{AC}",
                "TypingAnswer": "whatever",
            },
        }
        out = canon._normalize_meta(dict(meta), Path("ua-verb-0001.md"))
        assert out["fields"]["TypingAnswer"] == "whatever"

    def test_a_lexeme_note_is_synced_through_normalize_meta(self):
        """End-to-end through the entry point the hook actually calls, not just
        the helper -- the wiring is as easy to get wrong as the logic."""
        meta = {
            "schema": "cnsf/v0",
            "note_id": "ua-lexeme-0001",
            "anki": {"model": "UA_Lexeme", "deck": "UA::Recognition::UA→EN"},
            "note_type": "ua_lexeme",
            "tags": [],
            "fields": {
                "Lemma": f"ходи{AC}ти",
                "Perfective": f"піти{AC}",
                "TypingAnswer": "ходити",
            },
        }
        out = canon._normalize_meta(dict(meta), Path("ua-lexeme-0001.md"))
        assert out["fields"]["TypingAnswer"] == "ходити / піти"
