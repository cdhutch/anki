#!/usr/bin/env python3
"""Generate ua_lexeme CNSF stub notes for Яблуко Level 1, Вступ.

Run from repo root:
    python tools/anki/extract/gen_ua_lexemes_vstup.py

Numbers and pronouns are omitted — those become grammar notes separately.

Schema notes:
- Lemma:          primary form; for verbs = IPFV infinitive (with stress marks)
- Perfective:     PFV infinitive; blank for non-verbs
- CounterpartForm: cross-gender paired lexeme (e.g. f: акто́рка / m: медбра́т)
- IrregularForms: irregular gen/pl, indeclinability, special stems
- TypingAnswer:   Lemma stripped of stress marks (U+0301) — student types without accents
"""
from pathlib import Path

OUT_DIR = Path("domains/ua/anki/notes/lexemes/yabluko-l1/vstup")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Each tuple:
# (lemma, en_gloss, pos, gender, counterpart_form, irregular_forms, confusable, extra_tags, status)
#
# pos:         noun / adjective / adverb / phrase / proper-noun
# gender:      m / f / n / indecl / '' (blank for non-nouns)
# counterpart: cross-gender form, e.g. 'f: акто́рка' or 'm: медбра́т'
# irregular:   gen/pl irregularities, indeclinability — inflectional properties of THIS lemma
# confusable:  related lemma(s) easily confused with this one

