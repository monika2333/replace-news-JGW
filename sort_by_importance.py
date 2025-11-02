#!/usr/bin/env python3
"""
Sort news entries by external_importance or score field within each category.

This script sorts news entries within summary files in descending order
based on their external_importance or score values.

Usage:
    python sort_by_importance.py [--file FILE] [--backup] [--restore]

Examples:
    # Sort all high_score_summaries_*.txt files
    python sort_by_importance.py

    # Sort specific file with backup
    python sort_by_importance.py --file high_score_summaries_2025_11_02_merged.txt --backup

    # Restore from backup
    python sort_by_importance.py --file high_score_summaries_2025_11_02_merged.txt --restore
"""
import argparse
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

EXTERNAL_IMPORTANCE_RE = re.compile(r'external_importance=(\d+)')
SCORE_RE = re.compile(r'score=(\d+)')


def get_importance(text: str) -> int:
    """Extract importance value from text (external_importance or score)."""
    match = EXTERNAL_IMPORTANCE_RE.search(text)
    if match:
        return int(match.group(1))
    match = SCORE_RE.search(text)
    if match:
        return int(match.group(1))
    return 0


def backup_file(file_path: Path) -> Path:
    """Create a backup of the file."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
    shutil.copy2(file_path, backup_path)
    return backup_path


def restore_from_backup(file_path: Path) -> bool:
    """Restore file from its backup."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
    if backup_path.exists():
        shutil.copy2(backup_path, file_path)
        print(f"Restored {file_path.name} from {backup_path.name}")
        return True
    else:
        print(f"No backup found for {file_path.name}")
        return False


def sort_file(file_path: Path, create_backup: bool = False) -> None:
    """Sort a single file by importance."""
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract category
    category_match = re.search(r'^(【[^】]+】)', content, re.MULTILINE)
    category = category_match.group(1) if category_match else '【分类】'

    # Split into entries
    entries = re.split(r'\n\s*\n\s*', content)
    entries = [e.strip() for e in entries if e.strip() and not re.match(r'^【[^】]+】', e.strip())]

    if not entries:
        print(f"  No entries found in {file_path.name}")
        return

    # Sort by importance (high to low)
    sorted_entries = sorted(entries, key=get_importance, reverse=True)

    # Create backup if requested
    if create_backup:
        backup_path = backup_file(file_path)
        print(f"  Backup created: {backup_path.name}")

    # Write sorted content
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f"{category}共 {len(sorted_entries)} 条\n\n")
        for i, entry in enumerate(sorted_entries):
            f.write(entry)
            if i < len(sorted_entries) - 1:
                f.write("\n\n")

    # Show result
    max_imp = get_importance(sorted_entries[0])
    min_imp = get_importance(sorted_entries[-1])
    print(f"  ✓ Sorted {len(entries)} entries: {max_imp} → {min_imp}")


def main():
    parser = argparse.ArgumentParser(
        description="Sort news entries by external_importance or score (high to low).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Sort all high_score_summaries_*.txt files
  %(prog)s --file myfile.txt                  # Sort specific file
  %(prog)s --file myfile.txt --backup         # Sort with backup
  %(prog)s --file myfile.txt --restore        # Restore from backup
        """
    )

    parser.add_argument(
        '--file',
        type=Path,
        help='Specific file to sort (otherwise processes all high_score_summaries_*.txt)'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before sorting'
    )

    parser.add_argument(
        '--restore',
        action='store_true',
        help='Restore file from backup'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Sorting news entries by importance")
    print("=" * 60)

    if args.restore:
        if not args.file:
            parser.error("--restore requires --file")
        restore_from_backup(args.file)
        print("=" * 60)
        return

    if args.file:
        if not args.file.exists():
            print(f"Error: File {args.file} not found")
            return
        print(f"\nProcessing {args.file.name}...")
        sort_file(args.file, create_backup=args.backup)
    else:
        txt_files = sorted(Path('.').glob('high_score_summaries_*.txt'))
        if not txt_files:
            print("No high_score_summaries_*.txt files found.")
            return

        print(f"\nProcessing {len(txt_files)} file(s)...\n")
        for file_path in txt_files:
            print(f"{file_path.name}:")
            sort_file(file_path, create_backup=True)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
