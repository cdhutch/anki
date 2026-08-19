#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Field ORDER inside `fields:` is driven by the same FIELDS constants that drive
# the live Anki models -- one source of truth for both, rather than a second
# hand-maintained list here that drifts against them (Craig's call, 2026-08-18,
# "Option A"). Same import pattern check_cnsf_field_schema.py and
# inspect_note_type_fields.py already use for the field *set*; this extends it
# to order.
#
# Hook safety: this module runs under the `cnsf-canonical` pre-commit hook in an
# isolated venv that declares only pyyaml. The chain pulled in here --
# setup_ua_note_types -> tools.anki.sync.tsv_to_anki, and
# setup_ua_pvom_note_type -- is stdlib-only (argparse/csv/json/sys/
# urllib.request/dataclasses/pathlib/typing), so it adds no third-party
# dependency. Keep it that way: an external import anywhere in that chain would
# break the hook, not just this module.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.anki.setup.setup_ua_note_types import (  # noqa: E402
    FIELDS as _LEXEME_FIELDS,
    GRAMMAR_FIELDS as _GRAMMAR_FIELDS,
    VISUAL_FIELDS as _VISUAL_FIELDS,
    VERB_FIELDS as _VERB_FIELDS,
)
from tools.anki.setup.setup_ua_pvom_note_type import FIELDS as _PVOM_FIELDS  # noqa: E402


CANON_TOP_KEYS = [
    "schema",
    "domain",
    "note_type",
    "note_id",
    "anki",
    "tags",
    "fields",
]

CANON_ANKI_KEYS = ["model", "deck"]

# CNSF note_type -> the note type's canonical field order.
#
# Only the UA note types are listed. B737 and any other CNSF note type keep
# their existing author-order behaviour untouched (see _canonical_field_order):
# absence from this map means "don't reorder", not "reorder to empty".
#
# The CNSF key set is deliberately a SUBSET of the Anki field set -- computed
# fields (_AspectLabel, _UA_EN_DisplayLemma, _IsHomograph, _EuphonySlots,
# TypingTarget_UA) are written by the import scripts at sync time and never
# authored in CNSF, and ImperfectiveUnidirectional is sparse by decision (see
# CLAUDE.md item 17). So the goal is matching RELATIVE order of the authored
# subset, not identical lists. Any key not in the constant sorts after every
# key that is, preserving its relative order among the other unknowns -- so an
# unrecognised or experimental key is never silently dropped or shuffled
# against its neighbours, just moved to the end.
CANON_FIELD_ORDER: dict[str, list[str]] = {
    "ua_lexeme": _LEXEME_FIELDS,
    "ua_grammar": _GRAMMAR_FIELDS,
    "ua_visual": _VISUAL_FIELDS,
    "ua_verb": _VERB_FIELDS,
    "ua_pvom_infinitive": _PVOM_FIELDS,
}