VOCAB = [
    # === PROFESSIONS ===
    #  lemma                  en_gloss                        pos      gen  counterpart                     irregular                           confusable    extra_tags                          status
    ("акто́р",             "actor",                        "noun", "m",  "f: акто́рка",                   "",                                  "",           ["pos:profession"],                 "verified"),
    ("бізнесме́н",         "businessman",                  "noun", "m",  "f: бізнесме́нка",               "",                                  "",           ["pos:profession"],                 "verified"),
    ("воді́й",             "driver",                       "noun", "m",  "",                              "",                                  "",           ["pos:profession", "stress:unverified"], "verified"),
    ("журналі́ст",         "journalist",                   "noun", "m",  "f: журналі́стка",               "",                                  "",           ["pos:profession"],                 "verified"),
    ("куха́р",             "cook, chef",                   "noun", "m",  "f: куха́рка",                   "",                                  "",           ["pos:profession"],                 "verified"),
    ("лі́кар",             "doctor, physician",            "noun", "m",  "f: лі́карка",                   "",                                  "",           ["pos:profession"],                 "verified"),
    ("медсестра́",         "nurse",                        "noun", "f",  "m: медбра́т",                   "",                                  "",           ["pos:profession"],                 "verified"),
    ("офіціа́нтка",        "waitress",                     "noun", "f",  "m: офіціа́нт",                  "",                                  "",           ["pos:profession"],                 "verified"),
    ("пенсіоне́р",         "pensioner, retiree",           "noun", "m",  "f: пенсіоне́рка",               "",                                  "",           ["pos:profession"],                 "verified"),
    ("пи́сьменник",        "writer, author",               "noun", "m",  "f: пи́сьменниця",               "",                                  "",           ["pos:profession"],                 "verified"),
    ("полі́тик",           "politician",                   "noun", "m",  "m/f: same form",                "",                                  "",           ["pos:profession"],                 "verified"),
    ("продаве́ць",         "salesperson, seller",          "noun", "m",  "f: продавчи́ня",                "gen: продавця́",                     "",           ["pos:profession"],                 "verified"),
    ("спі́вак",            "singer",                       "noun", "m",  "f: співа́чка",                  "",                                  "",           ["pos:profession"],                 "verified"),
    ("спортсме́н",         "sportsman, athlete",           "noun", "m",  "f: спортсме́нка",               "",                                  "",           ["pos:profession"],                 "verified"),
    ("студе́нт",           "student (m.)",                 "noun", "m",  "f: студе́нтка",                 "",                                  "студе́нтка",  ["pos:profession"],                 "verified"),
    ("студе́нтка",         "student (f.)",                 "noun", "f",  "m: студе́нт",                   "",                                  "студе́нт",   ["pos:profession"],                 "verified"),
    ("фе́рмер",            "farmer",                       "noun", "m",  "f: фе́рмерка",                  "",                                  "",           ["pos:profession"],                 "verified"),
    ("худо́жник",          "artist, painter",              "noun", "m",  "f: худо́жниця",                 "",                                  "",           ["pos:profession"],                 "verified"),
    ("юри́ст",             "lawyer, jurist",               "noun", "m",  "m/f: same form",                "",                                  "",           ["pos:profession"],                 "verified"),
    ("вчи́тель",           "teacher",                      "noun", "m",  "f: вчи́телька / учи́телька",    "",                                  "",           ["pos:profession"],                 "verified"),
    ("школя́р",            "schoolboy, pupil",             "noun", "m",  "f: школя́рка",                  "",                                  "",           ["pos:profession"],                 "verified"),

    # === COMMON NOUNS ===
    ("абе́тка",            "alphabet; ABC primer",         "noun", "f",  "",                              "",                                  "алфаві́т",    [],                                 "verified"),
    ("алфаві́т",           "alphabet",                     "noun", "m",  "",                              "",                                  "абе́тка",     [],                                 "verified"),
    ("адре́са",            "address",                      "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("анке́та",            "questionnaire, form",          "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("бале́т",             "ballet",                       "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("буди́нок",           "building; apartment block",    "noun", "m",  "",                              "gen: будинку; pl: будинки",          "",            [],                                 "verified"),
    ("бу́ква",             "letter (of the alphabet)",     "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("ве́чір",             "evening",                      "noun", "m",  "",                              "",                                  "ра́нок",      [],                                 "verified"),
    ("вік",               "age; century",                 "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("вікно́",             "window",                       "noun", "n",  "",                              "",                                  "",            [],                                 "verified"),
    ("впра́ва",            "exercise (in a workbook)",     "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("ву́лиця",            "street",                       "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("завда́ння",          "task, assignment",             "noun", "n",  "",                              "gen sg = pl: завда́ння",             "",            [],                                 "verified"),
    ("зо́шит",             "notebook",                     "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("імʼя́",              "first name, given name",       "noun", "n",  "",                              "н.р. despite -я ending; pl: імена́", "",            [],                                 "verified"),
    ("кварти́ра",          "apartment, flat",              "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("кни́жка",            "book",                         "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("компʼю́тер",         "computer",                     "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("конве́рт",           "envelope",                     "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("краї́на",            "country",                      "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("малю́нок",           "drawing, picture",             "noun", "m",  "",                              "gen: малю́нка",                      "",            [],                                 "verified"),
    ("метро́",             "metro, subway",                "noun", "n",  "",                              "indeclinable",                       "",            [],                                 "verified"),
    ("мі́сто",             "city, town",                   "noun", "n",  "",                              "",                                  "",            [],                                 "verified"),
    ("мо́ва",              "language",                     "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("му́зика",            "music",                        "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("ніж",               "knife",                        "noun", "m",  "",                              "gen: но́жа; pl: но́жі",              "",            [],                                 "verified"),
    ("ніч",               "night",                        "noun", "f",  "",                              "gen: но́чі",                         "ве́чір",      [],                                 "verified"),
    ("олі́вець",           "pencil",                       "noun", "m",  "",                              "gen: олі́вця (loses -е-)",           "ру́чка",      [],                                 "verified"),
    ("о́пера",             "opera",                        "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("о́фіс",              "office",                       "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("парасо́ля",          "umbrella",                     "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("па́рта",             "school desk",                  "noun", "f",  "",                              "",                                  "стіле́ць",    [],                                 "verified"),
    ("піані́но",           "piano",                        "noun", "n",  "",                              "indeclinable",                       "",            [],                                 "verified"),
    ("підру́чник",         "textbook",                     "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("пра́пор",            "flag",                         "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("прі́звище",          "surname, last name",           "noun", "n",  "",                              "",                                  "",            [],                                 "verified"),
    ("профе́сія",          "profession, occupation",       "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("ра́нок",             "morning",                      "noun", "m",  "",                              "gen: ра́нку",                        "ве́чір",      [],                                 "verified"),
    ("рік",               "year",                         "noun", "m",  "",                              "gen: ро́ку; pl: ро́ки",              "",            [],                                 "verified"),
    ("ру́чка",             "pen",                          "noun", "f",  "",                              "",                                  "олі́вець",    [],                                 "verified"),
    ("сімʼя́",             "family",                       "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("стаття́",            "article (in a publication)",   "noun", "f",  "",                              "gen: статті́",                       "",            [],                                 "verified"),
    ("стіле́ць",           "chair",                        "noun", "m",  "",                              "gen: стільця́; pl: стільці́",        "па́рта",      [],                                 "verified"),
    ("сторі́нка",          "page",                         "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("ува́га",             "attention!",                   "noun", "f",  "",                              "used as exclamation",                "",            [],                                 "verified"),
    ("фільм",             "film, movie",                  "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),
    ("фі́рма",             "firm, company",                "noun", "f",  "",                              "",                                  "",            [],                                 "verified"),
    ("число́",             "number",                       "noun", "n",  "",                              "",                                  "",            [],                                 "verified"),
    ("цирк",              "circus",                       "noun", "m",  "",                              "",                                  "",            [],                                 "verified"),

    # === COUNTRIES (proper nouns) ===
    ("Австра́лія",         "Australia",                    "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Аме́рика",           "America",                      "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Брази́лія",          "Brazil",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Великобрита́нія",    "Great Britain",                "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Євро́па",            "Europe",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Іспа́нія",           "Spain",                        "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Іта́лія",            "Italy",                        "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Кана́да",            "Canada",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Кита́й",             "China",                        "proper-noun", "m", "", "", "", ["pos:country"], "verified"),
    ("Ні́меччина",         "Germany",                      "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("По́льща",            "Poland",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Росі́я",             "Russia",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Туре́ччина",         "Turkey",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Украї́на",           "Ukraine",                      "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Фра́нція",           "France",                       "proper-noun", "f", "", "", "", ["pos:country"], "verified"),
    ("Япо́нія",            "Japan",                        "proper-noun", "f", "", "", "", ["pos:country"], "verified"),

    # === NATIONALITY ADJECTIVES ===
    ("англі́йська",        "English (adj.)",               "adjective", "", "m: англі́йський; n: англі́йське", "", "", ["pos:nationality-adj"], "verified"),
    ("брази́льська",       "Brazilian (adj.)",             "adjective", "", "m: брази́льський",               "", "", ["pos:nationality-adj"], "verified"),
    ("іспа́нська",         "Spanish (adj.)",               "adjective", "", "m: іспа́нський",                 "", "", ["pos:nationality-adj"], "verified"),
    ("іта́лійська",        "Italian (adj.)",               "adjective", "", "m: іта́лійський",                "", "", ["pos:nationality-adj"], "verified"),
    ("кита́йська",         "Chinese (adj.)",               "adjective", "", "m: кита́йський",                 "", "", ["pos:nationality-adj"], "verified"),
    ("ні́мецька",          "German (adj.)",                "adjective", "", "m: ні́мецький",                  "", "", ["pos:nationality-adj"], "verified"),
    ("по́льська",          "Polish (adj.)",                "adjective", "", "m: по́льський",                  "", "", ["pos:nationality-adj"], "verified"),
    ("росі́йська",         "Russian (adj.)",               "adjective", "", "m: росі́йський",                 "", "", ["pos:nationality-adj"], "verified"),
    ("туре́цька",          "Turkish (adj.)",               "adjective", "", "m: туре́цький",                  "", "", ["pos:nationality-adj"], "verified"),
    ("украї́нська",        "Ukrainian (adj.)",             "adjective", "", "m: украї́нський",                "", "", ["pos:nationality-adj"], "verified"),
    ("францу́зька",        "French (adj.)",                "adjective", "", "m: францу́зький",                "", "", ["pos:nationality-adj"], "verified"),
    ("япо́нська",          "Japanese (adj.)",              "adjective", "", "m: япо́нський",                  "", "", ["pos:nationality-adj"], "verified"),

    # === ADVERBS / RESPONSES ===
    ("до́бре",             "well; fine; good",             "adverb", "", "", "", "", [], "verified"),
    ("непога́но",          "not bad",                      "adverb", "", "", "", "", [], "verified"),
    ("норма́льно",         "normally; fine",               "adverb", "", "", "", "", [], "verified"),
    ("пра́вильно",         "correctly; right",             "adverb", "", "", "", "", [], "verified"),
    ("ціка́во",            "interestingly; I wonder",      "adverb", "", "", "", "", [], "verified"),
    ("чу́дово",            "wonderfully; great!",          "adverb", "", "", "", "", [], "verified"),

    # === PHRASES AND GREETINGS ===
    ("приві́т",            "hi, hello (informal)",         "phrase", "", "", "", "", [], "verified"),
    ("До поба́чення",      "Goodbye",                      "phrase", "", "", "", "", [], "verified"),
    ("Ду́же прие́мно",     "Very pleased to meet you",     "phrase", "", "", "", "", [], "verified"),
    ("На добра́ніч",       "Good night",                   "phrase", "", "", "", "", [], "verified"),
    ("Як Вас зва́ти?",     "What is your name? (formal)",  "phrase", "", "", "", "", [], "verified"),
    ("Як спра́ви?",        "How are you? How are things?", "phrase", "", "", "", "", [], "verified"),
    ("Яка́ Ваша профе́сія?","What is your profession?",    "phrase", "", "", "", "", [], "verified"),
    ("Яки́й Ваш телефо́н?","What is your phone number?",  "phrase", "", "", "", "", [], "verified"),
    ("Скі́льки Вам ро́ків?","How old are you? (formal)",   "phrase", "", "", "", "", [], "verified"),
]


NOTE_TEMPLATE = """\
---
schema: cnsf/v0
note_type: ua_lexeme
note_id: {note_id}
anki:
  model: UA_Lexeme
  deck: UA::Recognition::UA→EN
tags:
  - domain:ua
  - topic:vocabulary
  - textbook:яблуко
  - ch:1.0
  - pos:{pos}{extra_tags}
  - status:{status}
fields:
  NoteID: {note_id}
  Lemma: {lemma_q}
  PartOfSpeech: {pos_q}
  Gender: {gender_q}
  Perfective: ''
  EN_Gloss: {gloss_q}
  Govt_Case: ''
  CounterpartForm: {counterpart_q}
  IrregularForms: {irregular_q}
  VerbMotion_Pair: ''
  ConfusableSet: {conf_q}
  CrossLang_Analog: ''
  EuphonyNote: ''
  TypingAnswer: {typing_q}
  UA_Example: ''
  EN_Example: ''
  Verb_Conj_Table: ''
  Tags_Ch: ch:1.0
---
"""


def q(s):
    """Single-quote a YAML string value."""
    if not s:
        return "''"
    return "'" + s.replace("'", "\\'") + "'"


def strip_stress(s):
    """Remove combining acute accent (U+0301) used for stress marks."""
    return s.replace("́", "")


def main():
    seen = set()
    unique = []
    for row in VOCAB:
        lemma = row[0]
        if lemma not in seen:
            seen.add(lemma)
            unique.append(row)

    for i, row in enumerate(unique, start=1):
        lemma, en_gloss, pos, gender, counterpart, irregular, confusable, extra_tags, status = row
        note_id = f"ua-lexeme-{i:04d}"

        extra = ""
        if gender:
            extra += f"\n  - gender:{gender}"
        for t in extra_tags:
            extra += f"\n  - {t}"

        content = NOTE_TEMPLATE.format(
            note_id=note_id,
            pos=pos,
            extra_tags=extra,
            status=status,
            lemma_q=q(lemma),
            pos_q=q(pos),
            gender_q=q(gender),
            gloss_q=q(en_gloss),
            counterpart_q=q(counterpart),
            irregular_q=q(irregular),
            conf_q=q(confusable),
            typing_q=q(strip_stress(lemma)),
        )

        (OUT_DIR / f"{note_id}.md").write_text(content, encoding="utf-8")

    print(f"Generated {len(unique)} notes in {OUT_DIR}/")


if __name__ == "__main__":
    main()
