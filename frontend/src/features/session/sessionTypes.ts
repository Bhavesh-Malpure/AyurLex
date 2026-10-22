export type Jurisdiction = 'india' | 'international';
export type SupportedLanguage = 'en' | 'hi';

export interface FormulationClassificationSummary {
  hasClassicalReference?: boolean;
  containsHeavyMetals?: boolean;
  innovativeProcess?: boolean;
  targetCategory?: string;
  notes?: string;
}

export interface SessionState {
  sessionId: string;
  jurisdiction: Jurisdiction;
  language: SupportedLanguage;
  classificationContext?: FormulationClassificationSummary;
  isComparisonActive: boolean;
}
