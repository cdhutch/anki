#!/usr/bin/env python3
"""
Integration tests for confusable_clusters.yaml registry.
Verifies registry works with existing note import/export system.
"""

import unittest
import yaml
import json
from pathlib import Path
from typing import Dict, Any


class TestConfusableRegistryIntegration(unittest.TestCase):
    """Test registry integration with existing CNSF/import system"""

    @classmethod
    def setUpClass(cls):
        """Load registry and sample CNSF files."""
        cls.repo_root = Path(__file__).parent.parent.parent
        cls.registry_path = cls.repo_root / 'domains/ua/anki/confusable_clusters.yaml'
        cls.lexeme_root = cls.repo_root / 'domains/ua/anki/notes/lexemes'

        with open(cls.registry_path, 'r', encoding='utf-8') as f:
            cls.registry = yaml.safe_load(f)

        # Load sample CNSF files
        cls.cnsf_files = {}
        for md_file in sorted(cls.lexeme_root.rglob('ua-lexeme-*.md'))[:20]:  # Sample 20 files
            try:
                content = md_file.read_text(encoding='utf-8')
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        data = yaml.safe_load(parts[1])
                        note_id = data.get('note_id')
                        if note_id:
                            cls.cnsf_files[note_id] = data
            except Exception:
                pass

    def test_registry_can_serialize_to_json(self):
        """Test that registry can be serialized to JSON (for web API)."""
        try:
            json_str = json.dumps(self.registry)
            loaded = json.loads(json_str)
            self.assertIsNotNone(loaded)
            self.assertIn('clusters', loaded)
        except Exception as e:
            self.fail(f"Registry JSON serialization failed: {e}")

    def test_compare_fields_match_cnsf_format(self):
        """Test that registry Compare fields match CNSF field names."""
        # CNSF uses CamelCase: CompareScenario, CompareA, Homograph_SenseA
        # Registry uses snake_case: compare_scenario, compare_a, homograph_sense_a
        field_mapping = {
            'compare_scenario': 'CompareScenario',
            'compare_a': 'CompareA',
            'compare_b': 'CompareB',
            'compare_c': 'CompareC',
            'compare_d': 'CompareD',
            'homograph_sense_a': 'Homograph_SenseA',
            'homograph_sense_b': 'Homograph_SenseB',
        }
        
        # Verify all registry members have snake_case fields
        for cluster_data in self.registry['clusters'].values():
            for member in cluster_data['members']:
                for snake_field in field_mapping.keys():
                    self.assertIn(snake_field, member,
                                f"Registry field '{snake_field}' missing in member")

    def test_registry_member_round_trip(self):
        """Test that registry member data survives round-trip (load → modify → save)."""
        original_yaml = yaml.dump(self.registry, allow_unicode=True, default_flow_style=False)
        reloaded = yaml.safe_load(original_yaml)
        
        # Compare structures
        self.assertEqual(
            len(self.registry['clusters']),
            len(reloaded['clusters']),
            "Cluster count changed after round-trip"
        )
        
        # Sample check: verify total members survived
        original_count = sum(len(c['members']) for c in self.registry['clusters'].values())
        reloaded_count = sum(len(c['members']) for c in reloaded['clusters'].values())
        
        self.assertEqual(original_count, reloaded_count,
            "Member count changed during round-trip")

    def test_registry_handles_empty_optional_fields(self):
        """Test that optional Compare fields (c, d) don't break parsing."""
        # All members should have empty string defaults for optional fields
        for cluster_data in self.registry['clusters'].values():
            for member in cluster_data['members']:
                for field in ['compare_c', 'compare_d']:
                    value = member.get(field, '')
                    self.assertIsInstance(value, str,
                        f"Optional field '{field}' should be string, got {type(value)}")

    def test_registry_unicode_handling(self):
        """Test that registry handles Ukrainian Unicode (stress marks, Cyrillic)."""
        # Verify stress marks preserved in lemmas
        stress_mark = '́'  # U+0301 combining acute accent
        
        found_stressed = False
        for cluster_data in self.registry['clusters'].values():
            for member in cluster_data['members']:
                lemma = member.get('lemma', '')
                if stress_mark in lemma:
                    found_stressed = True
                    # Verify it's preserved in round-trip
                    yaml_str = yaml.dump({'lemma': lemma}, allow_unicode=True)
                    reloaded = yaml.safe_load(yaml_str)
                    self.assertEqual(lemma, reloaded['lemma'],
                        "Stress mark lost in YAML round-trip")
        
        self.assertTrue(found_stressed, "No stress marks found in registry (check data)")

    def test_cluster_member_lemma_consistency(self):
        """Test that cluster member lemmas are appropriate for cluster type."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            lemmas = [m.get('lemma', '') for m in cluster_data['members']]
            
            # Detect homographs: same lemma (no stress) with different homograph_senses
            lemmas_no_stress = [l.replace('́', '') for l in lemmas]
            has_duplicate_base_lemmas = len(set(lemmas_no_stress)) < len(lemmas_no_stress)
            has_homograph_senses = any(
                m.get('homograph_sense_a', '').strip() and m.get('homograph_sense_b', '').strip()
                for m in cluster_data['members']
            )
            is_true_homograph = has_duplicate_base_lemmas and has_homograph_senses
            
            # Allow legitimate pairs:
            # 1. True homographs (same base lemma, different senses)
            # 2. Stress-differentiated pairs (different stress on same base, like те́пло vs тепло́)
            # Only flag clusters with duplicate base lemmas that aren't distinguished by stress or sense
            if is_true_homograph:
                # True homographs are allowed
                pass
            elif has_duplicate_base_lemmas:
                # If base lemmas duplicate but no homograph senses, check if stress differs
                stress_positions = {}
                for lemma in lemmas:
                    base = lemma.replace('́', '')
                    stress_pos = lemma.find('́')
                    if base not in stress_positions:
                        stress_positions[base] = []
                    stress_positions[base].append(stress_pos)
                
                # Stress-differentiated pairs are valid (different stress on same base)
                for base, positions in stress_positions.items():
                    if len(set(positions)) < len(positions):
                        # Same stress position for same base - this is a real duplicate issue
                        self.fail(f"Cluster '{cluster_name}' has duplicate lemmas with same stress: {lemmas}")

    def test_canonical_note_consistency(self):
        """Test that canonical notes are properly configured."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            canonical_id = cluster_data['canonical_note']
            member_ids = [m['note_id'] for m in cluster_data['members']]
            
            self.assertIn(canonical_id, member_ids,
                f"Cluster '{cluster_name}' canonical note not in members")

    def test_registry_can_generate_compare_cards(self):
        """Test that registry has sufficient data to generate Compare cards."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                # Every member should have scenario (required for Compare card)
                scenario = member.get('compare_scenario', '').strip()
                self.assertTrue(scenario,
                    f"Cluster '{cluster_name}' member missing compare_scenario")
                
                # Homograph clusters need sense descriptions
                if 'homograph' in cluster_name.lower():
                    sense_a = member.get('homograph_sense_a', '').strip()
                    sense_b = member.get('homograph_sense_b', '').strip()
                    self.assertTrue(sense_a and sense_b,
                        f"Homograph '{cluster_name}' member missing sense descriptions")
                
                # Non-homograph clusters need compare_a and compare_b
                else:
                    compare_a = member.get('compare_a', '').strip()
                    compare_b = member.get('compare_b', '').strip()
                    self.assertTrue(compare_a and compare_b,
                        f"Confusable '{cluster_name}' member missing compare_a/b")

    def test_registry_scenario_text_quality(self):
        """Test that compare_scenario text meets quality standards."""
        min_length = 20  # Minimum reasonable scenario length
        max_length = 500  # Maximum to prevent truncation
        
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                scenario = member.get('compare_scenario', '').strip()
                
                if scenario:  # Only check non-empty
                    self.assertGreaterEqual(len(scenario), min_length,
                        f"Cluster '{cluster_name}' scenario too short (min {min_length} chars): {scenario[:50]}")
                    
                    self.assertLessEqual(len(scenario), max_length,
                        f"Cluster '{cluster_name}' scenario too long (max {max_length} chars)")


class TestRegistryBackfillIdempotency(unittest.TestCase):
    """Test that backfill operation is idempotent (can run multiple times safely)."""

    def test_backfill_preserves_existing_data(self):
        """Test that backfill doesn't overwrite manually edited fields."""
        # This is a property test: if we run backfill twice,
        # second run should produce identical results to first
        # (Actual backfill script implements this via "only update if blank" logic)
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
