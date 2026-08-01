#!/usr/bin/env python3
"""Apply the Solarized palette to legacy B737 note types.

Models updated:
  - B737_SV_Cloze      (legacy cloze cards, being phased out)
  - B737_Systems       (older systems knowledge cards)

**Trimmed to B737-only 2026-08-01** (see CLAUDE.md item 1/3): this script used
to also carry CSS for UA_Conjugation/UA_Grammar/UA_Lexeme/UA_Lexeme_Legacy/
UA_Verb, but it was never wired into the Makefile, and its UA entries had
drifted stale relative to the live templates (e.g. its UA_Grammar/UA_Verb
versions only styled `.card`, missing most of the classes those templates
actually use). `tools/anki/setup/setup_ua_note_types.py` -- the script that's
actually run via `make ua-setup*` -- is now the single source of truth for
Solarized CSS across all four live UA note types (Lexeme, Grammar, Visual,
Verb). This script stays scoped to the two B737 legacy models above, which
setup_ua_note_types.py does not manage.

Usage:
    python tools/anki/setup/update_legacy_css.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# B737_SV_Cloze
# ---------------------------------------------------------------------------

SV_CLOZE_CSS = """\
/* Light mode (Solarized light) */
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: #586e75;
    background-color: #fdf6e3;
}

.cloze {
    font-weight: bold;
    color: #2aa198;
}

.cloze-text {
    white-space: pre-line;
}

/* Dark mode (Solarized dark) */
.nightMode .card {
    color: #657b83;
    background-color: #032029;
}
.night_mode .card {
    color: #657b83;
    background-color: #032029;
}

.nightMode .cloze {
    color: #2aa198;
}
.night_mode .cloze {
    color: #2aa198;
}
"""

# ---------------------------------------------------------------------------
# B737_Systems
# ---------------------------------------------------------------------------

B737_SYSTEMS_CSS = """\
/* Light mode (Solarized light) */
.card {
    font-family: Arial, sans-serif;
    font-size: 16px;
    color: #586e75;
    background-color: #fdf6e3;
    max-width: 680px;
    margin: 0 auto;
    padding: 16px 20px;
    text-align: left;
}

.sys-wrap { line-height: 1.35; font-size: 16px; }
.sys-kicker { color: #93a1a1; font-size: 12px; letter-spacing: 0.02em; text-transform: uppercase; margin-bottom: 2px; }
.sys-subsystem { font-weight: 700; font-size: 18px; color: #2aa198; margin-bottom: 2px; }
.sys-topic { color: #93a1a1; font-size: 13px; margin-bottom: 10px; }
.sys-prompt { font-size: 17px; font-weight: 600; margin-bottom: 8px; }
.sys-panel { color: #93a1a1; font-size: 13px; margin-top: 8px; }

.sep { border: 0; border-top: 1px solid #93a1a1; margin: 12px 0; }
.block { margin: 10px 0; }
.block .h { font-weight: 700; font-size: 13px; color: #586e75; margin-bottom: 4px; }
.block .body { color: #586e75; }

.meta-row { display: flex; gap: 10px; margin: 6px 0; }
.lbl { min-width: 110px; color: #93a1a1; font-weight: 600; }
.val { color: #586e75; }

.ref { margin-top: 8px; }
.foot { margin-top: 10px; font-size: 12px; }
.muted { color: #93a1a1; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

table { border-collapse: collapse; margin: 8px 0; }
th, td { border: 1px solid #93a1a1; padding: 6px 8px; vertical-align: top; }
th { font-weight: 700; background-color: #eee8d5; }

/* Dark mode (Solarized dark) */
.nightMode .card { color: #657b83; background-color: #032029; }
.night_mode .card { color: #657b83; background-color: #032029; }
.nightMode .sys-kicker { color: #586e75; }
.night_mode .sys-kicker { color: #586e75; }
.nightMode .sys-subsystem { color: #2aa198; }
.night_mode .sys-subsystem { color: #2aa198; }
.nightMode .sys-topic { color: #586e75; }
.night_mode .sys-topic { color: #586e75; }
.nightMode .sys-panel { color: #586e75; }
.night_mode .sys-panel { color: #586e75; }
.nightMode .sep { border-top-color: #586e75; }
.night_mode .sep { border-top-color: #586e75; }
.nightMode .block .h { color: #657b83; }
.night_mode .block .h { color: #657b83; }
.nightMode .block .body { color: #657b83; }
.night_mode .block .body { color: #657b83; }
.nightMode .lbl { color: #586e75; }
.night_mode .lbl { color: #586e75; }
.nightMode .val { color: #657b83; }
.night_mode .val { color: #657b83; }
.nightMode .muted { color: #586e75; }
.night_mode .muted { color: #586e75; }
.nightMode th, .nightMode td { border-color: #586e75; }
.night_mode th, .night_mode td { border-color: #586e75; }
.nightMode th { background-color: #032029; }
.night_mode th { background-color: #032029; }
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

MODELS = {
    "B737_SV_Cloze":    SV_CLOZE_CSS,
    "B737_Systems":     B737_SYSTEMS_CSS,
}


def main() -> int:
    version = anki_request("version", {}, url=ANKI_URL)
    print(f"AnkiConnect version: {version}\n")

    existing = anki_request("modelNames", {}, url=ANKI_URL) or []

    for model_name, css in MODELS.items():
        if model_name not in existing:
            print(f"SKIP: {model_name} not found in Anki")
            continue
        anki_request(
            "updateModelStyling",
            {"model": {"name": model_name, "css": css}},
            url=ANKI_URL,
        )
        print(f"Updated CSS: {model_name}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
