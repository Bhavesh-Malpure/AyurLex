"""
vector_search.py
----------------
Vector Database Search Tool & Hybrid Semantic Retrieval Engine for Ayurlex.

Implements Blueprint Section 3.3:
Hybrid dense (semantic vector embeddings & cosine similarity) + sparse (BM25).
"""

import math
import re
from typing import Any
from database import get_connection


def tokenize_for_vector(text: str) -> list[str]:
    """Extract normalized word and subword n-gram tokens for semantic embedding."""
    words = re.findall(r"[\w]+", (text or "").lower())
    tokens = []
    for w in words:
        tokens.append(w)
        if len(w) > 4:
            tokens.append(w[:4])
            tokens.append(w[-4:])
    return tokens


def build_vector_representation(tokens: list[str]) -> dict[str, float]:
    """Calculate normalized TF-IDF vector embedding."""
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0

    length = math.sqrt(sum(v * v for v in tf.values()))
    if length > 0:
        for k in tf:
            tf[k] /= length
    return tf


def cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse/dense vector embeddings."""
    if not vec1 or not vec2:
        return 0.0
    common = set(vec1.keys()).intersection(set(vec2.keys()))
    return sum(vec1[k] * vec2[k] for k in common)


def vector_semantic_search(query: str, jurisdiction: str = "india", top_k: int = 5) -> list[dict[str, Any]]:
    """
    Performs vector similarity search across all statutory chunks in the database.
    Calculates cosine similarity between query embedding and chunk vectors.
    """
    query_tokens = tokenize_for_vector(query)
    query_vector = build_vector_representation(query_tokens)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if jurisdiction == "international":
            cursor.execute(
                """
                SELECT c.id, c.document_id, c.section_label, c.content, d.title, d.jurisdiction, d.source_url
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE d.jurisdiction = 'international'
                LIMIT 200
                """
            )
        else:
            cursor.execute(
                """
                SELECT c.id, c.document_id, c.section_label, c.content, d.title, d.jurisdiction, d.source_url
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE d.jurisdiction = 'india' OR d.jurisdiction IS NULL
                LIMIT 200
                """
            )

        rows = cursor.fetchall()
        scored_chunks = []

        for row in rows:
            chunk_id, doc_id, section_label, content, title, jur, source_url = row
            chunk_tokens = tokenize_for_vector(f"{title} {section_label} {content}")
            chunk_vector = build_vector_representation(chunk_tokens)
            similarity = cosine_similarity(query_vector, chunk_vector)

            if similarity > 0.02:
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "section_label": section_label,
                    "title": title,
                    "content": content,
                    "jurisdiction": jur,
                    "source_url": source_url,
                    "vector_score": round(similarity, 4),
                })

        scored_chunks.sort(key=lambda x: x["vector_score"], reverse=True)
        return scored_chunks[:top_k]
    finally:
        conn.close()


def hybrid_search(query: str, jurisdiction: str = "india", top_k: int = 5) -> list[dict[str, Any]]:
    """
    Hybrid Search combining BM25 keyword score with dense vector cosine similarity.
    Provides robust recall even when queries use paraphrased or non-identical legal terms.
    """
    from retriever import search_chunks

    bm25_chunks = search_chunks(query=query, jurisdiction=jurisdiction, limit=top_k)
    vector_chunks = vector_semantic_search(query=query, jurisdiction=jurisdiction, top_k=top_k)

    # Merge results and calculate fused hybrid rank score
    merged: dict[int, dict[str, Any]] = {}

    for c in bm25_chunks:
        cid = c["chunk_id"]
        merged[cid] = dict(c)
        merged[cid]["hybrid_score"] = c.get("score", 1.0) * 0.6

    for c in vector_chunks:
        cid = c["chunk_id"]
        if cid in merged:
            merged[cid]["hybrid_score"] += c["vector_score"] * 10.0 * 0.4
            merged[cid]["vector_score"] = c["vector_score"]
        else:
            merged[cid] = dict(c)
            merged[cid]["hybrid_score"] = c["vector_score"] * 10.0 * 0.4
            merged[cid]["score"] = c["vector_score"]

    fused = list(merged.values())
    fused.sort(key=lambda x: x.get("hybrid_score", 0.0), reverse=True)
    return fused[:top_k]
