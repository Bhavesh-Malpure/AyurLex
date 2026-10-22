import React from 'react';
import { CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';

export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'unverified';

interface ConfidenceBadgeProps {
  level?: ConfidenceLevel;
  className?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  level = 'unverified',
  className = '',
}) => {
  const configs: Record<
    ConfidenceLevel,
    { label: string; description: string; icon: React.ElementType; badgeClass: string }
  > = {
    high: {
      label: 'Statutorily Verified',
      description: 'Backed by direct statutory provisions or official Gazette notifications',
      icon: CheckCircle2,
      badgeClass: 'badge-green',
    },
    medium: {
      label: 'Secondary Authority',
      description: 'Supported by commentaries, interpretive guidelines, or secondary case law',
      icon: AlertCircle,
      badgeClass: 'badge-neutral',
    },
    low: {
      label: 'Preliminary Inference',
      description: 'Requires validation with specific patent claims or state licensing authority',
      icon: AlertCircle,
      badgeClass: 'badge-warning',
    },
    unverified: {
      label: 'Confidence Unspecified',
      description: 'Awaiting backend verification score',
      icon: HelpCircle,
      badgeClass: 'badge-neutral',
    },
  };

  const config = configs[level] || configs.unverified;
  const Icon = config.icon;

  return (
    <span
      className={`badge ${config.badgeClass} ${className}`}
      title={config.description}
      aria-label={`Confidence assessment: ${config.label}. ${config.description}`}
      style={{ cursor: 'help' }}
    >
      <Icon size={12} aria-hidden="true" />
      <span>{config.label}</span>
    </span>
  );
};
