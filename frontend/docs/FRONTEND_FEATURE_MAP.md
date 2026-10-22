# Ayurlex Frontend Feature-to-File Map

This document synchronizes all 88 catalogued frontend requirements with their designated files, primary component responsibilities, and implementation phases.

| Feature ID | Feature Name | Primary Component / File | Phase | Status |
|---|---|---|---|---|
| F01 | Ayurlex logo and navigation bar | `src/components/layout/AppHeader.tsx` | MVP | In Progress |
| F02 | Hero section explaining the platform | `src/features/landing/components/HeroSection.tsx` | MVP | In Progress |
| F03 | Start Research button | `src/features/landing/components/HeroSection.tsx`, `src/app/router.tsx` | MVP | In Progress |
| F04 | Feature cards (patents, TM, GI, compliance, TK) | `src/features/landing/components/FeatureCards.tsx` | MVP | In Progress |
| F05 | Language selector | `src/components/language/LanguageSelector.tsx` | MVP | In Progress |
| F06 | Persistent legal disclaimer banner | `src/components/legal/DisclaimerBanner.tsx`, `src/app/App.tsx` | MVP | In Progress |
| F07 | Responsive desktop/mobile layouts | `src/styles/globals.css` | MVP | In Progress |
| F08 | Language selector (duplicate req) | `src/components/language/LanguageSelector.tsx` | MVP | In Progress |
| F09 | India / International toggle | `src/features/jurisdiction/components/JurisdictionToggle.tsx` | MVP | Not Started |
| F10 | Visible selected-jurisdiction indicator | `src/features/jurisdiction/components/JurisdictionStatus.tsx` | MVP | Not Started |
| F11 | Explicit comparison view | `src/features/jurisdiction/components/JurisdictionComparisonView.tsx` | MVP | Not Started |
| F12 | Session state for language and jurisdiction | `src/features/session/sessionStore.ts` | MVP | Not Started |
| F13 | One classification question at a time | `src/features/classification/components/ClassificationWizard.tsx` | MVP | Not Started |
| F14 | Multiple-choice classification options | `src/features/classification/components/ClassificationQuestion.tsx` | MVP | Not Started |
| F15 | Classification progress indicator | `src/features/classification/components/ClassificationProgress.tsx` | MVP | Not Started |
| F16 | Back and Continue buttons | `src/features/classification/components/ClassificationWizard.tsx` | MVP | Not Started |
| F17 | Classification answer summary | `src/features/classification/components/ClassificationSummary.tsx` | MVP | Not Started |
| F18 | Final formulation classification result | `src/features/classification/components/ClassificationResult.tsx` | MVP | Not Started |
| F19 | Research message input | `src/features/chat/components/ChatComposer.tsx` | MVP | Not Started |
| F20 | Send button | `src/features/chat/components/ChatComposer.tsx` | MVP | Not Started |
| F21 | User and AI message bubbles | `src/features/chat/components/MessageBubble.tsx`, `MessageList.tsx` | MVP | Not Started |
| F22 | Conversation history in active session | `src/features/chat/useChatSession.ts` | MVP | Not Started |
| F23 | Chat loading and error states | `src/features/chat/components/ChatStatus.tsx` | MVP | Not Started |
| F24 | Progressively streamed answers | `src/features/chat/useChatStream.ts` | MVP | Not Started |
| F25 | Citation chips attached to answers | `src/features/answers/components/CitationChip.tsx` | MVP | Not Started |
| F26 | Confidence indicator | `src/features/answers/components/ConfidenceBadge.tsx` | MVP | Not Started |
| F27 | Insufficient-evidence state | `src/features/answers/components/AbstentionPanel.tsx` | MVP | Not Started |
| F28 | Disclaimer on every substantive answer | `src/features/answers/components/AnswerRenderer.tsx` | MVP | Not Started |
| F29 | Research processing state | `src/features/chat/components/ChatStatus.tsx` | MVP | Not Started |
| F30 | Streaming response display | `src/features/chat/components/StreamingMessage.tsx` | MVP | Not Started |
| F31 | Helpful service-failure messages | `src/components/feedback/ErrorMessage.tsx` | MVP | Not Started |
| F32 | Clear insufficient-evidence messaging | `src/features/answers/components/AbstentionPanel.tsx` | MVP | Not Started |
| F33 | Document or legislation title | `src/features/sources/components/SourceDetailsPanel.tsx` | MVP | Not Started |
| F34 | Source jurisdiction | `src/features/sources/components/SourceDetailsPanel.tsx` | MVP | Not Started |
| F35 | Relevant section or rule | `src/features/sources/components/SourceDetailsPanel.tsx` | MVP | Not Started |
| F36 | Source URL | `src/features/sources/components/SourceDetailsPanel.tsx`, `sourceUrl.ts` | MVP | Not Started |
| F37 | Document date/amendment information | `src/features/sources/components/SourceDetailsPanel.tsx` | MVP | Not Started |
| F38 | Current/superseded status | `src/features/sources/components/SourceStatusBadge.tsx` | MVP | Not Started |
| F39 | Readable answer paragraphs and headings | `src/features/answers/components/AnswerRenderer.tsx` | MVP | Not Started |
| F40 | Clickable citation chips | `src/features/answers/components/CitationChip.tsx` | MVP | Not Started |
| F41 | Source details panel/modal | `src/features/sources/components/SourceDetailsDialog.tsx` | MVP | Not Started |
| F42 | Confidence indicators in answer view | `src/features/answers/components/ConfidenceBadge.tsx` | MVP | Not Started |
| F43 | Distinct insufficient-evidence answer layout | `src/features/answers/components/AbstentionPanel.tsx` | MVP | Not Started |
| F44 | Applicable/verification date | `src/features/answers/components/AnswerMeta.tsx` | MVP | Not Started |
| F45 | New Research button | `src/features/history/components/HistoryToolbar.tsx` | MVP | Not Started |
| F46 | Conversation list | `src/features/history/components/ConversationList.tsx` | MVP | Not Started |
| F47 | Message history | `src/features/history/components/ConversationHistory.tsx` | MVP | Not Started |
| F48 | Continue Research action | `src/features/history/components/ConversationListItem.tsx` | MVP | Not Started |
| F49 | Session title/summary | `src/features/history/components/ConversationListItem.tsx` | MVP | Not Started |
| F50 | Clear session controls | `src/features/history/components/SessionActions.tsx` | MVP | Not Started |
| F51 | Escalation button | `src/features/escalation/components/EscalationButton.tsx` | Phase 2 | Not Started |
| F52 | Escalation explanation | `src/features/escalation/components/EscalationIntro.tsx` | Phase 2 | Not Started |
| F53 | Consent/contact form | `src/features/escalation/components/EscalationForm.tsx` | Phase 2 | Not Started |
| F54 | Conversation summary preview | `src/features/escalation/components/EscalationSummaryPreview.tsx` | Phase 2 | Not Started |
| F55 | Escalation submission confirmation | `src/features/escalation/components/EscalationConfirmation.tsx` | Phase 2 | Not Started |
| F56 | Escalation status | `src/features/escalation/components/EscalationStatus.tsx` | Phase 2 | Not Started |
| F57 | Biological resource/ingredient input | `src/features/abs/components/AbsCheckForm.tsx` | Phase 2 | Not Started |
| F58 | ABS intended use | `src/features/abs/components/AbsCheckForm.tsx` | Phase 2 | Not Started |
| F59 | ABS research/commercial purpose | `src/features/abs/components/AbsCheckForm.tsx` | Phase 2 | Not Started |
| F60 | Other ABS facts required by rules | `src/features/abs/components/AbsCheckForm.tsx` | Phase 2 | Not Started |
| F61 | Formulation description for prior-art | `src/features/tkdl/components/TkdlSearchForm.tsx` | Phase 2 | Not Started |
| F62 | TKDL/prior-art search button | `src/features/tkdl/components/TkdlSearchForm.tsx` | Phase 2 | Not Started |
| F63 | Prior-art result cards | `src/features/tkdl/components/TkdlResultsList.tsx` | Phase 2 | Not Started |
| F64 | Classification codes/entries | `src/features/tkdl/components/TkdlResultCard.tsx` | Phase 2 | Not Started |
| F65 | Prior-art supporting source details | `src/features/tkdl/components/TkdlResultCard.tsx` | Phase 2 | Not Started |
| F66 | Prior-art limitation notice | `src/features/tkdl/components/TkdlLimitationsNotice.tsx` | Phase 2 | Not Started |
| F67 | Related-records panel | `src/features/knowledge-graph/components/RelatedRecordsPanel.tsx` | Phase 2 | Not Started |
| F68 | Links between ingredients, formulations, laws | `src/features/knowledge-graph/components/RelatedRecordItem.tsx` | Phase 2 | Not Started |
| F69 | Evidence trail for complex questions | `src/features/knowledge-graph/components/EvidenceTrail.tsx` | Phase 2 | Not Started |
| F70 | Expandable research explanation | `src/features/knowledge-graph/components/ResearchTraceDisclosure.tsx` | Phase 2 | Not Started |
| F71 | Translated interface labels | `src/i18n/config.ts` | MVP | Not Started |
| F72 | Language selection (duplicate req) | `src/components/language/LanguageSelector.tsx` | MVP | In Progress |
| F73 | Supported-language input handling | `src/features/chat/components/ChatComposer.tsx` | MVP | Not Started |
| F74 | Translated answer presentation | `src/features/answers/components/AnswerRenderer.tsx` | MVP | Not Started |
| F75 | Voice input/audio playback | `src/features/voice/VoiceControls.tsx` | Phase 4 | Not Started |
| F76 | Number of indexed documents | `src/features/admin/components/CorpusOverviewCards.tsx` | MVP | Not Started |
| F77 | Ingestion status | `src/features/admin/components/IngestionStatusTable.tsx` | MVP | Not Started |
| F78 | Last successful update | `src/features/admin/components/SourceHealthTable.tsx` | MVP | Not Started |
| F79 | Failed ingestion jobs | `src/features/admin/components/IngestionStatusTable.tsx` | MVP | Not Started |
| F80 | Source health | `src/features/admin/components/SourceHealthTable.tsx` | MVP | Not Started |
| F81 | Current and superseded doc versions | `src/features/admin/components/DocumentVersionsTable.tsx` | MVP | Not Started |
| F82 | Retrieval/citation statistics | `src/features/admin/components/QualityMetricsPanel.tsx` | MVP | Not Started |
| F83 | Registration/login if required | `src/features/auth/pages/LoginPage.tsx` | Decision Needed | Not Started |
| F84 | Session handling | `src/features/session/sessionStore.ts` | MVP | Not Started |
| F85 | Privacy and consent interfaces | `src/features/privacy/components/PrivacyNotice.tsx` | MVP | Not Started |
| F86 | Paid-source explicit permission | `src/features/privacy/components/PaidSourceConsentDialog.tsx` | Phase 3 | Not Started |
| F87 | Clear session/data controls | `src/features/privacy/components/DataControls.tsx` | MVP | Not Started |
| F88 | Error and access-denied screens | `src/pages/NotFoundPage.tsx`, `ForbiddenPage.tsx` | MVP | Not Started |
