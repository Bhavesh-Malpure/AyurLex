import React from 'react';
import { Compass, Globe } from 'lucide-react';
import { useSession } from '../../session/sessionStore';

interface JurisdictionStatusProps {
  className?: string;
  showDetails?: boolean;
}

export const JurisdictionStatus: React.FC<JurisdictionStatusProps> = ({
  className = '',
  showDetails = false,
}) => {
  const { jurisdiction } = useSession();
  const isIndia = jurisdiction === 'india';

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        fontSize: '0.8125rem',
      }}
      className={className}
      aria-label={`Active research jurisdiction: ${isIndia ? 'India (Domestic Acts & Rules)' : 'International (Global IPR)'}`}
    >
      <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
        {isIndia ? <Compass size={13} aria-hidden="true" /> : <Globe size={13} aria-hidden="true" />}
        <span>{isIndia ? 'India (Domestic ASU)' : 'International (Global IPR)'}</span>
      </span>
      {showDetails && (
        <span className="text-secondary text-xs">
          {isIndia
            ? 'Scoped to Indian Patent Act (Sec 3p/3d), TKDL, Drugs & Cosmetics Act, and Biological Diversity Act.'
            : 'Scoped to WIPO, USPTO, EPO, and international patent clearance databases.'}
        </span>
      )}
    </div>
  );
};
