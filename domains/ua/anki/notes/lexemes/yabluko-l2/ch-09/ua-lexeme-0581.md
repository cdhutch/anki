---
schema: cnsf/v0
note_type: ua_lexeme
note_id: ua-lexeme-0581
anki:
  model: UA_Lexeme
  deck: UA::Recognition::UA→EN
tags:
- ch:1.8.5
- domain:ua
- topic:vocabulary
- textbook:яблуко
- ch:2.9.4
- ch:2.6.2
- ch:1.3.3
- ch:1.3.7
- pos:verb
- motion:base
- status:verified
fields:
  NoteID: ua-lexeme-0581
  Lemma: ходи́ти
  Lemma_Euphony: ''
  PartOfSpeech: verb
  Gender: ''
  ImperfectiveUnidirectional: йти
  ImperfectiveUnidirectional_Euphony: іти́
  Perfective: піти́
  Perfective_Euphony: ''
  EuphonyNote: 'іти́ and йти are the same unidirectional imperfective "to go (on foot)" verb
    -- both Горох-verified as valid headwords. йти is used here (and matches the corpus''s
    existing prefixed family: прийти́, ви́йти, дійти́, etc. are all built on й-forms). іти́
    is the more common variant after a consonant or at the start of a clause/sentence, paralleling
    the і/й euphonic alternation seen elsewhere in Ukrainian (cf. і/й "and"). Treat the two
    as free variants of one lexeme, not separate words.'
  AspectCue: ''
  EN_Gloss: to walk, go (on foot)
  Govt_Case: ''
  IrregularForms: ''
  CounterpartForm: ''
  VerbMotion_Pair: 'Base motion-verb triplet: ходи́ти (multidirectional impf.) / йти (unidirectional
    impf.) / піти́ (perf.). Full conjugation tables exist as separate UA_Verb notes: ua-verb-0001
    (ходити), ua-verb-0002/0003 (іти/йти), ua-verb-0004 (піти).'
  ConfusableSet: ''
  Mnemonic_EN: Three-way split with no single-word English equivalent. ходи́ти = "walk/go
    around, habitually, no set direction" (multidirectional). йти = "be walking, headed one
    way, right now" (unidirectional). піти́ = "set off walking / to have gone" (perfective
    -- the trip as a completed whole). Think "wanders" vs "is walking there" vs "went."
  CrossLang_Analog: English does not grammaticalize the multidirectional/unidirectional distinction
    -- "walk" and "go" cover both ходити and йти. The closest analogy is aspectual, not lexical
    -- compare "used to walk over there" (multi) vs "was walking there" (uni) vs "set off
    walking" (perf).
  TypingAnswer: ходити / йти / піти
  UA_Example: Я щодня ходжу до школи пішки, а сьогодні йшов і думав про іспит.
  EN_Example: I walk to school every day, and today I was walking and thinking about the exam.
  Tags_Ch: ch:2.9.4, ch:2.6.2, ch:1.3.3, ch:1.3.7, ch:1.8.5
  Source_URL: https://goroh.pp.ua/Словозміна/ходити; https://goroh.pp.ua/Словозміна/йти; https://goroh.pp.ua/Словозміна/іти;
    https://goroh.pp.ua/Словозміна/піти
  Source_Note: Горох-verified 2026-07-31, base motion-verb triplet drafting session (ua-lexeme-0581..0585).
  Verification Notes: 'Stress marks for all three aspect slots confirmed via Горох Словозміна:
    ходи́ти (multi, impf.), йти/іти́ (uni, impf. -- йти is monosyllabic and Горох does not
    mark a monosyllable), піти́ (perf.). Note: піти''s Словозміна page has THREE homograph
    entries (пі́ти "to sing," піти́ "to go," and Пі́та as a place name) -- confirmed the correct
    entry (піти́, доконаний вид, "Інфінітив піти́, піть") by reading the full page rather
    than grabbing the first table. This is a new note; no prior lexeme note existed for the
    base (unprefixed) ходити/йти/піти triplet -- only the prefixed derivatives (прийти, вийти,
    дійти, etc., ua-lexeme-0114 onward) and the separate UA_Verb conjugation notes (ua-verb-0001..0004)
    existed before this. ConfusableSet intentionally left blank -- this note is not a lexical-confusable/homograph
    pair, it is a single aspect triplet, so the Compare card is expected to stay suspended
    (no ConfusableSet -> suspend_compare_card fires per ua_lexeme_import.py). Drafted per
    Craig''s request 2026-07-31 to fill the gap so the triplet-display feature (TypingTarget_UA
    / _AspectLabel, synced 2026-07-31) has a real multi/uni/perf example beyond singlets.
    The йти-vs-іти EuphonyNote call and the example sentence were the two open review items;
    both addressed 2026-08-04: per Craig, the йти/іти alternation is itself a euphonic (semi-vowel
    і~й) mutation, not a separate free-variant-headword category distinct from the в-/у- pairs
    -- same family as the і/й "and" alternation already cited in EuphonyNote above. Populated
    the new per-slot ImperfectiveUnidirectional_Euphony field with іти́ (previously only documented
    in EuphonyNote prose, which was never actually wired to grant typing credit -- neither
    before nor after the 2026-08-04 per-slot euphony tolerance rollout, since that prose is
    a full paragraph, not a bare delimited alternate, and this note is a triplet so the singlet-only
    EuphonyNote fallback in compute_euphony_slots() didn''t apply either). Typing іти́ for
    the unidirectional slot on the EN->UA card is now graded CORRECT/PERFECT (previously always
    INCORRECT), and the UA->EN Recognition front now shows "йти (іти́)". Merged duplicate
    standalone perfective note ua-lexeme-0581 (aspect-pairing dual-convention cleanup, 2026-08-29).
    Also bulleted in ch:2.6.2. That sub-chapter''s example: ''Він пішов додому рано.'' = ''He
    went home early.''.'
---

