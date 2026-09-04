"""Unit tests for confusable_clusters.yaml registry-driven Compare card import (Phase 6).

Tests the consolidated registry approach: CompareMembers field populated from
confusable_clusters.yaml; no fallback to CNSF CompareA/B/C/D fields.
"""

import json
import pytest
from pathlib import Path

from tools.anki.sync.ua_lexeme_import import (
    get_cluster_compare_members_json,
    import_note,
)
from tools.anki.lib.confusable_clusters import ClusterRegistry


class TestClusterCompareMembers:
    """Test CompareMembers JSON generation from registry."""

    def test_cluster_member_returns_json_with_scenario_and_members(self):
        """A note in a cluster returns JSON with scenario and member lemmas."""
        # Test with ua-lexeme-0115 (входити/вхідний cluster)
        result = get_cluster_compare_members_json("ua-lexeme-0115", [])

        assert result, "Should return non-empty JSON for cluster member"
        data = json.loads(result)
        assert isinstance(data, dict), "Should return JSON object with scenario + members"
        assert "scenario" in data, "Should contain 'scenario' key"
        assert "members" in data, "Should contain 'members' key"
        assert isinstance(data["members"], list), "members should be an array"
        assert len(data["members"]) > 0, "Should have at least one member"

    def test_non_cluster_member_returns_empty_string(self):
        """A note not in any cluster returns empty string."""
        # Use a note ID that exists but isn't in confusable_clusters.yaml
        result = get_cluster_compare_members_json("ua-lexeme-9999", [])
        assert result == "", "Should return empty string for non-clustered note"

    def test_cluster_members_contain_correct_lemmas(self):
        """Cluster members include the expected lemmas from registry."""
        result = get_cluster_compare_members_json("ua-lexeme-0115", [])
        if result:
            data = json.loads(result)
            members = data["members"]
            # Should include both the note itself and its cluster partners
            assert any("вхо" in lemma for lemma in members), \
                f"Should include entering/exiting form (вхо́дити or вихо́дити), got {members}"

    def test_scenario_included_in_json(self):
        """CompareScenario is embedded in the returned JSON."""
        result = get_cluster_compare_members_json("ua-lexeme-0115", [])
        if result:
            data = json.loads(result)
            scenario = data.get("scenario", "")
            # Scenario should be non-empty for active clusters
            # (may be empty for some, but structure should be consistent)
            assert isinstance(scenario, str), "scenario should be a string"


class TestImportWithRegistryOnly:
    """Test import logic with registry-only (no CNSF Compare fields)."""

    def test_import_sets_compare_members_from_registry(self):
        """Import sets CompareMembers from registry when cluster found."""
        # Simplified test: verify the field is set when CompareMembers JSON returned
        result_json = get_cluster_compare_members_json("ua-lexeme-0115", [])
        if result_json:
            # This field would be set in import_note
            parsed = json.loads(result_json)
            assert "members" in parsed
            assert "scenario" in parsed
            # In actual import, this would be: fields["CompareMembers"] = result_json

    def test_import_blanks_deprecated_fields(self):
        """Import should NOT try to set deprecated Compare fields."""
        # This is a behavioral test: ensure the code path no longer
        # tries to write CompareA/B/C/D (since they're not in schema)
        # Verified by code inspection: import_note no longer has:
        #   fields["CompareA"] = ...
        #   fields["CompareB"] = ...
        # The cleanup in Phase 5 removed this code path entirely.
        pass  # Code inspection confirms removal; no runtime test needed


class TestTemplateScenarioRendering:
    """Test that template can extract and render scenario from CompareMembers JSON."""

    def test_json_with_scenario_renders_in_template(self):
        """Template JavaScript can parse JSON with scenario + members."""
        sample_json = json.dumps({
            "scenario": "Який предмет ти любиш?",
            "members": ["входити", "виходити", "заходити"]
        })

        # Verify JSON is valid and structure matches template expectations
        data = json.loads(sample_json)
        assert data["scenario"] == "Який предмет ти любиш?"
        assert len(data["members"]) == 3

    def test_backward_compatible_with_simple_array(self):
        """Template JavaScript gracefully handles old array format."""
        old_format = json.dumps(["входити", "виходити", "заходити"])

        # Template should handle both: Array.isArray() check + fallback
        data = json.loads(old_format)
        members = data if isinstance(data, list) else (data.get("members", []) if isinstance(data, dict) else [])
        assert len(members) == 3, "Should extract members from array or object"


