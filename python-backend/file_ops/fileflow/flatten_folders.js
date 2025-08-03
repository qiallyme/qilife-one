#!/usr/bin/env python3
"""
flatten_small_folders.py

Purpose
-------
Interactive/CLI utility to flatten out *shallow* folder hierarchies where most
subfolders contain only a tiny number of files (e.g., 1). Typical use case:
Google Drive or other sync dumps that produced thousands of one-file folders.

Default behavior mirrors Q's immediate need:
    * Root defaults to: Q:\\GoogleDriveStream\\A_inbox_
    * Look exactly 1 level down (depth=1) from root.
    * If a folder contains <2 direct child *files* (ignores subfolders), move
      those file(s) up into the root, then delete the now-empty folder.

Generalized so you can reuse it:
    * Prompt-driven if args omitted.
    * Choose how many levels deep to scan.
    * Choose the file-count threshold (< limit triggers flatten).
    * Dry-run preview mode (default ON when prompting interactively).
    * Smart collision handling: auto-rename with numeric suffix if a same-named
      file already exists at the destination.

FAST & DIRTY  (one-off now)
--------------------------
python flatten_small_folders.py --root "Q:\\GoogleDriveStream\\A_inbox_" --levels 1 --limit 2 --yes

SOLID & SAFE  (prompt + dry-run preview)
---------------------------------------
python flatten_small_folders.py  # you'll be prompted

BIG ENERGY  (batch logs + CSV + recursive deeper clean)
------------------------------------------------------
Use --log and --report flags (see below) and run multiple passes at increasing
levels.

Windows-safe. Cross‑platform friendly.

Usage
-----
python flatten_small_folders.py [--root PATH] [--levels N] [--limit N]
                               [--target PATH] [--dry-run/--no-dry-run]
                               [--log LOGFILE] [--report CSVFILE]
                               [--include-hidden] [--yes]

Key Terms
---------
*levels*  = max depth (0=root only, 1=children, 2=grandchildren ...).
*limit*   = flatten when (#files in that folder) < limit. (ex: limit=2 => 0 or 1 file triggers.)

Notes
-----
• Only *direct child* files counted. Subdirectories inside a candidate folder
  are ignored (and the folder is skipped if it has subfolders unless you add
  --allow-subdirs).
• Destination defaults to the *root* path, regardless of how deep a small
  folder lives (consistent with Q's request). Override with --target.
• If a folder qualifies but all its files fail to move (permission errors), the
  folder will NOT be deleted.

"""

from __future__ import annotations
import argparse
import os
import shutil
import sys
import csv
from pathlib import Path
from typing import Iterable, List, Tuple, Optional


def prompt_if_missing(args: argparse.Namespace) -> None:
    """Interactively fill in missing args."""
    if args.root is None:
        default_root = r"Q:\\GoogleDriveStream\\A_inbox_"
        root_in = input(f"Root directory? [default: {default_root}] ").strip() or default_root
        args.root = root_in
    if args.levels is None:
        levels_in = input("How many levels deep to scan? [default: 1] ").strip() or "1"
        args.levels = int(levels_in)
    if args.limit is None:
        limit_in = input("Flatten folders with how many *max* files? Flatten when < limit. [default: 2] ").strip() or "2"
        args.limit = int(limit_in)
    if args.target is None:
        # default target = root
        tgt_in = input("Destination to move small-folder files into? [default: ROOT] ").strip()
        args.target = args.root if not tgt_in else tgt_in
    if args.dry_run is None:
        yn = input("Dry run first? [Y/n] ").strip().lower()
        args.dry_run = (yn != "n")
    if not args.yes:
        confirm = input("Proceed with scan? Type 'yes' to continue: ").strip().lower()
        if confirm not in ("y", "yes"):  # bail
            print("Aborted by user.")
            sys.exit(0)


def is_hidden(path: Path) -> bool:
    """Best‑effort hidden check (cross-platform)."""
    name = path.name
    if name.startswith('.'):
        return True
    # Windows hidden attrib? Can't reliably without ctypes; skip heavy.
    return False


def iter_dirs(root: Path, max_depth: int) -> Iterable[Path]:
    """Yield directories up to max_depth below root (depth=0 yields root only)."""
    root_depth = len(root.parts)
    for p in root.rglob('*'):
        if not p.is_dir():
            continue
        depth = len(p.parts) - root_depth
        if depth == 0:
            continue  # skip root itself
        if depth <= max_depth:
            yield p


def count_direct_files(folder: Path, include_hidden: bool) -> Tuple[int, List[Path]]:
    """Return (#files, list_of_file_paths) for *direct* children (no recursion)."""
    files = []
    try:
        for entry in folder.iterdir():
            if entry.is_file():
                if not include_hidden and is_hidden(entry):
                    continue
                files.append(entry)
    except PermissionError as e:
        print(f"[WARN] Permission denied reading {folder}: {e}")
    return len(files), files


def has_subdirs(folder: Path) -> bool:
    try:
        for entry in folder.iterdir():
            if entry.is_dir():
                return True
    except PermissionError:
        return False
    return False


