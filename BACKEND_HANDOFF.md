# Ayurlex Frontend-to-Backend Master Handoff

- **Project status**: VERIFIED & COMPLETE — Research-Answer Agent architecture with internal evidence grounding, intent classification, and streaming live.
- **Frontend owner**: UI, client state, typed API clients, responsive/accessibility implementation, design system, test suites, and documentation.
- **Backend owner**: APIs, authentication & authorization enforcement, database persistence, corpus ingestion & updates, legal/business rules, RAG retrieval orchestration, citations verification, confidence scoring, and audit logging.
- **Contract status guideline**: Endpoints listed as **CONFIRMED** are live and tested. Others are **PROPOSED**.
- **Last updated**: 2026-11-01

---

## 1. Confirmed Backend Endpoints (Live & Tested)

| Method | Path | Status | Notes |
|--------|------|--------|-------|
| `GET` | `/health` | **CONFIRMED** | Returns `{status, message}` |
| `POST` | `/query` | **CONFIRMED** | Stored corpus search only |
| `POST` | `/research/live` | **CONFIRMED** | Live official-source fetch |
| `POST` | `/research/smart` | **CONFIRMED** | Auto corpus→live fallback |
| `POST` | `/admin/research/route` | **CONFIRMED** | Returns routed source list |
| `GET` | `/admin/sources` | **CONFIRMED** | Lists ingested documents |
| `POST` | `/admin/sources/ingest` | **CONFIRMED** | Fetches and saves raw HTML |
| `POST` | `/admin/sources/{id}/chunk` | **CONFIRMED** | Chunks saved HTML into DB |
| `POST` | `/query/stream` | **CONFIRMED** | SSE Server-Sent Events progressive streaming |
| `POST` | `/research/live/stream` | **CONFIRMED** | SSE live research progressive streaming |
| `GET` | `/admin/engine/status` | **CONFIRMED** | Returns connected browsers (Chrome, Edge) & search engine status |

### `POST /research/smart`, `POST /query`, `POST /research/live` (CONFIRMED & TESTED)
**Request**:
```json
{
  "question": "string (min 3 chars)",
  "jurisdiction": "india | international",
  "response_mode": "fast | ai",
  "language": "auto | en | hi | ..."
}
```
**Response** (`QueryResponse`):
```json
{
  "question": "string",
  "summary": "string",
  "confidence": "high | medium | low",
  "is_abstained": boolean,
  "disclaimer": "Ayurlex provides information for research purposes and does not provide legal advice.",
  "retrieval": {
    "sources": [{ "id": "chunk_N", "title": "...", "jurisdiction": "...", "section": "...", "url": "..." }],
    "chunks": [...],
    "source_statuses": [{ "title": "...", "source_url": "...", "status": "..." }]
  },
  "research_mode": "stored | live | hybrid",
  "source_statuses": [...],
  "extraction_metadata": [...],
  "evidence_count": integer,
  "response_time_ms": float
}
```
`source_statuses.status` values: `stored_hit` | `corpus_hit` | `corpus_insufficient` | `corpus_miss` | `fetched` | `rendered` | `pdf_extracted` | `unavailable` | `insufficient_content` | `skipped_non_html` | `blocked` | `timeout`


## 2. Feature / Module Handoff Register

### Module 1: Chat Query & Streaming (F19, F20, F21, F23, F24, F29, F30)
- **Frontend Files**:
  - `src/features/chat/useChatSession.ts`
  - `src/features/chat/components/ChatComposer.tsx`
  - `src/features/chat/components/MessageList.tsx`
  - `src/features/chat/components/MessageBubble.tsx`
  - `src/features/chat/components/ChatStatus.tsx`
  - `src/features/answers/components/AnswerRenderer.tsx`
- **Confirmed Endpoints**: `POST /query/stream`, `POST /research/live/stream`
- **Method**: `POST` (Server-Sent Events streaming with `text/event-stream`)
- **Event Types**:
  - `event: status` -> `data: {"stage": "routing" | "researching_sources" | "generating_detailed_answer"}`
  - `event: fast_answer` -> `data: {"summary": "...", "sources": [...], "is_abstained": boolean, "confidence": "..."}`
  - `event: token` -> `data: {"text": "partial text"}`
  - `event: complete` -> `data: {"answer": "full answer", "sources": [...], "confidence": "...", "is_abstained": boolean}`
  - `event: error` -> `data: {"message": "..."}`
- **Contract Status**: `CONFIRMED`
- **Backend Work Required**: Implement SSE streaming generator or adapt `/query` into streaming endpoint with citation metadata.

