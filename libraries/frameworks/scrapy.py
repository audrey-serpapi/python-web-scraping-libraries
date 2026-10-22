"""
Framework: Scrapy.

HOW IT WORKS
Scrapy is a crawling framework that manages the whole scraping workflow.

You write a spider that says where to start and how to extract data.
Scrapy handles scheduling, downloading, concurrency, retries, throttling,
and exporting the results.

The `parse()` method yields one item for each quote it finds.

Setup:
    pip install scrapy

Run (from the repo root):
    python3 -m libraries.frameworks.scrapy
"""

import scrapy
from scrapy.crawler import CrawlerProcess

from libraries.common import (
    DELAY_SECONDS,
    MAX_PAGES,
    USER_AGENT,
    clean_author,
    clean_quote,
    page_url,
    parse_likes,
)


data = []


class GoodreadsQuotesSpider(scrapy.Spider):
    name = "goodreads_quotes"

    start_urls = [
        page_url(n)
        for n in range(1, MAX_PAGES + 1)
    ]

    custom_settings = {
        "USER_AGENT": USER_AGENT,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": DELAY_SECONDS,
        "CONCURRENT_REQUESTS": 1,
        "FEEDS": {
            "goodreads_scrapy.json": {
                "format": "json",
                "indent": 2,
                "encoding": "utf-8",
            }
        },
    }

    def parse(self, response):
        for q in response.css("div.quote"):
            raw_text = "\n".join(
                q.xpath(
                    ".//div[contains(concat(' ', normalize-space(@class), ' '), "
                    "' quoteText ')]//text()"
                ).getall()
            )

            item = {
                "text": clean_quote(raw_text),
                "author": clean_author(
                    q.css("span.authorOrTitle::text").get(default="")
                ),
                "tags": [
                    tag.strip()
                    for tag in q.css(
                        "div.greyText.smallText.left a::text"
                    ).getall()
                    if tag.strip()
                ],
                "likes": parse_likes(
                    q.css(
                        "a.smallText[title='View this quote']::text"
                    ).get()
                ),
            }

            data.append(item)
            yield item


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(GoodreadsQuotesSpider)
    process.start()

    print(f"Saved {len(data)} quotes")