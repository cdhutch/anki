#!/usr/bin/env python3
"""verify_stress_goroh.py — Stress verification against Горох Словозміна.

Verifies stress marks in ALL stored inflected forms (Lemma, IrregularForms,
CounterpartForm, Perfective) against the Горох Словозміна paradigm tables.

Handles variable stress: some Ukrainian words accept stress on multiple
syllables. These are flagged 'variable' rather than 'mismatch' so you can
choose which variant to use in the card.

After Яблуко Level 1, the textbook omits stress marks — Горох becomes the
sole authoritative source, so this tool is essential for all subsequent
batches.

── Workflow ──────────────────────────────────────────────────────────────────

  Step 1 — extract (Python):
    python tools/anki/inspect/verify_stress_goroh.py \\
        --extract --out-dir /tmp/goroh

    Writes:
      goroh_input.json    — all forms to verify
      goroh_fetch.js      — Chrome JS snippet; paste in DevTools console
                            OR run automatically via Claude in Chrome MCP

  Step 2 — fetch (Chrome):
    Paste goroh_fetch.js into Chrome console.
    It fetches all Горох pages and downloads goroh_cache.json automatically.
    (Or Claude in Chrome MCP can run it directly.)

  Step 3 — compare (Python):
    python tools/anki/inspect/verify_stress_goroh.py \\
        --compare /tmp/goroh/goroh_cache.json --out-dir /tmp/goroh

    Writes goroh_mismatches.tsv with columns:
      note_id, lemma, field, slot, stored, goroh, status, correction

    Status values:
      ok              — stress matches exactly
      monosyllable    — single vowel; stress trivially correct
      variable_ok     — matches one of multiple valid Горох variants
      variable        — Горох has multiple variants; stored form is one of them
                        (needs human choice of canonical form)
      mismatch        — stress differs; 'goroh' column shows correct form
      variable_mismatch — stored form doesn't match any Горох variant
      not_found       — bare form not found anywhere in Горох paradigm
      no_cache        — Горох page was not fetched for this lemma
      fetch_error     — Горох returned an error for this lemma

  Step 4 — review:
    Open goroh_mismatches.tsv. For rows with status 'mismatch',
    'variable_mismatch', or 'variable', fill in the 'correction' column
    with the form you want to store. Leave blank to keep as-is.

  Step 5 — apply (Python):
    python tools/anki/inspect/verify_stress_goroh.py \\
        --apply /tmp/goroh/goroh_mismatches.tsv [--dry-run]

    For each note where ALL forms are now verified:
      - applies field corrections from the 'correction' column
      - removes 'stress:unverified' tag
      - sets Source_Note to 'verified YYYY-MM-DD via Горох'

  Step 6 — reimport:
    python -m tools.anki.cnsf_canonicalize --write \\
        domains/ua/anki/notes/lexemes/yabluko-l1/vstup/*.md
    python tools/anki/sync/ua_lexeme_import.py \\
        domains/ua/anki/notes/lexemes/yabluko-l1/vstup/
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
NOTES_DIR = REPO_ROOT / "domains" / "ua" / "anki" / "notes"

STRESS = "́"          # U+0301 COMBINING ACUTE ACCENT
APOSTROPHE = "ʼ"      # U+02BC MODIFIER LETTER APOSTROPHE
VOWELS = set("аеєиіїоуюяАЕЄИІЇОУЮЯ")

# ── Stress utilities ──────────────────────────────────────────────────────────

def strip_stress(s: str) -> str:
    return s.replace(STRESS, "")


def vowel_count(word: str) -> int:
    return sum(1 for c in word if c in VOWELS)


def stressed_vowel_index(word: str) -> int | None:
    """0-based index of the stressed vowel among vowels only, or None if unstressed."""
    v_idx = 0
    for i, c in enumerate(word):
        if c in VOWELS:
            if i + 1 < len(word) and word[i + 1] == STRESS:
                return v_idx
            v_idx += 1
    return None


def normalize_bare(s: str) -> str:
    """Strip stress marks, apostrophes, and lowercase for bare comparison.

    Strips both U+02BC (MODIFIER LETTER APOSTROPHE, used in our notes) and
    ASCII apostrophe (used by Горох and left after _clean_form processing) so
    that e.g. stored ``компʼютер`` matches Горох's ``компютер``.
    """
    s = strip_stress(s)
    s = s.replace(APOSTROPHE, "").replace("'", "")
    return s.lower().strip()


def compare_stress(stored: str, goroh_candidates: list[str]) -> tuple[str, str]:
    """
    Compare a stored stressed form against one or more Горох candidates.

    Returns (status, detail):
      ok              exact match
      monosyllable    ≤1 vowel; stress position trivially correct
      variable_ok     matches one of multiple valid variants
      variable        Горох lists multiple variants; stored is one of them
                      but the user should pick the canonical form explicitly
      mismatch        stress differs from the single Горох form
      variable_mismatch stored form doesn't match any Горох variant
      not_found       bare form absent from all Горох candidates
    """
    stored_bare = normalize_bare(stored)
    matching = [g for g in goroh_candidates if normalize_bare(g) == stored_bare]

    if not matching:
        return "not_found", ""

    if vowel_count(stored) <= 1:
        return "monosyllable", matching[0]

    stored_idx = stressed_vowel_index(stored)
    matches_idx = [g for g in matching if stressed_vowel_index(g) == stored_idx]

    if matches_idx:
        if len(matching) > 1:
            # Check whether all candidates share the same stress position.
            # Горох often lists both a capitalised and a lowercase form
            # (Ку́хар / ку́хар) — that is not genuine variable stress.
            unique_positions = {stressed_vowel_index(g) for g in matching}
            if len(unique_positions) == 1:
                return "ok", matches_idx[0]
            # Multiple valid positions in Горох; ours is one of them —
            # surface as 'variable' so the user can confirm the choice
            return "variable", " / ".join(matching)
        return "ok", matches_idx[0]

    # Stress differs
    if len(matching) > 1:
        return "variable_mismatch", " / ".join(matching)
    return "mismatch", matching[0]


# ── Горох paradigm parsing (from Chrome JS output) ───────────────────────────

def parse_goroh_paradigm(rows: list[list[str]], all_forms: list[str]) -> dict[str, list[str]]:
    """
    Build slot → [stressed_form, ...] from Горох JS output.

    rows: [[case_short, cell1, cell2, ...], ...]  (case already mapped to
          'nom'/'gen' etc. by the JS)
    all_forms: flat list of every stressed token on the page (fallback)

    Slots: nom.sg, gen.sg, dat.sg, acc.sg, ins.sg, loc.sg, voc.sg,
           nom.pl, gen.pl, dat.pl, acc.pl, ins.pl, loc.pl, voc.pl,
           all_forms (always present as catch-all)
    """
    VALID_CASES = {"nom", "gen", "dat", "acc", "ins", "loc", "voc"}
    paradigm: dict[str, list[str]] = {}

    for row in rows:
        if not row or len(row) < 2:
            continue
        case_short = row[0].strip().lower()
        if case_short not in VALID_CASES:
            continue
        forms_raw = [c.strip() for c in row[1:] if c.strip()]
        # Column 0 = sg, column 1 = pl (standard noun/adj layout)
        # For adjectives Горох may return 4 gender columns; we still take
        # col 0 as sg and col 1+ as additional forms
        for i, raw in enumerate(forms_raw):
            for variant in _split_variants(raw):
                if i == 0:
                    _push(paradigm, f"{case_short}.sg", variant)
                elif i == 1:
                    _push(paradigm, f"{case_short}.pl", variant)
                # All forms go into the catch-all
                _push(paradigm, "all_forms", variant)

    # Merge the allForms list from JS (catches forms the table parser missed)
    for raw in all_forms:
        for variant in _split_variants(raw):
            _push(paradigm, "all_forms", variant)

    return paradigm


def _split_variants(s: str) -> list[str]:
    """Split 'форма1 / форма2' into separate forms; skip empty."""
    return [x.strip() for x in re.split(r"\s*/\s*|\s*,\s*", s) if x.strip()]


def _push(d: dict, key: str, value: str):
    if value:
        d.setdefault(key, [])
        if value not in d[key]:
            d[key].append(value)


# ── Note field parsers ────────────────────────────────────────────────────────

def parse_irregular_forms(value: str) -> list[tuple[str, str]]:
    """
    Extract (slot, form) pairs from an IrregularForms string.
    e.g. "gen.pl. вікон (zero ending)" → [("gen.pl", "вікон")]
         "gen.sg. вечора (stem vowel і→о)" → [("gen.sg", "вечора")]
    """
    UA_WORD = r"[а-яА-ЯіІїЇєЄʼʼ́\-]+"
    pattern = rf"\b((?:gen|dat|acc|ins|loc|nom|voc)\.(?:sg|pl))\.\s+({UA_WORD})"
    return [(m.group(1), m.group(2)) for m in re.finditer(pattern, value)]


def parse_counterpart_forms(value: str) -> list[tuple[str, str]]:
    """
    Extract (gender, form) pairs from a CounterpartForm string.
    e.g. "f: воді́йка" → [("f", "воді́йка")]
         "f: вчи́телька / учи́телька" → [("f", "вчи́телька"), ("f", "учи́телька")]
    """
    m = re.match(r"^([mfn]):\s+(.+)$", value.strip())
    if not m:
        return []
    gender, rest = m.group(1), m.group(2)
    return [(gender, form) for form in _split_variants(rest)]


# ── Note extraction ───────────────────────────────────────────────────────────

def extract_note_targets(path: Path) -> dict | None:
    """
    Parse a CNSF note and return all forms that need stress verification.
    Returns None if the note has no stress:unverified tag.
    """
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None

    if "stress:unverified" not in (meta.get("tags") or []):
        return None

    fields = meta.get("fields") or {}

    def fv(k: str) -> str:
        v = fields.get(k)
        return str(v).strip() if v else ""

    lemma = fv("Lemma")
    if not lemma:
        return None

    bare_lemma = strip_stress(lemma)
    targets: list[dict] = []

    # 1. Primary lemma — nom.sg for nouns/adj, infinitive for verbs
    if " " not in bare_lemma:  # skip phrases
        targets.append({
            "field": "Lemma",
            "form": lemma,
            "bare": bare_lemma,
            "slot": "nom.sg",
            "lookup_lemma": bare_lemma,
        })

    # 2. IrregularForms
    irr = fv("IrregularForms")
    if irr:
        for slot, form in parse_irregular_forms(irr):
            targets.append({
                "field": "IrregularForms",
                "form": form,
                "bare": strip_stress(form),
                "slot": slot,
                "lookup_lemma": bare_lemma,  # verify within primary lemma's paradigm
            })

    # 3. CounterpartForm — each form is its own lemma on Горох
    cpart = fv("CounterpartForm")
    if cpart:
        for _gender, form in parse_counterpart_forms(cpart):
            bare_form = strip_stress(form)
            if " " not in bare_form:
                targets.append({
                    "field": "CounterpartForm",
                    "form": form,
                    "bare": bare_form,
                    "slot": "nom.sg",
                    "lookup_lemma": bare_form,
                })

    # 4. Perfective infinitive (verbs only) — separate Горох lookup
    perf = fv("Perfective")
    if perf:
        bare_perf = strip_stress(perf)
        if " " not in bare_perf and bare_perf != bare_lemma:
            targets.append({
                "field": "Perfective",
                "form": perf,
                "bare": bare_perf,
                "slot": "nom.sg",
                "lookup_lemma": bare_perf,
            })

    if not targets:
        return None

    return {
        "note_file": str(path.relative_to(REPO_ROOT)),
        "note_id": meta.get("note_id", ""),
        "lemma": lemma,
        "pos": fv("PartOfSpeech"),
        "targets": targets,
    }


# ── Chrome JS template ────────────────────────────────────────────────────────

# The Словозміна URL path encoded as unicode escapes so the JS string
# is pure ASCII and safe to embed in any context.
_SLOVOZMINA = "\\u0421\\u043b\\u043e\\u0432\\u043e\\u0437\\u043c\\u0456\\u043d\\u0430"

# ── Python HTTP fetch (no Chrome required) ───────────────────────────────────

def _clean_form(s: str) -> str:
    """Strip phonetic markers per CLAUDE.md rules."""
    s = re.sub(r"[`':ʼ]", "", s)   # backtick, ASCII apostrophe, colon, U+02BC (phonetic)
    s = s.replace("{дз}", "дз").replace("{дж}", "дж")
    return s.strip()


def parse_goroh_html(html: str) -> dict:
    """
    Parse a Горох Словозміна HTML page into the same structure the Chrome JS
    produces: {rows: [[case_short, cell1, cell2, ...], ...], allForms: [...], notFound: bool}

    Uses only stdlib (no BeautifulSoup required).
    """
    import html as html_module

    # Strip <sup>...</sup> with all content (footnote markers)
    html = re.sub(r"<sup[^>]*>[\s\S]*?</sup>", "", html, flags=re.IGNORECASE)

    UA_CASES = {
        "Називний": "nom", "Родовий": "gen", "Давальний": "dat",
        "Знахідний": "acc", "Орудний": "ins", "Місцевий": "loc", "Кличний": "voc",
    }

    rows: list[list[str]] = []
    all_forms: list[str] = []
    seen_forms: set[str] = set()

    for tr_m in re.finditer(r"<tr[^>]*>([\s\S]*?)</tr>", html, re.IGNORECASE):
        cells = []
        for td_m in re.finditer(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>",
                                 tr_m.group(1), re.IGNORECASE):
            text = re.sub(r"<[^>]+>", "", td_m.group(1))
            text = _clean_form(html_module.unescape(text))
            cells.append(text)

        if len(cells) < 2:
            continue

        # Case row?
        case_key = next((k for k in UA_CASES if cells[0].startswith(k)), None)
        if case_key:
            rows.append([UA_CASES[case_key]] + cells[1:])

        # Collect stressed tokens for the fallback list
        for cell in cells:
            for tok in re.split(r"[\s,/]+", cell):
                tok = tok.strip()
                if STRESS in tok and tok not in seen_forms:
                    all_forms.append(tok)
                    seen_forms.add(tok)

    # ── Full-page scan ────────────────────────────────────────────────────────
    # Strip all HTML tags and collect every Ukrainian token with U+0301.
    # This catches invariable words (adverbs, particles) whose stressed form
    # appears in the page heading or intro text but not in a declension table.
    body = re.sub(r"<[^>]+>", " ", html)
    body = html_module.unescape(body)
    for tok in re.split(r"[\s,/()\[\]«»\"'`]+", body):
        tok = tok.strip(".;:!?—–")
        if STRESS in tok and tok not in seen_forms and re.search(r"[а-яА-ЯіІїЇєЄ]", tok):
            all_forms.append(tok)
            seen_forms.add(tok)

    return {
        "rows": rows,
        "allForms": all_forms,
        "notFound": len(rows) == 0 and len(all_forms) == 0,
    }


def goroh_url(bare_lemma: str, section: str = "Словозміна") -> str:
    """
    Build a Горох URL for a bare (unstressed) lemma.

    section: "Словозміна" (default, declension table) or "Тлумачення" (definition,
             used as fallback for invariable/compound words absent from Словозміна).

    Converts U+02BC (MODIFIER LETTER APOSTROPHE) to ASCII apostrophe so that
    words like компʼютер and сімʼя resolve correctly on goroh.pp.ua.
    """
    from urllib.parse import quote
    _path = quote(section, safe="")
    lemma_for_url = bare_lemma.replace(APOSTROPHE, "'")
    return f"https://goroh.pp.ua/{_path}/{quote(lemma_for_url, safe='')}"


def cmd_fetch(lemmas: list[str], out_dir: Path, delay: float = 0.15):
    """
    Fetch all Горох Словозміна pages using Python urllib (no Chrome needed).
    Writes goroh_cache.json in the same format expected by --compare.
    """
    import time
    import urllib.request

    # ANSI colours (no external deps; degrade gracefully if not a tty)
    _tty = sys.stdout.isatty()
    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if _tty else text
    GREEN  = "32"
    YELLOW = "33"
    RED    = "31"
    DIM    = "2"

    results: dict = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ua-anki-stress-verify/1.0)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "uk,en-US;q=0.9",
    }

    counts = {"ok": 0, "not_found": 0, "error": 0}
    not_found_lemmas: list[str] = []
    error_lemmas: list[tuple[str, str]] = []
    width = len(str(len(lemmas)))
    print(f"Fetching {len(lemmas)} Горох pages…\n")

    for i, lemma in enumerate(lemmas):
        url = goroh_url(lemma)
        n = f"{i + 1:{width}}/{len(lemmas)}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            parsed = parse_goroh_html(html)
            results[lemma] = {"data": parsed, "error": None}

            if parsed.get("notFound"):
                # Тлумачення fallback: covers invariable/compound words absent
                # from Словозміна (e.g. медбрат, some adverbs)
                tlum_url = goroh_url(lemma, section="Тлумачення")
                try:
                    req2 = urllib.request.Request(tlum_url, headers=headers)
                    with urllib.request.urlopen(req2, timeout=12) as resp2:
                        html2 = resp2.read().decode("utf-8", errors="replace")
                    parsed2 = parse_goroh_html(html2)
                except Exception:
                    parsed2 = {"rows": [], "allForms": [], "notFound": True}

                if not parsed2.get("notFound"):
                    results[lemma] = {"data": parsed2, "error": None,
                                      "source": "Тлумачення"}
                    counts["ok"] += 1
                    paradigm2 = parse_goroh_paradigm(parsed2.get("rows", []),
                                                     parsed2.get("allForms", []))
                    nom_sg2 = paradigm2.get("nom.sg", [])
                    preview2 = " / ".join(nom_sg2[:2]) if nom_sg2 else \
                               (paradigm2.get("all_forms", [""])[0])
                    hint2 = f"→ {preview2}" if preview2 else "(via Тлумачення)"
                    CYAN = "36"
                    print(f"  {n}  {_c('~', CYAN)}  {lemma}  "
                          f"{_c(hint2, DIM)}  {_c('(Тлумачення)', CYAN)}")
                else:
                    counts["not_found"] += 1
                    not_found_lemmas.append(lemma)
                    print(f"  {n}  {_c('?', YELLOW)}  {lemma}  {_c('(not found)', DIM)}")
            else:
                counts["ok"] += 1
                paradigm = parse_goroh_paradigm(parsed.get("rows", []),
                                                parsed.get("allForms", []))
                # Show nom.sg (primary citation form), or first allForms token
                nom_sg = paradigm.get("nom.sg", [])
                preview = " / ".join(nom_sg[:2]) if nom_sg else \
                          (paradigm.get("all_forms", [""])[0])
                hint = f"→ {preview}" if preview else f"({len(parsed.get('allForms', []))} forms)"
                print(f"  {n}  {_c('✓', GREEN)}  {lemma}  {_c(hint, DIM)}")

        except Exception as e:
            results[lemma] = {"data": None, "error": str(e)}
            counts["error"] += 1
            error_lemmas.append((lemma, str(e)))
            print(f"  {n}  {_c('✗', RED)}  {lemma}  {_c(str(e), RED)}")

        if delay and i < len(lemmas) - 1:
            time.sleep(delay)

    cache_path = out_dir / "goroh_cache.json"
    cache_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    n_ok  = counts["ok"]
    n_nf  = counts["not_found"]
    n_err = counts["error"]
    bar   = "─" * 50
    print()
    print(bar)
    print(f"  {_c(f'✓ {n_ok:>3} fetched', GREEN)}")
    if n_nf:
        print(f"  {_c(f'? {n_nf:>3} not found', YELLOW)}")
        for w in not_found_lemmas:
            print(f"      {_c(w, YELLOW)}")
    if n_err:
        print(f"  {_c(f'✗ {n_err:>3} errors', RED)}")
        for w, msg in error_lemmas:
            print(f"      {_c(w, RED)}  {_c(msg, DIM)}")
    print(bar)
    print(f"Wrote: {cache_path}")
    return cache_path


GOROH_JS_TEMPLATE = """\
// goroh_fetch.js — auto-generated by verify_stress_goroh.py --extract
//
// Paste this into Chrome DevTools console on any page.
// Fetches all Горох Словозміна pages and downloads goroh_cache.json.
//
// Lemmas: {n_lemmas} unique lookups in {n_batches} batches of 25.

