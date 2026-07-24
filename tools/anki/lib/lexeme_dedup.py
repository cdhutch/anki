"""
tools/anki/lib/lexeme_dedup.py

Corpus-wide dedup/homograph enforcement for UA_Lexeme note authoring.

Every candidate lemma considered during vocabulary sourcing falls into one
of three buckets (see CLAUDE.md "Vocabulary dedup & homograph handling"):

  1. No existing note has this spelling         -> brand new note.
  2. A note exists but with an UNRELATED meaning -> homograph: create a new
     note, cross-link both via ConfusableSet, tag both `homograph:true`.
  3. A note exists with the SAME meaning         -> true duplicate: do not
     create a new note; instead attach the new chapter reference to the
     existing note.

This module is meant to be imported by the per-batch generator scripts used
to author each new subchapter, so that dedup/homograph handling is a normal
part of note creation rather than a separate manual step. The standalone
CLI tool `tools/anki/inspect/check_lexeme_dedup.py` re-uses the read-only
primitives here (`strip_stress`, `split_frontmatter`, `load_index`) instead
of duplicating them.

Note: functions here only ever mutate the in-memory `fields`/`tags`
structures or write plain (non-canonical) YAML. As with every other CNSF
generator/patch script in this repo, run
`python -m tools.anki.cnsf_canonicalize --write <files>` after using this
module, before presenting/committing the result.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

import yaml

COMBINING_ACUTE = "́"

Decision = Literal["duplicate", "homograph"]


# ─────────────────────────────────────────────────────────────────────────────
# Stress-stripping (NFD-decompose, drop U+0301 only, recompose NFC)
# ─────────────────────────────────────────────────────────────────────────────


def strip_stress(s: str) -> str:
    """Remove stress marks only. Naive Mn-category stripping is WRONG here:
    it also destroys letters like й/ї that decompose under NFD. Only the
    combining acute (U+0301) should be removed."""
    decomposed = unicodedata.normalize("NFD", s)
    stripped = decomposed.replace(COMBINING_ACUTE, "")
    return unicodedata.normalize("NFC", stripped)


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter parsing
# ─────────────────────────────────────────────────────────────────────────────


def split_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block's raw text, or None if absent/malformed."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


# ─────────────────────────────────────────────────────────────────────────────
# Corpus index
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class LexemeRecord:
    note_id: str
    path: Path
    lemma: str
    gloss: str
    tags_ch: str
    pos: str
    tags: list[str] = field(default_factory=list)
    confusable_set: str = ""


def load_index(root: Path) -> dict[str, list[LexemeRecord]]:
    """Map stress-stripped Lemma -> list of LexemeRecord (usually len 1)."""
    index: dict[str, list[LexemeRecord]] = {}
    for path in sorted(Path(root).rglob("ua-lexeme-*.md")):
        text = path.read_text(encoding="utf-8")
        yaml_text = split_frontmatter(text)
        if yaml_text is None:
            continue
        doc = yaml.safe_load(yaml_text) or {}
        fields_ = doc.get("fields", {}) or {}
        lemma = fields_.get("Lemma", "")
        if not lemma:
            continue
        key = strip_stress(lemma)
        index.setdefault(key, []).append(
            LexemeRecord(
                note_id=fields_.get("NoteID", path.stem),
                path=path,
                lemma=lemma,
                gloss=fields_.get("EN_Gloss", ""),
                tags_ch=fields_.get("Tags_Ch", ""),
                pos=fields_.get("PartOfSpeech", ""),
                tags=list(doc.get("tags", []) or []),
                confusable_set=fields_.get("ConfusableSet", "") or "",
            )
        )
    return index


def lookup(lemma: str, index: dict[str, list[LexemeRecord]]) -> list[LexemeRecord]:
    """Exact-spelling (stress-stripped) lookup. Empty list if no match."""
    return index.get(strip_stress(lemma), [])


# ─────────────────────────────────────────────────────────────────────────────
# Decision enforcement
# ─────────────────────────────────────────────────────────────────────────────


class DedupError(Exception):
    """Base class for dedup/homograph resolution failures."""


class AmbiguousMatch(DedupError):
    """A match was found but no dedup_decision was given to resolve it."""

    def __init__(self, lemma: str, matches: list[LexemeRecord]):
        self.lemma = lemma
        self.matches = matches
        existing = "; ".join(f"{m.note_id} \"{m.gloss}\"" for m in matches)
        super().__init__(
            f"'{lemma}' already exists in the corpus ({existing}). "
            "Pass dedup_decision='duplicate' (same meaning — no new note) or "
            "dedup_decision='homograph' (unrelated meaning — new note, cross-linked)."
        )


class InconsistentDecision(DedupError):
    """dedup_decision doesn't match what the corpus actually contains."""


