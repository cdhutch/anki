# Ch-09 Vocabulary Appendix Sourcing Workflow

Source: `domains/ua/anki/sources/yabluko/level-2/yabluko-l2-vocabulary.pdf`, chapter
**"9 Рух — це життя"** ("Motion is Life"), subsections 9.1–9.7. Raw parsed word list
(149 items) delivered to Craig 2026-07-22 — see `ch09_vocab_raw.md` sent that session.
This is a *different* word set from the existing 18 `ua-lexeme-0114`–`0131` prefixed
motion verbs (those came from the grammar guide PDF, not this vocabulary appendix).

Agreed plan (2026-07-22), documented here before any note files were generated.

## The 5 rules (Craig's own wording, confirmed)

1. Check every word against Горох for spelling, intonation (stress), and meaning.
2. Verbs: check `domains/ua/anki/notes/verbs/` for an existing match first. New verbs:
   search Горох for the imperfective/perfective pairing, create the full `UA_Lexeme`,
   create a `UA_Verb` conjugation note, keep it suspended, link lexeme ↔ conjugation note.
3. Noun phrases / verb phrases: make a note for the phrase, and verify (create if
   missing) notes for all components — adjectives, verbs, nouns inside the phrase.
   Incorporate a book/chapter/subchapter tag (`ch:2.9.X`). Use the existing chapter-based
   folder, not a new one.
4. Be as autonomous as possible — minimize back-and-forth on routine calls.
5. Everything lands `status:draft` (imports suspended) until Craig reviews independently.

## Resolved design questions

- **Component auto-creation confirmed**: yes, create missing component lexemes, not just
  flag gaps. Expect real multiplication of note count — subsection 9.1 alone (14 words,
  mostly adjective+noun phrases) produces ~35 notes once phrases + components are counted.
- **Dedup rule**: before creating any new note, check for an existing lemma match across
  the whole corpus (not just this chapter). *A tag collision is not a problem* — tags
  aren't unique keys, multiple unrelated notes can share a tag value. If a word's lemma
  already has a note, **inspect it and update if required** (e.g. add a relevant tag)
  rather than create a duplicate.
- **Tag scheme**: `ch:2.9.1` through `ch:2.9.7` map directly to the vocabulary PDF's own
  subsection numbers (9.1 sports, 9.2 nature/water, ..., 9.7 camping/journey) — confirmed
  fine to reuse the same `ch:2.9.X` tag namespace already used for grammar-guide content
  (60+ existing notes use `ch:2.9.4` for unrelated про-/пере-/до-/в- material); the two
  schemes are allowed to overlap since tags aren't unique.
- **ID scheme**: continue sequential numbering in the *existing* folder
  (`domains/ua/anki/notes/lexemes/yabluko-l2/ch-09/`) — no new subfolder. Next
  `ua-lexeme-` ID is `0132`. Next `ua-verb-` ID (if any subsection turns up a new verb)
  is `0033`. **[Both numbers stale — see "Status update — 2026-08-28" at the bottom of this file for the current ID/dedup/Compare-card process.]**
