import React from 'react';
import { PlusCircle, RotateCcw, SplitSquareVertical } from 'lucide-react';
import { sessionStore } from '../../session/sessionStore';

interface HistoryToolbarProps {
  onNewSession: () => void;
  onToggleComparison: () => void;
  isComparisonActive: boolean;
  className?: string;
}

export const HistoryToolbar: React.FC<HistoryToolbarProps> = ({
  onNewSession,
  onToggleComparison,
  isComparisonActive,
  className = '',
}) => {
  const handleNewResearch = () => {
    sessionStore.resetSession();
    onNewSession();
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-2)',
        padding: 'var(--space-2) 0',
      }}
      className={className}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <button
          type="button"
          onClick={handleNewResearch}
          className="btn btn-secondary"
          style={{ fontSize: '0.8125rem', padding: '0.35rem 0.75rem' }}
          title="Create a new research inquiry session"
        >
          <PlusCircle size={14} style={{ color: 'var(--color-primary)' }} />
          <span>New Research Session</span>
        </button>

        <button
          type="button"
          onClick={onToggleComparison}
          className={`btn ${isComparisonActive ? 'btn-primary' : 'btn-secondary'}`}
          style={{ fontSize: '0.8125rem', padding: '0.35rem 0.75rem' }}
          title="Compare statutory provisions between India and International jurisdictions"
        >
          <SplitSquareVertical size={14} />
          <span>{isComparisonActive ? 'Close Comparison' : 'Compare Jurisdictions'}</span>
        </button>
      </div>

      <button
        type="button"
        onClick={handleNewResearch}
        className="btn btn-ghost"
        style={{ fontSize: '0.775rem', padding: '0.35rem 0.5rem', color: 'var(--color-text-tertiary)' }}
        title="Reset conversation state"
      >
        <RotateCcw size={12} />
        <span>Reset State</span>
      </button>
    </div>
  );
};
