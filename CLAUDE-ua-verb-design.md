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
## Verb Classification: Pugh & Press Conjugation Classes (2026-08-27)

**Status:** finalized classification scheme, established through direct review with Craig against
the live 87-note corpus in `domains/ua/anki/notes/verbs/`. **Not yet applied to the CNSF notes** --
the `class:` tag values below are pending Craig's sign-off on the note-by-note assignment before
they replace the ad hoc values currently in the corpus (`class:regular-1`, `class:prefixed`, etc. --
see the Tag Convention table above, which still reflects the *current* live values). This section
documents the target scheme and the full mapping for reference.

**Source:** class boundaries are Pugh & Press's *Ukrainian: A Comprehensive Grammar* Conjugation
I/II subclasses, adapted to the actual present-tense formation mechanism (rather than raw
infinitive spelling) and grounded against real conjugation data pulled from every note's
`Pres_1sg`/`Pres_3sg`/`Pres_3pl` fields. Conjugation (I vs II) is determined by the 3rd-person-plural
ending (`-уть`/`-ють` = I, `-ать`/`-ять` = II), not by infinitive shape, since infinitive spelling
can mislead (e.g. вируша́ти looks like it could take Conjugation II hushing treatment but is a plain
Conjugation I `-ати` vowel verb; бі́гти looks like a Conjugation I consonant stem but conjugates as
Conjugation II).

### Tag values

**Naming convention:** English grammar terms for the category, Cyrillic for any specific
spelling/ending being referenced (e.g. `consonant+ти`, `vowel+й`, `ояти`) -- consistent with the
domain's existing Cyrillic tag precedent (`pending-confusable:вигляд` on `UA_Lexeme`).

#### Conjugation I

| Class | Tag value | Corpus count |
|---|---|---|
| Vowel stem + /j/ | `class:conj1-vowel+й` | 47 |
| Consonant stem (plain) | `class:conj1-consonant+ти` | 5 |
| Consonant stem with mutation | `class:conj1-consonant-mutation` | 0 |
| -нути | `class:conj1-нути` | 1 |
| Irregulars | `class:conj1-irregular` | 13 |
| Бути | `class:conj1-бути` | 0 |

#### Conjugation II

| Class | Tag value | Corpus count |
|---|---|---|
| -ити | `class:conj2-ити` | 16 |
| -жати, -чати, -шати | `class:conj2-hushing+ати` | 1 |
| -іти | `class:conj2-іти` | 2 |
| -ояти | `class:conj2-ояти` | 0 |
| Consonant + -ти (бі́гти family) | `class:conj2-consonant+ти` | 2 |
| Irregulars | `class:conj2-irregular` | 0 |

**Design notes on specific classes:**

- **`conj1-vowel+й` absorbs five of Pugh & Press's original ten Conjugation I bullets** (`-ати`,
  `-яти`, `-іти`, `-ити`, `-ути`, `-авати`/`-явати`, `-увати`/`-ювати`) plus `мати`, because all of
  them share the same present-tense mechanism: the stem ends in a vowel and the present tense adds
  a glide `-й-` before the personal ending (spelled ю/є). The `-авати`/`-увати` family additionally
  deletes the `-ва-` formant before the glide is added (дава́ти → даю́) -- **except verbs built on
  the бу́ти/бува́ти root**, which keep `-ва-` throughout (прибува́ти → прибува́ю, not "прибую").
  `-ити` verbs are included only when they're genuinely this vowel-stem type (пи́ти, би́ти, ви́ти,
  ли́ти, уми́ти) -- most `-ити` verbs are Conjugation II and stay in `conj2-ити`.
- **`conj1-consonant-mutation`** is `-ати`/`-іти` verbs whose stem consonant mutates through the
  *entire* present paradigm, not just 1sg (писа́ти/пишу́, каза́ти/кажу́, рі́зати/рі́жу, хоті́ти/хочу́
  -- note хоті́ти is the concrete proof this pattern exists for `-іти`, not just `-ати`). No corpus
  member currently.
