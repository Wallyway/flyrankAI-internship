import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import schema
from extract import book_links, book_record, next_page_url
from fetcher import FetchError, PoliteFetcher

BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3
FAKE_URL = "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
BOOKS_PATH = OUTPUT_DIR / "books.json"
ERRORS_PATH = OUTPUT_DIR / "errors.json"
REPORT_PATH = OUTPUT_DIR / "run-report.json"


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def discover(fetcher):
    page_url = START_URL
    catalogue_pages = 0
    discovered = 0
    targets = {}

    while page_url and catalogue_pages < MAX_CATALOGUE_PAGES:
        html, _, _ = fetcher.fetch(page_url)
        catalogue_pages += 1
        for url in book_links(html, page_url):
            discovered += 1
            targets.setdefault(url, page_url)
        page_url = next_page_url(html, page_url)

    return catalogue_pages, discovered, targets


def collect(fetcher, targets):
    valid = []
    invalid = []
    failed = []

    for product_url, source_page in targets.items():
        try:
            html, _, fetched_at = fetcher.fetch(product_url)
            raw = book_record(html, product_url, source_page, fetched_at)
        except FetchError as error:
            print(f"SKIP {product_url} ({error.reason})")
            failed.append({"product_url": product_url, "stage": "fetch", "reason": error.reason})
            continue
        except Exception as error:
            print(f"SKIP {product_url} (extract failed: {error})")
            failed.append({"product_url": product_url, "stage": "extract", "reason": str(error)})
            continue

        try:
            valid.append(schema.build(raw))
        except Exception as error:
            print(f"INVALID {product_url}")
            invalid.append({"product_url": product_url, "reason": str(error)})

    return valid, invalid, failed


def write_json(path, payload):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Polite scraper for books.toscrape.com")
    parser.add_argument(
        "--inject-failure",
        action="store_true",
        help="add one made-up book URL to prove a broken page does not kill the run",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    started_at = utc_now()
    started_monotonic = time.monotonic()

    fetcher = PoliteFetcher()
    try:
        catalogue_pages, discovered, targets = discover(fetcher)
    except FetchError as error:
        print(f"ABORTED during discovery: {error}")
        return 1

    if args.inject_failure:
        targets.setdefault(FAKE_URL, START_URL)
        discovered += 1

    valid, invalid, failed = collect(fetcher, targets)
    books = sorted((book.model_dump() for book in valid), key=lambda book: book["product_url"])

    report = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started_monotonic, 2),
        "catalogue_pages": catalogue_pages,
        "discovered": discovered,
        "unique_urls": len(targets),
        "pages_fetched": fetcher.pages_fetched,
        "cache_hits": fetcher.cache_hits,
        "valid_records": len(books),
        "invalid_records": len(invalid),
        "failed_pages": len(failed),
        "failures": failed,
    }

    write_json(BOOKS_PATH, books)
    write_json(ERRORS_PATH, invalid)
    write_json(REPORT_PATH, report)

    print()
    for key in (
        "started_at",
        "duration_seconds",
        "catalogue_pages",
        "unique_urls",
        "pages_fetched",
        "cache_hits",
        "valid_records",
        "invalid_records",
        "failed_pages",
    ):
        print(f"{key}={report[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
