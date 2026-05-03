#!/usr/bin/env python3
"""set_flow_detail.py — Suspend detailed flow cards, preserve kept ones.

Suspend logic (per flow):
    type:flow AND flow:<name>          → suspend
    type:flow AND flow:<name>
        AND flow_detail:keep           → unsuspend (exempt)

Supported flows (via --flow argument):
    preflight

Usage:
    python tools/anki/sync/set_flow_detail.py --flow preflight
    python tools/anki/sync/set_flow_detail.py --flow preflight --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANKI_URL = "http://127.0.0.1:8765"

SUPPORTED_FLOWS = ["preflight"]

# ---------------------------------------------------------------------------
# AnkiConnect
# ---------------------------------------------------------------------------

def anki_request(action: str, params: dict | None = None, url: str = ANKI_URL) -> Any:
    payload = {"action": action, "version": 6, "params": params or {}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error [{action}]: {data['error']}")
    return data.get("result")


def find_cards(query: str) -> list[int]:
    return anki_request("findCards", {"query": query}) or []


def suspend_cards(card_ids: list[int]) -> None:
    if card_ids:
        anki_request("suspend", {"cards": card_ids})


def unsuspend_cards(card_ids: list[int]) -> None:
    if card_ids:
        anki_request("unsuspend", {"cards": card_ids})


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def apply_flow_detail_filter(flow: str, dry_run: bool) -> None:
    tag_flow = f"flow:{flow}"

    # Cards to suspend: type:flow + flow:<name>, no keep exemption
    to_suspend = find_cards(
        f"tag:type:flow tag:{tag_flow} -tag:flow_detail:keep"
    )

    # Cards to unsuspend: type:flow + flow:<name> + keep exemption
    to_unsuspend = find_cards(
        f"tag:type:flow tag:{tag_flow} tag:flow_detail:keep"
    )

    print(f"\nFlow filter: {tag_flow}")
    print(f"  Cards to suspend  : {len(to_suspend)}")
    print(f"  Cards to unsuspend: {len(to_unsuspend)}")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        if to_suspend:
            print(f"  Would suspend  : {to_suspend}")
        if to_unsuspend:
            print(f"  Would unsuspend: {to_unsuspend}")
        return

    if to_suspend:
        suspend_cards(to_suspend)
        print(f"  Suspended  {len(to_suspend)} card(s).")
    if to_unsuspend:
        unsuspend_cards(to_unsuspend)
        print(f"  Unsuspended {len(to_unsuspend)} card(s).")

    print("Done.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suspend detailed flow cards; exempt flow_detail:keep cards."
    )
    parser.add_argument(
        "--flow",
        required=True,
        choices=SUPPORTED_FLOWS,
        help="Which flow to apply the filter to.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without making changes.",
    )
    args = parser.parse_args()

    try:
        apply_flow_detail_filter(flow=args.flow, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: Cannot reach AnkiConnect — is Anki running? ({exc})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
