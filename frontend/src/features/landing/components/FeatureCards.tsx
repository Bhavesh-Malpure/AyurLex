import React from 'react';
import {
  FileCheck2,
  BookmarkCheck,
  MapPin,
  Scale,
  Library,
  ArrowUpRight,
} from 'lucide-react';

interface FeatureCardItem {
  id: string;
  title: string;
  description: string;
  badge: string;
  icon: React.ElementType;
  routeTarget: string;
}

interface FeatureCardsProps {
  onSelectFeature?: (route: string) => void;
}

export const FeatureCards: React.FC<FeatureCardsProps> = ({ onSelectFeature }) => {
  const cards: FeatureCardItem[] = [
    {
      id: 'patents',
      title: 'Patentability & Prior Art',
      description:
        'Analyze novelty hurdles under Indian Patent Act Section 3(p) and Section 3(d), evaluating claims against traditional knowledge databases.',
      badge: 'Section 3(p) Scrutiny',
      icon: FileCheck2,
      routeTarget: 'research',
    },
    {
      id: 'regulatory',
      title: 'ASU Regulatory Compliance',
      description:
        'Classify formulations under Drugs & Cosmetics Act Rules 158B and Schedule T Good Manufacturing Practices (GMP).',
      badge: 'Drugs & Cosmetics Act',
      icon: Scale,
      routeTarget: 'classification',
    },
    {
      id: 'tkdl',
      title: 'Traditional Knowledge & TKDL',
      description:
        'Identify documented Ayurvedic formulations across authoritative texts to prevent wrongful misappropriation and bio-piracy.',
      badge: 'TKDL Reference Map',
      icon: Library,
      routeTarget: 'compliance',
    },
    {
      id: 'gi',
      title: 'Geographical Indications (GI)',
      description:
        'Assess regional botanical authenticity, origin certificates, and indigenous herbal cultivar protection under GI Law.',
      badge: 'Herbal Cultivars',
      icon: MapPin,
      routeTarget: 'research',
    },
    {
      id: 'trademarks',
      title: 'Trademarks & Botanical Names',
      description:
        'Verify brand names against descriptive medicinal Sanskrit terminology and non-proprietary ingredient restrictions.',
      badge: 'Nomenclature Clearance',
      icon: BookmarkCheck,
      routeTarget: 'research',
    },
  ];

  return (
    <section
      aria-labelledby="features-title"
      style={{
        padding: 'var(--space-12) 0',
      }}
    >
      <div className="container-wide">
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <span className="badge badge-green" style={{ marginBottom: 'var(--space-2)' }}>
            Core Research Domains
          </span>
          <h2 id="features-title" style={{ marginBottom: 'var(--space-2)' }}>
            Specialized Ayurvedic Intellectual Property Intelligence
          </h2>
          <p className="text-secondary" style={{ maxWidth: '600px', margin: '0 auto' }}>
            Structured cross-referencing between statutory legal frameworks, pharmacological authorities, and global IP conventions.
          </p>
        </div>

        {/* 5-card responsive grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 'var(--space-4)',
          }}
        >
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.id}
                className="card card-clickable"
                tabIndex={0}
                role="button"
                onClick={() => onSelectFeature?.(card.routeTarget)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectFeature?.(card.routeTarget);
                  }
                }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%',
                }}
              >
                <div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: 'var(--space-4)',
                    }}
                  >
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: 'var(--radius-md)',
                        backgroundColor: 'var(--color-soft-green)',
                        color: 'var(--color-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Icon size={20} aria-hidden="true" />
                    </div>
                    <span className="badge badge-neutral text-xs">{card.badge}</span>
                  </div>

                  <h3 style={{ marginBottom: 'var(--space-2)', fontSize: '1.05rem' }}>
                    {card.title}
                  </h3>

                  <p
                    className="text-secondary"
                    style={{ fontSize: '0.875rem', lineHeight: 1.6 }}
                  >
                    {card.description}
                  </p>
                </div>

                <div
                  style={{
                    marginTop: 'var(--space-6)',
                    paddingTop: 'var(--space-3)',
                    borderTop: '1px solid var(--color-border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '0.8125rem',
                    color: 'var(--color-secondary)',
                    fontWeight: 500,
                  }}
                >
                  <span>Explore domain</span>
                  <ArrowUpRight size={16} aria-hidden="true" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
