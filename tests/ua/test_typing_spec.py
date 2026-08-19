"""
tests/ua/test_typing_spec.py

Unit tests for compute_typing_spec() in tools/anki/sync/ua_lexeme_import.py and
for the grading JS it feeds in EN_UA_BACK -- Option B of
docs/ua-en-ua-euphony-aspect-refactor.md, built 2026-08-19.

What this replaced and why:

  `_EuphonySlots` was a second " / "-joined string that had to stay index-
  aligned with `TypingTarget_UA`'s own " / " join. Nothing enforced the
  alignment and nothing could detect a break; the JS rebuilt the slot
  structure by splitting both strings and trusting positions to correspond.
  `_TypingSpec` makes the slot the unit -- primary and alternates travel
  together in one object -- so that class of bug stops being possible rather
  than being avoided.

  Separately, the old field stored alternates and compared them STRESS-
  STRIPPED on both sides, so the grader could not distinguish "euphonic
  alternate, perfectly stressed" from "euphonic alternate, no stress". Both
  landed in CORRECT and a fully-correct dictionary-attested answer could never
  reach PERFECT. Per Craig: ввійти́ is not a lesser answer than уві́йти, just a
  different attested one. Alternates are therefore stored stressed here, and
  TestSpecShape::test_alternates_keep_their_stress is the test that fails if
  anyone reintroduces pre-stripping.

Coverage split, deliberately:

  - TestSpecShape / TestSlotOrdering / TestEmptyCases pin the DATA CONTRACT
    (Python side). This is where most of the value is -- the JS is a
    consumer of this shape.
  - TestEmittedJavaScript pins the invariants of the grading block that are
    easy to break silently while the file still parses.

  The full tier matrix (PERFECT/CORRECT/INCORRECT across primary/alternate x
  stressed/unstressed x slot count x separator spacing) was exercised under
  node against the real emitted JS during development, 19 cases, all passing.
  That harness is not committed because this repo has no JS test tooling; to
  re-run it, extract EN_UA_BACK's <script> body and drive it with a fake
  document exposing feedback.dataset.{withStress,noStress,typingSpec}.
  NOTE if you do: check for 'INCORRECT' BEFORE 'CORRECT' when classifying the
  output -- "INCORRECT" contains "CORRECT" as a substring, which silently
  misreported five passing cases as failures the first time round.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import tools.anki.sync.ua_lexeme_import as li  # noqa: E402
import tools.anki.setup.setup_ua_note_types as setup  # noqa: E402

AC = chr(0x0301)  # combining acute

# ua-lexeme-0115 as it stands after the 2026-08-18 в-/у- flip. Used throughout
# because it is the corpus's only note with euphony on BOTH slots, and the one
# Craig validates against.
LEMMA, LEMMA_ALT = "вхо" + AC + "дити", "ухо" + AC + "дити"
PERF, PERF_ALT = "ввійти" + AC, "увійти" + AC


def spec_for(*args):
    raw = li.compute_typing_spec(*args)
    return json.loads(raw) if raw else None


class TestSpecShape:
    def test_doublet_with_alternates_on_both_slots(self):
        s = spec_for(LEMMA, "", PERF, LEMMA_ALT, "", PERF_ALT)
        assert s == {
            "slots": [
                {"primary": LEMMA, "alts": [LEMMA_ALT]},
                {"primary": PERF, "alts": [PERF_ALT]},
            ]
        }

    def test_alternates_keep_their_stress(self):
        """THE regression guard for this whole refactor. The old mechanism
        stripped stress from stored alternates, which is precisely why a
        fully-stressed alternate could never reach PERFECT."""
        s = spec_for(LEMMA, "", PERF, LEMMA_ALT, "", PERF_ALT)
        for slot in s["slots"]:
            for alt in slot["alts"]:
                assert AC in alt, f"alternate lost its stress mark: {alt!r}"

    def test_slot_without_an_alternate_keeps_an_empty_list(self):
        """Slot count must match TypingTarget_UA's, because the JS still splits
        the typed answer on the separator to know which slot is which. A slot
        with no alternate is present with alts:[], never omitted."""
        s = spec_for(LEMMA, "", PERF, "", "", PERF_ALT)
        assert [x["primary"] for x in s["slots"]] == [LEMMA, PERF]
        assert s["slots"][0]["alts"] == []
        assert s["slots"][1]["alts"] == [PERF_ALT]

    def test_pipe_delimited_alternates_split(self):
        s = spec_for("вбо" + AC + "лівати", "", "", "убо" + AC + "лівати|вболіва" + AC + "ти", "", "")
        assert s["slots"][0]["alts"] == ["убо" + AC + "лівати", "вболіва" + AC + "ти"]

    def test_whitespace_around_pipe_segments_is_trimmed(self):
        s = spec_for("а", "", "", "  б  |  в  ", "", "")
        assert s["slots"][0]["alts"] == ["б", "в"]

    def test_output_is_compact_json(self):
        """It lands in an Anki field and is re-parsed by the card template, so
        bytes matter more than readability."""
        raw = li.compute_typing_spec(LEMMA, "", PERF, LEMMA_ALT, "", PERF_ALT)
        assert ", " not in raw and '": ' not in raw

    def test_output_is_not_ascii_escaped(self):
        """ensure_ascii=False -- \\u0432... escapes would bloat the field and
        make it unreadable in the Anki browser."""
        raw = li.compute_typing_spec(LEMMA, "", PERF, LEMMA_ALT, "", PERF_ALT)
        assert "\\u" not in raw
        assert LEMMA in raw


class TestSlotOrdering:
    def test_lemma_then_impf_uni_then_perfective(self):
        """Same order every other computed field uses, and the order the JS
        assumes when zipping typed slots against spec slots."""
        s = spec_for("ходи" + AC + "ти", "йти", "пі" + AC + "ти", "a", "b", "c")
        assert [x["primary"] for x in s["slots"]] == ["ходи" + AC + "ти", "йти", "пі" + AC + "ти"]

    def test_unpopulated_slots_are_skipped_not_blanked(self):
        s = spec_for(LEMMA, "", PERF, LEMMA_ALT, "", "")
        assert len(s["slots"]) == 2

    def test_slot_order_matches_compute_typing_target(self):
        """The JS pairs spec slots with typed slots positionally, so these two
        must agree. If compute_typing_target's filter ever changes, this fails."""
        target = li.compute_typing_target("ходи" + AC + "ти", "йти", "пі" + AC + "ти")
        s = spec_for("ходи" + AC + "ти", "йти", "пі" + AC + "ти", "a", "b", "c")
        assert target[0].split(" / ") == [x["primary"] for x in s["slots"]]


