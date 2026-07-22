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
  is `0033`.
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
