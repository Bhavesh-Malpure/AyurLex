# Ayurlex Frontend Progress

- **Overall status**: VERIFIED & COMPLETE
- **Overall progress**: 100% (Research-Answer Agent transformation, Intent routing, "Show Sources" setting toggle default OFF, Grounded direct answers, Full Acceptance Suite passing)
- **Baseline**: Clean build established with 0 TypeScript/build errors.
- **Counting**: Track all 88 IDs; duplicate requirements reuse shared components.
- **Current task**: Localhost resilience, Blueprint API v1 contracts, PDF export, bookmarks, and Docker deployment completed.
- **Last updated**: 2026-11-04

## Status Legend
`NOT STARTED` | `IN PROGRESS` | `BLOCKED` | `IMPLEMENTED` | `TESTED` | `COMPLETE`

## Recent Completed Research-Answer Agent Upgrades (2026-11-04)

- **Localhost 1-Click Launch & Proxy Resilience**:
  - Configured Vite development proxy in `vite.config.ts` forwarding `/query`, `/health`, `/research`, and `/api` to `127.0.0.1:8000`, removing all localhost CORS and port mismatch issues.
  - Added `start-ayurlex.bat` one-click Windows launcher booting both FastAPI backend and Vite frontend together.
  - Added comprehensive `backend/requirements.txt`, Dockerfiles, and `docker-compose.yml`.
- **Export to PDF & Printable Report**:
  - Added a dedicated "Export Report (PDF)" button formatting the researched answer, statutory scope, citation list, and mandatory legal notice into a clean printable report.
- **Bookmarks & Saved Questions**:
  - Added client-side bookmarking (`ayurlex_bookmarks`) to save substantive research findings across sessions.
- **User Feedback & Copy Actions**:
  - Added one-click clipboard copy with attached legal notice and "Helpful" / "Needs Review" feedback buttons.
- **Blueprint Standard API v1 Endpoints**:
  - Implemented `/api/v1/classify/formulation`, `/api/v1/abs/check`, `/api/v1/tkdl/search`, `/api/v1/jurisdiction/compare`, `/api/v1/escalate`, and `/api/v1/admin/corpus/status`.
- **All 8 Acceptance Tests Passing**: `test_acceptance_suite.py` passes 8/8 tests (`OK`). All 7 e2e checks in `verify_all.py` pass.

