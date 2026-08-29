#!/usr/bin/env python3
"""Compute (or record) the incremental sync scope for one UA note type.

Default sync behaviour for all `make ua-*` targets is now incremental: only
notes that changed since the last successful sync for that note type are
sent to AnkiConnect. At full-corpus scale (~25 chapters), always resyncing
everything turned a few-minute sync into something like half an hour; most
runs only actually touch a handful of files.

State: one file per note type under .anki_sync_state/ (gitignored -- this
tracks progress against *your* local Anki collection, not repo content, so
it shouldn't be committed and doesn't carry over between machines) holding
the git commit SHA current as of the last successful sync.

Two subcommands:

    list    Print the files (relative to repo root) that need syncing, one
            per line: the union of (a) every file changed in a commit since
            the recorded baseline, and (b) every currently dirty/untracked
            file under --root right now (so edits made after the last
            commit, or never committed at all, are never missed). Deleted
            files are reported to stderr, not stdout -- removing the
            corresponding Anki note isn't handled by the import scripts, so
            this is surfaced for you to deal with by hand.

            Exit code 0 with output: sync exactly these files.
            Exit code 0, no output: nothing changed -- nothing to do.
            Exit code 3: no baseline recorded yet (first run for this key,
            or the recorded baseline commit no longer exists) -- caller
            should do a full sync of --root instead.

    commit  Record the current HEAD SHA as the new baseline for --state-key.
            Run this only after a sync actually succeeds.

Usage:
    python tools/anki/sync/sync_scope.py list --state-key ua_lexeme \\
        --root domains/ua/anki/notes/lexemes
    python tools/anki/sync/sync_scope.py commit --state-key ua_lexeme
    python tools/anki/sync/sync_scope.py list --state-key ua_lexeme --root ... --full
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = REPO_ROOT / ".anki_sync_state"


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def state_file(state_key: str) -> Path:
    return STATE_DIR / f"{state_key}.sha"


def commit_ref_exists(sha: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=REPO_ROOT, capture_output=True,
    )
    return result.returncode == 0


def cmd_list(state_key: str, root: str, full: bool, exclude: list[str]) -> int:
    sf = state_file(state_key)
    baseline = sf.read_text(encoding="utf-8").strip() if sf.exists() else ""

    if full or not baseline or not commit_ref_exists(baseline):
        if baseline and not commit_ref_exists(baseline):
            print(
                f"warning: recorded baseline {baseline[:12]} for '{state_key}' no longer "
                f"exists -- falling back to full sync",
                file=sys.stderr,
            )
        return 3

    changed: set[str] = set()
    deleted: set[str] = set()

    # (a) committed changes since baseline
    out = run_git(["diff", "--name-status", baseline, "HEAD", "--", root])
    for line in out.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        (deleted if status.startswith("D") else changed).add(path)

    # (b) currently dirty (staged + unstaged) under root
    out = run_git(["diff", "--name-status", "HEAD", "--", root])
    for line in out.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        (deleted if status.startswith("D") else changed).add(path)

    # (c) untracked new files under root
    out = run_git(["ls-files", "--others", "--exclude-standard", "--", root])
    for path in out.splitlines():
        if path.strip():
            changed.add(path.strip())

    changed -= deleted

    def is_excluded(p: str) -> bool:
        from fnmatch import fnmatch
        return any(fnmatch(p, pat) for pat in exclude)

    changed = {p for p in changed if p.endswith(".md") and not is_excluded(p)}

    if deleted:
        shown = sorted(deleted)[:20]
        print(
            f"note: {len(deleted)} file(s) deleted since last '{state_key}' sync -- "
            f"not auto-removed from Anki, handle manually if needed:",
            file=sys.stderr,
        )
        for p in shown:
            print(f"  D  {p}", file=sys.stderr)

    for p in sorted(changed):
        print(p)
    return 0


def cmd_commit(state_key: str) -> int:
    STATE_DIR.mkdir(exist_ok=True)
    sha = run_git(["rev-parse", "HEAD"]).strip()
    state_file(state_key).write_text(sha + "\n", encoding="utf-8")
    print(f"Recorded baseline for '{state_key}': {sha[:12]}", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--state-key", required=True)
    p_list.add_argument("--root", required=True)
    p_list.add_argument("--full", action="store_true")
    p_list.add_argument("--exclude", action="append", default=[], help="glob(s) to exclude, e.g. '*/exported/*'")

    p_commit = sub.add_parser("commit")
    p_commit.add_argument("--state-key", required=True)

    args = ap.parse_args()

    if args.cmd == "list":
        return cmd_list(args.state_key, args.root, args.full, args.exclude)
    elif args.cmd == "commit":
        return cmd_commit(args.state_key)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
