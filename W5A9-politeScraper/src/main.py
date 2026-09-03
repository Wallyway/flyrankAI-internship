import json
from pathlib import Path

import schema
from extract import book_links, book_record, next_page_url
from fetcher import FetchError, PoliteFetcher

BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
BOOKS_PATH = OUTPUT_DIR / "books.json"
ERRORS_PATH = OUTPUT_DIR / "errors.json"


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

    for product_url, source_page in targets.items():
        html, _, fetched_at = fetcher.fetch(product_url)
        raw = book_record(html, product_url, source_page, fetched_at)
        try:
            valid.append(schema.build(raw))
        except Exception as error:
            invalid.append({"product_url": product_url, "reason": str(error)})

    return valid, invalid


def write_json(path, payload):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    fetcher = PoliteFetcher()
    try:
        catalogue_pages, discovered, targets = discover(fetcher)
        valid, invalid = collect(fetcher, targets)
    except FetchError as error:
        print(f"FAILED {error}")
        return 1

    books = sorted((book.model_dump() for book in valid), key=lambda book: book["product_url"])
    write_json(BOOKS_PATH, books)
    write_json(ERRORS_PATH, invalid)

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={discovered}")
    print(f"unique_urls={len(targets)}")
    print(f"valid_records={len(books)}")
    print(f"invalid_records={len(invalid)}")
    print(f"pages_fetched={fetcher.pages_fetched} cache_hits={fetcher.cache_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
