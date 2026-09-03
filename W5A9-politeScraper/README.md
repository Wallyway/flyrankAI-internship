# W5A9 — The polite scraper

A small, polite scraping pipeline over [Books to Scrape](https://books.toscrape.com/):
fetch → extract → normalize → validate → store → report.

## Target classification

| Question | Answer |
| --- | --- |
| **Which site?** | `https://books.toscrape.com/` |
| **Why this one?** | [toscrape.com](https://toscrape.com/) calls itself a "Web Scraping Sandbox" and describes this site in its own words as "a fictional bookstore that **desperately wants to be scraped** ... a **safe place** for beginners learning web scraping". That sentence on their page is the permission this run stands on. |
| **How much?** | Only the first **3 catalogue pages** (`catalogue/page-1.html` → `page-3.html`), which is 60 book detail pages. The crawler follows the site's own "next" link and stops after the third page. |
| **What data?** | Per book: title, product URL, price text, availability text, rating text, description, plus the source page and fetch time. Public catalogue data only — no accounts, no personal data. |
| **Why is that appropriate?** | The site exists specifically so people can practise scraping, the volume is tiny and bounded (63 requests, once, then cached), and every request identifies itself with a real user-agent and waits 500 ms. |

### Robots check

Requested `https://books.toscrape.com/robots.txt` once:

```
$ curl -s -o /dev/null -w "%{http_code}" https://books.toscrape.com/robots.txt
404
```

**No robots file found.** A missing file is not permission — it is just a missing file. The permission here comes from the sandbox statement on toscrape.com, not from the absence of `robots.txt`.

### Why not eBay

The first target I considered was eBay's Apple laptop listings. I dropped it before writing any request code: eBay's User Agreement forbids automated data collection without written consent, and their `robots.txt` disallows the search paths those listings live on. A missing permission is a "no", so the target became the sandbox that says "yes" out loud.

> I will not reuse this code on another site without checking its rules and terms first.

## Status

Stage 0 complete — target classified, scope fixed at 3 catalogue pages, robots result recorded.
