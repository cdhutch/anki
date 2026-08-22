# Anki Expansion Plan — German, Czech, Slovak, IPA Domains

**Date**: 2026-08-22  
**Status**: Planning & tooling refactor (prerequisite)  
**Trip**: Czechia/Slovakia ~1 month away; Czech is 2× priority (more time in Czechia)

---

## Project Overview

Four new Anki domains to support trip preparation and continued language study:

- **German**: Phrase reactivation (A1/A2→A2+); ~70 phrases, no alphabet cards
- **Czech**: Full domain (phrases + alphabet + stress rules + false friends); ~70 phrases + phonetic cards
- **Slovak**: Full domain (phrases + alphabet + stress rules + false friends); ~70 phrases + phonetic cards
- **IPA**: Phonetic reference domain; maps IPA symbols to example words across all languages

**Shared resource**: All three languages translate the same **70-phrase master English list** (locked), ensuring parallel vocabulary and consistent card count.

---

## Master English Phrase List (Locked)

All three languages will be built from this source, translated independently.

### Categories (29 phrases across 8 topics):

1. **Greetings & politeness** (13): Hello, Good morning/afternoon/evening, Goodbye, Please, Thank you, You're welcome, Excuse me, I'm sorry, Yes, No, Mister, Missus
2. **Questions & needs** (8): What is this?, Where is the bathroom?, Do you speak English?, I don't understand, Can you help me?, How much?, What time?, Where am I?
3. **Food & drink** (14): I'm hungry/thirsty, Water/Coffee/Tea/Beer/Wine, Food, Bread/Cheese/Meat/Vegetables, Spicy/Not spicy, Allergic to
4. **Directions** (9): Train station, Hospital, Left/Right/Straight, Near/Far, North/South/East/West
5. **Emergencies** (7): Help, Police/Fire/Doctor/Hospital, I'm lost, Danger, Stop
6. **Accommodation** (7): Hotel, Room, Bed, Key, Check in/out, Cost per night
7. **Shopping & money** (8): Shop/Market, Price, Expensive/Cheap, Do you have?, I want, Cash/Card, How much?
8. **Miscellaneous** (5): Thank you very much, See you later, What's your name?, My name is, Nice to meet you

**Total**: ~70 phrases, consistent across all domains

---

## Domain Structure

```
domains/
  german/
    anki/
      notes/
        lexemes/
          phrases-*.md          # ~70 English↔German phrase cards
  czech/
    anki/
      notes/
        lexemes/
          phrases-*.md          # ~70 English↔Czech phrase cards
        alphabet/
          consonants.md
          vowels.md
        stress-rules/
          exceptions.md          # Czech is predictable (first syllable); reference only
  slovak/
    anki/
      notes/
        lexemes/
          phrases-*.md          # ~70 English↔Slovak phrase cards
        alphabet/
          consonants.md
          vowels.md
        stress-rules/
          exceptions.md          # Slovak has real exceptions; separate card subset
  ipa/
    anki/
      notes/
        lexemes/
          symbols-*.md          # IPA symbols mapped to language examples
```

---

## Card Format & Structure

### English-to-Language Phrases (German, Czech, Slovak)

**Front**: English phrase  
**Back**:
- Target language phrase (with articles for German nouns: der/die/das)
- IPA transcription (phonetic rendering)
- **Phonetic guide** (Czech/Slovak only): Ukrainian or Russian equivalent sound, stress position
- German: English/French analogues for unfamiliar sounds

**Note type**: Lexeme (reuse Ukrainian model template)  
**Tags**: `domain:`, `topic:`, `status:draft|verified`, `false_friend_vs:` (when applicable)

### Language-to-English (Recognition)

**Front**: Foreign language phrase  
**Back**: English translation

**Note type**: Lexeme (simpler variant)  
**Tags**: Same structure

### False Friends Field

**Optional field within lexeme cards** (no separate note type).

- **Field name**: `false_friend_note` or `confusable_with`
- **Tag scheme**: `false_friend_vs:russian`, `false_friend_vs:ukrainian`, `false_friend_vs:english`, `false_friend_vs:german`
- **Model**: Ukrainian homograph/homophone comparison cards (same approach)

