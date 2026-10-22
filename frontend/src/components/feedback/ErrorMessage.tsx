import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  onReset?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Service Temporarily Unavailable',
  message = 'We could not complete your legal research query at this time. No confidential inquiry details have been compromised.',
  onRetry,
  onReset,
  className = '',
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        borderRadius: 'var(--radius-md)',
        backgroundColor: 'var(--color-error-bg)',
        border: '1px solid var(--color-error-border)',
        padding: 'var(--space-6)',
        color: '#7F1D1D',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
      className={className}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <AlertTriangle size={20} aria-hidden="true" style={{ color: 'var(--color-error)', flexShrink: 0 }} />
        <h4 style={{ color: '#991B1B', fontWeight: 600, margin: 0 }}>{title}</h4>
      </div>

      <p style={{ margin: 0, fontSize: '0.9rem', color: '#7F1D1D', lineHeight: 1.5 }}>
        {message}
      </p>

      {(onRetry || onReset) && (
        <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="btn btn-secondary"
              style={{
                fontSize: '0.8125rem',
                padding: '0.4rem 0.85rem',
                backgroundColor: 'var(--color-surface)',
                color: '#7F1D1D',
                borderColor: 'var(--color-error-border)',
              }}
            >
              <RefreshCw size={14} aria-hidden="true" />
              <span>Retry Query</span>
            </button>
          )}

          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="btn btn-ghost"
              style={{
                fontSize: '0.8125rem',
                padding: '0.4rem 0.85rem',
                color: '#7F1D1D',
              }}
            >
              <Home size={14} aria-hidden="true" />
              <span>Return Home</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
