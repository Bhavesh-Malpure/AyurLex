import React, { useState } from 'react';
import { Citation } from '../../../services/api-client';
import { CitationChip } from './CitationChip';
import { DisclaimerBanner } from '../../../components/legal/DisclaimerBanner';
import { useSession } from '../../session/sessionStore';
import { Printer, ThumbsUp, ThumbsDown, Copy, Check, Bookmark, BookmarkCheck, Volume2, VolumeX } from 'lucide-react';

export interface AnswerData {
  text?: string;
  isAbstained?: boolean;
  abstentionReason?: string;
  confidence?: 'high' | 'medium' | 'low';
  citations: Citation[];
  asOfDate?: string;
  jurisdiction?: 'india' | 'international';
  language?: string;
}

interface AnswerRendererProps {
  answer: AnswerData;
  onCitationClick?: (citation: Citation) => void;
  onRefineQuestion?: () => void;
  onEscalate?: () => void;
  className?: string;
}

export const AnswerRenderer: React.FC<AnswerRendererProps> = ({
  answer,
  onCitationClick,
  className = '',
}) => {
  const { showSources } = useSession();
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'helpful' | 'not_helpful' | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleToggleSpeech = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported in this browser.');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    if (!answer.text) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(answer.text);

    // Language detection for voice model
    if (answer.language === 'mr' || /[\u0900-\u097F]/.test(answer.text)) {
      utterance.lang = 'mr-IN';
    } else if (answer.language === 'hi') {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-IN';
    }

    utterance.rate = 0.95;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = () => {
    if (!answer.text) return;
    const fullText = `${answer.text}\n\nDisclaimer: Ayurlex provides information for research purposes and does not provide legal advice.`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrintPdf = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const sourcesHtml =
      answer.citations && answer.citations.length > 0
        ? `<h3>Verified Statutory Sources</h3>
           <ul>
             ${answer.citations
               .map(
                 (c) =>
                   `<li><strong>${c.title}</strong> ${c.locator ? `— ${c.locator}` : ''} (${c.jurisdiction.toUpperCase()})<br/><small>${c.sourceUrl || ''}</small></li>`
               )
               .join('')}
           </ul>`
        : '';

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Ayurlex Statutory Research Report</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 40px; color: #1F2937; line-height: 1.6; }
            .header { border-bottom: 2px solid #0F5132; padding-bottom: 12px; margin-bottom: 24px; }
            .header h1 { margin: 0; color: #0F5132; font-size: 24px; }
            .header p { margin: 4px 0 0; color: #6B7280; font-size: 13px; }
            .badge { display: inline-block; padding: 3px 8px; background: #E8F5EE; color: #0F5132; border-radius: 4px; font-size: 12px; font-weight: 600; margin-bottom: 16px; }
            .content { white-space: pre-line; font-size: 14px; margin-bottom: 30px; }
            .disclaimer { border-top: 1px solid #E5E7EB; padding-top: 16px; font-size: 12px; color: #6B7280; font-style: italic; }
            ul { padding-left: 20px; font-size: 13px; }
            li { margin-bottom: 8px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>🌿 Ayurlex Research Intelligence</h1>
            <p>Ayurveda Intellectual Property & Regulatory Compliance Report · Generated ${new Date().toLocaleDateString()}</p>
          </div>
          <div class="badge">Scope: ${answer.jurisdiction === 'international' ? 'International (WIPO/EPO)' : 'India (ASU/TKDL/BDA)'}</div>
          <div class="content">${answer.text || 'No substantive content.'}</div>
          ${sourcesHtml}
          <div class="disclaimer">
            <strong>Mandatory Legal Notice:</strong> Ayurlex provides information for research purposes and does not provide legal advice.
          </div>
          <script>
            window.onload = function() { window.print(); };
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  const handleBookmark = () => {
    try {
      const existing = JSON.parse(localStorage.getItem('ayurlex_bookmarks') || '[]');
      if (isBookmarked) {
        const filtered = existing.filter((item: any) => item.text !== answer.text);
        localStorage.setItem('ayurlex_bookmarks', JSON.stringify(filtered));
        setIsBookmarked(false);
      } else {
        existing.push({
          text: answer.text,
          date: new Date().toISOString(),
          jurisdiction: answer.jurisdiction,
        });
        localStorage.setItem('ayurlex_bookmarks', JSON.stringify(existing));
        setIsBookmarked(true);
      }
    } catch {
      setIsBookmarked(!isBookmarked);
    }
  };

  // If backend signaled abstention / insufficient evidence
  if (answer.isAbstained) {
    return (
      <div
        className={className}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)',
        }}
      >
        <div
          style={{
            fontSize: '0.95rem',
            lineHeight: 1.7,
            color: 'var(--color-text-primary)',
            whiteSpace: 'pre-line',
          }}
        >
          {answer.text || 'I could not verify a reliable answer from the available official research sources.'}
        </div>
        <DisclaimerBanner variant="inline" />
      </div>
    );
  }

  return (
    <article
      aria-label="Researched Legal Answer"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
      className={className}
    >
      {/* 1. Direct Researched Answer (with Key Points & Practical Next Steps if present) */}
      <div
        style={{
          fontSize: '0.95rem',
          lineHeight: 1.7,
          color: 'var(--color-text-primary)',
          whiteSpace: 'pre-line',
        }}
      >
        {answer.text || 'I could not verify a reliable answer from the available official research sources.'}
      </div>

      {/* 2. Optional Sources: only shown when user explicitly enables "Show Sources" setting */}
      {showSources && answer.citations && answer.citations.length > 0 && (
        <div
          style={{
            marginTop: 'var(--space-2)',
            padding: 'var(--space-3)',
            backgroundColor: 'var(--color-surface-alt)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border)',
          }}
        >
          <div
            style={{
              fontSize: '0.775rem',
              fontWeight: 600,
              color: 'var(--color-text-secondary)',
              marginBottom: 'var(--space-2)',
            }}
          >
            Official Research Sources ({answer.citations.length})
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {answer.citations.map((citation) => (
              <CitationChip
                key={citation.id}
                citation={citation}
                onClick={onCitationClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* 3. Action Toolbar: Copy, Export PDF, Bookmark, and Feedback */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-2)',
          paddingTop: 'var(--space-2)',
          borderTop: '1px dashed var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <button
            type="button"
            onClick={handleCopy}
            className="btn-ghost"
            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            title="Copy answer with legal disclaimer"
          >
            {copied ? <Check size={13} style={{ color: 'var(--color-primary)' }} /> : <Copy size={13} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            type="button"
            onClick={handlePrintPdf}
            className="btn-ghost"
            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            title="Export / Print research report (PDF)"
          >
            <Printer size={13} />
            <span>Export Report (PDF)</span>
          </button>

          <button
            type="button"
            onClick={handleBookmark}
            className="btn-ghost"
            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            title={isBookmarked ? 'Remove bookmark' : 'Bookmark this research answer'}
          >
            {isBookmarked ? <BookmarkCheck size={13} style={{ color: 'var(--color-primary)' }} /> : <Bookmark size={13} />}
            <span>{isBookmarked ? 'Saved' : 'Save'}</span>
          </button>

          <button
            type="button"
            onClick={handleToggleSpeech}
            className="btn-ghost"
            style={{
              fontSize: '0.75rem',
              padding: '0.2rem 0.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: isSpeaking ? 'var(--color-primary)' : 'inherit',
              fontWeight: isSpeaking ? 600 : 'normal',
            }}
            title={isSpeaking ? 'Stop audio readout' : 'Listen to answer (Text-to-Speech)'}
          >
            {isSpeaking ? <VolumeX size={13} style={{ color: 'var(--color-primary)' }} /> : <Volume2 size={13} />}
            <span>{isSpeaking ? 'Stop Audio' : 'Listen / ऑडिओ'}</span>
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span style={{ fontSize: '0.725rem', color: 'var(--color-text-tertiary)' }}>Helpful?</span>
          <button
            type="button"
            onClick={() => setFeedback('helpful')}
            className={`btn-ghost ${feedback === 'helpful' ? 'text-primary' : ''}`}
            style={{
              padding: '0.2rem 0.4rem',
              color: feedback === 'helpful' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            }}
            title="Helpful"
          >
            <ThumbsUp size={13} />
          </button>
          <button
            type="button"
            onClick={() => setFeedback('not_helpful')}
            className={`btn-ghost ${feedback === 'not_helpful' ? 'text-primary' : ''}`}
            style={{
              padding: '0.2rem 0.4rem',
              color: feedback === 'not_helpful' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            }}
            title="Needs improvement"
          >
            <ThumbsDown size={13} />
          </button>
        </div>
      </div>

      {/* 4. Mandatory Persistent Legal Disclaimer */}
      <DisclaimerBanner variant="inline" />
    </article>
  );
};
