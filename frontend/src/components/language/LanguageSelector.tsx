import React from 'react';
import { Languages } from 'lucide-react';
import { useSession, sessionStore } from '../../features/session/sessionStore';
import { SupportedLanguage } from '../../features/session/sessionTypes';

interface LanguageSelectorProps {
  className?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ className = '' }) => {
  const { language } = useSession();

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    sessionStore.setLanguage(e.target.value as SupportedLanguage);
  };

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-1)',
        position: 'relative',
      }}
      className={className}
    >
      <Languages
        size={16}
        aria-hidden="true"
        style={{
          color: 'var(--color-text-secondary)',
          position: 'absolute',
          left: '8px',
          pointerEvents: 'none',
        }}
      />
      <label htmlFor="language-select" className="visually-hidden" style={{ position: 'absolute', width: 1, height: 1, padding: 0, margin: -1, overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', border: 0 }}>
        Select Language
      </label>
      <select
        id="language-select"
        value={language}
        onChange={handleLanguageChange}
        aria-label="Interface language"
        style={{
          appearance: 'none',
          padding: '0.4rem 1.75rem 0.4rem 1.85rem',
          fontSize: '0.8125rem',
          fontWeight: 500,
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-text-primary)',
          cursor: 'pointer',
          backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 0.5rem center',
          backgroundSize: '1em',
          transition: 'border-color var(--transition-fast)',
        }}
      >
        <option value="en">English (EN)</option>
        <option value="hi">हिंदी (HI)</option>
      </select>
    </div>
  );
};
