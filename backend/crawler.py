from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from connectors.website_connector import (
    SourceConnectionError,
    fetch_public_source,
    is_allowed_official_url,
)

MAX_PAGES = 5


def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)

    normalized_path = parsed_url.path.rstrip("/") or "/"

    return parsed_url._replace(
        path=normalized_path,
        fragment="",
        query="",
    ).geturl()


def get_internal_links(
    html_content: bytes,
    base_url: str,
    allowed_hostname: str,
    allowed_path_prefix: str,
) -> list[str]:
    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    links = set()

    for anchor in soup.find_all("a", href=True):
        full_url = normalize_url(
            urljoin(base_url, anchor["href"])
        )

        parsed_url = urlparse(full_url)

        if (
            parsed_url.hostname == allowed_hostname
            and parsed_url.path.startswith(allowed_path_prefix)
            and is_allowed_official_url(full_url)
        ):
            links.add(full_url)

    return sorted(links)


def crawl_official_website(
    start_url: str,
    max_pages: int = MAX_PAGES,
) -> list[dict]:
    if not is_allowed_official_url(start_url):
        raise SourceConnectionError(
            "Only approved official HTTPS websites may be crawled."
        )

    normalized_start_url = normalize_url(start_url)
    start_hostname = urlparse(normalized_start_url).hostname

    if not start_hostname:
        raise SourceConnectionError(
            "The start URL does not contain a valid hostname."
        )

    pages = []
    visited_urls = set()
    pending_urls = deque([normalized_start_url])
    allowed_path_prefix = ""

    while pending_urls and len(pages) < max_pages:
        current_url = pending_urls.popleft()

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            fetched_page = fetch_public_source(current_url)
        except Exception:
            continue

        if "html" not in fetched_page.content_type.lower():
            continue

        final_url = normalize_url(fetched_page.final_url)
        final_hostname = urlparse(final_url).hostname

        if final_hostname != start_hostname:
            continue

        if not allowed_path_prefix:
            allowed_path_prefix = (
                urlparse(final_url).path.rstrip("/")
            )

        current_path = urlparse(final_url).path

        if not current_path.startswith(allowed_path_prefix):
            continue

        if final_url in visited_urls and final_url != current_url:
            continue

        visited_urls.add(final_url)

        pages.append(
            {
                "url": current_url,
                "final_url": final_url,
                "content": fetched_page.content,
                "content_type": fetched_page.content_type,
            }
        )

        internal_links = get_internal_links(
            html_content=fetched_page.content,
            base_url=final_url,
            allowed_hostname=start_hostname,
            allowed_path_prefix=allowed_path_prefix,
        )

        for link in internal_links:
            if link not in visited_urls:
                pending_urls.append(link)

    return pages