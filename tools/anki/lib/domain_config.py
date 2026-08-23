#!/usr/bin/env python3
"""Domain configuration loader for multi-language Anki expansion.

Loads YAML domain configs that declare:
- Field schemas per note type
- Computed fields (populated at import time, never authored in CNSF)
- Always-present fields (blank default for every note)
- Sparse fields (okay to be blank across corpus)
- Suspension policy (tag/flag/content-based)
- Text normalization rules (apostrophes, etc.)
- CSS theme

Replaces hardcoded domain-specific logic in cnsf_canonicalize.py and import scripts.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class NoteTypeConfig:
    """Configuration for a single note type within a domain."""
    name: str
    fields: List[str]  # Ordered field list matching live Anki model
    computed_fields: List[str] = field(default_factory=list)  # Fields never authored in CNSF
    always_present_fields: List[str] = field(default_factory=list)  # Fields with blank default
    sparse_fields: List[str] = field(default_factory=list)  # Fields okay to be blank
    compare_card_enabled: bool = False  # Whether to generate Compare cards


@dataclass
class SuspensionPolicy:
    """Rules for when notes should be suspended."""
    tag_suspend: List[str] = field(default_factory=list)  # Tags that force suspension
    tag_no_suspend: List[str] = field(default_factory=list)  # Tags that override suspension
    flag_suspend: List[int] = field(default_factory=list)  # Flag numbers (1=red, 2=orange, etc)
    compare_card_suspend: bool = False  # Suspend Compare card if ConfusableSet but no Compare fields


@dataclass
class DomainConfig:
    """Runtime configuration for a language domain."""
    domain: str
    display_name: str
    note_types: Dict[str, NoteTypeConfig] = field(default_factory=dict)
    suspension_policy: SuspensionPolicy = field(default_factory=SuspensionPolicy)
    apostrophe_normalization: str = "u02bc"  # U+02BC is standard across Slavic
    css_theme: str = "gruvbox"  # Or inline CSS if needed

    @classmethod
    def load(cls, domain: str, config_dir: Path | None = None) -> DomainConfig:
        """Load domain config from YAML file.

        Args:
            domain: Domain name (e.g., 'ua', 'de', 'cs')
            config_dir: Directory containing domain YAML files.
                       Defaults to tools/anki/config/domains/

        Returns:
            Loaded and validated DomainConfig
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config" / "domains"

        config_path = config_dir / f"{domain}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {config_path}")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Parse note types
        note_types = {}
        for nt_name, nt_data in data.get("note_types", {}).items():
            note_types[nt_name] = NoteTypeConfig(
                name=nt_name,
                fields=nt_data.get("fields", []),
                computed_fields=nt_data.get("computed_fields", []),
                always_present_fields=nt_data.get("always_present_fields", []),
                sparse_fields=nt_data.get("sparse_fields", []),
                compare_card_enabled=nt_data.get("compare_card_enabled", False),
            )

        # Parse suspension policy
        policy_data = data.get("suspension_policy", {})
        suspension_policy = SuspensionPolicy(
            tag_suspend=policy_data.get("tag_suspend", []),
            tag_no_suspend=policy_data.get("tag_no_suspend", []),
            flag_suspend=policy_data.get("flag_suspend", []),
            compare_card_suspend=policy_data.get("compare_card_suspend", False),
        )

        return cls(
            domain=domain,
            display_name=data.get("display_name", domain.upper()),
            note_types=note_types,
            suspension_policy=suspension_policy,
            apostrophe_normalization=data.get("apostrophe_normalization", "u02bc"),
            css_theme=data.get("css_theme", "gruvbox"),
        )

    def get_fields(self, note_type: str) -> List[str]:
        """Get ordered field list for a note type."""
        if note_type not in self.note_types:
            raise ValueError(f"Unknown note type: {note_type}")
        return self.note_types[note_type].fields

    def get_computed_fields(self, note_type: str) -> List[str]:
        """Get list of computed field names for a note type."""
        if note_type not in self.note_types:
            raise ValueError(f"Unknown note type: {note_type}")
        return self.note_types[note_type].computed_fields

    def get_always_present_fields(self, note_type: str) -> List[str]:
        """Get fields that should exist (with blank default) on every note."""
        if note_type not in self.note_types:
            raise ValueError(f"Unknown note type: {note_type}")
        return self.note_types[note_type].always_present_fields

    def get_sparse_fields(self, note_type: str) -> List[str]:
        """Get fields that are okay to be blank across the corpus."""
        if note_type not in self.note_types:
            raise ValueError(f"Unknown note type: {note_type}")
        return self.note_types[note_type].sparse_fields

    def should_suspend(
        self,
        tags: List[str],
        flags: List[int],
        fields: Dict[str, str] | None = None,
    ) -> bool:
        """Determine if a note should be suspended based on suspension policy.

        Args:
            tags: List of note tags
            flags: List of flag numbers (1=red, 2=orange, etc)
            fields: Field dict (for content-based checks like Compare cards)

        Returns:
            True if note should be suspended
        """
        # Check tag-based suspension
        for tag in tags:
            if tag in self.suspension_policy.tag_suspend:
                # Check for override tags
                if not any(t in tags for t in self.suspension_policy.tag_no_suspend):
                    return True

        # Check flag-based suspension
        for flag in flags:
            if flag in self.suspension_policy.flag_suspend:
                return True

        return False

    def normalize_text(self, text: str) -> str:
        """Apply domain-specific text normalization (apostrophes, etc).

        Only normalize apostrophes in text that contains Cyrillic characters
        (e.g., Ukrainian, Russian, Czech uses Latin). This preserves English
        contractions like "it's" while normalizing Ukrainian text.
        """
        if self.apostrophe_normalization == "u02bc":
            # Only normalize if text contains Cyrillic characters (Ukrainian/Russian/etc.)
            # Cyrillic range: U+0400 to U+04FF
            if any('Ѐ' <= c <= 'ӿ' for c in text):
                # Normalize to U+02BC (MODIFIER LETTER APOSTROPHE)
                # Replace common apostrophe variants
                text = text.replace("'", "ʼ")  # ASCII apostrophe
                text = text.replace("'", "ʼ")  # Right single quotation mark
                text = text.replace("ʼ", "ʼ")  # Ensure consistency
        return text