**Examples to build**:
- Czech words deceptive to English speakers
- German words with Czech false friends (and vice versa)
- Slavic false friends (Czech↔Russian, Czech↔Ukrainian)

### Alphabet Cards (Czech, Slovak only)

**Front**: 
- Letter (consonant or vowel)
- IPA notation

**Back**:
- IPA in isolation
- Russian/Ukrainian phonetic anchor (pronunciation reference, not translation)
- Example words (from Forvo, CzechClass101, or local audio)
- Stress marks on all vowels (reinforcement)

**Note type**: Lexeme (custom template for phonetic cards)

---

## Linguistic Notes

### Czech

- **Stress**: Always first syllable (predictable, no exceptions)
- **Vowel reduction**: Some in unstressed syllables (less than Russian, more than Ukrainian)
- **Gender**: 3-gender system (m./f./n.); inferred from inflectional endings
- **Unique sounds**: **ř** (rolled r + fricative; no direct Russian/Ukrainian equivalent — use phonetic description)
- **Articles**: None (like Russian/Ukrainian)
- **Alphabet cards**: Full consonant + vowel set with stress-mark reinforcement

### Slovak

- **Stress**: Generally first syllable, **but has exceptions** → build separate stress-rules card subset
- **Vowel reduction**: Some in unstressed syllables (similar to Czech)
- **Gender**: 3-gender system; inferred from inflectional endings
- **Articles**: None (like Russian/Ukrainian)
- **Alphabet cards**: Full consonant + vowel set + stress-rules exceptions as separate cards

### German

- **User background**: A1/A2 level learned ~7 years ago; goal is phrase reactivation, not structural grammar
- **Articles**: **Always include** (der/die/das) — German nouns require gender markers
- **Unique sounds**: äu, eu diphthongs; use English/French analogues ("oy" sound)
- **IPA**: Include for reference; secondary to user's existing pronunciation intuition
- **Alphabet cards**: Skip (user already knows German pronunciation system)

---

## Audio Resources & Sourcing

### Czech
- **CzechClass101**: Extensive recordings of words/phrases
- **Forvo**: Crowdsourced native speaker pronunciations
- **IPA Handbook**: Phonetic reference and illustrations
- **Strategy**: Embed audio files into alphabet cards as sound examples per consonant/vowel

### Slovak
- **IPA Handbook**: Slovak illustrations with native speaker recordings
- **Forvo**: Crowdsourced pronunciations
- **University of Amsterdam Slovak phonetics**: Academic word lists
- **Strategy**: Same audio embedding approach as Czech

### German
- **Existing knowledge**: User already has intuition; minimal sourcing needed
- **Forvo**: Fallback for unusual words/phrases
- **Strategy**: No audio embedding required (user knows pronunciation)

---

## Critical: Tooling Refactor (Prerequisite for Scaling)

### Current Limitation

`cnsf_canonicalize.py` has **hardcoded Ukrainian assumptions**:
- Unconditionally injects `Verification Notes` field unless `note_type == "ua_verb"`
- Field defaults and validation logic assume Ukrainian-specific patterns
- Cannot scale to multi-language domains without refactoring

### Refactoring Approach

**Parameterize the YAML-to-Anki pipeline by domain**:

1. **`cnsf_canonicalize.py`**: Accept `--domain german|czech|slovak|ipa` CLI argument
   - Move Ukrainian field defaults into domain-specific config (e.g., `config/czech.yaml`)
   - Dynamically inject/validate only domain-relevant fields
   
2. **`cnsf_parse.py`**: Same parameterization for field parsing

3. **`Makefile`**: New targets
   - `make german`, `make czech`, `make slovak`, `make ipa`
   - Replace hardcoded `make ukrainian` with `make ua` alias
   - Each target runs domain-specific setup/sync logic

4. **Domain config files** (new):
   ```
   config/
     ua.yaml       # Ukrainian defaults (Verification Notes, etc.)
     czech.yaml    # Czech defaults
     slovak.yaml   # Slovak defaults
     german.yaml   # German defaults
     ipa.yaml      # IPA defaults
   ```

