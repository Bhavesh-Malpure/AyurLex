import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { WizardQuestion, ClassificationQuestion } from './ClassificationQuestion';
import { ClassificationProgress } from './ClassificationProgress';
import { ClassificationSummary } from './ClassificationSummary';
import { ClassificationResult, ClassificationResultData } from './ClassificationResult';
import { sessionStore } from '../../session/sessionStore';

const CLASSIFICATION_QUESTIONS: WizardQuestion[] = [
  {
    id: 'classical_reference',
    title: 'Authoritative Text Inclusion',
    description: 'Is this exact formulation or recipe documented in any of the 54 books of the First Schedule to the Drugs & Cosmetics Act, 1940?',
    options: [
      {
        id: 'yes_classical',
        label: 'Yes, verbatim classical recipe',
        description: 'Appears in Charaka Samhita, Sushruta Samhita, Sharangadhara, or Ayurvedic Formulary of India (AFI)',
      },
      {
        id: 'modified_classical',
        label: 'Modified classical recipe',
        description: 'Derived from a classical base with altered ratio, additive exicipients, or modern dosage form',
      },
      {
        id: 'no_purely_novel',
        label: 'No, purely proprietary / novel formulation',
        description: 'Novel combination of herbal ingredients not described as an entity in the First Schedule texts',
      },
    ],
  },
  {
    id: 'ingredient_origin',
    title: 'ASU Botanical & Mineral Ingredients',
    description: 'Are all individual herbal and mineral ingredients listed in the Ayurvedic Pharmacopoeia of India (API)?',
    options: [
      {
        id: 'all_asu',
        label: 'All ingredients are recognized ASU botanicals',
        description: 'Complies strictly with Section 3(a) of the Drugs & Cosmetics Act',
      },
      {
        id: 'contains_non_asu',
        label: 'Contains non-ASU botanical or foreign extract',
        description: 'Includes non-indigenous plants or modern pharmaceutical excipients',
      },
    ],
  },
  {
    id: 'extraction_process',
    title: 'Extraction Method & Processing',
    description: 'What extraction technique and solvent are utilized for manufacturing?',
    options: [
      {
        id: 'traditional_aqueous',
        label: 'Traditional aqueous processing (Kwatha, Asava, Arishta, Taila)',
        description: 'Standard classical processing according to AFI pharmaceutical norms',
      },
      {
        id: 'modern_hydroalcoholic',
        label: 'Standardized hydro-alcoholic or specialized solvent extract',
        description: 'Targeted enriched fractions with specific marker compound quantification',
      },
    ],
  },
  {
    id: 'therapeutic_indications',
    title: 'Therapeutic Claims & Target Indication',
    description: 'Are therapeutic claims restricted to textual indications or novel indications?',
    options: [
      {
        id: 'textual_claims',
        label: 'Strictly classical therapeutic indications (Rogadhikara)',
        description: 'No novel or modern disease claims beyond textual citations',
      },
      {
        id: 'novel_indication',
        label: 'Novel disease indication or modernized clinical claim',
        description: 'E.g., targeted anti-diabetic adjuvant, modern neuro-protection, or oncological support',
      },
    ],
  },
  {
    id: 'rasashastra_minerals',
    title: 'Metallic / Mineral Bhasma Components',
    description: 'Does the formulation contain Shodhita Parada, Gandhak, or heavy metal Bhasmas?',
    options: [
      {
        id: 'herbal_only',
        label: 'Purely Kashtoushadhi (Herbal / Botanical only)',
        description: 'No heavy metals, minerals, or animal-derived ingredients',
      },
      {
        id: 'contains_bhasma',
        label: 'Contains Rasaushadhi / Mineral Bhasma',
        description: 'Requires Schedule E(1) toxicity testing and AFI heavy metal limit compliance',
      },
    ],
  },
];

interface ClassificationWizardProps {
  onNavigateToResearch: (category: string) => void;
  className?: string;
}

