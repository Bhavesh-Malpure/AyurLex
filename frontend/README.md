# Ayurlex — Frontend Application

AI-Powered Ayurveda IPR, Patentability & Regulatory Compliance Research Platform.

## Technology Stack
- **Framework**: React 19 + TypeScript + Vite
- **Icons**: Lucide React
- **Design System**: Natural Green Minimalism (`#0F5132`, `#2E7D5B`, `#E8F5EE`, `#F7FAF8`)
- **API Protocol**: Typed REST & SSE client (`src/services/api-client.ts`)

## Project Scripts
```bash
# Install dependencies
npm install

# Start Vite local development server (port 5173)
npm run dev

# Full TypeScript check and production build
npm run build

# Preview production build
npm run preview
```

## Application Routes & Workspaces
- `/` (`landing`): Hero section, domain capabilities (Patents, Trademarks, GI, Regulatory Compliance, Traditional Knowledge).
- `/research`: Interactive research workspace, live message stream, statutory citations, confidence metrics, and abstention handling.
- `/classification`: 5-step Formulation Classification Wizard evaluating Schedule 1 text inclusion, novel extracts, Section 3(p) bars, and Rule 158B proof requirements.
- `/compliance`: Biological Diversity (ABS) Form III requirements & TKDL prior-art scrutiny overview.
- `/admin`: Corpus freshness, statutory source health, and indexed chunk statistics.

## Mandatory Rules & Disclaimers
1. **Legal Disclaimer**: Always visible in the top shell banner and appended to every substantive answer:
   > *"Ayurlex provides information for research purposes and does not provide legal advice."*
2. **Strict Verification**: No fabricated citations, URLs, confidence scores, or fake legal clearances are ever generated on the client.
