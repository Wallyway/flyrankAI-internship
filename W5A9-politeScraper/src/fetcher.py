import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Wallyway/flyrankAI-internship)"
TIMEOUT_SECONDS = 10
MIN_DELAY_SECONDS = 0.5

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def cache_path_for(url):
    path = urlparse(url).path
    catalogue_page = re.search(r"/catalogue/page-(\d+)\.html$", path)
    if catalogue_page:
        return CACHE_DIR / f"catalogue-page-{catalogue_page.group(1)}.html"
    slug = re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")
    return CACHE_DIR / f"book-{slug}.html"


def _utc_iso(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PoliteFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.last_request_at = None
        self.pages_fetched = 0
        self.cache_hits = 0

    def _wait_turn(self):
        if self.last_request_at is None:
            return
        elapsed = time.monotonic() - self.last_request_at
        if elapsed < MIN_DELAY_SECONDS:
            time.sleep(MIN_DELAY_SECONDS - elapsed)

    def _download(self, url):
        self._wait_turn()
        try:
            response = self.session.get(url, timeout=TIMEOUT_SECONDS)
        finally:
            self.last_request_at = time.monotonic()
        if response.status_code != 200:
            raise FetchError(url, response.status_code, f"HTTP {response.status_code}")
        response.encoding = "utf-8"
        return response.text

    def fetch(self, url):
        path = cache_path_for(url)
        if path.exists():
            self.cache_hits += 1
            html = path.read_text(encoding="utf-8")
            print(f"CACHE HIT {url} bytes={len(html.encode('utf-8'))}")
            return html, True, _utc_iso(path.stat().st_mtime)

        html = self._download(url)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        self.pages_fetched += 1
        print(f"FETCH {url} bytes={len(html.encode('utf-8'))}")
        return html, False, _utc_iso(path.stat().st_mtime)


class FetchError(Exception):
    def __init__(self, url, status, reason):
        super().__init__(f"{url}: {reason}")
        self.url = url
        self.status = status
        self.reason = reason