class TestEmptyCases:
    def test_no_euphony_anywhere_returns_blank(self):
        """~577 of 585 notes. Blank keeps the field out of the way, and the JS
        falls through to plain primary/no-stress comparison."""
        assert li.compute_typing_spec("ходи" + AC + "ти", "йти", "пі" + AC + "ти", "", "", "") == ""

    def test_no_populated_slots_returns_blank(self):
        assert li.compute_typing_spec("", "", "", "", "", "") == ""

    def test_euphony_on_an_unpopulated_slot_is_ignored(self):
        """An alternate for a slot with no primary is meaningless -- and would
        desync the spec's slot count from TypingTarget_UA's if emitted."""
        assert li.compute_typing_spec(LEMMA, "", "", "", "", PERF_ALT) == ""

    def test_legacy_euphony_note_fallback_is_gone(self):
        """compute_euphony_slots() fell back to the whole-note EuphonyNote for
        singlets. An audit (2026-08-19) found ONE note corpus-wide reaching it
        -- ua-lexeme-0353 -- and its EuphonyNote was explanatory prose, not a
        bare alternate, so the fallback was producing silent dead tolerance:
        prose compared as a spelling, matching nothing, warning about nothing.
        0353 was given a real Lemma_Euphony instead. The function no longer
        takes euphony_note at all; this asserts nobody quietly restores it."""
        import inspect
        assert "euphony_note" not in inspect.signature(li.compute_typing_spec).parameters
        assert not hasattr(li, "compute_euphony_slots")


