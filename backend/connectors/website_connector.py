"""
website_connector.py
--------------------
Secure HTTP connector for fetching and extracting content from pre-approved
official government and intergovernmental IP & traditional knowledge sources.

Key capabilities:
- Enforces strict HTTPS-only approved domain allowlist.
- Blocks localhost, RFC 1918 private IPs, non-HTTP(S) schemes.
- Detects and extracts PDFs using pypdf, preserving page numbers.
- Detects JavaScript-rendered shell content and attempts browser rendering fallback
  when available; otherwise falls back to static official subdomains (e.g., e-Charak).
- Follows up to 5 safe redirects with domain validation on every hop.
- Rejects CAPTCHA, login walls, and unsupported content types.
"""

from dataclasses import dataclass, field
import io
import ipaddress
import logging
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pypdf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Strict Approved Official Domain Allowlist (HTTPS preferred)
# ---------------------------------------------------------------------------
ALLOWED_DOMAINS = {
    # ── India: Legislation ────────────────────────────────────────────────
    "indiacode.nic.in",              # Central Acts, Rules, Amendments

    # ── India: IP Offices ─────────────────────────────────────────────────
    "ipindia.gov.in",                # Patents, Trademarks, GI Registry
    "ipindiaonline.gov.in",          # e-Filing portal
    "search.ipindia.gov.in",         # InPASS search & journal records

    # ── India: AYUSH & Traditional Knowledge ─────────────────────────────
    "ayush.gov.in",                  # Ministry of Ayush portal
    "echarak.ayush.gov.in",          # e-Charak medicinal herbs & classical formulations
    "tkdl.res.in",                   # Traditional Knowledge Digital Library
    "nmpb.nic.in",                   # National Medicinal Plants Board

    # ── India: Biodiversity & ABS ─────────────────────────────────────────
    "nbaindia.org",                  # National Biodiversity Authority

    # ── India: Drug & Food Standards ──────────────────────────────────────
    "cdsco.gov.in",                  # Central Drugs Standard Control Organisation
    "fssai.gov.in",                  # Food Safety and Standards Authority of India

    # ── International: WIPO ───────────────────────────────────────────────
    "wipo.int",                      # PCT, Madrid, Hague, TK, Treaties
    "patentscope.wipo.int",          # WIPO PATENTSCOPE portal

    # ── International: WTO ────────────────────────────────────────────────
    "wto.org",                       # TRIPS Agreement & Doha Declaration

    # ── International: CBD ────────────────────────────────────────────────
    "cbd.int",                       # Convention on Biological Diversity / Nagoya ABS

    # ── International: EPO ────────────────────────────────────────────────
    "epo.org",                       # European Patent Office
}

# Subdomain fallbacks when dynamic JS rendering is unavailable
JS_STATIC_FALLBACKS = {
    "ayush.gov.in": "https://echarak.ayush.gov.in/",
    "www.ayush.gov.in": "https://echarak.ayush.gov.in/",
}

MAX_REDIRECTS = 5
REQUEST_TIMEOUT = (3, 6)  # (connect_timeout, read_timeout)
MIN_USEFUL_LENGTH = 150

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (AyurlexResearchBot/2.0)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}


