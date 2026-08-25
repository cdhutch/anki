"""Tests for ClusterRegistry and cluster management."""

import pytest
import tempfile
from pathlib import Path
import yaml

from tools.anki.lib.confusable_clusters import (
    ClusterRegistry,
    ConfusableCluster,
    ClusterMember,
    ClusterMemberStatus,
)


@pytest.fixture
def sample_registry_yaml():
    """Sample registry YAML for testing."""
    return {
        "clusters": {
            "intensifier-adverbs": {
                "description": "Adverbial intensifiers for comparatives",
                "canonical_note": "ua-lexeme-0467",
                "members": [
                    {
                        "note_id": "ua-lexeme-0467",
                        "lemma": "значно",
                        "status": "sourced",
                        "chapter": "2.8.3",
                        "comment": "formal register"
                    },
                    {
                        "note_id": "ua-lexeme-0468",
                        "lemma": "набагато",
                        "status": "sourced",
                        "chapter": "2.8.3",
                        "comment": "conversational register"
                    },
                    {
                        "note_id": None,
                        "lemma": "забагато",
                        "status": "not-sourced",
                        "chapter": "?",
                        "comment": "pending"
                    }
                ]
            }
        }
    }


@pytest.fixture
def temp_registry_file(sample_registry_yaml):
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_registry_yaml, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink()


class TestClusterMember:
    """Tests for ClusterMember dataclass."""
    
    def test_member_creation(self):
        """Test creating a cluster member."""
        member = ClusterMember(
            note_id="ua-lexeme-0467",
            lemma="значно",
            status=ClusterMemberStatus.SOURCED,
            chapter="2.8.3",
            comment="formal"
        )
        assert member.note_id == "ua-lexeme-0467"
        assert member.lemma == "значно"
        assert member.is_active()
    
    def test_member_not_sourced(self):
        """Test member with null note_id is not active."""
        member = ClusterMember(
            note_id=None,
            lemma="забагато",
            status=ClusterMemberStatus.NOT_SOURCED,
            chapter="?",
            comment="pending"
        )
        assert not member.is_active()
        assert member.note_id is None
    
    def test_member_repr(self):
        """Test member string representation."""
        member = ClusterMember(
            note_id="ua-lexeme-0467",
            lemma="значно",
            status=ClusterMemberStatus.SOURCED,
            chapter="2.8.3",
            comment=""
        )
        assert "значно" in repr(member)
        assert "ua-lexeme-0467" in repr(member)


class TestConfusableCluster:
    """Tests for ConfusableCluster dataclass."""
    
    def test_cluster_creation(self):
        """Test creating a cluster."""
        members = [
            ClusterMember("ua-lexeme-0467", "значно", ClusterMemberStatus.SOURCED, "2.8.3", "formal"),
            ClusterMember("ua-lexeme-0468", "набагато", ClusterMemberStatus.SOURCED, "2.8.3", "conversational"),
            ClusterMember(None, "забагато", ClusterMemberStatus.NOT_SOURCED, "?", "pending")
        ]
        cluster = ConfusableCluster(
            name="intensifier-adverbs",
            description="Intensifiers",
            canonical_note_id="ua-lexeme-0467",
            members=members
        )
        assert cluster.name == "intensifier-adverbs"
        assert len(cluster.members) == 3
    
    def test_get_active_members(self):
        """Test getting only sourced members."""
        members = [
            ClusterMember("ua-lexeme-0467", "значно", ClusterMemberStatus.SOURCED, "2.8.3", "formal"),
            ClusterMember("ua-lexeme-0468", "набагато", ClusterMemberStatus.SOURCED, "2.8.3", "conversational"),
            ClusterMember(None, "забагато", ClusterMemberStatus.NOT_SOURCED, "?", "pending")
        ]
        cluster = ConfusableCluster(
            name="intensifier-adverbs",
            description="Intensifiers",
            canonical_note_id="ua-lexeme-0467",
            members=members
        )
        active = cluster.get_active_members()
        assert len(active) == 2
        assert all(m.is_active() for m in active)
    
    def test_get_hub_member(self):
        """Test getting the hub member."""
        members = [
            ClusterMember("ua-lexeme-0467", "значно", ClusterMemberStatus.SOURCED, "2.8.3", "formal"),
            ClusterMember("ua-lexeme-0468", "набагато", ClusterMemberStatus.SOURCED, "2.8.3", "conversational"),
        ]
        cluster = ConfusableCluster(
            name="intensifier-adverbs",
            description="Intensifiers",
            canonical_note_id="ua-lexeme-0467",
            members=members
        )
        hub = cluster.get_hub_member()
        assert hub is not None
        assert hub.note_id == "ua-lexeme-0467"
        assert hub.lemma == "значно"
    
    def test_is_hub(self):
        """Test hub detection."""
        members = [
            ClusterMember("ua-lexeme-0467", "значно", ClusterMemberStatus.SOURCED, "2.8.3", "formal"),
            ClusterMember("ua-lexeme-0468", "набагато", ClusterMemberStatus.SOURCED, "2.8.3", "conversational"),
        ]
        cluster = ConfusableCluster(
            name="intensifier-adverbs",
            description="Intensifiers",
            canonical_note_id="ua-lexeme-0467",
            members=members
        )
        assert cluster.is_hub("ua-lexeme-0467")
        assert not cluster.is_hub("ua-lexeme-0468")


