# W5A9 — The polite scraper

A small, polite scraping pipeline over [Books to Scrape](https://books.toscrape.com/):
**fetch → extract → normalize → validate → store → report.**

It downloads the first three catalogue pages, follows the site's own "next" link, visits all 60 book
pages, turns messy HTML into checked JSON, survives a broken page without crashing, and ends every
run with an honest report.

## Run it in five minutes

```bash
cd W5A9-politeScraper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

That one command produces `output/books.json` (60 validated records), `output/errors.json`, and
`output/run-report.json`. The first run takes ~42 s because it politely waits 500 ms between the 63
real requests; every run after that reads from `cache/` and finishes in well under a second.

To prove a broken page cannot kill the run:

```bash
python src/main.py --inject-failure
```

**Lane:** Python 3.10+ · [Requests](https://requests.readthedocs.io/) for HTTP ·
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for parsing ·
[Pydantic](https://docs.pydantic.dev/) for schema validation · the standard `json` module for output.

## Target classification

| Question | Answer |
| --- | --- |
| **Which site?** | `https://books.toscrape.com/` |
| **Why this one?** | [toscrape.com](https://toscrape.com/) calls itself a "Web Scraping Sandbox" and describes this site in its own words as "a fictional bookstore that **desperately wants to be scraped** ... a **safe place** for beginners learning web scraping". That sentence on their page is the permission this run stands on. |
| **How much?** | Only the first **3 catalogue pages** (`catalogue/page-1.html` → `page-3.html`), which is 60 book detail pages — 63 requests total, once, then cached. The crawler follows the site's own "next" link and stops after the third page; the 60 book URLs are never hardcoded. |
| **What data?** | Per book: title, product URL, price, availability, rating, description, plus the source page and fetch time. Public catalogue data only — no accounts, no personal data, no images. |
| **Why is that appropriate?** | The site exists specifically so people can practise scraping, the volume is tiny and bounded, and every request identifies itself and waits its turn. |

### Robots check

Requested `https://books.toscrape.com/robots.txt` once:

```
$ curl -s -o /dev/null -w "%{http_code}" https://books.toscrape.com/robots.txt
404
```

**No robots file found.** A missing file is not permission — it is just a missing file. The
permission here comes from the sandbox statement on toscrape.com, not from the absence of a
`robots.txt`.

### Why not eBay

The first target I considered was eBay's Apple laptop listings. I dropped it before writing any
request code: eBay's User Agreement forbids automated data collection without written consent, and
their `robots.txt` disallows the search paths those listings live on. A missing permission is a "no",
so the target became the sandbox that says "yes" out loud.

> I will not reuse this code on another site without checking its rules and terms first.

## Politeness rules

| Rule | How it is enforced |
| --- | --- |
| **Honest user-agent** | Every request sends `FlyRankInternshipA9/1.0 (+https://github.com/Wallyway/flyrankAI-internship)`, so a site owner reading their logs can find out who I am. |
| **Timeout** | 10 s. A request gives up instead of hanging forever. |
| **Delay** | At least 500 ms between real requests, measured from the end of the previous one. Cache reads wait for nothing — they never leave my machine. |
| **Status check** | The status code is checked *before* the body is touched. Only `200` is treated as HTML. |
| **Cache** | Every page is saved to `cache/` on first download and read from disk afterwards. Developing this script meant dozens of runs; the site felt 63 requests. |
| **Retry discipline** | One retry, after a 2 s pause, for a timeout, a connection error, or a `5xx`. Never for a `404` (the page does not exist — asking again will not create it) or a `403` (the site said no — asking again is how a polite robot becomes a pest). |

`cache/` is in `.gitignore` — the repo carries the code and one sample output, not hundreds of HTML files.

## The record schema

Defined once in [`src/schema.py`](src/schema.py) and validated with Pydantic **before** anything is
stored. A record that fails goes to `output/errors.json` with its reason; it never reaches
`books.json`.

| Field | Type | Notes |
| --- | --- | --- |
| `title` | `str` | Non-empty. |
| `product_url` | `str` | Must be absolute `https://`. This is the record's **canonical URL** — its identity. |
| `price_text` | `str` | The raw value exactly as the page showed it, e.g. `£51.77`. |
| `price_gbp` | `float` | The clean value, `51.77`. Raw and clean live side by side. |
| `availability_text` | `str` | e.g. `In stock (22 available)`, whitespace collapsed. |
| `rating_text` | `str` | e.g. `Three`, read from the `star-rating` class. |
| `description` | `str \| null` | **Optional.** `null` when the page has no description — never invented. |
| `source_page` | `str` | Which catalogue page led here. |
| `fetched_at` | `str` | UTC `YYYY-MM-DDTHH:MM:SSZ`. |

The last two are **provenance** — the receipt showing where and when a fact came from.

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "It's hard to imagine a world without A Light in the Attic. ...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-09-03T22:43:33Z"
}
```

### Idempotency

Running the scraper twice produces the same 60 records, not 120. Three things make that true:
`product_url` is the identity and duplicates collapse into it, `books.json` is rewritten rather than
appended to, and on a cache hit `fetched_at` comes from the cached file's modification time instead
of "now" — otherwise every rerun would rewrite all 60 records with a new timestamp and only *look*
idempotent. Runs one and two are byte-identical.

## Proof — a real run report

A cold run with an empty cache (`output/run-report.json`, committed):

```json
{
  "started_at": "2026-09-03T22:43:31Z",
  "finished_at": "2026-09-03T22:44:13Z",
  "duration_seconds": 41.77,
  "catalogue_pages": 3,
  "discovered": 60,
  "unique_urls": 60,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0,
  "failures": []
}
```

And the same pipeline with `--inject-failure`, which adds one made-up book URL. The run finishes, the
60 good records survive, and the report says so out loud:

```json
{
  "started_at": "2026-09-03T22:42:49Z",
  "duration_seconds": 0.59,
  "catalogue_pages": 3,
  "unique_urls": 61,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failures": [
    {
      "product_url": "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html",
      "stage": "fetch",
      "reason": "HTTP 404"
    }
  ]
}
```

The failure was injected on my side. Nothing was tested by hammering the real site.

## Why no browser was needed

The prices, titles, ratings and descriptions are already in the HTML the server sends — you can read
them with `curl`. A headless browser would download the same bytes and then spend a few hundred
megabytes of RAM rendering them, so it would add cost and no data. A browser earns its keep only when
the content arrives via JavaScript after the page loads, as on `quotes.toscrape.com/js`.

## Ethics note

If a site publishes an official API, use it — it is the front door, and it is cheaper for both sides.
Never bypass a login, a paywall, or a block: those are a site saying no, and working around a "no"
turns a scraper into an intruder. Take only the fields you actually need, go slowly enough that
nobody notices you, and say who you are while doing it. And treat everything you collect as untrusted
input — a page can be missing, malformed, or changed without warning, so check it before you store it.

## Honest limitations

- **The descriptions are duplicated at the source.** On these pages the description `<p>` contains a
  truncated preview immediately followed by the full text (`...and love th It's hard to imagine...`),
  and it ends with a literal `...more`. That is what the server sends, so that is what I store —
  cleaning it up would mean guessing where the real text begins. A consumer of this data would need
  to de-duplicate it, and I would rather hand over the mess honestly than a guess.
