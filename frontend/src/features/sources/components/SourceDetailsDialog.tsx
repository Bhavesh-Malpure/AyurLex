import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { Citation } from '../../../services/api-client';
import { SourceDetailsPanel } from './SourceDetailsPanel';

interface SourceDetailsDialogProps {
  citation: Citation | null;
  isOpen: boolean;
  onClose: () => void;
}

export const SourceDetailsDialog: React.FC<SourceDetailsDialogProps> = ({
  citation,
  isOpen,
  onClose,
}) => {
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeBtnRef.current?.focus();
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen || !citation) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="source-dialog-title"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        backgroundColor: 'rgba(15, 30, 20, 0.45)',
        backdropFilter: 'blur(2px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-4)',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '620px',
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: 'var(--color-surface)',
          padding: 'var(--space-6)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-modal)',
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
          <h2 id="source-dialog-title" style={{ fontSize: '1.25rem', margin: 0 }}>
            Source Verification Details
          </h2>
          <button
            ref={closeBtnRef}
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="btn-icon"
          >
            <X size={20} />
          </button>
        </div>

        <SourceDetailsPanel citation={citation} onClose={onClose} />
      </div>
    </div>
  );
};
