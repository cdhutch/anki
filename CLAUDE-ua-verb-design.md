# UA_Verb Note Type Design — Conjugation Morphology

**Principle:** Separate verb conjugation (morphology) from lexeme vocabulary. One UA_Verb note serves multiple lexemes via tag linking, avoiding 1:1 coupling.

---

## Note Type Structure

### Fields (20 total)

**Identity & Classification:**
- `NoteID` — unique identifier (ua-verb-0001, ua-verb-0002, etc.)
- `Lemma` — infinitive form (ходити, їхати, писати, бути, etc.)
- `Aspect` — "imperfective" or "perfective"
- `VerbClass` — conjugation pattern (ходити-type, іти-type, писати-type, irregular, etc.)
- `FreqSource` — source/ranking (e.g., "501-book-p42", "corpus-rank-187", "class-leader", "ch:2.9")

**Present tense (6 pronouns):**
- `Pres_1sg` — я ходжу
- `Pres_2sg` — ти ходиш
- `Pres_3sg` — він/вона/воно ходить
- `Pres_1pl` — ми ходимо
- `Pres_2pl` — ви ходите
- `Pres_3pl` — вони ходять

**Imperatives (3 forms):**
- `Impr_2sg` — ходи (standard 2nd person singular)
- `Impr_2sg_Formal` — ходіть (formal/polite with ви)
- `Impr_2pl` — ходіть (2nd person plural)

**Past tense (3 genders; plural = feminine):**
- `Past_m` — він ходив
- `Past_f` — вона ходила
- `Past_n` — воно ходило

**Participles (2 fields):**
- `Participle_Adverbial` — past adverbial (робивши) — *required*; useful for reading comprehension
- `Participle_Passive` — passive (робле́ний, можливий) — *optional*; blank if non-standard or rare

**Metadata & Linking:**
- `Tags_Conj` — category tags (see Tag Convention below)
- `Source_Note` — free text: class name, frequency rank, etymology, irregular notes, etc.

---

## Linking Strategy: Tags, Not Foreign Keys

**Problem:** If UA_Lexeme references UA_Verb by NoteID, we create 1:1 coupling. But one verb class (e.g., ходити-pattern) serves many lexemes (ходити, походити, заходити, виходити, etc.).

**Solution:** Bidirectional tag linking
- **UA_Lexeme** `Tags_Ch` includes a linking tag: `conj:motion-walking-ходити`
- **UA_Verb** `Tags_Conj` includes matching tag: `conj:motion-walking-ходити`
- Anki tag search discovers related conjugations without code changes
- Many lexemes can reference one conjugation note

**Example:**
```
UA_Lexeme ua-lexeme-0114 (ви́йти):
  Tags_Ch: textbook:яблуко ch:2.9 conj:motion-walking-піти motion:walking

UA_Verb ua-verb-0042 (піти - pf):
  Tags_Conj: class:leader irregular motion:walking phase:2a ch:2.9 conj:drill conj:motion-walking-піти

→ Both tagged with `conj:motion-walking-піти`; students/tools discover connection via tag search
```

---

## Tag Convention

Use these tags in `Tags_Conj`:

| Tag | Meaning | Example |
|-----|---------|---------|
| `class:leader` | Conjugation class model (teaches the pattern) | `class:leader` |
| `irregular` | Suppletive or highly irregular stem | `irregular` |
| `motion:walking` | Motion verb (ходити, іти, походити, etc.) | `motion:walking` |
| `motion:vehicle` | Motion verb (їхати, їздити, поїхати, etc.) | `motion:vehicle` |
| `freq:high` | High-frequency verb (top 500 corpus) | `freq:high` |
| `phase:2a` | Authored in Phase 2a (class leaders + irregulars) | `phase:2a` |
| `phase:2b` | Authored in Phase 2b (high-freq regulars) | `phase:2b` |
| `ch:2.9` | Used in ch-09 curriculum (or other chapter) | `ch:2.9` |
| `conj:motion-walking-ходити` | Linking tag: all verbs following this pattern | (see Linking Strategy) |
| `conj:drill` | Unsuspended on import (active conjugation drill) | `conj:drill` |
| `conj:suspended` | Suspended on import (reference only) | `conj:suspended` |

---

## Card Templates

### Card 1: Recognition (Infinitive → Conjugation)
**Front:** Lemma + English gloss + aspect label

**Back:** Full conjugation table (HTML or tabular, with collapsible past/imperative sections)

### Card 2: Production (Gloss + Pronoun → Form)
**Front:** English gloss + prompt "What is the 3rd person plural present?" (randomized)

**Back:** Answer + full conjugation table (for reference)

---

## Phase 2a Scope: ~60–70 Class Leaders + Irregulars

### Class Model Leaders (~25 notes)

