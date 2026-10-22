"""
Headless browser: Selenium.

HOW IT WORKS

Selenium starts a headless Chrome browser, opens a page, lets the JavaScript
run, and then reads the finished result. 

The main difference in style compared to Playwright is waiting. You tell Selenium
what to wait for (here, a quote element showing up) with an "explicit wait" 
so your code doesn't read the page before it's ready. 
As with any browser tool, expect it to be slower than plain HTTP requests.

NOTE FOR THIS EXAMPLE
Goodreads quotes are server-rendered, so a browser isn't needed. 
On your own, always check whether the data is in the page source before using a dynamic library.

Setup: 
pip install selenium   

Note: Google Chrome must be installed. Selenium downloads the matching driver for you.

Run: 
(from the repo root): 
python3 -m libraries.dynamic.selenium
"""
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from libraries.common import (
    DELAY_SECONDS, MAX_PAGES, USER_AGENT,
    clean_author, clean_quote, page_url, parse_likes,
)


def parse(driver):
    quotes = []
    for q in driver.find_elements(By.CSS_SELECTOR, "div.quote"):
        # find_elements (plural) returns an empty list when nothing matches, instead of an error
        likes = q.find_elements(By.CSS_SELECTOR, "a.smallText[title='View this quote']")
        tags = q.find_elements(By.CSS_SELECTOR, "div.greyText.smallText.left a")
        quotes.append({
            "text": clean_quote(q.find_element(By.CSS_SELECTOR, "div.quoteText").text),
            "author": clean_author(q.find_element(By.CSS_SELECTOR, "span.authorOrTitle").text),
            "tags": [t.text for t in tags],
            "likes": parse_likes(likes[0].text if likes else ""),
        })
    return quotes


def scrape():
    options = Options()
    options.add_argument("--headless=new")               
    options.add_argument(f"--user-agent={USER_AGENT}")   
    quotes = []

    with webdriver.Chrome(options=options) as driver:    
        wait = WebDriverWait(driver, 15)                 # wait up to 15 seconds for elements
        for n in range(1, MAX_PAGES + 1):
            driver.get(page_url(n))
            # explicit wait: pause until at least one quote is in the page
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote")))
            quotes.extend(parse(driver))
            time.sleep(DELAY_SECONDS)                    # pause between pages to be polite
    return quotes


if __name__ == "__main__":
    data = scrape()
    with open("goodreads_selenium.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} quotes")