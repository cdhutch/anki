# Ukrainian Confusables Queue

Words anticipated to have confusable/homograph pairs. **Ground truth is the YAML tags list in the CNSF files.**

## Tagging Convention

When creating a note for a queued word, **MUST** add `confusables:anticipated` to the `tags:` list in the CNSF YAML frontmatter. This marks the note as one that needs confusable/homograph pairs added to its ConfusableSet field. The tag persists until ConfusableSet is populated, at which point it should be removed or replaced with `confusables:populated`.

Example YAML frontmatter:
```yaml
tags:
- domain:ua
- topic:vocabulary
- textbook:яблуко
- ch:2.X.X
- confusables:anticipated
```

---

## Queued Words

### виступ (performance/act/appearance)

**Status:** Not yet sourced  
**YAML tag to add:** `confusables:anticipated`

**English meanings:** presentation, performance, act, appearance, outburst

**Anticipated confusables:** Multiple UA words for different presentation contexts
- Performance/theatrical: театральна постава, виступ (performance)
- Public speaking: доповідь, виступ (presentation)
- Physical appearance: вигляд, виступ (outward appearance)
- Other senses likely exist per Горох

**When sourced:** 
1. Create note with `confusables:anticipated` tag in YAML frontmatter
2. Later populate ConfusableSet with scenario-based discrimination
3. Remove/replace tag once ConfusableSet is complete

**Added:** 2026-07-28 during ch-09 review  
**Note:** Exact confusable words TBD by user

---

### вогонь (fire)

**Status:** Anticipated (ua-lexeme-0329, ch-09)  
**YAML tag to add:** `confusables:anticipated`

**English meanings:** fire, flame, blaze

**Anticipated confusables:** Multiple UA words for different fire contexts
- Literal fire/flame: вогонь (fire as element/phenomenon)
- Bonfire/campfire: ватра (traditional bonfire)
- Conflagration: пожежа (destructive fire/conflagration)
- Light/glow: полум'я (flame/blaze)
- Other senses likely exist per Горох

**When sourced:**
1. Create note with `confusables:anticipated` tag in YAML frontmatter
2. Later populate ConfusableSet with scenario-based discrimination
3. Remove/replace tag once ConfusableSet is complete

**Added:** 2026-07-28 during ch-09 review  
**Note:** Exact confusable words and distinctions TBD by user
