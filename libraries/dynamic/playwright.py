"""
Headless browser: Playwright.

HOW IT WORKS

Playwright launches a real browser engine to access JavaScript rendered data.
"Headless" means the browser runs without showing a window. 

The script opens a page, waits for the elements it needs to appear, and reads
them from the finished page, using "locators" to find elements. 

The tradeoff is cost. Browsers are slower and use much more memory than a plain request.

NOTE FOR THIS EXAMPLE
Goodreads quotes are server-rendered, so a browser isn't needed. 
On your own, always check whether the data is in the page source before using a dynamic library.


Setup: pip install playwright && playwright install chromium
Run: 
(from the repo root): python3 -m libraries.dynamic.playwright
"""
import json

from playwright.sync_api import sync_playwright

from libraries.common import DELAY_SECONDS, MAX_PAGES, USER_AGENT, clean_author, clean_quote, page_url, parse_likes


def scrape():
    quotes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)

        for n in range(1, MAX_PAGES + 1):
            page.goto(page_url(n))
            page.wait_for_selector("div.quote")

            for q in page.locator("div.quote").all():
                likes = q.locator("a.smallText[title='View this quote']")
                quotes.append({
                    "text": clean_quote(q.locator("div.quoteText").inner_text()),
                    "author": clean_author(q.locator("span.authorOrTitle").first.inner_text()),
                    "tags": q.locator("div.greyText.smallText.left a").all_inner_texts(),
                    "likes": parse_likes(likes.first.inner_text() if likes.count() else ""),
                })
            page.wait_for_timeout(DELAY_SECONDS * 1000)

        browser.close()
    return quotes


if __name__ == "__main__":
    data = scrape()
    with open("goodreads_playwright.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")