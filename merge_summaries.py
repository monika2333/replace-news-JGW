"""
Quickly merge numbered `high_score_summaries_YYYY_MM_DD(n).txt` files by date.

Usage:
    python merge_summaries.py
"""
from __future__ import annotations

import argparse
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

FILENAME_RE = re.compile(r"^high_score_summaries_(\d{4}_\d{2}_\d{2})\((\d+)\)\.txt$")
ALLOWED_CATEGORIES = {
    "【\u4eac\u5185\u6b63\u9762】",
    "【\u4eac\u5185\u8d1f\u9762】",
    "【\u4eac\u5916\u6b63\u9762】",
    "【\u4eac\u5916\u8d1f\u9762】",
}
CATEGORY_HEADER_RE = re.compile(
    r"^(【\u4eac\u5185\u6b63\u9762】|【\u4eac\u5185\u8d1f\u9762】|【\u4eac\u5916\u6b63\u9762】|【\u4eac\u5916\u8d1f\u9762】)"
)
ANY_HEADER_RE = re.compile(r"^【[^】]+】")


def find_segment_files(root: Path) -> Mapping[str, List[Path]]:
    grouped: Dict[str, List[Path]] = defaultdict(list)
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        match = FILENAME_RE.match(entry.name)
        if not match:
            continue
        grouped[match.group(1)].append(entry)
    for paths in grouped.values():
        paths.sort(key=_segment_sort_key)
    return grouped


def _segment_sort_key(path: Path) -> int:
    match = FILENAME_RE.match(path.name)
    return int(match.group(2)) if match else 0


def parse_summary_file(path: Path) -> "OrderedDict[str, List[str]]":
    categories: "OrderedDict[str, List[str]]" = OrderedDict()
    current_label: str | None = None
    current_lines: List[str] = []

    def flush_entry() -> None:
        if current_label is None or not current_lines:
            return
        entry_text = "".join(current_lines).rstrip()
        if entry_text:
            categories.setdefault(current_label, []).append(entry_text)
        current_lines.clear()

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            header_match = CATEGORY_HEADER_RE.match(stripped)
            if header_match:
                flush_entry()
                current_label = header_match.group(1)
                categories.setdefault(current_label, [])
                continue
            if ANY_HEADER_RE.match(stripped):
                flush_entry()
                current_label = None  # Ignore categories not in the allowlist.
                continue
            if current_label is None:
                continue
            if stripped == "":
                flush_entry()
            else:
                current_lines.append(raw_line)
        flush_entry()
    return categories


def merge_categories(parsed_files: Iterable["OrderedDict[str, List[str]]"]) -> "OrderedDict[str, List[str]]":
    merged: "OrderedDict[str, List[str]]" = OrderedDict()
    for category_map in parsed_files:
        for label, entries in category_map.items():
            merged.setdefault(label, [])
            merged[label].extend(entries)
    return merged


def write_merged_file(categories: "OrderedDict[str, List[str]]", output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        first_category = True
        for label, entries in categories.items():
            if not first_category:
                handle.write("\n")
            first_category = False
            handle.write(f"{label}：{len(entries)} 条\n\n")
            for entry in entries:
                handle.write(entry.rstrip())
                handle.write("\n\n")


def merge_all(root: Path, suffix: str, delete_sources: bool) -> None:
    groups = find_segment_files(root)
    if not groups:
        print("No matching summary files found.")
        return

    for date_key, paths in sorted(groups.items()):
        output_path = root / f"high_score_summaries_{date_key}{suffix}.txt"
        existing_categories: "OrderedDict[str, List[str]]" = (
            parse_summary_file(output_path) if output_path.exists() else OrderedDict()
        )

        parsed = [parse_summary_file(path) for path in paths]
        new_categories = merge_categories(parsed)
        if not new_categories:
            print(f"[{date_key}] Skipped: no categories detected.")
            continue

        # Append new entries while keeping existing content and avoiding duplicates.
        updated: "OrderedDict[str, List[str]]" = OrderedDict()
        for label, entries in existing_categories.items():
            updated[label] = list(entries)

        for label, entries in new_categories.items():
            existing_set = set(updated.get(label, []))
            additions = [entry for entry in entries if entry not in existing_set]
            if additions:
                updated.setdefault(label, []).extend(additions)

        if not updated:
            print(f"[{date_key}] Skipped: no content to write.")
            continue

        write_merged_file(updated, output_path)
        print(
            f"[{date_key}] Updated {output_path.name} "
            f"(existing categories: {len(existing_categories)}, added parts: {len(paths)})."
        )

        if delete_sources:
            for src in paths:
                try:
                    src.unlink()
                except OSError as exc:
                    print(f"[{date_key}] Warning: failed to delete {src.name}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge numbered high score summary files by date.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Directory to scan. Defaults to current directory.")
    parser.add_argument("--suffix", default="_merged", help="Suffix before .txt for merged files. Defaults to '_merged'.")
    parser.add_argument(
        "--keep-sources",
        action="store_true",
        help="Keep the numbered source files instead of deleting them after merge.",
    )
    args = parser.parse_args()
    merge_all(args.root.resolve(), suffix=args.suffix, delete_sources=not args.keep_sources)


if __name__ == "__main__":
    main()
