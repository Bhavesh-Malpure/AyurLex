import React, { useState } from 'react';
import { AppHeader } from '../components/layout/AppHeader';
import { DisclaimerBanner } from '../components/legal/DisclaimerBanner';
import { HeroSection } from '../features/landing/components/HeroSection';
import { FeatureCards } from '../features/landing/components/FeatureCards';
import { ClassificationWizard } from '../features/classification/components/ClassificationWizard';
import { JurisdictionComparisonView } from '../features/jurisdiction/components/JurisdictionComparisonView';
import { MessageList } from '../features/chat/components/MessageList';
import { ChatComposer } from '../features/chat/components/ChatComposer';
import { ChatStatus } from '../features/chat/components/ChatStatus';
import { HistoryToolbar } from '../features/history/components/HistoryToolbar';
import { SourceDetailsDialog } from '../features/sources/components/SourceDetailsDialog';
import { CorpusOverviewCards } from '../features/admin/components/CorpusOverviewCards';
import { SourceHealthTable } from '../features/admin/components/SourceHealthTable';
import { ComplianceOverview } from '../features/compliance/ComplianceOverview';
import { useChatSession } from '../features/chat/useChatSession';
import { useSession } from '../features/session/sessionStore';

export const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<string>('landing');
  const [isComparisonOpen, setIsComparisonOpen] = useState(false);

  const {
    messages,
    stage,
    errorMessage,
    selectedCitation,
    isCitationDialogOpen,
    sendMessage,
    openCitation,
    closeCitation,
    clearMessages,
  } = useChatSession();

  const { sessionId } = useSession();

  const handleStartResearch = (initialQuery?: string) => {
    setCurrentRoute('research');
    if (initialQuery) {
      sendMessage(initialQuery);
    }
  };

  const handleOpenClassifier = () => {
    setCurrentRoute('classification');
  };

  const handleToggleComparison = () => {
    setIsComparisonOpen((prev) => !prev);
  };

  return (
    <div className="app-shell">
      {/* Persistent App Shell Legal Disclaimer (F06) */}
      <DisclaimerBanner variant="global" />

      {/* App Header & Navigation (F01, F05, F09) */}
      <AppHeader currentRoute={currentRoute} onNavigate={(route) => setCurrentRoute(route)} />

      {/* Main Content Landmark */}
      <main className="main-content" id="main-content" tabIndex={-1}>
        {/* Route: Landing Page */}
        {currentRoute === 'landing' && (
          <div>
            <HeroSection
              onStartResearch={() => handleStartResearch()}
              onOpenClassifier={handleOpenClassifier}
            />
            <FeatureCards onSelectFeature={(route) => setCurrentRoute(route)} />
          </div>
        )}

        {/* Route: Research Workspace (F19-F24, F25-F32, F33-F44, F45-F50) */}
        {currentRoute === 'research' && (
          <div className="container-wide" style={{ padding: 'var(--space-6) var(--space-4)', width: '100%' }}>
            {/* Toolbar for session controls & comparison */}
            <HistoryToolbar
              onNewSession={clearMessages}
              onToggleComparison={handleToggleComparison}
              isComparisonActive={isComparisonOpen}
            />

            {/* Jurisdiction Comparison View (F11) if toggled */}
            {isComparisonOpen ? (
              <JurisdictionComparisonView
                onClose={() => setIsComparisonOpen(false)}
                onExploreTopic={(topic) => {
                  setIsComparisonOpen(false);
                  sendMessage(`Explain the statutory differences between India and International law for: ${topic}`);
                }}
              />
            ) : (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-4)',
                  maxWidth: '920px',
                  margin: '0 auto',
                  minHeight: '65vh',
                }}
              >
                {/* Message Stream & History */}
                <div style={{ flex: 1 }}>
                  <MessageList
                    messages={messages}
                    onCitationClick={openCitation}
                    onSuggestedQueryClick={(q) => sendMessage(q)}
                    onRefineQuestion={() => {
                      const input = document.getElementById('research-query-input') as HTMLTextAreaElement;
                      input?.focus();
                    }}
                  />
                </div>

                {/* Status Indicator */}
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <ChatStatus stage={stage} errorMessage={errorMessage} />
                </div>

                {/* Composer */}
                <div style={{ position: 'sticky', bottom: 'var(--space-4)', zIndex: 30 }}>
                  <ChatComposer
                    onSendMessage={sendMessage}
                    isLoading={stage !== 'idle' && stage !== 'error'}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Route: Formulation Classifier (F13-F18) */}
        {currentRoute === 'classification' && (
          <ClassificationWizard
            onNavigateToResearch={(category) => {
              handleStartResearch(`What are the specific Rule 158B licensing requirements and Section 3(p) implications for "${category}"?`);
            }}
          />
        )}

        {/* Route: Compliance (ABS & TKDL Overview) */}
        {currentRoute === 'compliance' && (
          <ComplianceOverview onStartResearch={(query) => handleStartResearch(query)} />
        )}

        {/* Route: Admin & Corpus Overview (F76-F82) */}
        {currentRoute === 'admin' && (
          <div className="container-wide" style={{ padding: 'var(--space-8) var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            <CorpusOverviewCards />
            <SourceHealthTable />
          </div>
        )}
      </main>

      {/* Accessible Citation Source Details Dialog (F41) */}
      <SourceDetailsDialog
        citation={selectedCitation}
        isOpen={isCitationDialogOpen}
        onClose={closeCitation}
      />

      {/* Footer */}
      <footer
        role="contentinfo"
        style={{
          borderTop: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          padding: 'var(--space-6) 0',
          fontSize: '0.8125rem',
          color: 'var(--color-text-secondary)',
          marginTop: 'auto',
        }}
      >
        <div
          className="container-wide"
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-4)',
          }}
        >
          <div>
            <strong>Ayurlex</strong> · AI-Powered Ayurveda IPR & Regulatory Intelligence
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
              Active Session ID: <code style={{ fontSize: '0.7rem' }}>{sessionId}</code>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
            <button
              type="button"
              onClick={() => setCurrentRoute('compliance')}
              className="btn-ghost"
              style={{ fontSize: '0.8rem', padding: 0 }}
            >
              ABS & TKDL Mandates
            </button>
            <button
              type="button"
              onClick={() => setCurrentRoute('admin')}
              className="btn-ghost"
              style={{ fontSize: '0.8rem', padding: 0 }}
            >
              Corpus Health
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