- **Adjective lexeme schema** (no prior precedent in the corpus): `PartOfSpeech:
  adjective`, `Lemma` = masculine nominative singular (Горох's citation form), `Gender`
  left blank (adjectives inflect for all three, doesn't fit the single-value field).
- **Phrase lexeme schema** (no prior precedent): `PartOfSpeech: phrase`, plus a
  `phrase:noun` or `phrase:verb` tag to distinguish phrase type.
- **Sync/import granularity**: Craig wants to sync **one subchapter at a time** so he can
  control study order — not the whole chapter at once. Not yet resolved how the import
  tooling will filter to just one subchapter's notes (folder-based `make ua-batch` picks
  up everything in `ch-09/`, which will include multiple subchapters' worth of new files
  as they accumulate). Needs a decision before the first sync — likely a tag-filtered
  import (`ch:2.9.X`) rather than folder-based. Not blocking authoring, which proceeds
  subsection by subsection regardless.

## Process per subchapter

1. Classify each item: single noun/adjective, or noun/verb phrase.
2. Check existing lexeme + verb directories for exact-lemma matches (dedup, whole corpus).
3. Батч-fetch Горох Словозміна pages via Claude in Chrome (JS `Promise.all`, established
   technique) for every new headword needed — phrase components, not phrases themselves
   (Горох doesn't have phrase-level entries).
4. New verbs: find aspect pair via Горох, create `UA_Lexeme` + `UA_Verb` (suspended),
   tag-link them.
5. New phrases: create the phrase note; ensure every component has (or gets) a lexeme.
6. Everything `status:draft`; `Source_URL`/`Source_Note` cite Горох (or r2u.org.ua for
   grammar-adjacent content); example sentences self-composed.
7. Present the full batch of new/updated files for Craig's review before he stages/commits.

## Approved sources

See `CLAUDE-approved-web-sources.md` — goroh.pp.ua and r2u.org.ua, pending Craig's
confirmation.

## Confusable-candidate flagging (agreed 2026-07-26, during ch.9 review)

Craig started drafting notes in a later chapter of the level-2 textbook, so he already
has exposure to a lot of vocabulary from the legacy `legacy_UA` Anki notes that hasn't
been re-encountered in this CNSF-authored corpus yet. He doesn't want to wait for the
counterpart word's own chapter to come up before capturing a remembered confusable
relationship -- but the full treatment (bidirectional `ConfusableSet` + a real
contrastive `Mnemonic_EN`) still requires both notes to exist to be done well.

Resolution: a lightweight, one-sided flag now; the full cross-link later.

- When Craig flags a word as confusable with something not yet drafted, add a
  `confusable:candidate` tag to the existing note (distinct from `homograph:true`, which
  is reserved for confirmed, fully cross-linked pairs).
- Populate `ConfusableSet` immediately with the remembered lemma, one-sided -- it's a
  plain-text field, not a hard link to a NoteID, so this is safe even though the
  counterpart note doesn't exist yet. The card surfaces the hint right away.
- Add a one-line `Verification Notes` entry recording what was flagged and why (e.g.
  "Craig flags this as confusable with X -- not yet drafted; revisit when X gets its own
  note").
- When the counterpart word's note is eventually drafted (regular dedup/sourcing pass),
  search for `confusable:candidate` tags matching it, complete the reverse `ConfusableSet`
  link and a real `Mnemonic_EN` contrasting the two, and drop the `confusable:candidate`
  tag from the original note (the pair is now a confirmed, bidirectional link).

**Legacy-deck mining tool**: `tools/anki/setup/mine_legacy_yabluko.py` pulls every note
from the legacy `Legacy::Ukrainian Active::Яблуко` Anki deck via AnkiConnect (Front/Back
notes and Cloze notes alike) into a searchable JSON + flat-text datafile. Craig's Cloze
notes there are the richest source of prior confusable-word context, since that's where
he originally called out contrasts directly. Run this before drafting a note for a word
that might already have legacy context, or when deciding what a `confusable:candidate`
flag was actually about.

## Status update — 2026-08-28 (lessons learned since this doc was written)

This doc dates from 2026-07-22/26, before the ch.8/ch.9 passes finished. The 5 rules and
the per-subchapter process below are still the right shape, but several specifics have
changed. Superseding details:

- **Dedup is now a formal 5-bucket triage**, not just "check for an existing lemma match."
  See CLAUDE.md → "Vocabulary dedup & homograph handling" for the canonical description:
  (1) brand new, (2) homograph — same spelling, unrelated meaning, (3) true duplicate —
  same spelling and meaning, reused across chapters (append `ch:2.X.Y` + `Tags_Ch` + a
  dated `Verification Notes` line rather than creating a new note), (4) convergent
  synonyms — different spellings, overlapping `EN_Gloss` (not spelling-based, judgment
  call, audited periodically rather than per-candidate), (5) pending-confusable watchlist —
  tag an existing note `pending-confusable:<bare-spelling>` when Craig names a not-yet-
  sourced future partner.
- **Dedup tooling exists now** (all Craig-run, per the Big 3 Rules — Claude reads/greps the
  corpus directly instead): `tools/anki/inspect/check_lexeme_dedup.py` (per-candidate
  spelling check), `tools/anki/lib/lexeme_dedup.py` (library, `create_or_link_lexeme()`,
  `strip_stress()`), `tools/anki/inspect/build_lexeme_index.py` (whole-corpus TSV dump —
  built specifically because per-file device-bridge staging hit HTTP 429 rate limits
  around ~180 files; don't stage note files one at a time at scale, read them via
  `device_bash cat`/`grep` instead or ask Craig to run the index script), `tools/anki/
  inspect/check_pending_confusables.py` (bucket-5 watchlist scanner, wired into
  `make ua-check`), `tools/anki/extract/gen_ch09_subsection.py` (routes a drafted batch
  through `create_or_link_lexeme()` so no candidate skips the dedup check — never
  exercised against a real batch yet as of this writing).
- **Compare-card architecture was replaced (landed 2026-08-26, cleaned up 2026-08-27).**
  The per-note `CompareA`/`CompareB`/`CompareC`/`CompareD`/`CompareScenario`/
  `Homograph_SenseA`/`Homograph_SenseB` fields described implicitly by the old dedup
  buckets above are **retired** — do not hand-author them on new notes. The single source
  of truth is now `domains/ua/anki/confusable_clusters.yaml` (`ClusterRegistry`): a
  cluster has a `canonical_note` (hub) + `members` (each `note_id`/`lemma`/`status`/
  `chapter`/`comment`/`compare_scenario`). At import time `get_cluster_compare_members_json()`
  computes a single `CompareMembers` JSON field from the registry — nothing per-note beyond
  the registry entry itself and an optional prose `ConfusableSet` string for the hub's
  card-back "cf. ..." line. Clusters aren't capped at 2-4 members. **Known limitation:** a
  note can only belong to one cluster (`note_to_cluster` is a single-value dict) — a second
  clustering silently steals the card with no error, so check
  `domains/ua/anki/confusable_clusters.yaml` before adding a note that already anchors a
  cluster to a second one, and flag the conflict in prose instead of picking a side if it
  comes up.
- **`ch:reference` convention (2026-08-26/27):** a note with no real textbook placement —
  existing purely to complete a confusable cluster — gets `ch:reference` and lives in
  `domains/ua/anki/notes/lexemes/reference/`, outside the `yabluko-l1`/`yabluko-l2` tree.
  Not expected to be needed for this pass (every word here has a real chapter), but relevant
  if a cluster partner turns out to need a component word with no textbook home.
- **`status:verified` is now the sole gatekeeper tag** (confirmed against live
  `ua_lexeme_import.py` 2026-08-28) — the old `stress:verified`/`stress:unverified` two-tag
  scheme mentioned nowhere in this doc but present in some ch.8 notes is retired. Every new
  note in this pass lands `status:draft`, same as this doc already said.
- **Euphony stress-mark convention** (`check_euphony_stress.py`, new 2026-08-18, wired into
  `make ua-check`): any populated `*_Euphony` field with a multisyllabic word must carry a
  stress mark. Monosyllables are exempt.
- **Orange flags no longer suspend cards** (2026-08-10) — only red does. Doesn't change
  drafting (everything here starts `status:draft` regardless), but relevant if Craig flags
  something during his review pass.
- **Chapter-tag format was widened** (`tests/ua/test_confusable_clusters.py::test_chapter_format`)
  to `^(?:[123]\.[0-9]+(\.[0-9]+)?|reference)$` — i.e. `1.`/`2.`/`3.`-prefixed chapter
  numbers, or the literal `reference`. This pass's tags (`ch:2.1.X` through `ch:2.7.X`,
  `ch:2.10.X`, `ch:2.11.X`, `ch:2.12.X`) all fit the existing `2.`-prefix pattern already
  used for ch.8/ch.9.
