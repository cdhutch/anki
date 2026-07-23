# CLAUDE.md — Anki Project Context (B737 + Ukrainian)

**Current work**: UA domain -- Ch-09 motion-verb polish punch list (7/7 items) complete as of
2026-07-22; push + PR to main pending Craig's go-ahead. B737 Phase A distractor authoring
paused (26/29 systems verified).

See **[CLAUDE-active-status.md](CLAUDE-active-status.md)** for queue and last session.

## Workflow Notes

This repo builds and maintains Anki flashcard decks across three top-level decks:

- **B737** (`domains/b737/`) — type rating study. CNSF markdown notes exported
  to TSV and imported via AnkiConnect. High-stakes professional content.
- **UA** (`domains/ua/`) — formal language learning (Galician/Lviv
  register, Яблуко textbook). Active branch `feature/ua-domain`.
  See `domains/ua/anki/docs/design.md` for full schema and migration plan.
- **Legacy** — archive of older decks. Being systematically migrated or archived.

**FSRS Isolation:** Each top-level deck has completely separate FSRS configuration 
and card history. Cards in B737 do not influence UA scheduling and vice versa.
See [CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md) for parameters.

### The Big 3 Rules (recite verbatim at session start if asked)

1. **Only Craig runs git commands, which Claude provides.** Claude never executes `git`
   itself -- including read-only commands like `status`/`diff`/`log`, even for quick
   investigation. Claude writes the exact command(s); Craig runs them and pastes back the
   output. (A violation on 2026-07-22 -- Claude ran `git status`/`git diff` directly via
   `device_bash` -- left a stale `.git/index.lock` that blocked Craig's own git commands
   until he manually removed it. See CLAUDE-known-issues.md.)
2. **Only Craig deletes files on his computer.** Claude does not delete files via any
   mechanism, even where technically possible. (In practice `device_bash` can't delete
   anyway -- `rm`/`rmdir`/`unlink` fail with "Operation not permitted," only `mv` works --
   but the rule holds regardless of mechanism.)
3. **After each set of commands, Claude waits for Craig to respond before providing
   additional commands.** No stacking multiple rounds of git/shell commands speculatively
   ahead of confirmation.

These extend to `make`, Python scripts that touch AnkiConnect, and any other shell command
in this repo -- all run by Craig, not Claude:

