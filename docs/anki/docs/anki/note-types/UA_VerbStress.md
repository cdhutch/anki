# UA_VerbStress Anki Note Type Specification

This document describes a recommended **Anki note type** for learning
Ukrainian verb conjugations while **preserving stress information**. The
design aims to:

-   Capture **stress shifts across conjugation**
-   Maintain **aspect pairs**
-   Support **active recall**
-   Avoid excessive card counts

This note type is meant to complement your **UA_Lexeme** deck.

------------------------------------------------------------------------

# Design Goals

1.  Preserve **stress placement** in every stored form.
2.  Allow reconstruction of the **entire paradigm** from stored forms.
3.  Keep **card count manageable**.
4.  Integrate naturally with existing fields like:
    -   `Lemma`
    -   `AspectPair_IPFV`
    -   `AspectPair_PFV`
    -   `TypingAnswer`

------------------------------------------------------------------------

# Recommended Note Type: `UA_VerbStress`

## Fields

Lemma\
AspectPair_IPFV\
AspectPair_PFV\
TypingAnswer

Pres_1sg\
Pres_2sg\
Pres_3sg\
Pres_1pl\
Pres_2pl\
Pres_3pl

Past_M\
Past_F\
Past_N\
Past_Pl

Imperative_2sg\
Imperative_2pl

InfinitiveStressNote\
StressPatternNote

UA_Example\
EN_Example

Tags

------------------------------------------------------------------------

# Example Entry

Example verb: **писа́ти / написа́ти**

Lemma\
писа́ти

AspectPair_IPFV\
писа́ти

AspectPair_PFV\
написа́ти

TypingAnswer\
писа́ти / написа́ти

Pres_1sg\
пи́шу

Pres_2sg\
пи́шеш

Pres_3sg\
пи́ше

Pres_1pl\
пи́шемо

Pres_2pl\
пи́шете

Pres_3pl\
пи́шуть

Past_M\
писа́в

Past_F\
писа́ла

Past_N\
писа́ло

Past_Pl\
писа́ли

Imperative_2sg\
пиши́

Imperative_2pl\
пиші́ть

------------------------------------------------------------------------

# Card Templates

## Card 1 --- Present Conjugation Recall

Front

Conjugate:

{{Lemma}}

1sg present?

Back

я {{Pres_1sg}}

Full present paradigm:

я {{Pres_1sg}}\
ти {{Pres_2sg}}\
він/вона {{Pres_3sg}}\
ми {{Pres_1pl}}\
ви {{Pres_2pl}}\
вони {{Pres_3pl}}

------------------------------------------------------------------------

## Card 2 --- Stress Pattern

Front

Where is the stress in the present tense of:

{{Lemma}}

Back

{{Pres_1sg}}\
{{Pres_2sg}}\
{{Pres_3sg}}\
{{Pres_1pl}}\
{{Pres_2pl}}\
{{Pres_3pl}}

------------------------------------------------------------------------

## Card 3 --- Past Tense

Front

Past masculine of:

{{Lemma}}

Back

він {{Past_M}}

Full past:

він {{Past_M}}\
вона {{Past_F}}\
воно {{Past_N}}\
вони {{Past_Pl}}

------------------------------------------------------------------------

## Card 4 --- Imperative

Front

Imperative (2sg):

{{Lemma}}

Back

ти {{Imperative_2sg}}\
ви {{Imperative_2pl}}

------------------------------------------------------------------------

# Stress Tracking Strategy

Ukrainian verbs often show **mobile stress**. Examples:

писа́ти → пи́шу\
нести́ → несу́\
да́ти → дам

Because of this, each form must store **explicit stress marks**.

Recommended categories for `StressPatternNote`:

-   fixed stem stress
-   fixed ending stress
-   infinitive → stem shift
-   stem → ending shift
-   mixed mobility

------------------------------------------------------------------------

# Card Count

Typical card load per verb:

-   Present recall
-   Stress recognition
-   Past recall
-   Imperative recall

Total: **4 cards per verb**

------------------------------------------------------------------------

# Integration With UA_Lexeme

Recommended division:

UA_Lexeme - meaning - aspect pair - government - usage

UA_VerbStress - morphology - stress shifts - conjugation

------------------------------------------------------------------------

# Recommendations

1.  Always store **stress marks in every form**.
2.  Use **Lemma = imperfective verb** when an aspect pair exists.
3.  Keep **TypingAnswer consistent** with your lexeme deck format.
4.  Prefer **real example sentences** to reinforce usage.
5.  Tag verbs by **conjugation pattern** if you want later filtering.

Example tag system:

verb:stress-mobile\
verb:conj-ати\
verb:conj-ити

------------------------------------------------------------------------

# Advantages of This System

-   preserves **stress shifts**
-   minimizes **card explosion**
-   allows **pattern recognition**
-   integrates well with **Slavic verb morphology**
