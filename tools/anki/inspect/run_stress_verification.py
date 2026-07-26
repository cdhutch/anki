#!/usr/bin/env python3
"""run_stress_verification.py — Interactive stress verification wizard.

Walks you through the full Горох stress verification workflow:
  1. Extract  — read notes, generate goroh_fetch.js
  2. Fetch    — guided Chrome DevTools instructions + wait for goroh_cache.json
  3. Compare  — diff stored forms vs Горох paradigms
  4. Review   — open mismatches.tsv for editing
  5. Apply    — patch note files, remove stress:unverified tags
  6. Reimport — canonicalize + sync to Anki

Usage:
    python tools/anki/inspect/run_stress_verification.py
    python tools/anki/inspect/run_stress_verification.py --out-dir /tmp/goroh
    python tools/anki/inspect/run_stress_verification.py --resume --out-dir /tmp/goroh
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).parent / "verify_stress_goroh.py"
NOTES_VSTUP = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes" / "yabluko-l1" / "ch-00"

# ── Terminal colours (no external deps) ──────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RED    = "\033[31m"
DIM    = "\033[2m"


def c(text: str, *codes: str) -> str:
    return "".join(codes) + text + RESET


def header(title: str):
    width = 60
    print()
    print(c("─" * width, CYAN))
    print(c(f"  {title}", BOLD + CYAN))
    print(c("─" * width, CYAN))


def ok(msg: str):
    print(c("  ✓ ", GREEN) + msg)


def warn(msg: str):
    print(c("  ⚠ ", YELLOW) + msg)


def info(msg: str):
    print(c("  · ", DIM) + msg)


def step(n: int, total: int, title: str):
    print()
    print(c(f"Step {n}/{total} — {title}", BOLD))


def pause(prompt: str = "Press Enter to continue…") -> str:
    try:
        return input(c(f"\n  {prompt} ", CYAN))
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)


def confirm(prompt: str) -> bool:
    while True:
        ans = pause(f"{prompt} [y/n]").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Please enter y or n.")


def run_script(args: list[str]) -> int:
    """Run verify_stress_goroh.py with args; return exit code."""
    cmd = [sys.executable, str(SCRIPT)] + args
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


def open_file(path: Path):
    """Open a file with the system default application."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        elif sys.platform == "win32":
            import os
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)])
    except Exception:
        warn(f"Could not open automatically: {path}")
        info(f"Open manually: {path}")


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard; return True on success."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        elif sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode(), check=True)
            return True
        else:
            # xclip or xsel
            for cmd in (["xclip", "-selection", "clipboard"],
                        ["xsel", "--clipboard", "--input"]):
                try:
                    subprocess.run(cmd, input=text.encode(), check=True)
                    return True
                except FileNotFoundError:
                    continue
    except Exception:
        pass
    return False


# ── Steps ─────────────────────────────────────────────────────────────────────

def step_extract(out_dir: Path, total: int):
    step(1, total, "Extract verification targets")
    info("Reading all notes tagged stress:unverified …")
    rc = run_script(["--extract", "--out-dir", str(out_dir)])
    if rc != 0:
        print(c("\nExtract failed — see errors above.", RED))
        sys.exit(1)
    ok("goroh_input.json written")
    ok("goroh_fetch.js written")


def step_fetch(out_dir: Path, total: int) -> Path:
    step(2, total, "Fetch Горох paradigms")

    cache_path = out_dir / "goroh_cache.json"

    print()
    print(c("  Choose fetch method:", BOLD))
    print()
    print(c("  1", BOLD) + "  Python (recommended) — fetches directly, no browser needed")
    print(c("  2", BOLD) + "  Chrome DevTools      — paste JS in browser console")
    print()

    choice = ""
    while choice not in ("1", "2"):
        choice = pause("Enter 1 or 2: ").strip()

    if choice == "1":
        return _fetch_python(out_dir, cache_path, total)
    else:
        return _fetch_chrome(out_dir, cache_path, total)


def _fetch_python(out_dir: Path, cache_path: Path, total: int) -> Path:
    info("Fetching all Горох pages via Python urllib …")
    print()
    rc = run_script(["--fetch", "--out-dir", str(out_dir)])
    if rc != 0:
        print(c("\nFetch failed — see errors above.", RED))
        print(c("  Try the Chrome DevTools method instead (re-run wizard, choose 2).", YELLOW))
        sys.exit(1)
    ok(f"goroh_cache.json written")
    return cache_path


