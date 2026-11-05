"""
retriever.py
------------
Retrieval layer for the Ayurlex stored corpus.

Uses SQLite FTS5 with BM25 ranking so queries like "Section 3(p) patent
ayurveda" return properly ranked results instead of naive word-count
scoring.  Falls back to LIKE-based search if FTS5 is unavailable.
"""

import re

from database import get_connection

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can",
    "for", "from", "had", "has", "have", "how", "i", "if", "in", "is",
    "it", "its", "me", "my", "not", "of", "on", "or", "our", "so",
    "that", "the", "their", "there", "they", "this", "to", "was", "we",
    "were", "what", "which", "with", "would", "could", "should", "does",
    "do", "did", "you", "your", "but", "about",
}

INDIC_ROMANIZED_STOP_WORDS = {
    "ka", "ki", "ke", "ko", "se", "me", "mein", "par", "pe", "kya", "kyu", "kyun",
    "kaise", "kab", "kaha", "kahan", "hai", "hain", "tha", "thi", "the", "hoga",
    "hogi", "hoge", "hua", "hui", "hue", "aur", "ya", "batao", "bataiye", "batayein",
    "chahiye", "karna", "karne", "kare", "karen", "sakta", "sakte", "sakti",
    "mujhe", "hume", "aap", "tum", "mera", "meri", "mere", "apna", "apni", "apne",
    "yeh", "woh", "is", "us", "in", "un", "toh", "bhi", "lekin", "magar",
}

MULTILINGUAL_CONCEPT_MAP = {
    # Romanized Indic (Hinglish / Latin alphabet)
    "haldi": ["turmeric", "curcuma"],
    "haridra": ["turmeric", "curcuma"],
    "neem": ["neem", "azadirachta"],
    "nimba": ["neem", "azadirachta"],
    "tulsi": ["tulsi", "ocimum"],
    "ashwagandha": ["ashwagandha", "withania"],
    "gomutra": ["cow", "urine", "distillate"],
    "gaumutra": ["cow", "urine", "distillate"],
    "triphala": ["triphala"],
    "chyawanprash": ["chyawanprash"],
    "radd": ["revocation", "revoked", "invalidated"],
    "kharij": ["revocation", "revoked"],
    "nirast": ["revocation", "revoked"],
    "dhara": ["section"],
    "niyam": ["rule"],
    "paramparik": ["traditional", "knowledge"],
    "gyan": ["knowledge"],
    "aushadh": ["drug", "medicine", "formulation"],
    "aushadhi": ["drug", "medicine", "formulation"],
    "dawa": ["drug", "medicine"],
    "dawai": ["drug", "medicine"],
    "jaivik": ["biological", "biodiversity"],
    "vividhta": ["diversity", "biodiversity"],
    "pradhikaran": ["authority", "nba"],
    "anumati": ["approval", "permission"],
    "manzoori": ["approval", "permission"],
    "avishkar": ["invention", "inventive"],
    "navinta": ["novelty", "novel"],
    "sahkriya": ["synergistic", "synergy"],
    "virodh": ["opposition"],
    "shastriya": ["classical", "formulation", "schedule"],
    "granth": ["first", "schedule", "text"],
    "pustak": ["first", "schedule", "text"],
    "manak": ["pharmacopoeia", "standard"],
    # Romanized Tamil / Telugu / regional
    "manjal": ["turmeric"],
    "pasupu": ["turmeric"],
    "veppam": ["neem"],
    "vepa": ["neem"],
    "kappurimai": ["patent"],
    "petent": ["patent"],

    # Hindi / Sanskrit / Marathi
    "हल्दी": ["turmeric", "curcuma"],
    "हळद": ["turmeric", "curcuma", "haldi"],
    "हळदीवर": ["turmeric", "curcuma", "haldi"],
    "नीम": ["neem", "azadirachta"],
    "कडुनिंब": ["neem", "azadirachta"],
    "पेटेंट": ["patent"],
    "पेटंट": ["patent"],
    "रद्द": ["revocation", "revoked", "invalidated"],
    "निरस्त": ["revocation", "revoked"],
    "खारिज": ["revocation", "revoked"],
    "पारंपरिक": ["traditional", "knowledge"],
    "पारम्परिक": ["traditional", "knowledge"],
    "ज्ञान": ["knowledge"],
    "धारा": ["section"],
    "कलम": ["section"],
    "नियम": ["rule"],
    "आयुर्वेद": ["ayurveda", "ayurvedic"],
    "आयुर्वेदिक": ["ayurveda", "ayurvedic"],
    "औषधि": ["drug", "medicine", "formulation"],
    "औषध": ["drug", "medicine", "formulation"],
    "औषधे": ["drug", "medicine", "formulations"],
    "दवा": ["drug", "medicine"],
    "जैव": ["biological", "biodiversity"],
    "जैविक": ["biological", "biodiversity"],
    "विविधता": ["diversity", "biodiversity"],
    "प्राधिकरण": ["authority", "nba"],
    "अनुमति": ["approval", "permission"],
    "परवानगी": ["approval", "permission", "nba"],
    "सहमति": ["approval", "consent"],
    "आविष्कार": ["invention", "inventive"],
    "नवीनता": ["novelty", "novel"],
    "सहक्रिया": ["synergistic", "synergy"],
    "विरोध": ["opposition"],
    "उल्लंघन": ["infringement"],
    "गोमूत्र": ["cow", "urine", "distillate"],
    "तुलसी": ["tulsi", "ocimum"],
    "तुळस": ["tulsi", "ocimum"],
    "अश्वगंधा": ["ashwagandha", "withania"],
    "त्रिफला": ["triphala"],
    "च्यवनप्राश": ["chyawanprash"],
    "फॉर्म": ["form"],
    "नोंदणी": ["registration", "filing"],
    "परवाना": ["license", "licensing"],
    "उत्पादन": ["manufacturing", "manufacture"],
    "अर्क": ["extract", "fraction"],
    "तपासणी": ["examination"],
    "अनुसंधान": ["research"],

    # Tamil
    "மஞ்சள்": ["turmeric"],
    "வேம்பு": ["neem"],
    "காப்புரிமை": ["patent"],
    "பாரம்பரிய": ["traditional"],
    "அறிவு": ["knowledge"],
    "பிரிவு": ["section"],

    # Telugu
    "పసుపు": ["turmeric"],
    "వేప": ["neem"],
    "పేటెంట్": ["patent"],
    "సాంప్రదాయ": ["traditional"],
    "జ్ఞానం": ["knowledge"],
    "సెక్షన్": ["section"],

    # Kannada
    "ಅರಿಶಿನ": ["turmeric"],
    "ಬೇವಿನ": ["neem"],
    "ಪೇಟೆಂಟ್": ["patent"],

    # Gujarati
    "હળદર": ["turmeric"],
    "લીમડો": ["neem"],
    "પેટન્ટ": ["patent"],

    # Bengali
    "হলুদ": ["turmeric"],
    "নিম": ["neem"],
    "পেটেন্ট": ["patent"],
}



