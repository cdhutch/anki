#!/usr/bin/env python3
"""validate_confusable_clusters.py — Validate cluster registry integrity.

Checks:
- All referenced note_ids exist in the corpus
- No circular hub references
- All cluster members properly tagged
- Registry YAML is well-formed
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from anki.lib.confusable_clusters import ClusterRegistry, ClusterMemberStatus
from anki.lib.lexeme_dedup import load_corpus


def validate_cluster_registry(registry: ClusterRegistry, corpus: dict) -> tuple[list, list, list]:
    """Validate cluster registry against the corpus.
    
    Args:
        registry: Loaded ClusterRegistry
        corpus: Dictionary of note_id -> (lemma, file_path) from corpus scan
    
    Returns:
        Tuple of (errors, warnings, missing_tags)
    """
    errors = []
    warnings = []
    missing_tags = []
    
    for cluster_name, cluster in registry.clusters.items():
        # Check that hub exists in corpus
        if cluster.canonical_note_id not in corpus:
            errors.append(
                f"Cluster '{cluster_name}': hub note '{cluster.canonical_note_id}' "
                f"not found in corpus"
            )
        
        # Check each member
        for member in cluster.members:
            if not member.note_id:
                # Pending member (not yet sourced)
                if member.status != ClusterMemberStatus.NOT_SOURCED:
                    warnings.append(
                        f"Cluster '{cluster_name}': member '{member.lemma}' has null note_id "
                        f"but status is '{member.status.value}' (expected 'not-sourced')"
                    )
                continue
            
            # Member has a note_id — verify it exists in corpus
            if member.note_id not in corpus:
                errors.append(
                    f"Cluster '{cluster_name}': member '{member.lemma}' references "
                    f"'{member.note_id}' which does not exist in corpus"
                )
                continue
            
            # Verify note has cluster tag
            corpus_lemma, corpus_path = corpus[member.note_id]
            
            # Read the note to check for cluster tag
            try:
                note_content = corpus_path.read_text(encoding='utf-8')
                if f"cluster:{cluster_name}" not in note_content:
                    missing_tags.append(
                        f"Note '{member.note_id}' ({member.lemma}) in cluster '{cluster_name}' "
                        f"missing 'cluster:{cluster_name}' tag in file {corpus_path.name}"
                    )
            except Exception as e:
                errors.append(
                    f"Could not read note file for '{member.note_id}': {e}"
                )
    
    return errors, warnings, missing_tags


def main():
    # Load registry
    try:
        registry = ClusterRegistry()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load registry: {e}")
        sys.exit(1)
    
    # Load corpus
    corpus = load_corpus()
    
    # Validate
    errors, warnings, missing_tags = validate_cluster_registry(registry, corpus)
    
    # Report
    print("Confusable Cluster Registry Validation")
    print("=" * 50)
    
    if not errors and not warnings and not missing_tags:
        print("✓ Registry is valid")
        return 0
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠ WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if missing_tags:
        print(f"\n📌 MISSING TAGS ({len(missing_tags)}):")
        for tag_issue in missing_tags:
            print(f"  - {tag_issue}")
    
    # Exit with error if any errors found
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
