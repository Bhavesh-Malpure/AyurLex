import React from 'react';
import { Edit2, CheckCircle2 } from 'lucide-react';
import { WizardQuestion } from './ClassificationQuestion';

interface ClassificationSummaryProps {
  questions: WizardQuestion[];
  answers: Record<string, string>;
  onEditStep: (stepIndex: number) => void;
  className?: string;
}

export const ClassificationSummary: React.FC<ClassificationSummaryProps> = ({
  questions,
  answers,
  onEditStep,
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
      <div style={{ marginBottom: 'var(--space-2)' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: 'var(--space-1)' }}>
          Review Formulation Attributes
        </h3>
        <p className="text-secondary" style={{ fontSize: '0.9rem' }}>
          Please review your responses before generating the statutory regulatory classification and Section 3(p) assessment.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {questions.map((q, idx) => {
          const selectedOptionId = answers[q.id];
          const selectedOpt = q.options.find((o) => o.id === selectedOptionId);

          return (
            <div
              key={q.id}
              className="card"
              style={{
                padding: 'var(--space-3) var(--space-4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 'var(--space-3)',
              }}
            >
              <div>
                <span className="text-secondary text-xs" style={{ display: 'block' }}>
                  Step {idx + 1}: {q.title}
                </span>
                <strong style={{ fontSize: '0.925rem', color: 'var(--color-primary)' }}>
                  {selectedOpt ? selectedOpt.label : 'Not answered'}
                </strong>
              </div>

              <button
                type="button"
                onClick={() => onEditStep(idx)}
                className="btn btn-ghost"
                style={{ fontSize: '0.8125rem', padding: '0.35rem 0.65rem' }}
                aria-label={`Edit Step ${idx + 1}: ${q.title}`}
              >
                <Edit2 size={13} aria-hidden="true" />
                <span>Edit</span>
              </button>
            </div>
          );
        })}
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          fontSize: '0.8125rem',
          color: 'var(--color-text-secondary)',
          marginTop: 'var(--space-2)',
        }}
      >
        <CheckCircle2 size={14} style={{ color: 'var(--color-primary)' }} />
        <span>All essential regulatory criteria have been specified.</span>
      </div>
    </div>
  );
};