(async () => {{
  const LEMMAS = {lemma_json};
  const BATCH = 25;
  const STRESS = "\\u0301";
  const UA_CASES = {{
    "\\u041d\\u0430\\u0437\\u0438\\u0432\\u043d\\u0438\\u0439": "nom",  // Називний
    "\\u0420\\u043e\\u0434\\u043e\\u0432\\u0438\\u0439":         "gen",  // Родовий
    "\\u0414\\u0430\\u0432\\u0430\\u043b\\u044c\\u043d\\u0438\\u0439": "dat",  // Давальний
    "\\u0417\\u043d\\u0430\\u0445\\u0456\\u0434\\u043d\\u0438\\u0439": "acc",  // Знахідний
    "\\u041e\\u0440\\u0443\\u0434\\u043d\\u0438\\u0439":          "ins",  // Орудний
    "\\u041c\\u0456\\u0441\\u0446\\u0435\\u0432\\u0438\\u0439":   "loc",  // Місцевий
    "\\u041a\\u043b\\u0438\\u0447\\u043d\\u0438\\u0439":          "voc",  // Кличний
  }};

  function cleanHtml(html) {{
    return html
      .replace(/<sup[\\s\\S]*?<\\/sup>/gi, "")   // strip footnote markers with content
      .replace(/[`':\\u02BC]/g, "")               // strip phonetic punctuation
      .replace(/\\u007b\\u0434\\u0437\\u007d/g, "\\u0434\\u0437")  // {{дз}} → дз
      .replace(/\\u007b\\u0434\\u0436\\u007d/g, "\\u0434\\u0436"); // {{дж}} → дж
  }}

  function parseParadigm(html) {{
    const clean = cleanHtml(html);
    const doc = new DOMParser().parseFromString(clean, "text/html");

    // Extract case table rows
    const rows = [];
    doc.querySelectorAll("table tr").forEach(tr => {{
      const cells = Array.from(tr.querySelectorAll("td, th"))
                         .map(c => c.textContent.trim());
      if (cells.length < 2) return;
      const caseShort = Object.entries(UA_CASES)
                              .find(([k]) => cells[0].startsWith(k));
      if (caseShort) rows.push([caseShort[1], ...cells.slice(1)]);
    }});

    // Collect every stressed token on the page as a fallback
    const allForms = new Set();
    doc.querySelectorAll("td").forEach(td => {{
      td.textContent.trim().split(/[\\s,]+/).forEach(tok => {{
        if (tok.includes(STRESS)) allForms.add(tok);
      }});
    }});

    // Detect "not found" pages (Горох redirects or shows no table)
    const notFound = rows.length === 0 && allForms.size === 0;

    return {{ rows, allForms: [...allForms], notFound }};
  }}

  const results = {{}};
  for (let i = 0; i < LEMMAS.length; i += BATCH) {{
    const batch = LEMMAS.slice(i, i + BATCH);
    await Promise.all(batch.map(async lemma => {{
      try {{
        const url = `https://goroh.pp.ua/{slovozmina}/${{encodeURIComponent(lemma)}}`;
        const r = await fetch(url);
        if (!r.ok) {{
          results[lemma] = {{ data: null, error: `HTTP ${{r.status}}` }};
          return;
        }}
        results[lemma] = {{ data: parseParadigm(await r.text()), error: null }};
      }} catch(e) {{
        results[lemma] = {{ data: null, error: e.message }};
      }}
    }}));
    console.log(`Batch ${{Math.floor(i / BATCH) + 1}} / {n_batches} done`);
  }}

  // Download as goroh_cache.json
  const blob = new Blob([JSON.stringify(results, null, 2)],
                        {{ type: "application/json" }});
  const a = Object.assign(document.createElement("a"),
                          {{ href: URL.createObjectURL(blob),
                             download: "goroh_cache.json" }});
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  console.log("\\u2713 goroh_cache.json downloaded (" + LEMMAS.length + " lemmas)");
  return results;
}})();
"""


# ── Extract mode ──────────────────────────────────────────────────────────────

def cmd_extract(out_dir: Path):
    note_files = sorted(NOTES_DIR.rglob("ua-lexeme-*.md"))
    notes = []
    all_lookup_lemmas: set[str] = set()

    for path in note_files:
        result = extract_note_targets(path)
        if result:
            notes.append(result)
            for t in result["targets"]:
                all_lookup_lemmas.add(t["lookup_lemma"])

    # Exclude phrases and empty strings
    lookup_lemmas = sorted(l for l in all_lookup_lemmas if l and " " not in l)
    n_batches = (len(lookup_lemmas) + 24) // 25

    input_path = out_dir / "goroh_input.json"
    js_path = out_dir / "goroh_fetch.js"

    input_path.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lemma_json = json.dumps(lookup_lemmas, ensure_ascii=False)
    js_path.write_text(
        GOROH_JS_TEMPLATE.format(
            lemma_json=lemma_json,
            n_lemmas=len(lookup_lemmas),
            n_batches=n_batches,
            slovozmina=_SLOVOZMINA,
        ),
        encoding="utf-8",
    )

    print(f"Notes with stress:unverified : {len(notes)}")
    print(f"Unique Горох lookups          : {len(lookup_lemmas)}")
    print(f"Batches (25 per batch)        : {n_batches}")
    print(f"\nWrote: {input_path}")
    print(f"Wrote: {js_path}")
    print("\nNext steps (choose one):")
    print("  A) Python fetch (recommended — no Chrome needed):")
    print(f"       python verify_stress_goroh.py --fetch --out-dir {out_dir}")
    print("  B) Chrome DevTools (fallback):")
    print("       See GOROH_VERIFICATION.md for instructions")
    print(f"  Then: python verify_stress_goroh.py --compare {out_dir}/goroh_cache.json \\")
    print(f"             --out-dir {out_dir}")

    return lookup_lemmas


# ── Compare mode ──────────────────────────────────────────────────────────────

def cmd_compare(cache_path: Path, out_dir: Path):
    raw_cache = json.loads(cache_path.read_text(encoding="utf-8"))

    # Build paradigm index: bare_lemma → slot → [stressed_form, ...]
    paradigm_index: dict[str, dict[str, list[str]]] = {}
    fetch_errors: set[str] = set()
    goroh_not_found: set[str] = set()   # successfully fetched but Горох has no entry

    for bare, entry in raw_cache.items():
        if entry.get("error"):
            fetch_errors.add(bare)
            paradigm_index[bare] = {}
            continue
        data = entry.get("data") or {}
        if data.get("notFound"):
            goroh_not_found.add(bare)
            paradigm_index[bare] = {}
            continue
        paradigm_index[bare] = parse_goroh_paradigm(
            data.get("rows", []),
            data.get("allForms", []),
        )

    input_path = out_dir / "goroh_input.json"
    if not input_path.exists():
        print(f"Missing {input_path} — run --extract first", file=sys.stderr)
        sys.exit(1)
    notes = json.loads(input_path.read_text(encoding="utf-8"))

    counts = {"ok": 0, "monosyllable": 0, "variable": 0, "variable_ok": 0,
              "mismatch": 0, "variable_mismatch": 0,
              "not_found": 0, "no_cache": 0, "fetch_error": 0}
    rows_out: list[dict] = []

    for note in notes:
        for t in note["targets"]:
            lookup = t["lookup_lemma"]
            slot = t["slot"]
            stored = t["form"]

            if lookup in fetch_errors:
                status, goroh_detail = "fetch_error", ""
            elif lookup not in paradigm_index:
                status, goroh_detail = "no_cache", ""
            elif vowel_count(stored) <= 1:
                # Monosyllables: Горох omits stress marks from the base form, so
                # it never appears in allForms and compare_stress would return
                # not_found falsely.  If the page was fetched successfully, stress
                # of a monosyllabic form is trivially correct.
                if lookup in goroh_not_found:
                    status, goroh_detail = "not_found", ""
                else:
                    status, goroh_detail = "monosyllable", ""
            else:
                paradigm = paradigm_index[lookup]
                # Try exact slot, fall back to all_forms
                candidates = (paradigm.get(slot) or []) + [
                    f for f in paradigm.get("all_forms", [])
                    if f not in (paradigm.get(slot) or [])
                ]
                status, goroh_detail = compare_stress(stored, candidates)

            counts[status] = counts.get(status, 0) + 1

            # Populate correction column automatically for clear mismatches
            auto_correction = ""
            if status == "mismatch":
                auto_correction = goroh_detail
            elif status == "variable_mismatch":
                auto_correction = goroh_detail  # user must choose

            rows_out.append({
                "note_id": note["note_id"],
                "lemma": note["lemma"],
                "pos": note["pos"],
                "field": t["field"],
                "slot": slot,
                "stored": stored,
                "goroh": goroh_detail,
                "status": status,
                "correction": auto_correction,
            })

    out_path = out_dir / "goroh_mismatches.tsv"
    fieldnames = ["note_id", "lemma", "pos", "field", "slot",
                  "stored", "goroh", "status", "correction"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        w.writerows(rows_out)

    # Summary
    total = sum(counts.values())
    print(f"\nVerification summary ({total} forms across {len(notes)} notes):")
    for status, n in sorted(counts.items(), key=lambda x: -x[1]):
        if n:
            print(f"  {status:<22} {n:>4}")

    action_needed = counts.get("mismatch", 0) + counts.get("variable_mismatch", 0) \
                  + counts.get("variable", 0)
    print(f"\nAction needed: {action_needed} forms")
    print(f"Wrote: {out_path}")
    if action_needed:
        print("\nReview goroh_mismatches.tsv:")
        print("  mismatch / variable_mismatch — fill 'correction' with the correct form")
        print("  variable — Горох accepts both stress positions; pick your canonical form")
        print("  not_found — check spelling; leave 'correction' blank to keep as-is")


# ── Apply mode ────────────────────────────────────────────────────────────────

def cmd_apply(mismatches_path: Path, dry_run: bool):
    with mismatches_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    # Build per-note picture: all statuses + any corrections
    by_note: dict[str, dict] = {}
    for r in rows:
        nid = r["note_id"]
        if nid not in by_note:
            by_note[nid] = {"rows": [], "all_ok": True}
        by_note[nid]["rows"].append(r)
        # A note is "all ok" if every form is ok/monosyllable/variable_ok
        # OR has a correction that resolves it
        status = r["status"]
        correction = r.get("correction", "").strip()
        needs_action = status in ("mismatch", "variable_mismatch", "variable",
                                  "not_found", "no_cache", "fetch_error")
        if needs_action and not correction:
            by_note[nid]["all_ok"] = False

    today = date.today().isoformat()
    applied_notes = 0

    for nid, info in by_note.items():
        corrections = [r for r in info["rows"]
                       if r.get("correction", "").strip()
                       and r["correction"].strip() != r["stored"].strip()]

        # Find note file
        matches = list(NOTES_DIR.rglob(f"{nid}.md"))
        if not matches:
            print(f"  WARN: {nid}.md not found", file=sys.stderr)
            continue
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        changed = False

        for fix in corrections:
            field = fix["field"]
            stored = fix["stored"]
            correction = fix["correction"].strip()

            if field == "Lemma":
                new_text = _set_field(text, "Lemma", correction)
                # Update TypingAnswer: lemma without stress marks
                new_text = _set_field(new_text, "TypingAnswer", strip_stress(correction))
                # Update Source_URL if it was based on the old bare lemma
                new_url = f"https://goroh.pp.ua/Словозміна/{strip_stress(correction)}"
                new_text = _set_field(new_text, "Source_URL", new_url)
                text = new_text
                changed = True
            elif field in ("IrregularForms", "CounterpartForm"):
                text = text.replace(stored, correction, 1)
                changed = True
            elif field == "Perfective":
                text = _set_field(text, "Perfective", correction)
                changed = True

        # Remove stress:unverified and update Source_Note if all forms resolved
        if info["all_ok"]:
            text = _remove_tag(text, "stress:unverified")
            # Distinguish notes where some forms were confirmed-as-is (not in Горох)
            confirmed_not_found = [
                r for r in info["rows"]
                if r["status"] == "not_found"
                and r.get("correction", "").strip() == r["stored"].strip()
            ]
            if confirmed_not_found:
                forms_str = ", ".join(r["stored"] for r in confirmed_not_found)
                source_note = (f"verified {today} via Горох "
                               f"(stress confirmed by derivation: {forms_str})")
            else:
                source_note = f"verified {today} via Горох"
            text = _set_field(text, "Source_Note", source_note)
            changed = True

        if changed:
            if dry_run:
                summary = [f"{r['stored']} → {r['correction']}" for r in corrections]
                tags_note = " + remove stress:unverified" if info["all_ok"] else ""
                print(f"  DRY {nid}: {', '.join(summary) or '(tag only)'}{tags_note}")
            else:
                path.write_text(text, encoding="utf-8")
                summary = [f"{r['stored']} → {r['correction']}" for r in corrections]
                tags_note = " ✓ stress:unverified removed" if info["all_ok"] else ""
                print(f"  FIX {nid}: {', '.join(summary) or '(tag only)'}{tags_note}")
                applied_notes += 1

    if not dry_run:
        print(f"\nPatched {applied_notes} notes.")
        if applied_notes:
            print("Next:")
            print("  make ua-batch-fix BATCH=yabluko-l1/ch-00")
            print("  make ua-batch     BATCH=yabluko-l1/ch-00")


# ── Low-level text patching ───────────────────────────────────────────────────

def _set_field(text: str, field: str, value: str) -> str:
    """Replace the value of a YAML field inside the fields: block."""
    needs_quoting = any(c in value for c in (":", "#", "[", "]", "/"))
    if needs_quoting or not value:
        replacement = rf"  {field}: '{value}'"
    else:
        replacement = rf"  {field}: {value}"
    pattern = rf"^  {re.escape(field)}:.*$"
    new_text, n = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if n == 0:
        raise ValueError(f"Field '{field}' not found in note")
    return new_text


def _remove_tag(text: str, tag: str) -> str:
    """Remove a tag line from the YAML tags list."""
    pattern = rf"^\s*- {re.escape(tag)}\n"
    return re.sub(pattern, "", text, flags=re.MULTILINE)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Verify stress marks against Горох Словозміна.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--extract", action="store_true",
                       help="Extract targets; write goroh_input.json + goroh_fetch.js")
    group.add_argument("--fetch", action="store_true",
                       help="Fetch Горох pages with Python urllib (no Chrome needed); "
                            "writes goroh_cache.json. Run --extract first.")
    group.add_argument("--compare", metavar="GOROH_CACHE",
                       help="Compare notes against Горох cache; write goroh_mismatches.tsv")
    group.add_argument("--apply", metavar="MISMATCHES_TSV",
                       help="Apply corrections; remove stress:unverified where all forms OK")
    parser.add_argument("--out-dir", metavar="DIR", default=".",
                        help="Directory for output files (default: cwd)")
    parser.add_argument("--dry-run", action="store_true",
                        help="(--apply only) preview without writing files")
    parser.add_argument("--delay", type=float, default=0.15,
                        help="(--fetch only) seconds between requests (default: 0.15)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.extract:
        cmd_extract(out_dir)
    elif args.fetch:
        input_path = out_dir / "goroh_input.json"
        if not input_path.exists():
            print(f"Missing {input_path} — run --extract first", file=sys.stderr)
            sys.exit(1)
        notes = json.loads(input_path.read_text(encoding="utf-8"))
        all_lookup: set[str] = set()
        for note in notes:
            for t in note["targets"]:
                lk = t["lookup_lemma"]
                if lk and " " not in lk:
                    all_lookup.add(lk)
        lemmas = sorted(all_lookup)
        cache_path = cmd_fetch(lemmas, out_dir, delay=args.delay)
        print(f"\nNext: python verify_stress_goroh.py --compare {cache_path} "
              f"--out-dir {out_dir}")
    elif args.compare:
        cmd_compare(Path(args.compare), out_dir)
    elif args.apply:
        cmd_apply(Path(args.apply), args.dry_run)


if __name__ == "__main__":
    main()
