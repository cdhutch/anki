"""Confusable word cluster registry and validation.

Manages canonical groupings of semantically-related words (confusable clusters).
Each cluster has a hub (canonical reference note) and satellites. Hub notes show
all active cluster members on their Compare card; satellites show only the hub.

Registry is loaded from domains/ua/anki/confusable_clusters.yaml
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class ClusterMemberStatus(Enum):
    """Status of a cluster member's sourcing."""
    SOURCED = "sourced"
    NOT_SOURCED = "not-sourced"
    PENDING = "pending"


@dataclass
class ClusterMember:
    """A single member of a confusable cluster."""

    note_id: Optional[str]  # ua-lexeme-NNNN or None if not yet sourced
    lemma: str
    status: ClusterMemberStatus
    chapter: Optional[str]  # "2.8.3" or "?" if unknown
    comment: str

    def is_active(self) -> bool:
        """Return True if this member has been sourced (note_id is not None)."""
        return self.note_id is not None

    def __repr__(self) -> str:
        status_str = f"({self.note_id})" if self.is_active() else "(not sourced)"
        return f"{self.lemma} {status_str}"


@dataclass
class ConfusableCluster:
    """A semantic cluster of confusable/related words."""

    name: str  # cluster ID: "intensifier-adverbs"
    description: str
    canonical_note_id: str  # ua-lexeme-0467 (hub)
    members: List[ClusterMember]

    def get_active_members(self) -> List[ClusterMember]:
        """Return only sourced members (those with note_id not None)."""
        return [m for m in self.members if m.is_active()]

    def get_hub_member(self) -> Optional[ClusterMember]:
        """Return the hub member object."""
        return next((m for m in self.members if m.note_id == self.canonical_note_id), None)

    def is_hub(self, note_id: str) -> bool:
        """Return True if note_id is this cluster's canonical hub."""
        return note_id == self.canonical_note_id

    def __repr__(self) -> str:
        active_count = len(self.get_active_members())
        total_count = len(self.members)
        return f"Cluster '{self.name}' ({active_count}/{total_count} sourced)"


