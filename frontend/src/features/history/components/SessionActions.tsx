import React, { useState } from 'react';
import { Trash2, AlertCircle } from 'lucide-react';

interface SessionActionsProps {
  onClearLocalHistory: () => void;
  className?: string;
}

export const SessionActions: React.FC<SessionActionsProps> = ({
  onClearLocalHistory,
  className = '',
}) => {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleConfirmClear = () => {
    onClearLocalHistory();
    setShowConfirm(false);
  };

  return (
    <div className={className}>
      {!showConfirm ? (
        <button
          type="button"
          onClick={() => setShowConfirm(true)}
          className="btn btn-ghost"
          style={{ fontSize: '0.8rem', color: '#991B1B' }}
        >
          <Trash2 size={13} />
          <span>Clear Local Session Messages</span>
        </button>
      ) : (
        <div
          style={{
            padding: 'var(--space-3)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: '#FEE2E2',
            border: '1px solid #FECACA',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-2)',
            fontSize: '0.8rem',
            color: '#7F1D1D',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <AlertCircle size={14} />
            <strong>Clear Local Session View?</strong>
          </div>
          <p style={{ margin: 0, fontSize: '0.775rem', lineHeight: 1.4 }}>
            This clears active conversation messages from your current browser window. (Note: No server-side deletion is triggered).
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: '4px' }}>
            <button
              type="button"
              onClick={handleConfirmClear}
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', color: '#991B1B', borderColor: '#FECACA' }}
            >
              Yes, Clear View
            </button>
            <button
              type="button"
              onClick={() => setShowConfirm(false)}
              className="btn btn-ghost"
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
