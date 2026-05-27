#!/usr/bin/env python3
"""Query AnkiConnect for all deck option presets and print every available parameter.

Run this while Anki is open with the AnkiConnect add-on active:
    python3 tools/anki/inspect/inspect_deck_configs.py

Writes full JSON to: build/deck_config_report.json
"""

import json
import urllib.request
from pathlib import Path

ANKI_URL = "http://localhost:8765"

# Human-readable labels for coded integer fields
REVIEW_ORDER = {0: "random", 1: "due date", 2: "deck", 3: "due date then random", 4: "relative overdueness"}
NEW_SORT_ORDER = {0: "card template then deck", 1: "card template then random", 2: "earliest due date first",
                  3: "latest due date first", 4: "random", 5: "no sorting", 6: "by deck"}
NEW_GATHER_PRIORITY = {0: "deck", 1: "scheduled then deck", 2: "scheduled then random"}
NEW_MIX = {0: "distribute through reviews", 1: "show after reviews", 2: "show before reviews"}
INTERDAY_LEARNING_MIX = {0: "distribute through reviews", 1: "show after reviews", 2: "show before reviews"}
LEECH_ACTION = {0: "suspend card", 1: "tag only"}
ANSWER_ACTION = {0: "none", 1: "answer again", 2: "answer good", 3: "answer easy", 4: "bury card", 5: "suspend card"}
QUESTION_ACTION = {0: "none", 1: "show answer"}


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, payload, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = json.loads(resp.read())
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error on '{action}': {result['error']}")
    return result["result"]


def decode(value, lookup):
    if isinstance(value, int) and value in lookup:
        return f"{value}  ({lookup[value]})"
    return value


def fmt_weights(weights):
    if not weights:
        return "[] (not set)"
    return "[" + ", ".join(f"{w:.6g}" for w in weights) + "]"


def print_preset(cfg):
    is_dyn = bool(cfg.get("dyn") and cfg.get("terms"))

    print(f"\n{'─'*60}")
    print(f"  PRESET: {cfg.get('name', '?')}  [id={cfg.get('id')}]")
    print(f"{'─'*60}")

    if is_dyn:
        print("  (Dynamic/filtered deck — no standard scheduling config)")
        print(f"  terms      : {cfg.get('terms')}")
        print(f"  resched    : {cfg.get('resched')}")
        return

    # ── FSRS ────────────────────────────────────────────────────────────────
    print("\n  [FSRS]")
    print(f"  fsrs (enabled)         : {cfg.get('fsrs', 'n/a')}")
    print(f"  desiredRetention       : {cfg.get('desiredRetention', 'n/a')}")
    print(f"  fsrsReschedule         : {cfg.get('fsrsReschedule', 'n/a')}")
    print(f"  sm2Retention           : {cfg.get('sm2Retention', 'n/a')}")
    print(f"  ignoreRevlogsBeforeDate: {cfg.get('ignoreRevlogsBeforeDate', 'n/a')}")
    print(f"  weightSearch           : '{cfg.get('weightSearch', '')}'")
    print(f"  fsrsWeights (v4.5)     : {fmt_weights(cfg.get('fsrsWeights', []))}")
    print(f"  fsrsParams5 (v5)       : {fmt_weights(cfg.get('fsrsParams5', []))}")
    print(f"  fsrsParams6 (v6/active): {fmt_weights(cfg.get('fsrsParams6', []))}")

    # ── NEW CARDS ────────────────────────────────────────────────────────────
    new = cfg.get("new", {})
    print("\n  [New Cards]")
    print(f"  perDay                 : {new.get('perDay', 'n/a')}")
    print(f"  newPerDayMinimum       : {cfg.get('newPerDayMinimum', 'n/a')}")
    print(f"  learning steps (delays): {new.get('delays', 'n/a')}  (minutes)")
    print(f"  order                  : {decode(new.get('order'), {0: 'random', 1: 'due order'})}")
    print(f"  bury siblings          : {new.get('bury', 'n/a')}")
    print(f"  initialFactor          : {new.get('initialFactor', 'n/a')}  (ease ÷ 1000)")
    print(f"  graduating interval    : {new.get('ints', ['?'])[0] if new.get('ints') else 'n/a'}  days")
    print(f"  easy interval          : {new.get('ints', ['?', '?'])[1] if new.get('ints') else 'n/a'}  days")
    print(f"  newMix                 : {decode(cfg.get('newMix'), NEW_MIX)}")
    print(f"  newGatherPriority      : {decode(cfg.get('newGatherPriority'), NEW_GATHER_PRIORITY)}")
    print(f"  newSortOrder           : {decode(cfg.get('newSortOrder'), NEW_SORT_ORDER)}")

    # ── REVIEWS ──────────────────────────────────────────────────────────────
    rev = cfg.get("rev", {})
    print("\n  [Reviews]")
    print(f"  perDay                 : {rev.get('perDay', 'n/a')}  (9999 = unlimited)")
    print(f"  reviewOrder            : {decode(cfg.get('reviewOrder'), REVIEW_ORDER)}")
    print(f"  bury siblings          : {rev.get('bury', 'n/a')}")
    print(f"  maxIvl                 : {rev.get('maxIvl', 'n/a')}  days")
    print(f"  ivlFct                 : {rev.get('ivlFct', 'n/a')}  (interval multiplier)")
    print(f"  ease4 bonus            : {rev.get('ease4', 'n/a')}")
    print(f"  hardFactor             : {rev.get('hardFactor', 'n/a')}")

    # ── LAPSES ───────────────────────────────────────────────────────────────
    lapse = cfg.get("lapse", {})
    print("\n  [Lapses]")
    print(f"  relearn steps (delays) : {lapse.get('delays', 'n/a')}  (minutes)")
    print(f"  minInt                 : {lapse.get('minInt', 'n/a')}  days")
    print(f"  mult (new ivl %)       : {lapse.get('mult', 'n/a')}")
    print(f"  leechFails             : {lapse.get('leechFails', 'n/a')}")
    print(f"  leechAction            : {decode(lapse.get('leechAction'), LEECH_ACTION)}")

    # ── INTERDAY LEARNING ────────────────────────────────────────────────────
    print("\n  [Interday Learning]")
    print(f"  interdayLearningMix    : {decode(cfg.get('interdayLearningMix'), INTERDAY_LEARNING_MIX)}")
    print(f"  buryInterdayLearning   : {cfg.get('buryInterdayLearning', 'n/a')}")

    # ── DISPLAY / TIMER ──────────────────────────────────────────────────────
    print("\n  [Display & Timer]")
    print(f"  maxTaken               : {cfg.get('maxTaken', 'n/a')}  sec (max answer time recorded)")
    print(f"  timer                  : {cfg.get('timer', 'n/a')}  (0=off)")
    print(f"  stopTimerOnAnswer      : {cfg.get('stopTimerOnAnswer', 'n/a')}")
    print(f"  secondsToShowQuestion  : {cfg.get('secondsToShowQuestion', 'n/a')}")
    print(f"  secondsToShowAnswer    : {cfg.get('secondsToShowAnswer', 'n/a')}")
    print(f"  questionAction         : {decode(cfg.get('questionAction'), QUESTION_ACTION)}")
    print(f"  answerAction           : {decode(cfg.get('answerAction'), ANSWER_ACTION)}")
    print(f"  autoplay               : {cfg.get('autoplay', 'n/a')}")
    print(f"  replayq                : {cfg.get('replayq', 'n/a')}")
    print(f"  waitForAudio           : {cfg.get('waitForAudio', 'n/a')}")

    # ── EASY DAYS ────────────────────────────────────────────────────────────
    easy = cfg.get("easyDaysPercentages", [])
    if easy:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        print("\n  [Easy Days]")
        for day, pct in zip(days, easy):
            bar = "█" * int(pct * 10)
            print(f"  {day}: {pct:.0%}  {bar}")

    # ── MISC ─────────────────────────────────────────────────────────────────
    print("\n  [Misc]")
    print(f"  mod (last modified)    : {cfg.get('mod', 'n/a')}")
    print(f"  usn                    : {cfg.get('usn', 'n/a')}")


