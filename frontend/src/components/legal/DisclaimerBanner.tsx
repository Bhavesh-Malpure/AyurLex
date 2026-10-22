import React from 'react';
import { AlertCircle } from 'lucide-react';

interface DisclaimerBannerProps {
  /**
   * 'global' is the sticky/persistent banner in the app shell.
   * 'inline' is attached to substantive answers or result cards.
   */
  variant?: 'global' | 'inline';
  className?: string;
}

export const LEGAL_DISCLAIMER_TEXT =
  'Ayurlex provides information for research purposes and does not provide legal advice.';

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({
  variant = 'global',
  className = '',
}) => {
  if (variant === 'global') {
    return (
      <aside
        role="complementary"
        aria-label="Legal Disclaimer"
        style={{
          backgroundColor: 'var(--color-soft-green)',
          borderBottom: '1px solid rgba(15, 81, 50, 0.15)',
          padding: '0.45rem var(--space-4)',
          fontSize: '0.8125rem',
          color: 'var(--color-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 'var(--space-2)',
          textAlign: 'center',
          fontWeight: 500,
          zIndex: 40,
        }}
        className={className}
      >
        <AlertCircle size={15} aria-hidden="true" style={{ flexShrink: 0 }} />
        <span>{LEGAL_DISCLAIMER_TEXT}</span>
      </aside>
    );
  }

  // Inline variant for substantive answers
  return (
    <div
      role="note"
      aria-label="Research Disclaimer"
      style={{
        marginTop: 'var(--space-4)',
        padding: '0.6rem 0.85rem',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: '#F9FAFB',
        border: '1px solid var(--color-border)',
        fontSize: '0.775rem',
        color: 'var(--color-text-secondary)',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
      }}
      className={className}
    >
      <AlertCircle size={14} aria-hidden="true" style={{ flexShrink: 0, color: 'var(--color-text-tertiary)' }} />
      <span>{LEGAL_DISCLAIMER_TEXT}</span>
    </div>
  );
};
