# Compare Card Field Mapping — UA_Lexeme

**Why this file exists:** the Compare card (`UA_Lexeme`'s 3rd template) serves two
genuinely different card designs off the same field set, switched by `_IsHomograph`.
The two designs put *different kinds of content* in `CompareA`/`CompareB` — sentences
in one, bare words in the other. Authoring a note without knowing which mode it's in
produces a card that renders but is wrong: an all-English front with nothing to
recognize (ua-lexeme-0181, found 2026-07-28), or the raw `ConfusableSet` paragraph
rendered as a fake answer chip (ua-lexeme-0305, found 2026-07-28, see "Failure modes"
below). This file is the field-by-field spec so that doesn't recur.

There are three shapes a `UA_Lexeme` note's disambiguation content can take. Pick one
per note *before* touching any of these fields.

---

## Shape 1 — Single UA word, multiple unrelated EN meanings (true homograph)

One Ukrainian spelling, split across **separate notes** (one per sense, own `NoteID`),
both tagged `homograph:true`. Example: мете́лик — ua-lexeme-0171 (butterfly) /
ua-lexeme-0181 (bow-tie). Also: вид — ua-lexeme-0182 (grammatical aspect) /
ua-lexeme-0143 (kind/type). Also: відправлення — ua-lexeme-0304 (departure) /
ua-lexeme-0380 (parcel).

| Field | Content type | Notes |
|---|---|---|
| `tags` | must include `homograph:true` on **both** sibling notes | drives `_IsHomograph` |
| `_IsHomograph` | **never hand-author** | computed by `ua_lexeme_import.py` from the `homograph:true` tag at sync time |
| `ConfusableSet` | English prose | explains the split, cross-references the sibling `NoteID` by number. Gates whether the Compare card renders at all (must be non-empty) |
| `CompareScenario` | the literal string `Which sense of <word> is being used?` | this is a caption, not a scenario — do not write a situational prompt here for homographs, the two sentences below carry the situation |
| `CompareA` | **a Ukrainian example sentence** disambiguating sense A by context | NOT English, NOT a bare word |
| `Homograph_SenseA` | English gloss for the sense `CompareA` demonstrates | this is where the English answer goes |
| `CompareB` | **a Ukrainian example sentence** disambiguating sense B by context | same rule as CompareA |
| `Homograph_SenseB` | English gloss for the sense `CompareB` demonstrates | |
| `Mnemonic_EN` | short English memory aid | shown on the back under both senses |

**Both sibling notes carry IDENTICAL `CompareA`/`Homograph_SenseA`/`CompareB`/
`Homograph_SenseB` values, in the same order** — the card is the same on both notes;
only which one is "this note's own sense" differs contextually. Copy the four fields
verbatim between siblings rather than re-deriving them per note.

**Front (Compare card, homograph mode):** "Which sense of X is being used?" + the two
Ukrainian sentences as options, no English visible until the flip.
**Back:** "Senses of {{Lemma}}:" + each sentence paired with its `Homograph_SenseX`.

---

## Shape 2 — Single EN gloss, multiple distinct UA words (confusables / near-synonyms)

Different Ukrainian spellings whose `EN_Gloss` values overlap enough to cause mix-ups.
Two or more **separate, unrelated-spelling** notes, NOT tagged `homograph:true`.
Examples: перемагати/перемогти (0177) vs вигравати/виграти (0212) — both loosely "win";
стартувати (0291) vs почина́ти (referenced by string only, no note); прибувати (0316)
vs приходити (referenced by string only); прибуття (0305) vs відправлення (0304).

| Field | Content type | Notes |
|---|---|---|
| `tags` | do **not** add `homograph:true` | different spellings, not one word |
| `_IsHomograph` | computed `""` (falsy) | routes the template to confusables mode automatically |
| `ConfusableSet` | English prose | explains the actual distinction (roles, register, object type — whatever the real difference is), cross-references the other note by `NoteID` if one exists |
| `CompareScenario` | an English situational prompt calibrated to elicit *this note's own word* | must not just restate `EN_Gloss` — for near-synonyms that leaks the answer outright (see добре/непогано/нормально/чудово in CLAUDE.md for why) |
| `CompareA` | **the stressed UA word itself** (a lemma, e.g. `прибува́ти`) | NOT a sentence, NOT English |
| `CompareB` (`/C`/`D`) | the other confusable word(s), same format as `CompareA` | 2–4 chips supported |
| `Homograph_SenseA`/`B` | **leave blank** | homograph-only fields, unused in this mode |
| `Mnemonic_EN` | short English memory aid | |

Each note in the cluster gets **its own `CompareScenario`** (tailored to elicit that
note's specific word) but the **same `CompareA`–`CompareD` chip set, in the same
order**, on every note in the cluster — see відбивати/забивати/завдавати/набирати
(0213–0218) for a 4-way example, or прибувати/відправлятися (0316/0315) for a 2-way
pair where each note's scenario points at its own answer.

**Front (Compare card, confusables mode):** "Choose the right word:" + English
scenario + the UA word chips (stressed lemma forms).
**Back:** the correct `Lemma` + `EN_Gloss` + `Mnemonic_EN`.

**If you don't hand-author `CompareA`/`CompareB`:** `ua_lexeme_import.py`'s
`compute_compare_options()` derives them automatically as `(Lemma, ConfusableSet-text)`
— this is a *legacy fallback* for notes that predate the CompareA/B redesign and is
almost never what you want for a new note (see Failure Mode 1 below). Always author
both by hand for new confusable clusters.

---

## Shape 3 — The Compare card mechanism itself ("which sense is being used")

Both shapes above render through the same template
(`COMPARISON_FRONT`/`COMPARISON_BACK` in `setup_ua_note_types.py`), gated and routed
by two fields:

- **Gate:** the Compare card only has real content when `ConfusableSet` is non-empty
  AND `CompareA` is non-empty. If `ConfusableSet` is populated but `CompareA` is
  blank, the front/back both render a red "should be suspended" warning instead.
- **Route:** `_IsHomograph` picks Shape 1's sentence-based layout vs Shape 2's
  word-chip layout. It is *always* computed from the `homograph:true` tag by the
  importer — never hand-author it.

`ConfusableSet` is also independently rendered as `cf. {{ConfusableSet}}` on the back
of the plain **UA→EN** card (not the Compare card) whenever it's populated — this
happens regardless of whether a Compare card exists for the note.

---

## Failure modes found 2026-07-28 (why this file exists)

**1. `ConfusableSet` populated, `CompareA`/`CompareB` left blank, note not tagged
`homograph:true` (ua-lexeme-0305).** Intent was "just show the `cf.` note on the back
of the UA→EN card, no Compare card needed." Actual result: `ua_lexeme_import.py`'s
`already_authored` check requires **both** `CompareA` and `CompareB` to be non-empty
before skipping the auto-derive step — leaving *either* one blank still triggers
`compute_compare_options()`, which stuffs the entire `ConfusableSet` prose paragraph
into `CompareA`. Because `CompareA` is then non-empty, the suspend-gate
(`suspend_compare_card = not confusable_set or not compare_a_content`) evaluates
false — **the card is not suspended** and the full discriminator paragraph renders
as a fake front-side answer chip. There is no supported way to populate
`ConfusableSet` (for the back-of-card `cf.` note) without also getting a live Compare
card — if you don't want one, you must still hand-author real `CompareA`/`CompareB`
content (turn it into a genuine Shape 2 card) rather than leaving them blank.

**2. `CompareA`/`CompareB` authored in the wrong content type for the note's mode
(ua-lexeme-0181).** Written before the dual-mode (`_IsHomograph`) redesign landed,
back when Compare cards for homographs held the two *English senses* as chips
(`CompareA: butterfly (insect)`, `CompareB: bow-tie (menswear accessory)`) rather than
Ukrainian sentences. The template was redesigned to Shape 1's current form (UA
sentences + `Homograph_SenseA`/`B`) but this note's data was never migrated, and its
sibling ua-lexeme-0171 already has the correct sentence-based content. Result: with
`_IsHomograph` true, the front takes the Shape 1 branch, but `CompareA`/`CompareB`
render as plain English text — the whole front is in English, nothing to recognize
in Ukrainian, "not a useful card" (Craig, 2026-07-28). Fix: copy the sibling's
already-correct `CompareScenario`/`CompareA`/`Homograph_SenseA`/`CompareB`/
`Homograph_SenseB` values over verbatim.

**Takeaway for future authoring:** before setting `ConfusableSet`, decide which Shape
the note is (1 or 2) and fill in *all* of that shape's required fields in the matching
content type in the same edit — never leave `ConfusableSet` populated on its own.
