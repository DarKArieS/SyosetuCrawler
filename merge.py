import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).parent


def merge(input_dir: str, output_file: str, chapter_range: tuple[int, int] | None = None):
    src = Path(input_dir)
    if not src.exists():
        print(f"ERROR: Input directory not found: {src}")
        return

    txt_files = sorted(src.glob("*.txt"), key=lambda f: f.name)

    if chapter_range is not None:
        start, end = chapter_range
        txt_files = [
            f for f in txt_files
            if (m := __import__("re").match(r"^(\d+)_", f.name)) and start <= int(m.group(1)) <= end
        ]

    if not txt_files:
        print("No matching chapter files found.")
        return

    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as fp:
        for i, chapter_file in enumerate(txt_files):
            content = chapter_file.read_text(encoding="utf-8")
            fp.write(content)
            if i < len(txt_files) - 1:
                fp.write("\n\n" + "=" * 40 + "\n\n")

    print(f"Merged {len(txt_files)} chapters → {out}")


def parse_chapter_range(value: str) -> tuple[int, int]:
    parts = value.split("-")
    if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
        raise argparse.ArgumentTypeError(
            f"Invalid range '{value}'. Expected format: START-END (e.g. 1-10)"
        )
    start, end = int(parts[0]), int(parts[1])
    if start < 1 or start > end:
        raise argparse.ArgumentTypeError(
            f"Invalid range '{value}'. START must be >= 1 and <= END."
        )
    return start, end


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge chapter txt files into one file")
    parser.add_argument(
        "--input",
        default=str(PROJECT_DIR / "output"),
        help="Input directory containing chapter txt files (default: <project>/output)",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_DIR / "output" / "merged.txt"),
        help="Output file path (default: <project>/output/merged.txt)",
    )
    parser.add_argument(
        "--chapters",
        metavar="START-END",
        type=parse_chapter_range,
        default=None,
        help="Merge only a chapter range, e.g. 1-10 (default: all chapters)",
    )
    args = parser.parse_args()

    merge(
        input_dir=args.input,
        output_file=args.output,
        chapter_range=args.chapters,
    )
