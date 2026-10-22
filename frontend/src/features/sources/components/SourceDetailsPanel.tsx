import React from 'react';
import { ExternalLink, Calendar, BookOpen, Shield, FileText } from 'lucide-react';
import { Citation } from '../../../services/api-client';
import { SourceStatusBadge } from './SourceStatusBadge';

interface SourceDetailsPanelProps {
  citation: Citation;
  onClose?: () => void;
  className?: string;
}

export const SourceDetailsPanel: React.FC<SourceDetailsPanelProps> = ({
  citation,
  className = '',
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
      }}
      className={className}
    >
      {/* Header info */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-2)' }}>
        <div>
          <span className="badge badge-neutral text-xs" style={{ marginBottom: 'var(--space-1)' }}>
            Doc ID: {citation.documentId}
          </span>
          <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary)', margin: 0 }}>
            {citation.title}
          </h3>
        </div>
        <SourceStatusBadge status={citation.documentStatus} />
      </div>

      {/* Grid of statutory metadata */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-3)',
          backgroundColor: 'var(--color-surface-alt)',
          padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div>
          <span className="text-secondary text-xs" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Shield size={12} /> Jurisdiction
          </span>
          <strong style={{ fontSize: '0.875rem' }}>
            {citation.jurisdiction === 'india' ? 'India (Domestic ASU Acts)' : 'International IPR'}
          </strong>
        </div>

        <div>
          <span className="text-secondary text-xs" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <BookOpen size={12} /> Section / Rule Locator
          </span>
          <strong style={{ fontSize: '0.875rem' }}>
            {citation.locator || 'Entire Statute / Record'}
          </strong>
        </div>

        {citation.publicationDate && (
          <div>
            <span className="text-secondary text-xs" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={12} /> Publication Date
            </span>
            <strong style={{ fontSize: '0.875rem' }}>{citation.publicationDate}</strong>
          </div>
        )}

        {citation.effectiveDate && (
          <div>
            <span className="text-secondary text-xs" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={12} /> Effective As Of
            </span>
            <strong style={{ fontSize: '0.875rem' }}>{citation.effectiveDate}</strong>
          </div>
        )}
      </div>

      {citation.amendmentStatus && (
        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
          <strong>Amendment Notes:</strong> {citation.amendmentStatus}
        </div>
      )}

      {/* Validated source link */}
      {citation.sourceUrl && (
        <div>
          <a
            href={citation.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
            style={{ display: 'inline-flex', fontSize: '0.875rem', gap: '6px' }}
          >
            <FileText size={15} />
            <span>Open Verified Gazette / Registry Record</span>
            <ExternalLink size={14} />
          </a>
        </div>
      )}
    </div>
  );
};
