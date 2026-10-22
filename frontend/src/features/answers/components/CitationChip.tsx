import React from 'react';
import { ExternalLink, BookCheck } from 'lucide-react';
import { Citation } from '../../../services/api-client';

interface CitationChipProps {
  citation: Citation;
  onClick?: (citation: Citation) => void;
  className?: string;
}

export const CitationChip: React.FC<CitationChipProps> = ({
  citation,
  onClick,
  className = '',
}) => {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onClick?.(citation);
    if (!onClick && citation.sourceUrl) {
      window.open(citation.sourceUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={`Citation: ${citation.title}${citation.locator ? ` (${citation.locator})` : ''}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '0.2rem 0.55rem',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: 'var(--color-soft-green)',
        border: '1px solid rgba(46, 125, 91, 0.3)',
        color: 'var(--color-primary)',
        fontSize: '0.75rem',
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'all var(--transition-fast)',
        maxWidth: '280px',
        textOverflow: 'ellipsis',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
      }}
      className={`citation-chip ${className}`}
      title={`${citation.title} ${citation.locator ? `[${citation.locator}]` : ''}`}
    >
      <BookCheck size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {citation.locator ? `${citation.title} · ${citation.locator}` : citation.title}
      </span>
      {citation.sourceUrl && (
        <ExternalLink size={10} aria-hidden="true" style={{ flexShrink: 0, opacity: 0.7 }} />
      )}
    </button>
  );
};
