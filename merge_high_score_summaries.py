"""
Merge segmented high score summary files by date while keeping category sections intact.

Example usage:
    python merge_high_score_summaries.py --root . --suffix _merged --overwrite
"""
from __future__ import annotations

import argparse
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

FILENAME_RE = re.compile(r"^high_score_summaries_(\d{4}_\d{2}_\d{2})\((\d+)\)\.txt$")
CATEGORY_HEADER_RE = re.compile(r"^(【[^】]+】)")


def find_segment_files(root: Path) -> Mapping[str, List[Path]]:
    grouped: Dict[str, List[Path]] = defaultdict(list)
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        match = FILENAME_RE.match(entry.name)
        if not match:
            continue
        date_key, segment = match.groups()
        grouped[date_key].append(entry)
    for paths in grouped.values():
        paths.sort(key=_segment_sort_key)
    return grouped


def _segment_sort_key(path: Path) -> int:
    match = FILENAME_RE.match(path.name)
    if not match:
        return 0
    return int(match.group(2))


def parse_summary_file(path: Path) -> "OrderedDict[str, List[str]]":
    categories: "OrderedDict[str, List[str]]" = OrderedDict()
    current_label: str | None = None
    current_lines: List[str] = []

    def flush_entry() -> None:
        if current_label is None or not current_lines:
            return
        # Keep internal formatting but drop trailing blank lines.
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


def write_merged_file(
    date_key: str,
    categories: "OrderedDict[str, List[str]]",
    output_root: Path,
    suffix: str,
) -> Path:
    output_path = output_root / f"high_score_summaries_{date_key}{suffix}.txt"
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        first_category = True
        for label, entries in categories.items():
            if not first_category:
                handle.write("\n")
            first_category = False
            handle.write(f"{label}共 {len(entries)} 条\n\n")
            for entry in entries:
                handle.write(entry.rstrip())
                handle.write("\n\n")
    return output_path


def merge_all(
    root: Path,
    output_root: Path,
    suffix: str,
    overwrite: bool,
    delete_sources: bool,
) -> None:
    groups = find_segment_files(root)
    if not groups:
        print("No segmented summary files found.")
        return

    if not output_root.exists():
        output_root.mkdir(parents=True, exist_ok=True)

    for date_key, paths in sorted(groups.items()):
        parsed = [parse_summary_file(path) for path in paths]
        merged = merge_categories(parsed)
        if not merged:
            print(f"[{date_key}] Skipped: no categories detected.")
            continue
        output_path = output_root / f"high_score_summaries_{date_key}{suffix}.txt"
        if output_path.exists() and not overwrite:
            print(f"[{date_key}] Skipped: {output_path.name} already exists. Use --overwrite to replace.")
            continue
        write_merged_file(date_key, merged, output_root, suffix)
        counts = ", ".join(f"{label}={len(entries)}" for label, entries in merged.items())
        print(f"[{date_key}] Wrote {output_path.name} ({counts}).")
        if delete_sources:
            for src in paths:
                try:
                    src.unlink()
                except OSError as exc:
                    print(f"[{date_key}] Warning: failed to delete {src.name}: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge segmented high score summary files (…(1).txt, …(2).txt, …) into a single file per date."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Directory to scan for segmented summary files. Defaults to current directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to place merged files. Defaults to the same directory given by --root.",
    )
    parser.add_argument(
        "--suffix",
        default="_merged",
        help="Suffix to append before .txt for merged files. Defaults to '_merged'.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing merged files that would otherwise block writing.",
    )
    parser.add_argument(
        "--delete-sources",
        action="store_true",
        help="Delete the numbered segment files after a successful merge.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else root
    suffix = args.suffix if args.suffix is not None else ""
    merge_all(
        root,
        output_dir,
        suffix=suffix,
        overwrite=args.overwrite,
        delete_sources=args.delete_sources,
    )


if __name__ == "__main__":
    main()
