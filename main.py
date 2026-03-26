import argparse
from pathlib import Path
from crawler import crawl

PROJECT_DIR = Path(__file__).parent


def parse_chapter_range(value: str) -> tuple[int, int] | None:
    """Parse '1-10' into (1, 10). Returns None if not provided."""
    if not value:
        return None
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
    parser = argparse.ArgumentParser(description="Syosetu novel crawler")
    parser.add_argument(
        "url",
        help="Novel URL, e.g. https://ncode.syosetu.com/n9636x/",
    )
    parser.add_argument(
        "--chapters",
        metavar="START-END",
        type=parse_chapter_range,
        default=None,
        help="Chapter range to download, e.g. 1-10 (default: all chapters)",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_DIR / "output"),
        help="Output directory (default: <project>/output)",
    )
    args = parser.parse_args()

    crawl(
        novel_url=args.url,
        output_dir=args.output,
        chapter_range=args.chapters,
    )