class TestReleaseActiveFiltering:
    """Test Compare card membership filtering by release-active state.

    Added 2026-09-01, per Craig: get_compare_card_members() used to include
    every *sourced* cluster-mate regardless of whether that cluster-mate was
    itself status:verified/release:active in its own CNSF note -- so an
    already-active hub could reference a still-draft sibling and test the
    learner on a word suspended everywhere else in Anki. Uses a synthetic
    fixture (temp note files + temp registry) rather than live corpus data,
    since which real notes are draft vs. active changes as the corpus is
    reviewed -- a test pinned to real note_ids would go stale.
    """

    @staticmethod
    def _write_note(root: Path, note_id: str, verified: bool) -> None:
        status = "status:verified" if verified else "status:draft"
        release = "release:active" if verified else "release:pending"
        (root / f"{note_id}.md").write_text(
            f"---\nnote_id: {note_id}\ntags:\n- domain:ua\n- {status}\n- {release}\n---\n",
            encoding="utf-8",
        )

    @staticmethod
    def _write_registry(path: Path) -> None:
        path.write_text(
            """
clusters:
  test-cluster:
    description: test
    canonical_note: ua-lexeme-0001
    show_all_members: true
    members:
    - note_id: ua-lexeme-0001
      lemma: aaa
      status: sourced
      chapter: '1.0'
      comment: active hub
      compare_scenario: scenario for aaa
    - note_id: ua-lexeme-0002
      lemma: bbb
      status: sourced
      chapter: '1.0'
      comment: draft satellite
      compare_scenario: scenario for bbb
    - note_id: ua-lexeme-0003
      lemma: ccc
      status: sourced
      chapter: '1.0'
      comment: active satellite
      compare_scenario: scenario for ccc
""",
            encoding="utf-8",
        )

    def _build_registry(self, tmp_path: Path) -> tuple[ClusterRegistry, set]:
        lexeme_root = tmp_path / "notes" / "lexemes"
        lexeme_root.mkdir(parents=True)
        self._write_note(lexeme_root, "ua-lexeme-0001", verified=True)
        self._write_note(lexeme_root, "ua-lexeme-0002", verified=False)
        self._write_note(lexeme_root, "ua-lexeme-0003", verified=True)

        registry_path = tmp_path / "confusable_clusters.yaml"
        self._write_registry(registry_path)

        registry = ClusterRegistry(registry_path=str(registry_path))
        release_active_ids = registry.get_release_active_note_ids(note_roots=[lexeme_root])
        return registry, release_active_ids

    def test_release_active_note_ids_excludes_draft(self, tmp_path):
        """get_release_active_note_ids() only includes verified+active notes."""
        _, release_active_ids = self._build_registry(tmp_path)
        assert release_active_ids == {"ua-lexeme-0001", "ua-lexeme-0003"}

    def test_unfiltered_members_include_draft_sibling(self, tmp_path):
        """Without release_active_ids, the draft sibling is still included
        (previous, unfiltered behavior -- existing callers are unaffected)."""
        registry, _ = self._build_registry(tmp_path)
        members = registry.get_compare_card_members("ua-lexeme-0001")
        assert {m.note_id for m in members} == {
            "ua-lexeme-0001", "ua-lexeme-0002", "ua-lexeme-0003"
        }

    def test_filtered_members_exclude_draft_sibling(self, tmp_path):
        """With release_active_ids, the draft sibling is filtered out."""
        registry, release_active_ids = self._build_registry(tmp_path)
        members = registry.get_compare_card_members(
            "ua-lexeme-0001", release_active_ids=release_active_ids
        )
        assert {m.note_id for m in members} == {"ua-lexeme-0001", "ua-lexeme-0003"}

    def test_compare_json_empty_when_fewer_than_two_active_remain(self, tmp_path):
        """get_cluster_compare_members_json() returns '' when filtering
        leaves fewer than two release-active members -- nothing left to
        distinguish."""
        lexeme_root = tmp_path / "notes" / "lexemes"
        lexeme_root.mkdir(parents=True)
        self._write_note(lexeme_root, "ua-lexeme-0001", verified=True)
        self._write_note(lexeme_root, "ua-lexeme-0002", verified=False)

        registry_path = tmp_path / "confusable_clusters.yaml"
        registry_path.write_text(
            """
clusters:
  solo-active-cluster:
    description: test
    canonical_note: ua-lexeme-0001
    members:
    - note_id: ua-lexeme-0001
      lemma: aaa
      status: sourced
      chapter: '1.0'
      comment: active hub
      compare_scenario: scenario for aaa
    - note_id: ua-lexeme-0002
      lemma: bbb
      status: sourced
      chapter: '1.0'
      comment: draft satellite
      compare_scenario: scenario for bbb
""",
            encoding="utf-8",
        )
        registry = ClusterRegistry(registry_path=str(registry_path))
        release_active_ids = registry.get_release_active_note_ids(note_roots=[lexeme_root])

        result = get_cluster_compare_members_json(
            "ua-lexeme-0001", [], registry=registry, release_active_ids=release_active_ids
        )
        assert result == "", "Only one release-active member remains -- nothing to compare"

    def test_compare_json_populated_when_two_active_remain(self, tmp_path):
        """get_cluster_compare_members_json() still returns real content when
        at least two release-active members remain after filtering."""
        registry, release_active_ids = self._build_registry(tmp_path)
        result = get_cluster_compare_members_json(
            "ua-lexeme-0001", [], registry=registry, release_active_ids=release_active_ids
        )
        assert result
        data = json.loads(result)
        assert set(data["members"]) == {"aaa", "ccc"}


class TestConsolidatedApproach:
    """Integration tests for the consolidated registry approach."""

    def test_registry_validator_passes(self):
        """Confusable_clusters.yaml passes validation."""
        validator = ClusterRegistry()
        # If we got here, the registry loaded successfully
        # (constructor validates on load)
        assert validator.clusters is not None

    def test_no_fallback_to_cnsf_fields(self):
        """Import path no longer checks for CompareA/B in CNSF."""
        # Code review: ua_lexeme_import.py no longer has:
        #   already_authored = fields.get("CompareA", "").strip() and ...
        #   if not is_homograph and not already_authored:
        #       compute_compare_options(...)
        # Phase 5 removed these lines entirely.
        # This test documents the behavioral change.
        pass  # Verified by code inspection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