### Deliverable

Once refactored, adding 50–75 notes per language becomes trivial:
- Write YAML files in domain-specific folder
- Run `make czech` or `make german`
- Import to Anki

**No further code changes needed for each new domain.**

---

## Implementation Order (Critical for Timeline)

### Phase 1: Generalize Tooling (Prerequisite)
1. Refactor `cnsf_canonicalize.py` to accept `--domain` parameter
2. Refactor `cnsf_parse.py` to accept `--domain` parameter
3. Create domain config files (`config/czech.yaml`, etc.)
4. Update Makefile with new targets
5. **Test with German** (smallest, simplest case — no alphabet cards, no stress rules)

### Phase 2: Build German Phrase Deck (Quick Win)
- ~70 English↔German lexeme cards
- Include articles (der/die/das) with nouns
- Target: 3–5 days
- IPA optional; defer if time-constrained

### Phase 3: Build Czech Domain (Priority for Trip)
- ~70 English↔Czech lexeme cards
- Full alphabet cards (consonants + vowels with stress marks)
- False friends field where applicable
- Audio examples for alphabet cards
- Target: 1–2 weeks

### Phase 4: Build Slovak Domain (Secondary)
- ~70 English↔Slovak lexeme cards
- Alphabet cards + stress-rules subset
- False friends field
- Audio examples
- Target: 1–2 weeks

### Phase 5: IPA Domain (Optional, Time-Permitting)
- Lexeme cards mapping IPA symbols to example words (Czech/Slovak/German)
- Reinforces alphabet learning across languages
- Target: 1 week (if time allows)

---

## Trip Priorities (Timeline: ~1 month)

| Priority | Language | Focus | Timeline |
|----------|----------|-------|----------|
| **Critical** | Czech | Phrases + alphabet | Weeks 1–2 (after tooling refactor) |
| **High** | Czech | False friends awareness | Week 2–3 (integrated into phrase cards) |
| **Medium** | Slovak | Phrases + alphabet | Weeks 3–4 |
| **Low** | German | Phrase reactivation | Weeks 1–2 (parallel to Czech, simpler) |
| **Optional** | IPA | Cross-language phonetic reference | Week 4 (if time allows) |

---

## False Friends Strategy

### Integration Approach
- **Not a separate domain or note type** — optional field within lexeme cards
- **Field name**: `false_friend_note` (or `confusable_with`)
- **Tags**: `false_friend_vs:language` to specify which language creates confusion
- **Model**: Reuse Ukrainian homograph/homophone comparison card template (CompareA/CompareB/CompareScenario)

### Example Patterns to Build

**Czech ↔ Russian false friends**:
- Czech word that looks/sounds like Russian but means something different
- Example: Czech "sejít" (to go down) vs. Russian "сейчас" (right now)

**Czech ↔ English false friends**:
- English word deceptive in Czech context
- Example: Czech "prezident" (president) ≠ German/English "Präsident" stress/usage

**German ↔ Czech false friends**:
- Cognates that diverged in meaning
- Example: German "Gift" (poison) vs. English "gift" (present)

---

## Notes for Future Sessions

- This document bridges the mobile-app conversation (2026-08-22) to the desktop repo workflow
- **Tooling refactor is the critical blocker** — everything else depends on it
- Ukrainian lexeme model is the template; no new patterns needed, just parameterized reuse
- Trip departure is ~1 month; Czech is the bottleneck (2× time allocation, full domain)
- Ready to begin implementation once tooling refactor is complete

---

## Reference: File Structure Template

Once tooling is generalized, each new domain follows this pattern:

```
domains/<language>/
  anki/
    notes/
      lexemes/
        <category>-<number>.md
        ...
      [alphabet/]                    # Czech/Slovak only
        consonants.md
        vowels.md
      [stress-rules/]                # Slovak only
        exceptions.md
    docs/
      design.md                       # Language-specific design notes
      sourcing.md                     # Sourcing strategy, audio links
      false-friends.md               # False friends list and patterns
    config/
      [domain-specific config]       # Set by generalized tooling
```

Each `.md` file follows CNSF v0 format (YAML front matter + fields).
