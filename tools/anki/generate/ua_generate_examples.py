#!/usr/bin/env python3
"""
tools/anki/generate/ua_generate_examples.py

Populate UA_Example / EN_Example fields for UA_Lexeme notes via the Anthropic API.

Usage:
    python tools/anki/generate/ua_generate_examples.py \\
        --batch domains/ua/anki/notes/lexemes/yabluko-l1/ch-00 \\
        [--limit 10] [--dry-run] [--model claude-haiku-4-5-20251001]

Writes directly into the note .md files and adds the 'example:generated' tag.
Notes that already have UA_Example filled are skipped automatically.

Requirements:
    pip install anthropic --break-system-packages
    export ANTHROPIC_API_KEY=sk-ant-...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

APOSTROPHE = "ʼ"   # ʼ  MODIFIER LETTER APOSTROPHE (Ukrainian)
STRESS     = "́"   # combining acute accent

DEFAULT_MODEL        = "claude-haiku-4-5-20251001"
INTER_REQUEST_DELAY  = 0.3  # seconds between API calls

# ── YAML helpers ──────────────────────────────────────────────────────────────

def _yaml_scalar(value: str) -> str:
    """Return value as a single-quoted YAML scalar, escaping embedded ' by doubling."""
    return "'" + value.replace("'", "''") + "'"


def extract_field(content: str, field: str) -> str:
    """Return the decoded value of a YAML field from raw note text."""
    pat = (
        r"^\s+" + re.escape(field) + r":\s*"
        r"(?:'((?:[^']|'')*)'|\"((?:[^\\\"]|\\.)*)\"|(.*))\s*$"
    )
    m = re.search(pat, content, re.MULTILINE)
    if not m:
        return ""
    if m.group(1) is not None:
        return m.group(1).replace("''", "'")   # single-quoted: unescape ''
    if m.group(2) is not None:
        return m.group(2)                       # double-quoted
    return (m.group(3) or "").strip()           # bare


def has_example(content: str) -> bool:
    """True if UA_Example is already populated."""
    return bool(extract_field(content, "UA_Example"))


def inject_examples(content: str, ua: str, en: str) -> str:
    """
    Replace blank UA_Example and EN_Example with generated values, and add
    the 'example:generated' tag.  Safe to call if UA_Example is already set
    (replaces it), but the caller filters those out beforehand.
    """
    # Replace UA_Example (matches '', "", or bare empty)
    content = re.sub(
        r"^(\s+UA_Example:)\s*(?:''|\"\"|)\s*$",
        lambda m: f"{m.group(1)} {_yaml_scalar(ua)}",
        content, flags=re.MULTILINE,
    )
    # Replace EN_Example
    content = re.sub(
        r"^(\s+EN_Example:)\s*(?:''|\"\"|)\s*$",
        lambda m: f"{m.group(1)} {_yaml_scalar(en)}",
        content, flags=re.MULTILINE,
    )
    # Add tag (idempotent)
    if "example:generated" not in content:
        # Insert as last tag, immediately before 'fields:' line
        content = re.sub(
            r"((?:^- [^\n]+\n)+)(^fields:)",
            lambda m: m.group(1) + "- example:generated\n" + m.group(2),
            content, flags=re.MULTILINE,
        )
    return content


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a Ukrainian language assistant specialising in modern Ukrainian, \
Galician/Lviv register.

Task: write ONE short, natural example sentence (8–14 words) that demonstrates \
the given vocabulary word in context.

