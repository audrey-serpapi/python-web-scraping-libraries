"""
Static scraping: requests (HTTP client) + Beautiful Soup (HTML parser).

HOW IT WORKS
Scraping a static page takes two steps, and this example uses one tool for each.

First, `requests` acts like a very simple browser: it asks the server for a page and
hands back the HTML as plain text. 

Second, Beautiful Soup reads that text and turns it into a tree of elements you can search. 
You describe what you want with CSS selectors (the same ones used to style web pages), such as "div.quote" for "every
<div> with the class quote", and it returns matching elements whose text you can
pull out. 

Setup:
pip install requests beautifulsoup4
Run:
(from the repo root): python3 -m libraries.static.beautiful_soup_requests
"""


import json
import time

import requests
from bs4 import BeautifulSoup

# clean_quote, clean_author and parse_likes (in common.py) tidy up the raw text
from libraries.common import DELAY_SECONDS, MAX_PAGES, USER_AGENT, clean_author, clean_quote, page_url, parse_likes

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for q in soup.select("div.quote"):
        # the like count is a link whose title attribute is "View this quote"
        likes = q.select_one("a.smallText[title='View this quote']")
        quotes.append({
            #keep line breaks in multi-line quotes
            "text": clean_quote(q.select_one("div.quoteText").get_text("\n")),
            "author": clean_author(q.select_one("span.authorOrTitle").get_text()),
            "tags": [a.get_text(strip=True) for a in q.select("div.greyText.smallText.left a")],
            "likes": parse_likes(likes.get_text() if likes else ""),
        })
    return quotes


def scrape():
    quotes = []
    with requests.Session() as session:
        session.headers["User-Agent"] = USER_AGENT
        for n in range(1, MAX_PAGES + 1):
            response = session.get(page_url(n), timeout=15)
            response.raise_for_status()
            quotes.extend(parse(response.text))
            time.sleep(DELAY_SECONDS)
    return quotes


if __name__ == "__main__":
    data = scrape()
    with open("goodreads_requests_bs4.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")