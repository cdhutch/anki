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
# Shared Solarized preamble (same across all B737 note types)
# ---------------------------------------------------------------------------

SOL_VARS = """\
/* Solarized palette */
:root {
  --sol-bg:      #fdf6e3;
  --sol-bg-alt:  #eee8d5;
  --sol-text:    #586e75;
  --sol-sub:     #93a1a1;
  --sol-border:  #93a1a1;
  --sol-accent:  #2aa198;
  --sol-acc-fg:  #fdf6e3;
  --sol-green:   #859900;
  --sol-green-bg:#eee8d5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --sol-bg:      #002b36;
    --sol-bg-alt:  #073642;
    --sol-text:    #839496;
    --sol-sub:     #586e75;
    --sol-border:  #586e75;
    --sol-accent:  #2aa198;
    --sol-acc-fg:  #002b36;
    --sol-green:   #859900;
    --sol-green-bg:#073642;
  }
}
"""

# ---------------------------------------------------------------------------
# B737_SV_Cloze
# ---------------------------------------------------------------------------

SV_CLOZE_CSS = SOL_VARS + """\
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: var(--sol-text);
    background-color: var(--sol-bg);
}

.cloze {
    font-weight: bold;
    color: var(--sol-accent);
}

.cloze-text {
    white-space: pre-line;
}
"""

# ---------------------------------------------------------------------------
# B737_Systems
# ---------------------------------------------------------------------------

B737_SYSTEMS_CSS = SOL_VARS + """\
.card {
    font-family: Arial, sans-serif;
    font-size: 16px;
    color: var(--sol-text);
    background-color: var(--sol-bg);
    max-width: 680px;
    margin: 0 auto;
    padding: 16px 20px;
    text-align: left;
}

.sys-wrap {
    line-height: 1.35;
    font-size: 16px;
}

.sys-kicker {
    color: var(--sol-sub);
    font-size: 12px;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.sys-subsystem {
    font-weight: 700;
    font-size: 18px;
    color: var(--sol-accent);
    margin-bottom: 2px;
}

.sys-topic {
    color: var(--sol-sub);
    font-size: 13px;
    margin-bottom: 10px;
}

.sys-prompt {
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 8px;
}

.sys-panel {
    color: var(--sol-sub);
    font-size: 13px;
    margin-top: 8px;
}

.sep {
    border: 0;
    border-top: 1px solid var(--sol-border);
    margin: 12px 0;
}

.block {
    margin: 10px 0;
}

.block .h {
    font-weight: 700;
    font-size: 13px;
    color: var(--sol-text);
    margin-bottom: 4px;
}

.block .body {
    color: var(--sol-text);
}

.meta-row {
    display: flex;
    gap: 10px;
    margin: 6px 0;
}

.lbl {
    min-width: 110px;
    color: var(--sol-sub);
    font-weight: 600;
}

.val {
    color: var(--sol-text);
}

.ref {
    margin-top: 8px;
}

.foot {
    margin-top: 10px;
    font-size: 12px;
}

.muted {
    color: var(--sol-sub);
}

.mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                 "Liberation Mono", "Courier New", monospace;
}

/* Tables */
table {
    border-collapse: collapse;
    margin: 8px 0;
}

th, td {
    border: 1px solid var(--sol-border);
    padding: 6px 8px;
    vertical-align: top;
}

th {
    font-weight: 700;
    background-color: var(--sol-bg-alt);
}
"""

# ---------------------------------------------------------------------------
# Ukrainian types
# ---------------------------------------------------------------------------

UA_CONJUGATION_CSS = SOL_VARS + """\
.card {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 18px;
  text-align: left;
  padding: 20px;
  line-height: 1.4;
  color: var(--sol-text);
  background-color: var(--sol-bg);
}

.lemma {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--sol-accent);
}

.subtitle {
  font-size: 16px;
  color: var(--sol-sub);
  margin-bottom: 16px;
}

.section {
  font-size: 18px;
  font-weight: 700;
  margin-top: 18px;
  margin-bottom: 8px;
  color: var(--sol-text);
}

.conj-table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 460px;
  margin-bottom: 12px;
}

.conj-table th,
.conj-table td {
  border: 1px solid var(--sol-border);
  padding: 6px 8px;
  vertical-align: top;
  color: var(--sol-text);
}

.conj-table th {
  background: var(--sol-bg-alt);
  font-weight: 600;
  text-align: left;
}

.col-person { width: 180px; }
.col-form { width: 280px; }

.note {
  margin-top: 12px;
  font-size: 16px;
  color: var(--sol-sub);
}
"""

UA_GRAMMAR_CSS = SOL_VARS + """\
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: var(--sol-text);
    background-color: var(--sol-bg);
}
"""

UA_LEXEME_CSS = SOL_VARS + """\
.card {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 18px;
  color: var(--sol-text);
  background-color: var(--sol-bg);
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

.lemma {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
  color: var(--sol-accent);
}

.perfective {
  font-size: 22px;
  color: var(--sol-sub);
  margin-bottom: 8px;
}

.pos {
  font-size: 13px;
  color: var(--sol-sub);
  font-style: italic;
  margin-bottom: 16px;
}

.gender {
  font-size: 13px;
  color: var(--sol-sub);
  margin-bottom: 4px;
}

hr#answer {
  border: none;
  border-top: 2px solid var(--sol-border);
  margin: 20px 0;
}

.gloss {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--sol-text);
}

.counterpart {
  font-size: 14px;
  color: var(--sol-sub);
  margin-top: 4px;
}

.irregular {
  font-size: 13px;
  color: var(--sol-sub);
  margin-top: 4px;
}

.confusable {
  font-size: 13px;
  color: var(--sol-green);
  margin-top: 6px;
}

.example-ua {
  font-size: 15px;
  margin-top: 14px;
  font-style: italic;
  color: var(--sol-text);
}

.example-en {
  font-size: 13px;
  color: var(--sol-sub);
  margin-top: 2px;
}

.note-id {
  font-size: 10px;
  color: var(--sol-border);
  text-align: right;
  margin-top: 16px;
}

input#typeans {
  font-size: 20px;
  font-family: system-ui, -apple-system, sans-serif;
  width: 80%;
  text-align: center;
  color: var(--sol-text);
  background-color: var(--sol-bg-alt);
  border: 1px solid var(--sol-border);
  padding: 6px;
}
"""

UA_LEXEME_LEGACY_CSS = SOL_VARS + """\
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: var(--sol-text);
    background-color: var(--sol-bg);
}
"""

UA_VERB_CSS = SOL_VARS + """\
.card {
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: var(--sol-text);
    background-color: var(--sol-bg);
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
