#!/usr/bin/env python3
"""Validate domains/ua/anki/confusable_clusters.yaml for degenerate Compare cards.

Run as a prerequisite of `make ua-lexeme` (see the ua-cluster-validate /
_ua-lexeme Makefile targets) so a bad registry edit fails loudly before it
ever reaches AnkiConnect, instead of silently shipping a Compare card with
no real distinguishing content.

The checks (all in ClusterRegistry._validate_compare_cards(), called from
validate()) catch the structural failure modes actually seen in production
on 2026-08-31, none of which need semantic judgment to detect:

  - An identical-lemma cluster (a true homophone) missing sentence-mode
    data (example_ua/meaning_en) on some member -- silently falls back to
    chip mode, rendering the same spelling twice with nothing to
    distinguish it. This is the original "chips but no scenario" bug this
    registry design exists to prevent.
  - Empty compare_scenario on a chip-mode cluster member.
  - Two or more members of the same chip-mode cluster sharing byte-
    identical compare_scenario text -- caught за́мок/замо́к, тепло́/те́пло,
    and гла́дкий/гладки́й, all copy-pasted boilerplate regardless of the
    exact wording used.
  - compare_scenario text that contains one of the cluster's own lemma
    strings verbatim -- gives away the answer instead of describing a
    situation (caught вража́ючий/дивови́жний, which named the word in
    parentheses right next to its own definition).

What this deliberately does NOT catch: whether a scenario is *good* --
correctly targeted, free of typos, actually distinguishing in a subtle
synonym pair. That needs a human or an LLM-assisted review pass, not a
fast deterministic gate. See ancient-synonyms in the registry for a case
that was flagged by hand rather than "fixed" here, because there wasn't a
non-fabricated rule to author a scenario around.

Usage:
    python tools/anki/sync/validate_clusters.py [--registry PATH]

Exit code 0: no errors. Warnings (pending-sourcing notices, etc.) print to
             stderr but don't block anything.
Exit code 1: one or more errors found -- sync should not proceed.
Exit code 2: registry file missing or malformed (can't even load it).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.lib.confusable_clusters import ClusterRegistry  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", default=None, help="Path to confusable_clusters.yaml (default: repo standard location)")
    args = ap.parse_args()

    try:
        registry = ClusterRegistry(registry_path=args.registry)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: could not load cluster registry: {e}", file=sys.stderr)
        return 2

    errors, warnings, _missing_tags = registry.validate()

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} Compare-card validation error(s) in {registry.registry_path}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(
            "\nFix these in confusable_clusters.yaml before syncing -- each one "
            "means a Compare card will render with no real distinguishing "
            "content. See this script's module docstring for what each check "
            "means and what it deliberately doesn't catch.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(registry.clusters)} cluster(s) validated, no Compare-card defects found", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
