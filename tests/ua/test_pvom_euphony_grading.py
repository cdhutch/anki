"""
tests/ua/test_pvom_euphony_grading.py

Guards the UA_PVOM_Infinitive tier ladder -- bug (a), one-slot version, fixed
2026-08-20.

The defect, in one line of FEEDBACK_SCRIPT:

    } else if (typedAnswer !== null && euphonyAlts.indexOf(stripStress(typedAnswer).normalize('NFC')) !== -1) {

`euphonyAlts` was built by stress-STRIPPING each stored alternate, and the
typed answer was stripped again at the comparison, so `ухо́дити` and `уходити`
were the same string by the time they met. The branch then hardcoded
`✓ CORRECT / Accepted alternate spelling`. A euphonic alternate could
therefore never reach PERFECT no matter how carefully it was typed, and the
code structurally could not have told the two apart even if the branch order
had been right.

This is the same defect Option B closed on UA_Lexeme. It needs no `_TypingSpec`
here: `_TypingSpec` exists to remove positional alignment between two joined
strings, and PVOM has four card templates each testing exactly one form -- no
join, no slot indexing, nothing to align. The fix is the branch order plus
keeping the alternates stressed.

Craig's call, carried over from UA_Lexeme unchanged: a fully-stressed euphonic
alternate is not a lesser answer than the primary, just a different attested
one, so it earns PERFECT.

Coverage split follows test_typing_spec.py's precedent:

  - TestEmittedJavaScript pins the invariants that break silently while the
    file still parses -- above all the ORDER of the comparisons, which is the
    entire fix and which nothing else in the suite would notice.
  - TestTierLadder ports the ladder to Python and drives it with ua-pvom-0012's
    real field values. The port is a mirror, not a derivation, so
    TestEmittedJavaScript is what keeps it honest: if the JS ladder is
    reordered, the structural tests fail even though the port still passes.

The full matrix was exercised against the real emitted JS under node during
development. That harness is not committed (this repo has no JS test tooling);
to re-run it, extract FEEDBACK_SCRIPT's <script> body and drive it with a fake
document exposing feedback.dataset.{withStress,noStress,euphony}. NOTE if you
do: check for 'INCORRECT' BEFORE 'CORRECT' when classifying output --
"INCORRECT" contains "CORRECT" as a substring, a trap test_typing_spec.py's
header already records paying for once.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.setup.setup_ua_pvom_note_type as pvom_setup  # noqa: E402

AC = chr(0x0301)  # combining acute -- the stress mark used throughout the corpus

JS = pvom_setup.FEEDBACK_SCRIPT

# ua-pvom-0012 (prefix в-), the corpus's only PVOM note with populated
# *_Euphony values on all four slots, and therefore the note this fix is
# validated on. Written with an explicit AC rather than as pasted literals so
# stress placement is visible in the source instead of being an invisible
# combining character.
WALKING_MULTI_UA = f"вхо{AC}дити"  # вхо́дити
WALKING_MULTI_TYPING = "входити"
WALKING_MULTI_EUPHONY = f"ухо{AC}дити"  # ухо́дити

WALKING_UNI_UA = f"ввійти{AC}"  # ввійти́
WALKING_UNI_TYPING = "ввійти"
WALKING_UNI_EUPHONY = f"увійти{AC}"  # увійти́


class TestEmittedJavaScript:
    """Invariants that break silently while the script still parses."""

    def test_alternates_are_not_pre_stripped(self):
        """The single most important line. If the map callback strips stress on
        the way in, every alternate is indistinguishable from its unstressed
        form again and no branch ordering can recover the difference."""
        head, _, tail = JS.partition("var euphonyAlts = euphonyRaw.split('|')")
        assert tail, "euphonyAlts construction not found"
        builder = tail.split(";", 1)[0]
        assert "stripStress" not in builder, (
            "euphonyAlts is being stress-stripped as it is built -- this is the "
            "2026-08-20 defect returning; a stressed alternate can no longer "
            "reach PERFECT"
        )
        assert ".normalize('NFC')" in builder, (
            "alternates must still be NFC-normalized -- the comparison is now "
            "exact, so a normalization mismatch fails silently"
        )

    def test_stressed_comparisons_precede_unstressed_ones(self):
        """THE fix. Both PERFECT branches must be evaluated before either
        CORRECT branch; if `typedAnswer === noStress` or the stripped-alternate
        check runs first, a perfectly-stressed answer is captured by a lower
        tier and the bug is back with every other test still green."""
        order = [
            JS.index("typedAnswer === withStress"),
            JS.index("matchesAlternateWithStress(typedAnswer)"),
            JS.index("typedAnswer === noStress"),
            JS.index("matchesAlternateWithoutStress(typedAnswer)"),
        ]
        assert order == sorted(order), (
            f"grading branches are out of tier order: {order} -- a stressed "
            f"comparison now sits below an unstressed one"
        )

    def test_a_stressed_alternate_can_reach_perfect(self):
        """Before the fix, the only PERFECT branch compared against the primary
        alone. Assert the alternate branch actually awards PERFECT rather than
        having been reordered into place while still saying CORRECT."""
        branch = JS.split("matchesAlternateWithStress(typedAnswer)", 1)[1]
        branch = branch.split("} else if", 1)[0]
        assert "PERFECT" in branch, (
            "the stressed-alternate branch does not award PERFECT"
        )
        assert "INCORRECT" not in branch

    def test_the_unstressed_alternate_branch_still_awards_correct(self):
        """The other half of the ladder: dropping the stress mark must still be
        accepted, not demoted to INCORRECT. Over-eager tightening here is the
        symmetric risk to the bug being fixed -- the same one the 2026-08-18
        nbsp fix had to be checked against."""
        branch = JS.split("matchesAlternateWithoutStress(typedAnswer)", 1)[1]
        branch = branch.split("} else", 1)[0]
        assert "CORRECT" in branch
        assert "PERFECT" not in branch
        # "INCORRECT" contains "CORRECT"; assert the negative explicitly.
        assert "INCORRECT" not in branch

    def test_typed_answer_is_nfc_normalized(self):
        """Added alongside the fix. Every comparison in this script is now
        exact, so an NFD-composed keyboard would fail all of them where the old
        stress-stripping path used to (accidentally) paper over some of it."""
        # Slice to the end of the STATEMENT, not to the first semicolon: the
        # callback passed into the call has its own `;`, and an earlier draft
        # of this test cut there and reported a missing normalize that was
        # right below the cut.
        recon = JS.split("typedAnswer = normalizeTypeansText(", 1)[1]
        recon = recon.split(";", 1)[0] + ";" + recon.split(";")[1]
        assert ".normalize('NFC')" in recon, recon

    def test_null_reconstruction_is_handled_before_any_comparison(self):
        """A failed reconstruction must not be graded against a target at all.
        Hoisted to the top of the chain 2026-08-20; previously the final else."""
        assert JS.index("if (typedAnswer === null)") < JS.index(
            "typedAnswer === withStress"
        )


def _strip_stress(s: str) -> str:
    return s.replace(AC, "")


def _grade(typed, with_stress, no_stress, euphony_raw):
    """Python mirror of FEEDBACK_SCRIPT's ladder. Kept deliberately literal --
    same branch order, same comparisons -- so it reads against the JS side by
    side. TestEmittedJavaScript is what stops the two diverging silently."""
    alts = [s.strip() for s in (euphony_raw or "").split("|")]
    alts = [s for s in alts if s]

    if typed is None:
        return "NEUTRAL"
    if typed == with_stress:
        return "PERFECT"
    if typed in alts:
        return "PERFECT"
    if typed == no_stress:
        return "CORRECT"
    if _strip_stress(typed) in [_strip_stress(a) for a in alts]:
        return "CORRECT"
    return "INCORRECT"


class TestTierLadder:
    """Driven with ua-pvom-0012's real values -- the note the fix is validated
    on, and the only one in the corpus that exercises these branches at all."""

    def test_primary_with_stress_is_perfect(self):
        assert (
            _grade(
                WALKING_MULTI_UA,
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "PERFECT"
        )

    def test_primary_without_stress_is_correct(self):
        assert (
            _grade(
                WALKING_MULTI_TYPING,
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "CORRECT"
        )

    def test_stressed_alternate_is_perfect(self):
        """The regression this file exists for: ухо́дити used to grade CORRECT.
        Craig's ruling is that it is a different attested form, not a worse
        answer."""
        assert (
            _grade(
                WALKING_MULTI_EUPHONY,
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "PERFECT"
        )

    def test_unstressed_alternate_is_correct(self):
        """And the tier below it stays intact -- уходити is still accepted, just
        without the stress bonus. This is the pair that was previously
        indistinguishable."""
        assert (
            _grade(
                _strip_stress(WALKING_MULTI_EUPHONY),
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "CORRECT"
        )

    def test_the_two_alternate_tiers_are_actually_distinguishable(self):
        """States the property directly rather than inferring it from the two
        tests above: whatever the tiers are called, the stressed and unstressed
        alternates must not collapse to the same verdict."""
        stressed = _grade(
            WALKING_MULTI_EUPHONY,
            WALKING_MULTI_UA,
            WALKING_MULTI_TYPING,
            WALKING_MULTI_EUPHONY,
        )
        unstressed = _grade(
            _strip_stress(WALKING_MULTI_EUPHONY),
            WALKING_MULTI_UA,
            WALKING_MULTI_TYPING,
            WALKING_MULTI_EUPHONY,
        )
        assert stressed != unstressed

    def test_stress_on_the_wrong_vowel_is_correct_not_perfect(self):
        """Misplaced stress is the case that produced the original nbsp bug, so
        it is worth pinning: right letters, wrong mark position -- accepted, but
        no bonus."""
        misplaced = f"у{AC}ходити"
        assert (
            _grade(
                misplaced,
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "CORRECT"
        )

    def test_a_wrong_form_is_still_incorrect(self):
        """The euphonic tolerance must not have become a wildcard."""
        assert (
            _grade(
                f"прихо{AC}дити",
                WALKING_MULTI_UA,
                WALKING_MULTI_TYPING,
                WALKING_MULTI_EUPHONY,
            )
            == "INCORRECT"
        )

    def test_walking_uni_slot_behaves_the_same(self):
        """The -ій- epenthesis slot, where the euphonic pair is ввійти́/увійти́ --
        the pair Craig's PERFECT ruling was actually stated about."""
        assert (
            _grade(
                WALKING_UNI_EUPHONY,
                WALKING_UNI_UA,
                WALKING_UNI_TYPING,
                WALKING_UNI_EUPHONY,
            )
            == "PERFECT"
        )
        assert (
            _grade(
                WALKING_UNI_UA,
                WALKING_UNI_UA,
                WALKING_UNI_TYPING,
                WALKING_UNI_EUPHONY,
            )
            == "PERFECT"
        )

    def test_notes_with_no_euphony_data_are_unaffected(self):
        """11 of the 13 PVOM notes have every *_Euphony field blank. The
        alternate branches must be inert for them, not throw and not widen what
        is accepted."""
        assert _grade(f"прийти{AC}", f"прийти{AC}", "прийти", "") == "PERFECT"
        assert _grade("прийти", f"прийти{AC}", "прийти", "") == "CORRECT"
        assert _grade("прийди", f"прийти{AC}", "прийти", "") == "INCORRECT"

    def test_failed_reconstruction_is_not_graded(self):
        assert (
            _grade(None, WALKING_MULTI_UA, WALKING_MULTI_TYPING, WALKING_MULTI_EUPHONY)
            == "NEUTRAL"
        )


class TestTemplateDictKey:
    """The template dicts spelled their name key "name" here and "Name" in
    setup_ua_note_types.py. AnkiConnect accepts either, so nothing broke -- but
    test_template_field_refs.py needed a _tmpl_name() shim to cover both, and a
    guard written against one spelling silently skips the other note type's
    templates. Unified on "Name" 2026-08-20."""

    def test_every_template_uses_the_capitalized_key(self):
        for tmpl in pvom_setup.CARD_TEMPLATES:
            assert "Name" in tmpl, tmpl.keys()
            assert "name" not in tmpl, (
                f"{tmpl.get('Name')}: lowercase 'name' key is back -- guards "
                f"written against 'Name' will silently skip this template"
            )

    def test_all_four_motion_templates_are_present(self):
        assert [t["Name"] for t in pvom_setup.CARD_TEMPLATES] == [
            "Walking (Multi)",
            "Walking (Uni)",
            "Vehicle (Multi)",
            "Vehicle (Uni)",
        ]
