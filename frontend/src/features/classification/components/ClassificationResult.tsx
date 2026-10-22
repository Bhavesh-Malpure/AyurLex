import React from 'react';
import { Scale, FileCheck2, ArrowRight, RotateCcw, AlertCircle } from 'lucide-react';
import { DisclaimerBanner } from '../../../components/legal/DisclaimerBanner';

export interface ClassificationResultData {
  category: string;
  regulatorySubtype: string;
  patentabilityStatus: string;
  legalBasis: string;
  requiredClinicalEvidence: string;
  statutoryRules: string[];
}

interface ClassificationResultProps {
  result: ClassificationResultData;
  onRestart: () => void;
  onExploreResearch: (category: string) => void;
  className?: string;
}

export const ClassificationResult: React.FC<ClassificationResultProps> = ({
  result,
  onRestart,
  onExploreResearch,
  className = '',
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-6)',
      }}
      className={className}
    >
      {/* Category Card */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--color-primary)',
          padding: 'var(--space-6)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
          <span className="badge badge-green">Regulatory Assessment</span>
          <span className="badge badge-neutral text-xs">Section 3(p) Scrutiny</span>
        </div>

        <h2 style={{ fontSize: '1.4rem', color: 'var(--color-primary)', marginBottom: 'var(--space-1)' }}>
          {result.category}
        </h2>
        <p className="text-secondary" style={{ fontSize: '0.925rem' }}>
          Classification Subtype: <strong>{result.regulatorySubtype}</strong>
        </p>

        <hr style={{ border: 'none', borderTop: '1px solid var(--color-border)', margin: 'var(--space-4) 0' }} />

        {/* Breakdown details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
              <Scale size={16} style={{ color: 'var(--color-secondary)' }} />
              <h4 style={{ fontSize: '0.95rem', margin: 0 }}>Statutory Basis & Legal Ground</h4>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {result.legalBasis}
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
              <FileCheck2 size={16} style={{ color: 'var(--color-secondary)' }} />
              <h4 style={{ fontSize: '0.95rem', margin: 0 }}>Patentability & Section 3(p) Status</h4>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {result.patentabilityStatus}
            </p>
          </div>

          <div>
            <h4 style={{ fontSize: '0.95rem', marginBottom: 'var(--space-1)' }}>Applicable Rules & Gazette References</h4>
            <ul style={{ paddingLeft: 'var(--space-4)', fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {result.statutoryRules.map((rule, idx) => (
                <li key={idx}>{rule}</li>
              ))}
            </ul>
          </div>
        </div>

        <div
          style={{
            marginTop: 'var(--space-6)',
            padding: 'var(--space-3)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: '#FEF3C7',
            border: '1px solid #FDE68A',
            fontSize: '0.8rem',
            color: '#92400E',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
          }}
        >
          <AlertCircle size={15} style={{ flexShrink: 0 }} />
          <span>Notice: This assessment is an automated analytical aid and does not constitute a legally binding certification from the State Licensing Authority (SLA) or Indian Patent Office.</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          type="button"
          onClick={onRestart}
          className="btn btn-secondary"
        >
          <RotateCcw size={16} />
          <span>Classify Another Formulation</span>
        </button>

        <button
          type="button"
          onClick={() => onExploreResearch(result.category)}
          className="btn btn-primary"
        >
          <span>Open Full Research Workspace for {result.category}</span>
          <ArrowRight size={16} />
        </button>
      </div>

      <DisclaimerBanner variant="inline" />
    </div>
  );
};
