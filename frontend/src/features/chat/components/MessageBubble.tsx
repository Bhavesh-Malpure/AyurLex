import React from 'react';
import { User, Sparkles } from 'lucide-react';
import { AnswerRenderer, AnswerData } from '../../answers/components/AnswerRenderer';
import { Citation } from '../../../services/api-client';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  text?: string;
  answerData?: AnswerData;
}

interface MessageBubbleProps {
  message: ChatMessage;
  onCitationClick?: (citation: Citation) => void;
  onRefineQuestion?: () => void;
  onEscalate?: () => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onCitationClick,
  onRefineQuestion,
  onEscalate,
}) => {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'flex-end',
          margin: 'var(--space-3) 0',
        }}
      >
        <div
          style={{
            maxWidth: '85%',
            display: 'flex',
            gap: 'var(--space-2)',
            alignItems: 'flex-start',
          }}
        >
          <div
            style={{
              backgroundColor: 'var(--color-primary)',
              color: 'var(--color-text-inverse)',
              padding: 'var(--space-3) var(--space-4)',
              borderRadius: 'var(--radius-lg) var(--radius-lg) 2px var(--radius-lg)',
              fontSize: '0.95rem',
              lineHeight: 1.5,
              wordBreak: 'break-word',
            }}
          >
            {message.text}
          </div>
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--color-soft-green)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
            aria-hidden="true"
          >
            <User size={15} />
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'flex-start',
        margin: 'var(--space-4) 0',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '920px',
          display: 'flex',
          gap: 'var(--space-3)',
          alignItems: 'flex-start',
        }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-soft-green)',
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginTop: '2px',
          }}
          aria-hidden="true"
        >
          <Sparkles size={17} />
        </div>

        <div
          className="card"
          style={{
            flex: 1,
            padding: 'var(--space-6)',
            borderRadius: 'var(--radius-lg)',
          }}
        >
          {message.answerData ? (
            <AnswerRenderer
              answer={message.answerData}
              onCitationClick={onCitationClick}
              onRefineQuestion={onRefineQuestion}
              onEscalate={onEscalate}
            />
          ) : (
            <p>{message.text}</p>
          )}
        </div>
      </div>
    </div>
  );
};