def _fetch_chrome(out_dir: Path, cache_path: Path, total: int) -> Path:
    js_path = out_dir / "goroh_fetch.js"
    print()
    print(c("  Chrome DevTools instructions:", BOLD))
    print()
    print("  1. Open Chrome and go to:  " +
          c("https://goroh.pp.ua/Словозміна/водій", CYAN + BOLD))
    print("     (Must be on goroh.pp.ua to avoid CORS restrictions.)")
    print()
    print("  2. Open DevTools: " + c("Cmd+Option+I", BOLD) +
          " (Mac)  or  " + c("F12", BOLD) + " (Windows)")
    print("     Click the " + c("Console", BOLD) + " tab.")
    print()
    print("  3. Paste the script and press Enter.")
    print(c("     If Chrome says 'Allow pasting?', type: allow pasting  then paste again.", DIM))
    print()
    print("  4. Wait for 'goroh_cache.json downloaded' in the console.")
    print()

    js_text = js_path.read_text(encoding="utf-8")
    if copy_to_clipboard(js_text):
        ok("Script copied to clipboard — paste with Cmd+V / Ctrl+V")
    else:
        warn("Could not copy automatically.")
        info(f"Run:  cat {js_path} | pbcopy")

    if confirm("Open goroh.pp.ua in Chrome now?"):
        webbrowser.open("https://goroh.pp.ua/Словозміна/водій")

    pause("Press Enter after goroh_cache.json has downloaded…")

    downloads = Path.home() / "Downloads" / "goroh_cache.json"
    if not cache_path.exists():
        if downloads.exists():
            shutil.move(str(downloads), str(cache_path))
            ok(f"Moved from Downloads → {cache_path}")
        else:
            warn("goroh_cache.json not found automatically.")
            entered = pause("Enter the path to goroh_cache.json: ").strip()
            if entered:
                src = Path(entered).expanduser()
                if src.exists():
                    shutil.copy(str(src), str(cache_path))
                    ok(f"Copied to {cache_path}")
                else:
                    print(c(f"\n  File not found: {src}", RED))
                    sys.exit(1)
            else:
                print(c("\nCannot continue without goroh_cache.json.", RED))
                sys.exit(1)
    else:
        ok(f"Found: {cache_path}")

    return cache_path


def step_compare(out_dir: Path, cache_path: Path, total: int) -> Path:
    step(3, total, "Compare stored forms vs Горох")
    rc = run_script(["--compare", str(cache_path), "--out-dir", str(out_dir)])
    if rc != 0:
        print(c("\nCompare failed — see errors above.", RED))
        sys.exit(1)
    tsv_path = out_dir / "goroh_mismatches.tsv"
    ok(f"goroh_mismatches.tsv written")
    return tsv_path


def step_review(tsv_path: Path, total: int):
    step(4, total, "Review mismatches")

    # Quick mismatch count
    try:
        with tsv_path.open(encoding="utf-8") as f:
            lines = f.readlines()
        header_line = lines[0] if lines else ""
        data_lines = lines[1:]
        n_mismatch = sum(
            1 for l in data_lines
            if "\tmismatch\t" in l or "\tvariable_mismatch\t" in l or "\tvariable\t" in l
        )
    except Exception:
        n_mismatch = -1

    if n_mismatch == 0:
        ok("No mismatches — all stored forms match Горох.")
        ok("You can proceed directly to Apply.")
        return

    print()
    if n_mismatch > 0:
        print(c(f"  {n_mismatch} forms need attention (mismatch / variable / variable_mismatch).", YELLOW))
    print()
    print(c("  In goroh_mismatches.tsv:", BOLD))
    print()
    print("  · status = mismatch        → fill 'correction' with the Горох form")
    print("  · status = variable        → Горох has two valid stress positions;")
    print("                               choose one and put it in 'correction'")
    print("  · status = variable_mismatch → fill 'correction' (shown in 'goroh' column)")
    print("  · status = not_found       → check spelling; leave 'correction' blank to keep")
    print()
    print(c("  Tip: the 'goroh' column already contains the suggested correction.", DIM))
    print(c("       For 'mismatch', that column is pre-filled in 'correction' automatically.", DIM))
    print()

    if confirm("Open goroh_mismatches.tsv now?"):
        open_file(tsv_path)
        pause("Press Enter when you have finished editing and saved the file…")
    else:
        info(f"Edit manually: {tsv_path}")
        pause("Press Enter when done…")


