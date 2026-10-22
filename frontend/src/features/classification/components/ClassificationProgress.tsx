import React from 'react';

interface ClassificationProgressProps {
  currentStep: number;
  totalSteps: number;
  stepTitle?: string;
  className?: string;
}

export const ClassificationProgress: React.FC<ClassificationProgressProps> = ({
  currentStep,
  totalSteps,
  stepTitle,
  className = '',
}) => {
  const percentage = Math.min(Math.round((currentStep / totalSteps) * 100), 100);

  return (
    <div
      role="progressbar"
      aria-valuenow={currentStep}
      aria-valuemin={1}
      aria-valuemax={totalSteps}
      aria-label={`Question ${currentStep} of ${totalSteps}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-6)',
      }}
      className={className}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-primary)' }}>
          Step {currentStep} of {totalSteps}
        </span>
        {stepTitle && (
          <span className="text-secondary text-xs">{stepTitle}</span>
        )}
        <span className="text-secondary text-xs">{percentage}%</span>
      </div>

      <div
        style={{
          width: '100%',
          height: '6px',
          backgroundColor: '#E5E7EB',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${percentage}%`,
            height: '100%',
            backgroundColor: 'var(--color-primary)',
            transition: 'width 300ms ease-in-out',
          }}
        />
      </div>
    </div>
  );
};
