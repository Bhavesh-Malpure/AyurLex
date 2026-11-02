"""
research_agent.py
-----------------
Advanced evidence-grounded live-research engine for Ayurlex.

Key capabilities:
- Routes to at most 3 relevant approved official sources per query.
- Fetches sources concurrently with strict per-source timeouts.
- Extracts substantive main content using density-scored content extractor.
- Supports PDF document text extraction page-by-page.
- Handles JavaScript-heavy official portals via renderer or static subdomain fallbacks.
- Ranks evidence chunks using query-term density.
- Handles PATENTSCOPE compliant search referencing without fabricating records.
- Returns comprehensive source_statuses and extraction_metadata.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import re

from connectors.website_connector import (
    SourceConnectionError,
    SourceFetchResult,
    fetch_public_source,
)
from content_extractor import extract_main_content
from source_router import OfficialSource, route_question_to_sources

# Maximum official sources to query per live research request
MAX_LIVE_SOURCES = 3

# Per-source and total context budgets
MAX_CONTEXT_CHARS_PER_SOURCE = 3_500
MAX_CONTEXT_CHARS_TOTAL = 10_000
CONTEXT_WINDOW_LINES = 3
MIN_CHUNK_LENGTH = 100

STOP_WORDS = {
    "a", "about", "after", "also", "an", "and", "are", "as", "at",
    "be", "been", "but", "by", "can", "do", "does", "for", "from",
    "had", "has", "have", "how", "in", "india", "is", "it", "its",
    "may", "not", "of", "on", "or", "shall", "so", "than", "that",
    "the", "their", "there", "they", "this", "to", "under", "was",
    "were", "what", "which", "who", "will", "with", "would",
}

PATENTSCOPE_KEYWORDS = {
    "latest patent", "latest patents", "patent publication", "new patent",
    "patent names", "wo number", "applicant", "patentscope",
}


def _extract_query_terms(question: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", question.lower())
    terms = [w for w in words if w not in STOP_WORDS]
    bigrams = [
        f"{words[i]} {words[i + 1]}"
        for i in range(len(words) - 1)
        if words[i] not in STOP_WORDS and words[i + 1] not in STOP_WORDS
    ]
    seen = set()
    result = []
    for t in terms + bigrams:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def _score_text(text: str, query_terms: list[str]) -> float:
    text_lower = text.lower()
    matches = sum(1 for term in query_terms if term in text_lower)
    return float(matches)


SPECIFIC_SUBSTANCE_TERMS = {
    "curcumin", "piperine", "turmeric", "neem", "ashwagandha", "tulsi",
    "triphala", "chyawanprash", "guggulu", "brahmi", "shatavari",
    "haridra", "nimba", "boswellia", "resveratrol", "aloe",
}


def _build_relevant_excerpt(
    text: str,
    query_terms: list[str],
    question: str = "",
    max_chars: int = MAX_CONTEXT_CHARS_PER_SOURCE,
) -> str:
    text_lower = text.lower()
    q_lower = (question or "").lower()

    # If the user's question asks about specific botanical/chemical substances,
    # require that the source text actually mentions at least one of those substances.
    # Otherwise general agency homepage text must not be passed off as substance evidence.
    asked_substances = [s for s in SPECIFIC_SUBSTANCE_TERMS if s in q_lower]
    if asked_substances and not any(s in text_lower for s in asked_substances):
        return ""

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""

    scored = [(i, sum(1 for term in query_terms if term in line.lower())) for i, line in enumerate(lines)]
    hot_indices = [i for i, score in scored if score > 0]

    if not hot_indices:
        return ""

    hot_indices.sort(key=lambda i: scored[i][1], reverse=True)

    windows = []
    covered = set()

    for hot_i in hot_indices:
        start = max(0, hot_i - CONTEXT_WINDOW_LINES)
        end = min(len(lines), hot_i + CONTEXT_WINDOW_LINES + 1)
        rng = set(range(start, end))
        if rng & covered:
            continue
        covered |= rng
        windows.append((scored[hot_i][1], lines[start:end]))

    windows.sort(key=lambda w: w[0], reverse=True)

    parts = []
    total = 0
    for _, window_lines in windows:
        block = "\n".join(window_lines)
        if total + len(block) > max_chars:
            rem = max_chars - total
            if rem > 60:
                parts.append(block[:rem])
            break
        parts.append(block)
        total += len(block)
        if total >= max_chars:
            break

    return "\n\n".join(parts)


def _fetch_and_extract_source(
    source: OfficialSource,
    question: str,
    query_terms: list[str],
) -> dict:
    """Fetch an official source, extract main content/PDF, and build evidence chunk."""
    status_entry = {
        "title": source.title,
        "source_url": source.source_url,
        "status": "unavailable",
    }
    extraction_meta = {
        "source_url": source.source_url,
        "final_url": source.source_url,
        "selector_used": "none",
        "text_length": 0,
        "content_type": "unknown",
        "extraction_status": "unavailable",
    }

    try:
        fetched: SourceFetchResult = fetch_public_source(source.source_url)
        status_entry["source_url"] = fetched.final_url
        status_entry["status"] = fetched.status

        # 1. Handle PDF Documents
        if fetched.status == "pdf_extracted" or fetched.content_type == "application/pdf":
            raw_text = fetched.extracted_text
            excerpt = _build_relevant_excerpt(raw_text, query_terms, question=question)
            score = _score_text(excerpt, query_terms) + 1.0

            extraction_meta.update({
                "source_url": source.source_url,
                "final_url": fetched.final_url,
                "selector_used": "pypdf_extractor",
                "text_length": len(raw_text),
                "content_type": "application/pdf",
                "extraction_status": "pdf_extracted",
            })

            if len(excerpt) >= MIN_CHUNK_LENGTH:
                chunk = {
                    "document_id": f"live_pdf_{source.source_url}",
                    "title": source.title,
                    "source_url": fetched.final_url,
                    "jurisdiction": source.jurisdiction,
                    "section_label": "Official Statutory PDF Excerpt",
                    "content": excerpt,
                    "score": score,
                }
                return {
                    "status_entry": status_entry,
                    "extraction_meta": extraction_meta,
                    "chunk": chunk,
                }

        # 2. Check for Non-HTML / empty
        if not fetched.content:
            return {
                "status_entry": status_entry,
                "extraction_meta": extraction_meta,
            }

        # 3. Main Content Extraction from HTML
        ext_result = extract_main_content(
            html_content=fetched.content,
            source_url=source.source_url,
            final_url=fetched.final_url,
            content_type=fetched.content_type,
        )
        extraction_meta = ext_result.metadata.to_dict()

        if ext_result.metadata.extraction_status == "insufficient_content" or len(ext_result.text) < MIN_CHUNK_LENGTH:
            status_entry["status"] = "insufficient_content"
            return {
                "status_entry": status_entry,
                "extraction_meta": extraction_meta,
            }

        # 4. PATENTSCOPE Policy (Requirement 11)
        q_lower = question.lower()
        if "patentscope" in fetched.final_url.lower() and any(k in q_lower for k in PATENTSCOPE_KEYWORDS):
            ps_notice = (
                "Official WIPO PATENTSCOPE Portal search reference: "
                "To search and inspect individual published patent applications, international publication numbers (WO), "
                "or applicants, query the official public portal at https://patentscope.wipo.int/search/en/search.jsf. "
                "Ayurlex provides verified framework guidance and does not scrape or fabricate unverified individual patent filings."
            )
            chunk = {
                "document_id": f"live_{source.source_url}",
                "title": source.title,
                "source_url": "https://patentscope.wipo.int/search/en/search.jsf",
                "jurisdiction": source.jurisdiction,
                "section_label": "WIPO PATENTSCOPE Search Framework",
                "content": ps_notice,
                "score": 3.0,
            }
            return {
                "status_entry": status_entry,
                "extraction_meta": extraction_meta,
                "chunk": chunk,
            }

        excerpt = _build_relevant_excerpt(ext_result.text, query_terms, question=question)
        score = _score_text(excerpt, query_terms) + 1.0

        if len(excerpt) < MIN_CHUNK_LENGTH:
            status_entry["status"] = "insufficient_content"
            return {
                "status_entry": status_entry,
                "extraction_meta": extraction_meta,
            }

        chunk = {
            "document_id": f"live_{source.source_url}",
            "title": source.title,
            "source_url": fetched.final_url,
            "jurisdiction": source.jurisdiction,
            "section_label": "Live official website content",
            "content": excerpt,
            "score": score,
        }
        return {
            "status_entry": status_entry,
            "extraction_meta": extraction_meta,
            "chunk": chunk,
        }

    except SourceConnectionError as e:
        status_entry["status"] = "unavailable"
        status_entry["reason"] = str(e)
    except Exception as e:
        status_entry["status"] = "unavailable"
        status_entry["reason"] = type(e).__name__

    return {
        "status_entry": status_entry,
        "extraction_meta": extraction_meta,
    }


def get_live_research_chunks(
    question: str,
    jurisdiction: str,
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Execute live research across at most 3 top approved official sources.
    Returns:
        (chunks, source_statuses, extraction_metadata)
    """
    # Requirement 6: Router selects at most 3 relevant sources
    selected_sources = route_question_to_sources(
        question=question,
        jurisdiction=jurisdiction,
    )[:MAX_LIVE_SOURCES]

    query_terms = _extract_query_terms(question)

    chunks: list[dict] = []
    source_statuses: list[dict] = []
    extraction_metadata: list[dict] = []

    # Fetch concurrently with thread pool
    ordered_results = [None] * len(selected_sources)
    with ThreadPoolExecutor(max_workers=min(3, max(1, len(selected_sources)))) as pool:
        future_map = {
            pool.submit(_fetch_and_extract_source, source, question, query_terms): idx
            for idx, source in enumerate(selected_sources)
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                ordered_results[idx] = future.result()
            except Exception as e:
                ordered_results[idx] = {
                    "status_entry": {
                        "title": selected_sources[idx].title,
                        "source_url": selected_sources[idx].source_url,
                        "status": "unavailable",
                        "reason": str(e),
                    },
                    "extraction_meta": {
                        "source_url": selected_sources[idx].source_url,
                        "status": "unavailable",
                    },
                }

    # Assemble results and rank evidence chunks
    total_chars = 0
    candidate_chunks = []

    for item in ordered_results:
        if not item:
            continue
        if "status_entry" in item:
            source_statuses.append(item["status_entry"])
        if "extraction_meta" in item:
            extraction_metadata.append(item["extraction_meta"])
        if "chunk" in item:
            candidate_chunks.append(item["chunk"])

    # Rank chunks by score descending
    candidate_chunks.sort(key=lambda c: c.get("score", 0), reverse=True)

    for chunk in candidate_chunks:
        rem_budget = MAX_CONTEXT_CHARS_TOTAL - total_chars
        if rem_budget <= 0:
            break
        if len(chunk["content"]) > rem_budget:
            chunk["content"] = chunk["content"][:rem_budget]

        chunk["chunk_id"] = len(chunks) + 1
        chunks.append(chunk)
        total_chars += len(chunk["content"])

    # Fall back to verified stored corpus if live sources yielded no usable chunks
    if not chunks:
        from retriever import search_chunks
        corpus_chunks = search_chunks(question, jurisdiction)
        if corpus_chunks:
            for c in corpus_chunks:
                source_statuses.append({
                    "title": c.get("title", "Official Corpus Document"),
                    "source_url": c.get("url", ""),
                    "status": "stored_hit",
                })
                c["chunk_id"] = len(chunks) + 1
                chunks.append(c)

    return chunks, source_statuses, extraction_metadata
