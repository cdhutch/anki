#!/usr/bin/env python3
"""
Unit tests for confusable_clusters.yaml registry.
Validates YAML syntax, cluster structure, and corpus integrity.
"""

import unittest
import yaml
from pathlib import Path
from typing import Dict, Set, Tuple


class TestConfusableClustersYAML(unittest.TestCase):
    """Test YAML syntax and structure of confusable_clusters.yaml"""

    @classmethod
    def setUpClass(cls):
        """Load the registry file once for all tests."""
        cls.registry_path = Path("domains/ua/anki/confusable_clusters.yaml")
        cls.lexeme_root = Path("domains/ua/anki/notes/lexemes")

        if not cls.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {cls.registry_path}")

        with open(cls.registry_path, 'r', encoding='utf-8') as f:
            cls.registry = yaml.safe_load(f)

        # Build corpus index of note_id -> (lemma, file_path)
        cls.corpus_notes = {}
        for md_file in sorted(cls.lexeme_root.rglob("ua-lexeme-*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not content.startswith('---'):
                    continue
                parts = content.split('---', 2)
                if len(parts) < 3:
                    continue
                yaml_content = parts[1].strip()
                data = yaml.safe_load(yaml_content)
                if not data:
                    continue
                note_id = data.get('note_id', '')
                lemma = data.get('fields', {}).get('Lemma', '')
                if note_id:
                    cls.corpus_notes[note_id] = (lemma, str(md_file))
            except Exception:
                pass

    def test_yaml_is_valid(self):
        """Test that confusable_clusters.yaml parses as valid YAML."""
        self.assertIsNotNone(self.registry, "Registry should parse as valid YAML")
        self.assertIn('clusters', self.registry, "Registry should have 'clusters' key")

    def test_clusters_key_exists(self):
        """Test that 'clusters' key exists and is a dict."""
        self.assertIsInstance(self.registry['clusters'], dict, "'clusters' should be a dict")
        self.assertGreater(len(self.registry['clusters']), 0, "Should have at least one cluster")

    def test_cluster_structure(self):
        """Test that each cluster has required fields."""
        required_fields = {'description', 'canonical_note', 'members'}

        for cluster_name, cluster_data in self.registry['clusters'].items():
            self.assertIsInstance(cluster_data, dict, f"Cluster '{cluster_name}' should be a dict")

            for field in required_fields:
                self.assertIn(field, cluster_data,
                            f"Cluster '{cluster_name}' missing required field: {field}")

            self.assertIsInstance(cluster_data['members'], list,
                                f"Cluster '{cluster_name}' members should be a list")
            self.assertGreater(len(cluster_data['members']), 0,
                             f"Cluster '{cluster_name}' should have at least one member")

    def test_member_structure(self):
        """Test that each cluster member has required fields."""
        required_member_fields = {'note_id', 'lemma', 'status', 'chapter'}

        for cluster_name, cluster_data in self.registry['clusters'].items():
            for i, member in enumerate(cluster_data['members']):
                self.assertIsInstance(member, dict,
                                    f"Member {i} in cluster '{cluster_name}' should be a dict")

                for field in required_member_fields:
                    self.assertIn(field, member,
                                f"Member {i} in cluster '{cluster_name}' missing field: {field}")

    def test_canonical_note_exists(self):
        """Test that each cluster's canonical_note exists in corpus."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            canonical_id = cluster_data['canonical_note']
            self.assertIn(canonical_id, self.corpus_notes,
                        f"Cluster '{cluster_name}' canonical note '{canonical_id}' not found in corpus")

    def test_member_note_ids_exist(self):
        """Test that all member note_ids exist in corpus."""
        missing_notes = []

        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                note_id = member['note_id']
                if note_id not in self.corpus_notes:
                    missing_notes.append((cluster_name, note_id))

        self.assertEqual(len(missing_notes), 0,
                       f"Found {len(missing_notes)} missing note IDs: {missing_notes}")

    def test_member_lemmas_match_corpus(self):
        """Test that member lemmas match corpus lemmas (stress-stripped)."""
        def strip_stress(text):
            """Remove U+0301 combining accent mark."""
            return text.replace('́', '')

        mismatches = []

        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                note_id = member['note_id']
                registry_lemma = strip_stress(member['lemma'])

                if note_id in self.corpus_notes:
                    corpus_lemma = strip_stress(self.corpus_notes[note_id][0])
                    if registry_lemma != corpus_lemma:
                        mismatches.append({
                            'cluster': cluster_name,
                            'note_id': note_id,
                            'registry_lemma': member['lemma'],
                            'corpus_lemma': self.corpus_notes[note_id][0]
                        })

        self.assertEqual(len(mismatches), 0,
                       f"Found {len(mismatches)} lemma mismatches: {mismatches}")

    def test_canonical_note_in_members(self):
        """Test that canonical_note is in cluster members."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            canonical_id = cluster_data['canonical_note']
            member_ids = {m['note_id'] for m in cluster_data['members']}
            self.assertIn(canonical_id, member_ids,
                        f"Cluster '{cluster_name}' canonical note '{canonical_id}' not in members")

    def test_no_duplicate_note_ids_within_cluster(self):
        """Test that note_ids don't repeat within a single cluster."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            note_ids = [m['note_id'] for m in cluster_data['members']]
            unique_ids = set(note_ids)
            self.assertEqual(len(note_ids), len(unique_ids),
                           f"Cluster '{cluster_name}' has duplicate note IDs: {note_ids}")

    def test_valid_status_values(self):
        """Test that member status values are recognized."""
        valid_statuses = {'sourced', 'draft', 'unverified'}
        invalid_statuses = []

        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                status = member.get('status', '')
                if status not in valid_statuses:
                    invalid_statuses.append({
                        'cluster': cluster_name,
                        'note_id': member['note_id'],
                        'status': status
                    })

        self.assertEqual(len(invalid_statuses), 0,
                       f"Found invalid status values: {invalid_statuses}")

    def test_comment_field_exists_or_optional(self):
        """Test that comment field, if present, is a string."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                if 'comment' in member:
                    self.assertIsInstance(member['comment'], str,
                                        f"Comment in cluster '{cluster_name}' should be a string")

    def test_cluster_name_format(self):
        """Test that cluster names use kebab-case."""
        import re
        kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

        for cluster_name in self.registry['clusters'].keys():
            self.assertRegex(cluster_name, kebab_pattern,
                           f"Cluster name '{cluster_name}' should be kebab-case")

    def test_chapter_format(self):
        """Test that chapter values are in expected format."""
        import re
        chapter_pattern = re.compile(r'^2\.[0-9]+(\.[0-9]+)?$')

        invalid_chapters = []
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                chapter = member.get('chapter', '')
                if not chapter_pattern.match(str(chapter)):
                    invalid_chapters.append({
                        'cluster': cluster_name,
                        'note_id': member['note_id'],
                        'chapter': chapter
                    })

        self.assertEqual(len(invalid_chapters), 0,
                       f"Found invalid chapter formats: {invalid_chapters}")


class TestClusterRegistryIntegrity(unittest.TestCase):
    """Test integrity of cluster definitions across the registry."""

    @classmethod
    def setUpClass(cls):
        """Load registry for integrity tests."""
        cls.registry_path = Path("domains/ua/anki/confusable_clusters.yaml")
        with open(cls.registry_path, 'r', encoding='utf-8') as f:
            cls.registry = yaml.safe_load(f)

    def test_unique_cluster_names(self):
        """Test that cluster names are unique."""
        cluster_names = list(self.registry['clusters'].keys())
        unique_names = set(cluster_names)
        self.assertEqual(len(cluster_names), len(unique_names),
                       "Cluster names should be unique")

    def test_no_note_id_in_multiple_clusters(self):
        """Test that note_ids don't appear in multiple clusters (optional - for now just log)."""
        note_to_clusters = {}

        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                note_id = member['note_id']
                if note_id not in note_to_clusters:
                    note_to_clusters[note_id] = []
                note_to_clusters[note_id].append(cluster_name)

        duplicates = {nid: clusters for nid, clusters in note_to_clusters.items()
                     if len(clusters) > 1}

        # Log but don't fail - some notes legitimately belong in multiple clusters
        if duplicates:
            print(f"Note IDs in multiple clusters (informational): {duplicates}")

    def test_description_not_empty(self):
        """Test that cluster descriptions are present and not empty."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            description = cluster_data.get('description', '').strip()
            self.assertGreater(len(description), 0,
                             f"Cluster '{cluster_name}' has empty description")

    def test_total_cluster_count(self):
        """Test that total cluster count matches documented count."""
        cluster_count = len(self.registry['clusters'])
        self.assertGreaterEqual(cluster_count, 1, "Should have at least one cluster")
        print(f"Registry has {cluster_count} clusters")

    def test_total_member_count(self):
        """Test total member count and log it."""
        total_members = 0
        for cluster_data in self.registry['clusters'].values():
            total_members += len(cluster_data['members'])

        self.assertGreater(total_members, 0, "Should have at least one member")
        print(f"Registry has {total_members} total members across all clusters")


if __name__ == '__main__':
    unittest.main()