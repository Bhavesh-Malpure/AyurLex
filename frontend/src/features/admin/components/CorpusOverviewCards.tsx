import React from 'react';
import { Database, FileCheck, Layers, RefreshCw } from 'lucide-react';

interface CorpusOverviewCardsProps {
  stats?: {
    totalDocuments: number;
    activeSources: number;
    lastUpdated: string;
    verifiedCitationsCount: number;
  };
  isLoading?: boolean;
  onRefresh?: () => void;
  className?: string;
}

export const CorpusOverviewCards: React.FC<CorpusOverviewCardsProps> = ({
  stats = {
    totalDocuments: 14850,
    activeSources: 54,
    lastUpdated: '2026-10-20T14:30:00Z',
    verifiedCitationsCount: 42100,
  },
  isLoading = false,
  onRefresh,
  className = '',
}) => {
  const cards = [
    {
      label: 'Indexed Statutory Documents',
      value: stats.totalDocuments.toLocaleString(),
      subtext: 'Gazette notifications, Pharmacopoeias, Acts',
      icon: Database,
    },
    {
      label: 'Authoritative ASU Sources',
      value: stats.activeSources.toString(),
      subtext: 'First Schedule texts, API, AFI, CCRAS',
      icon: Layers,
    },
    {
      label: 'Verified Statutory Citations',
      value: stats.verifiedCitationsCount.toLocaleString(),
      subtext: 'Cross-indexed section & rule locators',
      icon: FileCheck,
    },
  ];

  const formattedDate = new Date(stats.lastUpdated).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }} className={className}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: 'var(--color-primary)', margin: 0 }}>
            Ayurveda Corpus Ingestion & Health
          </h3>
          <span className="text-secondary text-xs">
            Last successful corpus synchronization: <strong>{formattedDate}</strong>
          </span>
        </div>

        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            disabled={isLoading}
            className="btn btn-secondary"
            style={{ fontSize: '0.8125rem', padding: '0.35rem 0.75rem' }}
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
            <span>Sync Corpus Status</span>
          </button>
        )}
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'var(--space-4)',
        }}
      >
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                <span className="text-secondary text-xs">{card.label}</span>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--color-soft-green)',
                    color: 'var(--color-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Icon size={16} />
                </div>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)', lineHeight: 1.2 }}>
                {card.value}
              </div>
              <span className="text-secondary text-xs" style={{ display: 'block', marginTop: 'var(--space-1)' }}>
                {card.subtext}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