Rules:
1. Use modern standard Ukrainian, Galician/Lviv register. Avoid Russian-influenced \
vocabulary.
2. Apostrophe: always ʼ (U+02BC MODIFIER LETTER APOSTROPHE), never ASCII apostrophe (').
3. No stress marks: do NOT include U+0301 combining acute accent.
4. Keep the sentence simple and natural — A1-A2 learner level.
5. The target word must appear in a grammatically correct inflected form.
6. Phrases (PartOfSpeech: phrase) and interjections: use as-is in a short \
situational sentence.
7. Return ONLY a JSON object — no markdown, no explanation:
   {"ua": "...", "en": "..."}
"""


def build_user_prompt(fields: dict) -> str:
    bare  = fields.get("TypingAnswer") or fields.get("Lemma", "").replace(STRESS, "")
    pos   = fields.get("PartOfSpeech", "")
    gloss = fields.get("EN_Gloss", "")
    govt  = fields.get("Govt_Case", "").strip()
    lines = [
        f"Word: {bare}",
        f"Part of speech: {pos}",
        f"English meaning: {gloss}",
    ]
    if govt:
        lines.append(f"Government case (requires): {govt}")
    return "\n".join(lines)


# ── API call ──────────────────────────────────────────────────────────────────

def generate_example(
    client,
    fields: dict,
    model: str,
) -> tuple[str, str] | None:
    """Return (ua_sentence, en_translation) or None on error."""
    prompt = build_user_prompt(fields)
    raw = ""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip accidental markdown code fences
        raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
        data = json.loads(raw)
        ua = data.get("ua", "").strip()
        en = data.get("en", "").strip()
        if ua and en:
            return ua, en
        print(f"  WARNING: empty field(s) in response: {raw!r}", file=sys.stderr)
        return None
    except json.JSONDecodeError as exc:
        print(f"  ERROR: JSON parse failed ({exc}) — raw: {raw!r}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"  ERROR: API call failed — {exc}", file=sys.stderr)
        return None


# ── Note field parsing ────────────────────────────────────────────────────────

_NOTE_FIELDS = [
    "NoteID", "Lemma", "PartOfSpeech", "Gender", "Perfective", "EN_Gloss",
    "Govt_Case", "CounterpartForm", "IrregularForms", "VerbMotion_Pair",
    "ConfusableSet", "CrossLang_Analog", "EuphonyNote", "TypingAnswer",
    "UA_Example", "EN_Example", "Verb_Conj_Table", "Tags_Ch",
    "Source_URL", "Source_Note", "Verification Notes",
]


def parse_note_fields(content: str) -> dict:
    return {f: extract_field(content, f) for f in _NOTE_FIELDS}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate UA_Example/EN_Example via Anthropic API (Haiku)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--batch", required=True,
        help="Notes directory, absolute or relative to repo root "
             "(e.g. domains/ua/anki/notes/lexemes/yabluko-l1/ch-00)",
    )
    ap.add_argument(
        "--limit", type=int, default=10,
        help="Maximum notes to process in this run (default: 10; use 0 for all)",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Print prompts and mock responses without writing files or calling the API",
    )
    ap.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Anthropic model (default: {DEFAULT_MODEL})",
    )
    args = ap.parse_args()

    # ── Resolve batch directory ──────────────────────────────────────────────
    batch = Path(args.batch)
    if not batch.is_absolute():
        batch = REPO_ROOT / batch
    if not batch.exists():
        sys.exit(f"ERROR: batch directory not found: {batch}")

    # ── Collect pending notes ────────────────────────────────────────────────
    all_notes = sorted(batch.glob("ua-lexeme-*.md"))
    pending   = [p for p in all_notes
                 if not has_example(p.read_text(encoding="utf-8"))]

    limit      = args.limit if args.limit > 0 else len(pending)
    to_process = pending[:limit]

    print(f"{len(pending)} notes need examples  ({len(all_notes)} total in batch)")
    print(f"Processing {len(to_process)}  (--limit {limit})\n")

    if not to_process:
        print("Nothing to do.")
        return

    # ── Set up Anthropic client ──────────────────────────────────────────────
    if not args.dry_run:
        try:
            import anthropic
        except ImportError:
            sys.exit(
                "ERROR: anthropic package not installed.\n"
                "Run: pip install anthropic --break-system-packages"
            )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            sys.exit("ERROR: ANTHROPIC_API_KEY environment variable not set")
        client = anthropic.Anthropic(api_key=api_key)
    else:
        client = None

    # ── Process ──────────────────────────────────────────────────────────────
    n_ok = n_err = 0
    width = len(str(len(to_process)))

    for i, path in enumerate(to_process, 1):
        content = path.read_text(encoding="utf-8")
        fields  = parse_note_fields(content)
        note_id = fields.get("NoteID", path.stem)
        lemma   = fields.get("Lemma", "?")

        print(f"[{i:{width}}/{len(to_process)}] {note_id}  {lemma}")

        if args.dry_run:
            print(f"  (dry-run) prompt:\n    " +
                  build_user_prompt(fields).replace("\n", "\n    "))
            n_ok += 1
            continue

        result = generate_example(client, fields, args.model)
        if result is None:
            n_err += 1
            continue

        ua, en = result
        print(f"  UA: {ua}")
        print(f"  EN: {en}")

        updated = inject_examples(content, ua, en)
        path.write_text(updated, encoding="utf-8")
        n_ok += 1

        if i < len(to_process):
            time.sleep(INTER_REQUEST_DELAY)

    # ── Summary ──────────────────────────────────────────────────────────────
    label = "dry-run" if args.dry_run else "written"
    print(f"\nDone: {n_ok} {label}, {n_err} errors")

    if pending[limit:]:
        print(f"{len(pending) - limit} notes still pending — run again to continue")

    if n_ok and not args.dry_run:
        rel = batch.relative_to(REPO_ROOT / "domains/ua/anki/notes/lexemes")
        print(f"\nNext: reimport\n  make ua-batch BATCH={rel}")


if __name__ == "__main__":
    main()
