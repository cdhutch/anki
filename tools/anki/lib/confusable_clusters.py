"""Confusable word cluster registry and validation.

Manages canonical groupings of semantically-related words (confusable clusters).
Each cluster has a hub (canonical reference note) and satellites. Hub notes show
all active cluster members on their Compare card; satellites show only the hub
and themselves -- UNLESS the cluster sets show_all_members: true, in which case
every member's card (hub or satellite) shows the full active member list. See
ConfusableCluster.show_all_members and get_compare_card_members().

Registry is loaded from domains/ua/anki/confusable_clusters.yaml
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
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
    compare_scenario: str = ""  # Usage context distinguishing this word from cluster-mates
    example_ua: str = ""  # Sentence mode only: authored UA sentence for this sense
    meaning_en: str = ""  # Sentence mode only: English meaning revealed as the answer

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
    show_all_members: bool = False  # opt-in: every member's card shows the
    # full active member list, not just hub-shows-all/satellite-shows-hub+self.
    # Set via show_all_members: true at the cluster level in the YAML registry.
    # Default False preserves existing hub/satellite behavior for every
    # cluster that doesn't opt in.

    def get_active_members(self) -> List[ClusterMember]:
        """Return only sourced members (those with note_id not None)."""
        return [m for m in self.members if m.is_active()]

    def get_hub_member(self) -> Optional[ClusterMember]:
        """Return the hub member object."""
        return next((m for m in self.members if m.note_id == self.canonical_note_id), None)

    def is_hub(self, note_id: str) -> bool:
        """Return True if note_id is this cluster's canonical hub."""
        return note_id == self.canonical_note_id

    def is_sentence_mode(self) -> bool:
        """True if this cluster renders as a sentence-mode Compare card.

        Mirrors the exact condition get_cluster_compare_members_json() in
        ua_lexeme_import.py uses to choose sentence mode over chip mode:
        every active member shares one identical lemma string (a true
        homophone -- nothing in the spelling distinguishes the senses) AND
        every active member has both example_ua and meaning_en populated.
        Kept here as the single source of truth so the renderer and the
        validator (validate()) can't drift apart -- an identical-lemma
        cluster that's missing example_ua/meaning_en on some member is NOT
        sentence mode; it silently falls back to chip mode instead, which
        is a degenerate card (same spelling shown twice, nothing to
        distinguish it) that validate() flags as an error.
        """
        active = self.get_active_members()
        if len(active) < 2:
            return False
        lemmas = {m.lemma for m in active}
        return len(lemmas) == 1 and all(m.example_ua and m.meaning_en for m in active)

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
        self._release_active_ids: Optional[Set[str]] = None  # lazy cache, see get_release_active_note_ids()
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
                comment=member_data.get('comment', ''),
                compare_scenario=member_data.get('compare_scenario', ''),
                example_ua=member_data.get('example_ua', ''),
                meaning_en=member_data.get('meaning_en', '')
            )
            members.append(member)

        return ConfusableCluster(
            name=cluster_name,
            description=description,
            canonical_note_id=canonical_note_id,
            members=members,
            show_all_members=bool(cluster_data.get('show_all_members', False))
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

    def get_release_active_note_ids(
        self, note_roots: Optional[List[Path]] = None
    ) -> Set[str]:
        """Return every note_id that is status:verified AND release:active.

        Scans CNSF note files directly (not the registry -- the registry
        only knows a member is "sourced", i.e. has a note_id; it has no
        idea whether that note's own tags currently make it live in Anki).
        Used to filter Compare card membership down to cluster-mates that
        are actually reachable elsewhere in the deck, so a verified/active
        hub's Compare card doesn't reference a still-draft sibling the
        learner has never seen unsuspended.

        Result is cached on first call (registry content doesn't change
        within a process; call reload() to invalidate along with the rest
        of the registry's cached state).

        Args:
            note_roots: Directories to scan for *.md CNSF notes. Defaults to
                the standard UA lexeme/verb note directories under repo root.

        Returns:
            Set of note_ids whose tags include both status:verified and
            release:active.
        """
        if self._release_active_ids is not None:
            return self._release_active_ids

        if note_roots is None:
            repo_root = Path(__file__).resolve().parents[3]
            note_roots = [
                repo_root / "domains" / "ua" / "anki" / "notes" / "lexemes",
                repo_root / "domains" / "ua" / "anki" / "notes" / "verbs",
            ]

        ids: Set[str] = set()
        for root in note_roots:
            if not root.exists():
                continue
            for md_file in root.rglob("*.md"):
                try:
                    text = md_file.read_text(encoding="utf-8")
                except OSError:
                    continue
                if not text.startswith("---"):
                    continue
                parts = text.split("---", 2)
                if len(parts) < 3:
                    continue
                try:
                    front = yaml.safe_load(parts[1])
                except yaml.YAMLError:
                    continue
                if not front:
                    continue
                note_id = front.get("note_id")
                tags = front.get("tags") or []
                if note_id and "status:verified" in tags and "release:active" in tags:
                    ids.add(note_id)

        self._release_active_ids = ids
        return ids

    def get_compare_card_members(
        self, note_id: str, release_active_ids: Optional[Set[str]] = None
    ) -> List[ClusterMember]:
        """Return the member list for Compare card generation on this note.

        Hub notes show all active (sourced) members as chips.
        Satellite notes show only the hub and themselves -- UNLESS the
        cluster has show_all_members: true set, in which case every member
        (hub or satellite) shows the full active member list.
        Non-clustered notes return an empty list.

        Args:
            note_id: Note ID to generate Compare card for
            release_active_ids: When given, the returned members are
                additionally filtered down to those whose note_id is in
                this set -- i.e. cluster-mates that are themselves
                status:verified/release:active, and thus actually reachable
                elsewhere in Anki. When None (default), behavior is
                unchanged from before this filter existed: every sourced
                cluster-mate is included regardless of its own status.

        Returns:
            List of ClusterMember objects to appear as chips on the Compare card.
        """
        cluster = self.get_cluster_by_note_id(note_id)
        if not cluster:
            return []

        if cluster.show_all_members or cluster.is_hub(note_id):
            # show_all_members clusters: every member shows the full list.
            # Otherwise, hub shows all active members.
            members = cluster.get_active_members()
        else:
            # Satellite shows hub + self
            hub_member = cluster.get_hub_member()
            self_member = next((m for m in cluster.members if m.note_id == note_id), None)

            if hub_member and self_member:
                members = [hub_member, self_member]
            else:
                members = []

        if release_active_ids is not None:
            members = [m for m in members if m.note_id in release_active_ids]

        return members

    def validate(self) -> Tuple[List[str], List[str], List[str]]:
        """Validate cluster integrity.

        Checks:
        - All referenced note_ids are well-formed (ua-lexeme-NNNN)
        - No circular references between hubs
        - All members are either None (not sourced) or valid note IDs
        - Compare-card content won't render degenerate (see _validate_compare_cards)

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

        self._validate_compare_cards(errors)

        return errors, warnings, missing_tags

    def _validate_compare_cards(self, errors: List[str]) -> None:
        """Catch structural Compare-card defects that don't need semantic
        judgment to detect -- the actual failure modes hit in production
        (2026-08-31): a chip cluster shipped with no scenario at all, two
        stress-shift homographs whose scenario was boilerplate copy-pasted
        across both members, and a near-synonym pair whose scenario named
        the answer word directly. Deliberately does NOT judge whether a
        scenario is well-written, just whether it's structurally capable of
        distinguishing the members -- see validate_clusters.py's docstring
        for what this can't catch and why. Appends to `errors` in place
        (these are hard failures, meant to block a sync, not warnings).
        """
        for cluster_name, cluster in self.clusters.items():
            active = cluster.get_active_members()
            if len(active) < 2:
                continue  # nothing to distinguish with only 0-1 sourced members

            if cluster.is_sentence_mode():
                continue  # compare_scenario is unused in sentence mode

            lemmas = {m.lemma for m in active}
            if len(lemmas) == 1:
                # Identical lemma but is_sentence_mode() said no -> some
                # member is missing example_ua/meaning_en, so this will
                # silently render as chip mode: the same spelling shown
                # twice with nothing to distinguish it. The original
                # "chips but no scenario" bug this registry exists to
                # prevent.
                missing = [
                    m.note_id for m in active
                    if not (m.example_ua and m.meaning_en)
                ]
                errors.append(
                    f"Cluster '{cluster_name}': members share identical lemma "
                    f"'{next(iter(lemmas))}' (a true homophone) but sentence-mode "
                    f"data is incomplete -- missing example_ua/meaning_en on: "
                    f"{', '.join(missing)}. Without it this renders as "
                    f"indistinguishable chips (same spelling twice, no scenario)."
                )

            scenario_owners: Dict[str, List[str]] = {}
            for member in active:
                scenario = (member.compare_scenario or '').strip()
                if not scenario:
                    errors.append(
                        f"Cluster '{cluster_name}', member '{member.note_id}' "
                        f"({member.lemma}): compare_scenario is empty -- card "
                        f"will show chips with no distinguishing context"
                    )
                    continue

                scenario_owners.setdefault(scenario, []).append(member.note_id)

                for other_lemma in lemmas:
                    if other_lemma and other_lemma in scenario:
                        errors.append(
                            f"Cluster '{cluster_name}', member '{member.note_id}': "
                            f"compare_scenario contains the lemma '{other_lemma}' "
                            f"verbatim -- gives away the answer instead of "
                            f"describing a situation"
                        )
                        break

            for scenario, owners in scenario_owners.items():
                if len(owners) > 1:
                    preview = scenario if len(scenario) <= 70 else scenario[:67] + '...'
                    errors.append(
                        f"Cluster '{cluster_name}': {len(owners)} members "
                        f"({', '.join(owners)}) share identical compare_scenario "
                        f"text (\"{preview}\") -- doesn't distinguish them"
                    )

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
        self._release_active_ids = None
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
