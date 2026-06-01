#!/usr/bin/env python3
"""Apply the Solarized palette to legacy note types (B737 + Ukrainian).

Models updated:
  - B737_SV_Cloze      (legacy cloze cards, being phased out)
  - B737_Systems       (older systems knowledge cards)
  - UA_Conjugation     (Ukrainian conjugation tables)
  - UA_Grammar         (Ukrainian grammar cards)
  - UA_Lexeme          (Ukrainian lexeme cards with examples)
  - UA_Lexeme_Legacy   (legacy Ukrainian cards)
  - UA_Verb            (Ukrainian verb cards)

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
    color: #839496;
    background-color: #073642;
}

.nightMode .cloze {
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
.nightMode .card { color: #839496; background-color: #073642; }
.nightMode .sys-kicker { color: #586e75; }
.nightMode .sys-subsystem { color: #2aa198; }
.nightMode .sys-topic { color: #586e75; }
.nightMode .sys-panel { color: #586e75; }
.nightMode .sep { border-top-color: #586e75; }
.nightMode .block .h { color: #839496; }
.nightMode .block .body { color: #839496; }
.nightMode .lbl { color: #586e75; }
.nightMode .val { color: #839496; }
.nightMode .muted { color: #586e75; }
.nightMode th, .nightMode td { border-color: #586e75; }
.nightMode th { background-color: #073642; }
"""

# ---------------------------------------------------------------------------
# Ukrainian types
# ---------------------------------------------------------------------------

UA_CONJUGATION_CSS = """\
/* Light mode (Solarized light) */
.card {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 18px;
  text-align: left;
  padding: 20px;
  line-height: 1.4;
  color: #586e75;
  background-color: #fdf6e3;
}

.lemma { font-size: 32px; font-weight: 700; margin-bottom: 10px; color: #2aa198; }
.subtitle { font-size: 16px; color: #93a1a1; margin-bottom: 16px; }
.section { font-size: 18px; font-weight: 700; margin-top: 18px; margin-bottom: 8px; color: #586e75; }

.conj-table { border-collapse: collapse; table-layout: fixed; width: 460px; margin-bottom: 12px; }
.conj-table th, .conj-table td { border: 1px solid #93a1a1; padding: 6px 8px; vertical-align: top; color: #586e75; }
.conj-table th { background: #eee8d5; font-weight: 600; text-align: left; }

.col-person { width: 180px; }
.col-form { width: 280px; }

.note { margin-top: 12px; font-size: 16px; color: #93a1a1; }

/* Dark mode (Solarized dark) */
.nightMode .card { color: #839496; background-color: #073642; }
.nightMode .lemma { color: #2aa198; }
.nightMode .subtitle { color: #586e75; }
.nightMode .section { color: #839496; }
.nightMode .conj-table th, .nightMode .conj-table td { border-color: #586e75; color: #839496; }
.nightMode .conj-table th { background: #073642; }
.nightMode .note { color: #586e75; }
"""

UA_GRAMMAR_CSS = """\
/* Light mode (Solarized light) */
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: #586e75;
    background-color: #fdf6e3;
}

/* Dark mode (Solarized dark) */
.nightMode .card {
    color: #839496;
    background-color: #073642;
}
"""

UA_LEXEME_CSS = """\
/* Light mode (Solarized light) */
.card {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 18px;
  color: #586e75;
  background-color: #fdf6e3;
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

.lemma { font-size: 28px; font-weight: bold; margin-bottom: 4px; color: #2aa198; }
.perfective { font-size: 22px; color: #93a1a1; margin-bottom: 8px; }
.pos { font-size: 13px; color: #93a1a1; font-style: italic; margin-bottom: 16px; }
.gender { font-size: 13px; color: #93a1a1; margin-bottom: 4px; }

hr#answer { border: none; border-top: 2px solid #93a1a1; margin: 20px 0; }

.gloss { font-size: 22px; font-weight: bold; margin-bottom: 8px; color: #586e75; }
.counterpart { font-size: 14px; color: #93a1a1; margin-top: 4px; }
.irregular { font-size: 13px; color: #93a1a1; margin-top: 4px; }
.confusable { font-size: 13px; color: #859900; margin-top: 6px; }

.example-ua { font-size: 15px; margin-top: 14px; font-style: italic; color: #586e75; }
.example-en { font-size: 13px; color: #93a1a1; margin-top: 2px; }

.note-id { font-size: 10px; color: #93a1a1; text-align: right; margin-top: 16px; }

input#typeans { font-size: 20px; font-family: system-ui, -apple-system, sans-serif; width: 80%; text-align: center; color: #586e75; background-color: #eee8d5; border: 1px solid #93a1a1; padding: 6px; }

/* Dark mode (Solarized dark) */
.nightMode .card { color: #839496; background-color: #073642; }
.nightMode .lemma { color: #2aa198; }
.nightMode .perfective { color: #586e75; }
.nightMode .pos { color: #586e75; }
.nightMode .gender { color: #586e75; }
.nightMode hr#answer { border-top-color: #586e75; }
.nightMode .gloss { color: #839496; }
.nightMode .counterpart { color: #586e75; }
.nightMode .irregular { color: #586e75; }
.nightMode .confusable { color: #859900; }
.nightMode .example-ua { color: #839496; }
.nightMode .example-en { color: #586e75; }
.nightMode .note-id { color: #586e75; }
.nightMode input#typeans { color: #839496; background-color: #073642; border-color: #586e75; }
"""

UA_LEXEME_LEGACY_CSS = """\
/* Light mode (Solarized light) */
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: #586e75;
    background-color: #fdf6e3;
}

/* Dark mode (Solarized dark) */
.nightMode .card {
    color: #839496;
    background-color: #073642;
}
"""

UA_VERB_CSS = """\
/* Light mode (Solarized light) */
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: #586e75;
    background-color: #fdf6e3;
}

/* Dark mode (Solarized dark) */
.nightMode .card {
    color: #839496;
    background-color: #073642;
}
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

MODELS = {
    "B737_SV_Cloze":    SV_CLOZE_CSS,
    "B737_Systems":     B737_SYSTEMS_CSS,
    "UA_Conjugation":   UA_CONJUGATION_CSS,
    "UA_Grammar":       UA_GRAMMAR_CSS,
    "UA_Lexeme":        UA_LEXEME_CSS,
    "UA_Lexeme_Legacy": UA_LEXEME_LEGACY_CSS,
    "UA_Verb":          UA_VERB_CSS,
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
