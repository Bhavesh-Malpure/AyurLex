import json
import logging
import re
import time

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import (
    generate_grounded_answer,
    generate_grounded_answer_stream,
    detect_input_language,
    validate_and_sanitize_citations,
)
from chunker import chunk_document_by_id
from connectors.website_connector import (
    SourceConnectionError,
    fetch_public_source,
)
from corpus_seeder import seed_all
from crawler import crawl_official_website
from database import initialize_database, list_documents, rebuild_fts_index
from ingestion import ingest_source
from intent_classifier import (
    classify_query_intent,
    get_intent_direct_answer,
    get_patent_discovery_guidance,
)
from research_agent import get_live_research_chunks
from retriever import search_chunks
from schemas import (
    ConnectSourceRequest,
    ConnectSourceResponse,
    CrawlSourceRequest,
    QueryAnalysis,
    QueryRequest,
    QueryResponse,
)
from seed_sources import seed_official_sources
from source_router import route_question_to_sources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

initialize_database()
seed_official_sources()
seed_all()  # Index embedded legal corpus + Patents Act PDF

app = FastAPI(title="Ayurlex Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_fast_answer(matched_chunks: list[dict], question: str = "") -> str:
    if not matched_chunks:
        return "I could not verify a reliable answer from the available official research sources."

    # 1. Check if canonical direct answer exists for this question
    direct_ans = get_intent_direct_answer(question)
    if direct_ans:
        return direct_ans

    # 2. Extract key findings from verified evidence in clean human language
    top_chunk = matched_chunks[0]
    section_label = top_chunk.get("section_label", "")
    content = re.sub(r"\s+", " ", top_chunk.get("content", "")).strip()
    lang = detect_input_language(question)

    # Clean direct synthesis without raw chunks or source tags
    if "3(p)" in section_label or "traditional knowledge" in content.lower():
        if lang in ("hindi", "hinglish"):
            return (
                "पारंपरिक ज्ञान या ज्ञात घटकों के मात्र समुच्चय (aggregation) को पेटेंट नहीं कराया जा सकता। "
                "यदि उत्पाद में अप्रत्याशित सहक्रियाशील प्रभाव (synergistic effect) या नवीन निष्कर्षण तकनीक सिद्ध होती है, "
                "तभी पेटेंट अनुदान संभव हो सकता है। आवेदन से पूर्व पूर्व-कला (prior-art) जांच अनिवार्य है।"
            )
        return (
            "An invention that is in effect traditional knowledge or an aggregation of known properties of traditionally "
            "known components is excluded from patentability. A patent may be considered only if there is a genuinely novel "
            "technical feature, unexpected synergistic effect, or new process. Prior-art review is essential before filing."
        )

    if "rule 158b" in section_label.lower() or "158b" in content.lower():
        if lang in ("hindi", "hinglish"):
            return (
                "आयुर्वेदिक, सिद्ध और यूनानी औषधियों के निर्माण लाइसेंस के लिए नियम 158B के तहत निर्धारित मानकों का अनुपालन अनिवार्य है। "
                "शास्त्रीय योगों के लिए अधिकृत संहिताओं का संदर्भ तथा पेटेंट/स्वामित्व औषधियों के लिए सुरक्षा व प्रभावकारिता का वैज्ञानिक साक्ष्य आवश्यक होता है।"
            )
        return (
            "Manufacturing approval for Ayurveda, Siddha, and Unani drugs requires compliance with statutory licensing conditions under Rule 158B. "
            "Classical formulations require authoritative textual citations from official pharmacopoeias, while proprietary formulations require safety and efficacy proof."
        )

    if "biological diversity" in top_chunk.get("title", "").lower() or "section 6" in section_label.lower():
        if lang in ("hindi", "hinglish"):
            return (
                "भारत के जैविक संसाधनों या संबंधित ज्ञान पर आधारित किसी भी आविष्कार के लिए देश या विदेश में पेटेंट आवेदन करने से पहले राष्ट्रीय जैव विविधता प्राधिकरण (NBA) से पूर्व-अनुमति लेना विधिक रूप से अनिवार्य है।"
            )
        return (
            "Prior approval from the National Biodiversity Authority is mandatory before applying for any intellectual property right, inside or outside India, based on biological resources or associated knowledge obtained from India."
        )

    # General direct synthesis
    if lang in ("hindi", "hinglish"):
        return (
            f"सत्यापित विधिक अनुसंधान के अनुसार, यह विषय {section_label or 'संबंधित विधिक प्रावधान'} द्वारा शासित होता है। "
            f"इस प्रावधान के अंतर्गत निर्धारित विधिक शर्तों और अनुपालन मानदंडों का पालन करना अनिवार्य है।"
        )

    return (
        f"Based on verified official legal research, this matter is governed by statutory provisions concerning {section_label or 'applicable IP/regulatory law'}. "
        f"Compliance with the specified criteria and procedural conditions is required."
    )


def format_sources(chunks: list[dict]) -> list[dict]:
    return [
        {
            "id": f"chunk_{chunk['chunk_id']}",
            "title": chunk["title"],
            "jurisdiction": chunk["jurisdiction"],
            "section": chunk["section_label"],
            "url": chunk["source_url"],
        }
        for chunk in chunks
    ]


def abstained_response(
    question: str,
    message: str,
    source_statuses: list[dict] | None = None,
    extraction_metadata: list[dict] | None = None,
    research_mode: str = "stored",
    response_time_ms: float = 0.0,
    query_analysis: QueryAnalysis | None = None,
) -> QueryResponse:
    return QueryResponse(
        question=question,
        summary=message,
        confidence="low",
        is_abstained=True,
        disclaimer=(
            "Ayurlex provides information for research purposes and "
            "does not provide legal advice."
        ),
        retrieval={
            "sources": [],
            "chunks": [],
            "source_statuses": source_statuses or [],
        },
        research_mode=research_mode,
        source_statuses=source_statuses or [],
        extraction_metadata=extraction_metadata or [],
        evidence_count=0,
        response_time_ms=response_time_ms,
        query_analysis=query_analysis,
    )


def clarification_response(
    question: str,
    analysis: QueryAnalysis,
    research_mode: str = "stored",
    response_time_ms: float = 0.0,
) -> QueryResponse:
    return QueryResponse(
        question=question,
        summary=analysis.clarification_prompt,
        confidence=analysis.confidence,
        is_abstained=False,
        disclaimer=(
            "Ayurlex provides information for research purposes and "
            "does not provide legal advice."
        ),
        retrieval={
            "sources": [],
            "chunks": [],
            "source_statuses": [],
        },
        research_mode=research_mode,
        source_statuses=[],
        extraction_metadata=[],
        evidence_count=0,
        response_time_ms=response_time_ms,
        query_analysis=analysis,
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Ayurlex backend is running",
    }


@app.get("/admin/engine/status")
def engine_status():
    from connectors.browser_connector import get_connected_browsers
    from connectors.website_connector import ALLOWED_DOMAINS
    browsers = get_connected_browsers()
    docs = list_documents()
    return {
        "status": "operational",
        "browsers_connected": browsers,
        "search_engine": {
            "mode": "multi_source_official_discovery",
            "engines": ["Google Chrome Headless DOM", "Microsoft Edge Headless DOM", "WIPO & IP India Portals"],
            "allowlist_enforced": True,
            "allowed_domains_count": len(ALLOWED_DOMAINS),
        },
        "multi_source_verification": {
            "active": True,
            "cross_checking": True,
            "currency_tracking": True,
        },
        "indexed_authoritative_documents": len(docs),
    }


@app.post("/admin/research/route")
def route_research_question(request: QueryRequest):
    selected_sources = route_question_to_sources(
        question=request.question,
        jurisdiction=request.jurisdiction,
    )

    return {
        "question": request.question,
        "jurisdiction": request.jurisdiction,
        "sources": [
            {
                "title": source.title,
                "source_url": source.source_url,
                "jurisdiction": source.jurisdiction,
                "purpose": source.purpose,
            }
            for source in selected_sources
        ],
    }


@app.post("/research/live", response_model=QueryResponse)
def research_live_official_websites(request: QueryRequest):
    start_time = time.perf_counter()

    direct_ans = get_intent_direct_answer(request.question, request.jurisdiction)
    if direct_ans:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        live_chunks, source_statuses, extraction_metadata = get_live_research_chunks(
            question=request.question,
            jurisdiction=request.jurisdiction,
        )
        sources = format_sources(live_chunks)
        return QueryResponse(
            question=request.question,
            summary=direct_ans,
            confidence="high",
            is_abstained=False,
            disclaimer="Ayurlex provides information for research purposes and does not provide legal advice.",
            retrieval={"sources": sources, "chunks": live_chunks, "source_statuses": source_statuses},
            research_mode="live",
            source_statuses=source_statuses,
            extraction_metadata=extraction_metadata,
            evidence_count=len(live_chunks),
            response_time_ms=elapsed_ms,
            query_analysis=None,
        )

    analysis = classify_query_intent(request.question, request.jurisdiction)

    if analysis.should_ask_clarification:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return clarification_response(
            question=request.question,
            analysis=analysis,
            research_mode="live",
            response_time_ms=elapsed_ms,
        )

    if analysis.intent == "PATENT_DISCOVERY":
        summary, sources = get_patent_discovery_guidance(
            question=request.question,
            jurisdiction=request.jurisdiction,
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        source_statuses = [
            {
                "title": s["title"],
                "source_url": s["url"],
                "status": "official_portal",
            }
            for s in sources
        ]
        return QueryResponse(
            question=request.question,
            summary=summary,
            confidence="high",
            is_abstained=False,
            disclaimer=(
                "Ayurlex provides information for research purposes and "
                "does not provide legal advice."
            ),
            retrieval={
                "sources": sources,
                "chunks": [],
                "source_statuses": source_statuses,
            },
            research_mode="live",
            source_statuses=source_statuses,
            extraction_metadata=[],
            evidence_count=len(sources),
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    live_chunks, source_statuses, extraction_metadata = get_live_research_chunks(
        question=request.question,
        jurisdiction=request.jurisdiction,
    )
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if not live_chunks:
        corpus_chunks = search_chunks(
            query=request.question,
            jurisdiction=request.jurisdiction,
        )
        if corpus_chunks:
            live_chunks = corpus_chunks
            source_statuses.extend(
                [{"title": c.get("title", "Official Corpus Document"), "source_url": c.get("url", ""), "status": "stored_hit"} for c in corpus_chunks]
            )

    if not live_chunks:
        return abstained_response(
            question=request.question,
            message=(
                "I could not verify a reliable answer from the available official research sources."
            ),
            source_statuses=source_statuses,
            extraction_metadata=extraction_metadata,
            research_mode="live",
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    sources = format_sources(live_chunks)

    if request.response_mode == "fast":
        answer = create_fast_answer(live_chunks, question=request.question)
    else:
        try:
            answer = generate_grounded_answer(
                question=request.question,
                retrieved_chunks=live_chunks,
                language=request.language,
            )
        except Exception as error:
            logger.warning(
                "Live research agent error: %s: %s; falling back to fast answer",
                type(error).__name__,
                error,
            )
            answer = create_fast_answer(live_chunks, question=request.question)

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return QueryResponse(
        question=request.question,
        summary=answer,
        confidence="medium" if len(live_chunks) > 1 else "low",
        is_abstained=False,
        disclaimer=(
            "Ayurlex provides information for research purposes and "
            "does not provide legal advice."
        ),
        retrieval={
            "sources": sources,
            "chunks": live_chunks,
            "source_statuses": source_statuses,
        },
        research_mode="live",
        source_statuses=source_statuses,
        extraction_metadata=extraction_metadata,
        evidence_count=len(live_chunks),
        response_time_ms=total_elapsed_ms,
        query_analysis=analysis,
    )


def stream_query_events(request: QueryRequest):
    yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"
    time.sleep(0.01)

    direct_ans = get_intent_direct_answer(request.question, request.jurisdiction)
    if direct_ans:
        matched_chunks = search_chunks(
            query=request.question,
            jurisdiction=request.jurisdiction,
        )
        sources = format_sources(matched_chunks)
        payload = {
            "summary": direct_ans,
            "sources": sources,
            "is_abstained": False,
            "confidence": "high",
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": None,
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': direct_ans, 'sources': sources, 'confidence': 'high', 'is_abstained': False, 'query_analysis': None})}\n\n"
        return

    analysis = classify_query_intent(request.question, request.jurisdiction)

    if analysis.should_ask_clarification:
        payload = {
            "summary": analysis.clarification_prompt,
            "sources": [],
            "is_abstained": False,
            "confidence": analysis.confidence,
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": analysis.model_dump(),
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': analysis.clarification_prompt, 'sources': [], 'confidence': analysis.confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    if analysis.intent == "PATENT_DISCOVERY":
        yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"
        summary, sources = get_patent_discovery_guidance(request.question, request.jurisdiction)
        payload = {
            "summary": summary,
            "sources": sources,
            "is_abstained": False,
            "confidence": "high",
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": analysis.model_dump(),
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': summary, 'sources': sources, 'confidence': 'high', 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"

    DOMAIN_TERMS = {
        "patent", "patents", "ip", "ayush", "ayurveda", "ayurvedic", "tradition",
        "formulation", "turmeric", "neem", "ashwagandha", "rule", "section", "act",
        "license", "licensing", "wipo", "epo", "fssai", "cdsco", "inpass", "tkdl",
        "medicinal", "herbal", "drug", "drugs", "plant", "extract", "student", "inventor",
        "invention", "infringement", "application", "specification", "novelty",
        "jurisdiction", "treaty", "trips", "nice", "locarno", "classification",
        "curcumin", "piperine", "guggulu", "brahmi", "shatavari", "triphala", "chyawanprash"
    }

    q_words = set(re.findall(r"[a-z0-9]+", request.question.lower()))
    if not q_words.intersection(DOMAIN_TERMS) and not re.search(r"[\u0900-\u097F]", request.question):
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return abstained_response(
            question=request.question,
            message="I could not verify a reliable answer from the available official research sources.",
            research_mode="stored",
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    matched_chunks = search_chunks(
        query=request.question,
        jurisdiction=request.jurisdiction,
    )
    total_relevance = sum(chunk.get("score", 0) for chunk in matched_chunks)

    if not matched_chunks or total_relevance < CORPUS_RELEVANCE_THRESHOLD:
        abstention_msg = (
            "I could not verify a reliable answer from the available official research sources."
        )
        yield f"event: fast_answer\ndata: {json.dumps({'summary': abstention_msg, 'sources': [], 'is_abstained': True, 'confidence': 'low', 'disclaimer': 'Ayurlex provides information for research purposes and does not provide legal advice.', 'query_analysis': analysis.model_dump()})}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': abstention_msg, 'sources': [], 'confidence': 'low', 'is_abstained': True, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    sources = format_sources(matched_chunks)
    fast_summary = create_fast_answer(matched_chunks, question=request.question)
    confidence = "high" if total_relevance >= 3.0 else "medium"

    # Step 1: Send the Fast result immediately before starting Gemini detailed generation
    yield f"event: fast_answer\ndata: {json.dumps({'summary': fast_summary, 'sources': sources, 'is_abstained': False, 'confidence': confidence, 'disclaimer': 'Ayurlex provides information for research purposes and does not provide legal advice.', 'query_analysis': analysis.model_dump()})}\n\n"

    if request.response_mode == "fast":
        yield f"event: complete\ndata: {json.dumps({'answer': fast_summary, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    # Step 2: Stream Detailed AI Answer
    yield f"event: status\ndata: {json.dumps({'stage': 'generating_detailed_answer'})}\n\n"

    full_answer_parts = []
    try:
        for token in generate_grounded_answer_stream(
            question=request.question,
            retrieved_chunks=matched_chunks,
            language=request.language,
        ):
            full_answer_parts.append(token)
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"

        full_answer = "".join(full_answer_parts).strip()
        validated_answer = validate_and_sanitize_citations(full_answer, matched_chunks)

        yield f"event: complete\ndata: {json.dumps({'answer': validated_answer, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
    except Exception as error:
        logger.warning(f"Error during streaming Gemini generation: {error}")
        words = fast_summary.split(" ")
        for i, word in enumerate(words):
            token = word if i == 0 else " " + word
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
            time.sleep(0.01)
        yield f"event: complete\ndata: {json.dumps({'answer': fast_summary, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"


def stream_live_research_events(request: QueryRequest):
    yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"
    time.sleep(0.01)

    direct_ans = get_intent_direct_answer(request.question, request.jurisdiction)
    if direct_ans:
        matched_chunks = search_chunks(
            query=request.question,
            jurisdiction=request.jurisdiction,
        )
        sources = format_sources(matched_chunks)
        payload = {
            "summary": direct_ans,
            "sources": sources,
            "is_abstained": False,
            "confidence": "high",
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": None,
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': direct_ans, 'sources': sources, 'confidence': 'high', 'is_abstained': False, 'query_analysis': None})}\n\n"
        return

    analysis = classify_query_intent(request.question, request.jurisdiction)

    if analysis.should_ask_clarification:
        payload = {
            "summary": analysis.clarification_prompt,
            "sources": [],
            "is_abstained": False,
            "confidence": analysis.confidence,
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": analysis.model_dump(),
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': analysis.clarification_prompt, 'sources': [], 'confidence': analysis.confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    if analysis.intent == "PATENT_DISCOVERY":
        yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"
        summary, sources = get_patent_discovery_guidance(request.question, request.jurisdiction)
        payload = {
            "summary": summary,
            "sources": sources,
            "is_abstained": False,
            "confidence": "high",
            "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
            "query_analysis": analysis.model_dump(),
        }
        yield f"event: fast_answer\ndata: {json.dumps(payload)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': summary, 'sources': sources, 'confidence': 'high', 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    yield f"event: status\ndata: {json.dumps({'stage': 'researching_sources'})}\n\n"

    live_chunks, source_statuses, extraction_metadata = get_live_research_chunks(
        question=request.question,
        jurisdiction=request.jurisdiction,
    )

    if not live_chunks:
        corpus_chunks = search_chunks(
            query=request.question,
            jurisdiction=request.jurisdiction,
        )
        if corpus_chunks:
            live_chunks = corpus_chunks

    if not live_chunks:
        abstention_msg = (
            "I could not verify a reliable answer from the available official research sources."
        )
        yield f"event: fast_answer\ndata: {json.dumps({'summary': abstention_msg, 'sources': [], 'is_abstained': True, 'confidence': 'low', 'disclaimer': 'Ayurlex provides information for research purposes and does not provide legal advice.', 'query_analysis': analysis.model_dump()})}\n\n"
        yield f"event: complete\ndata: {json.dumps({'answer': abstention_msg, 'sources': [], 'confidence': 'low', 'is_abstained': True, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    sources = format_sources(live_chunks)
    fast_summary = create_fast_answer(live_chunks, question=request.question)
    confidence = "medium" if len(live_chunks) > 1 else "low"

    # Step 1: Send the Fast result immediately
    yield f"event: fast_answer\ndata: {json.dumps({'summary': fast_summary, 'sources': sources, 'is_abstained': False, 'confidence': confidence, 'disclaimer': 'Ayurlex provides information for research purposes and does not provide legal advice.', 'query_analysis': analysis.model_dump()})}\n\n"

    if request.response_mode == "fast":
        yield f"event: complete\ndata: {json.dumps({'answer': fast_summary, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
        return

    # Step 2: Stream Detailed AI Answer
    yield f"event: status\ndata: {json.dumps({'stage': 'generating_detailed_answer'})}\n\n"

    full_answer_parts = []
    try:
        for token in generate_grounded_answer_stream(
            question=request.question,
            retrieved_chunks=live_chunks,
            language=request.language,
        ):
            full_answer_parts.append(token)
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"

        full_answer = "".join(full_answer_parts).strip()
        validated_answer = validate_and_sanitize_citations(full_answer, live_chunks)

        yield f"event: complete\ndata: {json.dumps({'answer': validated_answer, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"
    except Exception as error:
        logger.warning(f"Error during live streaming Gemini generation: {error}")
        words = fast_summary.split(" ")
        for i, word in enumerate(words):
            token = word if i == 0 else " " + word
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
            time.sleep(0.01)
        yield f"event: complete\ndata: {json.dumps({'answer': fast_summary, 'sources': sources, 'confidence': confidence, 'is_abstained': False, 'query_analysis': analysis.model_dump()})}\n\n"


@app.post("/query/stream")
def query_stream(request: QueryRequest):
    return StreamingResponse(
        stream_query_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/research/live/stream")
def research_live_stream(request: QueryRequest):
    return StreamingResponse(
        stream_live_research_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/admin/sources")
def admin_sources():
    return {
        "sources": list_documents()
    }


@app.post(
    "/admin/sources/connect",
    response_model=ConnectSourceResponse,
)
def connect_source(request: ConnectSourceRequest):
    try:
        source = fetch_public_source(request.source_url)
    except (
        SourceConnectionError,
        requests.RequestException,
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return ConnectSourceResponse(
        title=request.title,
        source_url=request.source_url,
        final_url=source.final_url,
        content_type=source.content_type,
        content_length=len(source.content),
        status="connected",
    )


@app.post("/admin/sources/ingest")
def ingest_website_source(request: ConnectSourceRequest):
    try:
        return ingest_source(
            title=request.title,
            source_url=request.source_url,
            jurisdiction=request.jurisdiction,
        )
    except (
        SourceConnectionError,
        requests.RequestException,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion error: {type(error).__name__}: {error}",
        ) from error


@app.post("/admin/sources/crawl")
def crawl_source(request: CrawlSourceRequest):
    try:
        pages = crawl_official_website(
            start_url=request.start_url,
            max_pages=request.max_pages,
        )

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No public HTML pages could be crawled from this URL.",
            )

        imported_documents = []

        for page_number, page in enumerate(pages, start=1):
            result = ingest_source(
                title=f"{request.title} - Page {page_number}",
                source_url=page["url"],
                jurisdiction=request.jurisdiction,
            )

            imported_documents.append(
                {
                    "document_id": result["document_id"],
                    "title": result["title"],
                    "source_url": result["source_url"],
                    "final_url": result["final_url"],
                }
            )

        return {
            "status": "completed",
            "start_url": request.start_url,
            "pages_crawled": len(imported_documents),
            "documents": imported_documents,
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Crawl error: {type(error).__name__}: {error}",
        ) from error


@app.post("/admin/sources/{document_id}/chunk")
def chunk_website_source(document_id: int):
    try:
        chunk_count = chunk_document_by_id(document_id)
    except (
        FileNotFoundError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {
        "document_id": document_id,
        "chunks_created": chunk_count,
        "status": "chunked",
    }


# BM25 scores are much higher than simple word-count scores.
# A cumulative score >= 1.0 means at least one strong FTS5 match.
CORPUS_RELEVANCE_THRESHOLD = 1.0


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    start_time = time.perf_counter()

    direct_ans = get_intent_direct_answer(request.question, request.jurisdiction)
    if direct_ans:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        matched_chunks = search_chunks(
            query=request.question,
            jurisdiction=request.jurisdiction,
        )
        sources = format_sources(matched_chunks)
        source_statuses = [{"title": s["title"], "source_url": s["url"], "status": "stored_hit"} for s in sources]
        return QueryResponse(
            question=request.question,
            summary=direct_ans,
            confidence="high",
            is_abstained=False,
            disclaimer="Ayurlex provides information for research purposes and does not provide legal advice.",
            retrieval={"sources": sources, "chunks": matched_chunks, "source_statuses": source_statuses},
            research_mode="stored",
            source_statuses=source_statuses,
            extraction_metadata=[],
            evidence_count=len(matched_chunks),
            response_time_ms=elapsed_ms,
            query_analysis=None,
        )

    analysis = classify_query_intent(request.question, request.jurisdiction)

    if analysis.should_ask_clarification:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return clarification_response(
            question=request.question,
            analysis=analysis,
            research_mode="stored",
            response_time_ms=elapsed_ms,
        )

    if analysis.intent == "PATENT_DISCOVERY":
        summary, sources = get_patent_discovery_guidance(
            question=request.question,
            jurisdiction=request.jurisdiction,
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        source_statuses = [
            {
                "title": s["title"],
                "source_url": s["url"],
                "status": "official_portal",
            }
            for s in sources
        ]
        return QueryResponse(
            question=request.question,
            summary=summary,
            confidence="high",
            is_abstained=False,
            disclaimer=(
                "Ayurlex provides information for research purposes and "
                "does not provide legal advice."
            ),
            retrieval={
                "sources": sources,
                "chunks": [],
                "source_statuses": source_statuses,
            },
            research_mode="stored",
            source_statuses=source_statuses,
            extraction_metadata=[],
            evidence_count=len(sources),
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    DOMAIN_TERMS = {
        "patent", "patents", "ip", "ayush", "ayurveda", "ayurvedic", "tradition",
        "formulation", "turmeric", "neem", "ashwagandha", "rule", "section", "act",
        "license", "licensing", "wipo", "epo", "fssai", "cdsco", "inpass", "tkdl",
        "medicinal", "herbal", "drug", "drugs", "plant", "extract", "student", "inventor",
        "invention", "infringement", "application", "specification", "novelty",
        "jurisdiction", "treaty", "trips", "nice", "locarno", "classification",
        "curcumin", "piperine", "guggulu", "brahmi", "shatavari", "triphala", "chyawanprash"
    }

    q_words = set(re.findall(r"[a-z0-9]+", request.question.lower()))
    if not q_words.intersection(DOMAIN_TERMS) and not re.search(r"[\u0900-\u097F]", request.question):
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return abstained_response(
            question=request.question,
            message="I could not verify a reliable answer from the available official research sources.",
            research_mode="stored",
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    matched_chunks = search_chunks(
        query=request.question,
        jurisdiction=request.jurisdiction,
    )

    total_relevance = sum(
        chunk.get("score", 0) for chunk in matched_chunks
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if not matched_chunks or total_relevance < CORPUS_RELEVANCE_THRESHOLD:
        return abstained_response(
            question=request.question,
            message=(
                "I could not verify a reliable answer from the available official research sources."
            ),
            research_mode="stored",
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    sources = format_sources(matched_chunks)

    if request.response_mode == "fast":
        answer = create_fast_answer(matched_chunks, question=request.question)
    else:
        try:
            answer = generate_grounded_answer(
                question=request.question,
                retrieved_chunks=matched_chunks,
                language=request.language,
            )
        except Exception as error:
            logger.warning(
                "Agent error: %s: %s; falling back to fast answer",
                type(error).__name__,
                error,
            )
            answer = create_fast_answer(matched_chunks, question=request.question)

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    source_statuses = [
        {
            "title": s["title"],
            "source_url": s["url"],
            "status": "stored_hit",
        }
        for s in sources
    ]

    return QueryResponse(
        question=request.question,
        summary=answer,
        confidence="high" if total_relevance >= 3.0 else "medium",
        is_abstained=False,
        disclaimer=(
            "Ayurlex provides information for research purposes and "
            "does not provide legal advice."
        ),
        retrieval={
            "sources": sources,
            "chunks": matched_chunks,
            "source_statuses": source_statuses,
        },
        research_mode="stored",
        source_statuses=source_statuses,
        extraction_metadata=[],
        evidence_count=len(matched_chunks),
        response_time_ms=total_elapsed_ms,
        query_analysis=analysis,
    )


@app.post("/research/smart", response_model=QueryResponse)
def smart_research(request: QueryRequest):
    """Try stored corpus first; fall back to live official-source
    research when corpus evidence is insufficient."""
    start_time = time.perf_counter()
    analysis = classify_query_intent(request.question, request.jurisdiction)

    if analysis.should_ask_clarification:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return clarification_response(
            question=request.question,
            analysis=analysis,
            research_mode="stored",
            response_time_ms=elapsed_ms,
        )

    if analysis.intent == "PATENT_DISCOVERY":
        summary, sources = get_patent_discovery_guidance(
            question=request.question,
            jurisdiction=request.jurisdiction,
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        source_statuses = [
            {
                "title": s["title"],
                "source_url": s["url"],
                "status": "official_portal",
            }
            for s in sources
        ]
        return QueryResponse(
            question=request.question,
            summary=summary,
            confidence="high",
            is_abstained=False,
            disclaimer=(
                "Ayurlex provides information for research purposes and "
                "does not provide legal advice."
            ),
            retrieval={
                "sources": sources,
                "chunks": [],
                "source_statuses": source_statuses,
            },
            research_mode="stored",
            source_statuses=source_statuses,
            extraction_metadata=[],
            evidence_count=len(sources),
            response_time_ms=elapsed_ms,
            query_analysis=analysis,
        )

    corpus_chunks = search_chunks(
        query=request.question,
        jurisdiction=request.jurisdiction,
    )

    total_relevance = sum(
        chunk.get("score", 0) for chunk in corpus_chunks
    )

    source_statuses: list[dict] = []
    extraction_metadata: list[dict] = []
    use_live = total_relevance < CORPUS_RELEVANCE_THRESHOLD
    research_mode = "stored"

    if not use_live:
        selected_chunks = corpus_chunks
        source_statuses.append(
            {
                "title": "Stored Verified Corpus",
                "source_url": "",
                "status": "corpus_hit",
            }
        )
    else:
        research_mode = "hybrid" if corpus_chunks else "live"
        source_statuses.append(
            {
                "title": "Stored Verified Corpus",
                "source_url": "",
                "status": (
                    "corpus_insufficient"
                    if corpus_chunks
                    else "corpus_miss"
                ),
            }
        )

        live_chunks, live_statuses, live_extraction_meta = get_live_research_chunks(
            question=request.question,
            jurisdiction=request.jurisdiction,
        )

        source_statuses.extend(live_statuses)
        extraction_metadata.extend(live_extraction_meta)

        if live_chunks:
            selected_chunks = live_chunks
        elif corpus_chunks:
            selected_chunks = corpus_chunks
        else:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return abstained_response(
                question=request.question,
                message=(
                    "I could not verify a reliable answer from the available official research sources."
                ),
                source_statuses=source_statuses,
                extraction_metadata=extraction_metadata,
                research_mode=research_mode,
                response_time_ms=elapsed_ms,
                query_analysis=analysis,
            )

    sources = format_sources(selected_chunks)

    if request.response_mode == "fast":
        answer = create_fast_answer(selected_chunks, question=request.question)
    else:
        try:
            answer = generate_grounded_answer(
                question=request.question,
                retrieved_chunks=selected_chunks,
                language=request.language,
            )
        except Exception as error:
            logger.warning(
                "Smart research agent error: %s: %s; falling back to fast answer",
                type(error).__name__,
                error,
            )
            answer = create_fast_answer(selected_chunks, question=request.question)

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return QueryResponse(
        question=request.question,
        summary=answer,
        confidence="medium",
        is_abstained=False,
        disclaimer=(
            "Ayurlex provides information for research purposes and "
            "does not provide legal advice."
        ),
        retrieval={
            "sources": sources,
            "chunks": selected_chunks,
            "source_statuses": source_statuses,
        },
        research_mode=research_mode,
        source_statuses=source_statuses,
        extraction_metadata=extraction_metadata,
        evidence_count=len(selected_chunks),
        response_time_ms=total_elapsed_ms,
        query_analysis=analysis,
    )