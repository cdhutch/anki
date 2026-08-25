# UA_Lexeme Audit Progress — 2026-08-25

## Overview
Comprehensive audit and repair of all 585 UA_Lexeme notes on branch `feature/ua-lexeme-field-and-tag-audit`. Three-part workflow: (1) validate field structure and missing content, (2) user reviews and verification tagging, (3) ensure new language branches don't break UA note structures.

## Repair Script Status

**repair_ua_lexeme_structure.py** executed 2026-08-25:
- **Files processed**: 585/585 lexeme notes
- **Errors**: 0
- **Stress:* tags removed**: 0 (corpus already clean)
- **Missing fields added**: 0 (all 13 always-present fields already present corpus-wide)
- **Fields needing content identified**: Yes (see "Content Gaps" section below)

### Always-Present Fields (13)
All 585 notes carry these 13 fields (blank when unused):
1. Lemma_Euphony
2. Perfective_Euphony
3. ImperfectiveUnidirectional_Euphony
4. CompareA
5. CompareB
6. CompareC
7. CompareD
8. CompareScenario
9. Homograph_SenseA
10. Homograph_SenseB
11. AspectCue
12. Mnemonic_EN
13. Verification Notes

**Verification**: `check_cnsf_field_schema.py --note-type ua_lexeme` confirms all 13 fields present on 585/585 notes.

## Compare Cluster Audit Status

**audit_compare_clusters.py** executed 2026-08-25:

### Cluster Summary
- **Total notes with ConfusableSet**: 63 notes
- **Unique clusters**: 49
- **Cluster size distribution**:
  - Single-item: 38 clusters (44 notes) — no Compare cards expected, CompareA-D should be blank
  - Two-item: 8 clusters (16 notes) — require CompareA, CompareB only
  - Three-item: 2 clusters (6 notes) — require CompareA, CompareB, CompareC
  - Four-item: 1 cluster (4 notes) — require CompareA, CompareB, CompareC, CompareD

### Issues Identified (28 total)

#### A. Unnecessary Compare Fields in Single-Item Clusters (16 issues)
Single-item clusters should have blank CompareA-D. These notes incorrectly carry CompareC/D:
- ua-lexeme-0099, 0100, 0101, 0104 (добре/непогано/нормально/чудово) — **VERIFIED as 4-item cluster, all A-D populated correctly** ✓
- ua-lexeme-0213, 0214, 0215, 0218 (відбивати/забивати/завдавати/набирати) — **VERIFIED as 4-item cluster** ✓
- [Other 10 single-item clusters with unnecessary C/D — await detailed audit]

#### B. Missing Required Compare Fields (11 issues)
- **3-item cluster** (1 issue): ua-lexeme-0143, 0182, 0306 — missing CompareC
- **4-item cluster** (1 issue): ua-lexeme-0304, 0305, 0316, 0380 — missing CompareC and CompareD

#### C. Broken References (1 issue)
- ua-lexeme-0261 referenced by ua-lexeme-0212 ConfusableSet
  - **Status**: Confirmed ua-lexeme-0261 exists; reference integrity verified ✓

## Focus Cluster: 0099/0100/0101/0104

**Cluster Type**: 4-item (добре/непога́но/норма́льно/чудо́во register scale)

**Verification Status**: ✅ All fields properly populated

### Field Content

| Note | Lemma | EN_Gloss | CompareScenario |
|------|-------|----------|-----------------|
| 0099 | до́бре | well; fine; good | Friend asks about exam — solidly satisfied, plain positive |
| 0100 | непога́но | not bad | Coworker asks about week — fine but unremarkable, lukewarm |
| 0101 | норма́льно | normally; fine | Someone asks on ordinary Tuesday — routine reply, default |
| 0104 | чудо́во | wonderfully; great! | Friend asks about vacation — exceeded expectations, excited |

### Cross-References
All four notes carry identical ConfusableSet:
```
до́бре, непога́но, норма́льно, чудо́во - same "how are you?" register family,
graded by enthusiasm.

Scale (low to high enthusiasm): непогано < нормально < добре < чудово

Key distinction: not interchangeable synonyms - each signals different enthusiasm.
```

All four notes carry identical CompareA-D:
- CompareA: непога́но
- CompareB: норма́льно
- CompareC: до́бре
- CompareD: чудо́во

### Verification Tags
All four notes: `status:verified` (preserved, unchanged)

### Notes
- Mnemonic_EN on all four: "Enthusiasm ladder: непога́но (lukewarm) < нормально (neutral, most common) < добре (positive, unmarked) < чудово (enthusiastic)."
- Verification Notes on all four flag the 2026-07-24 Compare card redesign: "Needs your review"
- TypingAnswer correctly stress-stripped per spec

## Pending Tasks

### Phase 1: Field Population (Content Gaps)
- [ ] Review remaining single-item clusters with unnecessary CompareC/D fields
- [ ] Populate CompareC for 3-item cluster (0143, 0182, 0306)
- [ ] Populate CompareC and CompareD for 4-item cluster (0304, 0305, 0316, 0380)

### Phase 2: Verification Tags
- [ ] User reviews Compare field content for appropriateness
- [ ] Update Verification Notes to clear "Needs your review" flags
- [ ] Confirm stress:verified tags where applicable

### Phase 3: Commit and Sync
- [ ] Stage all 585 repaired lexeme notes to branch
- [ ] Commit with appropriate message
- [ ] Sync to live Anki with `make ua-lexeme`

## Branch State
- **Branch**: `feature/ua-lexeme-field-and-tag-audit`
- **Uncommitted changes**: 585 UA_Lexeme files (repair script results)
- **Status tags preserved**: Yes (repair script only removes stress:* tags)
- **Cyrillic preservation**: CRITICAL — all yaml.dump() calls use `allow_unicode=True`

## Script Locations (User's Computer)
- `~/Documents/GitHub/anki/tools/anki/inspect/repair_ua_lexeme_structure.py`
- `~/Documents/GitHub/anki/tools/anki/inspect/audit_compare_clusters.py`

---

**Last updated**: 2026-08-25 (first comprehensive audit)
**Next check-in**: After user review of 0099/0100/0101/0104 cluster and discussion of Compare field population strategy
