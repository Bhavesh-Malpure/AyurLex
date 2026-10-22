import React from 'react';
import { ArrowRight, Sparkles, BookOpen } from 'lucide-react';
import { JurisdictionStatus } from '../../jurisdiction/components/JurisdictionStatus';

interface HeroSectionProps {
  onStartResearch: () => void;
  onOpenClassifier: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onStartResearch,
  onOpenClassifier,
}) => {
  return (
    <section
      aria-labelledby="hero-title"
      style={{
        padding: 'var(--space-12) 0 var(--space-8)',
        borderBottom: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
        position: 'relative',
      }}
    >
      <div className="container-narrow" style={{ textAlign: 'center' }}>
        {/* Status Pill */}
        <div style={{ display: 'inline-flex', marginBottom: 'var(--space-4)' }}>
          <JurisdictionStatus showDetails={false} />
        </div>

        {/* Main Headline */}
        <h1
          id="hero-title"
          style={{
            marginBottom: 'var(--space-4)',
            maxWidth: '750px',
            marginLeft: 'auto',
            marginRight: 'auto',
          }}
        >
          Ayurveda IP & Regulatory Research Intelligence
        </h1>

        {/* Subtitle / Supporting copy */}
        <p
          className="text-secondary"
          style={{
            fontSize: '1.075rem',
            maxWidth: '640px',
            margin: '0 auto var(--space-8)',
            lineHeight: 1.7,
          }}
        >
          Specialized legal research assistant for Ayurvedic formulations, ASU regulatory compliance under the Drugs & Cosmetics Act, Traditional Knowledge (TKDL), Section 3(p) prior art verification, and ABS biodiversity filings.
        </p>

        {/* Action Buttons (F03: Start Research Button) */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--space-3)',
          }}
        >
          <button
            type="button"
            onClick={onStartResearch}
            className="btn btn-primary"
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              boxShadow: '0 2px 8px rgba(15, 81, 50, 0.2)',
            }}
          >
            <span>Start Research Query</span>
            <ArrowRight size={18} aria-hidden="true" />
          </button>

          <button
            type="button"
            onClick={onOpenClassifier}
            className="btn btn-secondary"
            style={{
              padding: '0.75rem 1.35rem',
              fontSize: '1rem',
            }}
          >
            <Sparkles size={17} aria-hidden="true" style={{ color: 'var(--color-secondary)' }} />
            <span>Formulation Classifier Wizard</span>
          </button>
        </div>

        {/* Informational assurance note */}
        <div
          style={{
            marginTop: 'var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--space-2)',
            fontSize: '0.8125rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          <BookOpen size={14} aria-hidden="true" />
          <span>Verified against statutory Gazette notifications, ASU pharmacopoeias, and Section 3(p) guidelines.</span>
        </div>
      </div>
    </section>
  );
};
