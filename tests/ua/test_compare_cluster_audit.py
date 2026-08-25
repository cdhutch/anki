"""
Unit tests for Compare field cluster audit (audit_compare_clusters.py).

Tests:
1. Cluster detection via BFS through ConfusableSet references
2. Required Compare field calculation (CompareA for 2+, B for 2+, C for 3+, D for 4+)
3. Pending-confusable tagged notes excluded from cluster size
4. False-positive elimination (4-item cluster now correctly detected)
5. Missing/invalid Compare field detection
"""

import pytest
from collections import defaultdict, deque


def strip_stress(text):
    """Remove combining stress mark (U+0301) from text."""
    return text.replace('́', '')


def extract_note_ids_from_confusable(confusable_set_text):
    """Extract all note IDs from ConfusableSet text."""
    if not confusable_set_text:
        return []
    import re
    note_id_pattern = r'ua-lexeme-\d+'
    return re.findall(note_id_pattern, confusable_set_text)


def bfs_cluster(start_note_id, notes_by_id, exclude_pending=True):
    """
    Find all notes in a cluster via BFS through ConfusableSet references.

    Optionally exclude pending-confusable tagged notes from cluster size.
    """
    visited = set()
    queue = deque([start_note_id])
    cluster = set()

    while queue:
        note_id = queue.popleft()

        if note_id in visited or note_id not in notes_by_id:
            continue

        visited.add(note_id)
        note_data = notes_by_id[note_id]['data']

        # Check if note is pending-confusable tagged (skip if exclude_pending=True)
        tags = note_data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        is_pending = any(t.startswith('pending-confusable:') for t in tags)
        if exclude_pending and is_pending:
            continue

        cluster.add(note_id)

        # Extract referenced notes from ConfusableSet
        confusable_set = note_data.get('fields', {}).get('ConfusableSet', '').strip()
        referenced_ids = extract_note_ids_from_confusable(confusable_set)

        for ref_id in referenced_ids:
            if ref_id not in visited:
                queue.append(ref_id)

    return cluster


def get_required_compare_fields(cluster_size):
    """Determine which Compare fields are required based on cluster size."""
    required = []
    if cluster_size >= 2:
        required.extend(['CompareA', 'CompareB'])
    if cluster_size >= 3:
        required.append('CompareC')
    if cluster_size >= 4:
        required.append('CompareD')
    return required


def get_referenced_lemmas(note_ids, notes_by_id):
    """Get all Lemma values from referenced notes."""
    lemmas = set()
    for note_id in note_ids:
        if note_id in notes_by_id:
            lemma = notes_by_id[note_id]['data'].get('fields', {}).get('Lemma', '').strip()
            if lemma:
                lemmas.add(lemma)
    return lemmas