class TestEmittedJavaScript:
    """Invariants of the grading block that break silently while still parsing."""

    def test_template_reads_the_new_field(self):
        assert '<script type="application/json" id="typing-spec">' in setup.EN_UA_BACK
        assert "{{text:_TypingSpec}}" in setup.EN_UA_BACK

    def test_spec_is_not_carried_in_an_html_attribute(self):
        """THE bug of 2026-08-19, second attempt. Shipped first as
        data-typing-spec="{{text:_TypingSpec}}" on the #feedback div.

        Anki does NOT HTML-escape field content -- it splices the raw text in
        -- so the JSON's own double quotes closed the attribute at the very
        first one. The browser saw data-typing-spec="{", JSON.parse threw, and
        the defensive catch degraded to "no alternates". Every euphonic answer
        then graded INCORRECT, while the "Correct answer" lines still rendered
        correctly, because they live in EARLIER attributes that parsed fine.
        That split is what made it read as a grading-logic bug.

        Two things are worth encoding. The original test asserted the
        attribute was PRESENT, reasoning that {{text:}} avoided HTML-escaping
        -- exactly backwards -- and it passed happily while the feature was
        dead. And no Python-level test of compute_typing_spec() could have
        seen it: the spec was correct, the template was wrong. Hence the
        round-trip test below, which asserts at the boundary where the two
        meet.

        Checks the ATTRIBUTE FORM (name + ="), not the bare name, following
        test_old_field_is_fully_gone's precedent -- the name appears in prose
        explaining what replaced it, and a substring check on the bare name
        would fail on the documentation rather than on the defect."""
        assert 'data-typing-spec="' not in setup.EN_UA_BACK

    def test_spec_survives_being_rendered_into_the_template(self):
        """Render the real EN_UA_BACK the way Anki does -- raw field splice,
        no escaping -- then parse it with a real HTML parser and confirm the
        JSON comes back out byte-identical and re-parses.

        This is the test that would have caught the attribute bug on the first
        try, and it is deliberately end-to-end: it takes a real corpus note's
        fields, runs them through compute_typing_spec(), splices the result in
        exactly as Anki would, and asserts the consumer can still read it."""
        import json as _json
        from html.parser import HTMLParser

        raw = li.compute_typing_spec(LEMMA, "", PERF, LEMMA_ALT, "", PERF_ALT)
        assert '"' in raw, "precondition: the spec contains double quotes"

        rendered = setup.EN_UA_BACK
        for token, value in (
            ("{{text:_TypingSpec}}", raw),
            ("{{TypingTarget_UA}}", f"{LEMMA} / {PERF}"),
            ("{{TypingAnswer}}", "входити / ввійти"),
        ):
            rendered = rendered.replace(token, value)

        class Extract(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_spec = False
                self.payload = ""
                self.attr_values = []

            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                self.attr_values.extend(v for v in d.values() if v)
                if tag == "script" and d.get("id") == "typing-spec":
                    assert d.get("type") == "application/json", d
                    self.in_spec = True

            def handle_endtag(self, tag):
                if tag == "script":
                    self.in_spec = False

            def handle_data(self, data):
                if self.in_spec:
                    self.payload += data

        p = Extract()
        p.feed(rendered)

        assert p.payload.strip() == raw, (
            "the spec did not survive rendering; got "
            f"{p.payload.strip()!r} instead of {raw!r}"
        )
        assert _json.loads(p.payload.strip())["slots"][0]["alts"] == [LEMMA_ALT]

        # And the negative half: no attribute anywhere may carry the JSON,
        # because that is precisely the shape that truncates. Matches on '{"'
        # rather than '{' -- an unsubstituted Anki replacement like
        # {{Source_URL}} legitimately starts with a brace.
        assert not [v for v in p.attr_values if v.startswith('{"')], (
            "an attribute value begins with '{\"' -- the spec is being "
            "carried in an attribute again"
        )

    def test_old_field_is_fully_gone(self):
        """Checks the ATTRIBUTE and the CALL, not mentions -- both names still
        appear in comments explaining what replaced them, which is deliberate."""
        assert "_EuphonySlots" not in setup.FIELDS
        assert 'data-euphony-slots="' not in setup.EN_UA_BACK
        assert "euphonyAltsForSlot(" not in setup.EN_UA_BACK

    def test_new_field_is_in_the_model(self):
        assert "_TypingSpec" in setup.FIELDS
        assert len(setup.FIELDS) == len(set(setup.FIELDS))

    def test_grading_helpers_present(self):
        for fn in ("function splitSlots(", "function slotAlts(", "function matchSlot("):
            assert fn in setup.EN_UA_BACK, fn

    def test_parse_is_guarded(self):
        """A malformed spec must degrade to 'no alternates', never throw and
        leave the learner staring at a blank panel."""
        block = setup.EN_UA_BACK
        assert "JSON.parse" in block
        assert "try {" in block and "catch" in block

    def test_separator_split_is_tolerant(self):
        r"""Bug (c): splitting on the literal ' / ' made ходити/йти/піти grade
        INCORRECT outright despite being the right forms."""
        assert r"/\s*\/\s*/" in setup.EN_UA_BACK
        assert "typedAnswer.split(' / ')" not in setup.EN_UA_BACK

    def test_source_has_no_invalid_escape_sequences(self):
        r"""This module is ~80KB of JS and CSS inside Python string literals,
        so a regex like /\s*\/\s*/ written non-raw is an invalid escape:
        Python passes it through today (emitting correct JS) but warns, and a
        future Python makes it a SyntaxError. Caught exactly that on the
        separator regex added 2026-08-19. Compiling with these warnings as
        errors guards the whole file, not just the line that broke."""
        import warnings
        src = Path(setup.__file__).read_text(encoding="utf-8")
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            warnings.simplefilter("error", SyntaxWarning)
            compile(src, setup.__file__, "exec")

    def test_alternates_are_not_pre_stripped_in_js(self):
        """slotAlts() must hand back stressed alternates. If it ever strips
        again, PERFECT becomes unreachable for alternates and this refactor is
        silently undone."""
        i = setup.EN_UA_BACK.index("function slotAlts(")
        body = setup.EN_UA_BACK[i:i + 400]
        assert "stripStress" not in body
