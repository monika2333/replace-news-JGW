#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import re
from typing import List, Sequence, Tuple

CHINESE_NUMS = [
    "",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "十一",
    "十二",
    "十三",
    "十四",
    "十五",
    "十六",
    "十七",
    "十八",
    "十九",
    "二十",
    "二十一",
    "二十二",
    "二十三",
    "二十四",
    "二十五",
    "二十六",
    "二十七",
    "二十八",
    "二十九",
    "三十",
]


def chinese_number(num: int) -> str:
    """将阿拉伯数字转换为中文数词。"""
    if 0 <= num < len(CHINESE_NUMS):
        return CHINESE_NUMS[num]
    return str(num)


def number_news_items(lines: Sequence[str]) -> Tuple[List[str], int]:
    """Return updated lines with Chinese numbering and count of items changed."""
    new_lines: List[str] = []
    news_counter = 0
    added_count = 0
    i = 0
    total_lines = len(lines)

    while i < total_lines:
        raw_line = lines[i]
        stripped_line = raw_line.strip()

        if i < 5:
            new_lines.append(raw_line)
            i += 1
            continue

        if stripped_line.startswith("【"):
            new_lines.append(raw_line)
            news_counter = 0
            i += 1
            continue

        if not stripped_line:
            new_lines.append(raw_line)
            i += 1
            continue

        is_news_title = False
        if i + 1 < total_lines:
            next_line = lines[i + 1].strip()
            if next_line and len(next_line) > 50 and not next_line.startswith("【"):
                if not re.match(r"^(\d+月\d+日|近日|昨日|今日)", stripped_line):
                    is_news_title = True

        if is_news_title:
            news_counter += 1

            # 检查是否已有序号前缀
            existing_number_match = re.match(r"^[一二三四五六七八九十]+、", stripped_line)

            # 总是重新编号（无论是否已有序号）
            if raw_line.endswith("\r\n"):
                newline = "\r\n"
            elif raw_line.endswith("\n"):
                newline = "\n"
            elif raw_line.endswith("\r"):
                newline = "\r"
            else:
                newline = "\n"

            # 移除原有的序号前缀（如果存在）
            if existing_number_match:
                content_start = existing_number_match.end()
                content = stripped_line[content_start:]
            else:
                content = stripped_line
                added_count += 1

            numbered_line = f"{chinese_number(news_counter)}、{content}{newline}"
            new_lines.append(numbered_line)
        else:
            new_lines.append(raw_line)

        i += 1

    return new_lines, added_count


def process_file(path: pathlib.Path, dry_run: bool) -> Tuple[bool, int]:
    """Process a single file and return (changed flag, items updated)."""
    try:
        original_content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[skip] {path} (encoding not utf-8)")
        return False, 0

    original_lines = original_content.splitlines(keepends=True)
    new_lines, added_count = number_news_items(original_lines)

    if new_lines == original_lines:
        print(f"[ok]   {path} (no change)")
        return False, 0

    if dry_run:
        print(f"[dry]  {path} (would add numbers to {added_count} item(s))")
        return True, added_count

    path.write_text("".join(new_lines), encoding="utf-8")
    print(f"[edit] {path} (added numbers to {added_count} item(s))")
    return True, added_count


def collect_txt_files(targets: Sequence[pathlib.Path]) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    seen = set()

    for target in targets:
        if target.is_file():
            if target.suffix.lower() == ".txt":
                if target not in seen:
                    files.append(target)
                    seen.add(target)
            else:
                print(f"[skip] {target} (not a .txt file)")
            continue

        if target.is_dir():
            for candidate in sorted(p for p in target.glob("*.txt") if p.is_file()):
                if candidate not in seen:
                    files.append(candidate)
                    seen.add(candidate)
            continue

        print(f"[skip] {target} (path does not exist)")

    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add Chinese numbering prefixes to news items inside .txt files.",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        type=pathlib.Path,
        help="File(s) or directory(ies) to process (defaults to current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report files that would change without writing updates",
    )
    args = parser.parse_args()

    targets = args.targets or [pathlib.Path.cwd()]
    txt_files = collect_txt_files(targets)
    if not txt_files:
        print("No .txt files found.")
        return

    changed_files = 0
    total_numbered = 0
    for file_path in txt_files:
        changed, added = process_file(file_path, args.dry_run)
        if changed:
            changed_files += 1
            total_numbered += added

    summary_action = "Would update" if args.dry_run else "Updated"
    numbering_action = "would add numbering to" if args.dry_run else "added numbering to"
    print(
        f"\nDone. {summary_action} {changed_files} file(s); "
        f"scanned {len(txt_files)} total; {numbering_action} {total_numbered} item(s)."
    )


if __name__ == "__main__":
    main()
