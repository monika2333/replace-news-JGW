# AGENTS.md - Guidelines for Agentic Coding

## Project Overview
This is a Python 3.8+ text processing repository containing scripts for cleaning, reordering, numbering, and merging Chinese news text files. The codebase is disciplined with consistent patterns and modern Python practices.

## Build/Test Commands

### Running Scripts
```bash
# Bulk text replacement and cleanup
python bulk_replace.py                    # Process current directory
python bulk_replace.py <directory>        # Process specific directory  
python bulk_replace.py --dry-run          # Preview changes only

# Reorder brief entries by category priority
python reorder_brief.py <file>            # Reorder entries in file
python reorder_brief.py <file> -o <out>   # Output to new file
python reorder_brief.py <file> --in-place # Overwrite original file

# Add Chinese numbering to news items
python add_numbers.py                     # Process current directory .txt files
python add_numbers.py <file_or_dir>      # Process specific target
python add_numbers.py --dry-run           # Preview changes only

# Merge high-score summary files by date
python merge_summaries.py                 # Merge with default settings
python merge_summaries.py --keep-sources  # Keep source files after merge
python merge_summaries.py --root <dir>    # Specify scan directory
python merge_summaries.py --suffix <sfx>  # Custom output file suffix
```

### Testing Individual Scripts
```bash
# Test with dry-run mode first
python bulk_replace.py --dry-run
python add_numbers.py --dry-run

# Test on sample files (create test samples first)
python reorder_brief.py test_sample.txt -o test_output.txt
```

## Code Style Guidelines

### File Structure & Imports
- Use `#!/usr/bin/env python3` shebang for executable scripts
- Import standard library modules first, then third-party (none currently used)
- Group imports by type with blank lines between groups
- Use `from __future__ import annotations` for type hints compatibility
- Import `pathlib` for path operations instead of `os.path`

### Type Hints
- All functions must have complete type annotations
- Use `pathlib.Path` instead of string paths
- Use `Sequence[str] | None` for optional string sequences
- Use `Tuple[str, ...]` for immutable string tuples
- Return tuples for multiple values: `(result, changed_flag)`

### Naming Conventions
- **Functions**: `snake_case` with descriptive names
- **Variables**: `snake_case`, be explicit (e.g., `file_path` not `fp`)
- **Constants**: `UPPER_SNAKE_CASE` for module-level constants
- **Type aliases**: Use quotes for forward references when needed
- **Private functions**: Prefix with underscore (`_split_entries`)

### Error Handling
- Use specific exception types (`FileNotFoundError`, `UnicodeDecodeError`)
- Handle encoding issues gracefully with informative messages
- Validate file existence before processing
- Use argparse's `parser.error()` for argument validation
- Never suppress exceptions with bare `except:`

### Text Processing Patterns
- Always specify `encoding="utf-8"` for file I/O
- Use `pathlib.Path.read_text()` and `write_text()` methods
- Handle different line endings (`\r\n`, `\n`, `\r`) consistently
- Use compiled regex patterns as module-level constants
- Process text line-by-line for memory efficiency with large files

### Argument Parsing
- Use `argparse.ArgumentParser` with descriptive help text
- Provide sensible defaults (current directory, etc.)
- Include `--dry-run` flags for destructive operations
- Use `nargs="*"` for optional multiple targets
- Validate paths exist before processing

### Output & Logging
- Use consistent status prefixes: `[ok]`, `[edit]`, `[skip]`, `[dry]`
- Print summary statistics after batch operations
- Include file counts and change counts in summaries
- Use informative messages for skipped files with reasons

### Code Organization
- Keep main logic in `main()` function
- Separate parsing (`parse_args()`) from execution
- Use pure functions for text transformations
- Group related constants together at module top
- Use `if __name__ == "__main__":` guard

### Documentation
- Use module-level docstrings explaining purpose and usage
- Document all public functions with clear docstrings
- Include examples in docstrings for complex functions
- Use inline comments for non-obvious regex patterns
- Maintain README.md with current usage examples

## Project-Specific Patterns

### Chinese Text Processing
- Convert ASCII parentheses to Chinese full-width: `(` → `（`, `)` → `）`
- Handle Chinese numbering: `一、二、三、...` for news items
- Process category headers: `【京内正面】【京内负面】【京外正面】【京外负面】`
- Normalize news source names (e.g., "北京日报客户端" → "北京日报")

### File Operations
- Target `.txt` files specifically, skip other extensions
- Support both file and directory targets for batch operations
- Use `rglob("*.txt")` for recursive directory scanning
- Sort file lists for deterministic processing order
- Handle Unicode decode errors gracefully

### Category Classification
- Use keyword-based classification with predefined rules
- Maintain category priority order as tuples
- Support default category fallback
- Count entries by category for reporting

## Development Workflow
1. Always test with `--dry-run` first before making changes
2. Create sample test files for validation
3. Check file encoding assumptions (UTF-8 required)
4. Verify regex patterns with test data
5. Test edge cases (empty files, missing headers, etc.)

## Dependencies
- Python 3.8+ required
- Standard library only (no external dependencies)
- `pathlib`, `argparse`, `re`, `collections` modules used extensively