- **`conj1-consonant+ти`** and **`conj2-consonant+ти`** both cover the automatic к/г/х→ч/ж/ш
  alternation before a front-vowel ending (могти́, пекти́, лягти́ in Conjugation I) as a predictable
  phonological rule, not a distinguishing lexical property -- so it does *not* trigger
  `consonant-mutation` classification. **`conj2-consonant+ти` is a closed, single-root class**: per
  Pugh, бі́гти (and its prefixed family) is the *only* Conjugation II verb with a consonant-stem
  structure at all -- it is not a productive pattern, despite the naming parallelism with the
  Conjugation I tag.
- **`conj1-irregular`** covers suppletive/unpredictable stems, including the ї́хати family and the
  іти́/йти́/піти́ family (which insert a consonant -- д -- in the present rather than just a glide,
  so they don't qualify for `conj1-vowel+й` even though the infinitive ends in a vowel).

### Full corpus mapping (87/87 notes, 2026-08-27)

**Conjugation I**

- `conj1-vowel+й` (47): 0008 пла́вати, 0011 бі́гати, 0014 літа́ти, 0033 насоло́джуватися, 0034
  перемага́ти, 0035 поміча́ти, 0036 програва́ти, 0037 розмина́тися, 0038 би́тися, 0039 вболіва́ти,
  0040 виграва́ти, 0041 відбива́ти, 0042 забива́ти, 0043 завдава́ти, 0044 заробля́ти, 0045 ки́дати,
  0046 набира́ти, 0047 перекида́ти, 0048 посіда́ти, 0049 простяга́ти, 0052 ночува́ти, 0053
  переліта́ти, 0054 переплива́ти, 0055 переправля́тися, 0056 підніма́тися, 0057 дола́ти, 0058
  прива́блювати, 0059 розмі́щувати, 0060 спуска́тися, 0061 стартува́ти, 0062 фінішува́ти, 0063
  відправля́тися, 0064 прибува́ти, 0066 чу́ти, 0067 вибача́ти, 0068 повто́рювати, 0069
  перепро́шувати, 0070 заночува́ти, 0071 виклика́ти, 0072 вируша́ти, 0073 ма́ти, 0075 відрізня́тися,
  0076 стосува́тися, 0077 дотри́муватися, 0078 склада́тися, 0081 пірна́ти, 0083 вигляда́ти.
- `conj1-consonant+ти` (5): 0009 пливти́, 0010 попливти́, 0079 впа́сти, 0086 плисти́, 0087
  поплисти́.
- `conj1-consonant-mutation` (0): no corpus member.
- `conj1-нути` (1): 0085 па́хнути.
- `conj1-irregular` (13): 0002 іти́, 0003 йти, 0004 піти́, 0006 ї́хати, 0007 пої́хати, 0025
  приї́хати, 0026 ви́їхати, 0027 підʼї́хати, 0028 дої́хати, 0029 прої́хати, 0030 переї́хати, 0031
  заї́хати, 0032 відʼї́хати.
- `conj1-бути` (0): no corpus member.

**Conjugation II**

- `conj2-ити` (16): 0001 ходи́ти, 0005 ї́здити, 0017 прихо́дити, 0018 вихо́дити, 0019 підхо́дити,
  0020 дохо́дити, 0021 прохо́дити, 0022 перехо́дити, 0023 захо́дити, 0024 відхо́дити, 0050
  вила́зити, 0051 топи́ти, 0065 говори́ти, 0074 підво́зити, 0080 звари́тися, 0082 розво́дити.
- `conj2-hushing+ати` (1): 0084 звуча́ти.
- `conj2-іти` (2): 0015 леті́ти, 0016 полеті́ти.
- `conj2-ояти` (0): no corpus member.
- `conj2-consonant+ти` (2): 0012 бі́гти, 0013 побі́гти -- mutates г→ж through the *entire*
  paradigm (біжу́...біжа́ть), unlike Conjugation II's usual 1sg-only mutation pattern; treated as
  this closed class's own idiosyncrasy rather than a reason to split the class further.
- `conj2-irregular` (0): no corpus member.

**66 + 21 = 87 -- every corpus verb accounted for.**

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
