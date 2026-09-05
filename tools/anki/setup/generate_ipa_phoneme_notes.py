#!/usr/bin/env python3
"""
Generate CNSF ipa_phoneme note files from the Round 1 phoneme reference table.

Source of truth: "Claude outputs/ipa_round1_phoneme_card.md" (Consonants /
Vowels / Nasal vowels / Diphthongs tables, English-German-French-Russian-
Ukrainian columns). This supersedes complete_phoneme_superset.yaml for
Round-1 data -- the superset had confirmed inaccuracies (phantom UA/RU
front-rounded vowels and diphthongs, a missing Russian palatalization
series) that this table does not have, since every word in it was
cross-checked against Wikipedia phonology articles.

Usage:
    python tools/anki/setup/generate_ipa_phoneme_notes.py \
        --source "Claude outputs/ipa_round1_phoneme_card.md" \
        --output domains/ipa/anki/notes/phonemes/round1 \
        --start-id 2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
try:
    from tools.anki.cnsf_canonicalize import canonicalize_meta, dump_yaml  # noqa: E402
    HAVE_CANONICALIZER = True
except Exception as exc:  # pragma: no cover
    print(f"WARNING: could not import canonicalizer ({exc}); falling back to plain yaml.dump", file=sys.stderr)
    HAVE_CANONICALIZER = False
    import yaml

    def dump_yaml(meta: Dict[str, Any]) -> str:  # type: ignore[no-redef]
        return yaml.dump(meta, allow_unicode=True, sort_keys=False, default_flow_style=False)

    def canonicalize_meta(meta: Dict[str, Any], path: Path) -> Dict[str, Any]:  # type: ignore[no-redef]
        return meta

SOURCE_LANG_COLUMNS = ["English", "German", "French", "Russian", "Ukrainian"]

# ---------------------------------------------------------------------------
# Articulation metadata
# ---------------------------------------------------------------------------
# consonants: base IPA symbol (parenthetical stripped) -> (place, manner, voicing, description)
CONSONANT_META: Dict[str, Tuple[str, str, str, str]] = {
    "p": ("bilabial", "stop", "voiceless", "Voiceless bilabial stop"),
    "b": ("bilabial", "stop", "voiced", "Voiced bilabial stop"),
    "t": ("alveolar", "stop", "voiceless", "Voiceless alveolar stop"),
    "d": ("alveolar", "stop", "voiced", "Voiced alveolar stop"),
    "k": ("velar", "stop", "voiceless", "Voiceless velar stop"),
    "ɡ": ("velar", "stop", "voiced", "Voiced velar stop"),
    "m": ("bilabial", "nasal", "voiced", "Voiced bilabial nasal"),
    "n": ("alveolar", "nasal", "voiced", "Voiced alveolar nasal"),
    "ŋ": ("velar", "nasal", "voiced", "Voiced velar nasal"),
    "ɲ": ("palatal", "nasal", "voiced", "Voiced palatal nasal"),
    "f": ("labiodental", "fricative", "voiceless", "Voiceless labiodental fricative"),
    "v": ("labiodental", "fricative", "voiced", "Voiced labiodental fricative"),
    "ʋ": ("labiodental", "approximant", "voiced", "Voiced labiodental approximant (Ukrainian в)"),
    "θ": ("dental", "fricative", "voiceless", "Voiceless dental fricative"),
    "ð": ("dental", "fricative", "voiced", "Voiced dental fricative"),
    "s": ("alveolar", "fricative", "voiceless", "Voiceless alveolar fricative"),
    "z": ("alveolar", "fricative", "voiced", "Voiced alveolar fricative"),
    "ʃ": ("postalveolar", "fricative", "voiceless", "Voiceless postalveolar fricative"),
    "ʒ": ("postalveolar", "fricative", "voiced", "Voiced postalveolar fricative"),
    "x": ("velar", "fricative", "voiceless", "Voiceless velar fricative"),
    "ç": ("palatal", "fricative", "voiceless", "Voiceless palatal fricative"),
    "h": ("glottal", "fricative", "voiceless", "Voiceless glottal fricative"),
    "ɦ": ("glottal", "fricative", "voiced", "Voiced glottal fricative"),
    "ɫ": ("alveolar", "lateral approximant", "voiced", "Voiced alveolar lateral approximant (velarized 'dark' l)"),
    "l": ("alveolar", "lateral approximant", "voiced", "Voiced alveolar lateral approximant ('clear' l)"),
    "ɹ": ("alveolar", "approximant", "voiced", "Voiced alveolar approximant (English r)"),
    "r": ("alveolar", "trill", "voiced", "Voiced alveolar trill"),
    "ʁ": ("uvular", "fricative / approximant", "voiced", "Voiced uvular fricative or approximant (German/French r)"),
    "j": ("palatal", "approximant", "voiced", "Voiced palatal approximant"),
    "ɥ": ("labial-palatal", "approximant", "voiced", "Voiced labial-palatal approximant (French)"),
    "w": ("labial-velar", "approximant", "voiced", "Voiced labial-velar approximant"),
    "ts": ("alveolar", "affricate", "voiceless", "Voiceless alveolar affricate"),
    "dz": ("alveolar", "affricate", "voiced", "Voiced alveolar affricate"),
    "tʃ": ("postalveolar", "affricate", "voiceless", "Voiceless postalveolar affricate"),
    "tɕ": ("alveolo-palatal", "affricate", "voiceless", "Voiceless alveolo-palatal affricate (Russian ч)"),
    "ɕː": ("alveolo-palatal", "fricative", "voiceless", "Long voiceless alveolo-palatal fricative (Russian щ)"),
    "dʒ": ("postalveolar", "affricate", "voiced", "Voiced postalveolar affricate"),
    "pf": ("bilabial-labiodental", "affricate", "voiceless", "Voiceless labial affricate (German)"),
    "pʲ": ("bilabial", "stop", "voiceless", "Palatalized voiceless bilabial stop (Russian)"),
    "bʲ": ("bilabial", "stop", "voiced", "Palatalized voiced bilabial stop (Russian)"),
    "tʲ": ("alveolar", "stop", "voiceless", "Palatalized voiceless alveolar stop"),
    "dʲ": ("alveolar", "stop", "voiced", "Palatalized voiced alveolar stop"),
    "kʲ": ("velar", "stop", "voiceless", "Palatalized voiceless velar stop (Russian)"),
    "ɡʲ": ("velar", "stop", "voiced", "Palatalized voiced velar stop (Russian)"),
    "fʲ": ("labiodental", "fricative", "voiceless", "Palatalized voiceless labiodental fricative (Russian)"),
    "vʲ": ("labiodental", "fricative", "voiced", "Palatalized voiced labiodental fricative (Russian)"),
    "xʲ": ("velar", "fricative", "voiceless", "Palatalized voiceless velar fricative (Russian)"),
    "mʲ": ("bilabial", "nasal", "voiced", "Palatalized voiced bilabial nasal (Russian)"),
    "sʲ": ("alveolar", "fricative", "voiceless", "Palatalized voiceless alveolar fricative"),
    "zʲ": ("alveolar", "fricative", "voiced", "Palatalized voiced alveolar fricative"),
    "nʲ": ("alveolar", "nasal", "voiced", "Palatalized voiced alveolar nasal"),
    "lʲ": ("alveolar", "lateral approximant", "voiced", "Palatalized voiced alveolar lateral approximant"),
    "rʲ": ("alveolar", "trill", "voiced", "Palatalized voiced alveolar trill"),
    "tsʲ": ("alveolar", "affricate", "voiceless", "Palatalized voiceless alveolar affricate"),
}

VOWEL_DESC: Dict[str, str] = {
    "i / iː": "Close front unrounded vowel (short and long)",
    "ɪ": "Near-close near-front unrounded vowel",
    "ɨ": "Close central unrounded vowel",
    "eː": "Close-mid front unrounded vowel (long)",
    "ɛ": "Open-mid front unrounded vowel",
    "ɛː": "Open-mid front unrounded vowel (long)",
    "a": "Open front unrounded vowel",
    "aː": "Open front unrounded vowel (long)",
    "æ": "Near-open front unrounded vowel",
    "ɑ": "Open back unrounded vowel",
    "ɔ": "Open-mid back rounded vowel",
    "ɔː": "Open-mid back rounded vowel (long)",
    "o": "Close-mid back rounded vowel",
    "u / uː": "Close back rounded vowel (short and long)",
    "ʊ": "Near-close near-back rounded vowel",
    "ʌ": "Open-mid back unrounded vowel",
    "ə": "Mid central vowel (schwa)",
    "ɐ": "Near-open central vowel",
    "ɝ": "Open-mid central unrounded vowel, rhotacized (stressed)",
    "ɚ": "Mid central vowel, rhotacized (unstressed)",
    "y / yː": "Close front rounded vowel (short and long)",
    "ʏ": "Near-close near-front rounded vowel",
    "ø / øː": "Close-mid front rounded vowel (short and long)",
    "œ": "Open-mid front rounded vowel",
}

NASAL_VOWEL_DESC: Dict[str, str] = {
    "ɑ̃": "Open back unrounded vowel, nasalized (French)",
    "ɔ̃": "Open-mid back rounded vowel, nasalized (French)",
    "ɛ̃": "Open-mid front unrounded vowel, nasalized (French)",
    "œ̃": "Open-mid front rounded vowel, nasalized (French)",
}

DIPHTHONG_DESC: Dict[str, str] = {
    "eɪ": "Closing diphthong, mid front to close front (English)",
    "oʊ": "Closing diphthong, mid back to close back (English)",
    "aɪ": "Closing diphthong, open front/central to close front",
    "aʊ": "Closing diphthong, open front/central to close back",
    "ɔɪ": "Closing diphthong, open-mid back to close front (English)",
    "ɔʏ̯": "Closing diphthong, open-mid back to close front rounded (German)",
}

SOURCE_NOTE = (
    "Cross-checked against Wikipedia's English_phonology, "
    "Standard_German_phonology, French_phonology, Russian_phonology, and "
    "Ukrainian_phonology articles; see round1_phoneme_card.md methodology "
    "notes for scope decisions (length, diphthongs, palatalization)."
)

BLANK_CELL_RE = re.compile(r"^\s*[—-]\s*$")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def clean_cell(text: str) -> str:
    """Whitespace-trimmed cell text, markdown bold stripped -- used only for
    blank/cross-reference detection, never for what actually gets stored."""
    text = BOLD_RE.sub(r"\1", text.strip())
    return text.strip()


def cell_to_html(text: str) -> str:
    """Trim whitespace and convert markdown **bold** (marking the letters
    that spell the target sound) to HTML <b> so Anki renders it as bold
    instead of showing literal asterisks."""
    text = text.strip()
    return BOLD_RE.sub(r"<b>\1</b>", text)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text


def parse_markdown_tables(md_text: str) -> Dict[str, List[List[str]]]:
    """Return {section_heading: [[cell, cell, ...], ...]} for every '## ' section
    that contains a markdown table. Rows include the header row as element 0."""
    sections: Dict[str, List[List[str]]] = {}
    current_heading: Optional[str] = None
    current_rows: List[List[str]] = []
    in_table = False

    def flush():
        nonlocal current_rows, in_table
        if current_heading and current_rows:
            sections.setdefault(current_heading, [])
            sections[current_heading] = current_rows
        current_rows = []
        in_table = False

    for line in md_text.splitlines():
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            continue
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # skip separator rows like |---|---|
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                in_table = True
                continue
            current_rows.append(cells)
        else:
            if in_table:
                # table just ended; keep collecting rows only within the same section
                pass
    flush()
    return sections


def build_examples(header: List[str], row: List[str]) -> Dict[str, str]:
    """Return {language: html_word}, keyed off the cleaned (bold-stripped)
    cell for blank/cross-reference detection, but storing the HTML version
    (bold preserved) as the value so the card can render it."""
    examples: Dict[str, str] = {}
    for col_name, raw_cell in zip(header[1:], row[1:]):
        cell = clean_cell(raw_cell)
        if not cell or BLANK_CELL_RE.match(cell):
            continue
        if "see" in cell.lower() and ("(" in cell or "\u2192" in cell or "->" in cell):
            continue
        if cell.startswith("\u2014") or cell.startswith("-"):
            continue
        examples[col_name] = cell_to_html(raw_cell)
    return examples


def format_example_words(examples: Dict[str, str]) -> str:
    """One styled block per language, in card-ready HTML: a small muted
    language label followed by the (bold-lettered) example word, large."""
    return "".join(
        f'<div class="ipa-example-line"><span class="ipa-lang">{lang}</span>{word}</div>'
        for lang, word in examples.items()
    )


def make_note(
    note_id: str,
    ipa_cell: str,
    type_: str,
    description: str,
    examples: Dict[str, str],
    place: str = "",
    manner: str = "",
    voicing: str = "",
) -> Dict[str, Any]:
    deck = f"IPA::{type_.capitalize()}s"
    phoneme_slug = slugify(description)
    fields = {
        "NoteID": note_id,
        "Phoneme": phoneme_slug,
        "IPA_Symbol": ipa_cell,
        "Type": type_,
        "Description": description,
        "Manner_of_Articulation": manner,
        "Place_of_Articulation": place,
        "Voicing": voicing,
        "Airflow": "",
        "Example_Words": format_example_words(examples),
        "Language_Analogs": "",
        "Minimal_Pairs": "",
        "Confusable_With": "",
        "Mnemonic_EN": "",
        "EN_Gloss": "",
        "Tags_Ch": "",
        "Source_URL": "",
        "Source_Note": SOURCE_NOTE,
        "Verification Notes": "",
    }
    return {
        "schema": "cnsf/v0",
        "note_type": "ipa_phoneme",
        "note_id": note_id,
        "anki": {"model": "IPA_Phoneme", "deck": deck},
        "tags": ["status:draft"],
        "fields": fields,
    }


def write_note(meta: Dict[str, Any], out_dir: Path) -> Path:
    note_id = meta["note_id"]
    path = out_dir / f"{note_id}.md"
    canon = canonicalize_meta(meta, path)
    path.write_text(f"---\n{dump_yaml(canon)}\n---\n\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Path to ipa_round1_phoneme_card.md")
    parser.add_argument("--output", required=True, help="Output directory for generated notes")
    parser.add_argument("--start-id", type=int, default=2, help="First numeric NoteID to use (default: 2)")
    args = parser.parse_args()

    source_path = Path(args.source)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_text = source_path.read_text(encoding="utf-8")
    sections = parse_markdown_tables(md_text)

    counter = args.start_id
    written: List[Path] = []
    skipped: List[str] = []

    def next_id() -> str:
        nonlocal counter
        nid = f"ipa-phoneme-{counter:04d}"
        counter += 1
        return nid

    # --- Consonants ---
    for row in sections.get("Consonants", [])[1:]:
        header = sections["Consonants"][0]
        ipa_cell = row[0].strip()
        base = re.sub(r"\s*\(.*\)\s*$", "", ipa_cell).strip()
        if base not in CONSONANT_META:
            skipped.append(f"consonant row with unmapped symbol: {ipa_cell!r}")
            continue
        place, manner, voicing, description = CONSONANT_META[base]
        examples = build_examples(header, row)
        if not examples:
            skipped.append(f"consonant {ipa_cell!r} has no examples in EN/DE/FR/RU/UA -- skipped")
            continue
        meta = make_note(next_id(), ipa_cell, "consonant", description, examples, place, manner, voicing)
        written.append(write_note(meta, out_dir))

    # --- Vowels (monophthongs) ---
    for row in sections.get("Vowels (monophthongs)", [])[1:]:
        header = sections["Vowels (monophthongs)"][0]
        ipa_cell = row[0].strip()
        description = VOWEL_DESC.get(ipa_cell)
        if description is None:
            skipped.append(f"vowel row with unmapped symbol: {ipa_cell!r}")
            continue
        examples = build_examples(header, row)
        if not examples:
            skipped.append(f"vowel {ipa_cell!r} has no examples in EN/DE/FR/RU/UA -- skipped")
            continue
        meta = make_note(next_id(), ipa_cell, "vowel", description, examples)
        written.append(write_note(meta, out_dir))

    # --- Nasal vowels (French only) ---
    for row in sections.get("Nasal vowels (French only)", [])[1:]:
        header = sections["Nasal vowels (French only)"][0]
        ipa_cell = row[0].strip()
        description = NASAL_VOWEL_DESC.get(ipa_cell)
        if description is None:
            skipped.append(f"nasal vowel row with unmapped symbol: {ipa_cell!r}")
            continue
        examples = build_examples(header, row)
        if not examples:
            skipped.append(f"nasal vowel {ipa_cell!r} has no examples -- skipped")
            continue
        meta = make_note(next_id(), ipa_cell, "vowel", description, examples)
        written.append(write_note(meta, out_dir))

    # --- Diphthongs ---
    for row in sections.get("Diphthongs", [])[1:]:
        header = sections["Diphthongs"][0]
        ipa_cell = row[0].strip()
        description = DIPHTHONG_DESC.get(ipa_cell)
        if description is None:
            skipped.append(f"diphthong row with unmapped symbol: {ipa_cell!r}")
            continue
        examples = build_examples(header, row)
        if not examples:
            skipped.append(f"diphthong {ipa_cell!r} has no examples -- skipped")
            continue
        meta = make_note(next_id(), ipa_cell, "diphthong", description, examples)
        written.append(write_note(meta, out_dir))

    print(f"Wrote {len(written)} note(s) to {out_dir}")
    for p in written:
        print(f"  {p.name}")
    if skipped:
        print(f"\nSkipped {len(skipped)} row(s):")
        for s in skipped:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
