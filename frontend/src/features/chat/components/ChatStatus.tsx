import React from 'react';
import { Loader2, Search, FileCheck, AlertCircle } from 'lucide-react';

export type ResearchStage = 'idle' | 'searching' | 'analyzing' | 'verifying_citations' | 'error';

interface ChatStatusProps {
  stage: ResearchStage;
  errorMessage?: string;
  onRetry?: () => void;
  className?: string;
}

export const ChatStatus: React.FC<ChatStatusProps> = ({
  stage,
  errorMessage,
  onRetry,
  className = '',
}) => {
  if (stage === 'idle') return null;

  if (stage === 'error') {
    return (
      <div
        role="alert"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.65rem var(--space-4)',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--color-error-bg)',
          color: '#991B1B',
          fontSize: '0.85rem',
          border: '1px solid var(--color-error-border)',
        }}
        className={className}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <AlertCircle size={16} aria-hidden="true" />
          <span>{errorMessage || 'Unable to retrieve statutory sources. Please try again.'}</span>
        </div>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.2rem 0.55rem' }}
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  const stageMessages: Record<ResearchStage, { text: string; icon: React.ElementType }> = {
    idle: { text: '', icon: Loader2 },
    searching: { text: 'Searching ASU pharmacopoeias & patent databases...', icon: Search },
    analyzing: { text: 'Evaluating prior art & Section 3(p) statutory exclusions...', icon: Loader2 },
    verifying_citations: { text: 'Verifying Gazette notifications & citation locators...', icon: FileCheck },
    error: { text: '', icon: AlertCircle },
  };

  const current = stageMessages[stage] || stageMessages.searching;
  const Icon = current.icon;

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        padding: '0.5rem var(--space-4)',
        borderRadius: 'var(--radius-full)',
        backgroundColor: 'var(--color-soft-green)',
        color: 'var(--color-primary)',
        fontSize: '0.825rem',
        fontWeight: 500,
        border: '1px solid rgba(15, 81, 50, 0.15)',
      }}
      className={className}
    >
      <Icon size={14} className="animate-spin" aria-hidden="true" />
      <span>{current.text}</span>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1.2s linear infinite;
        }
      `}</style>
    </div>
  );
};