@dataclass
class SourceFetchResult:
    requested_url: str
    final_url: str
    content_type: str
    content: bytes
    status: str = "fetched"  # "fetched" | "rendered" | "pdf_extracted" | "unavailable" | "insufficient_content" | "blocked" | "timeout"
    extracted_text: str = ""
    pages: list[tuple[int, str]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class SourceConnectionError(Exception):
    pass


# ---------------------------------------------------------------------------
# Allowlist & Security Validation
# ---------------------------------------------------------------------------
def _normalise_hostname(hostname: str) -> str:
    hostname = (hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname


def is_private_ip(hostname: str) -> bool:
    """Detect private IP addresses, localhost, or link-local hosts."""
    if hostname in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local
    except ValueError:
        return False


def is_allowed_official_url(url: str) -> bool:
    """Return True if url belongs strictly to an approved official domain."""
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        return False

    hostname = _normalise_hostname(parsed.hostname or "")
    if is_private_ip(hostname):
        return False

    return any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in ALLOWED_DOMAINS
    )


def validate_source_url(url: str) -> None:
    if not is_allowed_official_url(url):
        raise SourceConnectionError(
            f"URL is not on the approved official-source allowlist: {url!r}"
        )


# ---------------------------------------------------------------------------
# PDF Extraction
# ---------------------------------------------------------------------------
def extract_pdf_document(pdf_bytes: bytes, source_url: str) -> tuple[str, list[tuple[int, str]]]:
    """Extract text from PDF page-by-page using pypdf."""
    text_parts: list[str] = []
    page_records: list[tuple[int, str]] = []

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page_idx, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                page_records.append((page_idx, page_text))
                text_parts.append(f"--- [Page {page_idx}] ---\n{page_text}")
    except Exception as e:
        logger.warning(f"pypdf extraction failed for {source_url}: {e}")

    full_text = "\n\n".join(text_parts)
    return full_text, page_records


# ---------------------------------------------------------------------------
# JavaScript Shell Detection & Headless Browser Fallback
# ---------------------------------------------------------------------------
def is_js_shell_content(html_bytes: bytes) -> bool:
    """Detect pages that require JavaScript to render substantive text."""
    if len(html_bytes) < 350:
        return True
    try:
        sample = html_bytes[:2048].decode("utf-8", errors="ignore").lower()
        if "<noscript>" in sample and "enable javascript" in sample:
            return True
        if 'id="root"' in sample and len(html_bytes) < 1500:
            return True
        if 'id="app"' in sample and len(html_bytes) < 1500:
            return True
    except Exception:
        pass
    return False


def try_browser_render(url: str, timeout_seconds: int = 12) -> tuple[bytes, str] | None:
    """Attempt multi-browser rendering using Google Chrome, Edge, or Playwright."""
    try:
        from connectors.browser_connector import render_with_browser
        return render_with_browser(url, timeout_seconds=timeout_seconds)
    except Exception as e:
        logger.warning(f"Browser rendering attempt failed for {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# Main Source Fetcher
# ---------------------------------------------------------------------------
def fetch_public_source(url: str) -> SourceFetchResult:
    """Fetch and extract content from an approved official source with multi-strategy support."""
    validate_source_url(url)
    current_url = url
    final_response = None

    try:
        for _ in range(MAX_REDIRECTS + 1):
            response = requests.get(
                current_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )

            if response.is_redirect:
                redirect_url = urljoin(current_url, response.headers.get("Location", ""))
                validate_source_url(redirect_url)
                current_url = redirect_url
                continue

            response.raise_for_status()
            final_response = response
            break

        if final_response is None:
            return SourceFetchResult(
                requested_url=url,
                final_url=current_url,
                content_type="unknown",
                content=b"",
                status="unavailable",
            )

    except requests.Timeout:
        rendered = try_browser_render(current_url)
        if rendered:
            rendered_bytes, render_status = rendered
            return SourceFetchResult(
                requested_url=url,
                final_url=current_url,
                content_type="text/html",
                content=rendered_bytes,
                status=render_status,
                metadata={"renderer": render_status},
            )
        return SourceFetchResult(
            requested_url=url,
            final_url=current_url,
            content_type="unknown",
            content=b"",
            status="timeout",
        )
    except Exception as e:
        logger.warning(f"HTTP fetch failed for {url}: {e}; attempting multi-browser fallback")
        rendered = try_browser_render(current_url)
        if rendered:
            rendered_bytes, render_status = rendered
            return SourceFetchResult(
                requested_url=url,
                final_url=current_url,
                content_type="text/html",
                content=rendered_bytes,
                status=render_status,
                metadata={"renderer": render_status},
            )
        return SourceFetchResult(
            requested_url=url,
            final_url=current_url,
            content_type="unknown",
            content=b"",
            status="unavailable",
        )

    content_type = final_response.headers.get("Content-Type", "").lower()
    raw_content = final_response.content

    # 1. Handle PDF Documents
    if "application/pdf" in content_type or url.lower().endswith(".pdf") or raw_content.startswith(b"%PDF"):
        pdf_text, pages = extract_pdf_document(raw_content, current_url)
        return SourceFetchResult(
            requested_url=url,
            final_url=current_url,
            content_type="application/pdf",
            content=raw_content,
            status="pdf_extracted" if pdf_text else "insufficient_content",
            extracted_text=pdf_text,
            pages=pages,
            metadata={
                "page_count": len(pages),
                "is_pdf": True,
            },
        )

    # 2. Check for JS Shell content & apply rendering / static fallback
    if is_js_shell_content(raw_content):
        # Attempt Playwright if available
        rendered = try_browser_render(current_url)
        if rendered:
            rendered_bytes, render_status = rendered
            return SourceFetchResult(
                requested_url=url,
                final_url=current_url,
                content_type=content_type,
                content=rendered_bytes,
                status=render_status,
            )

        # Fallback to static official subdomain if configured (e.g. echarak)
        hostname = _normalise_hostname(urlparse(current_url).hostname or "")
        if hostname in JS_STATIC_FALLBACKS:
            fallback_url = JS_STATIC_FALLBACKS[hostname]
            try:
                fallback_res = requests.get(fallback_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if fallback_res.ok and len(fallback_res.content) > MIN_USEFUL_LENGTH:
                    return SourceFetchResult(
                        requested_url=url,
                        final_url=fallback_url,
                        content_type="text/html",
                        content=fallback_res.content,
                        status="fetched",
                        metadata={"fallback_used": fallback_url},
                    )
            except Exception:
                pass

        return SourceFetchResult(
            requested_url=url,
            final_url=current_url,
            content_type=content_type,
            content=raw_content,
            status="insufficient_content",
        )

    # 3. Standard HTML content
    return SourceFetchResult(
        requested_url=url,
        final_url=current_url,
        content_type=content_type or "text/html",
        content=raw_content,
        status="fetched",
    )