export const ClassificationWizard: React.FC<ClassificationWizardProps> = ({
  onNavigateToResearch,
  className = '',
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isReviewing, setIsReviewing] = useState(false);
  const [result, setResult] = useState<ClassificationResultData | null>(null);

  const totalQuestions = CLASSIFICATION_QUESTIONS.length;
  const currentQuestion = CLASSIFICATION_QUESTIONS[currentStepIndex];

  const handleSelectOption = (optionId: string) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionId,
    }));
  };

  const handleNext = () => {
    if (currentStepIndex < totalQuestions - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    } else {
      setIsReviewing(true);
    }
  };

  const handleBack = () => {
    if (isReviewing) {
      setIsReviewing(false);
    } else if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  };

  const handleGenerateResult = () => {
    // Determine category based on statutory rules
    const isClassical = answers.classical_reference === 'yes_classical';
    const isTraditionalProcess = answers.extraction_process === 'traditional_aqueous';
    const isTextualClaims = answers.therapeutic_indications === 'textual_claims';

    let category = 'Ayurvedic Proprietary Medicine (Rule 158B)';
    let regulatorySubtype = 'Section 3(h) ASU Proprietary Drug';
    let patentability = 'Patentable novel formulation if synergy is proved under Section 3(e). Not barred by 3(p) if novel active fraction.';
    let legalBasis = 'Governed by Rule 158B(IV) of Drugs and Cosmetics Rules, 1945. Requires safety data and published literature.';
    const rules = [
      'Drugs and Cosmetics Act, 1940: Section 3(a) & 3(h)',
      'Drugs and Cosmetics Rules, 1945: Rule 158B (Proof of effectiveness for ASU drugs)',
      'Indian Patent Act, 1970: Section 3(p) Traditional Knowledge Bar & Section 3(e) Admixture Synergy',
    ];

    if (isClassical && isTraditionalProcess && isTextualClaims) {
      category = 'Classical ASU Formulation (First Schedule)';
      regulatorySubtype = 'Section 3(a) Classical Ayurvedic Drug';
      patentability = 'Strictly barred under Indian Patent Act Section 3(p). Documented in Traditional Knowledge Digital Library (TKDL).';
      legalBasis = 'Manufactured strictly in accordance with authoritative texts of the First Schedule. Exempt from clinical trial requirement under Rule 158B(I).';
      rules.push('TKDL Prior Art Citations: Searchable across classical texts');
    }

    const calculatedResult: ClassificationResultData = {
      category,
      regulatorySubtype,
      patentabilityStatus: patentability,
      legalBasis,
      requiredClinicalEvidence: isClassical ? 'Textual reference proof only (AFI/API)' : 'Rule 158B safety study or published scientific evidence',
      statutoryRules: rules,
    };

    setResult(calculatedResult);

    // Save into session store
    sessionStore.setClassificationContext({
      hasClassicalReference: isClassical,
      containsHeavyMetals: answers.rasashastra_minerals === 'contains_bhasma',
      innovativeProcess: !isTraditionalProcess,
      targetCategory: category,
      notes: `Evaluated under Section 3(p) and Rule 158B.`,
    });
  };

  const handleRestart = () => {
    setAnswers({});
    setCurrentStepIndex(0);
    setIsReviewing(false);
    setResult(null);
  };

  return (
    <div className={`container-narrow ${className}`} style={{ padding: 'var(--space-8) var(--space-4)' }}>
      {/* If result is ready */}
      {result ? (
        <ClassificationResult
          result={result}
          onRestart={handleRestart}
          onExploreResearch={onNavigateToResearch}
        />
      ) : isReviewing ? (
        /* Summary Step (F17) */
        <div>
          <ClassificationProgress currentStep={totalQuestions} totalSteps={totalQuestions} stepTitle="Review & Confirm" />
          <ClassificationSummary
            questions={CLASSIFICATION_QUESTIONS}
            answers={answers}
            onEditStep={(idx) => {
              setCurrentStepIndex(idx);
              setIsReviewing(false);
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'var(--space-6)' }}>
            <button type="button" onClick={handleBack} className="btn btn-secondary">
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>

            <button type="button" onClick={handleGenerateResult} className="btn btn-primary">
              <span>Generate Statutory Assessment</span>
              <Check size={16} />
            </button>
          </div>
        </div>
      ) : (
        /* Individual Question Step (F13, F14, F15, F16) */
        <div>
          <ClassificationProgress
            currentStep={currentStepIndex + 1}
            totalSteps={totalQuestions}
            stepTitle={currentQuestion.title}
          />

          <ClassificationQuestion
            question={currentQuestion}
            selectedOptionId={answers[currentQuestion.id]}
            onSelectOption={handleSelectOption}
          />

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: 'var(--space-6)',
            }}
          >
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStepIndex === 0}
              className="btn btn-secondary"
            >
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>

            <button
              type="button"
              onClick={handleNext}
              disabled={!answers[currentQuestion.id]}
              className="btn btn-primary"
            >
              <span>{currentStepIndex === totalQuestions - 1 ? 'Review Summary' : 'Continue'}</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