@dataclass
class DedupResolution:
    action: Literal["created", "linked_duplicate", "created_homograph"]
    note_id: str
    path: Path
    linked_note_ids: list[str] = field(default_factory=list)
    message: str = ""


def require_decision(
    lemma: str,
    index: dict[str, list[LexemeRecord]],
    decision: Decision | None,
) -> list[LexemeRecord]:
    """Validate `decision` against reality; return the matches (possibly empty).

    Raises AmbiguousMatch if a match exists and no decision was supplied.
    Raises InconsistentDecision if decision was supplied but doesn't fit
    (e.g. 'duplicate'/'homograph' with no match, or a match found with no
    way to treat it as brand-new).
    """
    matches = lookup(lemma, index)
    if matches and decision is None:
        raise AmbiguousMatch(lemma, matches)
    if not matches and decision is not None:
        raise InconsistentDecision(
            f"dedup_decision={decision!r} was given for '{lemma}', but no existing "
            "note has this spelling — nothing to link against. Omit dedup_decision "
            "for brand-new vocabulary."
        )
    return matches


# ─────────────────────────────────────────────────────────────────────────────
# Pure patch helpers (fields/tags in -> fields/tags out; no file I/O)
# ─────────────────────────────────────────────────────────────────────────────


def patch_duplicate(
    fields: dict,
    tags: list[str],
    *,
    new_chapter_tag: str,
    reuse_context: str,
    today: str | None = None,
) -> tuple[dict, list[str]]:
    """Attach a new chapter occurrence to an EXISTING note (bucket 3).

    `new_chapter_tag` — e.g. "ch:2.9.3"
    `reuse_context`    — short human phrase for the Verification Notes line,
                          e.g. "ch.9.3 ('outdoor gear')"
    """
    fields = dict(fields)
    tags = list(tags)

    if new_chapter_tag not in tags:
        tags.append(new_chapter_tag)

    existing_tags_ch = [t.strip() for t in (fields.get("Tags_Ch") or "").split(",") if t.strip()]
    if new_chapter_tag not in existing_tags_ch:
        existing_tags_ch.append(new_chapter_tag)
    fields["Tags_Ch"] = ", ".join(existing_tags_ch)

    today = today or date.today().isoformat()
    note_line = (
        f"Reused in {reuse_context} — same lemma, no new note created per the "
        f"whole-corpus dedup rule; added {new_chapter_tag} tag. ({today})"
    )
    existing_note = fields.get("Verification Notes") or ""
    fields["Verification Notes"] = (
        f"{existing_note}\n{note_line}".strip() if existing_note else note_line
    )

    return fields, tags


def build_homograph_confusable_text(other_lemma: str, other_gloss: str) -> str:
    return f"{other_lemma} — homograph, unrelated meaning: \"{other_gloss}\""


def patch_homograph_link(
    fields: dict,
    tags: list[str],
    *,
    other_lemma: str,
    other_gloss: str,
) -> tuple[dict, list[str]]:
    """Cross-link a note to a newly-discovered homograph partner (bucket 2).

    Appends (does not overwrite) ConfusableSet so any pre-existing
    near-synonym note there is preserved, and ensures `homograph:true` is
    tagged.
    """
    fields = dict(fields)
    tags = list(tags)

    link_text = build_homograph_confusable_text(other_lemma, other_gloss)
    existing_cs = (fields.get("ConfusableSet") or "").strip()
    if link_text not in existing_cs:
        fields["ConfusableSet"] = f"{existing_cs}; {link_text}" if existing_cs else link_text

    if "homograph:true" not in tags:
        tags.append("homograph:true")

    return fields, tags


# ─────────────────────────────────────────────────────────────────────────────
# File-level wrappers
# ─────────────────────────────────────────────────────────────────────────────


def _load_note(path: Path) -> tuple[dict, list[str]]:
    text = path.read_text(encoding="utf-8")
    yaml_text = split_frontmatter(text)
    if yaml_text is None:
        raise ValueError(f"{path}: not a valid CNSF file (missing YAML frontmatter)")
    doc = yaml.safe_load(yaml_text) or {}
    return doc, doc.get("fields", {}) or {}


def _write_note(path: Path, doc: dict) -> None:
    rendered = yaml.dump(doc, allow_unicode=True, sort_keys=False, width=100)
    path.write_text(f"---\n{rendered}---\n", encoding="utf-8")


