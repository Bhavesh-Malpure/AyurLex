import React from 'react';
import { Calendar, Shield } from 'lucide-react';

interface AnswerMetaProps {
  asOfDate?: string;
  jurisdiction?: 'india' | 'international';
  className?: string;
}

export const AnswerMeta: React.FC<AnswerMetaProps> = ({
  asOfDate,
  jurisdiction = 'india',
  className = '',
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 'var(--space-3)',
        fontSize: '0.75rem',
        color: 'var(--color-text-secondary)',
        paddingTop: 'var(--space-2)',
        borderTop: '1px solid var(--color-border-subtle)',
      }}
      className={className}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <Shield size={12} aria-hidden="true" />
        <span>Jurisdiction: {jurisdiction === 'india' ? 'India (Domestic Acts)' : 'International (IP Conventions)'}</span>
      </div>

      {asOfDate && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Calendar size={12} aria-hidden="true" />
          <span>Statutory Gazette Verification As Of: <strong>{asOfDate}</strong></span>
        </div>
      )}
    </div>
  );
};
