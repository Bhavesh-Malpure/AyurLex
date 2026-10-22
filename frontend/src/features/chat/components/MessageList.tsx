import React, { useRef, useEffect } from 'react';
import { BookOpen, Sparkles } from 'lucide-react';
import { MessageBubble, ChatMessage } from './MessageBubble';
import { Citation } from '../../../services/api-client';

interface MessageListProps {
  messages: ChatMessage[];
  onCitationClick?: (citation: Citation) => void;
  onRefineQuestion?: () => void;
  onEscalate?: () => void;
  onSuggestedQueryClick?: (query: string) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  onCitationClick,
  onRefineQuestion,
  onEscalate,
  onSuggestedQueryClick,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  if (messages.length === 0) {
    const suggestedQueries = [
      'Is Ashwagandha extract patentable under Indian Patent Act Section 3(p)?',
      'What are the mandatory Rule 158B clinical requirements for classical ASU formulations?',
      'Does European Patent Office allow patents on Curcumin-piperine synergistic combinations?',
      'How does the Biological Diversity Act 2002 impact foreign commercial utilization of Neem?',
    ];

    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 'var(--space-12) var(--space-4)',
          textAlign: 'center',
          minHeight: '380px',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--color-soft-green)',
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 'var(--space-4)',
          }}
        >
          <BookOpen size={24} aria-hidden="true" />
        </div>

        <h3 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-2)' }}>
          Ayurlex Legal & IPR Workspace
        </h3>
        <p className="text-secondary" style={{ maxWidth: '500px', marginBottom: 'var(--space-6)', fontSize: '0.9rem' }}>
          Ask any question regarding Ayurvedic patentability, prior art scrutiny, ASU regulatory rules, or statutory citations.
        </p>

        <div style={{ width: '100%', maxWidth: '650px', textAlign: 'left' }}>
          <div style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>
            Suggested Research Inquiries:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-2)' }}>
            {suggestedQueries.map((query, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSuggestedQueryClick?.(query)}
                className="btn btn-secondary"
                style={{
                  justifyContent: 'flex-start',
                  textAlign: 'left',
                  fontSize: '0.825rem',
                  padding: '0.6rem 0.85rem',
                  lineHeight: 1.4,
                  whiteSpace: 'normal',
                }}
              >
                <Sparkles size={14} style={{ color: 'var(--color-secondary)', flexShrink: 0 }} />
                <span>{query}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      role="log"
      aria-label="Conversation message history"
      style={{
        display: 'flex',
        flexDirection: 'column',
        padding: 'var(--space-4) 0',
      }}
    >
      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          onCitationClick={onCitationClick}
          onRefineQuestion={onRefineQuestion}
          onEscalate={onEscalate}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
};