| Class | Verb (impf) | Verb (pf) | Note |
|-------|----------|----------|------|
| Motion (walking) | ходити | піти | Suppletion: shared past ходи́в/пішо́в |
| Motion (vehicle) | їхати | поїхати | Regular -а- paradigm |
| -а- regular | писати | написати | Dominant class |
| -а- regular (high freq) | читати | прочитати | Common |
| -и- regular | робити | зробити | High frequency |
| -и- regular | жити | пожити | High frequency |
| -и- regular (reflexive) | дивитись | подивитись | Reflexive -ся |
| -и- regular (high freq) | говорити | поговорити | Common |
| -и- regular | слухати | послухати | Common |
| -и- regular (consonant) | гуляти | погуляти | High frequency |
| -а- vowel-stem | казати | сказати | Irregular allomorphy (каж-) |
| Thematic consonant | класти | покласти | Stem alternation (-т- theme) |
| Thematic consonant | стояти | постояти | Irregular thematic |
| Mixed | хотіти | захотіти | Mixed stem (хот-/хоч-) |
| Mixed (high freq) | міти | — | Obsolete/dialectal, but in texts |
| (+ 10–15 more) | — | — | TBD based on frequency/pedagogy |

### Irregulars (~30–40 notes)

| Verb | Type | Note |
|------|------|------|
| бути | impf only | Most irregular; essential |
| дати | pf; давати (impf) | Suppletive |
| їсти | impf; з'їсти (pf) | Irregular |
| брати | impf; взяти (pf) | Suppletive |
| ставати | impf; стати (pf) | Suppletive |
| лежати | impf; лягти (pf) | Suppletive |
| сидіти | impf; сісти (pf) | Suppletive |
| (+ 23–33 more) | — | From *501 Ukrainian Verbs* + frequency |

---

## Ch-09 Motion Verbs: Interim Approach

### Lexeme → Verb Linking via Tags

**18 UA_Lexeme notes** (ua-lexeme-0114–0131) represent 9 prefix pairs:
- Walking motion: ходити, походити, заходити, виходити, перейходити (pf: піти + same prefixes)
- Vehicle motion: їхати, поїхати, заїхати, виїхати (pf: поїхати, etc.)

**Strategy:** Create 2 base UA_Verb notes for ch-09:
1. `ua-verb-motion-walking` (ходити, impf) — class leader
2. `ua-verb-motion-vehicle` (їхати, impf) — class leader

Tag all 18 lexemes: `conj:motion-walking-ходити` or `conj:motion-vehicle-їхати`

Tag verb notes: `class:leader`, `ch:2.9`, `phase:2a`, `motion:walking` or `motion:vehicle`, `conj:drill`

Students drilling the visual cards can optionally switch to conjugation drill for the base verbs (ходити, їхати) rather than drilling every prefix variant individually — patterns transfer.

---

## Participles: Policy

### Adverbial Past Participle (required)

Form: `-л-` stem + `-и` → робивши́, писавши́, etc.

**Usage:** High-value for reading comprehension (present in literary texts)

**Policy:** Include for all verbs. If irregular or rare, note in `Source_Note`.

### Passive Participle (optional)

Forms vary by verb class and aspect:
- Regular -а- verbs → -ний (писаний, not common in -ний form; often -ний only for adjectives)
- Regular -и- verbs → -ний (зроблений, can/́ний)
- Irregulars → highly variable (можливий, взятий, etc.)

**Usage:** Moderate value; passive voice is less frequent than active in Ukrainian speech/text

**Policy:** Include if standard/common (зроблений, написаний, взятий). Leave blank if rare or non-standard or if only adjectival form exists.

**Alternative:** If passive participle is rare, store the adjectival form instead (e.g., можливий for мо́ч/мо́жна). Document in `Source_Note`.

---

## Implementation Sequence

1. **Define** UA_Verb note type in `setup_ua_note_types.py`
   - Add card templates (HTML conjugation table)
   - Add fields (listed above)
   - CSS for table layout

2. **Author/Import Phase 2a** (~60–70 notes)
   - Extract/author class leaders + irregulars
   - Tag with `phase:2a`, `class:leader` or `irregular`, category tags
   - Tag unsuspended cards with `conj:drill`
   - Batch import via `ua_verb_import.py`

3. **Link ch-09 lexemes**
   - Tag all 18 ch-09 lexemes with `conj:motion-walking-ходити` or `conj:motion-vehicle-їхати`
   - Create 2 base verb notes (ходити, їхати) with matching tags
   - Tag with `ch:2.9`, `class:leader`, `conj:drill`

4. **Import ch-09 pipeline**
   - Lexemes: `make ua-batch BATCH=yabluko-l2/ch-09`
   - Grammar: `make ua-grammar`
   - Visual: `make ua-visual`

5. **Phase 2b/2c** (future)
   - Expand UA_Verb with high-frequency regulars
   - Update tag system as new patterns emerge
   - Maintain UA_Verb as the canonical morphology reference

---

## Notes

- **No synthetic linking fields.** We use tags to avoid polluting note schema. Tags are flexible and queryable in Anki.
- **Prefixed verbs handled via pattern reference.** ви́йти and входи́ти both link to `conj:motion-walking-піти` (or `conj:motion-walking-ходити` for impf pairs); they don't need separate conjugation notes.
- **Suspended by default, drill opt-in.** Import all with `conj:suspended`; unsuspend selectively via tag `conj:drill` or manual review.
- **Participles are contextual.** Adverbial past is required (for reading); passive is optional (for writing, less common).
