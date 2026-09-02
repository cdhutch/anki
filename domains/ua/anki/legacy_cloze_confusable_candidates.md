# Legacy cloze mining — confusable-cluster candidates

Source: `domains/ua/anki/tmp/legacy_cloze_mine_20260901-045317.json` (3,862 notes scanned across
`Legacy::UA_Legacy::*` and `Legacy::Ukrainian Active::*`, 566 contained cloze markup). Of those,
~86 were pure grammar drills (conjugation tables, comparative-adjective morphology, declension
paradigms, case-government tables) and are excluded below — they're not confusable-word content.
The remaining ~480 were read in full and checked against all 57 clusters currently in
`confusable_clusters.yaml`. Nothing was written to the registry — this is a report only, per your
call. Report-only, nothing auto-built.

**Note on the source data:** several of these are Craig's own legacy tags — `conf:thick_full_dense`
and, most strikingly, two notes literally tagged **"Mistaken words"** by Craig years ago. Those are
called out specifically below since they're about as high-confidence as a candidate gets.

## Already captured — confirms existing work

These pairs/groups from the legacy deck are already fully represented in the registry. Listed for
reassurance, not action:

| Legacy note | Words | Registry cluster |
|---|---|---|
| 1706044905870, 1770498349652 (x2!) | товстий / повний | `thick-fat-synonyms` |
| 1667548508631 | тяжкий / важкий | `heavy-hardship-synonyms` (legacy note frames it as literary-vs-modern register rather than severity — worth a look if you want to sharpen the description) |
| 1667513451193, 1668111614968 | звичайно / зазвичай | `of-course-usually-synonyms` |
| 1676131831293 | абетка / алфавіт | `alphabet-types` |
| 1698229814677 | виграв­ати / перемагати | `win-beat-verbs` |
| 1679061331583 | малюнок/малювання/малярство + живопис/картина/розпис + малювати/розписувати/фарбувати | `drawing-nouns` + `painting-nouns` + `painting-verbs` (all three, verbatim) |
| 1703688148603 | потужний / сильний / міцний | `power-strength-synonyms` (legacy framing: external-technical / personal-integral / sturdy-durable — could sharpen your `compare_scenario` wording) |
| 1733168009884 | давній/древній/стародавній/старовинний/античний (+ класичний) | `ancient-synonyms` — класичний appears here too, consistent with your deliberate exclusion of it |
| 1733937687971 | замок / замок | `castle-lock-homograph` |
| 1733165902348 ("Mistaken words") | пригода/погода/природа/порода | `near-rhyme-lookalike-nouns` — Craig's own legacy tag is literally "Mistaken words," matches your framing exactly |
| 1768146945080 | вражаючий / дивовижний | `amazing-impressive-synonyms` |

## Extension candidates — existing clusters, new member

Same cluster, a word the legacy deck pairs against it that isn't a member yet:

- **`quantity-synonyms`** (кілька/скільки/декілька): legacy deck also pairs in **трохи** (1679352491587, 1730821366680: "uncountable" vs кілька "countable"), **мало** (1730821980232), and **кількість** (1730756835990, the abstract noun "a quantity"). Worth considering трохи/мало/кількість as a 4th–6th member or a sibling cluster.
  - One flag: 1730821980232 frames кілька/декілька as different in nuance ("adequacy" vs "flexibility") — this conflicts with the "true synonyms" framing my research this session landed on for that pair. Worth a look — either Craig's old intuition or the dictionary sources (or both, imperfectly) may be right.
- **`intensifier-adverbs`** (значно/набагато/занадто/забагато/замало): legacy deck pairs значно against **дуже** ("very," 1705405995550) — дуже isn't a member.
- **`fire-general-vs-blaze-vs-campfire`** (пожежа/вогонь/ватра): legacy deck pairs ватра against **вогнище** ("a bonfire," 1698601687597) — вогнище isn't a member.
- **`journey-trip-synonyms`** (мандрівка/подорож): legacy deck pairs подорож against **поїздка** (1700156374396) — поїздка isn't a member.
- **`sensation-feeling-synonyms`** (відчуття/почуття): legacy deck adds **настрій** ("mood, frame of mind," 1722971222894) as a third term in the same triad — worth considering as a 3rd member.
- **`look-appearance-synonyms`** (погляд/вигляд/доглядати): legacy deck pairs доглядати against **виглядати** the verb ("to look out of," 1691694236286) — note виглядати (the verb) already exists elsewhere in the registry as `seem-emerge-homograph`, so this isn't strictly uncaptured, just not cross-linked to this cluster.

