import React from 'react';
import { Citation } from '../../../services/api-client';
import { CitationChip } from './CitationChip';
import { DisclaimerBanner } from '../../../components/legal/DisclaimerBanner';
import { useSession } from '../../session/sessionStore';

export interface AnswerData {
  text?: string;
  isAbstained?: boolean;
  abstentionReason?: string;
  confidence?: 'high' | 'medium' | 'low';
  citations: Citation[];
  asOfDate?: string;
  jurisdiction?: 'india' | 'international';
  language?: string;
}

interface AnswerRendererProps {
  answer: AnswerData;
  onCitationClick?: (citation: Citation) => void;
  onRefineQuestion?: () => void;
  onEscalate?: () => void;
  className?: string;
}

export const AnswerRenderer: React.FC<AnswerRendererProps> = ({
  answer,
  onCitationClick,
  className = '',
}) => {
  const { showSources } = useSession();

  // If backend signaled abstention / insufficient evidence
  if (answer.isAbstained) {
    return (
      <div
        className={className}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)',
        }}
      >
        <div
          style={{
            fontSize: '0.95rem',
            lineHeight: 1.7,
            color: 'var(--color-text-primary)',
            whiteSpace: 'pre-line',
          }}
        >
          {answer.text || 'I could not verify a reliable answer from the available official research sources.'}
        </div>
        <DisclaimerBanner variant="inline" />
      </div>
    );
  }

  return (
    <article
      aria-label="Researched Legal Answer"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
      className={className}
    >
      {/* 1. Direct Researched Answer (with Key Points & Practical Next Steps if present) */}
      <div
        style={{
          fontSize: '0.95rem',
          lineHeight: 1.7,
          color: 'var(--color-text-primary)',
          whiteSpace: 'pre-line',
        }}
      >
        {answer.text || 'I could not verify a reliable answer from the available official research sources.'}
      </div>

      {/* 2. Optional Sources: only shown when user explicitly enables "Show Sources" setting */}
      {showSources && answer.citations && answer.citations.length > 0 && (
        <div
          style={{
            marginTop: 'var(--space-2)',
            padding: 'var(--space-3)',
            backgroundColor: 'var(--color-surface-alt)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border)',
          }}
        >
          <div
            style={{
              fontSize: '0.775rem',
              fontWeight: 600,
              color: 'var(--color-text-secondary)',
              marginBottom: 'var(--space-2)',
            }}
          >
            Official Research Sources ({answer.citations.length})
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {answer.citations.map((citation) => (
              <CitationChip
                key={citation.id}
                citation={citation}
                onClick={onCitationClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* 3. Mandatory Persistent Legal Disclaimer */}
      <DisclaimerBanner variant="inline" />
    </article>
  );
};
