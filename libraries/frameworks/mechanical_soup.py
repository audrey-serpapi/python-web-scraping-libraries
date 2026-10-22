"""
Framework: MechanicalSoup.

HOW IT WORKS
It combines Requests (for fetching) and Beautiful Soup (for parsing) behind a "stateful browser".
MechanicalSoup opens pages, remembers cookies between requests, follows links, and can fill in and submit forms. 
That makes it a good fit when the hard part isn't parsing but getting to the data, such as
logging in or stepping through a search form. 

After each page is opened, `browser.page` is an ordinary Beautiful Soup object,
so you read it with the same CSS selectors as the first example.
There is no JavaScript engine, so it can't handle pages that build their content in
the browser, and it doesn't schedule or retry crawls the way Scrapy does.

Goodreads quotes need no login, so this example simply opens each page in turn. See the
MechanicalSoup docs for `select_form()` and `submit_selected()`, which handle forms.

Setup: 
pip install mechanicalsoup

Run: 
python3 -m libraries.frameworks.mechanical_soup
"""
import json
import time

import mechanicalsoup

from libraries.common import DELAY_SECONDS, MAX_PAGES, USER_AGENT, clean_author, clean_quote, page_url, parse_likes


def parse(soup):
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


def scrape():
    quotes = []
    browser = mechanicalsoup.StatefulBrowser(user_agent=USER_AGENT)
    for n in range(1, MAX_PAGES + 1):
        browser.open(page_url(n))
        quotes.extend(parse(browser.page))   # browser.page is a Beautiful Soup object
        time.sleep(DELAY_SECONDS)
    browser.close()
    return quotes


if __name__ == "__main__":
    data = scrape()
    with open("goodreads_mechanicalsoup.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")