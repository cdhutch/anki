#!/usr/bin/env python3
"""tools/anki/lib/lexeme_dedup.py — Dedup/homograph enforcement for UA_Lexeme generation.

Rebuilt 2026-07-24: an earlier version of this module (and its test suite) was
authored on a different machine and never made it into this repo/branch — see
CLAUDE.md "Vocabulary dedup & homograph handling" and CLAUDE-ch09-vocab-workflow.md
for the design this reimplementation follows. This is a from-scratch rebuild, not a
recovery of the original file.

Purpose
-------
`tools/anki/inspect/check_lexeme_dedup.py` is a *manual* pre-flight check: you run it
by hand before drafting a batch, read the report, and decide new/duplicate/homograph
yourself. This module is the same corpus-lookup logic, but wired directly into
note-generation code via `create_or_link_lexeme()` — the entry point future
`gen_ua_lexemes_*.py`-style batch scripts should call instead of writing a new
`ua-lexeme-NNNN.md` file directly.

Every candidate lemma falls into one of three buckets (CLAUDE.md "Vocabulary dedup &
homograph handling"):

  1. New       — no existing note has this spelling. Write the new note as-is.
  2. Homograph — same spelling, unrelated meaning. Write the new note (its own
     NoteID), but cross-link both notes via ConfusableSet and tag both
     `homograph:true`.
  3. Duplicate — same spelling AND same meaning, encountered again in a later
     chapter. Do NOT create a new note. Append the new chapter tag to the existing
     note's `tags` list and `Tags_Ch` field, and a dated line to
     `Verification Notes`.

`create_or_link_lexeme()` enforces that a `dedup_decision` is supplied whenever a
spelling collision exists in the corpus (bucket 2 vs. 3 is a meaning judgment call
this module cannot make — see `check_lexeme_dedup.py`'s docstring) and performs the
resulting file writes/edits.

This module intentionally reuses `tools/anki/cnsf_canonicalize.py`'s frontmatter
parsing/serialization (`split_frontmatter`, `canonicalize_meta`, `dump_yaml`) rather
than reimplementing YAML formatting, so files this module edits come out in the same
canonical shape `cnsf_canonicalize.py --check` expects — no separate "run the
canonicalizer afterward" step.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tools.anki.cnsf_canonicalize import canonicalize_meta, dump_yaml, split_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"

COMBINING_ACUTE = "́"

VALID_DECISIONS = frozenset({"new", "duplicate", "homograph"})


# ─────────────────────────────────────────────────────────────────────────────
# Errors
# ─────────────────────────────────────────────────────────────────────────────


class DedupError(Exception):
    """Raised when a candidate can't be safely processed without a human/Claude
    decision, or when the caller's inputs are inconsistent with corpus state."""


# ─────────────────────────────────────────────────────────────────────────────
# Stress stripping (same rule as check_lexeme_dedup.py / backfill_source_url.py:
# only strip the combining acute, U+0301 — naive Mn-category stripping also
# destroys letters like й/ї that decompose under NFD).
# ─────────────────────────────────────────────────────────────────────────────


def strip_stress(s: str) -> str:
    decomposed = unicodedata.normalize("NFD", s)
    stripped = decomposed.replace(COMBINING_ACUTE, "")
    return unicodedata.normalize("NFC", stripped)


# ─────────────────────────────────────────────────────────────────────────────
# Corpus index
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DedupMatch:
    note_id: str
    path: Path
    lemma: str
    gloss: str
    tags_ch: str
    pos: str


@dataclass(frozen=True)
class DedupResult:
    candidate: str
    key: str
    matches: list[DedupMatch] = field(default_factory=list)

    @property
    def has_match(self) -> bool:
        return len(self.matches) > 0


def load_corpus(lexeme_root: Path | None = None) -> dict[str, list[DedupMatch]]:
    """Map stress-stripped Lemma -> list of DedupMatch, scanning every
    ua-lexeme-*.md file under lexeme_root (whole corpus, all chapters)."""
    root = lexeme_root or DEFAULT_LEXEME_ROOT
    index: dict[str, list[DedupMatch]] = {}
    for path in sorted(root.rglob("ua-lexeme-*.md")):
        meta = _read_meta(path)
        if meta is None:
            continue
        fields = meta.get("fields", {}) or {}
        lemma = fields.get("Lemma", "")
        if not lemma:
            continue
        key = strip_stress(lemma)
        index.setdefault(key, []).append(
            DedupMatch(
                note_id=fields.get("NoteID", path.stem),
                path=path,
                lemma=lemma,
                gloss=fields.get("EN_Gloss", ""),
                tags_ch=fields.get("Tags_Ch", ""),
                pos=fields.get("PartOfSpeech", ""),
            )
        )
    return index


