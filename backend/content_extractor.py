"""
content_extractor.py
--------------------
Reusable, high-quality main-content extractor for official IP & legal documents.

Features:
- Prefers <main>, <article>, [role=main], and primary content containers.
- Scores candidate containers by readable text length, text density, and link density.
- Rejects containers dominated by navigation/menu links.
- Strips boilerplate (scripts, styles, headers, footers, navbars, cookie notices, sidebars).
- Collects extraction metadata: source_url, final_url, selector_used, text_length, content_type, extraction_status.
"""

from dataclasses import asdict, dataclass
import re
from bs4 import BeautifulSoup, Tag

REMOVE_TAGS = [
    "script",
    "style",
    "nav",
    "footer",
    "header",
    "aside",
    "form",
    "noscript",
    "svg",
    "iframe",
    "button",
]

REMOVE_CLASSES_OR_IDS = [
    "nav",
    "navbar",
    "menu",
    "navigation",
    "breadcrumb",
    "footer",
    "header",
    "cookie-banner",
    "cookie-notice",
    "sidebar",
    "social-share",
    "pagination",
]

CANDIDATE_SELECTORS = [
    "main",
    "article",
    "[role='main']",
    "#main-content",
    "#mainContent",
    "#content",
    ".main-content",
    ".article-content",
    ".entry-content",
    ".page-content",
    ".field--name-body",
    ".region-content",
    "body",
]

MINIMUM_USEFUL_TEXT_LENGTH = 120
MAX_LINK_DENSITY_THRESHOLD = 0.55  # Reject if >55% of characters belong to <a> tags


@dataclass
class ExtractionMetadata:
    source_url: str
    final_url: str
    selector_used: str
    text_length: int
    content_type: str
    extraction_status: str  # "extracted" | "insufficient_content" | "pdf_extracted" | "fallback_body"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExtractionResult:
    text: str
    metadata: ExtractionMetadata


def clean_text(raw_text: str) -> str:
    """Normalize whitespace and remove blank or trivial lines."""
    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in raw_text.splitlines()
    ]
    meaningful = [
        line for line in lines
        if len(line) > 1 and not re.match(r"^[-=_*#\s]{3,}$", line)
    ]
    return "\n".join(meaningful)


def calculate_link_density(element: Tag, text_length: int) -> float:
    """Ratio of text inside <a> tags to total text length."""
    if text_length <= 0:
        return 1.0
    links_text = "".join(a.get_text(strip=True) for a in element.find_all("a"))
    return len(links_text) / text_length


def score_container(element: Tag) -> tuple[float, str, float]:
    """Score a candidate DOM container based on text length, density, and link ratio."""
    raw_text = clean_text(element.get_text(separator="\n"))
    text_len = len(raw_text)
    if text_len < MINIMUM_USEFUL_TEXT_LENGTH:
        return 0.0, raw_text, 1.0

    link_density = calculate_link_density(element, text_len)
    if link_density > MAX_LINK_DENSITY_THRESHOLD:
        # Heavily penalize navigation/menu containers
        return 0.0, raw_text, link_density

    # Text density = ratio of text to HTML markup size
    html_len = len(str(element)) or 1
    text_density = min(text_len / html_len, 1.0)

    # Score rewards text volume, density, and low link ratio
    score = text_len * text_density * (1.0 - link_density)
    return score, raw_text, link_density


def extract_main_content(
    html_content: bytes | str,
    source_url: str = "",
    final_url: str = "",
    content_type: str = "text/html",
) -> ExtractionResult:
    """Extract substantive main text and metadata from HTML content."""
    if isinstance(html_content, bytes):
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            soup = BeautifulSoup(html_content.decode("utf-8", errors="ignore"), "html.parser")
    else:
        soup = BeautifulSoup(html_content, "html.parser")

    # 1. Decompose noisy elements
    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    for pattern in REMOVE_CLASSES_OR_IDS:
        for elem in soup.find_all(
            lambda tag: any(
                pattern in (tag.get("class") or [])
                or pattern == tag.get("id")
                for _ in [1]
            )
        ):
            elem.decompose()

    # 2. Evaluate candidate containers
    best_score = 0.0
    best_text = ""
    best_selector = "none"

    for selector in CANDIDATE_SELECTORS:
        candidates = soup.select(selector)
        for cand in candidates:
            score, cand_text, _ = score_container(cand)
            if score > best_score:
                best_score = score
                best_text = cand_text
                best_selector = selector

    # 3. Fallback to cleaned body if container selector was too aggressive
    if len(best_text) < MINIMUM_USEFUL_TEXT_LENGTH:
        body = soup.body or soup
        fallback_text = clean_text(body.get_text(separator="\n"))
        if len(fallback_text) >= MINIMUM_USEFUL_TEXT_LENGTH:
            return ExtractionResult(
                text=fallback_text,
                metadata=ExtractionMetadata(
                    source_url=source_url,
                    final_url=final_url or source_url,
                    selector_used="body_fallback",
                    text_length=len(fallback_text),
                    content_type=content_type,
                    extraction_status="fallback_body",
                ),
            )

        return ExtractionResult(
            text=best_text or fallback_text,
            metadata=ExtractionMetadata(
                source_url=source_url,
                final_url=final_url or source_url,
                selector_used=best_selector,
                text_length=len(best_text or fallback_text),
                content_type=content_type,
                extraction_status="insufficient_content",
            ),
        )

    return ExtractionResult(
        text=best_text,
        metadata=ExtractionMetadata(
            source_url=source_url,
            final_url=final_url or source_url,
            selector_used=best_selector,
            text_length=len(best_text),
            content_type=content_type,
            extraction_status="extracted",
        ),
    )
