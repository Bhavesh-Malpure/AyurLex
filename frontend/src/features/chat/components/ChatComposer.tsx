import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft } from 'lucide-react';
import { useSession } from '../../session/sessionStore';

interface ChatComposerProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  className?: string;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSendMessage,
  isLoading,
  placeholder,
  className = '',
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { language, jurisdiction } = useSession();

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const defaultPlaceholder =
    language === 'hi'
      ? 'आयुर्वेदिक सूत्रीकरण, पेटेंट, धारा ३(प), या औषधि और प्रसाधन सामग्री अधिनियम के बारे में पूछें...'
      : `Ask about Ayurvedic patentability (Sec 3p/3d), classical formulation references, or ${
          jurisdiction === 'india' ? 'Indian ASU rules' : 'international IPR conventions'
        }...`;

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        position: 'relative',
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-card)',
        padding: 'var(--space-2) var(--space-3)',
        transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
      }}
      className={`chat-composer ${className}`}
    >
      <label htmlFor="research-query-input" className="visually-hidden" style={{ position: 'absolute', width: 1, height: 1, padding: 0, margin: -1, overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', border: 0 }}>
        Research Query Input
      </label>

      <textarea
        id="research-query-input"
        ref={textareaRef}
        rows={2}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || defaultPlaceholder}
        disabled={isLoading}
        aria-label="Enter your legal or Ayurvedic research question"
        style={{
          width: '100%',
          border: 'none',
          outline: 'none',
          resize: 'none',
          fontSize: '0.95rem',
          lineHeight: 1.5,
          color: 'var(--color-text-primary)',
          backgroundColor: 'transparent',
          padding: 'var(--space-2) 0',
        }}
      />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: 'var(--space-2)',
          borderTop: '1px solid var(--color-border-subtle)',
          marginTop: 'var(--space-1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span className="text-secondary text-xs" style={{ display: 'none', alignItems: 'center', gap: '2px' }} id="helper-shortcut">
            Press <kbd style={{ padding: '1px 4px', background: '#f3f4f6', borderRadius: '3px', fontSize: '11px' }}>Enter</kbd> <CornerDownLeft size={11} /> to send
          </span>
          <span className="badge badge-neutral text-xs">
            {jurisdiction === 'india' ? 'India Scoped' : 'International Scoped'}
          </span>
        </div>

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="btn btn-primary"
          aria-label="Send research query"
          style={{
            padding: '0.45rem 1rem',
            fontSize: '0.875rem',
            borderRadius: 'var(--radius-md)',
          }}
        >
          <span>Send</span>
          <Send size={14} aria-hidden="true" />
        </button>
      </div>

      <style>{`
        @media (min-width: 640px) {
          #helper-shortcut { display: inline-flex !important; }
        }
      `}</style>
    </form>
  );
};