def _canonical_field_order(note_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Reorder a note's `fields:` mapping to its note type's canonical order.

    Added 2026-08-18. Before this, `fields:` key order was whatever each file
    happened to be authored with, and every setdefault()-style backfill appended
    new keys wherever that file ended -- the same drift the live Anki models had
    (see sync_field_order() in setup_ua_note_types.py), just on the file side.
    A 12-note sample across ch-00/ch-08/ch-09 turned up THREE distinct orders,
    none matching the model's. cmd_check() never caught it because
    _top_level_key_order() only ever compared the seven top-level keys.

    Unknown note types pass through unchanged.
    """
    order = CANON_FIELD_ORDER.get(note_type)
    if not order:
        return fields

    out: dict[str, Any] = {}
    for k in order:
        if k in fields:
            out[k] = fields[k]
    for k in fields:  # unknown keys trail, in their original relative order
        if k not in out:
            out[k] = fields[k]
    return out

# Ukrainian apostrophe (апостроф) normalization. U+02BC MODIFIER LETTER APOSTROPHE
# is the Ukrainian National Academy's recommended character for this letter (e.g.
# м'який) -- it's a distinct letter in Ukrainian orthography, not punctuation.
# Source text sometimes has the curly single-quote apostrophe (U+2019) or a plain
# straight apostrophe (U+0027) instead. Normalize either -> U+02BC only when it
# sits directly between two Cyrillic characters, so ordinary apostrophe/quote
# punctuation in non-Ukrainian text (English possessives/contractions, quoted
# strings, etc.) is left untouched.
UA_APOSTROPHE_TARGET = "ʼ"
_UA_APOSTROPHE_SOURCE_RE = re.compile(r"(?<=[Ѐ-ӿ])['’](?=[Ѐ-ӿ])")


def normalize_ukrainian_apostrophes(text: str) -> str:
    return _UA_APOSTROPHE_SOURCE_RE.sub(UA_APOSTROPHE_TARGET, text)


def _normalize_apostrophes_recursive(obj: Any) -> Any:
    if isinstance(obj, str):
        return normalize_ukrainian_apostrophes(obj)
    if isinstance(obj, dict):
        return {k: _normalize_apostrophes_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize_apostrophes_recursive(v) for v in obj]
    return obj


@dataclass(frozen=True)
class SplitFM:
    yaml_text: str
    body_text: str


def split_frontmatter(text: str, path: Path) -> SplitFM:
    """
    Expect file to start with:
      ---
      <yaml>
      ---
    """
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter (expected leading ---).")

    # find second '---' line (front matter end)
    # Accept --- on its own line; keep everything after as body.
    m = re.search(r"(?m)^\s*---\s*$", text)
    if not m:
        raise ValueError(f"{path}: missing YAML start delimiter '---'.")

    # find end delimiter after start
    m2 = re.search(r"(?m)^\s*---\s*$", text[m.end() :])
    if not m2:
        raise ValueError(f"{path}: missing YAML end delimiter '---'.")

    start = m.end()
    end = m.end() + m2.start()
    yaml_text = text[start:end].strip("\n")
    body_text = text[m.end() + m2.end() :].lstrip("\n")
    return SplitFM(yaml_text=yaml_text, body_text=body_text)


def _top_level_key_order(yaml_text: str) -> list[str]:
    """
    Best-effort top-level key order parser (only keys at column 0).
    """
    keys: list[str] = []
    for line in yaml_text.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        # key:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
        if m:
            keys.append(m.group(1))
    return keys


def _reject_blank_lines_in_yaml(yaml_text: str, path: Path) -> None:
    """
    CNSF front matter must not contain blank lines.
    This keeps YAML deterministic and avoids non-semantic formatting drift.
    """
    for i, line in enumerate(yaml_text.splitlines(), start=1):
        if not line.strip():
            raise ValueError(
                f"{path}: blank lines are not allowed inside YAML front matter (line {i})."
            )


def _normalize_meta(meta: dict[str, Any], path: Path) -> dict[str, Any]:
    """
    Normalize known CNSF keys and coerce obvious legacy variants.
    """
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: YAML must be a mapping/object at top level.")

    # Legacy/accidental variants we’ve already seen:
    # - max8 file had stray 'source:' mapping; we fold it into fields.Source Document when possible.
    if "source" in meta and isinstance(meta.get("source"), dict):
        src = meta["source"]
        # If source.document exists and fields doesn't already provide Source Document, set it.
        doc = src.get("document")
        if doc:
            fields = meta.get("fields")
            if fields is None or not isinstance(fields, dict):
                fields = {}
                meta["fields"] = fields
            fields.setdefault("Source Document", doc)
        # remove legacy 'source'
        meta.pop("source", None)

    # Ensure schema is present and correct (do not “fix” silently)
    schema = (meta.get("schema") or "").strip()
    if schema != "cnsf/v0":
        raise ValueError(f"{path}: schema must be 'cnsf/v0' (found: {schema!r}).")

    # Enforce note_id grammar: lowercase tokens separated by hyphens or underscores
    note_id = (meta.get("note_id") or "").strip()
    if not note_id:
        raise ValueError(f"{path}: YAML must include note_id.")
    if not re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", note_id):
        raise ValueError(
            f"{path}: note_id must use lowercase letters/numbers with hyphens or underscores only: {note_id!r}"
        )

    # Normalize anki mapping
    anki = meta.get("anki")
    if anki is None:
        raise ValueError(f"{path}: YAML missing required key: anki")
    if not isinstance(anki, dict):
        raise ValueError(f"{path}: YAML key 'anki' must be a mapping/object.")
    # Require model and deck keys (again: don’t auto-invent)
    if not (anki.get("model") and anki.get("deck")):
        raise ValueError(f"{path}: anki must include 'model' and 'deck'.")

    # Normalize tags to list[str]
    tags = meta.get("tags")
    if tags is None:
        raise ValueError(f"{path}: YAML missing required key: tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValueError(f"{path}: tags must be a list of strings.")

    # Normalize fields to mapping (optional but recommended; we treat as required in CNSF v0)
    fields = meta.get("fields")
    if fields is None:
        raise ValueError(f"{path}: YAML missing required key: fields")
    if not isinstance(fields, dict):
        raise ValueError(f"{path}: fields must be a mapping/object.")
    # Optional: ensure the known field names exist (allow extensions)
    # Verification Notes uses the same field name across every note type that
    # carries it (unified 2026-08-11, per Craig -- previously UA_Verb/
    # UA_PVOM_Infinitive used an underscore-separated variant; see
    # CLAUDE-flag-audit.md for the full history). No more per-note-type
    # branching needed.
    fields.setdefault("Verification Notes", "")

    # UA_Lexeme "newer optional fields" convention (decided 2026-08-11, per
    # Craig): always-present, blank when unused -- matching how the rest of
    # the schema already works, rather than sparse-key-only. Covers the
    # per-slot euphony tolerance fields (item 16, CLAUDE.md) and the Compare/
    # Homograph/AspectCue/Mnemonic_EN fields that had drifted to sparse
    # presence across the corpus (see CLAUDE-work-queue.md "Decide the
    # convention for newer optional fields"). UA_Lexeme-specific -- these
    # keys don't exist on the other 4 note types' models at all.
    note_type = meta.get("note_type", "")
    if note_type == "ua_lexeme":
        for key in (
            "Lemma_Euphony",
            "Perfective_Euphony",
            "ImperfectiveUnidirectional_Euphony",
            "CompareA",
            "CompareB",
            "CompareC",
            "CompareD",
            "CompareScenario",
            "Homograph_SenseA",
            "Homograph_SenseB",
            "AspectCue",
            "Mnemonic_EN",
        ):
            fields.setdefault(key, "")

    # Same always-present convention extended to UA_PVOM_Infinitive's four
    # *_Euphony fields (Craig, 2026-08-18). These had drifted exactly the way
    # UA_Lexeme's optional fields had: 11 of 13 notes carried no *_Euphony key
    # at all, ua-pvom-0012 carried all four populated, and ua-pvom-0013 carried
    # all four blank -- so check_cnsf_field_schema.py reported 2/13 and the
    # Makefile kept STRICT=1 off partly because of it. Blank-when-unused, so
    # every PVOM note has the same field set.
    if note_type == "ua_pvom_infinitive":
        for key in (
            "Walking_Multi_Euphony",
            "Walking_Uni_Euphony",
            "Vehicle_Multi_Euphony",
            "Vehicle_Uni_Euphony",
        ):
            fields.setdefault(key, "")

    # Fix YAML boolean coercion in Choice fields: unquoted True/False in YAML is
    # loaded as Python bool by yaml.safe_load, then dumped as lowercase true/false.
    # Preserve the intended string value for all Choice slots.
    for choice_key in ("Choice A", "Choice B", "Choice C", "Choice D"):
        val = fields.get(choice_key)
        if isinstance(val, bool):
            fields[choice_key] = "True" if val else "False"

    # Normalize Ukrainian apostrophes (curly U+2019 -> modifier-letter U+02BC)
    # in all field content. Scoped to `fields` rather than the whole meta dict --
    # tags/note_id/model/deck are structural identifiers, not prose, so there's no
    # legitimate case for an apostrophe there.
    meta["fields"] = _normalize_apostrophes_recursive(fields)

    return meta


def canonicalize_meta(meta: dict[str, Any], path: Path) -> dict[str, Any]:
    """
    Produce a new dict with canonical key order and canonical sub-order.
    """
    meta = _normalize_meta(dict(meta), path)

    # Canonicalize nested anki order
    anki = meta.get("anki")
    assert isinstance(anki, dict)
    anki_canon: dict[str, Any] = {}
    for k in CANON_ANKI_KEYS:
        if k in anki:
            anki_canon[k] = anki[k]
    # preserve any extra anki keys after the canonical ones
    for k in anki.keys():
        if k not in anki_canon:
            anki_canon[k] = anki[k]
    meta["anki"] = anki_canon

    # Canonicalize field order within `fields:` (2026-08-18). Runs AFTER
    # _normalize_meta above, since that's where setdefault() injects the
    # always-present optional keys -- ordering before it would leave those
    # freshly-added keys stranded at the end, which is the exact drift this
    # is here to remove.
    fields = meta.get("fields")
    if isinstance(fields, dict):
        meta["fields"] = _canonical_field_order(meta.get("note_type", ""), fields)

    # Canonicalize top-level order
    out: dict[str, Any] = {}
    for k in CANON_TOP_KEYS:
        if k in meta:
            out[k] = meta[k]
    # Preserve any extension keys after canonical ones
    for k in meta.keys():
        if k not in out:
            out[k] = meta[k]

    return out


class _DQStr(str):
    """Marker subclass: force double-quoted YAML style for this string."""


class _DQDumper(yaml.SafeDumper):
    pass


def _represent_dq_str(dumper: yaml.SafeDumper, data: str):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


_DQDumper.add_representer(_DQStr, _represent_dq_str)


def _force_dquote_multiline(obj: Any) -> Any:
    """Recursively wrap any string containing an embedded newline so it always
    dumps double-quoted (with \\n escaped), never single-quoted.

    PyYAML's default representer picks single-quoted style for a multi-line
    string UNLESS the string also happens to contain a single-quote character,
    in which case it picks double-quoted instead. Single-quoted style folds
    each embedded "\\n" into a *blank physical line* on dump — which silently
    violates this module's own "no blank lines inside frontmatter" rule
    (_reject_blank_lines_in_yaml) the next time the file is parsed. Whether a
    given field's value happens to contain an apostrophe is incidental to its
    content, not a deliberate style choice, so relying on it is fragile: e.g.
    ua-lexeme-0058's ConfusableSet field (which discusses "a plumber's...
    skills") happened to dump safely only because of that apostrophe; a
    similar multi-line field without one (as several fields added during the
    2026-07-24 dedup/homograph audit were) would dump broken. Forcing
    double-quoted style for every multi-line string removes the dependency on
    incidental content and matches the byte-identical output PyYAML already
    produces for 0058 today (verified: canonicalizing 0058 with this function
    reproduces its current on-disk bytes exactly), so this is not a formatting
    change for any note already stored this way — it only fixes the cases that
    were previously silently broken.
    """
    if isinstance(obj, str):
        return _DQStr(obj) if "\n" in obj else obj
    if isinstance(obj, dict):
        return {k: _force_dquote_multiline(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_force_dquote_multiline(v) for v in obj]
    return obj


def dump_yaml(meta: dict[str, Any]) -> str:
    """
    Deterministic-ish YAML dump (order preserved, no sort_keys).
    """
    wrapped = _force_dquote_multiline(meta)
    return yaml.dump(
        wrapped,
        Dumper=_DQDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=88,
    ).strip("\n")


def canonicalized_file_text(path: Path) -> tuple[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    fm = split_frontmatter(text, path)
    _reject_blank_lines_in_yaml(fm.yaml_text, path)
    meta = yaml.safe_load(fm.yaml_text) or {}
    meta_c = canonicalize_meta(meta, path)
    y = dump_yaml(meta_c)
    new_text = f"---\n{y}\n---\n\n{fm.body_text}"
    return new_text, meta_c


def _has_field_order_drift(old_text: str, path: Path) -> bool:
    """True when the only-or-also-wrong thing is `fields:` key order.

    Compares the file's authored key order against what _canonical_field_order()
    would produce for the SAME key set -- deliberately not against the full
    constant, so a note that's merely missing an optional key isn't reported as
    an ordering problem. Best-effort: any parse failure returns False and the
    caller falls back to the generic drift message.
    """
    try:
        fm = split_frontmatter(old_text, path)
        meta = yaml.safe_load(fm.yaml_text)
        fields = meta.get("fields")
        if not isinstance(fields, dict):
            return False
        authored = list(fields.keys())
        return authored != list(_canonical_field_order(meta.get("note_type", ""), fields))
    except Exception:
        return False


def cmd_check(paths: list[Path]) -> int:
    bad = 0
    for p in paths:
        new_text, _ = canonicalized_file_text(p)
        old_text = p.read_text(encoding="utf-8")
        if new_text != old_text:
            # specifically detect “order drift” at top-level
            fm = split_frontmatter(old_text, p)
            old_order = _top_level_key_order(fm.yaml_text)
            if old_order != [k for k in CANON_TOP_KEYS if k in old_order]:
                print(f"FAIL (YAML order drift): {p}")
            elif _has_field_order_drift(old_text, p):
                # Distinguished from generic canonicalization drift (2026-08-18)
                # so the fix is obvious from the message alone: field-order
                # drift is always resolved by --write and never needs a content
                # decision, unlike an apostrophe or boolean-coercion fix.
                print(f"FAIL (field order drift): {p}")
            else:
                print(f"FAIL (canonicalization drift): {p}")
            bad += 1
    return 1 if bad else 0


def cmd_write(paths: list[Path]) -> int:
    changed = 0
    for p in paths:
        new_text, _ = canonicalized_file_text(p)
        old_text = p.read_text(encoding="utf-8")
        if new_text != old_text:
            p.write_text(new_text, encoding="utf-8")
            print(f"FIXED: {p}")
            changed += 1
        else:
            print(f"OK: {p}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Canonicalize CNSF v0 YAML front matter (order + normalization).")
    ap.add_argument("paths", nargs="+", help="One or more CNSF .md note files")
    ap.add_argument("--check", action="store_true", help="Fail if any file would change")
    ap.add_argument("--write", action="store_true", help="Rewrite files in-place")
    args = ap.parse_args()

    if args.check == args.write:
        raise SystemExit("Choose exactly one of --check or --write.")

    paths = [Path(p) for p in args.paths if not Path(p).name.startswith("_")]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"Not found: {p}")

    rc = cmd_check(paths) if args.check else cmd_write(paths)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
