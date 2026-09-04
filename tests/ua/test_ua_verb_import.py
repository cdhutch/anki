"""
tests/ua/test_ua_verb_import.py

Unit tests for tools/anki/sync/ua_verb_import.py's suspension policy
(should_suspend) and per-category empty-card detection (category_is_empty).
Everything else in this module talks to AnkiConnect directly and isn't
practically unit-testable without a live Anki instance -- these two pure
decision-logic functions are what's worth covering.

Per Option A refactoring (2026-08-25), stress:unverified is decoupled from
suspension logic. The conj:drill/conj:suspended curation axis was removed
2026-08-27 (per Craig): all status:verified verbs are now meant to be actively
drillable, not just a hand-picked set of class leaders, since class leaders
trickle in gradually as older chapters get backfilled.

release: added 2026-08-29 (per Craig) as a second, independent gate alongside
status. status tracks content-quality/review state; release tracks study-
pacing -- whether a verified note has actually been let into rotation yet, so
a large freshly-authored backlog can sit verified-but-suspended until Craig
releases it in controlled batches. Unsuspending now requires BOTH
status:verified AND release:active (AND gate); either one missing suspends,
so a note with no release tag at all fails closed (suspended).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.sync.ua_verb_import import (  # noqa: E402
    CARD_FIELD_CATEGORIES,
    category_is_empty,
    category_should_suspend,
    compute_card_suspension_targets,
    should_suspend,
)


class TestShouldSuspend:
    """Test the should_suspend() decision logic.

    Two-axis AND gate as of 2026-08-29: status:verified AND release:active
    both required to unsuspend. stress:unverified no longer suspends
    (Option A, 2026-08-25); conj:suspended no longer suspends (2026-08-27
    removal of the conj: curation axis).
    """

    def test_verified_and_active_unsuspends(self):
        assert should_suspend(["domain:ua", "status:verified", "release:active"]) is False

    def test_verified_without_release_tag_suspends(self):
        # AND gate fails closed: verified content not yet released stays suspended.
        assert should_suspend(["domain:ua", "status:verified"]) is True

    def test_verified_with_release_pending_suspends(self):
        assert should_suspend(["domain:ua", "status:verified", "release:pending"]) is True

    def test_status_draft_suspends(self):
        assert should_suspend(["domain:ua", "status:draft"]) is True

    def test_status_draft_suspends_even_with_release_active(self):
        # Both axes must clear; status:draft alone still suspends.
        assert should_suspend(["domain:ua", "status:draft", "release:active"]) is True

    def test_conj_suspended_tag_no_longer_suspends(self):
        # The conj:drill/conj:suspended axis was removed 2026-08-27 -- a
        # verified, released verb stays active for drilling even if a stray
        # conj:suspended tag is still present on the note.
        assert should_suspend(
            ["domain:ua", "status:verified", "release:active", "conj:suspended"]
        ) is False

    def test_status_verified_and_stress_unverified_does_not_suspend(self):
        # A verb can carry unconfirmed stress marks but still be content-verified
        # and released -- stress:unverified never suspends (Option A).
        assert should_suspend(
            ["domain:ua", "status:verified", "release:active", "stress:unverified"]
        ) is False

    def test_stress_unverified_alone_suspends(self):
        # Per Option A refactoring, stress:unverified is decoupled from suspension --
        # but with no status:verified/release:active present, the AND gate still fails.
        assert should_suspend(["stress:unverified"]) is True

    def test_no_tags_suspends(self):
        # Fail closed: nothing asserts verified+active, so a bare/untagged note
        # stays suspended rather than defaulting to active.
        assert should_suspend([]) is True

    def test_status_draft_suspends_regardless_of_other_tags(self):
        assert should_suspend(["status:draft", "stress:unverified", "conj:drill"]) is True


class TestCategoryIsEmpty:
    """Test category_is_empty() -- the per-Production-card content check added
    2026-09-03 (per Craig; see CLAUDE.md "Remaining Work" item 21) so that a
    card with zero actual forms (e.g. стосуватися's Imperative card -- a
    defective 3rd-person-only verb with no Imperative_* forms at all) gets
    suspended on its own, instead of the old blanket-suspend-Participles-only
    behavior.
    """

    IMPERATIVE_FIELDS = ["Imperative_2sg", "Imperative_1pl", "Imperative_2pl"]

    def test_all_blank_is_empty(self):
        fields = {"Imperative_2sg": "", "Imperative_1pl": "", "Imperative_2pl": ""}
        assert category_is_empty(fields, self.IMPERATIVE_FIELDS) is True

    def test_missing_keys_treated_as_blank(self):
        # CNSF notes always carry every field, but the check shouldn't crash
        # or misfire on a dict that happens to omit one.
        assert category_is_empty({}, self.IMPERATIVE_FIELDS) is True

    def test_whitespace_only_treated_as_blank(self):
        fields = {"Imperative_2sg": "  ", "Imperative_1pl": "", "Imperative_2pl": ""}
        assert category_is_empty(fields, self.IMPERATIVE_FIELDS) is True

    def test_one_populated_field_is_not_empty(self):
        # стосуватися's real Present category: only Pres_3sg/Pres_3pl populated,
        # the rest blank -- category as a whole is NOT empty, card stays active.
        fields = {
            "Pres_1sg": "", "Pres_2sg": "", "Pres_3sg": "стосу́ється",
            "Pres_1pl": "", "Pres_2pl": "", "Pres_3pl": "стосу́ються",
        }
        present_fields = ["Pres_1sg", "Pres_2sg", "Pres_3sg", "Pres_1pl", "Pres_2pl", "Pres_3pl"]
        assert category_is_empty(fields, present_fields) is False

    def test_all_populated_is_not_empty(self):
        fields = {"Imperative_2sg": "ви́глянь", "Imperative_1pl": "ви́гляньмо", "Imperative_2pl": "ви́гляньте"}
        assert category_is_empty(fields, self.IMPERATIVE_FIELDS) is False

    def test_card_field_categories_covers_four_production_cards_in_order(self):
        # Order must track VERB_CARD_TEMPLATES in setup_ua_note_types.py --
        # findCards returns cards in creation order, and
        # sync_card_suspension()/compute_card_suspension_targets() index
        # into this list positionally.
        names = [name for name, _fields, _force in CARD_FIELD_CATEGORIES]
        assert names == [
            "Production (Present)",
            "Production (Past)",
            "Production (Imperative)",
            "Production (Participles)",
        ]

    def test_only_participles_is_force_suspended(self):
        # Present/Past/Imperative are content-driven; Participles is a
        # curriculum-pacing override (2026-09-03, per Craig: "I want the
        # participles to be suspended, since I haven't gotten to learning
        # how to form them yet") -- suspended regardless of content until
        # Craig flips it off.
        flags = {name: force for name, _fields, force in CARD_FIELD_CATEGORIES}
        assert flags == {
            "Production (Present)": False,
            "Production (Past)": False,
            "Production (Imperative)": False,
            "Production (Participles)": True,
        }


class TestCategoryShouldSuspend:
    """Test category_should_suspend() -- the per-card decision that combines
    the force_suspend curriculum-pacing override with the content check
    (added 2026-09-03, per Craig, same day as the force_suspend flag itself).
    """

    POPULATED_PARTICIPLES = {
        "Participle_Active_Present": "",
        "Participle_Adverbial_Present": "вигляда́ючи",
        "Participle_Passive_Past": "",
        "Participle_Impersonal_Past": "",
        "Participle_Adverbial_Past": "вигляда́вши",
    }
    PARTICIPLE_FIELDS = list(POPULATED_PARTICIPLES.keys())

    def test_force_suspend_wins_even_with_content(self):
        # ua-verb-0083 (вигляда́ти) has real participle content, but Craig
        # wants Participles suspended regardless -- this is the exact
        # regression this test guards against.
        assert category_should_suspend(self.POPULATED_PARTICIPLES, self.PARTICIPLE_FIELDS, True) is True

    def test_force_suspend_true_with_empty_content_still_suspends(self):
        empty = {name: "" for name in self.PARTICIPLE_FIELDS}
        assert category_should_suspend(empty, self.PARTICIPLE_FIELDS, True) is True

    def test_no_force_suspend_falls_back_to_content_check(self):
        # force_suspend=False (Present/Past/Imperative): behaves exactly
        # like category_is_empty.
        assert category_should_suspend(self.POPULATED_PARTICIPLES, self.PARTICIPLE_FIELDS, False) is False
        empty = {name: "" for name in self.PARTICIPLE_FIELDS}
        assert category_should_suspend(empty, self.PARTICIPLE_FIELDS, False) is True


class TestComputeCardSuspensionTargets:
    """Test compute_card_suspension_targets() -- the whole-note gate combined
    with the per-category decision, in CARD_FIELD_CATEGORIES order (added
    2026-09-03, per Craig, replacing the old two-step set_suspended() +
    sync_category_card_suspension() -- see sync_card_suspension()'s
    docstring for why that pairing's "changed" log was unreliable even
    though its final suspended state was always correct).
    """

    # стосуватися (ua-verb-0076): 3sg/3pl present, full past, zero imperative,
    # zero participles -- the real note that surfaced the original bug.
    STOSUVATYSYA_FIELDS = {
        "Pres_1sg": "", "Pres_2sg": "", "Pres_3sg": "стосу́ється",
        "Pres_1pl": "", "Pres_2pl": "", "Pres_3pl": "стосу́ються",
        "Past_1sg_m": "стосува́вся", "Past_1sg_f": "стосува́лася",
        "Past_1sg_n": "стосува́лося", "Past_3pl": "стосува́лися",
        "Imperative_2sg": "", "Imperative_1pl": "", "Imperative_2pl": "",
        "Participle_Active_Present": "", "Participle_Adverbial_Present": "",
        "Participle_Passive_Past": "", "Participle_Impersonal_Past": "",
        "Participle_Adverbial_Past": "",
    }

    def test_note_suspend_true_suspends_all_four_regardless_of_content(self):
        # Whole-note gate wins outright -- matches old blanket set_suspended(True).
        assert compute_card_suspension_targets(self.STOSUVATYSYA_FIELDS, True) == [True, True, True, True]

    def test_note_suspend_false_stosuvatysya_matches_confirmed_live_state(self):
        # Craig's own AnkiConnect spot-check on the real note confirmed this
        # exact pattern: Present/Past/Participles unsuspended, Imperative
        # suspended -- Participles unsuspended here only because force_suspend
        # wasn't added yet at that point; see the next test for post-force_suspend.
        present, past, imperative, participles = compute_card_suspension_targets(
            self.STOSUVATYSYA_FIELDS, False
        )
        assert (present, past, imperative) == (False, False, True)
        assert participles is True  # force_suspend, independent of its empty content

    def test_order_matches_card_field_categories(self):
        targets = compute_card_suspension_targets(self.STOSUVATYSYA_FIELDS, False)
        assert len(targets) == len(CARD_FIELD_CATEGORIES) == 4
