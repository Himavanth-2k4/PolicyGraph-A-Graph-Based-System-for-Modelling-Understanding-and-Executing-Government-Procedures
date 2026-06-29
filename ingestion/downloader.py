"""
PDF Downloader — give it a website URL and it will:
1. Crawl the page for all PDF links.
2. Download each PDF into data/raw/.
3. Return a list of downloaded file paths.

Usage from CLI:
    python ingestion/downloader.py "https://example.gov.in/schemes"

Usage from code:
    from ingestion.downloader import download_pdfs_from_url
    paths = download_pdfs_from_url("https://example.gov.in/schemes")
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

# Make project root importable when running as a script:
#   python ingestion/downloader.py "https://example.gov.in/schemes"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from logging_utils import logger, setup_logging


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitise_filename(url: str) -> str:
    """
    Turn a URL into a safe filename.
    e.g. https://example.com/docs/scheme%20guide.pdf  →  scheme_guide.pdf
    """
    parsed = urlparse(url)
    name = unquote(Path(parsed.path).name)          # decode %20 etc.
    name = re.sub(r"[^\w.\-]", "_", name)            # replace unsafe chars
    name = re.sub(r"_+", "_", name).strip("_")       # collapse underscores
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def _looks_like_pdf_link(href: str) -> bool:
    """Return True if the href likely points to a PDF."""
    if not href:
        return False
    lower = href.lower().split("?")[0].split("#")[0]  # ignore query/fragment
    return lower.endswith(".pdf")


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def find_pdf_links(page_url: str, timeout: int = 30) -> List[str]:
    """
    Fetch a webpage and return a deduplicated list of absolute URLs
    that point to PDF files.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    logger.info(f"Fetching page: {page_url}\n")
    resp = requests.get(page_url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    pdf_urls: List[str] = []
    seen: set[str] = set()

    # Strategy 1: <a> tags whose href ends with .pdf
    for tag in soup.find_all("a", href=True):
        href: str = tag["href"].strip()
        if _looks_like_pdf_link(href):
            abs_url = urljoin(page_url, href)
            if abs_url not in seen:
                seen.add(abs_url)
                pdf_urls.append(abs_url)

    # Strategy 2: <a> tags whose link text mentions "PDF" / "Download"
    # even if the URL doesn't end in .pdf (some govt portals use redirects)
    for tag in soup.find_all("a", href=True):
        text = (tag.get_text() or "").strip().lower()
        href = tag["href"].strip()
        if any(kw in text for kw in ("pdf", "download", "guidelines", "notification")):
            abs_url = urljoin(page_url, href)
            if abs_url not in seen:
                # Do a HEAD request to confirm content-type
                try:
                    head = requests.head(abs_url, headers=headers, timeout=10, allow_redirects=True)
                    ct = head.headers.get("Content-Type", "")
                    if "pdf" in ct.lower():
                        seen.add(abs_url)
                        pdf_urls.append(abs_url)
                except Exception:
                    pass  # skip unreachable links

    logger.info(f"Found {len(pdf_urls)} PDF link(s) on {page_url}\n")
    return pdf_urls


def download_pdf(
    url: str,
    save_dir: Optional[Path] = None,
    timeout: int = 120,
) -> Optional[Path]:
    """
    Download a single PDF from *url* into *save_dir* (default: data/raw/).
    Returns the saved file path, or None on failure.
    """
    save_dir = save_dir or config.paths.data_raw
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = _sanitise_filename(url)
    dest = save_dir / filename

    if dest.exists():
        logger.info(f"Already exists, skipping: {dest}\n")
        return dest

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    logger.info(f"Downloading: {url}\n")
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()

        with dest.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = dest.stat().st_size / 1024
        logger.info(f"  → Saved {filename} ({size_kb:.0f} KB)\n")
        return dest

    except Exception as exc:
        logger.error(f"  ✗ Failed to download {url}: {exc}\n")
        if dest.exists():
            dest.unlink()  # remove partial file
        return None


def download_pdfs_from_url(
    page_url: str,
    save_dir: Optional[Path] = None,
    delay: float = 0.5,
) -> List[Path]:
    """
    Main entry point: scrape a page for PDF links and download them all.

    Args:
        page_url:  The webpage to scrape (e.g. a government schemes listing page).
        save_dir:  Where to save PDFs (default: data/raw/).
        delay:     Seconds to wait between downloads (be polite to servers).

    Returns:
        List of Paths to successfully downloaded PDFs.
    """
    pdf_links = find_pdf_links(page_url)
    if not pdf_links:
        logger.warning("No PDF links found on that page.\n")
        return []

    downloaded: List[Path] = []
    for i, link in enumerate(pdf_links, 1):
        logger.info(f"[{i}/{len(pdf_links)}] ", end="")
        path = download_pdf(link, save_dir=save_dir)
        if path:
            downloaded.append(path)
        if i < len(pdf_links):
            time.sleep(delay)  # polite delay between requests

    logger.info(f"\nDone. Downloaded {len(downloaded)}/{len(pdf_links)} PDFs.\n")
    return downloaded


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    if len(sys.argv) < 2:
        print("Usage:  python ingestion/downloader.py <URL>")
        print('  e.g.  python ingestion/downloader.py "https://scholarships.gov.in/guidelines"')
        sys.exit(1)

    url = sys.argv[1]
    paths = download_pdfs_from_url(url)

    if paths:
        print(f"\n✓ {len(paths)} PDF(s) saved to {config.paths.data_raw}:")
        for p in paths:
            print(f"  • {p.name}")
    else:
        print("\n✗ No PDFs were downloaded.")


if __name__ == "__main__":
    main()
