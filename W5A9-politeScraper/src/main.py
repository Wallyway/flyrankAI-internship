from fetcher import FetchError, PoliteFetcher

BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3


def main():
    fetcher = PoliteFetcher()
    try:
        html, from_cache, fetched_at = fetcher.fetch(START_URL)
    except FetchError as error:
        print(f"FAILED {error}")
        return 1

    print(f"source={'cache' if from_cache else 'network'} fetched_at={fetched_at}")
    print(f"pages_fetched={fetcher.pages_fetched} cache_hits={fetcher.cache_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
