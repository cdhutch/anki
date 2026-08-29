---
schema: cnsf/v0
note_type: ua_verb
note_id: ua-verb-0009
anki:
  model: UA_Verb
  deck: UA::Verbs
tags:
- domain:ua
- class:conj1-consonant+ти
- motion:swimming
- phase:2a
- ch:2.9.2
- status:verified
- release:active
fields:
  NoteID: ua-verb-0009
  Lemma: пливти́
  Aspect: imperfective
  VerbClass: motion-swimming-new
  FreqSource: ch:2.9
  Pres_1sg: пливу́
  Pres_2sg: пливе́ш
  Pres_3sg: пливе́
  Pres_1pl: пливемо́
  Pres_2pl: пливете́
  Pres_3pl: пливу́ть
  Imperative_2sg: пливи́
  Imperative_1pl: пливі́мо
  Imperative_2pl: пливі́ть
  Past_1sg_m: плив
  Past_1sg_f: пливла́
  Past_1sg_n: пливло́
  Past_3pl: пливли́
  Participle_Active_Present: ''
  Participle_Adverbial_Present: пливучи́
  Participle_Passive_Past: ''
  Participle_Impersonal_Past: ''
  Participle_Adverbial_Past: ''
  Source_Note: ''
  Verification Notes: 'Corrected 2026-08-04, per Craig -- stored Pres_*/Imperative_*/Past_*
    fields previously matched плинути ("to flow/stream," an unrelated -нути verb), not пливти.
    Replaced with the Горох-verified пливти paradigm sourced 2026-07-31 while drafting ua-verb-0086
    (плисти) -- see that note''s Verification_Notes for the full sourcing detail and the Горох
    URL (goroh.pp.ua/Словозміна/плисти, which also confirms пливти''s forms). Present tense
    and imperative are IDENTICAL between пливти and плисти (пливу́/пливе́ш/пливе́/пливе́м,пливемо́/пливете́/пливу́ть;
    пливи́/пливі́м,пливі́мо/пливі́ть); only the past tense diverges -- пливти takes плив (masc,
    unstressed monosyllable)/пливла́/пливло́/пливли́, vs плисти''s плив/плила́/плило́/плили́.
    попливти (ua-verb-0010) has a parallel data-mismatch bug (matches попити/поплинути-adjacent
    forms, not попливти) still open -- its correct paradigm was never independently Горох-verified
    (ua-verb-0087/поплисти''s 2026-07-31 sourcing only covered its own lemma, not попливти),
    so it needs its own verification pass before fixing, not a same-session fix like this
    one. 2026-08-04 (continued): found a dangling commit (f907726, branch chore/ua-verb-participle-merge-and-stress-pass,
    deleted locally but still live as origin/chore/ua-verb-participle-merge-and-stress-pass
    -- tagged archive/ua-verb-participle-merge-and-stress-pass for safekeeping) with its own,
    independently-authored version of this note dated 2026-08-02, predating today''s fix.
    Cross-checked both versions live against goroh.pp.ua/Словозміна/пливти. Two findings:
    (1) the dangling branch''s Lemma correctly carries a stress mark (пливти́) -- today''s
    fix had left Lemma unstressed (пливти), a real gap now corrected here, since an unstressed
    multisyllable lemma is the project''s own documented red flag for a bad extraction. (2)
    the dangling branch''s Pres_1pl/Imperative_1pl collapse to single forms (пливемо́/пливі́мо),
    dropping the free-variant short forms -- Горох''s live page confirms BOTH forms are valid
    (пливе́м, пливемо́ / пливі́м, пливі́мо), so today''s dual-variant fix was correct and
    the dangling branch''s version is the one that''s incomplete on this point, not this note.
    The dangling branch also has Participle_Adverbial_Present: пливучи́ populated (blank here)
    and uses a since-superseded schema (single Participle_Passive_Past field instead of this
    note''s Participle_Passive_Past_m/_f split) -- that schema question is a separate, larger-scope
    item for whenever the branch gets properly reconciled, not fixed here. 2026-08-04 (further
    correction, per Craig -- "anything verified from archive/ua-verb-participle-merge-and-stress-pass
    is truth"): Pres_1pl and Imperative_1pl reverted from the dual-variant forms above (пливе́м,
    пливемо́ / пливі́м, пливі́мо) to the dangling branch''s single -мо form (пливемо́ / пливі́мо).
    Горох does list both as valid free variants (confirmed live, see above) -- this isn''t
    a correctness reversal, it''s adopting the branch''s verified project convention of storing
    only the full -мо ending for 1st-plural present/imperative forms rather than both variants.
    Also adopted the branch''s Participle_Adverbial_Present: пливучи́ (previously blank here)
    on the same "branch is truth" basis. Open follow-up: whether ua-verb-0086/0087 (плисти/поплисти)
    -- sourced 2026-07-31, still carrying dual-variant Pres_1pl/Imperative_1pl -- need the
    same -мо-only simplification, and the still-unresolved Participle_Passive_Past schema
    question (single field on the branch vs. this note''s _m/_f split), are both deferred
    to the larger, proper merge of the whole archive/ua-verb-participle-merge-and-stress-pass
    branch, not fixed here. 2026-08-11 (resolved, per Craig): the Participle_Passive_Past
    schema question above is now settled -- singular field, male form as the default, no _m/_f
    split. This note''s Participle_Passive_Past_m/_f (both blank, no data to migrate) consolidated
    back to a single Participle_Passive_Past field. See CLAUDE.md item 13''s 2026-08-11 correction
    for the full history of how the split claim got into this repo in the first place.'
---

