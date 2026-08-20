"""
tests/ua/test_typeans_normalization.py

Guards normalizeTypeansText() -- the fix for the detached-stress-mark bug
(ua-lexeme-0532, reported 2026-08-08, root-caused and fixed 2026-08-18).

The bug: Anki's own diff renderer deliberately prepends U+00A0 to any chunk
that BEGINS with a combining mark, in rslib/src/typeanswer.rs --

    /// Prefixes a leading mark character with a non-breaking space to
    /// prevent it from joining the previous token.
    fn isolate_leading_mark(text: &str) -> Cow<'_, str> { ... }

-- and that nbsp lands INSIDE a .typeGood/.typeBad span. Both feedback scripts
reconstruct the typed answer by concatenating those spans' textContent, so they
swallow the nbsp; the string then matches no target and renders with a visible
gap before what looks like a detached accent. It only surfaces on a stress-mark
POSITION mismatch, since that is when the character-level diff splits a chunk
mid-grapheme -- which is why other mismatches never showed it.

This file tests the fix two ways, because the JS lives inside Python string
literals and can break in two independent ways:

  1. Escaping. `\\u00A0` in a non-raw Python string would collapse to a literal
     NBSP character in the emitted JS, and `\\\\u00A0` would emit an escaped
     backslash -- a regex matching a literal backslash followed by "u00A0",
     which silently never matches. Both are easy to introduce by editing the
     surrounding Python and impossible to see by eye. TestEmittedJavaScript
     pins the emitted bytes.

  2. Semantics. TestNormalizationSemantics ports the same regexes to Python and
     exercises the real corpus strings. Python and JS agree on these patterns
     (literal chars, one capture group, a BMP range), so this is a faithful
     check without requiring node in the test environment.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.setup.setup_ua_note_types as setup  # noqa: E402
import tools.anki.setup.setup_ua_pvom_note_type as pvom_setup  # noqa: E402
from tools.anki.lib.typeans_js import NORMALIZE_TYPEANS_JS  # noqa: E402

# Built with chr() rather than written as literals ON PURPOSE. An earlier draft
# of this very file wrote them as literal characters and immediately hit the
# bug it exists to catch: a raw NBSP is invisible in an editor and in a diff,
# so you cannot tell it apart from the escape sequence by eye. If these ever
# go back to being literals, this file stops proving anything.
NBSP = chr(0x00A0)
ACUTE = chr(0x0301)  # combining acute -- the stress mark used throughout the corpus
GRAVE = chr(0x0300)
COMBINING_RANGE = f"[{chr(0x0300)}-{chr(0x036F)}]"
NBSP_ESCAPE = "\\" + "u00A0"  # the two-token form JS must receive

SCRIPTS = [
    ("EN_UA_BACK", setup.EN_UA_BACK),
    ("UA_PVOM_Infinitive FEEDBACK_SCRIPT", pvom_setup.FEEDBACK_SCRIPT),
]


class TestEmittedJavaScript:
    """Both scripts must define the helper AND route the reconstruction
    through it. PVOM uses the identical #typeans technique, so it has the
    identical bug -- and every PVOM answer carries a stress mark."""

    def test_helper_is_defined_in_both_scripts(self):
        for label, js in SCRIPTS:
            assert "function normalizeTypeansText(s)" in js, label

    def test_reconstruction_routes_through_the_helper(self):
        for label, js in SCRIPTS:
            assert "normalizeTypeansText(" in js.split(
                "function normalizeTypeansText(s)", 1
            )[1], f"{label}: helper defined but never called"

    def test_emits_a_real_escape_not_a_literal_nbsp(self):
        """A literal NBSP in the source would still *work* as a regex today,
        but it is invisible in a diff and one stray edit from breaking."""
        for label, js in SCRIPTS:
            body = _helper_body(js)
            assert NBSP not in body, f"{label}: literal NBSP char leaked into the JS"
            assert NBSP_ESCAPE in body, f"{label}: expected a \\u00A0 escape"

    def test_escape_is_not_double_backslashed(self):
        r"""`\\u00A0` in the emitted JS is a regex matching a literal backslash
        followed by 'u00A0' -- it would never match, and the bug would silently
        return with all tests still green unless we check for this."""
        for label, js in SCRIPTS:
            assert "\\\\u00A0" not in _helper_body(js), (
                f"{label}: escape was double-backslashed; the regex can never match"
            )

    def test_both_scripts_emit_identical_helper_bodies(self):
        """They used to be deliberate copies, and this caught the case where
        one was fixed and the other wasn't. Since 2026-08-20 there is one
        shared body (tools/anki/lib/typeans_js.py), so this is now a guard
        against a copy being reintroduced rather than against drift."""
        bodies = {label: _helper_body(js) for label, js in SCRIPTS}
        assert len(set(bodies.values())) == 1, bodies

    def test_both_scripts_embed_the_shared_constant_verbatim(self):
        """The point of hoisting the helper into tools/anki/lib/typeans_js.py
        is that "the two copies drifted" stops being a reachable state. A
        substring check, not an equality one, because each script splices the
        constant into a larger template. If someone re-inlines the helper this
        fails even if the two inlined bodies happen to agree with each other --
        which is exactly the state we just left."""
        for label, js in SCRIPTS:
            assert NORMALIZE_TYPEANS_JS in js, (
                f"{label}: does not embed NORMALIZE_TYPEANS_JS verbatim -- the "
                f"helper looks re-inlined"
            )


def _helper_body(js: str) -> str:
    m = re.search(r"function normalizeTypeansText\(s\) \{(.*?)\n\s*\}", js, re.S)
    assert m, "normalizeTypeansText() not found"
    return m.group(1)


def _normalize(s: str) -> str:
    """Python port of the emitted JS, derived from the emitted source itself
    rather than hardcoded -- so if the JS regex changes and this test file
    doesn't, the port changes with it."""
    return re.sub(NBSP + f"({COMBINING_RANGE})", r"\1", s).replace(NBSP, " ")


