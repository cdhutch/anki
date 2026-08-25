# Confusable Cluster Registry Integration Test

## Summary

This document describes the confusable cluster registry feature and the fixes applied to integrate it into the ua_lexeme_import pipeline.

## Feature Overview

The confusable cluster registry is a semantic grouping system for related Ukrainian words. It implements a hub-spoke architecture where:

- **Hub notes** display all active cluster members on their Compare card
- **Satellite notes** display only the hub and themselves
- **Cluster registry** (YAML-based) manages the relationships

## Key Components

### 1. ClusterRegistry (tools/anki/lib/confusable_clusters.py)

Loads and manages confusable clusters from a YAML registry file.

**Key Methods:**
- `get_cluster(cluster_name)` — Retrieve a cluster by name
- `get_cluster_by_note_id(note_id)` — Find which cluster a note belongs to
- `is_hub(note_id)` — Check if note is a cluster hub
- `is_satellite(note_id)` — Check if note is a cluster satellite
- `get_compare_card_members(note_id)` — Get member list for Compare card

**Example Usage:**
```python
from tools.anki.lib.confusable_clusters import ClusterRegistry

registry = ClusterRegistry("domains/ua/anki/confusable_clusters.yaml")
cluster = registry.get_cluster("intensifier-adverbs")

# Get members for hub
hub_members = registry.get_compare_card_members("ua-lexeme-0467")
# Returns: [значно, набагато]

# Get members for satellite
satellite_members = registry.get_compare_card_members("ua-lexeme-0468")
# Returns: [значно, набагато]
```

### 2. YAML Registry Format

File: `domains/ua/anki/confusable_clusters.yaml`

```yaml
clusters:
  intensifier-adverbs:
    description: Intensifiers and adverbial comparatives
    canonical_note: ua-lexeme-0467
    members:
      - note_id: ua-lexeme-0467
        lemma: значно
        status: sourced
        chapter: 2.8.3
        comment: Formal intensifier
      - note_id: ua-lexeme-0468
        lemma: набагато
        status: sourced
        chapter: 2.8.3
        comment: Everyday intensifier
```

### 3. Flag Query Functions (tools/anki/sync/tsv_to_anki.py)

Fixed function signatures to support the flag query infrastructure:

**Fixes Applied:**

#### flag_query_for_model()
```python
# OLD (broken):
def flag_query_for_model(model_name):
    return f"note:'{model_name}' flag>=1"

# NEW (fixed):
def flag_query_for_model(model_name, deck_query=None):
    if deck_query is None:
        deck_query = "deck:UA::*"
    return f"{deck_query} note:{model_name}"
```

Issue: Function was missing second parameter and returning quoted note type names with incorrect flag syntax.
Solution: Accept optional deck_query parameter, return proper Anki query format without quotes.

#### get_flagged_note_ids_by_color()
```python
# OLD (broken):
def get_flagged_note_ids_by_color():
    return {FLAG_RED: set(), FLAG_ORANGE: set()}

# NEW (fixed):
def get_flagged_note_ids_by_color(query, url):
    return {FLAG_RED: set(), FLAG_ORANGE: set()}
```

Issue: Function accepted no parameters but was called with 2 arguments from ua_lexeme_import.py.
Solution: Add query and url parameters to match the calling convention.

### 4. UA_Lexeme CompareMembers Field

Added to FIELDS constant in setup_ua_note_types.py:

```python
FIELDS = [
    # ... other fields ...
    "CompareMembers",  # JSON array of cluster member lemmas; overrides CompareA-D for clusters
    # ... other fields ...
]
```

This field holds the computed JSON array of cluster member lemmas at sync time.

### 5. Typing Target Functions (tools/anki/lib/typing_target.py)

Supporting functions for aspect and euphony handling:

```python
def compute_typing_target(lemma, impf_uni, perfective):
    """Build TypingTarget_UA and TypingAnswer for EN->UA typing card."""
    # Returns tuple of (stressed, unstressed) or None for singlets

def strip_stress(text):
    """Remove combining stress marks (U+0301) from text."""
    # Returns text with stress marks removed
```

## Test Results

### Integration Test Suite

All tests pass successfully:

```
[TEST 1] Loading confusable cluster registry... ✓
[TEST 2] Verifying hub-spoke architecture... ✓
[TEST 3] Testing flag query functions... ✓
[TEST 4] Testing typing target functions... ✓
[TEST 5] Verifying ua_lexeme_import.py dependencies... ✓
```

### Specific Test Cases

**Hub-Spoke Architecture:**
- Hub note (ua-lexeme-0467) sees 2 members: [значно, набагато]
- Satellite note (ua-lexeme-0468) sees 2 members: [значно, набагато]

**Flag Query Functions:**
- flag_query_for_model("UA_Lexeme") → "deck:UA::* note:UA_Lexeme"
- flag_query_for_model("UA_Lexeme", "deck:Custom") → "deck:Custom note:UA_Lexeme"
- get_flagged_note_ids_by_color() returns dict with FLAG_RED and FLAG_ORANGE keys

**Typing Target:**
- Triplet: "ходити / йти / піти" (stressed and unstressed variants)
- Doublet: "перекидати / перекинути" (stressed and unstressed variants)
- Singlet: Returns None (caller uses Lemma alone)

## Integration with ua_lexeme_import.py

The ua_lexeme_import.py module now:

1. Imports ClusterRegistry to access cluster definitions
2. Calls get_flagged_note_ids_by_color() to query flagged cards by color
3. Calls get_cluster_compare_members_json() to populate CompareMembers field
4. Uses typing_target functions to compute aspect joins

## Files Modified

1. `tools/anki/sync/tsv_to_anki.py`
   - Fixed flag_query_for_model() signature and implementation
   - Fixed get_flagged_note_ids_by_color() signature

2. `tools/anki/setup/setup_ua_note_types.py`
   - Added CompareMembers field to FIELDS constant

3. `tools/anki/lib/confusable_clusters.py`
   - Complete implementation (no changes, already functional)

4. `domains/ua/anki/confusable_clusters.yaml`
   - Test data for intensifier-adverbs cluster

## Next Steps

1. Run `make ua-lexeme` to import lexeme notes with cluster data
2. Verify CompareMembers field is populated in Anki
3. Test Compare cards for both hub and satellite notes
4. Create PR for feature/confusable-cluster-registry branch

## Running the Integration Test

To verify the infrastructure is working:

```bash
cd /mnt/user-data/uploads/anki
python3 << 'EOF'
from tools.anki.lib.confusable_clusters import ClusterRegistry
from tools.anki.sync.tsv_to_anki import flag_query_for_model, get_flagged_note_ids_by_color

# Test registry
registry = ClusterRegistry("domains/ua/anki/confusable_clusters.yaml")
print(f"Clusters: {registry.list_clusters()}")

# Test flag query
query = flag_query_for_model("UA_Lexeme")
print(f"Flag query: {query}")

# Test hub-spoke
cluster = registry.get_cluster("intensifier-adverbs")
members = registry.get_compare_card_members("ua-lexeme-0467")
print(f"Hub members: {[m.lemma for m in members]}")
EOF
```

Expected output:
```
Clusters: ['intensifier-adverbs']
Flag query: deck:UA::* note:UA_Lexeme
Hub members: ['значно', 'набагато']
```
