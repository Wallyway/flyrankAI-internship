import json

from extract import book_links, book_record, dedupe, next_page_url
from fetcher import FetchError, PoliteFetcher

BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3


def discover(fetcher):
    page_url = START_URL
    catalogue_pages = 0
    discovered = []

    while page_url and catalogue_pages < MAX_CATALOGUE_PAGES:
        html, _, _ = fetcher.fetch(page_url)
        catalogue_pages += 1
        for url in book_links(html, page_url):
            discovered.append((url, page_url))
        page_url = next_page_url(html, page_url)

    return catalogue_pages, discovered


def unique_targets(discovered):
    targets = {}
    for url, source_page in discovered:
        targets.setdefault(url, source_page)
    return targets


def collect(fetcher, targets):
    records = []
    for product_url, source_page in targets.items():
        html, _, fetched_at = fetcher.fetch(product_url)
        records.append(book_record(html, product_url, source_page, fetched_at))
    return records


def main():
    fetcher = PoliteFetcher()
    try:
        catalogue_pages, discovered = discover(fetcher)
        targets = unique_targets(discovered)
        records = collect(fetcher, targets)
    except FetchError as error:
        print(f"FAILED {error}")
        return 1

    print()
    print(json.dumps(records[0], indent=2, ensure_ascii=False))
    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered)}")
    print(f"unique_urls={len(targets)}")
    print(f"detail_pages={len(records)}")
    print(f"pages_fetched={fetcher.pages_fetched} cache_hits={fetcher.cache_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