def main():
    print("Connecting to AnkiConnect...")

    all_decks = anki("deckNames")
    b737_decks = [d for d in all_decks if "737" in d or "B737" in d]
    print(f"Found {len(all_decks)} decks total, {len(b737_decks)} B737-related")

    deck_to_config = {}
    for deck in b737_decks:
        try:
            cfg = anki("getDeckConfig", deck=deck)
            deck_to_config[deck] = cfg
        except Exception as e:
            deck_to_config[deck] = {"error": str(e)}

    seen_ids = set()
    unique_configs = {}
    for deck, cfg in deck_to_config.items():
        if isinstance(cfg, dict) and "id" in cfg:
            cid = cfg["id"]
            if cid not in seen_ids:
                seen_ids.add(cid)
                unique_configs[cid] = cfg

    # ── Deck → Preset mapping ────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  B737 DECK → PRESET MAPPING")
    print(f"{'═'*60}")
    for deck, cfg in deck_to_config.items():
        name = cfg.get("name", "ERROR") if isinstance(cfg, dict) else "ERROR"
        print(f"  {deck:<52} → {name}")

    # ── Full preset detail ───────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print(f"  {len(unique_configs)} UNIQUE PRESETS — FULL PARAMETER LISTING")
    print(f"{'═'*60}")
    for cid, cfg in unique_configs.items():
        print_preset(cfg)

    print(f"\n{'─'*60}")

    # ── Write JSON ───────────────────────────────────────────────────────────
    report = {
        "all_decks": all_decks,
        "b737_decks": b737_decks,
        "deck_to_config_name": {
            d: (c.get("name", "?") if isinstance(c, dict) else "ERROR")
            for d, c in deck_to_config.items()
        },
        "unique_presets": unique_configs,
    }
    out = Path("build/deck_config_report.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nFull JSON written to: {out}")


if __name__ == "__main__":
    main()
