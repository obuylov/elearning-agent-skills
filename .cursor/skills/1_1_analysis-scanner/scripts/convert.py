"""
Batch conversion of source files to Markdown using MarkItDown.

Usage:
    python convert.py [--source DIR] [--output DIR] [--force]

Defaults:
    --source  sources/original
    --output  sources/converted
    --force   re-convert even if .md already exists

Features:
    - Recursively scans subdirectories in source folder
    - Preserves subdirectory structure in output folder
    - Outputs basic quality metrics for each converted file
    - Cross-platform (Windows / macOS / Linux)
"""

import argparse
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx",
    ".html", ".htm",
    ".csv", ".json", ".xml",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
    ".wav", ".mp3",
    ".zip",
    ".epub",
}

# Patterns that indicate OCR artifacts or encoding issues
GARBAGE_PATTERNS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]|[ÿ□■]{3,}|(.)\1{10,}')


def find_project_root() -> Path:
    """Walk up from script location to find project-state.json."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "project-state.json").exists():
            return current
        current = current.parent
    return Path.cwd()


def analyze_quality(text: str) -> dict:
    """Analyze converted markdown quality and return metrics."""
    words = text.split()
    word_count = len(words)

    # Count headings (H1-H3)
    headings = re.findall(r'^#{1,3}\s+.+', text, re.MULTILINE)
    heading_count = len(headings)

    # Count markdown tables (lines with | separators)
    table_rows = re.findall(r'^\|.+\|', text, re.MULTILINE)
    table_separators = re.findall(r'^\|[\s\-:|]+\|', text, re.MULTILINE)
    has_tables = len(table_rows) > 0
    tables_valid = len(table_separators) > 0 if has_tables else True

    # Check for garbage characters
    garbage_matches = GARBAGE_PATTERNS.findall(text)
    has_garbage = len(garbage_matches) > 5

    # Determine quality
    if word_count < 10:
        quality = "empty"
    elif has_garbage:
        quality = "poor"
    elif (has_tables and not tables_valid) or (word_count > 1000 and heading_count == 0):
        quality = "degraded"
    else:
        quality = "good"

    return {
        "word_count": word_count,
        "heading_count": heading_count,
        "has_tables": has_tables,
        "tables_valid": tables_valid,
        "has_garbage": has_garbage,
        "quality": quality,
    }


def main():
    parser = argparse.ArgumentParser(description="Convert source files to Markdown via MarkItDown")
    parser.add_argument("--source", type=str, default=None, help="Source directory (default: sources/original)")
    parser.add_argument("--output", type=str, default=None, help="Output directory (default: sources/converted)")
    parser.add_argument("--force", action="store_true", help="Re-convert even if .md already exists")
    args = parser.parse_args()

    root = find_project_root()

    source_dir = Path(args.source) if args.source else root / "sources" / "original"
    output_dir = Path(args.output) if args.output else root / "sources" / "converted"

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Recursive scan: find all supported files in source_dir and subdirectories
    source_files = sorted([
        f for f in source_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not source_files:
        print(f"No supported files found in {source_dir} (including subdirectories)")
        print(f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        sys.exit(0)

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("markitdown is not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markitdown[all]"])
        from markitdown import MarkItDown

    md = MarkItDown()

    converted = 0
    skipped = 0
    failed = 0
    quality_issues = []

    # Collect unique subdirectories for summary
    subdirs_used = set()

    print(f"Source:  {source_dir}")
    print(f"Output:  {output_dir}")
    print(f"Files:   {len(source_files)}")
    print(f"Force:   {args.force}")
    print("-" * 60)

    for src_file in source_files:
        # Calculate relative path to preserve subdirectory structure
        relative_path = src_file.relative_to(source_dir)
        out_file = output_dir / relative_path.with_suffix(".md")

        # Create subdirectory in output if needed
        if relative_path.parent != Path("."):
            subdirs_used.add(str(relative_path.parent))
            out_file.parent.mkdir(parents=True, exist_ok=True)

        if out_file.exists() and not args.force:
            print(f"  SKIP  {relative_path} → already exists")
            skipped += 1
            continue

        try:
            result = md.convert(str(src_file))
            out_file.write_text(result.markdown, encoding="utf-8")

            # Analyze quality of converted file
            metrics = analyze_quality(result.markdown)
            quality_tag = metrics["quality"].upper()
            print(
                f"  OK    {relative_path} → {out_file.relative_to(output_dir)}  "
                f"[{quality_tag}  words:{metrics['word_count']}  "
                f"headings:{metrics['heading_count']}  "
                f"tables:{'yes' if metrics['has_tables'] else 'no'}]"
            )

            if metrics["quality"] != "good":
                quality_issues.append((str(relative_path), metrics))

            converted += 1
        except Exception as e:
            print(f"  FAIL  {relative_path} → {e}")
            failed += 1

    print("-" * 60)
    print(f"Done: {converted} converted, {skipped} skipped, {failed} failed")

    if subdirs_used:
        print(f"Subdirectories preserved: {', '.join(sorted(subdirs_used))}")

    # Quality summary
    if quality_issues:
        print()
        print("⚠ QUALITY ISSUES DETECTED:")
        for filename, metrics in quality_issues:
            reasons = []
            if metrics["quality"] == "empty":
                reasons.append(f"nearly empty ({metrics['word_count']} words)")
            if metrics["has_garbage"]:
                reasons.append("garbage/OCR artifacts detected")
            if metrics["has_tables"] and not metrics["tables_valid"]:
                reasons.append("broken tables (missing separators)")
            if metrics["word_count"] > 1000 and metrics["heading_count"] == 0:
                reasons.append("no headings in large file")
            print(f"  {filename}: {metrics['quality']} — {', '.join(reasons)}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
