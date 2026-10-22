"""Shared constants and helper functions for web scraping examples."""

import re
from urllib.parse import urljoin


# Configuration
BASE_URL = "https://www.goodreads.com/quotes"
DELAY_SECONDS = 1
MAX_PAGES = 10
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def clean_author(author):
    """Remove leading and trailing whitespace from an author name."""
    if not author:
        return ""
    return " ".join(author.split())


def clean_quote(quote):
    """Normalize whitespace in quote text."""
    if not quote:
        return ""
    return " ".join(quote.split())


def page_url(page_number):
    """Build the URL for a Goodreads quotes page."""
    if page_number < 1:
        raise ValueError("page_number must be at least 1")

    if page_number == 1:
        return BASE_URL

    return f"{BASE_URL}?page={page_number}"


def parse_likes(text):
    """Extract a numeric like count from text."""
    if not text:
        return 0

    match = re.search(r"[\d,]+", str(text))

    if not match:
        return 0

    return int(match.group().replace(",", ""))
