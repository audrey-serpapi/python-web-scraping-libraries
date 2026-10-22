"""
Managed service: SerpApi Extract API.

HOW IT WORKS
SerpApi's Extract API fetches each Goodreads quotes page for us and returns
the raw HTML. Beautiful Soup then parses that HTML locally, producing the
same quote fields as the other scraping examples.

Setup:
    pip install requests beautifulsoup4

    Get an API key at https://serpapi.com/users/sign_up, then set it as
    an environment variable:

        export SERPAPI_KEY="your_key"

Run (from the repo root):
    python3 -m libraries.enterprise.<your_filename>
"""

import json
import os

import requests
from bs4 import BeautifulSoup

from libraries.common import (
    MAX_PAGES,
    clean_author,
    clean_quote,
    page_url,
    parse_likes,
)


API_KEY = os.environ["SERPAPI_KEY"]


def scrape():
    quotes = []

    for n in range(1, MAX_PAGES + 1):
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "extract",
                "url": page_url(n),
                "api_key": API_KEY,
                "output": "html",
            },
            timeout=60,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for q in soup.select("div.quote"):
            likes = q.select_one(
                "a.smallText[title='View this quote']"
            )

            quotes.append({
                "text": clean_quote(
                    q.select_one("div.quoteText").get_text("\n")
                ),
                "author": clean_author(
                    q.select_one("span.authorOrTitle").get_text()
                ),
                "tags": [
                    a.get_text(strip=True)
                    for a in q.select("div.greyText.smallText.left a")
                ],
                "likes": parse_likes(
                    likes.get_text() if likes else ""
                ),
            })

    return quotes


if __name__ == "__main__":
    data = scrape()

    with open("goodreads_serpapi.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} quotes")