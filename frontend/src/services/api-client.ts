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
  language?: string;
  sessionId?: string;
  responseMode?: 'fast' | 'ai';
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

export interface StreamEventHandlers {
  onStatus?: (stage: string) => void;
  onToken?: (text: string) => void;
  onFastAnswer?: (data: { summary: string; sources: Citation[]; isAbstained: boolean; confidence: string }) => void;
  onComplete?: (data: { answer: string; sources: Citation[]; confidence: 'high' | 'medium' | 'low'; isAbstained: boolean }) => void;
  onError?: (err: Error) => void;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined
  ? import.meta.env.VITE_API_BASE_URL
  : '';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Helper to perform fetch with automatic fallback from relative proxy path
   * to direct http://127.0.0.1:8000 if needed on localhost.
   */
  private async safeFetch(endpoint: string, options?: RequestInit): Promise<Response> {
    const primaryUrl = `${this.baseUrl}${endpoint}`;
    try {
      const res = await fetch(primaryUrl, options);
      return res;
    } catch (primaryErr) {
      // Fallback: If running in browser and primary path failed, try direct port 8000
      if (!this.baseUrl && typeof window !== 'undefined') {
        try {
          const fallbackUrl = `http://127.0.0.1:8000${endpoint}`;
          const res = await fetch(fallbackUrl, options);
          return res;
        } catch {
          // Re-throw original error
        }
      }
      throw primaryErr;
    }
  }

