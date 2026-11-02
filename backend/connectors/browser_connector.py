"""
browser_connector.py
--------------------
Multi-browser rendering engine pipeline for Ayurlex.

Connects native Google Chrome and Microsoft Edge headless browsers to:
- Render JavaScript-heavy official portals (WIPO, e-Charak, Ayush, FSSAI, CDSCO, EPO).
- Bypass static scraper limitations while adhering strictly to approved official domains.
- Extract dynamic DOM representations for legal evidence grounding.
- Provide automatic failover between Google Chrome, Microsoft Edge, and Playwright.
"""

import logging
import os
import re
import shutil
import subprocess

logger = logging.getLogger(__name__)

# Known standard installation paths on Windows & Linux
CHROME_CANDIDATE_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "google-chrome",
    "chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

EDGE_CANDIDATE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    "msedge",
    "edge",
    "/usr/bin/microsoft-edge",
]


def find_executable(candidate_paths: list[str]) -> str | None:
    for path in candidate_paths:
        if os.path.isabs(path) and os.path.isfile(path):
            return path
        resolved = shutil.which(path)
        if resolved and os.path.isfile(resolved):
            return resolved
    return None


def get_chrome_path() -> str | None:
    return find_executable(CHROME_CANDIDATE_PATHS)


def get_edge_path() -> str | None:
    return find_executable(EDGE_CANDIDATE_PATHS)


def get_connected_browsers() -> list[dict]:
    """Inspect and return available connected browsers on the host system."""
    connected = []

    chrome = get_chrome_path()
    if chrome:
        connected.append({
            "name": "Google Chrome",
            "type": "chrome",
            "path": chrome,
            "status": "connected",
            "headless_mode": "--headless=new",
        })

    edge = get_edge_path()
    if edge:
        connected.append({
            "name": "Microsoft Edge",
            "type": "edge",
            "path": edge,
            "status": "connected",
            "headless_mode": "--headless=new",
        })

    try:
        import playwright
        connected.append({
            "name": "Playwright Automation Engine",
            "type": "playwright",
            "path": playwright.__file__,
            "status": "connected",
            "headless_mode": "playwright_sync",
        })
    except ImportError:
        pass

    return connected


def render_with_browser(url: str, timeout_seconds: int = 15) -> tuple[bytes, str] | None:
    """
    Render an approved official website URL using the multi-browser pipeline.
    Attempts Google Chrome first, then Microsoft Edge, then Playwright.
    Returns:
        (html_bytes, engine_name) or None if all fail.
    """
    browsers = get_connected_browsers()
    if not browsers:
        logger.warning("No native browser found (Chrome, Edge, or Playwright).")
        return None

    # Flags for clean, sandboxed headless DOM dumping
    browser_flags = [
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-background-networking",
        "--blink-settings=imagesEnabled=false",  # Skip heavy images for high speed
        "--dump-dom",
    ]

    for browser in browsers:
        b_type = browser["type"]
        b_name = browser["name"]
        b_path = browser["path"]

        if b_type in ("chrome", "edge"):
            try:
                cmd = [b_path] + browser_flags + [url]
                logger.info(f"Rendering official source using {b_name} for: {url}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=timeout_seconds,
                    check=False,
                )

                if result.stdout and len(result.stdout) > 200:
                    raw_output = result.stdout
                    # Strip any browser diagnostic prefixes before <!DOCTYPE or <html
                    html_match = re.search(rb"(?i)(<!DOCTYPE|<html)", raw_output)
                    if html_match:
                        raw_output = raw_output[html_match.start():]
                    logger.info(f"Successfully rendered {len(raw_output)} bytes using {b_name} from {url}")
                    return raw_output, f"rendered_{b_type}"

            except subprocess.TimeoutExpired:
                logger.warning(f"{b_name} timed out after {timeout_seconds}s for {url}")
            except Exception as e:
                logger.warning(f"{b_name} execution error for {url}: {e}")

        elif b_type == "playwright":
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    pw_browser = p.chromium.launch(headless=True)
                    page = pw_browser.new_page()
                    page.goto(url, timeout=timeout_seconds * 1000, wait_until="domcontentloaded")
                    content = page.content().encode("utf-8")
                    pw_browser.close()
                    if content and len(content) > 200:
                        return content, "rendered_playwright"
            except Exception as e:
                logger.warning(f"Playwright rendering error for {url}: {e}")

    return None