def extract_search_terms(query: str) -> list[str]:
    """Extract informative search terms from any language input.

    - Preserves Latin/ASCII legal section/rule tokens (e.g. 3, p, 158b).
    - Extracts non-Latin script words (Devanagari, Tamil, Telugu, etc.).
    - Maps multilingual and Romanized (Hinglish/Tanglish) Ayurvedic & legal concepts
      to English statutory terms so queries in any language or transliteration
      match the official legal corpus.
    - Drops English and Romanized Indic stop-words.
    """
    latin_words = re.findall(r"[a-zA-Z0-9]+", query.lower())

    unicode_words = re.findall(
        r"[\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F"
        r"\u0C80-\u0CFF\u0A80-\u0AFF\u0980-\u09FF]{2,}",
        query,
    )

    combined_stop_words = STOP_WORDS | INDIC_ROMANIZED_STOP_WORDS

    informative_latin = [w for w in latin_words if w not in combined_stop_words]
    all_words = informative_latin + unicode_words

    # Multilingual concept expansion: map Indic and Romanized terms to English corpus keywords
    expanded_terms = list(all_words)
    for word in (latin_words + unicode_words):
        if word in MULTILINGUAL_CONCEPT_MAP:
            for eng_term in MULTILINGUAL_CONCEPT_MAP[word]:
                if eng_term not in expanded_terms:
                    expanded_terms.append(eng_term)

    return expanded_terms