- All 60 books in this three-page scope happen to have a description, so the `null` branch is
  exercised by a hand-made fixture rather than by live data.
- The cache never expires. It is a development cache, not a freshness strategy; a long-lived job
  would need a max-age and revalidation.
- Only the first retry is implemented, with a fixed 2 s pause. Real backoff and `Retry-After` are
  deliberately left for next week's assignment.

## Repository layout

```
W5A9-politeScraper/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py       entry point, CLI, and the run report
│   ├── fetcher.py    user-agent, timeout, delay, cache, status check, retry
│   ├── extract.py    catalogue links, "next" link, and the raw book record
│   └── schema.py     price normalization and the Pydantic record schema
├── cache/            saved HTML (git-ignored)
└── output/
    ├── books.json        60 validated records
    ├── errors.json       records that failed validation, with reasons
    └── run-report.json   what actually happened
```

## Stage log

| Stage | Commit |
| --- | --- |
| 0 · Classify the target | `Stage 0: classify scraping target` |
| 1 · Fetch once, cache once | `Stage 1: fetch and cache HTML` |
| 2 · Find all three pages | `Stage 2: discover three catalogue pages` |
| 3 · Extract the raw records | `Stage 3: extract book details` |
| 4 · Clean it, check it, store it | `Stage 4: validate normalized records` |
| 5 · One bad page must not kill the run | `Stage 5: survive failures, report the run` |
| 6 · Publish the evidence | `Stage 6: publish scraper evidence` |
