"""Static scraping at speed: HTTPX (async client) + Selectolax (fast parser, lexbor backend).

HOW IT WORKS
HTTPX is a lot like the requests library, but it can also work asynchronously.

A normal script requests one page, waits for the answer, then requests the next. 
An async script can start several requests and wait for them together, so the program isn't sitting
idle while the network responds.

Here, asyncio runs the requests, and a semaphore caps how many are in flight at once
(it's set low to stay polite).
 Selectolax, a thin Python wrapper around a fast HTML engine written in C, then does the parsing.
It uses the same CSS selectors as Beautiful Soup, but is much quicker on big jobs.

Setup: pip install httpx selectolax
Run (from the repo root): python3 -m libraries.static.httpx_selectolax
"""
import asyncio
import json

import httpx
from selectolax.lexbor import LexborHTMLParser

from libraries.common import (
    DELAY_SECONDS, MAX_PAGES, USER_AGENT,
    clean_author, clean_quote, page_url, parse_likes,
)

CONCURRENCY = 2  # at most 2 requests in flight at once


def parse(html):
    # `html` is a string holding the whole page. The parser builds a searchable tree from it.
    tree = LexborHTMLParser(html)
    quotes = []

    # css() returns every match as a list: one element per quote on the page
    for q in tree.css("div.quote"):
        # the like count is a link whose title attribute is "View this quote"
        likes = q.css_first("a.smallText[title='View this quote']")
        quotes.append({
            # text() gets the text inside an element; separator="\n" keeps line breaks
            "text": clean_quote(q.css_first("div.quoteText").text(separator="\n")),
            "author": clean_author(q.css_first("span.authorOrTitle").text()),
            # strip=True trims the whitespace around each tag's text
            "tags": [a.text(strip=True) for a in q.css("div.greyText.smallText.left a")],
            "likes": parse_likes(likes.text() if likes else ""),
        })
    return quotes


async def fetch(client, semaphore, n):
    """Download page n. `await` means "wait here, but let other downloads keep going"."""
    async with semaphore:                  # wait for a free slot 
        response = await client.get(page_url(n))
        response.raise_for_status()
        await asyncio.sleep(DELAY_SECONDS)  # keep the slot busy a moment to space out requests
        return response.text


async def scrape():
    semaphore = asyncio.Semaphore(CONCURRENCY)
    # AsyncClient is HTTPX's async version of a requests.Session: it reuses connections and
    # applies these settings to every request.
    async with httpx.AsyncClient(timeout=15, follow_redirects=True,
                                 headers={"User-Agent": USER_AGENT}) as client:
        # start every download, then collect the results (returned in page order)
        pages = await asyncio.gather(*(fetch(client, semaphore, n) for n in range(1, MAX_PAGES + 1)))

    quotes = []
    for html in pages:
        quotes.extend(parse(html))
    return quotes


if __name__ == "__main__":
    data = asyncio.run(scrape())
    with open("goodreads_httpx_selectolax.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")