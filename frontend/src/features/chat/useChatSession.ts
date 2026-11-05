import { useState, useCallback } from 'react';
import { ChatMessage } from './components/MessageBubble';
import { apiClient, Citation } from '../../services/api-client';
import { ResearchStage } from './components/ChatStatus';
import { useSession } from '../session/sessionStore';

export function useChatSession() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [stage, setStage] = useState<ResearchStage>('idle');
  const [errorMessage, setErrorMessage] = useState<string | undefined>();
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [isCitationDialogOpen, setIsCitationDialogOpen] = useState(false);

  const { jurisdiction, language, sessionId } = useSession();

  const openCitation = useCallback((citation: Citation) => {
    setSelectedCitation(citation);
    setIsCitationDialogOpen(true);
  }, []);

  const closeCitation = useCallback(() => {
    setIsCitationDialogOpen(false);
    setSelectedCitation(null);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        sender: 'user',
        timestamp: new Date().toISOString(),
        text,
      };

      const asstMessageId = `asst_${Date.now() + 1}`;
      let accumulatedText = '';
      let receivedCitations: Citation[] = [];

      setMessages((prev) => [...prev, userMessage]);
      setStage('searching');
      setErrorMessage(undefined);

      try {
        // Attempt progressive SSE streaming first
        await apiClient.streamResearchQuery(
          {
            question: text,
            jurisdiction,
            language,
            sessionId,
            responseMode: 'fast',
          },
          {
            onStatus: (stg) => {
              if (stg === 'researching_sources') setStage('searching');
              else if (stg === 'generating_detailed_answer') setStage('analyzing');
            },
            onFastAnswer: (data) => {
              accumulatedText = data.summary;
              receivedCitations = data.sources || [];

              setMessages((prev) => {
                const filtered = prev.filter((m) => m.id !== asstMessageId);
                return [
                  ...filtered,
                  {
                    id: asstMessageId,
                    sender: 'assistant',
                    timestamp: new Date().toISOString(),
                    answerData: {
                      text: accumulatedText,
                      citations: receivedCitations,
                      confidence: data.confidence as any,
                      isAbstained: data.isAbstained,
                      jurisdiction,
                      language,
                      asOfDate: 'Gazette of India (2024)',
                    },
                  },
                ];
              });
            },
            onToken: (token) => {
              accumulatedText += token;
              setMessages((prev) => {
                const filtered = prev.filter((m) => m.id !== asstMessageId);
                return [
                  ...filtered,
                  {
                    id: asstMessageId,
                    sender: 'assistant',
                    timestamp: new Date().toISOString(),
                    answerData: {
                      text: accumulatedText,
                      citations: receivedCitations,
                      confidence: 'high',
                      isAbstained: false,
                      jurisdiction,
                      language,
                      asOfDate: 'Gazette of India (2024)',
                    },
                  },
                ];
              });
            },
            onComplete: (data) => {
              setMessages((prev) => {
                const filtered = prev.filter((m) => m.id !== asstMessageId);
                return [
                  ...filtered,
                  {
                    id: asstMessageId,
                    sender: 'assistant',
                    timestamp: new Date().toISOString(),
                    answerData: {
                      text: data.answer || accumulatedText,
                      citations: data.sources.length > 0 ? data.sources : receivedCitations,
                      confidence: data.confidence,
                      isAbstained: data.isAbstained,
                      jurisdiction,
                      language,
                      asOfDate: 'Gazette of India (2024)',
                    },
                  },
                ];
              });
              setStage('idle');
            },
            onError: (err) => {
              throw err;
            },
          }
        );
      } catch (streamErr) {
        // Fallback to standard HTTP POST /query if streaming encounters any network issue
        console.warn('Streaming blip, falling back to synchronous /query:', streamErr);
        try {
          const response = await apiClient.submitResearchQuery({
            question: text,
            jurisdiction,
            language,
            sessionId,
          });

          const assistantMessage: ChatMessage = {
            id: asstMessageId,
            sender: 'assistant',
            timestamp: new Date().toISOString(),
            answerData: {
              text: response.answer || 'I could not verify a reliable answer from the available official research sources.',
              confidence: response.confidence || 'medium',
              isAbstained: response.is_abstained || false,
              citations: response.citations,
              jurisdiction,
              language,
              asOfDate: 'Gazette of India (2024)',
            },
          };

          setMessages((prev) => {
            const filtered = prev.filter((m) => m.id !== asstMessageId);
            return [...filtered, assistantMessage];
          });
          setStage('idle');
        } catch (fetchErr: any) {
          setStage('error');
          setErrorMessage(
            fetchErr?.message?.includes('fetch') || fetchErr?.message?.includes('network')
              ? 'FastAPI backend server is currently unreachable on localhost:8000. Start it by running: npm run backend'
              : 'An error occurred while evaluating statutory sources. Please try again.'
          );
        }
      }
    },
    [jurisdiction, language, sessionId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setStage('idle');
    setErrorMessage(undefined);
  }, []);

  return {
    messages,
    stage,
    errorMessage,
    selectedCitation,
    isCitationDialogOpen,
    sendMessage,
    openCitation,
    closeCitation,
    clearMessages,
  };
}