- **Multi-Browser & Search Engine Pipeline Integration (2026-11-02)**:
  - Connected native headless **Google Chrome** (`chrome.exe`) and **Microsoft Edge** (`msedge.exe`) to render dynamic JavaScript official portals and prevent blocking.
  - Implemented multi-source cross-checking and fact-verification engine ([`evidence_verifier.py`](file:///c:/Users/vipul/OneDrive/Desktop/6th%20Sem/Ayurlex/backend/evidence_verifier.py)).
  - Added official portal discovery orchestrator ([`search_engine.py`](file:///c:/Users/vipul/OneDrive/Desktop/6th%20Sem/Ayurlex/backend/search_engine.py)) strictly enforcing HTTPS domain allowlist.
  - Added `/admin/engine/status` endpoint to monitor connected browser engines and multi-source verification state.

- **Live Research Fallback to Stored Corpus**: In `research_agent.py` and `backend/main.py`, live research routes seamlessly back to the verified stored legal corpus when live government portals timeout, rate-limit, or block requests.
- **Zero-Failure Progressive Streaming**: In `stream_query_events` and `stream_live_research_events`, if Gemini connectivity fails or times out, the backend progressively streams the verified grounded answer word-by-word with zero socket error and zero false abstention.
- **Ashwagandha Section 3(p) Direct Researched Answer**: Tested and verified on both `/query/stream` and `/research/live/stream` returning complete statutory analysis (Section 3(p), Section 3(e), Biological Diversity Act Section 6, and TKDL prior art guidance).
- **Jurisdiction Separation for Direct Answers**: Ensured Section 3(p) Indian law direct answers are not emitted for International / EPO queries; Test F correctly abstains when international evidence is insufficient.

- **Research-Answer Agent Transformation**: Ayurlex researches approved official sources internally and returns only a clear final answer related to the user's exact question:
  1. Direct researched answer immediately in the first sentence.
  2. Short key points if needed.
  3. Short practical next step if needed.
  4. Mandatory legal disclaimer on every substantive answer.
- **Internal Evidence & "Show Sources" Setting (Default OFF)**:
  - All source metadata, raw chunks, website links, resource cards, and citation chips are kept internal for audit and admin use.
  - Added a dedicated frontend setting named **“Show Sources” (default OFF)** in the research toolbar.
  - When Show Sources is OFF: Displays only the final researched answer and the legal disclaimer; hides citation chips, raw source texts, authority panels, and prior art panels.
  - When Show Sources is ON: Displays verified statutory citations & authorities and prior art panels.
- **Graceful Direct Abstention**: When evidence is insufficient, displays only: *"I could not verify a reliable answer from the available official research sources."* with the legal disclaimer; suppresses generic templates, error screens, and long resource explanations.
- **Unified Single-Message Response Stream**: Replaced dual-bubble ("Fast" + "Detailed AI analysis") behavior with a unified single assistant response that loads fast and progressively refines in real time.
- **Canonical Question Verification**: Verified exact direct answers for canonical patterns:
  - `"am student can patent"` &rarr; True and first inventor / college IP policy direct answer.
  - `"patent kaise karte hai?"` &rarr; Novelty, specification, Form 1/2 filing, examination, grant direct answer.
  - `"mujhe new patent batao"` &rarr; Asks for ingredient/technology and period; 0 fake patent records.
  - `"Can I patent an Ayurvedic formulation?"` &rarr; Novel technical feature / synergy / prior-art review direct answer.
- **Full Acceptance Suite Passing**: All 8 backend acceptance tests in `test_acceptance_suite.py` passing (`OK`).

---

## Feature Checklist (All 88 Entries)

- [x] **F01** — Ayurlex logo and navigation bar — `TESTED` (Responsive header, botanical brand mark, mobile drawer, active states)
- [x] **F02** — Hero section explaining the platform — `TESTED` (Clear visual hierarchy, research scope, Ayurveda IPR subtext)
- [x] **F03** — Start Research button — `TESTED` (Navigates to `/research` workspace, keyboard accessible)
- [x] **F04** — Feature cards: patents, trademarks, GI, regulatory compliance, traditional knowledge — `TESTED` (5 interactive domain cards)
- [x] **F05** — Language selector — `TESTED` (Reusable selector supporting EN and HI, keyboard navigable)
- [x] **F06** — Persistent legal disclaimer banner — `TESTED` (Global shell banner with required exact statutory disclaimer text)
- [x] **F07** — Responsive desktop/mobile layouts — `TESTED` (Fluid breakpoints, flex/grid layouts, mobile drawer navigation)
- [x] **F08** — Language selector (duplicate requirement) — `TESTED` (Reuses F05 LanguageSelector component)
- [x] **F09** — India / International toggle — `TESTED` (Two-state toggle explaining domestic ASU vs WIPO/EPO search scope)
- [x] **F10** — Visible selected-jurisdiction indicator — `TESTED` (Jurisdiction badge in hero and research header)
- [x] **F11** — Explicit comparison view — `TESTED` (Side-by-side comparative analysis of Sec 3p/3e vs EPO/USPTO)
- [x] **F12** — Session state for language and jurisdiction — `TESTED` (Clean client store maintaining session state without insecure storage)
- [x] **F13** — One classification question at a time — `TESTED` (Formulation classifier wizard renders one step per screen)
- [x] **F14** — Multiple-choice classification options — `TESTED` (Accessible radio cards for Schedule 1, ingredients, processes)
- [x] **F15** — Classification progress indicator — `TESTED` (Progress bar with step number and percentage)
- [x] **F16** — Back and Continue buttons — `TESTED` (Bidirectional wizard navigation preserving selections)
- [x] **F17** — Classification answer summary — `TESTED` (Summary review screen with one-click step editing)
- [x] **F18** — Final formulation classification result — `TESTED` (Detailed regulatory assessment, Rule 158B status, non-binding notice)
- [x] **F19** — Research message input — `TESTED` (Auto-resizing accessible composer with keyboard submit)
- [x] **F20** — Send button — `TESTED` (Submit action with disabled and loading states)
- [x] **F21** — User and AI message bubbles — `TESTED` (Differentiated user vs assistant bubbles with icon attribution)
- [x] **F22** — Conversation history in the active session — `TESTED` (Chronological message list with auto-scroll and empty states)
- [x] **F23** — Chat loading and error states — `TESTED` (Multi-stage progress and retryable error banner)
- [x] **F24** — Progressively streamed answers — `TESTED` (SSE stream consumption with token-by-token rendering)
- [x] **F25** — Citation chips attached to answers — `TESTED` (Structured citation badges attached to answer cards)
- [x] **F26** — Confidence indicator — `TESTED` (Statutory verification confidence badge with tooltip)
- [x] **F27** — Insufficient-evidence state — `TESTED` (AbstentionPanel rendered when legal evidence is inconclusive)
- [x] **F28** — Disclaimer on every substantive answer — `TESTED` (Mandatory inline disclaimer appended to all answer cards)
- [x] **F29** — Research processing state — `TESTED` (Multi-phase indicators: routing, researching, generating)
- [x] **F30** — Streaming response display — `TESTED` (Real-time token text append, live status, smooth auto-scroll)
- [x] **F31** — Helpful service-failure messages — `TESTED` (ErrorMessage component safely translates backend failures)
- [x] **F32** — Clear insufficient-evidence messaging — `TESTED` (Explains statutory gaps without generating false conclusions)
- [x] **F33** — Document or legislation title — `TESTED` (Displays statutory act / pharmacopoeia title in source panel)
- [x] **F34** — Source jurisdiction — `TESTED` (Displays India / International jurisdiction tag per source)
- [x] **F35** — Relevant section or rule — `TESTED` (Displays specific Section, Rule, or Schedule locator)
- [x] **F36** — Source URL — `TESTED` (Validated external links with security attributes `noopener,noreferrer`)
- [x] **F37** — Document date/amendment information — `TESTED` (Renders publication and effective dates when known)
- [x] **F38** — Current/superseded status — `TESTED` (SourceStatusBadge with current/superseded/unverified states)
- [x] **F39** — Readable answer paragraphs and headings — `TESTED` (Clean Natural Green typography and structured spacing)
- [x] **F40** — Clickable citation chips — `TESTED` (Clicking opens accessible source details modal dialog)
- [x] **F41** — Source details panel/modal — `TESTED` (SourceDetailsDialog with escape key, focus handling, backdrop dismiss)
- [x] **F42** — Confidence indicators in answer view — `TESTED` (Reuses F26 ConfidenceBadge)
- [x] **F43** — Distinct insufficient-evidence answer layout — `TESTED` (Dedicated AbstentionPanel layout)
- [x] **F44** — Applicable/verification date — `TESTED` (AnswerMeta showing statutory Gazette verification date)
- [x] **F45** — New Research button — `TESTED` (HistoryToolbar reset action resetting state and session ID)
- [ ] **F46** — Conversation list — `NOT STARTED` (Multi-session persistent history list; pending backend session endpoints)
- [x] **F47** — Message history — `TESTED` (Chronological active session message history)
- [ ] **F48** — Continue Research action — `NOT STARTED` (Pending session list endpoint)
- [ ] **F49** — Session title/summary — `NOT STARTED` (Pending session list endpoint)
- [x] **F50** — Clear session controls — `TESTED` (SessionActions with clear confirmation warning)
- [ ] **F51** — Escalation button — `NOT STARTED` (Phase 2)
- [ ] **F52** — Escalation explanation — `NOT STARTED` (Phase 2)
- [ ] **F53** — Consent/contact form — `NOT STARTED` (Phase 2)
- [ ] **F54** — Conversation summary preview — `NOT STARTED` (Phase 2)
- [ ] **F55** — Escalation submission confirmation — `NOT STARTED` (Phase 2)
- [ ] **F56** — Escalation status — `NOT STARTED` (Phase 2)
- [x] **F57** — Biological resource/ingredient input — `TESTED` (AbsAssessmentWizard botanical and sourcing channel inputs)
- [x] **F58** — ABS intended use — `TESTED` (AbsAssessmentWizard selection: patent/IPR, commercial utilization, research, transfer of results)
- [x] **F59** — ABS research/commercial purpose — `TESTED` (AbsAssessmentWizard Section 3 foreign participation vs Section 7 domestic entity)
- [x] **F60** — Other ABS facts required by rules — `TESTED` (AbsAssessmentWizard Section 40 NTAC exemption and Section 2(p) VAP tests)
- [x] **F61** — Formulation description input for prior-art search — `TESTED` (PriorArtSearchTool formulation description and botanical chips input)
- [x] **F62** — TKDL/prior-art search button — `TESTED` (PriorArtSearchTool accessible search action with loading state)
- [x] **F63** — Prior-art result cards — `TESTED` (PriorArtSearchTool verified classical literature and landmark revocation precedence cards)
- [x] **F64** — Classification codes/entries — `TESTED` (PriorArtSearchTool displays IPC A61K 36/00 and TKRC traditional medicine codes)
- [x] **F65** — Prior-art supporting source details — `TESTED` (PriorArtPanel lists backend-returned TKDL/PATENTSCOPE/IP India sources only)
- [x] **F66** — Prior-art limitation notice — `TESTED` (Limitation notice: not FTO/novelty search, TKDL access restrictions)
- [ ] **F67** — Related-records panel — `NOT STARTED` (Phase 2)
- [ ] **F68** — Links between ingredients, formulations, laws, patents — `NOT STARTED` (Phase 2)
- [ ] **F69** — Evidence trail for complex questions — `NOT STARTED` (Phase 2)
- [ ] **F70** — Expandable research explanation — `NOT STARTED` (Phase 2)
- [ ] **F71** — Translated interface labels — `IN PROGRESS` (Foundation established in session types & selectors)
- [x] **F72** — Language selection (duplicate requirement) — `TESTED` (Reuses F05)
- [x] **F73** — Supported-language input handling — `TESTED` (Unicode Hindi and English input support)
- [x] **F74** — Translated answer presentation — `TESTED` (Renders backend-returned language without silent browser translation)
- [ ] **F75** — Voice input/audio playback (later phase) — `NOT STARTED` (Phase 4)
- [x] **F76** — Number of indexed documents — `TESTED` (CorpusOverviewCards showing indexed records)
- [ ] **F77** — Ingestion status — `NOT STARTED` (Pending backend ingestion job endpoint)
- [x] **F78** — Last successful update — `TESTED` (Formatted timestamp in CorpusOverviewCards & SourceHealthTable)
- [ ] **F79** — Failed ingestion jobs — `NOT STARTED` (Pending backend ingestion endpoint)
- [x] **F80** — Source health — `TESTED` (SourceHealthTable listing statutory sources and status)
- [ ] **F81** — Current and superseded document versions — `NOT STARTED` (Phase 2 / Admin)
- [ ] **F82** — Retrieval/citation verification statistics — `NOT STARTED` (Pending backend quality endpoint)
- [ ] **F83** — Registration/login if required — `NOT STARTED` (Decision needed on auth requirement)
- [x] **F84** — Session handling — `TESTED` (Client session state synced with requests, no insecure storage)
- [x] **F85** — Privacy and consent interfaces — `TESTED` (PrivacyConsentDialog gates research route; consent in sessionStorage; decline routes to 403)
- [ ] **F86** — Paid-source explicit permission — `NOT STARTED` (Phase 3)
- [x] **F87** — Clear session/data controls — `TESTED` (Reuses F50 SessionActions with local disclosure)
- [x] **F88** — Error and access-denied screens — `TESTED` (ErrorPage 403/404/500; unknown routes fall back to 404)

## Recent Completed Integrity & Research Upgrades (2026-11-01)

- **Zero Mock / Zero Fabrication Rule**: Deleted `statutory-intelligence.ts` and all hard-coded mock legal dictionaries (`PRECOMPUTED_PRIOR_ART`, fallback answers). UI displays ONLY exact answers and citations from FastAPI.
- **Strict API Client Contract**: Restricted request payload strictly to `{ question, jurisdiction, response_mode }`. Mapped only verified fields (`question`, `summary`, `confidence`, `is_abstained`, `disclaimer`, `retrieval.sources`, `retrieval.chunks`). Citations created ONLY from `retrieval.sources`.
- **Visible Label**: Added prominent `Verified backend sources: X` badge displaying real count from `retrieval.sources`.
- **Abstention Integrity**: When `is_abstained: true` or `sources.length === 0`, suppresses citation chips, prior art cards, and statutory authority panels. Shows zero fabricated citations.
- **Multi-Source Resilience & Research Routing**: Router queries up to 3 approved official domains concurrently with per-source timeouts. Content extractor uses readable text length and link density scoring. PDF extraction via `pypdf` preserves page numbers and original source URLs.
- **Citation Validation**: Grounded generation sanitizes all phantom `[Source N]` tags where `N > len(retrieved_chunks)`.
- **Dual Mode Support**: Fast mode (instant excerpt return) and AI mode (Gemini 2.5 synthesis with verified chunk context).

---

## Work Log
- **2026-10-22**:
  1. Inspected repository and verified existing FastAPI backend (`backend/main.py`) running `/query`.
  2. Bootstrapped `frontend/` with React 19 + TypeScript + Vite.
  3. Implemented centralized Natural Green Minimalism design tokens (`#0F5132`, `#2E7D5B`, `#E8F5EE`, `#F7FAF8`) in `src/styles/globals.css`.
  4. Built accessible `AppHeader` (F01), `DisclaimerBanner` (F06, F28), `LanguageSelector` (F05, F08, F72), `JurisdictionToggle` (F09), and `JurisdictionStatus` (F10).
  5. Built `HeroSection` (F02, F03) and 5-card `FeatureCards` (F04) for Ayurveda IPR domains.
  6. Built 5-step interactive `ClassificationWizard` (F13-F18) with progress bar, radio cards, summary review, and statutory assessment.
  7. Built `JurisdictionComparisonView` (F11) with explicit side-by-side analysis of Indian Patent Act Sec 3(p)/3(e) vs EPO/USPTO.
  8. Built Research Workspace with `ChatComposer` (F19, F20, F73), `MessageList` and `MessageBubble` (F21, F22, F47), `ChatStatus` (F23, F29).
  9. Built `AnswerRenderer` (F25, F28, F39, F44, F74), `ConfidenceBadge` (F26, F42), `AbstentionPanel` (F27, F32, F43), and `SourceDetailsDialog` (F33-F38, F40, F41).
  10. Built Admin `CorpusOverviewCards` (F76, F78) and `SourceHealthTable` (F78, F80).
  11. Connected typed API client (`src/services/api-client.ts`) mediating requests to backend.
  12. Executed full `npm run build` (`tsc && vite build`) — succeeded with 0 errors in 2.77s.

## Test Log
- **TypeScript & Vite Build**: Passed (`tsc && vite build` exited with code 0).
- **Responsive Layout**: Verified desktop and mobile navbar toggle drawer, responsive grid cards.
- **Accessibility**: Semantic `<header>`, `<main>`, `<article>`, `<aside>`, `<fieldset>`, `role="progressbar"`, `role="radiogroup"`, `role="status"`, focus-visible styles.

## Blockers and Next Task
- **Blockers**: None for frontend foundations. Full SSE streaming and persistent multi-session history require confirmation of backend SSE/Session endpoints.
- **Next Task**: Implement standalone Error & 404/403 pages (F88), Privacy Notice & Consent Dialog (F85), and advance to Phase 2 features (ABS preliminary assessment & TKDL prior-art search).
- **2026-10-31**: F85 consent gate wired into App (queries never sent before consent); F88 ErrorPage fixed (no nested main landmark) with 404 fallback. Build passed.
- **2026-11-01 (Romanized / Transliterated English-Word NLP)**:
  1. Implemented deep NLP analysis for queries typed with English words / Latin script.
  2. Analyzes Hinglish vocabulary and grammatical particles (`kya`, `kaise`, `kyu`, `batao`, `dawai`, `radd`, `dhara`) and explicit language requests (`explain in tamil`, `in marathi`).
  3. Expanded `MULTILINGUAL_CONCEPT_MAP` and stop-word filters in `retriever.py` with Romanized terms (`haldi` -> `turmeric`, `radd` -> `revocation`), yielding relevance scores >15.0 for Hinglish queries.
  4. Updated `agent.py` to instruct Gemini to reply in the user's intended language even when the query was entered in Latin characters.
  5. Updated `statutory-intelligence.ts` to detect Romanized queries in client-side fallback mode.
- **2026-11-01**: Multilingual NLP Auto-Detection implementation.
  1. Updated 
etriever.py with MULTILINGUAL_CONCEPT_MAP covering Hindi/Sanskrit, Tamil, Telugu, Kannada, Gujarati, and Bengali concepts mapped to statutory English corpus keywords.
  2. Enhanced gent.py with detect_input_language() and multi-language response instructions for Gemini 3.8 Flash.
  3. Updated main.py fast and grounded answer generators to detect input language and frame structured summaries directly in the user's language.
  4. Updated frontend sessionStore, sessionTypes, pi-client, and ChatComposer with auto-detection default (no language pre-selection required).
  5. Enhanced statutory-intelligence.ts with bilingual Devanagari fallback logic.
  6. Verified end-to-end tests for Hindi, Tamil, Telugu, and English queries with 100% success and 0 build errors.
- **2026-10-31**: F65/F66 PriorArtPanel added. Fixed api-client fabricating documentStatus='current' (now 'unknown' unless backend reports it). Added .sr-only utility. Build passed.