- **Shell commands are run by Craig**, not Claude. Claude provides commands to copy/paste; it does not execute git, make, or Python commands directly. (Claude's sandbox lacks access to the required conda env and git hooks will fail.)
- **Pull requests**: Claude provides the `gh pr create` command; Craig runs it and completes the PR on the GitHub website.

## Reference Files

| Topic | File |
|-------|------|
| **SV field spec** | [CLAUDE-sv-field-conventions.md](CLAUDE-sv-field-conventions.md) |
| **Deck architecture** | [CLAUDE-deck-architecture.md](CLAUDE-deck-architecture.md) |
| **Known issues** | [CLAUDE-known-issues.md](CLAUDE-known-issues.md) |
| **Key paths** | [CLAUDE-key-paths.md](CLAUDE-key-paths.md) |
| **Migration progress** | [CLAUDE-migration-log.md](CLAUDE-migration-log.md) |
| **UA_Verb design** | [CLAUDE-ua-verb-design.md](CLAUDE-ua-verb-design.md) |
| **FSRS deck configs** | [CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md) |
| **Flag audit workflow** | [CLAUDE-flag-audit.md](CLAUDE-flag-audit.md) |
| **Ch-09 vocabulary sourcing workflow** | [CLAUDE-ch09-vocab-workflow.md](CLAUDE-ch09-vocab-workflow.md) |
| **Approved web sources** | [CLAUDE-approved-web-sources.md](CLAUDE-approved-web-sources.md) |

---

## Ukrainian Domain (`domains/ua/`)

**Branch:** `feature/ua-domain` (based off `main`)

**Status (as of 2026-07-22):** Вступ (ch-00) complete — 113 notes live, stress verified, examples added.
Book 2 Ch. 9 (`feature/ua-verb-phase2a` branch) imported and polished — 7-item punch list
complete:
  - **18 UA_Lexeme notes** (ua-lexeme-0114–0131, prefixed walking + vehicle motion verbs)
    imported via `make ua-batch BATCH=yabluko-l2/ch-09`. `status:verified`; both UA→EN and
    EN→UA cards active (36 cards). `Compare` card template active for confusable pairs
    (про-/пере- pairs 0120/0121, 0129/0130, plus 0059 from ch-00) via `ConfusableSet` +
    new `Mnemonic_EN`/`CompareA`/`CompareB` fields (see Comparison card section below).
  - **UA_Grammar**: rebuilt from scratch as a real Cloze model (the live model had been a
    stale non-cloze legacy model — see CLAUDE-known-issues.md footgun #5). 9 notes
    (ua-grammar-0001–0009), all `status:draft`/suspended. 0008 (до/в–у/на destination
    prepositions) and 0009 (від/з–із–зі source/departure prepositions) are new, atomically
    clozed and leak-checked — see Cloze design principles below. 0001–0007 still use the
    older "busy" multi-fact-per-cloze pattern and have empty `Source_URL`/`Source_Note`;
    not yet revisited.
  - **UA_Visual**: redesigned from 2 templates (Spatial→UA / UA→Spatial) to a single
    "Prefix + Government" card (front = diagram + blank table, back = same table filled in
    place). 9 notes, 9 cards, `status:verified`, active in `UA::Recognition::Visual`.
  - **UA_PVOM_Infinitive**: reworked from 22 single-form notes to 11 notes × 4 card
    templates (Walking Multi/Uni, Vehicle Multi/Uni) — 44 cards total, each base form
    independently suspendable/leech-trackable.
  - All lexeme + grammar stresses Горох-verified. `Verb_Conj_Table` fully populated for
    all 18 verb pairs (0114–0131).

**UA_Visual card template design (2026-07-10):**
  - Card 1 (Spatial→UA): front = diagram + English meaning; back = Ukrainian prefix, government, verb pairs, example.
  - Card 2 (UA→Spatial): front = Ukrainian prefix + verb pairs; back = diagram + English meaning + government + example.
  - Template redesign fixed & deployed ✅ — `setup_ua_note_types.py` now calls `updateModelTemplates` with all templates in single call (not per-template loop).
  - Templates update correctly via `make ua-setup-visual`.

**Pending / Next planned work (as of 2026-07-23):**
  0. **TOP PRIORITY (set by Craig 2026-07-23):** Integrate the dedup/homograph-check logic
     directly into the vocabulary-generation workflow, not just the standalone
     `check_lexeme_dedup.py` tool. Today that tool has to be run manually before drafting a
     batch; the goal is to wire the same check into the per-subchapter generator scripts
     (the `gen_ch09_*.py`-style scripts used to draft each batch) so every candidate word is
     checked against the corpus automatically before a new note is created, and the
     new/homograph/duplicate outcome (see "Vocabulary dedup & homograph handling" above) is
     handled inline as part of generation rather than as a separate manual step run after
     the fact. Do this before continuing further ch.9.3+ sourcing.
  1. Continue sourcing and importing UA vocabulary from Yabluko L2 Chapter 9 — subsections
     9.3 onward. (9.1 sourced, reviewed, verified, and synced. 9.2 sourced, drafted,
     canonicalized, and synced as `status:draft` — 18 lexemes ua-lexeme-0163–0180 + 5
     conjugation notes ua-verb-0033–0037.) Keep following the 5 established sourcing rules
     (Горох verification, verb pairing, phrase+component creation, autonomy, draft-until-
     reviewed status).
  2. Craig reviews/validates the ch.9.2 batch and flips `status:draft` → `status:verified`
     once satisfied, same process used for ch.9.1. Re-sync afterward with `make ua-lexeme`
     / `make ua-verb`, or the new `make ua` aggregate target (canonicalizes + syncs every
     UA note type in one pass — see Reference Files).
  3. Get the Solarized light/dark palette correct and consistent across both Anki domains
     (B737 and Ukrainian). Concrete bug found 2026-07-23: `UA_Visual`'s CSS uses the
     `.night_mode` (snake_case) selector instead of `.nightMode` (camelCase) — confirmed via
     AnkiMobile's own docs that both desktop Anki and AnkiMobile key off `.nightMode`, so
     `UA_Visual`'s dark-mode rules are currently dead on every platform, not just iOS. Most
     other note types already carry Solarized CSS via `tools/anki/setup/update_legacy_css.py`
     (7 legacy models: B737_SV_Cloze, B737_Systems, UA_Conjugation, UA_Grammar, UA_Lexeme,
     UA_Lexeme_Legacy, UA_Verb) plus the individual `setup_*_model.py` scripts. Still need to
     audit `B737_Checklist`, `B737_Mnemonic`, `B737_Structured`, `B737_SV_MCQ`, `B737_SV_TF`
     for Solarized coverage and confirm none share the night-mode selector bug. See
     `.claude/memory/b737-anki-solarized-theme.md` for the original project tracking note.
     Craig wants this kept CSS-only — do not touch B737 note-type structure/fields.

### Current Anki state
- 3,932 existing Ukrainian notes in vanilla Basic / Basic+reversed / Cloze types
- 788 leeches (20%) — triage before bulk migration
- Active deck hierarchy: `UA::Recognition::*` / `UA::Production::*`
- New canonical decks: `UA::Recognition::UA→EN` / `UA::Production::EN→UA`
- Legacy decks: `Ukrainian Active::Яблуко`, `Inactive::Ukrainian Inactive::*`
- Tags in use: `textbook:яблуко`, `ch:2.8.x` (= Level 2, Ch. 8, §x), `leech`, `converted`, `to_convert`

### Primary note type: `UA_Lexeme`

**Fields (20, in semantic order):**

*Identity & Metadata:* `NoteID`

*Core Lemma & Morphology:* `Lemma`, `PartOfSpeech`, `Gender`

*Aspect (verbs only):* `Perfective` (PFV counterpart), `ImperfectiveUnidirectional` (motion verb directional form)

*Semantic Content:* `EN_Gloss`

*Grammatical Properties:* `Govt_Case`, `IrregularForms`, `CounterpartForm` (gender pairs), `VerbMotion_Pair` (base unprefixed form)

*Semantic Relations:* `ConfusableSet`, `CrossLang_Analog`, `EuphonyNote` (alternate spellings: уже/вже, всі/усі)

*Typing & Examples:* `TypingAnswer` (Lemma without stress marks), `UA_Example`, `EN_Example`

*Metadata & Sources:* `Tags_Ch`, `Source_URL`, `Source_Note`

**Aspect convention:** Lemma is always imperfective (base form). Perfective field contains PFV counterpart. Aspect is implicit in field structure (no explicit Aspect field needed).

**Verb conjugations:** `Verb_Conj_Table` field is being phased out of UA_Lexeme — blanked corpus-wide 2026-07-22 (all ~180 lexeme notes), but the field itself has not yet been removed from the schema/model. Full removal is planned but not yet executed — see "Verb_Conj_Table Removal Plan (Future)" below. Conjugation morphology belongs in the UA_Verb note type as structured fields, one note per lemma's own aspect, linked to the lexeme via matching Lemma text.

### Verb_Conj_Table Removal Plan (Future)

**Status:** Planned, not yet executed. Decided 2026-07-22 after clearing all *content* from the
field on the 18 pre-existing verb lexemes (`ua-lexeme-0114`–`0131`) and the 5 new ch.9.2 verb
lexemes (`ua-lexeme-0176`–`0180`) — this plan covers removing the *field itself* from the
schema/model, corpus-wide.

**Correction of prior doc drift:** this file previously claimed (above) that `Verb_Conj_Table`
had already been removed from `UA_Lexeme` — that was aspirational/incorrect. The field is still
live in the Anki model and present (currently blank) in all ~180 lexeme `.md` files.

**Rationale:** repo-wide grep confirms no card template anywhere references `{{Verb_Conj_Table}}`
— the field has never been rendered on any card, in any note-type version. It's genuinely dead
data, not just duplicated-but-harmless. Conjugation data belongs on the dedicated `UA_Verb` notes
(structured `Pres_*`/`Imperative_*`/`Past_*` fields).

**Known complication:** `tools/anki/setup/setup_ua_note_types.py`'s `FIELDS` list — the nominal
source of truth for the model definition — does *not* currently include `Verb_Conj_Table`, nor
`Verification Notes`, `Mnemonic_EN`, `CompareA`, or `CompareB`, all of which real notes have. That
script is stale relative to the live Anki model — **don't trust it as ground truth** for this
migration. Before touching the live model, run `tools/anki/inspect/inspect_ua_lexeme_fields.py` to
get the actual field list/order straight from AnkiConnect.

**Migration steps:**

1. **Verify live state** (read-only): run `inspect_ua_lexeme_fields.py` to confirm
   `Verb_Conj_Table`'s exact position in the real model and note any other drift from
   `setup_ua_note_types.py`.
2. **Back up the Anki collection** before any schema mutation (File → Export, or Anki's own
   backup) — `modelFieldRemove` is destructive and not easily undone.
3. **Strip the field from all CNSF source files**: delete the `Verb_Conj_Table` key from the
   `fields:` dict in all ~180 `ua_lexeme` `.md` files (`yabluko-l1/` and `yabluko-l2/`), then run
   `python -m tools.anki.cnsf_canonicalize --write` across the whole lexeme corpus. Commit this
   on its own.
4. **Update tooling that references the field:**
   - `tools/anki/extract/mappings/UA_Lexeme.yml` — remove the `f__Verb_Conj_Table` entry.
   - `tools/anki/generate/ua_generate_examples.py` (~line 176) — remove `"Verb_Conj_Table"` from
     its field-order list.
   - `tests/ua/test_verify_stress_goroh.py` (4 fixture occurrences) and
     `tests/ua/test_backfill_source_url.py` (1 occurrence) — hardcode `Verb_Conj_Table: ''` in
     sample note fixtures; update or the tests may fail once real notes stop carrying the key.
     Run the full `tests/ua/` suite after.
   - `tools/anki/extract/gen_ua_lexemes_l2_ch09.py` / `gen_ua_lexemes_vstup.py` are historical
     one-off generation scripts (already run, not part of the live pipeline) — optional cleanup
     only, low priority.
   - `tools/anki/inspect/patch_ch09_conj_tables.py` / `patch_ch09_stress.py` are historical patch
     scripts, already executed — leave as-is, historical record.
5. **Remove the field from the live Anki model**: AnkiConnect `modelFieldRemove` on `UA_Lexeme`
   for `Verb_Conj_Table`. Craig runs this himself (same pattern as all sync/import scripts) —
   probably worth a tiny one-off script that prints the field list before and after, rather than
   a raw API call.
6. **Verify:** re-run `inspect_ua_lexeme_fields.py` to confirm removal; re-run
   `cnsf_canonicalize --check` across the corpus; run `tests/ua/`; spot-check a few `UA_Lexeme`
   cards in the Anki browser (expect zero visual change, since nothing ever rendered this field).

**Not blocking:** the field is already blank everywhere as of 2026-07-22, so there's no urgency —
this is a cleanup, not a bug fix.

### Card Template Techniques

**Polysemous word examples (multiple meanings)**

When a UA word has multiple distinct meanings, demonstrate semantic range in the example fields:

```yaml
UA_Example: |
  Example showing meaning 1
  Example showing meaning 2
EN_Example: |
  Translation for meaning 1
  Translation for meaning 2
```

Example: вік (age as measure of time; era/epoch as historical period)
```
UA_Example: У якому віці діти йдуть до школи? | Вони жили в добу Середніх віків.
EN_Example: At what age do children go to school? | They lived during the Middle Ages.
```

This shows the learner that the same Ukrainian word spans multiple semantic domains.

**Comparison card (scenario-based confusable discrimination)**

UA_Lexeme generates a 3rd optional "Compare" card template when `ConfusableSet` is populated:

- **Front:** Scenario/context requiring semantic discrimination (not pattern recognition)
- **Back:** Correct word + explanation of why it fits this specific context
- **Design principle:** Scenario-based + bidirectional (forces understanding of *when* each word fits, not just *that* one is correct)
- **Avoids memorization trap:** Multiple scenarios with different contexts prevent learner from simply memorizing "gloss → word"

**ConfusableSet format** (structured for scenario generation):
```yaml
ConfusableSet: |
  фах (alternative word + brief definition)
  Scenario A: Context where lemma fits
  → Use: lemma (when/why)
  Scenario B: Context where confusable fits
  → Use: confusable (when/why)
  Key distinction: Explicit semantic/contextual difference
```

Example: професія vs. фах
- Scenario A: "Asking someone about their job formally" → професія (formal career identity)
- Scenario B: "Discussing a plumber's expertise" → фах (skilled trade/craft)

The "Compare" card only renders when `ConfusableSet` is populated, making it lightweight.

**PVOM prefix drilling (multi-form typing cards)**

`UA_PVOM_Infinitive` (one note per prefix, `domains/ua/anki/notes/pvom/`) drills all four
verb-of-motion base forms a prefix combines with, as four separate card templates rather
than one card with four blanks:

- **Walking (Multi)** — multidirectional, imperfective (ходити-family)
- **Walking (Uni)** — unidirectional, perfective (іти-family)
- **Vehicle (Multi)** — multidirectional, imperfective; labeled "їздити" on the card, but
  the typed answer is the dictionary-primary **-їжджати** surface form (Горох consistently
  redirects "-їздити" entries to "-їжджати" as the canonical headword — both are real, but
  -їжджати is the one attested as primary)
- **Vehicle (Uni)** — unidirectional, perfective (їхати-family)

**Why four separate templates, not one card:** each base form gets independent FSRS
scheduling and leech tracking. The four forms are not equally hard — mutations
(apostrophe insertion: підʼїхати, відʼїхати, надʼїхати, обʼїхати, зʼїхати; epenthetic
-ій-: підійти, відійти, надійти, обійти, зійти; з→с assimilation before voiceless х:
з- + ходити → сходити, not "зходити") make some prefixes much harder to produce than
others, and a student can be solid on the walking forms while still missing vehicle
forms. Separate templates let each be suspended/re-weighted independently without
touching the others.

**Card design — no hints on the front.** Front is just `{{Prefix}} + <base label>` (e.g.
"ви + іти", "під + їздити") — no aspect labels, no mutation hints. The point is for the
student to internalize the prefixation patterns through repeated production, not to be
told the answer's shape in advance.

**Field pattern:** each base has a stressed field (`*_UA`) and an unstressed field
(`*_Typing`) used for Anki's `{{type:...}}` comparison; the back-side script compares the
typed answer against both to give tiered feedback (perfect-with-stress / correct-no-stress
/ incorrect), same pattern as `UA_Lexeme`'s typing cards.

**Verification caveat:** the з- prefix (схо́дити/зійти́) is the one form in this set where
Горох's dictionary entry doesn't cleanly label the aspectual pair the way it does for the
other ten prefixes — its primary listed sense is "ascend," not explicitly "get off/descend."
Treat it as slightly lower-confidence than the rest until cross-checked against the
textbook.

**Cloze note design principles (UA_Grammar, established 2026-07-22)**

- **Atomicity:** each distinct cloze number (`{{c1::}}`, `{{c2::}}`, ...) should test exactly
  one isolated fact. Reusing the same cloze number for multiple unrelated facts in one note
  (the pattern in `ua-grammar-0001`–`0007`) makes a single card "busy" — it forces recall of
  several things at once instead of one clean fact.
- **No self-leak:** nothing outside a cloze span may name the answer being tested inside that
  span. Concrete examples belong in `Extra` (back-side only), not in `Text` next to the
  cloze — a parenthetical like "(зайти до друга)" sitting outside a
  `{{c1::до + genitive}}` span gives the answer away on the very card testing it.
- **No cross-cloze substring leak:** one cloze's answer text must not be a literal substring
  of another cloze's visible answer text on the same note (e.g. "зі" as its own cloze target
  when "з/із/зі" is also shown plainly elsewhere on the card).
- **Don't pad to hit a card-count target.** Atomicity means one card per fact that earns
  independent recall, not maximizing cloze numbers — see `ua-grammar-0009`, trimmed from an
  initial 4-fact draft down to 2 after the extra facts turned out to be low-value trivia.
- **Cloze cards aren't retroactively deleted when a `{{cN::}}` tag is removed from Text.**
  If a stale extra card persists after trimming a note's cloze count, delete the note in
  Anki and let the next sync recreate it with the correct card count — this is expected
  Anki behavior, not a bug to chase.

### Language conventions (critical)
- Dialect: modern Ukrainian, **Galician/Lviv** register
- Apostrophe: **U+02BC `ʼ`** — never ASCII `'`
- Stress marks: **never guess** — verify against Горох (goroh.pp.ua) via Claude in Chrome.
  Tag unverified with `stress:unverified`. Remove tag only after Горох confirms.
- Stress disambiguation: some words have stress-dependent meanings (e.g. му́зика = music,
  музи́ка = musician). Always check before "correcting" based on Горох alone.
- **Two accent marks on one word is valid Горох output** — it means the word has free/variant
  stress (either syllable may be stressed). Do NOT treat this as an extraction bug or garbled
  data; do NOT collapse it to a single mark when transcribing. Record both marks in the Lemma
  field as Горох shows them.
- **Data-quality priority: a multisyllable word with ZERO stress marks is a stronger red flag
  than one with two.** Double-stress is a legitimate linguistic outcome (see above); a missing
  stress mark on a multisyllable lemma is not — that's the pattern that indicates a real
  extraction bug (wrong homograph block, failed fetch, stripped markup) and should block on
  re-verification before the note is trusted.
- `сь` after vowels preferred (дивлюсь, вчусь) — preserve unless correcting
- Grammar explanations always in English

### Stress verification workflow (established)

Горох Словозміна (`goroh.pp.ua/Словозміна/<word>`) returns the full inflection paradigm
with stress marks. Accessible via Claude in Chrome (not via web_fetch — blocked).

Batch verification process:
1. Extract lemmas from notes (Python, strip stress to get bare form)
2. Fetch Горох pages in batch via Chrome JS `Promise.all` (30 at a time to avoid truncation)
3. Strip phonetic markers from Горох output: remove `<sup>...</sup>` WITH content,
   backtick, apostrophe, colons, `{дз}`/`{дж}` → keep content, `ў` stays as non-vowel
4. Compare vowel-index of stress in lemma vs Горох form; flag mismatches
5. Apply corrections; keep `stress:unverified` tag until user confirms

Important: Горох returns the **masculine adjective** form for adjectives (e.g. `-ський`
instead of `-ська`). The vowel-index comparison handles this correctly since the stressed
syllable is the same. The script is embedded in session context — rebuild from the pattern
in `tools/anki/inspect/` when needed as a standalone tool.

### Vocabulary dedup & homograph handling (established 2026-07-23)

As chapter-by-chapter sourcing continues, every new candidate word falls into one of three
buckets. Triage deliberately — do not assume from spelling alone.

1. **Brand new vocabulary.** No existing note has this spelling. Default behavior: Горох-
   verify, create a new `ua-lexeme-NNNN` note per the standard process.

2. **Homograph — same spelling, unrelated meaning** (e.g. EN "blue" the color vs "blue" the
   mood; ГА "коса" braid / scythe / spit-of-land). Горох itself already surfaces this as
   separate `.article-block` entries under distinct H2 labels on the same Словозміна page —
   this is the same multi-homograph-page pattern the "біг"/"Бог" extraction bug taught us to
   handle correctly (match the H2 label text, don't grab the first table). Handling:
     - Create a normal new note (own NoteID/file) — do not merge into the existing one.
     - Cross-link both notes via `ConfusableSet`, explicitly stating "homograph — unrelated
       meaning" plus both glosses, matching the pattern used for алфавіт/абетка (ua-lexeme-
       0022/0023 — note that pair is near-synonyms, not true homographs, but the field
       mechanics are identical).
     - Tag both notes `homograph:true` so the set is queryable later (e.g. for a dedicated
       homograph-review pass or card set).
     - Write `UA_Example` sentences where surrounding context makes the intended sense
       unambiguous.
     - Proposed but not yet built: extend the existing `Mnemonic_EN` / `CompareA` /
       `CompareB` fields + Comparison card template (built for про-/пере- prefix pairs) to
       lexical homographs generally, for explicit discrimination drilling. Needs Craig's
       go-ahead before repurposing that template's scope.

3. **True duplicate — same spelling AND same meaning**, encountered again in a later
   chapter. Do NOT create a new note. Instead:
     - Append the new `ch:2.9.X` tag to the note's `tags` list.
     - Append the new chapter to `Tags_Ch` (comma-separated, e.g. `"ch:2.9.1, ch:2.9.2"`).
     - Append a short dated note to `Verification Notes` documenting the reuse.
   This is the exact pattern already used for перегони (ua-lexeme-0144, reused across
   9.1/9.2) — now the standard procedure rather than ad hoc.

**Tooling:** `tools/anki/inspect/check_lexeme_dedup.py` — given one or more candidate
lemmas, stress-strips them (NFD/NFC method) and recursively scans every `ua-lexeme-*.md`
under `domains/ua/anki/notes/lexemes/` for an exact-spelling match. Reports NoteID, file
path, current `EN_Gloss`, and `Tags_Ch` for any match, so the new/homograph/duplicate call
gets made deliberately instead of by ad hoc grep (which produced false negatives earlier
in this project — see the перегони/перемогти́/програ́ти dedup-check history). Meaning
comparison (bucket 2 vs. 3) still requires human/Горох judgment — the tool only automates
the "does this spelling already exist" lookup reliably.

### Deck Presets and Limit Configuration (2026-07-20)

**Strategy:** Differentiated daily limits by cognitive load tier + data-driven preset creation.

**Preset configuration files:**
- `domains/ua/anki/presets/preset_definitions.json` — UA domain presets (6 presets: parent + 5 child tiers)
- `domains/b737/anki/presets/preset_definitions.json` — B737 domain preset (1 preset: review-only)

**Limit configuration files:**
- `domains/ua/anki/config/deck_limits.yaml` — UA domain limit strategy with commentary
- `domains/b737/anki/config/deck_limits.yaml` — B737 domain limit strategy with role-based suspension

**Key concepts:**
- **Parent limit:** 50 new / 100 review per day (UA domain). Child decks cannot exceed this.
- **Cognitive load tiers:**
  - High (PVOM, Lexeme EN→UA): 15–18 new/day (typing/production)
  - Medium (Grammar, Verbs): 20 new/day (recognition + recall)
  - Low (Visual): 25 new/day (recognition)
- **Total child capacity:** 98 new/day (98 > 50 parent), but balanced by selective activation
- **B737 limits:** 0 new / 200 review (review-only, no new cards for type-rating study)
- **Suspension tagging:** Decks suspended with tags documenting reason (role:captain, scope:out-of-scope, etc.)

**Preset creation workflow:**
1. `tools/anki/setup/create_deck_presets.py` — Reads JSON preset definitions, creates/updates presets via AnkiConnect
2. `tools/anki/inspect/update_deck_limits.py` — Reads YAML limits, updates existing deck configs, applies to UA decks
3. `tools/anki/inspect/update_b737_deck_limits.py` — Same pattern for B737 (honors suspension flags)

**Execution order (Craig runs these):**
```bash
python tools/anki/setup/create_deck_presets.py      # Create all presets
python tools/anki/inspect/update_deck_limits.py     # Apply UA limits
python tools/anki/inspect/update_b737_deck_limits.py # Apply B737 limits
```

### Tooling status
| Path | Status | Purpose |
|---|---|---|
| Rename `UA` → `UA_Legacy` in Anki GUI | ✓ done | One-time manual rename; frees UA:: namespace |
| `tools/anki/setup/setup_ua_note_types.py` | ✓ done | Creates/updates UA_Lexeme + UA_Grammar + UA_Visual |
| `tools/anki/setup/create_deck_presets.py` | ✓ new (2026-07-20) | Data-driven preset creation from JSON definitions |
| `tools/anki/sync/ua_lexeme_import.py` | ✓ done | CNSF notes → Anki via AnkiConnect (upsert) |
| `tools/anki/sync/ua_grammar_import.py` | ✓ done | UA_Grammar CNSF notes → Anki (upsert) |
| `tools/anki/sync/ua_visual_import.py` | ✓ done | UA_Visual CNSF notes → Anki (upsert) |
| `tools/anki/extract/gen_ua_lexemes_vstup.py` | ✓ done | One-shot generator for Вступ batch |
| `tools/anki/inspect/update_deck_limits.py` | ✓ new (2026-07-20) | Apply UA domain limits from YAML config |
| `tools/anki/inspect/update_b737_deck_limits.py` | ✓ new (2026-07-20) | Apply B737 domain limits, honor suspension tags |
| `tools/anki/inspect/backfill_source_url.py` | ✓ done | Add Source_URL + Source_Note to all lexeme notes |
| `tools/anki/inspect/verify_stress_goroh.py` | ✓ done | Stress verification vs Горох; Вступ pass complete |
| `tools/anki/inspect/test_preset_creation.py` | ✓ new (2026-07-20) | Diagnostic tool for testing preset creation approaches |
| `tools/anki/generate/ua_generate_examples.py` | ✓ done | Populate UA_Example/EN_Example via Anthropic API |
| `tools/anki/inspect/patch_ch09_conj_tables.py` | ✓ done | One-shot: Verb_Conj_Table for notes 0117–0131 |
| `tools/anki/export/ua_lexeme_md_to_tsv.py` | not written | Canonical notes → TSV (if needed) |
| `tools/anki/extract/export_ua_legacy.py` | not written | Pull existing Anki cards → CNSF skeletons |

### UA_Verb Note Type (Phase 2a, committed 2026-07-12)

**Design:** See [CLAUDE-ua-verb-design.md](CLAUDE-ua-verb-design.md) for complete specification.

**Implementation status (2026-07-12):**
- ✅ UA_Verb note type created in Anki (27 fields: identity, present 6, imperatives 3, past 4, participles 6, metadata)
- ✅ Recognition card template deployed (collapsible details for imperatives, past, participles)
- ✅ ua_verb_import.py + `make ua-verb` target operational
- ✅ 2 base motion verbs authored & imported (ходити ua-verb-0001, їхати ua-verb-0002) — Горох verified
- ✅ ua_verb_export.py created; 69 legacy UA_Verb + 5 UA_Conjugation exported to CNSF, canonicalized
- ⏳ Production template (randomized conjugation drilling): design decision pending

**Key principles:**
- **Separate morphology from vocabulary.** One UA_Verb note (ходити) serves multiple lexemes (ходити, походити, заходити, etc.) via tag linking, not 1:1 coupling.
- **Structured fields, not HTML.** 26 fields store individual conjugation forms (6 pronouns, 3 imperatives, 4 past, 6 participles) + metadata. Templates render as tables. HTML is generated cache, not canonical.
- **CNSF canonical format.** All UA_Verb notes version-controlled as markdown with YAML front matter, imported via AnkiConnect.
- **Tag-based linking.** UA_Lexeme and UA_Verb share tags (e.g., `conj:motion-walking-ходити`) for bidirectional reference without foreign keys.
- **Suspended by default, unsuspend selectively.** Import with `conj:suspended` tag; unsuspend class leaders + irregulars tagged `conj:drill` (~90–100 cards active).

**Phase 2a execution plan (12 steps, in progress 2026-07-13):**
1. ✅ Create `ua_verb_export.py` — Export 69 existing UA_Verb + 5 UA_Conjugation notes to CNSF (backup + version control)
2. ✅ Export all legacy notes to canonical .md files in `domains/ua/anki/notes/verbs/exported/` — 74 notes canonicalized, ready for migration
3. ✅ Build & test Recognition card template for ходити/їхати — Card template designed with block-based layout:
   - **Present tense:** 2-column grid (я/ми, ти/ви, він,вона,воно/вони)
   - **Past tense:** Full-width 4 rows (ч.р., ж.р., с.р., мн.)
   - **Imperative:** Full-width 3 rows (ти, ми, ви)
   - **Participles:** Collapsible section (Act. Pres., Adv. Pres., Pass. Past m/f, Impersonal, Adv. Past)
   - Both ua-verb-0001 (ходити) and ua-verb-0002 (їздити) synced to Anki with correct conjugation data. Template deployed via setup_ua_note_types.py. Created survey_ua_verb.py tool for card verification.
4. Design decision: Production template needed (randomized conjugation drilling) or recognition-only sufficient?
5. Finish ch-09 verbs (Phase 2a) — target 35–50 canonical CNSF notes:
   - **Prefixed motion verbs** (10–14): походити, заходити, виходити, перейходити (ходити base); поїхати, заїхати, виїхати (їхати base). Tag: `conj:motion-walking-ходити` / `conj:motion-vehicle-їхати`
   - **Class leaders** (5–10): писати, читати, казати, робити, жити, говорити, слухати, гуляти, хотіти, etc. Tag: `class:leader, phase:2a, conj:drill`
   - **Irregulars** (8–12): бути, дати/давати, їсти/з'їсти, брати/взяти, ставати/стати, лежати/лягти, сідіти/сісти, etc. Tag: `class:irregular, phase:2a, conj:drill`
6. Create `ua_conjugation_to_verb.py` migration script — Automate 5 UA_Conjugation → UA_Verb CNSF conversion (field mapping: Pres_1S→Pres_1sg, ActPart_Pres→Participle_Active_Present, Gerund→Participle_Adverbial)
7. Run migration — Generate CNSF files in `domains/ua/anki/notes/verbs/migrated/`
8. Field-coverage audit — Compare old vs new structure; flag data loss before sync
9. Verify tags & metadata — Standardize legacy tags to new scheme (phase:2a, conj:drill, conj:suspended)
10. Stage sync in batches:
    - Batch A: 2 new verbs (ходити, їхати) ✓ complete
    - Batch B: New Phase 2a verbs (prefixed, class leaders, irregulars)
    - Batch C: 69 legacy UA_Verb reimported from exported CNSF
    - Batch D: 5 migrated UA_Conjugation → UA_Verb format
11. Final QA — Spot-check in Anki: verify conjugations, tags, deck placement
12. Update CLAUDE.md — Document completion, tools, tagging conventions

**CNSF canonicalization note (2026-07-13):**
- UA_Verb notes use `Verification_Notes` (underscore) not `Verification Notes` (space). The canonicalizer (`tools/anki/cnsf_canonicalize.py`) has been fixed to remove the space variant when processing ua_verb note_type. This prevents duplicate fields in canonical files.

**Participles policy:**
- **Adverbial past participle** (е.g., робивши) — *required*; useful for reading comprehension
- **Passive participle** (e.g., робленный) — *optional*; include if standard/common, else blank

**UA_Verb sequencing** — *501 Ukrainian Verbs* (book) used as breadth/coverage map, not a to-do list.

- **Phase 2a** — Implement UA_Verb note type; author class leaders + irregulars (~60–70 notes). These are structural skeletons of Ukrainian conjugation.
- **Phase 2b** — High-frequency regulars (~60–100 additional notes) from Яблуко + Ukrainian National Corpus frequency list.
- **Phase 2c (ongoing)** — Expand via *501 Ukrainian Verbs* as curriculum demands. Target total: ~160–220 authored notes, ~90–100 marked for active drill.
- **Prefixed verb variants** inherit base conjugation via tag linking; no separate conjugation notes per prefix.

**LLM example sentence generation** — `tools/anki/generate/ua_generate_examples.py` ✓ written.
Run with `make ua-generate-examples BATCH=yabluko-l1/ch-00 [LIMIT=10]`.
Requires `ANTHROPIC_API_KEY` env var and `pip install anthropic`.
Generated examples tagged `example:generated` until reviewed; then remove tag.

Alternative: **extract examples from the Яблуко textbook PDF directly** — higher
authenticity than generated examples and no hallucination risk. The Level 1 PDF is
at `domains/ua/anki/sources/yabluko/level-1/`. Would require OCR/extraction tooling
and per-lemma lookup; feasible as a future enrichment pass to replace or supplement
generated examples.

**Unit 1–12 lexeme generation** — follow the pattern of `gen_ua_lexemes_vstup.py`,
extracting vocab from Яблуко appendix pages 220–237 unit by unit.

**Legacy card migration** — write `export_ua_legacy.py` to pull existing Basic/Cloze
cards from Anki and generate CNSF skeletons. Enrich with PoS, gender, stress marks
before re-importing. Priority: `to_convert` tagged (13) → Shevchuk → Яблуко ch-by-ch.

**EN translation variant guidance** — When developing UA_Lexeme cards, for English words with multiple UA translations, provide the literal EN translation in addition to the common meaning. This helps learners understand why a single English word might map to different Ukrainian equivalents, showing semantic nuance rather than just glosses.

### Flagged Card Fix Workflow (Future)

**Purpose:** Periodic review and correction of flagged cards (red=errors, orange=confusing).
After each study session, fix all flagged cards and remove flags.

**Workflow:**
1. Query Anki for flagged cards in UA domain → extract NoteIDs
2. For each flagged NoteID:
   - Read canonical CNSF file from repo
   - Show to Claude: full note (fields)
   - Claude asks: "Why flagged?" (with flag color context)
   - You respond with issue/fix
   - Claude suggests if unclear
   - Update CNSF file with correction
3. Batch re-import corrected notes to Anki (via `ua_lexeme_import.py`, `ua_verb_import.py`, etc.)
4. Remove flags from all cards in one query
5. Commit corrected CNSF files to git

**Tools needed:**
- `ua_flag_audit.py` — Query flagged cards, extract NoteIDs, map to canonical file paths
- Integration with existing import scripts (ua_lexeme_import.py, ua_verb_import.py, ua_grammar_import.py, ua_visual_import.py)

**Status:** Planned. End of queue after Phase 2a completion.

### Source materials
| Path | Purpose |
|---|---|
| `domains/ua/anki/sources/yabluko/level-1/` | Яблуко Level 1 PDF (good copy available) |
| `domains/ua/anki/sources/yabluko/level-2/` | Яблуко Level 2 OCR'd excerpts: `yabluko-l2-vocabulary.pdf`, `yabluko-l2-grammar-guide.pdf`, `yabluko-l2-verb-dictionary.pdf` |
| `domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/` | 113 ua_lexeme notes — Вступ (= ch-00) |
| `domains/ua/anki/notes/grammar/` | ua_grammar canonical notes (not yet populated) |
| `domains/ua/anki/docs/design.md` | Full schema, deck architecture, migration plan |
| `tools/anki/inspect/survey_ukrainian.py` | AnkiConnect survey script |
