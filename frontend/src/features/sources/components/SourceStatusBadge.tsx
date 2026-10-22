import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface SourceStatusBadgeProps {
  status?: 'current' | 'superseded' | 'unknown';
  className?: string;
}

export const SourceStatusBadge: React.FC<SourceStatusBadgeProps> = ({
  status = 'unknown',
  className = '',
}) => {
  if (status === 'current') {
    return (
      <span className={`badge badge-green ${className}`}>
        <CheckCircle2 size={12} aria-hidden="true" />
        <span>In Force / Current</span>
      </span>
    );
  }

  if (status === 'superseded') {
    return (
      <span className={`badge badge-warning ${className}`}>
        <AlertTriangle size={12} aria-hidden="true" />
        <span>Superseded / Amended</span>
      </span>
    );
  }

  return (
    <span className={`badge badge-neutral ${className}`}>
      <HelpCircle size={12} aria-hidden="true" />
      <span>Status Unverified</span>
    </span>
  );
};