class TestClusterRegistry:
    """Tests for ClusterRegistry."""
    
    def test_registry_load(self, temp_registry_file):
        """Test loading registry from file."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        assert "intensifier-adverbs" in registry.clusters
        cluster = registry.clusters["intensifier-adverbs"]
        assert cluster.canonical_note_id == "ua-lexeme-0467"
        assert len(cluster.members) == 3
    
    def test_get_cluster(self, temp_registry_file):
        """Test retrieving cluster by name."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        cluster = registry.get_cluster("intensifier-adverbs")
        assert cluster is not None
        assert cluster.name == "intensifier-adverbs"
    
    def test_get_cluster_not_found(self, temp_registry_file):
        """Test retrieving nonexistent cluster."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        cluster = registry.get_cluster("nonexistent")
        assert cluster is None
    
    def test_get_cluster_by_note_id(self, temp_registry_file):
        """Test finding cluster by note ID."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        cluster = registry.get_cluster_by_note_id("ua-lexeme-0467")
        assert cluster is not None
        assert cluster.name == "intensifier-adverbs"
    
    def test_get_cluster_by_note_id_satellite(self, temp_registry_file):
        """Test finding cluster for satellite note."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        cluster = registry.get_cluster_by_note_id("ua-lexeme-0468")
        assert cluster is not None
        assert cluster.name == "intensifier-adverbs"
    
    def test_get_cluster_by_note_id_not_found(self, temp_registry_file):
        """Test finding cluster for non-member note."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        cluster = registry.get_cluster_by_note_id("ua-lexeme-9999")
        assert cluster is None
    
    def test_is_hub(self, temp_registry_file):
        """Test hub detection via registry."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        assert registry.is_hub("ua-lexeme-0467")
        assert not registry.is_hub("ua-lexeme-0468")
    
    def test_is_satellite(self, temp_registry_file):
        """Test satellite detection via registry."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        assert not registry.is_satellite("ua-lexeme-0467")
        assert registry.is_satellite("ua-lexeme-0468")
    
    def test_get_compare_card_members_hub(self, temp_registry_file):
        """Test Compare card members for hub note."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        members = registry.get_compare_card_members("ua-lexeme-0467")
        assert len(members) == 2  # Only active members
        assert all(m.is_active() for m in members)
    
    def test_get_compare_card_members_satellite(self, temp_registry_file):
        """Test Compare card members for satellite note."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        members = registry.get_compare_card_members("ua-lexeme-0468")
        assert len(members) == 2  # Hub + self
        lemmas = [m.lemma for m in members]
        assert "значно" in lemmas  # Hub
        assert "набагато" in lemmas  # Self
    
    def test_get_compare_card_members_not_clustered(self, temp_registry_file):
        """Test Compare card members for non-clustered note."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        members = registry.get_compare_card_members("ua-lexeme-9999")
        assert len(members) == 0
    
    def test_list_clusters(self, temp_registry_file):
        """Test listing all cluster names."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        clusters = registry.list_clusters()
        assert "intensifier-adverbs" in clusters
        assert len(clusters) == 1
    
    def test_validate(self, temp_registry_file):
        """Test registry validation."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        errors, warnings, missing_tags = registry.validate()
        
        # Should warn about pending members
        assert any("забагато" in w for w in warnings)
        
        # Should have no critical errors (all note_ids are valid format)
        assert len(errors) == 0
    
    def test_summary(self, temp_registry_file):
        """Test registry summary output."""
        registry = ClusterRegistry(registry_path=str(temp_registry_file))
        summary = registry.summary()
        assert "intensifier-adverbs" in summary
        assert "значно" in summary
        assert "набагато" in summary
        assert "2/3 sourced" in summary  # 2 active, 3 total


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
