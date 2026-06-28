#!/usr/bin/env python3
import argparse
from itertools import cycle
from pathlib import Path
import os
import sys
import time


def find_serato_stems(root: Path):
    spinner = cycle("|/-\\")
    stem_files = []
    scanned = 0

    sys.stdout.write(f"Searching {root} ... ")
    sys.stdout.flush()

    for dirpath, _, files in os.walk(root):
        for filename in files:
            scanned += 1
            if scanned % 20 == 0:
                sys.stdout.write(
                    f"\rSearching {root} ... {next(spinner)} scanned={scanned} found={len(stem_files)}"
                )
                sys.stdout.flush()

            if filename.lower().endswith(".serato-stems"):
                stem_files.append(Path(dirpath) / filename)

    sys.stdout.write(
        f"\rSearching {root} ... done scanned={scanned} found={len(stem_files)}\n"
    )
    sys.stdout.flush()
    return sorted(stem_files)


def confirm(prompt: str) -> bool:
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a folder recursively for .serato-stems files, list them, count them, and optionally delete them."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder to scan. Defaults to current directory.",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Delete found files without asking for confirmation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the files that would be deleted without removing them.",
    )
    args = parser.parse_args()

    root = Path(args.folder).expanduser().resolve()
    if not root.exists():
        print(f"Error: folder does not exist: {root}")
        return 1
    if not root.is_dir():
        print(f"Error: path is not a folder: {root}")
        return 1

    stem_files = find_serato_stems(root)
    count = len(stem_files)
    print(f"Scanning: {root}")
    print(f"Found {count} .serato-stems file{'s' if count != 1 else ''}.")

    if count == 0:
        return 0

    for path in stem_files:
        print(path)

    if args.dry_run:
        print("\nDry run enabled: no files will be deleted.")
        return 0

    if args.yes or confirm("Do you want to delete these files? [y/N] "):
        deleted = 0
        for path in stem_files:
            try:
                path.unlink()
                deleted += 1
            except Exception as exc:
                print(f"Failed to delete {path}: {exc}")
        print(f"Deleted {deleted} file{'s' if deleted != 1 else ''}.")
    else:
        print("Nothing was deleted.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