---

### Module 2: Formulation Classification Wizard (F13 - F18)
- **Frontend Files**:
  - `src/features/classification/components/ClassificationWizard.tsx`
  - `src/features/classification/components/ClassificationQuestion.tsx`
  - `src/features/classification/components/ClassificationProgress.tsx`
  - `src/features/classification/components/ClassificationSummary.tsx`
  - `src/features/classification/components/ClassificationResult.tsx`
- **Proposed Endpoint**: `POST /api/v1/classify/formulation`
- **Method**: `POST`
- **Proposed Request Schema**:
  ```json
  {
    "answers": {
      "hasClassicalReference": boolean,
      "containsHeavyMetals": boolean,
      "innovativeProcess": boolean,
      "targetIndications": ["string"],
      "compositionNotes": "string"
    }
  }
  ```
- **Proposed Response Schema**:
  ```json
  {
    "category": "Classical Formulation | Proprietary Medicine | ASU Extract | Not Eligible",
    "confidence": "high | medium | low",
    "legalBasis": "string",
    "regulatoryNotes": "string",
    "suggestedIprPathway": ["Patent", "GI", "Trademark"],
    "ruleReferences": ["Drugs and Cosmetics Act, Section 3(a)", "..."]
  }
  ```
- **Contract Status**: `PROPOSED`
- **Backend Work Required**: Connect decision tree / ML classifier to provide structured decision rationale.

---

### Module 3: Jurisdiction Comparison (F11)
- **Frontend Files**:
  - `src/features/jurisdiction/components/JurisdictionComparisonView.tsx`
- **Proposed Endpoint**: `POST /api/v1/jurisdiction/compare`
- **Method**: `POST`
- **Proposed Request Schema**:
  ```json
  {
    "query": "string",
    "jurisdictions": ["india", "international"]
  }
  ```
- **Proposed Response Schema**:
  ```json
  {
    "india": {
      "summary": "string",
      "citations": [Citation],
      "provisions": ["string"]
    },
    "international": {
      "summary": "string",
      "citations": [Citation],
      "provisions": ["string"]
    },
    "keyDifferences": ["string"]
  }
  ```
- **Contract Status**: `PROPOSED`

---

### Module 4: Session & History Management (F12, F22, F45 - F50, F84)
- **Frontend Files**:
  - `src/features/session/sessionStore.ts`
  - `src/features/session/api.ts`
  - `src/features/history/components/ConversationList.tsx`
- **Proposed Endpoints**:
  - `GET /api/v1/sessions` — List user research sessions.
  - `POST /api/v1/sessions` — Create a new session.
  - `GET /api/v1/sessions/{id}/messages` — Fetch message history.
  - `DELETE /api/v1/sessions/{id}` — Clear or delete session data.
- **Contract Status**: `PROPOSED`

---

### Module 5: Admin Corpus & Ingestion Health (F76 - F82)
- **Frontend Files**:
  - `src/features/admin/components/CorpusOverviewCards.tsx`
  - `src/features/admin/components/IngestionStatusTable.tsx`
  - `src/features/admin/components/SourceHealthTable.tsx`
- **Proposed Endpoint**: `GET /api/v1/admin/corpus/status`
- **Contract Status**: `PROPOSED`

---

## 3. Change Log
- **2026-10-22**: Document initialized at project baseline (0% progress). All contracts marked `PROPOSED`. Existing backend endpoint `POST /query` noted for reference.
- **2026-10-31**: Live research agent rebuilt. Full official-source catalogue added to `source_router.py` and `connectors/website_connector.py`:
  - **TKDL** (`tkdl.res.in`) — Traditional Knowledge Digital Library, home + search
  - **India Code** acts: Patents Act, Trademarks Act, Designs Act, GI Act, Biological Diversity Act, Drugs & Cosmetics Act, PPVFR Act
  - **IP India Patents** — InPASS e-filing search, Patent Search portal, Patent Journal, IP India main
  - **IP India Trademarks** — TM Registry, TM Public Search
  - **IP India Designs** — Designs Registry, Design Search portal
  - **IP India GI** — GI Registry
  - **NBA / ABS Portal** (`nbaindia.org`) — NBA home, ABS guidelines
  - **CDSCO + CDSCO-ASU** — drug regulation, Rule 158B, ASU schedules
  - **FSSAI + FSSAI Regulations** — food/nutraceutical standards
  - **WIPO PCT** — PCT system page, PATENTSCOPE search
  - **WIPO Madrid** — Madrid System, Madrid Monitor (Brand DB)
  - **WIPO Hague** — Hague System for international design registration
  - **WIPO Budapest** — Budapest Treaty for microorganism deposits
  - **WIPO TK / GRs** — Traditional Knowledge & Genetic Resources IGC
  - **WIPO GI** — Geographical Indications, Lisbon Agreement
  - **WIPO Treaties** — Paris Convention, general treaty portal
  - **WTO TRIPS** — TRIPS Agreement text + Art. 27.3(b) TK page
  - **CBD Nagoya Protocol** — ABS page + full Nagoya text
  - **CBD Home** — Convention on Biological Diversity portal
  - `research_agent.py` rebuilt: concurrent fetching (ThreadPoolExecutor), relevance window excerpt (4 000 chars/source, 24 000 total budget), 2-gram query term matching, no hard 3-source cap (up to 8 priority-ordered sources).
  - `agent.py`: MAX_EXCERPT_CHARACTERS raised 700→3 500, max_output_tokens raised 400→800, system instructions improved.
