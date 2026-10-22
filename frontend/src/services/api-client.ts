/**
 * Ayurlex Centralized Typed API Client
 * Mediates all network communication. Never accesses database or vector store directly from browser.
 */

export interface Citation {
  id: string;
  documentId: string;
  title: string;
  jurisdiction: 'india' | 'international';
  locator?: string;
  sourceUrl?: string;
  publicationDate?: string;
  effectiveDate?: string;
  amendmentStatus?: string;
  documentStatus?: 'current' | 'superseded' | 'unknown';
}

export interface ResearchQueryPayload {
  question: string;
  jurisdiction?: 'india' | 'international';
  language?: 'en' | 'hi';
  sessionId?: string;
}

export interface ResearchQueryResponse {
  question: string;
  answer?: string;
  detected_language?: string;
  detected_jurisdiction?: string;
  confidence?: 'high' | 'medium' | 'low';
  is_abstained?: boolean;
  citations: Citation[];
  as_of_date?: string;
  retrieval?: Record<string, unknown>;
  research_plan?: Record<string, unknown>;
  query_analysis?: Record<string, unknown>;
  ipr_classification?: Record<string, unknown>;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Health check to test backend connection
   */
  async checkHealth(): Promise<{ status: string }> {
    try {
      const res = await fetch(`${this.baseUrl}/health`);
      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }
      return await res.json();
    } catch {
      return { status: 'disconnected' };
    }
  }

  /**
   * Submits a research question to the backend.
   * Handles the existing backend contract (/query) and gracefully formats the response.
   */
  async submitResearchQuery(payload: ResearchQueryPayload): Promise<ResearchQueryResponse> {
    const res = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: payload.question,
      }),
    });

    if (!res.ok) {
      throw new Error(`Research query request failed with status ${res.status}`);
    }

    const data = await res.json();

    // Map backend response safely into typed format
    const citations: Citation[] = [];
    if (data.retrieval && Array.isArray(data.retrieval.sources)) {
      data.retrieval.sources.forEach((src: any, index: number) => {
        citations.push({
          id: `cit_${index + 1}`,
          documentId: src.id || `doc_${index + 1}`,
          title: src.title || 'Official Statutory Source',
          jurisdiction: (src.jurisdiction as 'india' | 'international') || 'india',
          locator: src.section || src.rule,
          sourceUrl: src.url,
          publicationDate: src.date,
          documentStatus: 'current',
        });
      });
    }

    return {
      question: data.question || payload.question,
      answer: data.summary || (data.research_plan ? JSON.stringify(data.research_plan, null, 2) : undefined),
      detected_language: data.detected_language,
      detected_jurisdiction: data.jurisdiction?.jurisdiction,
      citations,
      confidence: 'medium',
      is_abstained: false,
      retrieval: data.retrieval,
      research_plan: data.research_plan,
      query_analysis: data.query_analysis,
      ipr_classification: data.ipr_classification,
    };
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
