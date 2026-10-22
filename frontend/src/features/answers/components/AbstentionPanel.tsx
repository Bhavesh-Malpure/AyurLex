import React from 'react';
import { HelpCircle, Sparkles, UserCheck } from 'lucide-react';

interface AbstentionPanelProps {
  reason?: string;
  onRefineQuestion?: () => void;
  onEscalate?: () => void;
  className?: string;
}

export const AbstentionPanel: React.FC<AbstentionPanelProps> = ({
  reason = 'Insufficient primary legal evidence in verified ASU pharmacopoeias or statutory databases to formulate a conclusive answer.',
  onRefineQuestion,
  onEscalate,
  className = '',
}) => {
  return (
    <div
      role="region"
      aria-label="Insufficient Evidence Advisory"
      style={{
        borderRadius: 'var(--radius-md)',
        backgroundColor: '#FFFBEB',
        border: '1px solid #FDE68A',
        padding: 'var(--space-6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
      className={className}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <HelpCircle size={20} aria-hidden="true" style={{ color: '#D97706', flexShrink: 0 }} />
        <h4 style={{ color: '#92400E', margin: 0, fontWeight: 600 }}>
          Inconclusive Statutory Basis — Research Abstention
        </h4>
      </div>

      <p style={{ margin: 0, fontSize: '0.9rem', color: '#78350F', lineHeight: 1.6 }}>
        {reason}
      </p>

      <div
        style={{
          marginTop: 'var(--space-2)',
          paddingTop: 'var(--space-3)',
          borderTop: '1px solid rgba(217, 119, 6, 0.2)',
          display: 'flex',
          flexWrap: 'wrap',
          gap: 'var(--space-3)',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: '0.8125rem', color: '#92400E', fontWeight: 500 }}>
          Recommended Next Steps:
        </span>

        {onRefineQuestion && (
          <button
            type="button"
            onClick={onRefineQuestion}
            className="btn btn-secondary"
            style={{
              fontSize: '0.8125rem',
              padding: '0.35rem 0.75rem',
              backgroundColor: 'var(--color-surface)',
              borderColor: '#FDE68A',
              color: '#92400E',
            }}
          >
            <Sparkles size={14} aria-hidden="true" />
            <span>Refine Query with Specific ASU Ingredients</span>
          </button>
        )}

        {onEscalate && (
          <button
            type="button"
            onClick={onEscalate}
            className="btn btn-ghost"
            style={{
              fontSize: '0.8125rem',
              padding: '0.35rem 0.75rem',
              color: '#92400E',
            }}
          >
            <UserCheck size={14} aria-hidden="true" />
            <span>Request Ayurveda IPR Facilitator Review</span>
          </button>
        )}
      </div>
    </div>
  );
};
