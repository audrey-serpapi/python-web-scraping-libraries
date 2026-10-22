# Python Web Scraping Libraries

Examples of popular Python tools for web scraping, using the same Goodreads Quotes task for comparison.

Each example extracts:

```text
text
author
tags
likes
```

The examples cover static scraping, browser automation, crawling frameworks, and managed scraping services.

## Tools

| Tool | Best for |
|---|---|
| Requests + Beautiful Soup | Beginners and simple scripts |
| Requests + lxml | Fast parsing and XPath |
| HTTPX + Selectolax | Fast async scraping |
| Playwright | JavaScript-heavy websites |
| Selenium | Browser automation |
| Crawl4AI | Browser crawling and AI workflows |
| Scrapy | Large, repeatable crawls |
| Crawlee | Async crawling |
| MechanicalSoup | Forms and sessions without JavaScript |
| SerpApi | Managed scraping services |

## Project structure

```text
python-web-scraping-libraries/
├── libraries/
│   ├── common.py
│   ├── static/
│   ├── dynamic/
│   ├── frameworks/
│   ├── stateful/
│   └── enterprise/
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Some browser tools require additional setup.

Playwright:

```bash
playwright install
```

Crawl4AI:

```bash
crawl4ai-setup
```

## Run an example

Run each scraper from the repository root:

```bash
python3 -m libraries.static.beautiful_soup_requests
python3 -m libraries.static.lxml_requests
python3 -m libraries.static.httpx_selectolax

python3 -m libraries.dynamic.playwright
python3 -m libraries.dynamic.selenium
python3 -m libraries.dynamic.crawl4ai

python3 -m libraries.frameworks.scrapy
python3 -m libraries.frameworks.crawlee

python3 -m libraries.stateful.mechanical_soup

python3 -m libraries.enterprise.serpapi
```

The examples save their results as JSON files.

## Configuration

Shared settings are in `libraries/common.py`.

```python
BASE_URL = "https://www.goodreads.com/quotes"
DELAY_SECONDS = 1
MAX_PAGES = 10
```

The examples use the same pages, fields, and output format so the tools can be compared directly.

## Choosing a tool

Start with the simplest tool that fits the page:

- **Static HTML:** Requests + Beautiful Soup
- **Fast parsing:** Requests + lxml
- **Async scraping:** HTTPX + Selectolax
- **JavaScript:** Playwright or Selenium
- **Larger crawls:** Scrapy or Crawlee
- **Forms without JavaScript:** MechanicalSoup
- **Managed scraping:** SerpApi

If the site provides an API, use it instead of scraping when possible.

## Article

This repository accompanies the article **Getting Started with Web Scraping in Python**, which explains how to identify the type of data a website serves and choose an appropriate scraping tool.

[Read the article](<article URL>)

## Notes

Scrape responsibly. Check the site's `robots.txt` and terms of service, use reasonable request rates, and avoid unnecessary concurrency.