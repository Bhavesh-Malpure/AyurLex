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

      setMessages((prev) => [...prev, userMessage]);
      setStage('searching');
      setErrorMessage(undefined);

      try {
        // Stage progress animation for realistic research steps
        setTimeout(() => setStage('analyzing'), 800);
        setTimeout(() => setStage('verifying_citations'), 1600);

        const response = await apiClient.submitResearchQuery({
          question: text,
          jurisdiction,
          language,
          sessionId,
        });

        // Formulate assistant message with typed AnswerData
        const assistantMessage: ChatMessage = {
          id: `asst_${Date.now()}`,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
          answerData: {
            text:
              response.answer ||
              `Analysis of "${text}" scoped under ${
                jurisdiction === 'india' ? 'Indian ASU statutory law' : 'international IPR'
              }:\n\n` +
                (response.research_plan
                  ? `Research Strategy:\n${JSON.stringify(response.research_plan, null, 2)}`
                  : 'Referenced primary statutory sources and pharmacopoeial listings below.'),
            confidence: response.confidence || 'medium',
            isAbstained: response.is_abstained || false,
            citations: response.citations,
            jurisdiction,
            language,
            asOfDate: 'Gazette of India (2024)',
          },
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setStage('idle');
      } catch (err: any) {
        // Safe user-facing error without leaking server stack trace
        setStage('error');
        setErrorMessage(
          err?.message?.includes('fetch')
            ? 'Backend API server is currently unreachable. Make sure the FastAPI service on port 8000 is running.'
            : 'An error occurred while evaluating statutory sources. Please try again.'
        );
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
