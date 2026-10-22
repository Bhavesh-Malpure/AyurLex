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
