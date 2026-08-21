"""tools/anki/lib/deck_presets.py — machine-readable deck-preset definitions.

Single source of truth for the presets this repo manages. `DECK_PRESETS.md` is
the human-facing rendering of what is here; `create_deck_presets.py` applies it
to Anki. Nothing else should hold preset values.

Written 2026-08-20, replacing domains/{ua,b737}/anki/presets/preset_definitions.json.
Those files had drifted: they specified review limits of 100/6/8/10/8 where live
Anki has 9999 everywhere, so a working idempotent apply would have reliably
reverted the live state. Values here are taken from live Anki, per Craig.

Follows the pattern that fixed CNSF field order: constants imported by the tools
that act on them, rather than a document parsed at runtime.


WHAT THIS MODULE DOES NOT COVER
-------------------------------
* `fsrsParams6` — FSRS parameters are earned from a preset's own review history.
  They are configuration output, not input, and MANAGED_KEYS deliberately
  excludes them so no apply can clobber an optimization.
* Six B737 presets — `B737 FSRS Core`, `B737 FSRS Core (0n_200r)`, `B737 SV Exam`,
  `B737 Cats and Dogs`, `B737 Checklists`, `B737 Mnemonics` — were created by
  other means and are documented but NOT managed here. Adding them would give
  this script ownership of presets nobody asked it to own.
* 15 Legacy presets — unspecified, see DECK_PRESETS.md section 4.
"""
from __future__ import annotations

# Parameters this repo asserts. Anything absent is left exactly as Anki has it.
# Dotted keys index into the nested config dict.
MANAGED_KEYS = (
    "new.perDay",
    "rev.perDay",
    "new.delays",
    "new.separate",
    "lapse.delays",
    "lapse.leechFails",
    "lapse.leechAction",
    "desiredRetention",
    "rev.maxIvl",
    "rev.fuzz",
    "rev.minSpace",
    "rev.bury",
    "new.bury",
    "buryInterdayLearning",
    "newGatherPriority",
    "newSortOrder",
    "newMix",
    "interdayLearningMix",
    "reviewOrder",
    "maxTaken",
    "waitForAudio",
)

# Shared across every managed preset. Read off live Anki 2026-08-20, where all
# nine UA presets were byte-identical on 44 of 46 parameters.
#
# Display-order values are pinned to GUI labels, NOT guessed -- the decode table
# in inspect_deck_configs.py is stale:
#   newGatherPriority 0=Deck            3=Random Notes
#   newSortOrder      0=Card type, then order gathered   4=Random
#   reviewOrder       0=Due date, then random            3=Ascending intervals
BASELINE = {
    "rev.perDay": 9999,
    "new.delays": [15.0, 180.0],
    "new.separate": True,
    "lapse.delays": [10.0],
    "lapse.leechFails": 8,
    "lapse.leechAction": 1,          # 1 = Tag Only
    "desiredRetention": 0.9,
    "rev.maxIvl": 36500,
    "rev.fuzz": 0.05,
    "rev.minSpace": 1,
    "rev.bury": True,
    "new.bury": True,
    "buryInterdayLearning": False,
    "newGatherPriority": 3,          # Random Notes
    "newSortOrder": 4,               # Random
    "newMix": 0,                     # Mix with reviews
    "interdayLearningMix": 0,        # Mix with reviews
    "reviewOrder": 0,                # Due date, then random
    "maxTaken": 60,
    "waitForAudio": False,
}

# name -> {new_per_day, decks, overrides, note}
# `decks` must exist in Anki; a missing deck is reported, never created. The old
# JSON assigned B737 to `B737::FO Systems` and `B737::FO Challenges`, neither of
# which exists, and those failures were swallowed on every run.
PRESETS = {
    "UA": {
        "new_per_day": 50,
        "decks": ["UA"],
        "note": "Top parent. Caps the whole UA tree; children sum to 118.",
    },
    "UA Production Pass-through": {
        "new_per_day": 9999,
        "decks": ["UA::Production"],
        "note": "Middle parent -- deliberately does not throttle.",
    },
    "UA Recognition Pass-through": {
        "new_per_day": 9999,
        "decks": ["UA::Recognition"],
        "note": "Middle parent -- deliberately does not throttle.",
    },
    "UA Lexeme EN→UA": {
        "new_per_day": 15,
        "decks": ["UA::Production::EN→UA"],
        "note": "Typed production. Carries its own fsrsParams6.",
    },
    "UA PVOM": {
        "new_per_day": 18,
        "decks": ["UA::Recognition::PVOM"],
    },
    "UA->EN": {
        "new_per_day": 20,
        "decks": ["UA::Recognition::UA→EN"],
    },
    "UA Visual": {
        "new_per_day": 25,
        "decks": ["UA::Recognition::Visual"],
    },
    "UA Grammar": {
        "new_per_day": 20,
        "decks": ["UA::Recognition::Grammar"],
    },
    "UA Verbs": {
        "new_per_day": 20,
        "decks": ["UA::Verbs"],
    },
    "B737": {
        "new_per_day": 0,
        "decks": ["B737", "B737::FO Procedures"],
        "note": "Almost all B737 notes are in review and the rest suspended, so "
                "new_per_day here is largely inert -- not an intake budget.",
    },
}

# Documented, deliberately not managed. Listed so a reader can tell "we chose not
# to own this" from "we forgot about it".
UNMANAGED = {
    "B737 FSRS Core": "14 decks; older shape, normalization pending (DECK_PRESETS.md 5.1)",
    "B737 FSRS Core (0n_200r)": "3 decks; rename pending (DECK_PRESETS.md 5.2)",
    "B737 SV Exam": "4 decks",
    "B737 Cats and Dogs": "1 deck",
    "B737 Checklists": "1 deck; carries FSRS-6 stock defaults",
    "B737 Mnemonics": "1 deck",
}


def dig(cfg, dotted):
    """Read a dotted key out of a nested config dict. None if any hop is absent."""
    cur = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def put(cfg, dotted, value):
    """Write a dotted key into a nested config dict, creating intermediate dicts."""
    parts = dotted.split(".")
    cur = cfg
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def wanted(name):
    """The full parameter set this repo asserts for one preset."""
    spec = PRESETS[name]
    out = dict(BASELINE)
    out["new.perDay"] = spec["new_per_day"]
    out.update(spec.get("overrides", {}))
    return {k: v for k, v in out.items() if k in MANAGED_KEYS}
