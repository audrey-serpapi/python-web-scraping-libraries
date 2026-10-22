"""
Headless browser (AI-friendly): Crawl4AI.

HOW IT WORKS
Crawl4AI is an open-source crawler built on top of Playwright. 
Like the other browser tools it loads the page in a real (headless) browser, so JavaScript
runs and you get the finished page.

What it adds is convenience for modern projects. It is async by default, can wait for a specific element (`wait_for`), caches results, and converts
each page to clean Markdown, which is handy when the goal is feeding web content to an
LLM.

Here we use it just as a smart page fetcher. We ask for the rendered HTML, parse it
with Beautiful Soup exactly as in the first example, and also save page 1 as Markdown.

NOTE FOR THIS EXAMPLE
Goodreads quotes are server-rendered, so a browser isn't needed. 
On your own, always check whether the data is in the page source before using a dynamic library.

Setup:
    pip install crawl4ai beautifulsoup4
    crawl4ai-setup        # one-time: installs the browser it uses
Run: 
(from the repo root): python3 -m libraries.dynamic.crawl4ai
"""
import asyncio
import json

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

from libraries.common import DELAY_SECONDS, MAX_PAGES, USER_AGENT, clean_author, clean_quote, page_url, parse_likes

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for q in soup.select("div.quote"):
        likes = q.select_one("a.smallText[title='View this quote']")
        quotes.append({
            "text": clean_quote(q.select_one("div.quoteText").get_text("\n")),
            "author": clean_author(q.select_one("span.authorOrTitle").get_text()),
            "tags": [a.get_text(strip=True) for a in q.select("div.greyText.smallText.left a")],
            "likes": parse_likes(likes.get_text() if likes else ""),
        })
    return quotes


async def scrape():
    browser_config = BrowserConfig(headless=True, user_agent=USER_AGENT)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, wait_for="css:div.quote")
    quotes = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for n in range(1, MAX_PAGES + 1):
            result = await crawler.arun(url=page_url(n), config=run_config)
            if not result.success:
                raise RuntimeError(f"Page {n} failed: {result.error_message}")
            quotes.extend(parse(result.html))

            if n == 1:  # the extra Crawl4AI gives you: the page as clean Markdown
                with open("goodreads_page1.md", "w", encoding="utf-8") as f:
                    f.write(str(result.markdown))
            await asyncio.sleep(DELAY_SECONDS)
    return quotes


if __name__ == "__main__":
    data = asyncio.run(scrape())
    with open("goodreads_crawl4ai.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")