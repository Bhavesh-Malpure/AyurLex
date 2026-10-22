import React from 'react';
import { ShieldCheck, Library, AlertCircle, FileSearch } from 'lucide-react';
import { DisclaimerBanner } from '../../components/legal/DisclaimerBanner';

interface ComplianceOverviewProps {
  onStartResearch: (query: string) => void;
  className?: string;
}

export const ComplianceOverview: React.FC<ComplianceOverviewProps> = ({
  onStartResearch,
  className = '',
}) => {
  return (
    <div className={`container-wide ${className}`} style={{ padding: 'var(--space-8) var(--space-4)' }}>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <span className="badge badge-green" style={{ marginBottom: 'var(--space-2)' }}>
          Statutory Safeguards
        </span>
        <h2 style={{ fontSize: '1.4rem', color: 'var(--color-primary)', margin: 0 }}>
          Biological Diversity (ABS) & Traditional Knowledge (TKDL)
        </h2>
        <p className="text-secondary" style={{ fontSize: '0.9rem', marginTop: '4px' }}>
          Overview of mandatory compliance under the Biological Diversity Act, 2002 and Traditional Knowledge prior-art scrutiny.
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 'var(--space-6)',
          marginBottom: 'var(--space-6)',
        }}
      >
        {/* Card 1: ABS Compliance */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-3)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-soft-green)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ShieldCheck size={20} />
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Access & Benefit Sharing (ABS)</h3>
            </div>
            <p className="text-secondary" style={{ fontSize: '0.875rem', lineHeight: 1.6, marginBottom: 'var(--space-4)' }}>
              Mandatory under Section 3 and Section 6 of the Biological Diversity Act, 2002. Any individual or non-Indian entity utilizing Indian biological resources for commercial utilization or applying for intellectual property must seek prior National Biodiversity Authority (NBA) approval.
            </p>
            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-surface-alt)', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              <strong>Key Mandate:</strong> Form I (NBA Commercial Access) & Form III (IPR Prior Approval).
            </div>
          </div>

          <div style={{ marginTop: 'var(--space-4)' }}>
            <button
              type="button"
              onClick={() => onStartResearch('What are the Form III requirements under the Biological Diversity Act for patent applications?')}
              className="btn btn-secondary"
              style={{ width: '100%', fontSize: '0.85rem' }}
            >
              <FileSearch size={14} />
              <span>Query ABS Form III Rules</span>
            </button>
          </div>
        </div>

        {/* Card 2: TKDL & Section 3(p) */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-3)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-soft-green)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Library size={20} />
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: 0 }}>TKDL Prior Art Scrutiny</h3>
            </div>
            <p className="text-secondary" style={{ fontSize: '0.875rem', lineHeight: 1.6, marginBottom: 'var(--space-4)' }}>
              The Traditional Knowledge Digital Library translates classical Sanskrit, Hindi, Arabic, Persian, and Tamil formulations into structured patent classification terms. Section 3(p) of the Patents Act strictly prohibits patenting traditional Ayurvedic wisdom.
            </p>
            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-surface-alt)', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              <strong>Key Mandate:</strong> Overcoming Section 3(p) requires demonstrably non-obvious synergistic extraction with quantified proof.
            </div>
          </div>

          <div style={{ marginTop: 'var(--space-4)' }}>
            <button
              type="button"
              onClick={() => onStartResearch('How to demonstrate unexpected synergy under Section 3(e) to overcome Section 3(p)?')}
              className="btn btn-secondary"
              style={{ width: '100%', fontSize: '0.85rem' }}
            >
              <FileSearch size={14} />
              <span>Query Section 3(p) Synergistic Burden</span>
            </button>
          </div>
        </div>
      </div>

      <div
        style={{
          padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)',
          backgroundColor: '#EFF6FF',
          border: '1px solid #BFDBFE',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-3)',
          marginBottom: 'var(--space-4)',
        }}
      >
        <AlertCircle size={18} style={{ color: '#2563EB', flexShrink: 0 }} />
        <span style={{ fontSize: '0.85rem', color: '#1E40AF' }}>
          Phase 2 will integrate the automated interactive ABS Form wizard and direct authorized TKDL classification search integration as backend contracts become confirmed.
        </span>
      </div>

      <DisclaimerBanner variant="inline" />
    </div>
  );
};