def step_apply(tsv_path: Path, out_dir: Path, total: int):
    step(5, total, "Apply corrections")

    print()
    info("Dry run first to preview changes…")
    print()
    rc = run_script(["--apply", str(tsv_path), "--dry-run"])
    if rc != 0:
        print(c("\nDry run failed — see errors above.", RED))
        sys.exit(1)

    print()
    if not confirm("Apply these changes to the note files?"):
        info("Skipped. Run manually when ready:")
        info(f"  python verify_stress_goroh.py --apply {tsv_path}")
        return

    rc = run_script(["--apply", str(tsv_path)])
    if rc != 0:
        print(c("\nApply failed — see errors above.", RED))
        sys.exit(1)
    ok("Note files updated")


def step_reimport(total: int):
    step(6, total, "Canonicalize + reimport to Anki")

    vstup_glob = str(NOTES_VSTUP / "*.md")
    sync_script = str(REPO_ROOT / "tools" / "anki" / "sync" / "ua_lexeme_import.py")

    canonicalize_cmd = f"python -m tools.anki.cnsf_canonicalize --write {vstup_glob}"
    import_cmd = f"python {sync_script} {NOTES_VSTUP}"

    print()
    print("  Run these commands (Anki must be open with AnkiConnect running):")
    print()
    print(c(f"    {canonicalize_cmd}", CYAN))
    print(c(f"    {import_cmd}", CYAN))
    print()

    if confirm("Run canonicalize now? (Anki does not need to be open)"):
        import glob
        md_files = sorted(glob.glob(vstup_glob))
        if md_files:
            result = subprocess.run(
                [sys.executable, "-m", "tools.anki.cnsf_canonicalize", "--write"] + md_files,
                cwd=str(REPO_ROOT),
            )
            if result.returncode == 0:
                ok("Canonicalized")
            else:
                warn("Canonicalize had errors — check output above")
        else:
            warn("No .md files found to canonicalize")

    if confirm("Run import now? (Anki must be open with AnkiConnect)"):
        result = subprocess.run(
            [sys.executable, sync_script, str(NOTES_VSTUP)],
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            ok("Import complete")
        else:
            warn("Import had errors — check output above")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", default="/tmp/goroh",
                        help="Directory for working files (default: /tmp/goroh)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip extract/fetch; resume from --compare using existing cache")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    TOTAL = 6

    # ── Banner ────────────────────────────────────────────────────────────────
    print()
    print(c("╔══════════════════════════════════════════════════════════╗", CYAN + BOLD))
    print(c("║     Горох Stress Verification — Interactive Wizard       ║", CYAN + BOLD))
    print(c("╚══════════════════════════════════════════════════════════╝", CYAN + BOLD))
    print()
    print(c("  Verifies stress marks in all Вступ notes against Горох.", DIM))
    print(c("  Handles variable stress (multiple valid positions).", DIM))
    print(c(f"  Working directory: {out_dir}", DIM))
    print()
    print(c("  See GOROH_VERIFICATION.md for full documentation.", DIM))

    cache_path = out_dir / "goroh_cache.json"
    tsv_path = out_dir / "goroh_mismatches.tsv"

    if args.resume:
        info("--resume: skipping extract and fetch steps")
        if not cache_path.exists():
            print(c(f"\n  goroh_cache.json not found in {out_dir}", RED))
            print(c("  Run without --resume to start from the beginning.", RED))
            sys.exit(1)
    else:
        step_extract(out_dir, TOTAL)
        cache_path = step_fetch(out_dir, TOTAL)

    step_compare(out_dir, cache_path, TOTAL)
    step_review(tsv_path, TOTAL)
    step_apply(tsv_path, out_dir, TOTAL)
    step_reimport(TOTAL)

    # ── Done ──────────────────────────────────────────────────────────────────
    header("All done!")
    ok("Stress verification complete.")
    ok("Notes with all forms verified now have stress:unverified removed.")
    print()
    print(c("  Next suggested tasks:", BOLD))
    print("  · Generate example sentences (ua_generate_examples.py)")
    print("  · Start Яблуко Unit 1 lexeme batch")
    print()


if __name__ == "__main__":
    main()
