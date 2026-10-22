import React from 'react';
import { Globe, Compass } from 'lucide-react';
import { useSession, sessionStore } from '../../session/sessionStore';
import { Jurisdiction } from '../../session/sessionTypes';

interface JurisdictionToggleProps {
  className?: string;
}

export const JurisdictionToggle: React.FC<JurisdictionToggleProps> = ({ className = '' }) => {
  const { jurisdiction } = useSession();

  const handleSelect = (j: Jurisdiction) => {
    sessionStore.setJurisdiction(j);
  };

  return (
    <div
      role="group"
      aria-label="Legal Jurisdiction Selection"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px',
        backgroundColor: '#F3F4F6',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--color-border)',
      }}
      className={className}
    >
      <button
        type="button"
        role="radio"
        aria-checked={jurisdiction === 'india'}
        onClick={() => handleSelect('india')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '5px',
          padding: '0.35rem 0.75rem',
          fontSize: '0.8125rem',
          fontWeight: jurisdiction === 'india' ? 600 : 500,
          borderRadius: 'calc(var(--radius-md) - 2px)',
          border: 'none',
          backgroundColor: jurisdiction === 'india' ? 'var(--color-surface)' : 'transparent',
          color: jurisdiction === 'india' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
          boxShadow: jurisdiction === 'india' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
          cursor: 'pointer',
          transition: 'all var(--transition-fast)',
        }}
        title="Search Indian ASU regulations, TKDL, Indian Patent Act (Sec 3p)"
      >
        <Compass size={14} aria-hidden="true" />
        <span>India (ASU & Acts)</span>
      </button>

      <button
        type="button"
        role="radio"
        aria-checked={jurisdiction === 'international'}
        onClick={() => handleSelect('international')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '5px',
          padding: '0.35rem 0.75rem',
          fontSize: '0.8125rem',
          fontWeight: jurisdiction === 'international' ? 600 : 500,
          borderRadius: 'calc(var(--radius-md) - 2px)',
          border: 'none',
          backgroundColor: jurisdiction === 'international' ? 'var(--color-surface)' : 'transparent',
          color: jurisdiction === 'international' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
          boxShadow: jurisdiction === 'international' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
          cursor: 'pointer',
          transition: 'all var(--transition-fast)',
        }}
        title="Search International IPR, USPTO, EPO, WIPO conventions"
      >
        <Globe size={14} aria-hidden="true" />
        <span>International (WIPO/EPO)</span>
      </button>
    </div>
  );
};
