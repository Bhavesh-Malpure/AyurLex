import React from 'react';
import { SourceStatusBadge } from '../../sources/components/SourceStatusBadge';

export interface SourceHealthRecord {
  id: string;
  name: string;
  jurisdiction: 'india' | 'international';
  totalChunks: number;
  lastSync: string;
  status: 'current' | 'superseded' | 'unknown';
}

interface SourceHealthTableProps {
  sources?: SourceHealthRecord[];
  className?: string;
}

export const SourceHealthTable: React.FC<SourceHealthTableProps> = ({
  sources = [
    {
      id: 'src_1',
      name: 'Ayurvedic Pharmacopoeia of India (API) Vol I-IX',
      jurisdiction: 'india',
      totalChunks: 4820,
      lastSync: '2026-10-20',
      status: 'current',
    },
    {
      id: 'src_2',
      name: 'Drugs and Cosmetics Act, 1940 & Rules 1945',
      jurisdiction: 'india',
      totalChunks: 2150,
      lastSync: '2026-10-18',
      status: 'current',
    },
    {
      id: 'src_3',
      name: 'Indian Patent Act 1970 (Section 3p/3d/3e guidelines)',
      jurisdiction: 'india',
      totalChunks: 1420,
      lastSync: '2026-10-19',
      status: 'current',
    },
    {
      id: 'src_4',
      name: 'Traditional Knowledge Digital Library (TKDL Sample Index)',
      jurisdiction: 'india',
      totalChunks: 5310,
      lastSync: '2026-10-15',
      status: 'current',
    },
    {
      id: 'src_5',
      name: 'WIPO / Nagoya Protocol Directives on ABS',
      jurisdiction: 'international',
      totalChunks: 1150,
      lastSync: '2026-10-10',
      status: 'current',
    },
  ],
  className = '',
}) => {
  return (
    <div className={`card ${className}`} style={{ padding: 'var(--space-6)', overflowX: 'auto' }}>
      <h4 style={{ fontSize: '1rem', color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }}>
        Statutory Source Ingestion Health & Freshness
      </h4>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--color-border)', textAlign: 'left', color: 'var(--color-text-secondary)' }}>
            <th style={{ padding: 'var(--space-2) var(--space-3)' }}>Statutory Source</th>
            <th style={{ padding: 'var(--space-2) var(--space-3)' }}>Jurisdiction</th>
            <th style={{ padding: 'var(--space-2) var(--space-3)' }}>Indexed Records</th>
            <th style={{ padding: 'var(--space-2) var(--space-3)' }}>Last Ingestion</th>
            <th style={{ padding: 'var(--space-2) var(--space-3)' }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((src) => (
            <tr key={src.id} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
              <td style={{ padding: 'var(--space-3)', fontWeight: 500, color: 'var(--color-primary)' }}>
                {src.name}
              </td>
              <td style={{ padding: 'var(--space-3)' }}>
                <span className="badge badge-neutral text-xs">
                  {src.jurisdiction === 'india' ? 'India' : 'International'}
                </span>
              </td>
              <td style={{ padding: 'var(--space-3)' }}>{src.totalChunks.toLocaleString()}</td>
              <td style={{ padding: 'var(--space-3)', color: 'var(--color-text-secondary)' }}>{src.lastSync}</td>
              <td style={{ padding: 'var(--space-3)' }}>
                <SourceStatusBadge status={src.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
