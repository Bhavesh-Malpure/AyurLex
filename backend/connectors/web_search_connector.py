"""
web_search_connector.py
-----------------------
Web Search Tool & Deep Research Connectors integrating:
1. Tavily Search API (via TAVILY_API_KEY)
2. Google Search API (via GOOGLE_SEARCH_API_KEY & GOOGLE_CSE_ID)
3. Fallback: Ayurlex Official Government Portals Discovery Engine
"""

import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)


def search_tavily(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search web using Tavily Search API if configured."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []

    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": f"{query} ayurveda patent intellectual property",
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": max_results,
        }
        res = requests.post(url, json=payload, timeout=5.0)
        if res.status_code == 200:
            data = res.json()
            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "source_engine": "Tavily Search API",
                }
                for item in data.get("results", [])
            ]
    except Exception as e:
        logger.warning(f"Tavily API search error: {e}")
    return []


def search_google_custom_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search web using Google Custom Search JSON API if configured."""
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        return []

    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(max_results, 10),
        }
        res = requests.get(url, params=params, timeout=5.0)
        if res.status_code == 200:
            data = res.json()
            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "content": item.get("snippet", ""),
                    "source_engine": "Google Custom Search API",
                }
                for item in data.get("items", [])
            ]
    except Exception as e:
        logger.warning(f"Google Search API error: {e}")
    return []


def execute_deep_web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """
    Unified Web & Deep Research Tool.
    Attempts Tavily & Google Search API, and falls back to our curated
    official government domain search engine.
    """
    results = search_tavily(query, max_results=max_results)
    if not results:
        results = search_google_custom_search(query, max_results=max_results)

    engine_used = "Tavily/Google API" if results else "Ayurlex Official Government Discovery"

    if not results:
        # Fallback to official portals search engine
        from search_engine import discover_and_extract_evidence
        evidence, statuses, _ = discover_and_extract_evidence(query, jurisdiction="india")
        results = [
            {
                "title": c.get("title", "Official Statutory Document"),
                "url": c.get("source_url", ""),
                "content": c.get("content", "")[:350],
                "source_engine": "Ayurlex Official Portal Crawler",
            }
            for c in evidence[:max_results]
        ]

    return {
        "query": query,
        "engine": engine_used,
        "results_count": len(results),
        "results": results,
    }
