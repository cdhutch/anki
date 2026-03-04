#!/usr/bin/env python3
"""
diff_cnsf_vs_anki.py

Compare canonical CNSF notes (domains/<domain>/anki/notes/**.md) against an
Anki-extracted wide TSV (from anki_to_l3_tsv.py) and report drift.

- Canonical truth remains CNSF.
- This tool is read-only.
- Hashes are computed over (front_html + US + back_html) on both sides.
- Canonical HTML is produced by md_to_html_mmd.py which writes:
    <note_id>__front.html and <note_id>__back.html
- HTML is normalized before hashing to avoid false drift from provenance/whitespace.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

US = "\u241f"


def eprint(*args):
    print(*args, file=sys.stderr)


def sha256_short(s: str, n: int = 12) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def tsv_unescape_cell(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    # reverse of anki_to_l3_tsv.tsv_escape_cell()
    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\\\", "\\")
    return s


def normalize_html_for_hash(html: str) -> str:
    """Normalize HTML to prevent drift from trivial differences.

    We normalize away:
      - renderer provenance comments
      - platform line endings
      - TSV/pretty-print artifacts (literal '\n', leading '\ ' before tags, backslash-only lines)
      - insignificant whitespace between tags
    """
    if html is None:
        return ""
    h = str(html)

    # Remove renderer provenance comments
    h = re.sub(r"<!--\s*renderer:.*?-->", "", h, flags=re.IGNORECASE)

    # Normalize real line endings
    h = h.replace("\r\n", "\n").replace("\r", "\n")

    # Convert literal backslash-n sequences to real newlines (TSV artifacts)
    h = h.replace("\\n", "\n")

    # Drop common pretty-print prefix: "\ <tag>" at start of line
    h = re.sub(r"(?m)^\\\s+(?=<)", "", h)

    # Remove lines that are just a backslash (optionally with spaces)
    h = re.sub(r"(?m)^\s*\\\s*$", "", h)

    # Remove stray fenced-code markers
    h = re.sub(r"(?m)^\s*```\s*$", "", h)

    # Collapse whitespace between tags
    h = re.sub(r">\s+<", "><", h)

    # Collapse repeated whitespace
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n{2,}", "\n", h)

    return h.strip()