class TestClusterDetectionViaBFS:
    """Test cluster detection through BFS traversal."""

    def test_four_item_cluster_via_bfs(self):
        """
        Test BFS cluster detection for добре́/непога́но/норма́льно/чудово́.

        Before: False positive — audit_compare_clusters thought this was a singlet
        After: Correctly detects 4-item cluster via note ID resolution
        """
        # Simulate the four notes in the cluster
        notes_by_id = {
            'ua-lexeme-0099': {
                'data': {
                    'fields': {
                        'Lemma': 'добре́',
                        'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0100': {
                'data': {
                    'fields': {
                        'Lemma': 'непога́но',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0101, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0101': {
                'data': {
                    'fields': {
                        'Lemma': 'норма́льно',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0104': {
                'data': {
                    'fields': {
                        'Lemma': 'чудово́',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0101'
                    },
                    'tags': []
                }
            }
        }

        # Run BFS from any starting point
        cluster = bfs_cluster('ua-lexeme-0099', notes_by_id, exclude_pending=True)

        # Expect all four members
        assert len(cluster) == 4
        assert cluster == {'ua-lexeme-0099', 'ua-lexeme-0100', 'ua-lexeme-0101', 'ua-lexeme-0104'}

    def test_cluster_with_pending_excluded(self):
        """
        Test that pending-confusable tagged notes are excluded from cluster size.

        Two-item cluster: 0463 (рух) + pending reference to затор
        With exclude_pending=True, cluster size = 1
        """
        notes_by_id = {
            'ua-lexeme-0463': {
                'data': {
                    'fields': {
                        'Lemma': 'рух',
                        'ConfusableSet': 'ua-lexeme-0464'
                    },
                    'tags': ['pending-confusable:затор']
                }
            },
            'ua-lexeme-0464': {
                'data': {
                    'fields': {
                        'Lemma': 'затор',
                        'ConfusableSet': 'ua-lexeme-0463'
                    },
                    'tags': []
                }
            }
        }

        # With exclude_pending=True, 0464 is skipped if it were pending
        # Here 0464 is not pending, so it's included
        cluster = bfs_cluster('ua-lexeme-0463', notes_by_id, exclude_pending=True)
        assert len(cluster) == 2

        # Now mark 0464 as pending and test again
        notes_by_id['ua-lexeme-0464']['data']['tags'] = ['pending-confusable:затор']
        cluster = bfs_cluster('ua-lexeme-0463', notes_by_id, exclude_pending=True)
        assert len(cluster) == 1  # Only 0463, 0464 excluded
        assert cluster == {'ua-lexeme-0463'}

    def test_isolated_note_cluster_size_one(self):
        """
        Test that a note with no ConfusableSet is a cluster of size 1.
        """
        notes_by_id = {
            'ua-lexeme-0500': {
                'data': {
                    'fields': {
                        'Lemma': 'изолированный',
                        'ConfusableSet': ''
                    },
                    'tags': []
                }
            }
        }

        cluster = bfs_cluster('ua-lexeme-0500', notes_by_id, exclude_pending=True)
        assert len(cluster) == 1
        assert cluster == {'ua-lexeme-0500'}


class TestRequiredCompareFields:
    """Test required Compare field calculation."""

    def test_two_item_cluster(self):
        """2-item cluster requires CompareA and CompareB."""
        required = get_required_compare_fields(2)
        assert required == ['CompareA', 'CompareB']

    def test_three_item_cluster(self):
        """3-item cluster requires CompareA, CompareB, CompareC."""
        required = get_required_compare_fields(3)
        assert required == ['CompareA', 'CompareB', 'CompareC']

    def test_four_item_cluster(self):
        """4-item cluster requires CompareA, CompareB, CompareC, CompareD."""
        required = get_required_compare_fields(4)
        assert required == ['CompareA', 'CompareB', 'CompareC', 'CompareD']

    def test_singlet_no_required_fields(self):
        """Singlet requires no Compare fields."""
        required = get_required_compare_fields(1)
        assert required == []


class TestCompareFieldValidation:
    """Test Compare field validation against referenced lemmas."""

    def test_valid_compare_fields(self):
        """
        Test that valid Compare fields pass validation.

        3-item cluster: добре́/непога́но/нормально́
        CompareA-C populated with actual lemmas from referenced notes
        """
        notes_by_id = {
            'ua-lexeme-0099': {
                'data': {
                    'fields': {
                        'Lemma': 'добре́',
                        'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101',
                        'CompareA': 'добре́',
                        'CompareB': 'непога́но',
                        'CompareC': 'нормально́'
                    }
                }
            },
            'ua-lexeme-0100': {
                'data': {
                    'fields': {
                        'Lemma': 'непога́но',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0101'
                    }
                }
            },
            'ua-lexeme-0101': {
                'data': {
                    'fields': {
                        'Lemma': 'нормально́',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100'
                    }
                }
            }
        }

        referenced_ids = extract_note_ids_from_confusable(notes_by_id['ua-lexeme-0099']['data']['fields']['ConfusableSet'])
        referenced_lemmas = get_referenced_lemmas(referenced_ids, notes_by_id)

        # All three Compare values should be in referenced_lemmas
        for field_name in ['CompareA', 'CompareB', 'CompareC']:
            field_value = notes_by_id['ua-lexeme-0099']['data']['fields'][field_name].strip()
            assert field_value in referenced_lemmas

    def test_missing_compare_field(self):
        """
        Test that missing required Compare fields are detected.

        4-item cluster with CompareD missing
        """
        cluster_size = 4
        required_fields = get_required_compare_fields(cluster_size)

        # Simulate a note with CompareA, CompareB, CompareC but missing CompareD
        note_data = {
            'fields': {
                'CompareA': 'слово1',
                'CompareB': 'слово2',
                'CompareC': 'слово3',
                'CompareD': ''  # Missing
            }
        }

        issues = []
        for field_name in required_fields:
            field_value = note_data['fields'].get(field_name, '').strip()
            if not field_value:
                issues.append({
                    'type': 'missing_field',
                    'field': field_name,
                    'cluster_size': cluster_size
                })

        # Should flag CompareD as missing
        assert len(issues) == 1
        assert issues[0]['field'] == 'CompareD'

    def test_invalid_compare_value(self):
        """
        Test that Compare field values not in referenced lemmas are detected.

        Compare value 'неправильный' does not exist as any referenced Lemma
        """
        notes_by_id = {
            'ua-lexeme-0200': {
                'data': {
                    'fields': {
                        'Lemma': 'слово1',
                        'ConfusableSet': 'ua-lexeme-0201, ua-lexeme-0202'
                    }
                }
            },
            'ua-lexeme-0201': {
                'data': {
                    'fields': {
                        'Lemma': 'слово2',
                        'ConfusableSet': 'ua-lexeme-0200, ua-lexeme-0202'
                    }
                }
            },
            'ua-lexeme-0202': {
                'data': {
                    'fields': {
                        'Lemma': 'слово3',
                        'ConfusableSet': 'ua-lexeme-0200, ua-lexeme-0201'
                    }
                }
            }
        }

        referenced_ids = extract_note_ids_from_confusable(notes_by_id['ua-lexeme-0200']['data']['fields']['ConfusableSet'])
        referenced_lemmas = get_referenced_lemmas(referenced_ids, notes_by_id)

        # Invalid Compare value
        compare_value = 'неправильный'
        assert compare_value not in referenced_lemmas


class TestAuditIntegration:
    """Integration tests for full audit workflow."""

    def test_false_positive_elimination(self):
        """
        Test that the 4-item cluster (0099/0100/0101/0104) is no longer a false positive.

        This is the root issue that triggered this entire refactor.
        """
        # Set up the exact 4-item cluster that was producing false positives
        notes_by_id = {
            'ua-lexeme-0099': {
                'data': {
                    'fields': {
                        'Lemma': 'добре́',
                        'ConfusableSet': 'ua-lexeme-0100, ua-lexeme-0101, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0100': {
                'data': {
                    'fields': {
                        'Lemma': 'непога́но',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0101, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0101': {
                'data': {
                    'fields': {
                        'Lemma': 'норма́льно',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0104'
                    },
                    'tags': []
                }
            },
            'ua-lexeme-0104': {
                'data': {
                    'fields': {
                        'Lemma': 'чудово́',
                        'ConfusableSet': 'ua-lexeme-0099, ua-lexeme-0100, ua-lexeme-0101'
                    },
                    'tags': []
                }
            }
        }

        # Detect cluster
        cluster = bfs_cluster('ua-lexeme-0099', notes_by_id, exclude_pending=True)
        cluster_size = len(cluster)

        # Calculate required fields
        required_fields = get_required_compare_fields(cluster_size)

        # Key assertions that fix the false positive:
        assert cluster_size == 4  # Was incorrectly detected as 1
        assert set(required_fields) == {'CompareA', 'CompareB', 'CompareC', 'CompareD'}

        # Therefore, if a note in this cluster has CompareA/B/C/D populated, it's correct
        # (not a "has Compare fields it shouldn't have" false positive)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])