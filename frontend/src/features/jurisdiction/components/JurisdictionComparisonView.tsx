import React from 'react';
import { Compass, Globe, SplitSquareVertical, ArrowRight } from 'lucide-react';

interface JurisdictionComparisonViewProps {
  onClose?: () => void;
  onExploreTopic?: (topic: string) => void;
  className?: string;
}

export const JurisdictionComparisonView: React.FC<JurisdictionComparisonViewProps> = ({
  onClose,
  onExploreTopic,
  className = '',
}) => {
  const comparisonAspects = [
    {
      title: 'Traditional Knowledge Patentability Exclusion',
      india: {
        provision: 'Indian Patents Act, 1970 — Section 3(p)',
        detail:
          'Invention which in effect is traditional knowledge or an aggregation/duplication of known properties of traditionally known components is not an invention.',
        evidentiaryStandard: 'TKDL citations act as complete anticipation of novelty and inventive step.',
      },
      international: {
        provision: 'EPO Art. 54/56 & USPTO 35 U.S.C. 102/103',
        detail:
          'No blanket statutory exclusion for traditional knowledge. Evaluated strictly under general prior art novelty and obviousness tests.',
        evidentiaryStandard: 'Requires published written prior art; undocumented oral traditions often face proof challenges.',
      },
    },
    {
      title: 'Synergy and Combination Claims',
      india: {
        provision: 'Indian Patents Act, 1970 — Section 3(e)',
        detail:
          'A substance obtained by a mere admixture resulting only in the aggregation of the properties of the components is non-patentable without unexpected synergy.',
        evidentiaryStandard: 'Applicant must prove statistically significant synergistic efficacy over individual ingredients.',
      },
      international: {
        provision: 'EPO Problem-and-Solution Approach / USPTO Synergy',
        detail:
          'Combination claims are patentable if a technical problem is solved with unexpected non-obvious results.',
        evidentiaryStandard: 'Comparative experimental data or technical effects across the full claim breadth.',
      },
    },
    {
      title: 'Biological Diversity Access & Benefit Sharing (ABS)',
      india: {
        provision: 'Biological Diversity Act, 2002 — Section 6',
        detail:
          'Mandatory prior approval of the National Biodiversity Authority (NBA) before applying for any IPR based on Indian biological resources.',
        evidentiaryStandard: 'NBA clearance required prior to grant; non-compliance carries criminal penalties.',
      },
      international: {
        provision: 'Nagoya Protocol / WIPO Treaty on Genetic Resources',
        detail:
          'Mandatory patent disclosure of country of origin and certificate of compliance (IRCC) depending on member country ratifications.',
        evidentiaryStandard: 'Patent offices vary in disclosure stringency; EU requires compliance checks under EU Reg 511/2014.',
      },
    },
  ];

  return (
    <div className={`container-wide ${className}`} style={{ padding: 'var(--space-8) var(--space-4)' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-3)',
          marginBottom: 'var(--space-6)',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: 'var(--space-4)',
        }}
      >
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: 'var(--space-1)' }}>
            <SplitSquareVertical size={18} style={{ color: 'var(--color-primary)' }} />
            <span className="badge badge-green">Side-by-Side Regulatory Analysis</span>
          </div>
          <h2 style={{ fontSize: '1.4rem', color: 'var(--color-primary)', margin: 0 }}>
            Comparative Statutory Analysis: India vs. International
          </h2>
          <p className="text-secondary" style={{ fontSize: '0.875rem', marginTop: '4px' }}>
            Explicit separation of Indian ASU frameworks and global IPR jurisdictions.
          </p>
        </div>

        {onClose && (
          <button type="button" onClick={onClose} className="btn btn-secondary">
            <span>Return to Workspace</span>
          </button>
        )}
      </div>

      {/* Grid of comparison rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {comparisonAspects.map((aspect, idx) => (
          <div
            key={idx}
            className="card"
            style={{
              padding: 0,
              overflow: 'hidden',
            }}
          >
            {/* Aspect Title Header */}
            <div
              style={{
                padding: 'var(--space-4) var(--space-6)',
                backgroundColor: 'var(--color-surface-alt)',
                borderBottom: '1px solid var(--color-border)',
                fontWeight: 600,
                fontSize: '1rem',
                color: 'var(--color-primary)',
              }}
            >
              {aspect.title}
            </div>

            {/* Split 2-column layout */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              }}
            >
              {/* India Column */}
              <div
                style={{
                  padding: 'var(--space-6)',
                  borderRight: '1px solid var(--color-border)',
                  backgroundColor: 'rgba(232, 245, 238, 0.25)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: 'var(--space-2)' }}>
                  <Compass size={16} style={{ color: 'var(--color-primary)' }} />
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-primary)' }}>
                    India (Domestic Framework)
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 'var(--space-2)' }}>
                  {aspect.india.provision}
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 'var(--space-3)' }}>
                  {aspect.india.detail}
                </p>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)', backgroundColor: 'var(--color-soft-green)', padding: '0.4rem 0.65rem', borderRadius: 'var(--radius-sm)' }}>
                  <strong>Evidentiary Rule:</strong> {aspect.india.evidentiaryStandard}
                </div>
              </div>

              {/* International Column */}
              <div
                style={{
                  padding: 'var(--space-6)',
                  backgroundColor: 'var(--color-surface)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: 'var(--space-2)' }}>
                  <Globe size={16} style={{ color: 'var(--color-secondary)' }} />
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-secondary)' }}>
                    International (WIPO, EPO, USPTO)
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 'var(--space-2)' }}>
                  {aspect.international.provision}
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 'var(--space-3)' }}>
                  {aspect.international.detail}
                </p>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', backgroundColor: '#F3F4F6', padding: '0.4rem 0.65rem', borderRadius: 'var(--radius-sm)' }}>
                  <strong>Evidentiary Rule:</strong> {aspect.international.evidentiaryStandard}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {onExploreTopic && (
        <div style={{ marginTop: 'var(--space-8)', textAlign: 'center' }}>
          <button
            type="button"
            onClick={() => onExploreTopic('Section 3(p) vs EPO novelty')}
            className="btn btn-primary"
          >
            <span>Query Cross-Jurisdiction Harmonization</span>
            <ArrowRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
};
