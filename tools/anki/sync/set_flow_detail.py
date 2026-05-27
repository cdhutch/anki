#!/usr/bin/env python3
"""set_flow_detail.py — Suspend detailed flow cards by stage.

Suspend logic (per flow):
    type:flow AND flow:<name>                          → suspend
    type:flow AND flow:<name> AND flow_detail:keep     → unsuspend (exempt)
    type:flow AND flow:<name> AND always_show          → never suspended

Stage definitions
-----------------
Stage 1 — Hide all flows (except always_show / flow_detail:keep)
    Active flows: none

Add flows to FLOW_STAGES as study progresses, e.g.:
    2: ["preflight", "before_start"]

Use --all --stage N to apply across every flow:<name> tag in Anki.
Use --flow <name> --stage N to target a single flow.

Usage:
    python tools/anki/sync/set_flow_detail.py --all --stage 1
    python tools/anki/sync/set_flow_detail.py --all --stage 1 --dry-run
    python tools/anki/sync/set_flow_detail.py --flow preflight --stage 1
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

# Each entry lists the *additional* flows activated at that stage.
# Stage 1 activates nothing — all flows are hidden except always_show.
FLOW_STAGES: dict[int, list[str]] = {
    1: [],
    # 2: ["preflight", "before_start"],
    # 3: [...],
}


def active_flows(stage: int) -> set[str]:
    """Return the set of flow names that should be unsuspended at *stage*."""
    flows: set[str] = set()
    for s in range(1, stage + 1):
        flows.update(FLOW_STAGES.get(s, []))
    return flows


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


def all_flow_names(url: str = ANKI_URL) -> list[str]:
    """Return sorted list of flow names by inspecting Anki's tag list."""
    all_tags: list[str] = anki_request("getTags", url=url) or []
    names = [
        tag[len("flow:"):] for tag in all_tags
        if tag.startswith("flow:") and tag != "flow:"
    ]
    return sorted(set(names))


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def apply_flow_detail_filter(flow: str, stage: int, dry_run: bool) -> None:
    tag_flow = f"flow:{flow}"
    flow_is_active = flow in active_flows(stage)

    if flow_is_active:
        # Unsuspend: flow is active at this stage — reveal non-always_hide cards
        to_suspend: list[int] = []
        to_unsuspend = find_cards(
            f"tag:type:flow tag:{tag_flow} -tag:always_hide"
        )
    else:
        # Suspend: flow is inactive — hide all except always_show / flow_detail:keep
        to_suspend = find_cards(
            f"tag:type:flow tag:{tag_flow} -tag:flow_detail:keep -tag:always_show"
        )
        to_unsuspend = find_cards(
            f"tag:type:flow tag:{tag_flow} tag:flow_detail:keep"
        )

    status = "ACTIVE  " if flow_is_active else "INACTIVE"
    print(f"  [{status}]  flow:{flow}")
    print(f"               suspend {len(to_suspend):>4}  unsuspend {len(to_unsuspend):>4}")

    if dry_run:
        return

    suspend_cards(to_suspend)
    unsuspend_cards(to_unsuspend)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suspend/unsuspend flow cards by stage; exempt always_show and flow_detail:keep."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Discover all flow:<name> tags in Anki and apply filter to each.",
    )
    group.add_argument(
        "--flow",
        metavar="NAME",
        help="Apply filter to a single named flow (e.g. preflight).",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=sorted(FLOW_STAGES.keys()),
        required=True,
        help="Flow study stage. Stage 1 hides all flows except always_show.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without making changes.",
    )
    args = parser.parse_args()

    try:
        if args.all:
            flows = all_flow_names()
            if not flows:
                print("No flow:<name> tags found in Anki.")
                sys.exit(0)
            print(f"{'DRY RUN — ' if args.dry_run else ''}Flow detail filter — "
                  f"stage {args.stage} — {len(flows)} flow(s):")
            for flow in flows:
                apply_flow_detail_filter(flow=flow, stage=args.stage, dry_run=args.dry_run)
        else:
            print(f"{'DRY RUN — ' if args.dry_run else ''}Flow detail filter — "
                  f"stage {args.stage}:")
            apply_flow_detail_filter(flow=args.flow, stage=args.stage, dry_run=args.dry_run)

        print(f"\n{'DRY RUN complete.' if args.dry_run else 'Done.'}")

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: Cannot reach AnkiConnect — is Anki running? ({exc})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