def check_dedup(candidate: str, index: dict[str, list[DedupMatch]]) -> DedupResult:
    key = strip_stress(candidate.strip())
    return DedupResult(candidate=candidate, key=key, matches=list(index.get(key, [])))


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter helpers (thin wrappers around cnsf_canonicalize, kept local so
# callers of this module don't need to know about the canonicalizer directly)
# ─────────────────────────────────────────────────────────────────────────────


def _read_meta(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    try:
        fm = split_frontmatter(text, path)
    except ValueError:
        return None
    doc = yaml.safe_load(fm.yaml_text) or {}
    if not isinstance(doc, dict):
        return None
    return doc


def _write_canonical(path: Path, meta: dict[str, Any], body_text: str) -> None:
    meta_c = canonicalize_meta(meta, path)
    y = dump_yaml(meta_c)
    path.write_text(f"---\n{y}\n---\n\n{body_text.lstrip(chr(10))}", encoding="utf-8")


def _parse_note_content(note_content: str, label: str) -> tuple[dict[str, Any], str]:
    """Parse a full CNSF note file's text (frontmatter + body) that a caller is
    about to write as a *new* note file. `label` is used in error messages only."""
    fake_path = Path(label)
    try:
        fm = split_frontmatter(note_content, fake_path)
    except ValueError as e:
        raise DedupError(f"note_content for {label!r} is not valid CNSF: {e}") from e
    meta = yaml.safe_load(fm.yaml_text) or {}
    if not isinstance(meta, dict):
        raise DedupError(f"note_content for {label!r}: YAML front matter must be a mapping.")
    return meta, fm.body_text


def _append_tag(meta: dict[str, Any], tag: str) -> None:
    tags = meta.setdefault("tags", [])
    if not isinstance(tags, list):
        raise DedupError(f"'tags' must be a list, found {type(tags).__name__}")
    if tag not in tags:
        tags.append(tag)


def _append_tags_ch(fields: dict[str, Any], new_chapter_tag: str) -> None:
    """Tags_Ch is a comma-separated string field, independent of the `tags` list."""
    existing = (fields.get("Tags_Ch") or "").strip()
    existing_parts = [p.strip() for p in existing.split(",") if p.strip()] if existing else []
    if new_chapter_tag not in existing_parts:
        existing_parts.append(new_chapter_tag)
    fields["Tags_Ch"] = ", ".join(existing_parts)


def _append_verification_note(fields: dict[str, Any], dated_note: str) -> None:
    existing = (fields.get("Verification Notes") or "").strip()
    if existing:
        fields["Verification Notes"] = f"{existing}\n{dated_note}"
    else:
        fields["Verification Notes"] = dated_note


def _append_confusable(fields: dict[str, Any], addition: str) -> None:
    existing = (fields.get("ConfusableSet") or "").strip()
    if not addition.strip():
        return
    if addition.strip() in existing:
        return  # already cross-linked; don't duplicate
    if existing:
        fields["ConfusableSet"] = f"{existing}\n{addition.strip()}"
    else:
        fields["ConfusableSet"] = addition.strip()


# ─────────────────────────────────────────────────────────────────────────────
# create_or_link_lexeme
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DedupOutcome:
    bucket: str  # "new" | "duplicate" | "homograph"
    written: list[Path]
    modified: list[Path]


def create_or_link_lexeme(
    candidate_lemma: str,
    note_content: str,
    new_note_path: Path,
    *,
    dedup_decision: str | None = None,
    new_chapter_tag: str | None = None,
    dated_note: str | None = None,
    homograph_confusable_new: str | None = None,
    homograph_confusable_existing: str | None = None,
    lexeme_root: Path | None = None,
    index: dict[str, list[DedupMatch]] | None = None,
) -> DedupOutcome:
    """Look up `candidate_lemma` against the whole-corpus dedup index and either
    write a new note, or edit the existing colliding note(s) in place, per the
    bucket rules in CLAUDE.md "Vocabulary dedup & homograph handling".

    Args:
        candidate_lemma: the lemma spelling to check (stress marks OK).
        note_content: full rendered CNSF text (YAML front matter, "---"-delimited)
            for the *new* note. Required for bucket "new" and "homograph"; ignored
            (may be "") for bucket "duplicate", since no new file is written.
        new_note_path: where the new note file would be written for bucket "new"/
            "homograph". Must not already exist.
        dedup_decision: None, "new", "duplicate", or "homograph". Required
            ("duplicate" or "homograph") whenever the corpus already has a
            spelling match — see DedupError below. Must NOT be "duplicate" or
            "homograph" when there is no match.
        new_chapter_tag: e.g. "ch:2.9.3" — required for "duplicate".
        dated_note: dated one-line note appended to the existing note's
            "Verification Notes" — required for "duplicate".
        homograph_confusable_new: ConfusableSet text appended to the *new* note,
            describing the pre-existing homograph(s) — required for "homograph".
        homograph_confusable_existing: ConfusableSet text appended to each
            *existing* matched note, describing the new homograph — required for
            "homograph".
        lexeme_root: corpus root to scan (defaults to the real UA lexeme corpus).
        index: a pre-built corpus index (from `load_corpus`) to reuse across many
            calls instead of rescanning the whole corpus each time.

    Returns:
        DedupOutcome(bucket, written, modified) — paths actually written/edited.

    Raises:
        DedupError on any inconsistency: missing required decision, decision that
        contradicts corpus state, missing bucket-specific arguments, malformed
        note_content, or an attempt to overwrite an existing file.
    """
    if dedup_decision is not None and dedup_decision not in VALID_DECISIONS:
        raise DedupError(
            f"dedup_decision must be one of {sorted(VALID_DECISIONS)} or None, got {dedup_decision!r}"
        )

    idx = index if index is not None else load_corpus(lexeme_root)
    result = check_dedup(candidate_lemma, idx)

    if result.has_match:
        if dedup_decision not in ("duplicate", "homograph"):
            lines = "\n".join(
                f"  {m.note_id}  ({m.pos})  {m.lemma}  — \"{m.gloss}\"  [{m.path}]"
                for m in result.matches
            )
            raise DedupError(
                f"'{candidate_lemma}' already exists in the corpus under "
                f"{len(result.matches)} note(s):\n{lines}\n"
                "A dedup_decision of 'duplicate' or 'homograph' is required — "
                "compare the intended meaning against the existing gloss(es) above "
                "before creating or linking a note. (See CLAUDE.md 'Vocabulary "
                "dedup & homograph handling'.)"
            )
    else:
        if dedup_decision == "duplicate":
            raise DedupError(
                f"dedup_decision='duplicate' but no existing note matches "
                f"'{candidate_lemma}' in the corpus — nothing to link to."
            )
        if dedup_decision == "homograph":
            raise DedupError(
                f"dedup_decision='homograph' but no existing note matches "
                f"'{candidate_lemma}' in the corpus — nothing to cross-link with."
            )

    if not result.has_match or dedup_decision == "new" or dedup_decision is None:
        return _handle_new(candidate_lemma, note_content, new_note_path)

    if dedup_decision == "duplicate":
        return _handle_duplicate(result, new_chapter_tag, dated_note)

    if dedup_decision == "homograph":
        return _handle_homograph(
            candidate_lemma,
            note_content,
            new_note_path,
            result,
            homograph_confusable_new,
            homograph_confusable_existing,
        )

    raise AssertionError("unreachable")  # pragma: no cover


def _handle_new(candidate_lemma: str, note_content: str, new_note_path: Path) -> DedupOutcome:
    if new_note_path.exists():
        raise DedupError(f"refusing to overwrite existing file: {new_note_path}")
    meta, body = _parse_note_content(note_content, str(new_note_path))
    _validate_note_id_matches_path(meta, new_note_path)
    new_note_path.parent.mkdir(parents=True, exist_ok=True)
    _write_canonical(new_note_path, meta, body)
    return DedupOutcome(bucket="new", written=[new_note_path], modified=[])


def _handle_duplicate(
    result: DedupResult,
    new_chapter_tag: str | None,
    dated_note: str | None,
) -> DedupOutcome:
    if not new_chapter_tag:
        raise DedupError("dedup_decision='duplicate' requires new_chapter_tag (e.g. 'ch:2.9.3')")
    if not dated_note:
        raise DedupError(
            "dedup_decision='duplicate' requires dated_note (a dated one-line "
            "note documenting the reuse, appended to Verification Notes)"
        )

    modified: list[Path] = []
    for match in result.matches:
        meta = _read_meta(match.path)
        if meta is None:
            raise DedupError(f"could not re-parse existing note for edit: {match.path}")
        fields = meta.setdefault("fields", {})
        _append_tag(meta, new_chapter_tag)
        _append_tags_ch(fields, new_chapter_tag)
        _append_verification_note(fields, dated_note)
        body = match.path.read_text(encoding="utf-8")
        body_text = split_frontmatter(body, match.path).body_text
        _write_canonical(match.path, meta, body_text)
        modified.append(match.path)

    return DedupOutcome(bucket="duplicate", written=[], modified=modified)


def _handle_homograph(
    candidate_lemma: str,
    note_content: str,
    new_note_path: Path,
    result: DedupResult,
    homograph_confusable_new: str | None,
    homograph_confusable_existing: str | None,
) -> DedupOutcome:
    if not homograph_confusable_new:
        raise DedupError(
            "dedup_decision='homograph' requires homograph_confusable_new (ConfusableSet "
            "text to add to the NEW note, describing the pre-existing homograph(s))"
        )
    if not homograph_confusable_existing:
        raise DedupError(
            "dedup_decision='homograph' requires homograph_confusable_existing (ConfusableSet "
            "text to append to each EXISTING matched note, describing the new homograph)"
        )
    if new_note_path.exists():
        raise DedupError(f"refusing to overwrite existing file: {new_note_path}")

    meta, body = _parse_note_content(note_content, str(new_note_path))
    _validate_note_id_matches_path(meta, new_note_path)
    fields = meta.setdefault("fields", {})
    _append_confusable(fields, homograph_confusable_new)
    _append_tag(meta, "homograph:true")
    new_note_path.parent.mkdir(parents=True, exist_ok=True)
    _write_canonical(new_note_path, meta, body)

    modified: list[Path] = []
    for match in result.matches:
        existing_meta = _read_meta(match.path)
        if existing_meta is None:
            raise DedupError(f"could not re-parse existing note for edit: {match.path}")
        existing_fields = existing_meta.setdefault("fields", {})
        _append_confusable(existing_fields, homograph_confusable_existing)
        _append_tag(existing_meta, "homograph:true")
        existing_body = match.path.read_text(encoding="utf-8")
        existing_body_text = split_frontmatter(existing_body, match.path).body_text
        _write_canonical(match.path, existing_meta, existing_body_text)
        modified.append(match.path)

    return DedupOutcome(bucket="homograph", written=[new_note_path], modified=modified)


def _validate_note_id_matches_path(meta: dict[str, Any], path: Path) -> None:
    note_id = (meta.get("note_id") or "").strip()
    fields = meta.get("fields", {}) or {}
    field_note_id = (fields.get("NoteID") or "").strip()
    expected = path.stem
    if note_id and note_id != expected:
        raise DedupError(
            f"note_content's note_id {note_id!r} does not match new_note_path stem {expected!r}"
        )
    if field_note_id and field_note_id != expected:
        raise DedupError(
            f"note_content's fields.NoteID {field_note_id!r} does not match "
            f"new_note_path stem {expected!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: next sequential NoteID (used when a generator script needs to
# mint a new ua-lexeme-NNNN before it can build note_content/new_note_path)
# ─────────────────────────────────────────────────────────────────────────────


def next_note_id(prefix: str = "ua-lexeme", lexeme_root: Path | None = None) -> str:
    root = lexeme_root or DEFAULT_LEXEME_ROOT
    max_num = 0
    for path in root.rglob(f"{prefix}-*.md"):
        suffix = path.stem[len(prefix) + 1 :]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))
    return f"{prefix}-{max_num + 1:04d}"