  /**
   * Health check to test backend connection
   */
  async checkHealth(): Promise<{ status: string; message?: string }> {
    try {
      const res = await this.safeFetch('/health');
      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }
      return await res.json();
    } catch {
      return { status: 'disconnected', message: 'FastAPI backend unreachable' };
    }
  }

  /**
   * Submits a research question to the backend.
   * Handles the backend contract (/query or /research/smart) with accurate field mapping.
   */
  async submitResearchQuery(payload: ResearchQueryPayload): Promise<ResearchQueryResponse> {
    const res = await this.safeFetch('/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: payload.question,
        jurisdiction: payload.jurisdiction || 'india',
        response_mode: payload.responseMode || 'fast',
        language: payload.language || 'auto',
      }),
    });

    if (!res.ok) {
      throw new Error(`Research query request failed with status ${res.status}`);
    }

    const data = await res.json();

    // Map backend sources safely into typed format
    const citations: Citation[] = [];
    if (data.retrieval && Array.isArray(data.retrieval.sources)) {
      data.retrieval.sources.forEach((src: any, index: number) => {
        citations.push({
          id: src.id || `cit_${index + 1}`,
          documentId: src.id || `doc_${index + 1}`,
          title: src.title || 'Official Statutory Source',
          jurisdiction: (src.jurisdiction as 'india' | 'international') || 'india',
          locator: src.section || src.rule || undefined,
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
      detected_jurisdiction: data.jurisdiction?.jurisdiction || payload.jurisdiction,
      citations,
      confidence: (data.confidence as 'high' | 'medium' | 'low') || 'medium',
      is_abstained: Boolean(data.is_abstained),
      retrieval: data.retrieval,
      research_plan: data.research_plan,
      query_analysis: data.query_analysis,
      ipr_classification: data.ipr_classification,
      as_of_date: 'Gazette of India (2024)',
    };
  }

  /**
   * Progressive Server-Sent Events (SSE) streaming research query.
   * Enables real-time word-by-word streaming in the chat interface.
   */
  async streamResearchQuery(
    payload: ResearchQueryPayload,
    handlers: StreamEventHandlers
  ): Promise<void> {
    try {
      const response = await this.safeFetch('/query/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          question: payload.question,
          jurisdiction: payload.jurisdiction || 'india',
          response_mode: payload.responseMode || 'ai',
          language: payload.language || 'auto',
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Streaming failed with status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          const eventMatch = block.match(/^event:\s*(\w+)/m);
          const dataMatch = block.match(/^data:\s*(.+)$/m);

          if (!eventMatch || !dataMatch) continue;

          const eventType = eventMatch[1];
          try {
            const parsedData = JSON.parse(dataMatch[1]);

            if (eventType === 'status' && handlers.onStatus) {
              handlers.onStatus(parsedData.stage);
            } else if (eventType === 'token' && handlers.onToken) {
              handlers.onToken(parsedData.text);
            } else if (eventType === 'fast_answer' && handlers.onFastAnswer) {
              const mappedSources: Citation[] = (parsedData.sources || []).map((s: any, idx: number) => ({
                id: s.id || `cit_${idx + 1}`,
                documentId: s.id || `doc_${idx + 1}`,
                title: s.title || 'Official Statutory Source',
                jurisdiction: (s.jurisdiction as 'india' | 'international') || 'india',
                locator: s.section || s.rule,
                sourceUrl: s.url,
                publicationDate: s.date,
                documentStatus: 'current',
              }));
              handlers.onFastAnswer({
                summary: parsedData.summary,
                sources: mappedSources,
                isAbstained: Boolean(parsedData.is_abstained),
                confidence: parsedData.confidence || 'high',
              });
            } else if (eventType === 'complete' && handlers.onComplete) {
              const mappedSources: Citation[] = (parsedData.sources || []).map((s: any, idx: number) => ({
                id: s.id || `cit_${idx + 1}`,
                documentId: s.id || `doc_${idx + 1}`,
                title: s.title || 'Official Statutory Source',
                jurisdiction: (s.jurisdiction as 'india' | 'international') || 'india',
                locator: s.section || s.rule,
                sourceUrl: s.url,
                publicationDate: s.date,
                documentStatus: 'current',
              }));
              handlers.onComplete({
                answer: parsedData.answer,
                sources: mappedSources,
                confidence: (parsedData.confidence as 'high' | 'medium' | 'low') || 'high',
                isAbstained: Boolean(parsedData.is_abstained),
              });
            } else if (eventType === 'error') {
              throw new Error(parsedData.message || 'Stream error');
            }
          } catch (parseErr) {
            console.error('Error parsing SSE event:', parseErr);
          }
        }
      }
    } catch (err: any) {
      if (handlers.onError) {
        handlers.onError(err instanceof Error ? err : new Error(String(err)));
      } else {
        throw err;
      }
    }
  }

  /**
   * Blueprint 9.4: /api/v1/classify/formulation
   */
  async classifyFormulation(answers: Record<string, unknown>): Promise<any> {
    const res = await this.safeFetch('/api/v1/classify/formulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    if (!res.ok) throw new Error(`Classification failed: ${res.status}`);
    return await res.json();
  }

  /**
   * Blueprint 9.4: /api/v1/abs/check
   */
  async checkAbsCompliance(payload: {
    resource_name: string;
    intended_use?: 'commercial' | 'patent' | 'research' | 'transfer';
    entity_type?: 'domestic' | 'foreign';
    is_commodity?: boolean;
  }): Promise<any> {
    const res = await this.safeFetch('/api/v1/abs/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`ABS check failed: ${res.status}`);
    return await res.json();
  }

  /**
   * Blueprint 9.4: /api/v1/tkdl/search
   */
  async searchTkdlPriorArt(query: string, botanicalName: string = ''): Promise<any> {
    const res = await this.safeFetch('/api/v1/tkdl/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, botanical_name: botanicalName }),
    });
    if (!res.ok) throw new Error(`TKDL search failed: ${res.status}`);
    return await res.json();
  }

  /**
   * Blueprint 9.4: /api/v1/jurisdiction/compare
   */
  async compareJurisdictions(topic: string): Promise<any> {
    const res = await this.safeFetch('/api/v1/jurisdiction/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });
    if (!res.ok) throw new Error(`Compare failed: ${res.status}`);
    return await res.json();
  }

  /**
   * Blueprint 9.4: /api/v1/escalate
   */
  async escalateToFacilitator(payload: {
    sessionId: string;
    summary: string;
    query: string;
    contactEmail?: string;
  }): Promise<any> {
    const res = await this.safeFetch('/api/v1/escalate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: payload.sessionId,
        summary: payload.summary,
        query: payload.query,
        contact_email: payload.contactEmail || '',
      }),
    });
    if (!res.ok) throw new Error(`Escalation failed: ${res.status}`);
    return await res.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
