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


def _clean(text):
    return " ".join(text.split())


def _required_text(product, selector, product_url):
    node = product.select_one(selector)
    if node is None:
        raise ExtractError(f"{product_url}: no element matched {selector!r}")
    text = _clean(node.get_text())
    if not text:
        raise ExtractError(f"{product_url}: {selector!r} matched an empty value")
    return text


def _rating_text(product, product_url):
    node = product.select_one("p.star-rating")
    if node is None:
        raise ExtractError(f"{product_url}: no rating element")
    for name in node.get("class", []):
        if name != "star-rating":
            return name
    raise ExtractError(f"{product_url}: rating element carries no rating class")


def _description(soup):
    header = soup.select_one("#product_description")
    if header is None:
        return None
    paragraph = header.find_next_sibling("p")
    if paragraph is None:
        return None
    text = _clean(paragraph.get_text())
    return text or None


def book_record(html, product_url, source_page, fetched_at):
    soup = parse(html)
    product = soup.select_one("article.product_page")
    if product is None:
        raise ExtractError(f"{product_url}: no article.product_page on the page")
    main = product.select_one("div.product_main")
    if main is None:
        raise ExtractError(f"{product_url}: no div.product_main inside the product area")

    return {
        "title": _required_text(main, "h1", product_url),
        "product_url": product_url,
        "price_text": _required_text(main, "p.price_color", product_url),
        "availability_text": _required_text(main, "p.instock.availability", product_url),
        "rating_text": _rating_text(main, product_url),
        "description": _description(soup),
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


class ExtractError(Exception):
    pass
