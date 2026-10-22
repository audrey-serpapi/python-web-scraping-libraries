"""Static scraping: requests (HTTP client) + lxml (fast parser, XPath).

HOW IT WORKS
As with the Beautiful Soup example, `requests` downloads the page and a parser reads it.
lxml is built on fast C libraries, so it handles large pages quickly. It is usually used
with XPath, a query language that describes a path through the page's elements.

A few XPath basics (all used below):
    //div[...]               every <div> anywhere in the page that matches the condition
    .//span[...]             a <span> inside the current element only (the leading dot matters)
    contains(@class, 'x')    the element's class attribute contains the text "x"
    //text()                 all the text inside an element
    string(...)              all the text inside an element, joined into one string

XPath takes longer to learn than CSS selectors, but it is very precise and can do things
CSS can't, such as selecting an element based on its text.

Setup: pip install requests lxml
Run (from the repo root): python3 -m libraries.static.lxml_requests
"""
import json
import time

import requests
from lxml import html as lxml_html

from libraries.common import (
    DELAY_SECONDS, MAX_PAGES, USER_AGENT,
    clean_author, clean_quote, page_url, parse_likes,
)

# The XPath expressions for each piece of data, named so parse() is easier to understand
QUOTES = "//div[contains(concat(' ', normalize-space(@class), ' '), ' quote ')]"
TEXT = ".//div[contains(concat(' ', normalize-space(@class), ' '), ' quoteText ')]//text()"
AUTHOR = "string(.//span[contains(concat(' ', normalize-space(@class), ' '), ' authorOrTitle ')])"
TAGS = ".//div[contains(concat(' ', normalize-space(@class), ' '), ' greyText ') and contains(concat(' ', normalize-space(@class), ' '), ' smallText ') and contains(concat(' ', normalize-space(@class), ' '), ' left ')]/a/text()"
LIKES = "string(.//a[@title='View this quote'])"


def parse(html):
    tree = lxml_html.fromstring(html)
    quotes = []
    for quote in tree.xpath(QUOTES):
        quotes.append({
            "text": clean_quote("\n".join(quote.xpath(TEXT))),
            "author": clean_author(quote.xpath(AUTHOR)),
            "tags": [tag.strip() for tag in quote.xpath(TAGS)],
            "likes": parse_likes(quote.xpath(LIKES)),
        })
    return quotes


def scrape():
    quotes = []
    with requests.Session() as session:
        session.headers["User-Agent"] = USER_AGENT
        for n in range(1, MAX_PAGES + 1):
            response = session.get(page_url(n), timeout=15)
            response.raise_for_status()
            quotes.extend(parse(response.text))   # .text decodes using the page's declared charset
            time.sleep(DELAY_SECONDS)             # pause between pages to be polite
    return quotes


if __name__ == "__main__":
    data = scrape()
    with open("goodreads_requests_lxml.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")