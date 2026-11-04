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

import { LoginPage } from '../features/auth/pages/LoginPage';
import { RegisterPage } from '../features/auth/pages/RegisterPage';

import '../features/auth/auth.css';

export const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<string>('landing');
  const [isComparisonOpen, setIsComparisonOpen] = useState(false);

  // Check whether the current page is an authentication page
  const isAuthRoute =
    currentRoute === 'login' || currentRoute === 'register';

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

  // Start research workspace
  const handleStartResearch = (initialQuery?: string) => {
    setCurrentRoute('research');

    if (initialQuery) {
      sendMessage(initialQuery);
    }
  };

  // Open formulation classifier
  const handleOpenClassifier = () => {
    setCurrentRoute('classification');
  };

  // Toggle jurisdiction comparison
  const handleToggleComparison = () => {
    setIsComparisonOpen((prev) => !prev);
  };

  return (
    <div className="app-shell">

      {/* ======================================
          GLOBAL HEADER AND NAVIGATION
      ====================================== */}

      {!isAuthRoute && (
        <>
          {/* Persistent Legal Disclaimer */}
          <DisclaimerBanner variant="global" />

          {/* Main Application Header */}
          <AppHeader
            currentRoute={currentRoute}
            onNavigate={(route) => setCurrentRoute(route)}
          />

          {/* Authentication Navigation */}
          <div className="auth-navigation">

            <button
              type="button"
              className="auth-nav-login"
              onClick={() => setCurrentRoute('login')}
            >
              Login
            </button>

            <button
              type="button"
              className="auth-nav-register"
              onClick={() => setCurrentRoute('register')}
            >
              Create account
            </button>

          </div>
        </>
      )}

      {/* ======================================
          MAIN CONTENT
      ====================================== */}

      <main
        className="main-content"
        id="main-content"
        tabIndex={-1}
      >

        {/* LOGIN PAGE */}
        {currentRoute === 'login' && (
          <LoginPage
            onNavigate={setCurrentRoute}
          />
        )}

        {/* REGISTER PAGE */}
        {currentRoute === 'register' && (
          <RegisterPage
            onNavigate={setCurrentRoute}
          />
        )}

        {/* LANDING PAGE */}
        {currentRoute === 'landing' && (
          <div>

            <HeroSection
              onStartResearch={() => handleStartResearch()}
              onOpenClassifier={handleOpenClassifier}
            />

            <FeatureCards
              onSelectFeature={(route) => setCurrentRoute(route)}
            />

          </div>
        )}

        {/* ======================================
            RESEARCH WORKSPACE
        ====================================== */}

        {currentRoute === 'research' && (
          <div
            className="container-wide"
            style={{
              padding: 'var(--space-6) var(--space-4)',
              width: '100%',
            }}
          >

            {/* Session Toolbar */}
            <HistoryToolbar
              onNewSession={clearMessages}
              onToggleComparison={handleToggleComparison}
              isComparisonActive={isComparisonOpen}
            />

            {/* Jurisdiction Comparison */}
            {isComparisonOpen ? (

              <JurisdictionComparisonView
                onClose={() => setIsComparisonOpen(false)}
                onExploreTopic={(topic) => {
                  setIsComparisonOpen(false);

                  sendMessage(
                    `Explain the statutory differences between India and International law for: ${topic}`
                  );
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

                {/* Message Stream */}
                <div style={{ flex: 1 }}>
                  <MessageList
                    messages={messages}
                    onCitationClick={openCitation}
                    onSuggestedQueryClick={(q) => sendMessage(q)}
                    onRefineQuestion={() => {
                      const input = document.getElementById(
                        'research-query-input'
                      ) as HTMLTextAreaElement;

                      input?.focus();
                    }}
                  />
                </div>

                {/* Chat Status */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  <ChatStatus
                    stage={stage}
                    errorMessage={errorMessage}
                  />
                </div>

                {/* Chat Composer */}
                <div
                  style={{
                    position: 'sticky',
                    bottom: 'var(--space-4)',
                    zIndex: 30,
                  }}
                >
                  <ChatComposer
                    onSendMessage={sendMessage}
                    isLoading={
                      stage !== 'idle' && stage !== 'error'
                    }
                  />
                </div>

              </div>
            )}

          </div>
        )}

        {/* ======================================
            FORMULATION CLASSIFIER
        ====================================== */}

        {currentRoute === 'classification' && (
          <ClassificationWizard
            onNavigateToResearch={(category) => {
              handleStartResearch(
                `What are the specific Rule 158B licensing requirements and Section 3(p) implications for "${category}"?`
              );
            }}
          />
        )}

        {/* ======================================
            COMPLIANCE OVERVIEW
        ====================================== */}

        {currentRoute === 'compliance' && (
          <ComplianceOverview
            onStartResearch={(query) => handleStartResearch(query)}
          />
        )}

        {/* ======================================
            ADMIN AND CORPUS OVERVIEW
        ====================================== */}

        {currentRoute === 'admin' && (
          <div
            className="container-wide"
            style={{
              padding: 'var(--space-8) var(--space-4)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)',
            }}
          >

            <CorpusOverviewCards />

            <SourceHealthTable />

          </div>
        )}

      </main>

      {/* ======================================
          CITATION SOURCE DETAILS
      ====================================== */}

      {!isAuthRoute && (
        <SourceDetailsDialog
          citation={selectedCitation}
          isOpen={isCitationDialogOpen}
          onClose={closeCitation}
        />
      )}

      {/* ======================================
          FOOTER
      ====================================== */}

      {!isAuthRoute && (
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

              <div
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--color-text-tertiary)',
                }}
              >
                Active Session ID:{' '}
                <code style={{ fontSize: '0.7rem' }}>
                  {sessionId}
                </code>
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                gap: 'var(--space-4)',
              }}
            >

              <button
                type="button"
                onClick={() => setCurrentRoute('compliance')}
                className="btn-ghost"
                style={{
                  fontSize: '0.8rem',
                  padding: 0,
                }}
              >
                ABS & TKDL Mandates
              </button>

              <button
                type="button"
                onClick={() => setCurrentRoute('admin')}
                className="btn-ghost"
                style={{
                  fontSize: '0.8rem',
                  padding: 0,
                }}
              >
                Corpus Health
              </button>

            </div>

          </div>

        </footer>
      )}

    </div>
  );
};