## New homograph candidates (same spelling, different sense — Shape 1)

- **дорога** (a road) vs **дорога́** (dear, fem. adj.) — stress-shift homograph, exact same pattern as `castle-lock-homograph`/`smooth-plump-homograph`. (1700155293150)
- **молода́** (bride, noun) vs **молода́** (young, fem. adj.) — same spelling, same stress even; distinguished only by context/POS. (1681221069391)
- **слід** (a trail/trace, noun) vs **слід** (should/ought to, modal particle) — same spelling, different grammatical category. (1736516619594)

## New near-synonym / confusable-pair candidates (Shape 2) — high confidence

Either Craig's own legacy tag calls these out explicitly, or the spelling is close enough to be a
genuine visual/phonetic trap (same pattern as `near-rhyme-lookalike-nouns`):

- **"Mistaken words" (Craig's own tag), root -беріг-/-збир-**: берегти/зберегти ("to guard, protect") vs зберігати/зберегти ("to put in storage") vs збирати/зібрати ("to gather, collect") vs збиратися/зібратися ("to plan to do something"). (1721826423926, 1733166065265) — four-way, all sharing overlapping root forms, extremely easy to conflate.
- **горіх** (walnut) vs **горо́х** (peas) — stress-shift near-homograph, unrelated meaning. (1685716391681)
- **кориця** (cinnamon) vs **криниця** (a spring/well) — near-homophone, unrelated meaning. (1687963476647)
- **душа** (a soul) vs **душ** (a shower) — near-homograph. (1687965633546)
- **чоло** (a forehead) vs **чохол** (a cover, of a machine) — near-homograph. (1704669331014)
- **зоря́** vs **зі́рка** (both "a star") — near-homograph, genuine near-synonym too. (1721824259093)
- **відро** (bucket) / **візок** (pushcart) / **вінок** (wreath) — three-way near-rhyme, unrelated meanings, exactly the `near-rhyme-lookalike-nouns` pattern. (1706233514906)
- **виникати/виникнути** (to arise) vs **зникати/зникнути** (to disappear) vs **уникати/уникнути** (to avoid) — near-homograph triple, all share -никати/-никнути. (1727733268811)
- **упізнавати/упізнати** (to recognize) vs **пізнавати/пізнати** (to get to know) vs **дізнаватися/дізнатися** (to find out) — near-homograph triple, -знава-/-зна- root. (1722893194501)
- **вірити/повірити** (to believe in) vs **довіряти/довірити** (to trust) vs **перевіряти/перевірити** (to verify) — near-homograph triple, -віря- root. (1736541471605)
- **визначати/визначити** (to define/determine) vs **відзначати/відзначити** (to commemorate) — near-homograph. (1733173945952)
- **втрачати/втратити** (to lose unintentionally) vs **витрачати/витратити** (to spend intentionally) — near-homograph. (1710586455905)

## New near-synonym candidates — general vocabulary (medium confidence)

Grouped loosely by theme. Note_id given for traceability; not exhaustive prose, just enough to
evaluate:

**Words/naming/identity:** ім'я/назва/прізвище/прізвисько/найменування (1681057363037, 5-way "names of things"). **Feelings/love:** кохання/любов (1668021187285); закохуватися/кохати/кохатися (1681047881775); любий/любовний/улюблений/коханий (1721824513334); дорогий/любий/шановний (1721824560920). **Try/plan/invent:** вигадувати/винаходити/придумувати/планувати/задумувати/задумуватися (1712568224323, rich 6-way). **Pour verbs:** сипати/посипати vs виливати/обливати/вливати, with Craig's own mnemonic already attached (1721144805398) — this one's basically ready to go as-is. **Cut verbs:** різати/відрізати/вирізати/нарізати/розрізати/рубати (1722895678036, 7-way). **"Turn/return/transform" root family:** перевертати/повертати/повертатися/перетворювати/повторювати (1721144646162). **Fear/horror:** страшний/страшенно/страх/страхіття/жах (1730213603545). **Loud:** шумний/голосний/гучний (1753109357342). **Serve:** служити/відслуговувати/прослуговувати/заслуговувати (1754594753749). **Leader/director:** директор/керівник/режисер/лідер (1733166817454).

Plus a long tail of clean two-word pairs, each a plausible standalone cluster: потяг/поїзд (train), гарячий/гострий (hot-temp vs spicy), щеня/цуценя (puppy), ринок/базар (market), танець/танок (dance), палець/палиця (finger vs stick — near-homophone), плід/фрукт (fruit), небіж/племінник + небога/племінниця (nephew/niece, register), дочка/донька (daughter, register), розповідати/розказувати (to narrate), книжка/книга (book), горо́д/сад (vegetable garden vs orchard), інститут/установа, завод/фабрика, мабуть/імовірний, гарний/прекрасний/красивий (beautiful, 3-way), хороший/добрий (good), кожен/кожний (true synonyms, like кілька/декілька), тонкий/худий ("thin" — the natural companion to your thick-fat-synonyms cluster), зустріч/побачення (a meeting), число/дата (a date), зустрічатися/зустрічатися-з (to date vs to meet with), просити/запрошувати/припрошувати (request vs invite x2), боліти/хворіти-захворіти (ache vs be sick), відразу-одразу/негайно (immediately), за раз/тепер (now), шкода/на жаль (unfortunately), брати-взяти-шлюб/одружуватися (get married), потім/згодом (afterwards), відмовляти/домовлятися/замовляти/розмовляти (root -мовля-, 4-way), сорт/рейтинг (a rating), забувати/губити/губитися/заблудитися (to lose/get lost, 4-way), пампушок/пончик/тістечко/торт (pastry, 4-way), святий/Божий (holy/divine), майстерня/майстер/майстриня, мішок/кошик (sack/basket), незвичний/незвичайний (near-homograph), ввічливий/чемний/чесний (polite/disciplined/honest, 3-way — also 1703682023911 duplicate), поруч-з/поряд-з (near-homograph phrase), міняти/змінювати/змінюватися/обмінюватися (4-way), краса/врода (beauty), танцюрист/танцівник (dancer, register), орендувати/здавати/віддавати (rent/give back), бо/тому-що/оскільки (because, register 3-way), група/гурт, конкурс/змагання/матч (competition — related to existing game-match clusters), предмет/суб'єкт, сукня/плаття (dress), ювілей/річниця (anniversary), зерно/зернятко/зважжя (grain family), ставатися/відбуватися (happen: unplanned/planned), веселий/щасливий (happy), стверджувати/заявляти/уявляти/виявлятися/з'являтися (5-way root family), сидіти/сідати/посідати (sit/sit-down/occupy, 3-way), стежка/траса/маршрут (path/route/itinerary — consolidate 3 separate legacy notes), хвилюватися/нервувати (graded intensity), запис­ка/записник/блокнот (note/notebook, near-homograph, consolidate 2 notes), собака/пес (dog, gender/register), комфортний/зручний, за-початку/на-початку-чого (at first), кабінет/офіс, напрям/курс, відпустка/відпочинок, чистити/мити (to clean), скромний/соромний/соромно (near-homograph 3-way), брова/вія (eyebrow/eyelash), лице/обличчя (face), монумент/пам'ятник, лекція/заняття/клас/урок (4-way class/lesson family), перегляд/виставка (review/exhibition — consolidate 2 notes), усмішка/сміх (smile/laughter), сміливий/мужній, заздрісний/ревнивий, головний/основний, зокрема/окремий, пів/половина, штат/держава, міряти/вимірювати (measure generally/precisely), лавра/монастир, викидати/виконувати (weak candidate — see caveats), сни­тися/мріяти (dream), у-той-час/на-той-час/тоді (3-way), колись/одного-разу (once), плавати/пливти/поплисти vs плисти/поплисти (swim/sail nuance), торба/сумка (bag), складатися-з/становити, жадібний/впевнений/впертий (weak — see caveats), загадувати-бажання/згадувати (near-homograph), знайомство/знайомий/ознайомлення, виправляти/поправлятися, позичати/розмічати/помічати (near-homograph-ish), спочатку/на-початку-чого (duplicate of above), залишатися-вдома/сидіти-вдома, сервіз/послуга/сервіс (near-homograph 3-way), сережка/стежка (near-homophone — possibly merge with стежка/траса/маршрут above), мачуха/свекруха, посилка/доставка, використовувати/вживати/уживати (make use of), проводити/встановлювати (install: infrastructure/software), радити/давати-пораду (advise), одруження/весілля (marriage/wedding), поема/вірш/поезія/поет (poetry family), влаштовувати/організовувати (organize), вірність/довіра, важити/поважати/заважати (near-homograph, weigh/respect/interfere), світити/сяяти (radiate/reflect light), день-народження/уродини (birthday, register), вірний/лояльний (loyal), божеволіти/дуріти/дурити (insane/wild/deceive), триматися-на-вершині/посісти-перше-місце (idiom pair), взагалі/загалом (near-homograph "in general"), уставляти/розставляти (insert/arrange), оцінювати/переоцінювати (evaluate/reevaluate — weak, transparent prefix), нудити/скучати/сумувати (nauseated/miss/grieve), тощо/і-так-далі (etc., register), повсякденний/побутовий, зовсім/повністю/поступово/пості́йно (completely/gradually/constantly — consolidate 2 notes), листівка/поштівка (postcard, near-homograph), канцтовари/канцелярські-товари (true synonym, abbreviation), несподіванка/сюрприз, вимагати/виганяти, неправжній/вигаданий/неправдивий (fake/fictitious/false), стукатися/стукнутися vs стукатися/постукатися, стукати/стукнути vs стукати/постукати (knock family, consolidate 2 notes), забава/розвага (fun), шульга/лівша (left-handed, register), свято/фестиваль (festival — also svyato/svyatkuvannya pair, consolidate), злодій/злочинець/злочин (near-homograph 3-way), запізнюватися/спізнюватися (near-homograph, be late), страшний-family (see above), рете́льно/уважно, різкий/різко/різний/інший/різноманітний (near-homograph rich family), поштар/листоноша (postman, register), мешканець/житель (resident), вміння/навичка (capability/skill), молодь/юність (youth: group/life-stage), проголошення/оголошення (near-homograph), дбати/турбуватися (take care of/worry), креативний/творчий, видавати/публікувати (publish: produce/distribute), вказівник/дорожній-знак (sign), перебування/відвідини/відвідування (staying/visit/visiting), прикрашений/декорований (decorated, register), досить/достатньо (true synonym), захід/подія/пригода (semantic-axis triple — note this is a DIFFERENT axis than пригода's existing rhyme-based cluster), своєрідний/унікальний, дослідження/розслідування (near-homograph, also relates to слід homograph above), випо́внюватися/попо́внювати (near-homograph, root -повн-, also relates to повний), водночас/одночасно (true synonym), вертоліт/гелікоптер (true synonym, loanword), наприклад/до-прикладу (true synonym).