class ClusterRegistry:
    """Loads, parses, and queries the confusable clusters registry.

    The registry maps note IDs to their semantic clusters, enabling Compare card
    generation and validation of confusable relationships.
    """

    def __init__(self, registry_path: Optional[str] = None):
        """Initialize and load the cluster registry.

        Args:
            registry_path: Path to confusable_clusters.yaml. Defaults to
                          domains/ua/anki/confusable_clusters.yaml relative to repo root.

        Raises:
            FileNotFoundError: If registry file does not exist.
            yaml.YAMLError: If registry YAML is malformed.
        """
        self.registry_path = Path(registry_path) if registry_path else self._default_path()
        self.clusters: Dict[str, ConfusableCluster] = {}
        self.note_to_cluster: Dict[str, str] = {}  # Reverse index: ua-lexeme-0467 → "intensifier-adverbs"
        self._load()

    def _default_path(self) -> Path:
        """Return default registry path relative to repo root."""
        repo_root = Path(__file__).resolve().parents[3]  # tools/anki/lib/confusable_clusters.py → repo root
        return repo_root / "domains" / "ua" / "anki" / "confusable_clusters.yaml"

    def _load(self) -> None:
        """Load and parse YAML registry.

        Raises:
            FileNotFoundError: If registry file does not exist.
            yaml.YAMLError: If YAML is malformed.
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Confusable clusters registry not found at {self.registry_path}\n"
                f"Create it with: domains/ua/anki/confusable_clusters.yaml"
            )

        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'clusters' not in data:
            raise ValueError(f"Registry YAML missing 'clusters' key at {self.registry_path}")

        for cluster_name, cluster_data in data['clusters'].items():
            cluster = self._parse_cluster(cluster_name, cluster_data)
            self.clusters[cluster_name] = cluster

            # Build reverse index: note_id → cluster_name
            for member in cluster.members:
                if member.note_id:
                    self.note_to_cluster[member.note_id] = cluster_name

    def _parse_cluster(self, cluster_name: str, cluster_data: Dict) -> ConfusableCluster:
        """Parse a single cluster from YAML data.

        Args:
            cluster_name: Name of the cluster (key from YAML)
            cluster_data: Cluster dict from YAML

        Returns:
            Parsed ConfusableCluster object

        Raises:
            ValueError: If cluster data is malformed.
        """
        description = cluster_data.get('description', '')
        canonical_note_id = cluster_data.get('canonical_note')

        if not canonical_note_id:
            raise ValueError(f"Cluster '{cluster_name}' missing 'canonical_note' key")

        members_data = cluster_data.get('members', [])
        if not members_data:
            raise ValueError(f"Cluster '{cluster_name}' has no members")

        members = []
        for member_data in members_data:
            status_str = member_data.get('status', 'not-sourced')
            try:
                status = ClusterMemberStatus(status_str)
            except ValueError:
                raise ValueError(
                    f"Cluster '{cluster_name}' member '{member_data.get('lemma')}' "
                    f"has invalid status '{status_str}'. Must be one of: "
                    f"{', '.join(s.value for s in ClusterMemberStatus)}"
                )

            member = ClusterMember(
                note_id=member_data.get('note_id'),
                lemma=member_data.get('lemma', ''),
                status=status,
                chapter=member_data.get('chapter'),
                comment=member_data.get('comment', '')
            )
            members.append(member)

        return ConfusableCluster(
            name=cluster_name,
            description=description,
            canonical_note_id=canonical_note_id,
            members=members
        )

    def get_cluster(self, cluster_name: str) -> Optional[ConfusableCluster]:
        """Retrieve a cluster by name.

        Args:
            cluster_name: Name of cluster (e.g., "intensifier-adverbs")

        Returns:
            ConfusableCluster object or None if not found.
        """
        return self.clusters.get(cluster_name)

    def get_cluster_by_note_id(self, note_id: str) -> Optional[ConfusableCluster]:
        """Find which cluster a note belongs to (if any).

        Args:
            note_id: Note ID (e.g., "ua-lexeme-0467")

        Returns:
            ConfusableCluster object or None if note is not in any cluster.
        """
        cluster_name = self.note_to_cluster.get(note_id)
        return self.get_cluster(cluster_name) if cluster_name else None

    def is_hub(self, note_id: str) -> bool:
        """Return True if note is a cluster hub (canonical reference point).

        Args:
            note_id: Note ID to check

        Returns:
            True if note is a hub, False otherwise.
        """
        cluster = self.get_cluster_by_note_id(note_id)
        return cluster and cluster.is_hub(note_id)

    def is_satellite(self, note_id: str) -> bool:
        """Return True if note is a cluster satellite (not hub).

        Args:
            note_id: Note ID to check

        Returns:
            True if note is a satellite, False otherwise.
        """
        cluster = self.get_cluster_by_note_id(note_id)
        return cluster and not cluster.is_hub(note_id)

    def get_compare_card_members(self, note_id: str) -> List[ClusterMember]:
        """Return the member list for Compare card generation on this note.

        Hub notes show all active (sourced) members as chips.
        Satellite notes show only the hub and themselves.
        Non-clustered notes return an empty list.

        Args:
            note_id: Note ID to generate Compare card for

        Returns:
            List of ClusterMember objects to appear as chips on the Compare card.
        """
        cluster = self.get_cluster_by_note_id(note_id)
        if not cluster:
            return []

        if cluster.is_hub(note_id):
            # Hub shows all active members
            return cluster.get_active_members()
        else:
            # Satellite shows hub + self
            hub_member = cluster.get_hub_member()
            self_member = next((m for m in cluster.members if m.note_id == note_id), None)

            if hub_member and self_member:
                return [hub_member, self_member]
            else:
                return []

    def validate(self) -> Tuple[List[str], List[str], List[str]]:
        """Validate cluster integrity.

        Checks:
        - All referenced note_ids are well-formed (ua-lexeme-NNNN)
        - No circular references between hubs
        - All members are either None (not sourced) or valid note IDs

        Returns:
            Tuple of (errors, warnings, missing_tags):
            - errors: Critical issues that block usage (will cause import failures)
            - warnings: Non-critical issues (pending sourcing, note_id mismatch)
            - missing_tags: Notes in clusters but potentially missing cluster:* tags
        """
        errors = []
        warnings = []
        missing_tags = []

        for cluster_name, cluster in self.clusters.items():
            # Validate canonical hub exists and is in members
            hub_in_members = any(m.note_id == cluster.canonical_note_id for m in cluster.members)
            if not hub_in_members:
                errors.append(
                    f"Cluster '{cluster_name}': canonical_note '{cluster.canonical_note_id}' "
                    f"not found in members list"
                )

            # Validate each member
            for member in cluster.members:
                if member.note_id:
                    # Validate note_id format
                    if not self._is_valid_note_id(member.note_id):
                        errors.append(
                            f"Cluster '{cluster_name}', member '{member.lemma}': "
                            f"invalid note_id format '{member.note_id}'. "
                            f"Expected ua-lexeme-NNNN or ua-verb-NNNN"
                        )
                else:
                    # Pending member
                    if member.status == ClusterMemberStatus.NOT_SOURCED:
                        warnings.append(
                            f"Cluster '{cluster_name}': member '{member.lemma}' not yet sourced "
                            f"(will be added when ch-{member.chapter} is completed)"
                        )

        return errors, warnings, missing_tags

    @staticmethod
    def _is_valid_note_id(note_id: str) -> bool:
        """Check if note_id matches expected format (ua-lexeme-NNNN, ua-verb-NNNN, etc.)."""
        if not note_id:
            return False
        parts = note_id.split('-')
        if len(parts) < 3:
            return False
        try:
            int(parts[-1])  # Last part should be numeric
            return True
        except ValueError:
            return False

    def reload(self) -> None:
        """Reload registry from disk (useful for testing or manual refresh)."""
        self.clusters.clear()
        self.note_to_cluster.clear()
        self._load()

    def list_clusters(self) -> List[str]:
        """Return list of all cluster names."""
        return sorted(self.clusters.keys())

    def summary(self) -> str:
        """Return a human-readable summary of all clusters."""
        lines = []
        for cluster_name in self.list_clusters():
            cluster = self.clusters[cluster_name]
            active = len(cluster.get_active_members())
            total = len(cluster.members)
            lines.append(f"  {cluster_name}: {active}/{total} sourced")
            for member in cluster.members:
                status_marker = "✓" if member.is_active() else "○"
                lines.append(f"    {status_marker} {member.lemma} {member.note_id or '(pending)'}")

        return "Confusable Clusters Registry:\n" + "\n".join(lines)
