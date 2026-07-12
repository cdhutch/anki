# CLAUDE.md — Anki Project Context (B737 + Ukrainian)

**Current work**: Distractor authoring (Phase A), 26/29 systems verified.

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

---

## Ukrainian Domain (`domains/ua/`)

**Branch:** `feature/ua-domain` (based off `main`)

**Status (as of 2026-07-10):** Вступ (ch-00) complete — 113 notes live, stress verified, examples added.
Book 2 Ch. 9 in progress on branch `feature/ua-l2-ch09-motion-verbs`:
  - 18 UA_Lexeme notes authored (ua-lexeme-0114–0131): prefixed walking + vehicle motion verbs.
  - 7 UA_Grammar cloze notes authored (ua-grammar-0001–0007): two-group rule, aspect formation,
    prefix meanings, phonetic changes, apostrophe rule, піти and ходити meanings.
  - 9 UA_Visual notes authored (ua-visual-0001–0009): one per prefix, inline SVG diagrams,
    spatial meaning + prepositional government. Two cards each (Spatial→UA, UA→Spatial).
    Notes in `domains/ua/anki/notes/visual/`.
  - All new notes: `status:draft`. Stresses Горох-verified; `stress:unverified` tag removed.
  - `Verb_Conj_Table` fully populated for all 18 verb pairs (0114–0131).

**UA_Visual card template design (2026-07-10):**
  - Card 1 (Spatial→UA): front = diagram + English meaning; back = Ukrainian prefix, government, verb pairs, example.
  - Card 2 (UA→Spatial): front = Ukrainian prefix + verb pairs; back = diagram + English meaning + government + example.
  - Template redesign fixed & deployed ✅ — `setup_ua_note_types.py` now calls `updateModelTemplates` with all templates in single call (not per-template loop).
  - Templates update correctly via `make ua-setup-visual`.

**Pending before import:**
  1. ✓ Template fix committed & verified
  2. Run: `make ua-setup` (updates UA_Lexeme + UA_Grammar + UA_Visual in Anki with fixed templates)
  3. Flip `status:draft` → `status:verified` after review
  4. Import lexemes: `make ua-batch BATCH=yabluko-l2/ch-09`
  5. Import grammar: `make ua-grammar`
  6. Import visual prefix cards: `make ua-visual`

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

**Verb conjugations:** Removed `Verb_Conj_Table` field from UA_Lexeme; conjugation morphology now belongs in UA_Verb note type as structured fields.

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

### Language conventions (critical)
- Dialect: modern Ukrainian, **Galician/Lviv** register
- Apostrophe: **U+02BC `ʼ`** — never ASCII `'`
- Stress marks: **never guess** — verify against Горох (goroh.pp.ua) via Claude in Chrome.
  Tag unverified with `stress:unverified`. Remove tag only after Горох confirms.
- Stress disambiguation: some words have stress-dependent meanings (e.g. му́зика = music,
  музи́ка = musician). Always check before "correcting" based on Горох alone.
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

### Tooling status
| Path | Status | Purpose |
|---|---|---|
| Rename `UA` → `UA_Legacy` in Anki GUI | ✓ done | One-time manual rename; frees UA:: namespace |
| `tools/anki/setup/setup_ua_note_types.py` | ✓ done | Creates/updates UA_Lexeme + UA_Grammar + UA_Visual |
| `tools/anki/sync/ua_lexeme_import.py` | ✓ done | CNSF notes → Anki via AnkiConnect (upsert) |
| `tools/anki/sync/ua_grammar_import.py` | ✓ done | UA_Grammar CNSF notes → Anki (upsert) |
| `tools/anki/sync/ua_visual_import.py` | ✓ done | UA_Visual CNSF notes → Anki (upsert) |
| `tools/anki/extract/gen_ua_lexemes_vstup.py` | ✓ done | One-shot generator for Вступ batch |
| `tools/anki/inspect/backfill_source_url.py` | ✓ done | Add Source_URL + Source_Note to all lexeme notes |
| `tools/anki/inspect/verify_stress_goroh.py` | ✓ done | Stress verification vs Горох; Вступ pass complete |
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

**Phase 2a execution plan (12 steps, in progress 2026-07-12):**
1. ✅ Create `ua_verb_export.py` — Export 69 existing UA_Verb + 5 UA_Conjugation notes to CNSF (backup + version control)
2. ✅ Export all legacy notes to canonical .md files in `domains/ua/anki/notes/verbs/exported/` — 74 notes canonicalized, ready for migration
3. Build & test Recognition card template for ходити/їхати — verify collapsible rendering in Anki
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
| `domains/ua/anki/sources/yabluko/level-2/` | Яблуко Level 2 PDF (most existing cards are ch:2.x.x — PDF not yet available) |
| `domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/` | 113 ua_lexeme notes — Вступ (= ch-00) |
| `domains/ua/anki/notes/grammar/` | ua_grammar canonical notes (not yet populated) |
| `domains/ua/anki/docs/design.md` | Full schema, deck architecture, migration plan |
| `tools/anki/inspect/survey_ukrainian.py` | AnkiConnect survey script |
