from urllib.parse import urljoin

from bs4 import BeautifulSoup


def parse(html):
    return BeautifulSoup(html, "html.parser")


def book_links(html, page_url):
    soup = parse(html)
    links = []
    for pod in soup.select("article.product_pod h3 a[href]"):
        links.append(urljoin(page_url, pod["href"]))
    return links


def next_page_url(html, page_url):
    soup = parse(html)
    link = soup.select_one("li.next a[href]")
    if link is None:
        return None
    return urljoin(page_url, link["href"])


def dedupe(urls):
    seen = {}
    for url in urls:
        seen.setdefault(url, None)
    return list(seen)