- **2026-10-31**: Frontend F85/F88 completed. No new backend contracts required; privacy consent is client-side only (PROPOSED: backend should not log query text without consent flag).
- **2026-10-31**: PROPOSED: retrieval.sources[] should include document_status ('current'|'superseded') — frontend now shows 'unknown' when absent. Prior-art panel detects TKDL/PATENTSCOPE/IP India by source URL hostname; no new endpoint needed.
- **2026-10-31**: Stored corpus retrieval and indexing fix:
  - `retriever.py`: Search term extraction updated to preserve single-token section and clause identifiers (e.g. `3`, `p`, `d`, `e`) while filtering English stopwords. Added phrase matching for statutory citations (`section 3`, `rule 158b`) and boosted `section_label` weight in BM25 ranking (3.0 for label, 1.0 for content) so relevant statutory sections surface at the top.
  - `corpus_seeder.py`: Fixed bug in `seed_embedded_corpus()` that checked document-level existence and skipped duplicate `source_url` chunks; now checks chunk-level existence (`_chunk_exists`) ensuring all 17 curated statutory provisions (Section 3(p), 3(e), 2(1)(j), Section 25, Sections 84-92, TKDL Biopiracy) are properly seeded and indexed.
  - `pdf_chunker.py`: Added fallback to `pypdf` when `pymupdf` is not installed; made section labeling stateful across chunks to preserve chapter and section titles across chunk boundaries instead of falling back to "General". Re-indexed Patents Act PDF into 254 structured chunks.
  - Verified smart research scoring (`debug_score.py`) now computes relevance >= 41.9 for Section 3(p) queries, correctly triggering `corpus_hit` rather than unnecessary live web requests.

### 2026-11-01: Multilingual NLP Auto-Detection Contract & Indic Retrieval
- **Endpoints Affected**: `POST /query`, `POST /research/smart`
- **New Field in QueryRequest**: `language: str = "auto"`
  - When `language: "auto"`, the backend runs script-based detection (`detect_input_language`) to identify the query script (Devanagari/Hindi, Tamil, Telugu, Kannada, Gujarati, Bengali, etc.).
  - FTS5 retrieval uses `MULTILINGUAL_CONCEPT_MAP` in `retriever.py` to bridge non-English queries to official English statutory texts without losing precision.
  - Gemini `SYSTEM_INSTRUCTIONS` mandates responding in the exact language the user used.
  - Fast answers return localized headers and guidance in Hindi for Devanagari input.

### 2026-11-01 (Part 2): Romanized / Latin-Script Multilingual NLP & Language Analysis
- **NLP Analysis for English-word inputs**:
  - `detect_input_language()` analyzes English/Latin word queries for:
    1. **Hinglish/Romanized Indic grammar & vocabulary**: (`kya`, `kaise`, `kyu`, `batao`, `dawai`, `radd`, `haldi`, `neem`, `dhara`).
    2. **Explicit language prompts**: e.g., `explain in tamil`, `answer in marathi`, `in hindi please`.
  - When detected, the backend instructs Gemini to respond in the matching native language (Hindi, Tamil, Marathi, etc.) with verified statutory citations.
  - `retriever.py` extracts informative search terms and maps Romanized keywords (`haldi` -> `turmeric`, `radd` -> `revocation`) while removing Hinglish stop-words (`ka`, `ki`, `ke`, `ko`, `se`, `me`, `par`, `pe`, `kyu`, `hua`, `hai`).
