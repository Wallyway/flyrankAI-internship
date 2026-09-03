from extract import book_links, dedupe, next_page_url
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


def main():
    fetcher = PoliteFetcher()
    try:
        catalogue_pages, discovered = discover(fetcher)
    except FetchError as error:
        print(f"FAILED {error}")
        return 1

    unique = dedupe([url for url, _ in discovered])

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered)}")
    print(f"unique_urls={len(unique)}")
    print(f"pages_fetched={fetcher.pages_fetched} cache_hits={fetcher.cache_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
