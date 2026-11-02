from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    jurisdiction: Literal["india", "international"] = "india"
    response_mode: Literal["fast", "ai"] = "fast"
    language: str = "auto"


class Source(BaseModel):
    id: str
    title: str
    jurisdiction: Literal["india", "international"]
    section: str
    url: str


class QueryAnalysis(BaseModel):
    intent: Literal[
        "PATENT_DISCOVERY",
        "PATENTABILITY_ADVICE",
        "PATENT_FILING_PROCESS",
        "AYUSH_REGULATION",
        "INTERNATIONAL_IP",
        "UNKNOWN_OR_AMBIGUOUS",
    ]
    confidence: Literal["high", "medium", "low"] = "high"
    missing_filters: list[str] = Field(default_factory=list)
    should_ask_clarification: bool = False
    clarification_prompt: str = ""
    clarification_examples: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    question: str
    summary: str
    confidence: Literal["high", "medium", "low"]
    is_abstained: bool
    disclaimer: str
    retrieval: dict
    research_mode: Literal["stored", "live", "hybrid"] = "stored"
    source_statuses: list[dict] = Field(default_factory=list)
    extraction_metadata: list[dict] = Field(default_factory=list)
    evidence_count: int = 0
    response_time_ms: float = 0.0
    query_analysis: QueryAnalysis | None = None


class ConnectSourceRequest(BaseModel):
    title: str = Field(min_length=3)
    source_url: str = Field(min_length=8)
    jurisdiction: Literal["india", "international"]


class ConnectSourceResponse(BaseModel):
    title: str
    source_url: str
    final_url: str
    content_type: str
    content_length: int
    status: str


class CrawlSourceRequest(BaseModel):
    title: str = Field(min_length=3)
    start_url: str = Field(min_length=8)
    jurisdiction: Literal["india", "international"]
    max_pages: int = Field(default=5, ge=1, le=5)
