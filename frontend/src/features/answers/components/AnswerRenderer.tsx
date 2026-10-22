import React from 'react';
import { Citation } from '../../../services/api-client';
import { CitationChip } from './CitationChip';
import { ConfidenceBadge, ConfidenceLevel } from './ConfidenceBadge';
import { AbstentionPanel } from './AbstentionPanel';
import { AnswerMeta } from './AnswerMeta';
import { DisclaimerBanner } from '../../../components/legal/DisclaimerBanner';

export interface AnswerData {
  text?: string;
  isAbstained?: boolean;
  abstentionReason?: string;
  confidence?: ConfidenceLevel;
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
  onRefineQuestion,
  onEscalate,
  className = '',
}) => {
  // If backend signaled abstention / insufficient evidence
  if (answer.isAbstained) {
    return (
      <div className={className}>
        <AbstentionPanel
          reason={answer.abstentionReason}
          onRefineQuestion={onRefineQuestion}
          onEscalate={onEscalate}
        />
        <DisclaimerBanner variant="inline" />
      </div>
    );
  }

  return (
    <article
      aria-label="Substantive Research Answer"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
      className={className}
    >
      {/* Top Header: Confidence & Jurisdiction */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-2)',
          marginBottom: 'var(--space-1)',
        }}
      >
        <ConfidenceBadge level={answer.confidence} />
        {answer.language && (
          <span className="badge badge-neutral text-xs">
            Language: {answer.language.toUpperCase()}
          </span>
        )}
      </div>

      {/* Answer Body Text: readable typography */}
      <div
        style={{
          fontSize: '0.95rem',
          lineHeight: 1.7,
          color: 'var(--color-text-primary)',
          whiteSpace: 'pre-line',
        }}
      >
        {answer.text || 'No substantive text provided by research retriever.'}
      </div>

      {/* Citations Section */}
      {answer.citations && answer.citations.length > 0 && (
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
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              color: 'var(--color-text-secondary)',
              marginBottom: 'var(--space-2)',
            }}
          >
            Statutory Citations & Authorities ({answer.citations.length})
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

      {/* Answer Metadata: As-of Date & Verification */}
      <AnswerMeta asOfDate={answer.asOfDate} jurisdiction={answer.jurisdiction} />

      {/* Mandatory substantive answer disclaimer banner */}
      <DisclaimerBanner variant="inline" />
    </article>
  );
};