def apply_duplicate_to_file(
    path: Path,
    *,
    new_chapter_tag: str,
    reuse_context: str,
    dry_run: bool = False,
) -> None:
    doc, fields_ = _load_note(path)
    tags = list(doc.get("tags", []) or [])
    new_fields, new_tags = patch_duplicate(
        fields_, tags, new_chapter_tag=new_chapter_tag, reuse_context=reuse_context
    )
    doc["fields"] = new_fields
    doc["tags"] = new_tags
    if not dry_run:
        _write_note(path, doc)


def apply_homograph_to_file(
    path: Path,
    *,
    other_lemma: str,
    other_gloss: str,
    dry_run: bool = False,
) -> None:
    doc, fields_ = _load_note(path)
    tags = list(doc.get("tags", []) or [])
    new_fields, new_tags = patch_homograph_link(
        fields_, tags, other_lemma=other_lemma, other_gloss=other_gloss
    )
    doc["fields"] = new_fields
    doc["tags"] = new_tags
    if not dry_run:
        _write_note(path, doc)


# ─────────────────────────────────────────────────────────────────────────────
# High-level entry point for generator scripts
# ─────────────────────────────────────────────────────────────────────────────


def create_or_link_lexeme(
    *,
    index: dict[str, list[LexemeRecord]],
    lemma: str,
    new_note_path: Path,
    new_note_doc: dict,
    chapter_tag: str,
    reuse_context: str,
    dedup_decision: Decision | None = None,
    target_note_id: str | None = None,
    dry_run: bool = False,
) -> DedupResolution:
    """The single call generator scripts should make instead of blindly
    writing a new lexeme file.

    - No match, dedup_decision=None            -> creates new_note_path as-is.
    - Match(es), dedup_decision='duplicate'     -> does NOT create a new file;
      patches the existing note (tags/Tags_Ch/Verification Notes) instead.
      If more than one existing match exists, `target_note_id` must select
      which one.
    - Match(es), dedup_decision='homograph'     -> creates new_note_path
      (auto-tagged/cross-linked), and reciprocally patches every existing
      match's ConfusableSet + homograph:true tag.
    - Any mismatch between reality and dedup_decision raises DedupError
      (AmbiguousMatch / InconsistentDecision) before anything is written.
    """
    matches = require_decision(lemma, index, dedup_decision)

    if not matches:
        if not dry_run:
            new_note_path.parent.mkdir(parents=True, exist_ok=True)
            _write_note(new_note_path, new_note_doc)
        return DedupResolution(
            action="created",
            note_id=new_note_doc.get("fields", {}).get("NoteID", new_note_path.stem),
            path=new_note_path,
        )

    if dedup_decision == "duplicate":
        if len(matches) > 1 and target_note_id is None:
            ids = ", ".join(m.note_id for m in matches)
            raise InconsistentDecision(
                f"'{lemma}' matches {len(matches)} existing notes ({ids}) — "
                "pass target_note_id to select which one to reuse."
            )
        target = matches[0] if target_note_id is None else next(
            (m for m in matches if m.note_id == target_note_id), None
        )
        if target is None:
            raise InconsistentDecision(f"target_note_id={target_note_id!r} not among matches for '{lemma}'")
        apply_duplicate_to_file(
            target.path,
            new_chapter_tag=chapter_tag,
            reuse_context=reuse_context,
            dry_run=dry_run,
        )
        return DedupResolution(
            action="linked_duplicate",
            note_id=target.note_id,
            path=target.path,
            linked_note_ids=[target.note_id],
        )

    # dedup_decision == "homograph"
    new_gloss = new_note_doc.get("fields", {}).get("EN_Gloss", "")
    new_lemma_field = new_note_doc.get("fields", {}).get("Lemma", lemma)
    doc = dict(new_note_doc)
    doc["fields"] = dict(doc.get("fields", {}))
    doc["tags"] = list(doc.get("tags", []) or [])
    for match in matches:
        doc["fields"], doc["tags"] = patch_homograph_link(
            doc["fields"], doc["tags"], other_lemma=match.lemma, other_gloss=match.gloss
        )
        apply_homograph_to_file(
            match.path,
            other_lemma=new_lemma_field,
            other_gloss=new_gloss,
            dry_run=dry_run,
        )
    if not dry_run:
        new_note_path.parent.mkdir(parents=True, exist_ok=True)
        _write_note(new_note_path, doc)
    return DedupResolution(
        action="created_homograph",
        note_id=doc["fields"].get("NoteID", new_note_path.stem),
        path=new_note_path,
        linked_note_ids=[m.note_id for m in matches],
    )
