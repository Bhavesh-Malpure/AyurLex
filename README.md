<div align="center">

# 🌿 Ayurlex

### *AI-Powered Ayurveda Intellectual Property & Regulatory Research Intelligence*

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-0F5132.svg?style=for-the-badge)](#)
[![React 19](https://img.shields.io/badge/React-19.0-2E7D5B.svg?style=for-the-badge&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2-646CFF.svg?style=for-the-badge&logo=vite)](https://vitejs.dev/)
[![DPDP Act Compliant](https://img.shields.io/badge/DPDP-Compliant-0F5132.svg?style=for-the-badge)](#)

<p align="center">
  <strong>Grounded, non-hallucinated statutory research bridging AYUSH practitioners, biotechnology startups, and global IP frameworks across Patents, Trademarks, Geographical Indications (GI), Traditional Knowledge (TKDL), and Access & Benefit Sharing (ABS).</strong>
</p>

[Explore Workspace](#-key-capabilities) • [System Architecture](#-high-level-architecture) • [Getting Started](#-getting-started) • [Decision Matrix](#-formulation-classification-matrix) • [Roadmap](#-staged-roadmap)

---

</div>

## 📖 Vision & Core Tenets

Ayurlex solves the complex overlap between **Ayurvedic statutory compliance** (Drugs and Cosmetics Act, 1940; Biological Diversity Act, 2002) and **intellectual property protection** (Indian Patents Act, 1970; WIPO treaties; EPO guidelines). 

Traditional research often leads to erroneous filings, severe Section 3(p) rejections, or inadvertent bio-piracy. Ayurlex provides source-grounded, non-hallucinated research intelligence with statutory auditability.

### 🛡️ Non-Negotiable Tenets

| Tenet | Statutory Enforcement |
|:---|:---|
| **Traceable Citations** | Every substantive legal claim must be anchored to a specific chunk locator (Act, Chapter, Section, Rule, or Gazette notification). Uncited claims are rejected. |
| **Strict Jurisdiction Isolation** | India (Domestic ASU statutes & TKDL) and International (WIPO, EPO, USPTO) citations are never blended into unstructured prose. Comparisons are strictly side-by-side. |
| **Confidence & Abstention** | If primary legal evidence is insufficient or contradictory, the agent abstains explicitly rather than guessing or interpolating. |
| **Mandatory Legal Disclaimer** | Every substantive response and app shell persistently displays: *"Ayurlex provides information for research purposes and does not provide legal advice."* |
| **DPDP Compliance** | Explicit user consent for paid-source integrations, strict data minimization, and audit logging with India-region data residency. |

---

## 🏛️ High-Level Architecture

The platform operates across five coordinated layers: an accessible user interface, an intelligent orchestration layer, three parallel domain reasoning engines, a curated statutory corpus, and a comprehensive guardrail wrapper.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                           │
│     Web & Mobile UI (React 19)  •  Natural Green Minimalism  •  i18n    │
│                  Voice & Bhashini Multilingual (Phase 4)                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                           ORCHESTRATION LAYER                           │
│   Intent Router  ──►  Formulation Classifier  ──►  Jurisdiction Router  │
│                   Agent Planner (Multi-Step Reasoning)                  │
└──────────────┬─────────────────────┬─────────────────────┬──────────────┘
               │                     │                     │
┌──────────────▼──────┐   ┌──────────▼──────────┐   ┌──────▼──────────────┐
│      RAG CORE       │   │  ABS / TKDL HELPER  │   │   KNOWLEDGE GRAPH   │
│  Hybrid Dense +     │   │  BDA 2023 / Rules   │   │  Ingredients ↔ Texts│
│  BM25 Sparse +      │   │  NBA Form I/III     │   │  Patents ↔ Statutes │
│  Citation Verifier  │   │  TKDL Prior-Art Map │   │  Multi-Hop Reasoning│
└──────────────┬──────┘   └──────────┬──────────┘   └──────┬──────────────┘
               │                     │                     │
┌──────────────▼─────────────────────▼─────────────────────▼──────────────┐
│                    CURATED, VERSION-TRACKED CORPUS                      │
│   First Schedule Texts  •  API & AFI Pharmacopoeias  •  Gazettes        │
│   Indian Patent Act  •  Drugs & Cosmetics Act  •  WIPO / EPO Treaties   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                           GUARDRAILS & AUDIT                            │
│   Disclaimer Injection  •  Confidence Scorer  •  Abstention Engine     │
│   Human IP Facilitator Escalation  •  DPDP Consent & Audit Logging      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Capabilities

### 1. 🔍 Interactive Research Workspace
- **Multi-Phase Status Animations**: Real-time feedback showing retrieval steps (*Searching ASU pharmacopoeias* ➔ *Analyzing Section 3(p) prior art* ➔ *Verifying Gazette notifications*).
- **Statutory Citation Chips**: Interactive chips displaying document ID, title, section/rule locator, publication dates, and verified source links with modal drill-down.
- **Confidence Badges**: Clear badges distinguishing *Statutorily Verified* provisions, *Secondary Commentaries*, and *Preliminary Inferences*.
- **Explicit Abstention View**: Renders actionable guidance, query refinement advice, and human expert escalation when evidence is inconclusive.

### 2. 🌿 5-Step Formulation Classification Wizard
A guided statutory decision tree that evaluates:
1. **First Schedule Inclusion**: Verification against the 54 classical authoritative texts of the Drugs & Cosmetics Act, 1940.
2. **Botanical Origin**: Compliance with Ayurvedic Pharmacopoeia of India (API) monographs.
3. **Extraction & Processing**: Classical aqueous kwatha processing vs. modern hydro-alcoholic or supercritical fluid fractions.
4. **Therapeutic Claims**: Traditional textual indications (Rogadhikara) vs. modern disease claims.
5. **Heavy Metal Bhasmas**: Rasashastra mineral compliance and Schedule E(1) safety thresholds.

### 3. ⚖️ Comparative Jurisdiction Engine
- **Explicit Side-by-Side Analysis**: Compares Indian domestic provisions with international IP norms:
  - **Indian Patents Act Section 3(p)** vs. **EPO Article 54/56 & USPTO 35 U.S.C. 102/103**
  - **Section 3(e) Synergistic Admixtures** vs. **PCT Unexpected Results standard**
  - **Biological Diversity Act (BDA) Section 6 approval** vs. **Nagoya Protocol IRCC requirements**

### 4. 🛡️ ABS & TKDL Compliance
- **Biological Diversity Act (2023 Amendment) & 2024 Rules**: Automated tracking of National Biodiversity Authority (NBA) **Form I** (commercial access) and **Form III** (IPR prior approval).
- **TKDL Prior-Art Guidance**: Scrutiny of classical recipes to evaluate Section 3(p) anticipation hurdles.

### 5. 📊 Corpus Health & Administrative Monitoring
- Live tracking of indexed statutory documents, pharmacopoeial volumes, Gazette sync dates, and version lineage (active vs. superseded statutes).

---

## 🎯 Formulation Classification Matrix

Ayurlex uses a first-gate classification tree to assign formulations to specific statutory buckets, conditioning all downstream retrieval:

| Formulation Bucket | Key Identifying Criteria | IP & Regulatory Pathway |
|:---|:---|:---|
| **Classical / Generic ASU** | Exact recipe in First Schedule texts (Charaka, Sushruta, AFI) | Section 3(p) patent bar; defend via TKDL; Rule 158B(I) clinical trial exemption. |
| **Ayurvedic Proprietary Medicine** | Modified classical base or novel ratio under own brand name | Trademark + Rule 158B(IV) safety study; limited patent scope under Section 3(e). |
| **New ASU Phytopharmaceutical** | Standardized fraction/extract with proven bioactive marker | CDSCO phytopharmaceutical pathway; patentable formulation dossier. |
| **Ayurveda-Aahar / Nutraceutical** | Food/beverage with health claims derived from ASU botanicals | FSSAI regime (not drug IP); labeling and safety compliance. |
| **Cosmetic Formulation** | Topical application for cleansing, beautifying, or grooming | Cosmetic Rules compliance; trademark & industrial design protection. |

---

## 🎨 Design System: Natural Green Minimalism

Ayurlex uses an intentional, accessible design system tailored for legal professionals, researchers, and startups:

```css
:root {
  --color-primary: #0F5132;        /* Primary green: major actions & brand header */
  --color-secondary: #2E7D5B;      /* Secondary green: interactive accents & hovers */
  --color-soft-green: #E8F5EE;     /* Highlighted panels & subtle backgrounds */
  --color-background: #F7FAF8;     /* Neutral, calming application backdrop */
  --color-surface: #FFFFFF;        /* Clean white surface cards & dialogs */
  --color-text-primary: #1F2937;   /* High-contrast readable typography */
  --color-text-secondary: #6B7280; /* Metadata, citations & helper text */
  --color-border: #E5E7EB;         /* Subtle structural borders (no heavy shadows) */
  --color-focus: #2E7D5B;          /* Accessible keyboard focus rings */
}
```

---

## 💻 Tech Stack

| Domain | Technology / Library | Role in Ayurlex |
|:---|:---|:---|
| **Frontend** | React 19, TypeScript, Vite | Fast, accessible, typed client application |
| **Icons & Styling** | Lucide React, Design-Token CSS | Restrained botanical iconography & responsive layout |
| **Backend API** | FastAPI (Python 3.11+), Pydantic v2 | High-throughput asynchronous REST & SSE streaming |
| **Orchestration** | LangGraph / Custom Agent Planner | Multi-step query decomposition & intent routing |
| **Vector Database** | Qdrant / Weaviate / pgvector | Hybrid dense embeddings (BGE-M3 / Voyage) |
| **Sparse Retrieval** | Elasticsearch / OpenSearch (BM25) | Exact statutory phrase & section matching |
| **Knowledge Graph** | Neo4j (Phase 2) | Multi-hop relationships: Ingredients ↔ Formulations ↔ Patents |
| **Multilingual** | Bhashini APIs (Phase 4) | ASR, TTS, and English/Hindi boundary translation |
| **Compliance** | DPDP-Compliant Cloud (India) | Data residency, consent logging, and audit tracking |

---

## 📂 Repository Structure

```
AyurLex/
├── AGENTS.md                          # Engineering rules & design directives
├── FRONTEND_PROGRESS.md               # Live 88-feature progress tracker (58% completed)
├── BACKEND_HANDOFF.md                 # API contracts & schema specifications
├── Ayurlex_Blueprint-3.pdf            # Master architecture & evaluation blueprint
│
├── frontend/                          # React 19 + TypeScript + Vite Application
│   ├── src/
│   │   ├── app/                       # Application shell & router
│   │   ├── components/                # Layout, Header, Disclaimer, Language selector
│   │   ├── features/
│   │   │   ├── landing/               # Hero section & domain capability cards
│   │   │   ├── chat/                  # Composer, MessageList, Status, useChatSession
│   │   │   ├── answers/               # AnswerRenderer, CitationChip, ConfidenceBadge
│   │   │   ├── classification/        # 5-step Formulation Classification Wizard
│   │   │   ├── jurisdiction/          # India/Intl toggle & side-by-side comparison
│   │   │   ├── sources/               # SourceDetailsPanel & accessible dialog modal
│   │   │   ├── compliance/            # Biological Diversity (ABS) & TKDL guidance
│   │   │   ├── admin/                 # CorpusOverviewCards & SourceHealthTable
│   │   │   └── session/               # Reactive store & session type definitions
│   │   ├── services/                  # Typed api-client.ts mediating backend requests
│   │   ├── styles/                    # globals.css (Natural Green design tokens)
│   │   └── main.tsx                   # React root entry
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                           # FastAPI Backend Service
│   ├── main.py                        # API routes, CORS & research query endpoint
│   └── __pycache__/
│
└── ai/                                # AI Modules & Retrieval Orchestration
    ├── ipr_classifier/                # IPR classification engine
    ├── jurisdiction_manager/          # India vs International jurisdiction detector
    ├── language_detector/             # Language detection module
    ├── orchestrator/                  # Multi-step research planner agent
    ├── query_analyzer/                # Ayurvedic intent analyzer
    └── retriever/                     # Statutory source retrieval engine
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: `v20.0.0` or higher (recommended: `v24.15.0`)
- **Python**: `v3.11` or higher
- **Package Managers**: `npm` and `pip`

### 1. Frontend Setup & Launch
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server (port 5173)
npm run dev

# Run TypeScript checks and build production bundle
npm run build
```
Once started, navigate to `http://localhost:5173` in your browser.

### 2. Backend Setup & Launch
```bash
# In a separate terminal, install backend requirements
cd backend
pip install fastapi uvicorn pydantic

# Start the FastAPI server (port 8000)
uvicorn main:app --reload --port 8000
```
Backend API health check is available at `http://localhost:8000/health`.

---

## 🗺️ Staged Roadmap

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ [x] MVP (Current Phase)                                                │
  │     • Natural Green Minimalism design system & responsive shell        │
  │     • Persistent legal disclaimer banner (global + per substantive ans)│
  │     • 5-step Formulation Classification Wizard                         │
  │     • Side-by-side jurisdiction comparison (India vs. International)   │
  │     • Statutory citation chips & accessible source details modal       │
  │     • Confidence badges & explicit insufficient-evidence abstention    │
  │     • Admin corpus freshness and source health overview               │
  ├────────────────────────────────────────────────────────────────────────┤
  │ [ ] Phase 2: Agentic Orchestration & Knowledge Graph                   │
  │     • Neo4j Knowledge Graph connecting ingredients, formulations, laws │
  │     • Automated NBA Form III & ABS check wizard                        │
  │     • Authorized TKDL prior-art classification code search             │
  │     • Human IP Facilitator handoff with conversation preview           │
  ├────────────────────────────────────────────────────────────────────────┤
  │ [ ] Phase 3: Paid-Source Connectors                                    │
  │     • Commercial patent database connectors with explicit user consent│
  │     • DPDP consent audit log & billing thresholds                      │
  ├────────────────────────────────────────────────────────────────────────┤
  │ [ ] Phase 4: Multilingual Voice & Case Law                             │
  │     • Bhashini ASR/TTS voice input and speech synthesis                │
  │     • High Court & Supreme Court ASU trademark/patent case law index   │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ Statutory Disclaimer

> **IMPORTANT NOTICE**: Ayurlex provides information strictly for research and educational purposes and does not provide legal advice. Intellectual property filings, patent claims, and regulatory licensing under the Drugs and Cosmetics Act, 1940 or Biological Diversity Act, 2002 require validation with qualified patent attorneys, registered patent agents, or the relevant State Licensing Authority (SLA).

---

<div align="center">
  <p>Crafted with care for the Ayurvedic research & innovation ecosystem -- A project By Bhavesh Malpure and Team🌿</p>
</div>
