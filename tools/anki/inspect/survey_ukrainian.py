#!/usr/bin/env python3
"""Survey all Ukrainian-related Anki content via AnkiConnect.

Prints a structured report: deck names, note types/fields, tag breakdown,
and sample notes — everything needed to design a canonical note schema.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/inspect/survey_ukrainian.py
    python tools/anki/inspect/survey_ukrainian.py > /tmp/ukrainian_survey.txt
"""
from __future__ import annotations

import json
import sys
import urllib.request
from collections import Counter, defaultdict

ANKI_URL = "http://127.0.0.1:8765"
SAMPLE_PER_MODEL = 3  # number of sample notes to show per note type


def anki(action: str, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, payload, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        result = json.loads(r.read())
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error ({action}): {result['error']}")
    return result["result"]


def find_ukrainian(query: str) -> list[int]:
    return anki("findNotes", query=query)


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def subsection(title: str):
    print(f"\n--- {title} ---")


def main():
    print("AnkiConnect Ukrainian Survey")
    print(f"URL: {ANKI_URL}\n")

    # ------------------------------------------------------------------ #
    # 1. All decks — flag Ukrainian-looking ones
    # ------------------------------------------------------------------ #
    section("1. ALL DECKS (Ukrainian-relevant flagged with *)")
    all_decks = sorted(anki("deckNames"))
    ua_decks = []
    for d in all_decks:
        marker = ""
        if any(kw in d.lower() for kw in ("ukr", "ukrainian", "uкр", "україн")):
            marker = "  *"
            ua_decks.append(d)
        print(f"  {d}{marker}")

    if not ua_decks:
        print("\n  (no decks with 'ukr'/'ukrainian' in name — will search by tag/content too)")

    # ------------------------------------------------------------------ #
    # 2. Find all notes that look Ukrainian
    #    Try several search strategies
    # ------------------------------------------------------------------ #
    section("2. UKRAINIAN NOTE DISCOVERY")

    queries = {
        "deck contains 'ukr'":     "deck:*ukr*",
        "deck contains 'Ukr'":     "deck:*Ukr*",
        "tag contains 'ukr'":      "tag:*ukr*",
        "tag contains 'ukrainian'":"tag:*ukrainian*",
        "tag lang:uk":             "tag:lang:uk",
        "tag language:ukrainian":  "tag:language:ukrainian",
    }

    ua_note_ids: set[int] = set()
    for label, q in queries.items():
        try:
            ids = find_ukrainian(q)
            print(f"  {label:35s}  {len(ids):>6,} notes")
            ua_note_ids.update(ids)
        except Exception as e:
            print(f"  {label:35s}  ERROR: {e}")

    print(f"\n  Total unique Ukrainian notes found: {len(ua_note_ids):,}")

    if not ua_note_ids:
        print("\n  No Ukrainian notes found via standard queries.")
        print("  Tip: rerun after adding tag:lang:uk or similar to your cards.")
        sys.exit(0)

    # ------------------------------------------------------------------ #
    # 3. Break down by note type
    # ------------------------------------------------------------------ #
    section("3. NOTE TYPE BREAKDOWN")

    # Fetch note info in batches of 500
    note_ids = list(ua_note_ids)
    all_note_info = []
    batch = 500
    for i in range(0, len(note_ids), batch):
        all_note_info.extend(anki("notesInfo", notes=note_ids[i:i+batch]))

    model_counter: Counter = Counter()
    model_notes: dict[str, list] = defaultdict(list)
    for n in all_note_info:
        m = n["modelName"]
        model_counter[m] += 1
        model_notes[m].append(n)

    for model, count in model_counter.most_common():
        print(f"  {count:>6,}  {model}")

    # ------------------------------------------------------------------ #
    # 4. Field schema per note type
    # ------------------------------------------------------------------ #
    section("4. FIELD SCHEMAS PER NOTE TYPE")

    all_models = anki("modelNames")
    ua_models = [m for m in all_models if m in model_counter]

    for model in ua_models:
        subsection(model)
        fields = anki("modelFieldNames", modelName=model)
        for i, f in enumerate(fields, 1):
            print(f"    {i:2}. {f}")

    # ------------------------------------------------------------------ #
    # 5. Tag breakdown across Ukrainian notes
    # ------------------------------------------------------------------ #
    section("5. TAG BREAKDOWN (top 60)")

    tag_counter: Counter = Counter()
    for n in all_note_info:
        for t in n.get("tags", []):
            tag_counter[t] += 1

    for tag, count in tag_counter.most_common(60):
        print(f"  {count:>6,}  {tag}")

    # ------------------------------------------------------------------ #
    # 6. Sample notes per model
    # ------------------------------------------------------------------ #
    section(f"6. SAMPLE NOTES ({SAMPLE_PER_MODEL} per note type)")

    for model in ua_models:
        subsection(f"Model: {model}")
        samples = model_notes[model][:SAMPLE_PER_MODEL]
        for n in samples:
            print(f"\n  Note ID : {n['noteId']}")
            print(f"  Tags    : {' '.join(n.get('tags', []))}")
            for fname, fdata in n["fields"].items():
                val = fdata["value"].replace("\n", "↵").replace("<br>", "↵")
                # Truncate long HTML
                if len(val) > 120:
                    val = val[:117] + "..."
                print(f"  {fname:<25} {val}")

    # ------------------------------------------------------------------ #
    # 7. Deck distribution of Ukrainian notes
    # ------------------------------------------------------------------ #
    section("7. DECK DISTRIBUTION OF UKRAINIAN NOTES")

    deck_counter: Counter = Counter()
    for n in all_note_info:
        # cards → deck; one note can have multiple cards
        pass  # need cards for deck info — do a second lookup

    # Get cards for all Ukrainian notes
    card_ids = anki("findCards", query=" OR ".join(f"nid:{nid}" for nid in note_ids[:200]))
    # Limit to 200 notes for deck lookup to keep it fast
    if card_ids:
        cards_info = anki("cardsInfo", cards=card_ids[:500])
        for c in cards_info:
            deck_counter[c["deckName"]] += 1

    for deck, count in deck_counter.most_common():
        print(f"  {count:>6,}  {deck}")

    print("\n\nSurvey complete.")


if __name__ == "__main__":
    main()
