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

---

### молода (bride) / молодий-as-groom

**Status:** Not yet sourced -- молода ("bride") does not appear as a headword in either yabluko vocabulary list.  
**YAML tag to add:** `confusables:anticipated`

**English meanings:** bride (noun); also "young" (fem., the adjective-agreement form of молодий)

**Chapter attribution:** молода itself is never printed in either vocabulary list, so there's no chapter to cite for it directly. Its likely home is yabluko-l1 ch.4.3, a wedding-vocabulary chapter (весілля, взяти шлюб, наречений, одружитися, etc.) where молодий appears once, sitting directly beside наречений (groom/fiancé). Right now that occurrence is folded entirely into the existing "young" note (ua-lexeme-0429, whose Tags_Ch already includes ch:1.4.3) rather than split into a "groom" sense -- the same kind of split дорогий already got (ua-lexeme-0437 "expensive" / ua-lexeme-0580 "dear"). молода (bride) itself would still be an inferred word from its attested male counterpart, not a transcribed wordlist entry.

**Anticipated confusables:** молода (bride, noun) vs молодий (young, masc. adj., ua-lexeme-0429) vs a possible split-out молодий-as-groom sense (parallel to the дорогий split)

**When sourced:**
1. Decide whether молодий's ch.1.4.3 occurrence should be split into a "groom" sense note, parallel to дорогий's expensive/dear split
2. Decide whether молода (bride) is added as an unattested-but-implied companion, or left out since it never appears in print
3. Create note(s) with `confusables:anticipated` tag, then populate ConfusableSet

**Added:** 2026-09-01, from the legacy Anki cloze-mining report's new-homograph candidates  
**Note:** Chapter attribution and sourcing approach TBD by user

---

### слід (footprint/trace; also "one should...")

**Status:** Not yet sourced -- not found as a standalone headword in yabluko-l1-vocabulary.pdf, yabluko-l1-vstup-vocabulary.pdf, or yabluko-l1-verb-dictionary.pdf, nor in yabluko-l2-vocabulary.pdf (only appears embedded in the fixed compound "вуглецевий слід," carbon footprint, l2 ch.11.1). Craig recalls слід existing somewhere in Yabluko L1 and will search further (possibly the full student-book/workbook text rather than the vocabulary appendix).  
**YAML tag to add:** `confusables:anticipated`

**English meanings:** trace, footprint, mark (noun); "one should / one ought to" (modal predicate, невідмінювана словникова одиниця)

**Anticipated confusables:** слід (noun, trace/footprint) vs слід (modal predicate, "should") -- a pure-polysemy homograph, same spelling and stress, no shared etymology, like ра́к or вид already in the registry

**When sourced:**
1. Confirm chapter placement once Craig locates the source
2. Create note(s) with `confusables:anticipated` tag, then populate ConfusableSet
3. If only the compound "вуглецевий слід" is ever attested, decide whether that alone justifies sourcing bare слід as a standalone noun

**Added:** 2026-09-01, from the legacy Anki cloze-mining report's new-homograph candidates  
**Note:** Sourcing location TBD by user
