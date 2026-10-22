# Ayurlex Engineering & Agent Working Rules

## 1. Scope & System Architecture
- **Frontend Scope**: Pure React 19 + TypeScript + Vite. Accessible semantic HTML, responsive design, keyboard navigation, clean error handling.
- **Backend Separation**: Frontend never calls databases, vector stores, or secret-bearing external services directly. All communication is mediated through typed API client modules (`src/services/api-client.ts`, feature api files).
- **Backend Statuses**: Contracts are `PROPOSED` until the backend developer confirms them. Never claim an endpoint is functional if it is only a proposed schema or mock.

## 2. Design System: Natural Green Minimalism
- **Primary Green**: `#0F5132` (Primary actions, active states)
- **Secondary Green**: `#2E7D5B` (Hover states, interactive accents)
- **Soft Green**: `#E8F5EE` (Highlighted panels, subtle backgrounds)
- **Page Background**: `#F7FAF8`
- **Surface**: `#FFFFFF`
- **Primary Text**: `#1F2937`
- **Secondary Text**: `#6B7280`
- **Border**: `#E5E7EB`
- **Input Focus**: `#2E7D5B`
- No heavy shadows, decorative gradients, or unapproved colors. Consistent spacing (4/8/12/16/24/32/48px).

## 3. Strict Truthfulness Constraints
- **Never fabricate**: Legal citations, document URLs, patent numbers, TKDL references, confidence scores, effective dates, or fake success notifications.
- **Mandatory Disclaimer**: `"Ayurlex provides information for research purposes and does not provide legal advice."` must always be visible in the application shell and attached to every substantive answer.
- **Abstention**: If evidence is insufficient, show an explicit abstention / insufficient-evidence state with suggestions to refine or consult an expert.

## 4. Execution Discipline
- Work incrementally in small dependency-ordered tasks.
- After every task, run validation checks (`npm run build`, `tsc`, etc.).
- Update `FRONTEND_PROGRESS.md` and `BACKEND_HANDOFF.md` on every completed item.
