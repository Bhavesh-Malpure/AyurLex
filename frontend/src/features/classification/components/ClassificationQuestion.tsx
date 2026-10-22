import React from 'react';

export interface QuestionOption {
  id: string;
  label: string;
  description?: string;
}

export interface WizardQuestion {
  id: string;
  title: string;
  description: string;
  options: QuestionOption[];
}

interface ClassificationQuestionProps {
  question: WizardQuestion;
  selectedOptionId?: string;
  onSelectOption: (optionId: string) => void;
  className?: string;
}

export const ClassificationQuestion: React.FC<ClassificationQuestionProps> = ({
  question,
  selectedOptionId,
  onSelectOption,
  className = '',
}) => {
  return (
    <fieldset
      style={{
        border: 'none',
        padding: 0,
        margin: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
      }}
      className={className}
    >
      <legend style={{ padding: 0, marginBottom: 'var(--space-2)' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: 'var(--space-1)' }}>
          {question.title}
        </h3>
        <p className="text-secondary" style={{ fontSize: '0.9rem' }}>
          {question.description}
        </p>
      </legend>

      <div
        role="radiogroup"
        aria-label={question.title}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)',
        }}
      >
        {question.options.map((opt) => {
          const isSelected = selectedOptionId === opt.id;
          return (
            <label
              key={opt.id}
              className="card card-clickable"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 'var(--space-3)',
                padding: 'var(--space-4)',
                borderColor: isSelected ? 'var(--color-secondary)' : 'var(--color-border)',
                backgroundColor: isSelected ? 'var(--color-soft-green)' : 'var(--color-surface)',
                cursor: 'pointer',
              }}
            >
              <input
                type="radio"
                name={question.id}
                value={opt.id}
                checked={isSelected}
                onChange={() => onSelectOption(opt.id)}
                style={{
                  marginTop: '3px',
                  accentColor: 'var(--color-primary)',
                  cursor: 'pointer',
                }}
              />
              <div style={{ flex: 1 }}>
                <span
                  style={{
                    display: 'block',
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    color: isSelected ? 'var(--color-primary)' : 'var(--color-text-primary)',
                  }}
                >
                  {opt.label}
                </span>
                {opt.description && (
                  <span
                    className="text-secondary"
                    style={{
                      display: 'block',
                      fontSize: '0.85rem',
                      marginTop: '2px',
                    }}
                  >
                    {opt.description}
                  </span>
                )}
              </div>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
};