def unique_dest(dest_dir: Path, name: str) -> Path:
    """Generate a non-colliding destination path by appending _# before suffix."""
    candidate = dest_dir / name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    i = 1
    while True:
        new_name = f"{stem}_{i}{suffix}"
        candidate = dest_dir / new_name
        if not candidate.exists():
            return candidate
        i += 1


def move_files(files: Iterable[Path], dest_dir: Path, dry_run: bool) -> List[Tuple[Path, Path, bool, str]]:
    """Move each file to dest_dir, returning action records.

    Returns list of tuples: (src, dest, success, msg)
    """
    results = []
    for f in files:
        dest = unique_dest(dest_dir, f.name)
        try:
            if dry_run:
                msg = "dry-run"
                success = True
            else:
                shutil.move(str(f), str(dest))
                msg = "moved"
                success = True
        except Exception as e:  # broad to ensure logging continues
            msg = f"ERROR: {e}"
            success = False
        results.append((f, dest, success, msg))
    return results


def delete_folder_if_empty(folder: Path, dry_run: bool) -> Tuple[bool, str]:
    try:
        if any(folder.iterdir()):
            return False, "not empty"
        if dry_run:
            return True, "dry-run-delete"
        folder.rmdir()
        return True, "deleted"
    except Exception as e:  # broad safe
        return False, f"ERROR: {e}"


def scan_and_flatten(root: Path,
                     max_depth: int,
                     limit: int,
                     target: Path,
                     include_hidden: bool = False,
                     allow_subdirs: bool = False,
                     dry_run: bool = True,
                     log_records: Optional[List[dict]] = None) -> None:
    """Perform the flatten operation."""
    total_dirs = 0
    flattened = 0
    skipped = 0

    for folder in iter_dirs(root, max_depth):
        total_dirs += 1
        if not allow_subdirs and has_subdirs(folder):
            skipped += 1
            if log_records is not None:
                log_records.append({
                    'folder': str(folder),
                    'action': 'skip-has-subdirs',
                    'files': 0,
                })
            continue

        file_count, file_list = count_direct_files(folder, include_hidden)
        if file_count < limit:
            print(f"[FLATTEN] {folder} -> {target} ({file_count} files)")
            flattened += 1
            move_res = move_files(file_list, target, dry_run)
            del_ok, del_msg = delete_folder_if_empty(folder, dry_run)
            if log_records is not None:
                for src, dest, success, msg in move_res:
                    log_records.append({
                        'folder': str(folder),
                        'src': str(src),
                        'dest': str(dest),
                        'move': msg,
                        'deleted': del_msg if del_ok else del_msg,
                    })
        else:
            skipped += 1
            if log_records is not None:
                log_records.append({
                    'folder': str(folder),
                    'action': 'skip-filecount',
                    'files': file_count,
                })

    print("\n=== SUMMARY ===")
    print(f"Scanned dirs:   {total_dirs}")
    print(f"Flattened dirs: {flattened}")
    print(f"Skipped dirs:   {skipped}")
    if dry_run:
        print("(dry run: no changes made)")


def write_logfile(log_path: Path, records: List[dict]) -> None:
    if not records:
        return
    headers = sorted({k for r in records for k in r.keys()})
    with log_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    print(f"Log written: {log_path}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Flatten tiny subfolders by moving their files up to a target directory.")
    p.add_argument('--root', type=str, help='Root directory to scan.')
    p.add_argument('--levels', type=int, help='How many levels deep to scan (1=children).')
    p.add_argument('--limit', type=int, help='Flatten when <limit direct files. (Default 2).')
    p.add_argument('--target', type=str, help='Destination directory for moved files (default=root).')
    p.add_argument('--include-hidden', action='store_true', help='Include hidden dotfiles in counts/moves.')
    p.add_argument('--allow-subdirs', action='store_true', help='Allow flattening folders even if they contain subfolders (subfolders NOT moved).')
    dry_group = p.add_mutually_exclusive_group()
    dry_group.add_argument('--dry-run', dest='dry_run', action='store_true', help='Preview actions (default if prompting).')
    dry_group.add_argument('--no-dry-run', dest='dry_run', action='store_false', help='Execute moves/deletes.')
    p.set_defaults(dry_run=None)  # None => unknown => will prompt
    p.add_argument('--log', type=str, help='CSV log output path.')
    p.add_argument('--yes', action='store_true', help='Assume yes / skip interactive confirmation.')
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    # Fill interactively if needed
    interactive = any(x is None for x in (args.root, args.levels, args.limit, args.target, args.dry_run)) and not args.yes
    if interactive:
        prompt_if_missing(args)

    root = Path(args.root).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        print(f"ERROR: root not found / not dir: {root}")
        return 1
    if not target.exists():
        try:
            if args.dry_run:
                print(f"[dry-run] would create target: {target}")
            else:
                target.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"ERROR creating target: {e}")
            return 1

    records: List[dict] = [] if args.log else None  # type: ignore

    scan_and_flatten(
        root=root,
        max_depth=args.levels,
        limit=args.limit,
        target=target,
        include_hidden=args.include_hidden,
        allow_subdirs=args.allow_subdirs,
        dry_run=args.dry_run if args.dry_run is not None else True,
        log_records=records,
    )

    if records is not None:
        log_path = Path(args.log).expanduser().resolve()
        write_logfile(log_path, records)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
