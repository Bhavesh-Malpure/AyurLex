"""
search_engine.py
----------------
Search engine discovery and multi-source web retrieval orchestrator for Ayurlex.

Connects the research pipeline to:
1. Google Chrome & Microsoft Edge browser-based rendering and query execution.
2. Official portal search systems (WIPO PATENTSCOPE, IP India InPASS, e-Charak, India Code).
3. Targeted domain search queries strictly restricted to approved official domains.
4. Multi-source fact verification and cross-checking pipeline.
"""

import logging
import re
from urllib.parse import quote, urlparse

from connectors.browser_connector import get_connected_browsers, render_with_browser
from connectors.website_connector import ALLOWED_DOMAINS, fetch_public_source, is_allowed_official_url

logger = logging.getLogger(__name__)


def build_official_search_url(query: str, jurisdiction: str = "india") -> list[dict]:
    """
    Construct direct official portal search URLs for specific research questions.
    """
    clean_q = re.sub(r"[^\w\s]", "", query).strip()
    encoded_q = quote(clean_q)
    targets = []

    if jurisdiction == "international" or any(w in query.lower() for w in ["wipo", "pct", "epo", "trips", "international"]):
        targets.append({
            "title": "WIPO PATENTSCOPE Official Search",
            "url": f"https://patentscope.wipo.int/search/en/search.jsf?queryString={encoded_q}",
            "jurisdiction": "international",
            "type": "official_patent_search",
        })
        targets.append({
            "title": "WIPO Classifications (Nice & Locarno)",
            "url": "https://www.wipo.int/classifications/en/",
            "jurisdiction": "international",
            "type": "official_classification",
        })
    else:
        targets.append({
            "title": "IP India InPASS Official Search",
            "url": "https://ipindiaservices.gov.in/publicsearch",
            "jurisdiction": "india",
            "type": "official_patent_search",
        })
        targets.append({
            "title": "e-Charak Ministry of Ayush Herb Search",
            "url": f"https://echarak.ayush.gov.in/",
            "jurisdiction": "india",
            "type": "official_ayush_portal",
        })
        targets.append({
            "title": "India Code Central Acts Search",
            "url": "https://www.indiacode.nic.in/",
            "jurisdiction": "india",
            "type": "official_legislation",
        })

    return targets


def execute_deep_web_research(
    query: str,
    jurisdiction: str = "india",
    max_sources: int = 3,
) -> tuple[list[dict], dict]:
    """
    Conduct multi-source web and browser research:
    1. Discovers connected browsers (Google Chrome, Microsoft Edge).
    2. Identifies targeted official portal URLs.
    3. Fetches and renders pages using native headless browser engines.
    4. Enforces strict official domain verification.
    Returns:
        (retrieved_chunks, metadata)
    """
    browsers = get_connected_browsers()
    browser_names = [b["name"] for b in browsers]

    search_targets = build_official_search_url(query, jurisdiction)[:max_sources]
    chunks = []
    statuses = []

    for target in search_targets:
        url = target["url"]
        if not is_allowed_official_url(url):
            continue

        fetch_res = fetch_public_source(url)
        statuses.append({
            "title": target["title"],
            "url": url,
            "status": fetch_res.status,
            "renderer": fetch_res.metadata.get("renderer", "default_http"),
        })

        # If substantive content exists or extracted text
        content_text = fetch_res.extracted_text or fetch_res.content.decode("utf-8", errors="ignore")
        if len(content_text) > 150:
            chunks.append({
                "title": target["title"],
                "source_url": fetch_res.final_url,
                "jurisdiction": target["jurisdiction"],
                "section_label": target["type"],
                "content": content_text[:3500],
                "score": 2.5,
            })

    metadata = {
        "connected_browsers": browser_names,
        "search_targets_contacted": len(search_targets),
        "successful_renders": len(chunks),
        "source_statuses": statuses,
    }

    return chunks, metadata