## Lower-confidence / needs-judgment (not counted above)

- **Weather noun/adjective/adverb families** (вітер/вітряний/вітряно, гроза/грозовий, прохолода/прохолодний/прохолодно, сніг/сніжний/сніжно, сонце/сонячний/сонячно, туман/туманний/туманно, хмара/хмарний/хмарно/хмарність, дощ/дощовий, спека/спекотний/спекотно, тепло/теплий/тепло, холод/холодний/холодно) — these are single-root noun→adjective→adverb derivation triads, not competing different-root words. Structurally more like a vocabulary grouping than a confusable cluster in the sense the registry currently uses it. Flagging in case you want a different treatment for these, but I'd lean toward leaving them out of the confusable register.
- **Single-word polysemy notes** (one Ukrainian word, two English glosses, no second UA word): банка (jar/can), чек (check/receipt), площа (square/area), великий (big/great), герой (hero/protagonist), дружба (friendship/best man), вид (aspect/type/vista), число (number/date), ку́хня (kitchen/cuisine), родзинка (raisin/charming detail), гвоздика (carnation/cloves), захід (event/West), керувати (drive/manage), похо́дити (originate/resemble), чужий (someone else's/alien), потребувати-type single cards, зад (rear/butt), obслуговування (operation/service), коло́нка (column/loudspeaker), миш­ка (mouse animal/computer), таємниця (secret/enigma, though also paired against секрет elsewhere — that pairing IS in the candidate list above), вівця (just vocab). These aren't "two words confused with each other" so much as one word with two senses — worth a look individually if you want to consider homograph splits, but I didn't treat them as cluster candidates here.
- **Possibly weak/unclear pairings**: викидати/виконувати (share a prefix but not obviously confusable in meaning), жадібний/впевнений/впертий (three unrelated adjectives, unclear why grouped), дресирований/досвідчений (each has its own mnemonic, don't look related to each other), вільний/цілий (English glosses don't obviously collide).

## Stats

- 3,862 notes scanned, 566 contained cloze markup.
- ~86 excluded as pure grammar (conjugation, comparative-adjective morphology, declension/case tables).
- ~480 read in full.
- 11 pairs/groups already fully captured in the registry.
- 5 extension candidates for existing clusters.
- 3 new homograph candidates.
- 12 high-confidence new Shape-2 candidates (Craig-tagged "Mistaken words," or near-homograph spelling risk).
- ~110 additional medium-confidence new candidates (clean vocabulary near-synonym pairs/groups).
- A double-digit set of lower-confidence items (weather word-families, single-word polysemy, a few unclear groupings) flagged separately, not counted as candidates.
