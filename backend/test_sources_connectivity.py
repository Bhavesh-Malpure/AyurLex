"""
test_sources_connectivity.py
-----------------------------
Checks every OfficialSource defined in source_router against the live web.
For each URL it reports:
  ✓  HTTP 200, content-type, and approx text length
  ✗  HTTP error code
  ✗  Connection / timeout error
  ⚠  Non-HTML (PDF etc.) — counted as reachable
  ⚠  Very short content (< 300 chars) — deep-fetch would trigger

Run from the backend/ directory:
    python test_sources_connectivity.py
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Force UTF-8 output so Unicode chars work on Windows cp1252 terminals.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

# Import every declared source directly from the router
from source_router import (
    # India — Legislation
    INDIA_CODE,
    INDIA_PATENTS_ACT,
    INDIA_TRADEMARKS_ACT,
    INDIA_DESIGNS_ACT,
    INDIA_GI_ACT,
    INDIA_BIODIVERSITY_ACT,
    INDIA_DRUGS_ACT,
    INDIA_PLANTS_ACT,
    # India — IP India
    IP_INDIA,
    IP_INDIA_PATENTS,
    IP_INDIA_INPASS,
    IP_INDIA_PATENT_SEARCH,
    IP_INDIA_JOURNAL,
    IP_INDIA_TM,
    IP_INDIA_TM_SEARCH,
    IP_INDIA_DESIGNS,
    IP_INDIA_DESIGN_SEARCH,
    IP_INDIA_GI,
    # India — TKDL
    TKDL,
    TKDL_SEARCH,
    # India — AYUSH
    MINISTRY_OF_AYUSH,
    E_CHARAK_KNOWLEDGE,
    E_CHARAK_HOME,
    NMPB,
    # India — NBA / ABS
    NBA_INDIA,
    NBA_ABS,
    # India — Drugs / Food
    CDSCO,
    CDSCO_ASU,
    FSSAI,
    FSSAI_REGULATIONS,
    # International — WIPO
    WIPO_TREATIES,
    WIPO_PCT,
    WIPO_PATENTSCOPE,
    WIPO_MADRID,
    WIPO_MADRID_BRAND_DB,
    WIPO_HAGUE,
    WIPO_BUDAPEST,
    WIPO_TK,
    WIPO_GI,
    # International — WTO
    WTO_TRIPS,
    WTO_TRIPS_TK,
    # International — CBD / Nagoya
    CBD_ABS,
    CBD_NAGOYA_TEXT,
    CBD_HOME,
)

ALL_SOURCES = [
    # ── India: Legislation ─────────────────────────────────────────────
    INDIA_CODE,
    INDIA_PATENTS_ACT,
    INDIA_TRADEMARKS_ACT,
    INDIA_DESIGNS_ACT,
    INDIA_GI_ACT,
    INDIA_BIODIVERSITY_ACT,
    INDIA_DRUGS_ACT,
    INDIA_PLANTS_ACT,
    # ── India: IP India ────────────────────────────────────────────────
    IP_INDIA,
    IP_INDIA_PATENTS,
    IP_INDIA_INPASS,
    IP_INDIA_PATENT_SEARCH,
    IP_INDIA_JOURNAL,
    IP_INDIA_TM,
    IP_INDIA_TM_SEARCH,
    IP_INDIA_DESIGNS,
    IP_INDIA_DESIGN_SEARCH,
    IP_INDIA_GI,
    # ── India: TKDL ────────────────────────────────────────────────────
    TKDL,
    TKDL_SEARCH,
    # ── India: AYUSH / Ayurveda ────────────────────────────────────────
    MINISTRY_OF_AYUSH,
    E_CHARAK_KNOWLEDGE,
    E_CHARAK_HOME,
    NMPB,
    # ── India: NBA / ABS ──────────────────────────────────────────────
    NBA_INDIA,
    NBA_ABS,
    # ── India: Drugs / Food ────────────────────────────────────────────
    CDSCO,
    CDSCO_ASU,
    FSSAI,
    FSSAI_REGULATIONS,
    # ── International: WIPO ───────────────────────────────────────────
    WIPO_TREATIES,
    WIPO_PCT,
    WIPO_PATENTSCOPE,
    WIPO_MADRID,
    WIPO_MADRID_BRAND_DB,
    WIPO_HAGUE,
    WIPO_BUDAPEST,
    WIPO_TK,
    WIPO_GI,
    # ── International: WTO ────────────────────────────────────────────
    WTO_TRIPS,
    WTO_TRIPS_TK,
    # ── International: CBD / Nagoya ────────────────────────────────────
    CBD_ABS,
    CBD_NAGOYA_TEXT,
    CBD_HOME,
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AyurlexResearchBot/1.0; "
        "+https://ayurlex.in/bot)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}
TIMEOUT = (15, 45)
MIN_USEFUL = 300


def approx_text_len(html_bytes: bytes) -> int:
    try:
        soup = BeautifulSoup(html_bytes, "html.parser")
        for t in soup(["script", "style", "nav", "footer", "header"]):
            t.decompose()
        return len(soup.get_text(" ", strip=True))
    except Exception:
        return len(html_bytes)


def check_source(source) -> dict:
    t0 = time.perf_counter()
    try:
        resp = requests.get(
            source.source_url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        elapsed = time.perf_counter() - t0
        ct = resp.headers.get("Content-Type", "?")
        status = resp.status_code

        if status != 200:
            return dict(
                source=source,
                ok=False,
                symbol="[HTTP ERR]",
                detail=f"HTTP {status}",
                elapsed=elapsed,
            )

        is_html = "html" in ct.lower()
        if not is_html:
            return dict(
                source=source,
                ok=True,
                symbol="[NON-HTML]",
                detail=f"{ct.split(';')[0].strip()}",
                elapsed=elapsed,
            )

        text_len = approx_text_len(resp.content)
        if text_len < MIN_USEFUL:
            return dict(
                source=source,
                ok=True,
                symbol="[THIN]",
                detail=f"~{text_len} chars (deep-fetch would trigger)",
                elapsed=elapsed,
            )

        return dict(
            source=source,
            ok=True,
            symbol="✓ OK",
            detail=f"~{text_len:,} chars | {ct.split(';')[0].strip()}",
            elapsed=elapsed,
        )

    except requests.exceptions.SSLError as e:
        return dict(source=source, ok=False, symbol="[SSL ERR]", detail=str(e)[:80], elapsed=time.perf_counter()-t0)
    except requests.exceptions.ConnectionError as e:
        return dict(source=source, ok=False, symbol="[CONN ERR]", detail=str(e)[:80], elapsed=time.perf_counter()-t0)
    except requests.exceptions.Timeout:
        return dict(source=source, ok=False, symbol="[TIMEOUT]", detail="Timed out", elapsed=time.perf_counter()-t0)
    except Exception as e:
        return dict(source=source, ok=False, symbol="[ERR]", detail=str(e)[:80], elapsed=time.perf_counter()-t0)


def run_tests():
    print(f"\n{'='*80}")
    print(f"  Ayurlex — Official Source Connectivity Test ({len(ALL_SOURCES)} sources)")
    print(f"{'='*80}\n")

    results = [None] * len(ALL_SOURCES)
    source_list = list(ALL_SOURCES)

    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_idx = {
            pool.submit(check_source, s): i
            for i, s in enumerate(source_list)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
            r = results[idx]
            # Print as they complete (out of order) for live feedback
            print(
                f"  {r['symbol']:<12} {r['source'].jurisdiction.upper():<13} "
                f"{r['source'].title[:52]:<52} "
                f"({r['elapsed']:.1f}s)"
            )

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")

    ok_count      = sum(1 for r in results if r["ok"])
    fail_count    = sum(1 for r in results if not r["ok"])
    thin_count    = sum(1 for r in results if r["symbol"] == "[THIN]")
    nonhtml_count = sum(1 for r in results if r["symbol"] == "[NON-HTML]")

    print(f"\n  Total sources : {len(results)}")
    print(f"  ✓ Reachable   : {ok_count}")
    print(f"  ✗ Failed      : {fail_count}")
    print(f"  ⚠ Thin content: {thin_count}  (deep-fetch will auto-retry sub-links)")
    print(f"  ⚠ Non-HTML    : {nonhtml_count}")

    if fail_count:
        print(f"\n  FAILED SOURCES:")
        for r in results:
            if not r["ok"]:
                print(
                    f"    {r['symbol']:<12} {r['source'].source_url}\n"
                    f"             -> {r['detail']}"
                )

    if thin_count:
        print(f"\n  THIN CONTENT (deep-fetch will try sub-links):")
        for r in results:
            if r["symbol"] == "[THIN]":
                print(
                    f"    {r['source'].source_url}\n"
                    f"             -> {r['detail']}"
                )

    print(f"\n{'='*80}\n")
    return fail_count


if __name__ == "__main__":
    fails = run_tests()
    sys.exit(1 if fails else 0)
