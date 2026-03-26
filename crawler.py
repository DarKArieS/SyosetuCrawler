import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ncode.syosetu.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
REQUEST_DELAY = 1.0  # seconds between requests


def _fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "lxml")


def _sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()


def get_chapter_links(novel_url: str) -> list[tuple[int, str, str]]:
    """Return list of (chapter_number, chapter_title, absolute_url) for all chapters."""
    # Extract novel code from URL, e.g. "n9636x" from https://ncode.syosetu.com/n9636x/
    novel_code = urlparse(novel_url).path.strip("/")
    chapter_href_re = re.compile(rf"^/{re.escape(novel_code)}/(\d+)/?$")

    seen = set()
    chapters = []
    page_url = novel_url

    while page_url:
        soup = _fetch(page_url)
        time.sleep(REQUEST_DELAY)

        for a in soup.find_all("a", href=chapter_href_re):
            href = a["href"]
            if href in seen:
                continue
            seen.add(href)
            m = chapter_href_re.match(href)
            chapter_num = int(m.group(1))
            title = a.get_text(strip=True)
            chapters.append((chapter_num, title, urljoin(BASE_URL, href)))

        # Check for next page ("次へ")
        next_link = soup.find("a", string=re.compile(r"次へ"))
        if next_link and next_link.get("href"):
            page_url = urljoin(BASE_URL, next_link["href"])
        else:
            page_url = None

    # Sort by chapter number (order in HTML is not guaranteed across pages)
    chapters.sort(key=lambda x: x[0])
    return chapters


def get_chapter_content(chapter_url: str) -> tuple[str, str]:
    """Return (title, body_text) for a chapter page."""
    soup = _fetch(chapter_url)

    # Title: try known selectors, fall back to <h1>
    title = ""
    for selector in (
        ("p", {"class_": "novel_subtitle"}),
        ("h1", {"class_": "p-novel__title"}),
        ("h1", {}),
    ):
        tag, kwargs = selector
        found = soup.find(tag, **kwargs)
        if found:
            title = found.get_text(strip=True)
            break

    # Body: try known selectors, fall back to largest <div> with <p> children
    body = ""
    for selector in (
        ("div", {"id": "novel_honbun"}),
        ("div", {"class_": "p-novel__body"}),
    ):
        tag, kwargs = selector
        found = soup.find(tag, **kwargs)
        if found:
            paragraphs = [p.get_text() for p in found.find_all("p")]
            body = "\n".join(paragraphs)
            break

    return title, body


def save_chapter(output_dir: Path, chapter_number: int, title: str, body: str):
    safe_title = _sanitize_filename(title)
    filename = output_dir / f"{chapter_number:04d}_{safe_title}.txt"
    filename.write_text(f"{title}\n\n{body}", encoding="utf-8")
    return filename


def crawl(
    novel_url: str,
    output_dir: str = "output",
    chapter_range: tuple[int, int] | None = None,
):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Fetching chapter list from {novel_url} ...")
    chapters = get_chapter_links(novel_url)
    print(f"Found {len(chapters)} chapters.")

    if chapter_range is not None:
        start, end = chapter_range
        chapters = [(n, t, u) for n, t, u in chapters if start <= n <= end]
        print(f"Filtering to chapters {start}-{end} ({len(chapters)} chapters).")

    for chapter_number, chapter_title, chapter_url in chapters:
        # Resume: skip if any file starting with this number already exists
        existing = list(out.glob(f"{chapter_number:04d}_*.txt"))
        if existing:
            print(f"[{chapter_number}/{len(chapters)}] Skip (already saved): {chapter_title}")
            continue

        print(f"[{chapter_number}/{len(chapters)}] Downloading: {chapter_title}")
        try:
            title, body = get_chapter_content(chapter_url)
            saved_path = save_chapter(out, chapter_number, title, body)
            print(f"  Saved → {saved_path.name}")
        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(REQUEST_DELAY)

    print("Done.")