def _build_fts_query(terms: list[str], raw_query: str = "") -> str:
    """Build an FTS5 query string from search terms and optional legal phrases.

    Uses OR logic so partial matches still surface results, while
    BM25 ranking ensures multi-term hits float to the top.
    Adds legal phrases like 'section 3' if present in the raw query.
    """
    safe_terms: list[str] = []

    # Detect legal section phrases in the raw query (e.g., "section 3", "rule 158b")
    if raw_query:
        sec_phrases = re.findall(
            r"\b(?:section|rule|article|chapter)\s+\d+[a-z]?",
            raw_query.lower(),
        )
        for phrase in sec_phrases:
            cleaned_phrase = re.sub(r'["\'\-*^()]', "", phrase).strip()
            if cleaned_phrase:
                safe_terms.append(f'"{cleaned_phrase}"')

    # Add individual terms
    for term in terms:
        cleaned = re.sub(r'["\'\-*^()]', "", term).strip()
        if cleaned and f'"{cleaned}"' not in safe_terms:
            safe_terms.append(f'"{cleaned}"')

    return " OR ".join(safe_terms)


def search_chunks(
    query: str,
    jurisdiction: str | None = None,
    limit: int = 8,
) -> list[dict]:
    """Search the stored corpus using FTS5 with BM25 ranking.

    Returns up to *limit* chunks sorted by relevance.
    """
    search_terms = extract_search_terms(query)

    if not search_terms:
        return []

    fts_query = _build_fts_query(search_terms, raw_query=query)
    if not fts_query:
        return []

    try:
        return _fts5_search(fts_query, jurisdiction, limit, raw_query=query)
    except Exception:
        # FTS5 table may not exist yet – fall back to LIKE search
        return _fallback_search(search_terms, jurisdiction, limit)


def _fts5_search(
    fts_query: str,
    jurisdiction: str | None,
    limit: int,
    raw_query: str = "",
) -> list[dict]:
    """Execute FTS5 match query with BM25 ranking."""
    sql = """
        SELECT
            chunks.id          AS chunk_id,
            chunks.section_label,
            chunks.content,
            documents.id       AS document_id,
            documents.title,
            documents.source_url,
            documents.jurisdiction,
            bm25(chunks_fts, 3.0, 1.0)  AS rank
        FROM chunks_fts
        JOIN chunks
            ON chunks.id = chunks_fts.rowid
        JOIN documents
            ON documents.id = chunks.document_id
        WHERE chunks_fts MATCH ?
    """
    params: list = [fts_query]

    if jurisdiction:
        sql += " AND documents.jurisdiction = ?"
        params.append(jurisdiction)

    sql += " ORDER BY rank, chunks.id ASC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    results = [
        {
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "title": row["title"],
            "source_url": row["source_url"],
            "jurisdiction": row["jurisdiction"],
            "section_label": row["section_label"],
            "content": row["content"],
            "score": abs(row["rank"]),  # BM25 returns negative scores
        }
        for row in rows
    ]

    if results and results[0]["score"] >= 10.0:
        top_score = results[0]["score"]
        results = [r for r in results if r["score"] >= top_score * 0.35]

    # Specific Authority Grounding check:
    # If the user specifically asks for European Patent Office / EPO, only return chunks from EPO.
    # Never return WTO or Indian documents to answer a question specifically about EPO practice.
    q_lower = (raw_query or "").lower()
    if any(k in q_lower for k in ["european patent office", "epo", "european patent"]):
        results = [
            c for c in results
            if "epo.org" in c.get("source_url", "").lower()
            or "european patent office" in c.get("title", "").lower()
            or "epo" in c.get("title", "").lower()
        ]

    return results


def _fallback_search(
    search_terms: list[str],
    jurisdiction: str | None,
    limit: int,
) -> list[dict]:
    """LIKE-based fallback when FTS5 is not available."""
    sql = """
        SELECT
            chunks.id AS chunk_id,
            chunks.section_label,
            chunks.content,
            documents.id AS document_id,
            documents.title,
            documents.source_url,
            documents.jurisdiction
        FROM chunks
        JOIN documents
            ON documents.id = chunks.document_id
    """
    params: list = []

    if jurisdiction:
        sql += " WHERE documents.jurisdiction = ?"
        params.append(jurisdiction)

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    results = []
    for row in rows:
        content_lower = (row["content"] or "").lower()
        label_lower = (row["section_label"] or "").lower()
        score = sum(
            content_lower.count(term) + (label_lower.count(term) * 3)
            for term in search_terms
        )
        if score == 0:
            continue

        results.append(
            {
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "title": row["title"],
                "source_url": row["source_url"],
                "jurisdiction": row["jurisdiction"],
                "section_label": row["section_label"],
                "content": row["content"],
                "score": score,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]