class TestNormalizationSemantics:
    def test_the_reported_bug_ua_lexeme_0532(self):
        """Lemma 'розве́дення ове́ць' -- Craig typed the stress correctly, the
        diff split mid-grapheme, and the reconstruction picked up Anki's
        isolation nbsp, so it matched nothing."""
        target = f"розве{ACUTE}дення ове{ACUTE}ць"
        from_anki = f"розве{NBSP}{ACUTE}дення ове{ACUTE}ць"
        assert _normalize(from_anki) == target

    def test_real_space_in_a_phrase_answer_survives(self):
        """The phrase notes are exactly where a too-eager nbsp strip would do
        damage -- 'розведенняовець' would grade INCORRECT forever."""
        s = f"розве{ACUTE}дення ове{ACUTE}ць"
        assert _normalize(s) == s
        assert " " in _normalize(s)

    def test_bare_nbsp_becomes_an_ordinary_space(self):
        """Defensive: today's Anki preserves real spaces via white-space:
        pre-wrap rather than entity-encoding them. If that ever changes, this
        keeps phrase answers grading correctly instead of silently breaking."""
        assert _normalize(f"розве{ACUTE}дення{NBSP}ове{ACUTE}ць") == (
            f"розве{ACUTE}дення ове{ACUTE}ць"
        )

    def test_multiple_isolations_in_one_answer(self):
        """Triplet notes type three stressed forms at once (ua-lexeme-0581),
        so a single answer can carry several isolation artifacts."""
        assert _normalize(f"ходи{NBSP}{ACUTE}ти / йти / пі{NBSP}{ACUTE}ти") == (
            f"ходи{ACUTE}ти / йти / пі{ACUTE}ти"
        )

    def test_clean_input_is_untouched(self):
        """No regression on the overwhelmingly common path."""
        for s in (f"вхо{ACUTE}дити", "входити", "", f"ходи{ACUTE}ти / йти / пі{ACUTE}ти"):
            assert _normalize(s) == s

    def test_other_combining_marks_in_range_also_isolate(self):
        """isolate_leading_mark() keys off Unicode general category Mark, not
        the acute specifically, so the fix must cover the combining range --
        not just U+0301."""
        assert _normalize(f"те{NBSP}{GRAVE}ст") == f"те{GRAVE}ст"

    def test_nbsp_before_a_non_mark_is_not_swallowed(self):
        """Only the mark case is Anki's artifact; anything else is real
        content and must survive as a space, not vanish."""
        assert _normalize(f"два{NBSP}слова") == "два слова"
        assert len(_normalize(f"два{NBSP}слова")) == len("два слова")
