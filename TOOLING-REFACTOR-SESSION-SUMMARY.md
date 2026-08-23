# Multi-Domain Anki Expansion: Tooling Refactor Session Summary

**Session Date:** 2026-08-22  
**Branch:** `feature/expansion-german-czech-slovak-ipa`  
**Status:** Foundational architecture complete; implementation in progress

---

## Table of Contents

1. [Project Context](#project-context)
2. [Current Implementation Architecture](#current-implementation-architecture)
3. [Hardcoded Logic Identified](#hardcoded-logic-identified)
4. [Refactoring Architecture](#refactoring-architecture)
5. [Implementation Strategy for Lexeme and Alphabet](#implementation-strategy)
6. [Testing and Validation](#testing-and-validation)
7. [Immediate Next Steps](#immediate-next-steps)

---

## Project Context

Craig is extending the Anki flashcard system beyond its current Ukrainian-only implementation to support four additional language domains: **German, Czech, Slovak, and IPA** (International Phonetic Alphabet).

The core challenge is that the current codebase contains **hardcoded Ukraine-specific logic** throughout the canonicalization and import pipeline. The refactoring goal is to extract this domain-specific configuration into **parameterized, data-driven structures** so that new languages can be added with minimal code duplication.

### Timeline Constraint
Trip to Czechia/Slovakia approximately one month from session date, with **Czech at 2x priority** (extended time there).

### Master Content Plan
- **70-phrase master English list** (locked across all three languages)
- **German:** 3-5 days implementation, baseline for refactoring
- **Czech:** 1-2 weeks (lexeme + new Alphabet note type for phonemes)
- **Slovak:** 1-2 weeks (similar to Czech, parallel work possible)
- **IPA:** 1 week optional (standalone specialized domain)

---

## Current Implementation Architecture

### CNSF Format Foundation
**CNSF v0** = YAML frontmatter + markdown body. All notes are version-controlled as markdown files organized hierarchically by domain and chapter (e.g., `domains/ua/anki/notes/lexemes/yabluko-l2/ch-09/ua-lexeme-0114.md`).

### Field Schema Pattern: UA_Lexeme Example
The UA_Lexeme note type has **38 ordered fields** grouped logically into eight tiers:

1. **Identity** (1): NoteID
2. **Core lemma & morphology** (8): Lemma, Lemma_Euphony, PartOfSpeech, Gender, ImperfectiveUnidirectional, ImperfectiveUnidirectional_Euphony, Perfective, Perfective_Euphony
3. **Computed/display-only** (3): _AspectLabel, _UA_EN_DisplayLemma, _IsHomograph (never authored, populated at sync)
4. **Semantic content** (1): EN_Gloss
5. **Grammatical properties** (4): Govt_Case, IrregularForms, CounterpartForm, VerbMotion_Pair
6. **Semantic relations & Compare** (9): ConfusableSet, Mnemonic_EN, CompareScenario, CompareA-D, Homograph_SenseA-B, CrossLang_Analog
7. **Typing & examples** (5): TypingTarget_UA, TypingAnswer, _TypingSpec, UA_Example, EN_Example
8. **Metadata & sources** (4): Tags_Ch, Source_URL, Source_Note, Verification Notes

### New Domain Requirements
- **German Lexeme:** 15-20 fields (no aspect/euphony complexity)
- **Czech Lexeme:** ~25 fields (richer than German, aspect complexity minimal)
- **Czech Alphabet:** 15 fields (phoneme, IPA symbol, audio, examples, metadata)

### Computed Fields Pattern
Three categories populated by import scripts at sync time, never authored in CNSF:

- **Aspect-driven:** _AspectLabel (displays "(impf.)" or "(pf.)" for singlets)
- **Euphony-driven:** _UA_EN_DisplayLemma, _TypingSpec (compact JSON for grading)
- **Compare-driven:** _IsHomograph (boolean from tags, switches Compare layout)

### Card Routing Logic
Routes to decks based on template name:
- "UA→EN" → `UA::Recognition::UA→EN`
- "EN→UA" → `UA::Production::EN→UA`
- "Compare" → `UA::Recognition::Compare`

**This logic is domain-agnostic** and can be centralized.

### Suspension Policy (Declarative, Self-Healing)
Suspends/unsuspends based on:
- **Tag-based:** `status:draft`, `stress:unverified` force suspension
- **Flag-based:** red flags force suspension, orange flags print call-out only
- **Content-based:** Compare card suspends if ConfusableSet populated but CompareA/B blank
- **Override:** `conj:suspended` tag independently controls drilling

**Completely domain-agnostic** — queries only note type + tags + flags + field content.

### CSS and Styling
Single Gruvbox palette with dark-mode support:
- **Light:** bg0 #fbf1c7, fg1 #3c3836
- **Dark:** bg0 #282828, fg1 #ebdbb2
- **Accent A (orange):** #af3a03 light / #fe8019 dark
- **Accent B (blue):** #076678 light / #83a598 dark

Suitable for all planned languages; parameterizable per domain.

---

## Hardcoded Logic Identified

### In `cnsf_canonicalize.py`

**Lines 28-34:** Direct imports of field constants from setup_ua_note_types.py and setup_ua_pvom_note_type.py. These are **domain-specific and hardcoded**.

**Lines 65-71:** `CANON_FIELD_ORDER` dictionary lists **only Ukrainian note types** (ua_lexeme, ua_grammar, ua_visual, ua_verb, ua_pvom_infinitive). No domain-aware structure.

**Lines 299-326 in `_normalize_meta()`:** Field injection is **completely hardcoded**:
- Unconditionally inject "Verification Notes" with blank default
- Check if `note_type == "ua_lexeme"` → inject 12 optional fields
- Check if `note_type == "ua_pvom_infinitive"` → inject 4 euphony fields
- Check if `note_type == "ua_verb"` → inject Source_Note

**Lines 117-130 in `_canonical_field_order()`:** Good, domain-agnostic logic. Reusable as-is.

**Lines 155+:** Ukrainian apostrophe normalization. Language-specific; move to domain config.

**CLI entry points:** cmd_check() and cmd_write() hardcoded to process all files. Need `--domain` parameter.

### In `setup_ua_note_types.py`

**Lines 34-161:** FIELDS constant is hardcoded. Field grouping pattern is **excellent and should be preserved** for new domains.

**Lines 167-299:** CSS hardcoded in script. Should move to domain config YAML; all languages can share Gruvbox.

### In `ua_lexeme_import.py`

**Lines 73, 75-93:** MODEL_NAME, DECK configuration hardcoded for UA. Need `--model`, `--domain` parameters.

**Lines 236-318 in `compute_typing_spec()`:** Generates _TypingSpec JSON. **Ukrainian-specific** (aspect morphology). German needs different logic; Czech similar to UA.

**Lines 320-353 in `compute_ua_en_display()`:** Aspect-driven. **Ukrainian-specific.**

**Lines 356-373 in `compute_compare_options()`:** Deterministic Compare card ordering. **Domain-agnostic and excellent.**

**Lines 376-522 in `import_note()`:** Suspension policy (lines 473-496) is **domain-agnostic** and must be extracted to shared utility.

### In `Makefile`

**Lines 700-999:** Pattern is **highly formulaic and reusable**:
- Each domain declares ROOT paths
- Each note type has check/fix/sync targets: find → canonicalize → import
- Targets aggregate with domain prefixes

**Can be auto-generated for new domains.**

---

## Refactoring Architecture

### 1. Domain Configuration Files

Created `tools/anki/config/domains/<domain>.yaml` structure:

```yaml
domain: ua
display_name: Ukrainian

note_types:
  ua_lexeme:
    fields: [ordered list]
    computed_fields: [_AspectLabel, _UA_EN_DisplayLemma, ...]
    always_present_fields: [Lemma_Euphony, ...]
    sparse_fields: [ImperfectiveUnidirectional, ...]
    compare_card_enabled: true

suspension_policy:
  tag_suspend: [status:draft, stress:unverified]
  tag_no_suspend: [conj:drill]
  flag_suspend: [1]  # red flag

apostrophe_normalization: u02bc
css_theme: gruvbox
```

**Created:**
- `tools/anki/config/domains/ua.yaml` — reference implementation
- `tools/anki/config/domains/de.yaml` — minimal German schema

**German example:** 20 fields, no computed fields, minimal always-present set (Gender, Article, Verification Notes).

### 2. DomainConfig Class

Created `tools/anki/lib/domain_config.py`:

```python
@dataclass
class NoteTypeConfig:
    name: str
    fields: List[str]  # Ordered
    computed_fields: List[str]
    always_present_fields: List[str]
    sparse_fields: List[str]
    compare_card_enabled: bool

@dataclass
class SuspensionPolicy:
    tag_suspend: List[str]
    tag_no_suspend: List[str]
    flag_suspend: List[int]
    compare_card_suspend: bool

@dataclass
class DomainConfig:
    domain: str
    display_name: str
    note_types: Dict[str, NoteTypeConfig]
    suspension_policy: SuspensionPolicy
    apostrophe_normalization: str
    css_theme: str
    
    @classmethod
    def load(cls, domain: str, config_dir: Path | None = None) -> DomainConfig:
        # Loads from YAML
    
    def get_fields(self, note_type: str) -> List[str]
    def get_computed_fields(self, note_type: str) -> List[str]
    def get_always_present_fields(self, note_type: str) -> List[str]
    def should_suspend(self, tags, flags, fields) -> bool
    def normalize_text(self, text: str) -> str
```

**Key design decision:** Load configuration at runtime instead of hardcoding conditionals. This eliminates the coupling between code and domain-specific metadata.

### 3. Refactored cnsf_canonicalize.py

**Changes:**
- Add `--domain` CLI parameter
- Load DomainConfig instead of hardcoded imports
- Replace `_normalize_meta()` hardcoded logic with config-driven field injection
- Replace `CANON_FIELD_ORDER` dict construction with config loading
- Preserve `_canonical_field_order()` (domain-agnostic logic)
- Keep apostrophe normalization but delegate to DomainConfig.normalize_text()

**Usage:**
```bash
cnsf_canonicalize.py --check --domain ua domains/ua/anki/notes/lexemes/**/*.md
cnsf_canonicalize.py --write --domain de domains/de/anki/notes/lexemes/**/*.md
```

**Zero-impact rollout strategy:**
1. First commit: Load UA config alongside existing hardcoded logic (both active)
2. Verify output identical via regression tests (existing UA corpus)
3. Second commit: Remove hardcoded logic, rely entirely on config
4. Regression tests confirm zero drift

### 4. Refactored Import Scripts

Pattern-based implementation:

```python
class LexemeImporter:
    def __init__(self, domain: str, model_name: str, decks: Dict[str, str]):
        self.domain_config = DomainConfig(domain)
        self.model_name = model_name
        self.decks = decks
    
    def import_note(self, note: Dict) -> int:
        computed = {}
        
        # Only compute fields declared in domain config
        for field in self.domain_config.get_computed_fields(self.model_name):
            if field == '_AspectLabel':
                computed['_AspectLabel'] = self._compute_aspect_label(note)
            elif field == '_TypingSpec':
                computed['_TypingSpec'] = self._compute_typing_spec(note)
            # ...
        
        note['fields'].update(computed)
        
        # Apply domain-agnostic suspension policy
        should_suspend = self.domain_config.should_suspend(
            note.get('tags', []),
            [],  # flags
            note.get('fields', {})
        )
        
        return self._add_or_update_note(note, should_suspend)
```

**German overrides minimal logic:**
```python
class GermanLexemeImporter(LexemeImporter):
    def _compute_computed_fields(self, note):
        # German has no aspect-driven computed fields
        return {}
```

**Czech Alphabet is entirely separate:**
```python
class CzechAlphabetImporter:
    def __init__(self):
        self.domain_config = DomainConfig('cs')
        self.model_name = 'cs_alphabet'
    
    def import_note(self, note: Dict) -> int:
        # Audio file handling specific to Alphabet
        # Compute IPA variants if needed
        # Route to Alphabet deck
```

### 5. Makefile Parameterization

Use make functions to generate domain targets programmatically:

```makefile
define add_domain
  $(1)-lexeme-check:
      find $$($(1)_LEXEME_ROOT) -name "$(1)-lexeme-*.md" | \
        xargs python -m tools.anki.cnsf_canonicalize --check --domain $(1)
  
  $(1)-lexeme-fix:
      find $$($(1)_LEXEME_ROOT) -name "$(1)-lexeme-*.md" | \
        xargs python -m tools.anki.cnsf_canonicalize --write --domain $(1)
  
  _$(1)-lexeme:
      python -m tools.anki.sync.$(1)_lexeme_import $$($(1)_LEXEME_ROOT)
  
  $(1)-lexeme: $(1)-lexeme-check $(1)-lexeme-fix _$(1)-lexeme
endef

$(eval $(call add_domain,ua))
$(eval $(call add_domain,de))
$(eval $(call add_domain,cs))
$(eval $(call add_domain,sk))
```

**Each language only needs:**
- Domain config YAML
- Language-specific import script
- ROOT path constants

---

## Implementation Strategy for Lexeme and Alphabet

### Phase 1: Lexeme Refactoring (Weeks 1-2)

#### Week 1: Foundation
1. **Design and implement DomainConfig class** ✓ (completed this session)
2. **Create domain config YAML files** ✓ (ua.yaml, de.yaml completed)
3. **Refactor cnsf_canonicalize.py** (in progress):
   - Add `--domain` parameter
   - Load DomainConfig
   - Replace hardcoded field injection
   - Regression test on existing UA corpus
4. **Create de_lexeme_import.py** — German importer
5. **Create cs_lexeme_import.py** — Czech importer
6. **Update Makefile** with parameterized targets

#### Week 2: Validation
1. **Create unit tests:**
   - DomainConfig loading and field access
   - Canonicalize field ordering on German/Czech samples
   - Importer computed field logic
2. **Create German test data** — 10 phrases from master list, CNSF format
3. **Test German pipeline** — canonicalize → import → verify in Anki
4. **Test Czech Lexeme** — 10 phrases, richer schema, Compare cards
5. **Regression test Ukrainian** — full 584-note corpus, zero drift expected

#### Validation Checklist
- [ ] German lexemes parse without errors (10 test notes)
- [ ] Field order matches FIELDS constant (zero repositioning calls)
- [ ] Computed fields (if any) generated correctly
- [ ] Suspension policy applies correctly
- [ ] Compare cards generate when ConfusableSet populated
- [ ] Deck routing places German→English in Recognition, English→German in Production
- [ ] Apostrophe normalization handles U+02BC correctly
- [ ] Czech notes import with richer field set (no errors)
- [ ] Full UA regression test: zero changes to existing 584 notes

### Phase 2: Alphabet Note Type (Weeks 3-4)

#### Week 3: Czech Alphabet Design & Implementation
1. **Design cs_alphabet note type:**
   ```
   - Identity: NoteID
   - Core: Phoneme, IPA_Symbol, Vowel/Consonant classification
   - Audio: Audio_File (path/reference), Recorded_By
   - Examples: Example_Word, Example_Word_English, Sentence_Context
   - Metadata: Tags_Ch, Source_URL, Source_Note, Verification Notes
   ```
2. **Create cs_alphabet.yaml** domain config (new note type)
3. **Create CzechAlphabetImporter** class
4. **Design card templates:**
   - "Czech→IPA": Front = IPA symbol + description, Back = phoneme + audio
   - "IPA→Czech": Front = IPA symbol, Back = Czech example + audio
5. **Source audio for Czech phonemes:**
   - CzechClass101 or Forvo: native speaker recordings
   - Standardize to MP3
   - Store at `domains/cs/anki/media/phoneme-<ipa>.mp3`
   - Document source in Source_URL field

#### Week 4: Alphabet Validation
1. **Create 25-30 test Czech phoneme notes**
2. **Test audio sync mechanism** — files referenced correctly
3. **Verify IPA rendering** — no font issues
4. **Test card templates** — Czech→IPA and IPA→Czech display correctly
5. **Validate phoneme order** — linguistic/pedagogical sequence
6. **Validate example words** — common, easy to remember

#### Validation Checklist
- [ ] 30 Czech alphabet notes import successfully
- [ ] Audio files referenced and accessible to Anki
- [ ] Card templates render IPA symbols correctly
- [ ] "Czech→IPA" and "IPA→Czech" templates display correctly
- [ ] Phoneme order matches pedagogical sequence
- [ ] Example words are appropriate
- [ ] Suspension policy works for alphabet cards
- [ ] Deck routing places alphabet cards in `CS::Alphabet` deck

---

## Testing and Validation

### Unit Testing
- **test_domain_config.py:** Load config, verify field lists, check computed field declarations
- **test_cnsf_canonicalize.py:** Existing UA tests + new domain-agnostic tests for field injection and ordering
- **test_lexeme_importers.py:** German and Czech importers on 10-note samples
- **test_alphabet_importer.py:** Czech alphabet importer on 5-note sample with audio

### Integration Testing
- **End-to-end pipeline:** CNSF → canonicalize → import → Anki
- **Domain isolation:** German/Czech notes don't interfere with UA, don't corrupt existing
- **Deck routing:** Correct deck assignments per domain
- **Suspension policy:** Tag/flag combinations apply correctly across domains

### Regression Testing
- **Full UA re-sync:** All 584 lexeme notes, 87 verb notes, etc.
- **Zero expected changes** to already-canonical notes
- **Spot-check 10 random UA notes** in Anki browser for visual correctness

### Validation Testing
- **German:** Import 70 test notes, manually review 5 at random in Anki
- **Czech Lexeme:** Import 30 notes, check field set richness
- **Alphabet:** Import 25 phoneme notes, play audio, verify IPA rendering

### Edge Cases
- Empty fields (should not cause import errors)
- Unicode edge cases (U+02BC apostrophes, combining diacritics, Czech háček/čaron)
- Field ordering (verify reposition logic works on new domains)
- Computed fields (ensure never imported from CNSF)
- Comparison cards (German/Czech ConfusableSet + CompareA/B rendering)
- Audio file paths (relative/absolute, missing file handling)

---

## Immediate Next Steps

### Right Now (This Turn)
1. ✓ Create DomainConfig class
2. ✓ Create ua.yaml reference config
3. ✓ Create de.yaml minimal config
4. → **Next: Refactor cnsf_canonicalize.py** to load domain config and use --domain parameter
5. → **Next: Create de_lexeme_import.py** and cs_lexeme_import.py skeletons

### Session Priority Order
1. Finalize cnsf_canonicalize.py refactor + regression test on UA corpus
2. Create German importer + test on 10 German phrases
3. Create Czech importer + test on 10 Czech phrases
4. Update Makefile with parameterized targets
5. Create unit tests for new domain-aware code
6. Prepare German test data (70 phrases from master English list)
7. Prepare Czech Lexeme test data (30 phrases)
8. Create PR with refactored tooling (zero-impact on UA domain)

### Post-Implementation
1. Build 70-phrase master English list (locked across all languages)
2. Translate into German, Czech, Slovak
3. Source audio for Czech/Slovak alphabet cards
4. Create false friends clusters for Compare cards
5. Timeline alignment: German baseline week 1, Czech ready week 2-3

---

## Architecture Design Decisions

### Decision 1: Domain Configuration as YAML
**Rationale:** Declarative, version-controllable, loadable at runtime without code changes. Replaces hardcoded conditionals and imports.

### Decision 2: DomainConfig Class Pattern
**Rationale:** Single source of truth for domain metadata. Centralizes suspension policy, apostrophe normalization, and field schema access. Enables consistent behavior across all import scripts.

### Decision 3: Parameterized Import Scripts
**Rationale:** Eliminates code duplication for German/Czech/Slovak. Each language defines only what differs from the baseline (computed fields, sparse fields, etc.).

### Decision 4: Alphabet as Separate Note Type
**Rationale:** Czech Alphabet has fundamentally different field schema and card routing. Separate importer class avoids contaminating lexeme logic with phoneme-specific code.

### Decision 5: Zero-Impact Rollout Strategy
**Rationale:** Load new config alongside hardcoded logic first, regression test to confirm identical output, then remove hardcoded logic. Minimizes risk of breaking existing 584 Ukrainian notes.

### Decision 6: Makefile Parameterization via make Functions
**Rationale:** Eliminates repetitive Makefile entries for each domain. Single `add_domain` function generates all check/fix/sync targets. Easy to add Slovak/IPA later.

---

## Key Design Principles

### Principle 1: Single Source of Truth
Field ordering, field schema, and domain-specific logic live in domain config YAML, not in code. Code changes don't affect field definitions.

### Principle 2: Computed Fields are Declarative
Each note type declares its computed fields in config. Import scripts read this list and only compute declared fields.

### Principle 3: Suspension Policy is Domain-Agnostic
Tag/flag/content-based suspension logic is identical across all domains. Implemented once in DomainConfig.should_suspend(), reused everywhere.

### Principle 4: Incremental Implementation
Start with German (lowest complexity), validate on small corpus (10 phrases). Then Czech (medium complexity), then Slovak (medium-high, parallel work). IPA last (optional, standalone).

### Principle 5: Regression Testing is Non-Negotiable
Existing Ukrainian corpus is production data. Any refactoring must prove zero drift before merging. 584 lexeme notes are the regression test baseline.

---

## Files Created This Session

- `tools/anki/lib/domain_config.py` — DomainConfig class (171 lines)
- `tools/anki/config/domains/ua.yaml` — Ukrainian reference config
- `tools/anki/config/domains/de.yaml` — German minimal config
- `TOOLING-REFACTOR-SESSION-SUMMARY.md` — This document

## Next Session Deliverables

- Refactored `cnsf_canonicalize.py` with --domain parameter
- `tools/anki/sync/de_lexeme_import.py` — German importer
- `tools/anki/sync/cs_lexeme_import.py` — Czech importer
- Updated `Makefile` with parameterized domain targets
- Regression test results: UA corpus zero-drift confirmation
- Unit test suite for new domain-aware code
- PR ready for review

---

**End of Session Summary**

Session established the foundation for multi-language expansion. Domain configuration infrastructure is in place. Ready to proceed with cnsf_canonicalize.py refactor and German importer implementation.
