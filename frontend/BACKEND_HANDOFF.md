# Ayurlex Frontend-to-Backend Master Handoff

- **Project status**: IN PROGRESS; Frontend baseline initialized at 0%.
- **Frontend owner**: UI, client state, typed API clients, responsive/accessibility implementation, design system, test suites, and documentation.
- **Backend owner**: APIs, authentication & authorization enforcement, database persistence, corpus ingestion & updates, legal/business rules, RAG retrieval orchestration, citations verification, confidence scoring, and audit logging.
- **Contract status guideline**: All endpoints and schemas are **PROPOSED** until explicitly agreed with the backend team.

---

## 1. Existing Backend Baseline
- **Observed in `backend/main.py`**:
  - `GET /` — API root status.
  - `GET /health` — Health check endpoint (`{"status": "ok"}`).
  - `POST /query` — Single research query endpoint accepting `{"question": string}` and returning `{ question, detected_language, query_analysis, jurisdiction, ipr_classification, research_plan, retrieval }`.
- **Target Architecture**: Transition towards versioned REST/SSE endpoints (`/api/v1/...`) supporting streaming responses, structured citations, multi-step classification, and comparison views.

---

## 2. Feature / Module Handoff Register

### Module 1: Chat Query & Streaming (F19, F20, F21, F23, F24, F29, F30)
- **Frontend Files**:
  - `src/features/chat/api.ts`
  - `src/features/chat/useChatStream.ts`
  - `src/features/chat/components/ChatComposer.tsx`
  - `src/features/chat/components/MessageList.tsx`
  - `src/features/chat/components/StreamingMessage.tsx`
  - `src/features/chat/components/ChatStatus.tsx`
- **Proposed Endpoint**: `POST /api/v1/chat/query`
- **Method**: `POST` (Server-Sent Events streaming or JSON fallback)
- **Proposed Request Schema**:
  ```json
  {
    "sessionId": "string (optional/uuid)",
    "question": "string (required, max 2000 chars)",
    "jurisdiction": "india | international",
    "language": "en | hi",
    "formulationContext": "object (optional classification context)"
  }
  ```
- **Proposed SSE Event Types**:
  - `event: status` -> `data: {"stage": "searching" | "analyzing" | "verifying_citations"}`
  - `event: token` -> `data: {"text": "chunk"}`
  - `event: citations` -> `data: {"citations": [Citation]}`
  - `event: done` -> `data: {"messageId": "string", "confidence": "high" | "medium" | "low", "abstention": boolean, "asOfDate": "string"}`
  - `event: error` -> `data: {"code": "string", "message": "user-safe message"}`
- **Contract Status**: `PROPOSED`
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
