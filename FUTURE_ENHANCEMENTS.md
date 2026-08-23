# Future Enhancements

## Card Flags by Language Domain

Add visual flags representing the language on cards. When studying multi-language sets (CS, SK, DE, etc.), cards should display a language indicator (flag emoji or language code badge) to make it immediately clear which domain/language the card belongs to.

**Implementation:** Modify card templates to include a language badge/flag in the corner.

## IPA Phoneme Cards Enhancement

Expand IPA phoneme capabilities:
- **Other language phoneme examples**: Show how the phoneme is realized in other languages (e.g., English, German, etc.)
- **Audio files**: Embed audio pronunciation examples on cards
- **Large IPA symbols**: Increase IPA symbol display size on front of card for better recognition
- **Phonetic environment**: Show common phonetic contexts where the phoneme occurs

**Related fields to add:**
- `IPA_Audio_EN` - English pronunciation audio
- `IPA_Audio_Other` - Phoneme audio in other languages
- `IPA_Contexts` - Common phonetic environments
- `IPA_Symbol_Size` - CSS sizing for large display

## Configuration-Driven Card Styling

Move hardcoded CSS from templates into domain YAML configs. This allows per-domain styling without code changes.

**Example:**
```yaml
domains/cs.yaml:
  card_css:
    lemma_size: "28px"
    gloss_size: "22px"
    language_flag: "🇨🇿"
```

## Bidirectional Card Verification

Add tests to verify that all bidirectional card pairs (XX→EN, EN→XX) render correctly without front-side collisions.
