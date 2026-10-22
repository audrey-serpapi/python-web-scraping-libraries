"""
Framework: Crawlee for Python.

HOW IT WORKS
Crawlee is a crawling framework, so like Scrapy it manages the whole workflow
rather than just one step.

You create a crawler, attach a handler that runs on every page it downloads,
and give it a list of starting URLs. Crawlee manages the request queue,
retries, concurrency, and dataset storage.

Here we use Crawlee's BeautifulSoupCrawler, so the downloaded HTML is
available as `context.soup` and can be parsed with familiar CSS selectors.

Setup:
    pip install "crawlee[beautifulsoup]"

Run (from the repo root):
    python3 -m libraries.frameworks.crawlee
"""

import asyncio
import json

from crawlee import ConcurrencySettings
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from libraries.common import (
    DELAY_SECONDS,
    MAX_PAGES,
    clean_author,
    clean_quote,
    page_url,
    parse_likes,
)


async def scrape():
    crawler = BeautifulSoupCrawler(
        max_requests_per_crawl=MAX_PAGES,
        # Keep requests sequential and limit the request rate.
        concurrency_settings=ConcurrencySettings(
            desired_concurrency=1,
            max_concurrency=1,
            max_tasks_per_minute=60 // max(DELAY_SECONDS, 1),
        ),
    )

    @crawler.router.default_handler
    async def handle_page(context: BeautifulSoupCrawlingContext) -> None:
        # The handler runs once for each downloaded page.
        for q in context.soup.select("div.quote"):
            likes = q.select_one(
                "a.smallText[title='View this quote']"
            )

            # Push each quote as its own dataset item so the final result
            # is a flat list, just like the other scraper examples.
            await context.push_data({
                "text": clean_quote(
                    q.select_one("div.quoteText").get_text("\n")
                ),
                "author": clean_author(
                    q.select_one("span.authorOrTitle").get_text()
                ),
                "tags": [
                    a.get_text(strip=True)
                    for a in q.select(
                        "div.greyText.smallText.left a"
                    )
                ],
                "likes": parse_likes(
                    likes.get_text() if likes else ""
                ),
            })

    await crawler.run(
        [page_url(n) for n in range(1, MAX_PAGES + 1)]
    )

    dataset = await crawler.get_data()
    return dataset.items


if __name__ == "__main__":
    data = asyncio.run(scrape())

    with open(
        "goodreads_crawlee.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} quotes")