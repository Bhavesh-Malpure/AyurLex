import { useState, useEffect } from 'react';
import { Jurisdiction, SupportedLanguage, SessionState, FormulationClassificationSummary } from './sessionTypes';

// Generate a random user session ID for research tracking (non-sensitive UUID-like token)
function generateSessionId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'sess_' + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
}

const INITIAL_STATE: SessionState = {
  sessionId: generateSessionId(),
  jurisdiction: 'india',
  language: 'en',
  isComparisonActive: false,
};

let currentState: SessionState = { ...INITIAL_STATE };
const listeners = new Set<(state: SessionState) => void>();

function notify() {
  listeners.forEach((listener) => listener(currentState));
}

export const sessionStore = {
  getState(): SessionState {
    return currentState;
  },

  setJurisdiction(jurisdiction: Jurisdiction) {
    currentState = { ...currentState, jurisdiction };
    notify();
  },

  setLanguage(language: SupportedLanguage) {
    currentState = { ...currentState, language };
    notify();
  },

  setComparisonActive(active: boolean) {
    currentState = { ...currentState, isComparisonActive: active };
    notify();
  },

  setClassificationContext(context: FormulationClassificationSummary) {
    currentState = { ...currentState, classificationContext: context };
    notify();
  },

  resetSession() {
    currentState = {
      ...INITIAL_STATE,
      sessionId: generateSessionId(),
      jurisdiction: currentState.jurisdiction,
      language: currentState.language,
    };
    notify();
  },

  subscribe(listener: (state: SessionState) => void): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};

export function useSession(): SessionState {
  const [state, setState] = useState<SessionState>(sessionStore.getState());

  useEffect(() => {
    return sessionStore.subscribe((newState) => {
      setState(newState);
    });
  }, []);

  return state;
}
