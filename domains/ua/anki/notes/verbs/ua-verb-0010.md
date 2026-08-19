---
schema: cnsf/v0
note_type: ua_verb
note_id: ua-verb-0010
anki:
  model: UA_Verb
  deck: UA::Verbs
tags:
- domain:ua
- motion:swimming
- phase:2a
- conj:drill
- ch:2.9.2
- stress:verified
fields:
  NoteID: ua-verb-0010
  Lemma: попливти́
  Aspect: perfective
  VerbClass: motion-swimming-new
  FreqSource: ch:2.9
  Pres_1sg: попливу́
  Pres_2sg: попливе́ш
  Pres_3sg: попливе́
  Pres_1pl: попливемо́
  Pres_2pl: попливете́
  Pres_3pl: попливу́ть
  Imperative_2sg: попливи́
  Imperative_1pl: попливі́мо
  Imperative_2pl: попливі́ть
  Past_1sg_m: попли́в
  Past_1sg_f: попливла́
  Past_1sg_n: попливло́
  Past_3pl: попливли́
  Participle_Active_Present: ''
  Participle_Adverbial_Present: ''
  Participle_Passive_Past: ''
  Participle_Impersonal_Past: ''
  Participle_Adverbial_Past: ''
  Verification Notes: 'Corrected 2026-08-04, per Craig -- stored Pres_*/Imperative_*/Past_*
    fields previously matched попити ("to drink up")/поплинути-adjacent forms, not попливти.
    Replaced with попливти''s own Горох Словозміна page (goroh.pp.ua/Словозміна/попливти),
    fetched and verified live via Claude in Chrome 2026-08-04 (ua-verb-0087/поплисти''s 2026-07-31
    sourcing had explicitly NOT covered this lemma -- only flagged 0010 as wrong). попливу́/попливе́ш/попливе́/попливе́м,попливемо́/попливете́/попливу́ть
    (future/"Pres_*"), попливи́/попливі́м,попливі́мо/попливі́ть (imperative) turn out IDENTICAL
    to ua-verb-0087 (поплисти)''s forms, matching the same present/imperative-identical, past-divergent
    pattern established for пливти/плисти (ua-verb-0009/0086). Past tense: попли́в (masc --
    stressed, two syllables, unlike пливти''s unstressed monosyllabic плив) / попливла́ /
    попливло́ / попливли́. Горох also lists попливи́-но as an emphatic 2sg imperative variant,
    not captured in a separate field (no *_Emphatic slot in this note type). 2026-08-04 (continued):
    found a dangling commit (f907726, branch chore/ua-verb-participle-merge-and-stress-pass,
    deleted locally but still live as origin/chore/ua-verb-participle-merge-and-stress-pass
    -- tagged archive/ua-verb-participle-merge-and-stress-pass for safekeeping) with its own
    version of this note dated 2026-08-02. Cross-checked both against goroh.pp.ua/Словозміна/попливти
    live. Same pattern as ua-verb-0009: the dangling branch''s Lemma correctly carries a stress
    mark (попливти́) -- corrected here, previously unstressed. Its Pres_1pl/Imperative_1pl
    collapse to single forms, but Горох confirms both free-variant forms are valid (попливе́м,
    попливемо́ / попливі́м, попливі́мо), matching what this note already had at the time.
    Same open schema question (single Participle_Passive_Past field on the dangling branch
    vs. this note''s _m/_f split) applies here too; deferred to the branch-reconciliation
    pass, not fixed in this note. 2026-08-04 (further correction, per Craig -- "anything verified
    from archive/ua-verb-participle-merge-and-stress-pass is truth"): Pres_1pl and Imperative_1pl
    reverted from the dual-variant forms above (попливе́м, попливемо́ / попливі́м, попливі́мо)
    to the dangling branch''s single -мо form (попливемо́ / попливі́мо), matching the same
    project-convention adoption made on ua-verb-0009 -- Горох''s dual free-variant forms are
    still grammatically valid, this is a "store one canonical form" convention choice, not
    a correctness fix. Participle_Adverbial_Present stays blank on both this note and the
    dangling branch (expected -- попливти is perfective, no present participle). Same open
    follow-ups as ua-verb-0009: ua-verb-0087 (поплисти) may need the same -мо-only simplification,
    and the Participle_Passive_Past schema question is deferred to the larger branch-reconciliation
    pass. 2026-08-05: Craig independently re-verified this note''s stored forms and confirmed
    stress:verified (the tag had gone back to stress:unverified in the interim, per Craig''s
    own review process -- see his 2026-08-04 note elsewhere in this session about reverting
    пливти/попливти to unverified pending his own check). No field values changed as part
    of this pass, only the tag. 2026-08-11 (resolved, per Craig): singular field, male form
    as the default, no _m/_f split. This note''s Participle_Passive_Past_m/_f (both blank,
    no data to migrate) consolidated back to a single Participle_Passive_Past field -- see
    ua-verb-0009''s note and CLAUDE.md item 13''s 2026-08-11 correction. Both paragraphs kept
    when maint/verb-review merged main 2026-08-19: they record different things (the 2026-08-05
    tag re-verification and the 2026-08-11 schema decision) and neither supersedes the other.'
---

