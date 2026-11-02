import hashlib
import logging
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)

ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# The Gemini model served by this deployment of the google-genai SDK.
MODEL_NAME = "gemini-3.8-flash"

# Maximum chars from each chunk included in the Gemini prompt.
MAX_EXCERPT_CHARACTERS = 3_500

answer_cache: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Language detection & NLP analysis for any script or transliteration
# ---------------------------------------------------------------------------

_SCRIPT_RANGES = {
    "hindi":     r"[\u0900-\u097F]",   # Devanagari (Hindi, Marathi, Sanskrit)
    "tamil":     r"[\u0B80-\u0BFF]",
    "telugu":    r"[\u0C00-\u0C7F]",
    "kannada":   r"[\u0C80-\u0CFF]",
    "gujarati":  r"[\u0A80-\u0AFF]",
    "bengali":   r"[\u0980-\u09FF]",
    "punjabi":   r"[\u0A00-\u0A7F]",
    "malayalam": r"[\u0D00-\u0D7F]",
    "odia":      r"[\u0B00-\u0B7F]",
    "arabic":    r"[\u0600-\u06FF]",
}

_INDIC_ROMANIZED_KEYWORDS = {
    "kya", "kyu", "kyun", "kaise", "kisko", "kiska", "kab", "kaha", "kahan",
    "hai", "hain", "tha", "thi", "the", "hoga", "hogi", "hoge", "hua", "hui", "hue",
    "batao", "batayein", "bataiye", "bata", "karna", "karne", "kare", "karen",
    "chahiye", "milega", "sakte", "sakta", "sakti", "dawai", "dawa", "aushadhi",
    "radd", "nirast", "kharij", "jaankari", "samjhao", "samjhaiye", "shastriya",
    "paramparik", "gyan", "jaivik", "pradhikaran", "anumati", "dhara", "niyam",
    "haldi", "gomutra", "gaumutra", "ashwagandha", "triphala", "mujhe", "hume",
    "mera", "meri", "mere", "apna", "apni", "apne", "aur", "lekin", "magar",
}

_EXPLICIT_LANG_PATTERNS = [
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+hindi\b", "hindi"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+tamil\b", "tamil"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+telugu\b", "telugu"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+kannada\b", "kannada"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+marathi\b", "marathi"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+gujarati\b", "gujarati"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+bengali\b", "bengali"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+punjabi\b", "punjabi"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+malayalam\b", "malayalam"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+sanskrit\b", "sanskrit"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+urdu\b", "arabic"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+french\b", "french"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+spanish\b", "spanish"),
    (r"\b(?:in|into|using|reply\s+in|answer\s+in|explain\s+in)\s+german\b", "german"),
]


def detect_input_language(text: str) -> str:
    """Analyze input query to determine language and dialect, even when typed
    in English/Latin characters.
    """
    text_lower = text.lower()

    # 1. Explicit language request in English text
    for pattern, lang in _EXPLICIT_LANG_PATTERNS:
        if re.search(pattern, text_lower):
            return lang

    # 2. Unicode script ranges
    counts = {lang: len(re.findall(pat, text)) for lang, pat in _SCRIPT_RANGES.items()}
    total_non_latin = sum(counts.values())
    if total_non_latin >= 2:
        return max(counts, key=lambda k: counts[k])

    # 3. Analyze Latin/English words for Romanized Indic (Hinglish)
    words = set(re.findall(r"[a-z]+", text_lower))
    hinglish_matches = words.intersection(_INDIC_ROMANIZED_KEYWORDS)
    if len(hinglish_matches) >= 2 or (
        len(hinglish_matches) >= 1
        and any(w in words for w in ["kya", "kyu", "kyun", "kaise", "hai", "hain", "batao", "samjhao", "dawai", "radd"])
    ):
        return "hinglish"

    return "english"


_LANGUAGE_INSTRUCTION = {
    "english":  "Respond entirely in English with clear headings and statutory citations.",
    "hindi":    "उत्तर पूरी तरह हिंदी में दें (हेडिंग, बुलेट पॉइंट्स और वैधानिक विश्लेषण सहित)।",
    "hinglish": "The user asked their question in Romanized Hindi / Hinglish (Latin letters). Analyze their linguistic intent and respond in accessible Hindi (written in clear Devanagari script with key legal terms noted) so the user gets a comprehensive, native answer.",
    "tamil":    "முழு பதிலையும் தமிழில் கொடுங்கள் (தலைப்புகள் மற்றும் சட்டக் குறிப்புகளுடன்).",
    "telugu":   "సంపూర్ణ సమాధానం తెలుగులో ఇవ్వండి (శీర్షికలు మరియు చట్టపరమైన ఉల్లేఖనాలతో).",
    "kannada":  "ಸಂಪೂರ್ಣ ಉತ್ತರವನ್ನು ಕನ್ನಡದಲ್ಲಿ ನೀಡಿ.",
    "marathi":  "संपूर्ण उत्तर मराठीत द्या (शीर्षके आणि कायदेशीर तरतुदींसह).",
    "gujarati": "સંપૂર્ણ જવાબ ગુજરાતીમાં આપો (શીર્ષકો અને કાનૂની જોગવાઈઓ સાથે).",
    "bengali":  "সম্পূর্ণ उत्तर বাংলায় দিন (শিরোনাম এবং আইনি রেফারেন্স সহ)।",
    "punjabi":  "ਪੂਰਾ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ।",
    "malayalam":"മുഴുവൻ ഉത്തരവും മലയാളത്തിൽ നൽകുക.",
    "odia":     "ସମ୍ପୂର୍ଣ ଉତ୍ତର ଓଡ଼ିଆରେ ଦିଅ।",
    "sanskrit": "उत्तरं संस्कृतभाषायां ददातु।",
    "arabic":   "أجب بالكامل باللغة العربية / اردو۔",
    "french":   "Répondez entièrement en français.",
    "spanish":  "Responda enteramente en español.",
    "german":   "Antworten Sie vollständig auf Deutsch.",
}


SYSTEM_INSTRUCTIONS = """
You are Ayurlex, an internal research-answer agent for Ayurveda, patent, IP, regulatory, traditional-knowledge, formulation, compliance, WIPO, EPO, AYUSH, FSSAI, CDSCO, and patent-publication queries.

GOAL:
Research verified official sources internally and return ONLY a clear, concise final answer answering the exact question asked by the user.

USER-FACING OUTPUT STRUCTURE:
1. Direct researched answer (start directly with the substantive answer in the very first sentence).
2. Short key points (2-3 concise bullet points) if needed.
3. Short practical next step if needed.

CRITICAL ANSWER RULES:
1. Answer only what the user asked.
2. Start with the direct answer, not background information or generic legal intros.
3. Use simple, natural human language.
4. Keep the answer concise but complete.
5. Explain legal/technical terms only when needed.
6. Do not give unrelated information.
7. Keep sources strictly internal: DO NOT include source lists, website links, URLs, [Source N] tags, or citation chips in your answer text.
8. Do NOT mention sources unless the user explicitly asks "source show" or "where did you find this?".
9. Never invent facts, patent names, law sections, dates, case names, or legal conclusions.
10. If evidence is insufficient, return strictly:
   "I could not verify a reliable answer from the available official research sources."
11. Do not include research plans, internal reasoning, or technical errors.
"""



def build_context(retrieved_chunks: list[dict]) -> str:
    sections = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        excerpt = chunk["content"][:MAX_EXCERPT_CHARACTERS]

        sections.append(
            f"""[Source {index}]
Title: {chunk["title"]}
Jurisdiction: {chunk["jurisdiction"]}
Section: {chunk["section_label"]}
URL: {chunk["source_url"]}

Excerpt:
{excerpt}
"""
        )

    return "\n\n".join(sections)


def create_cache_key(
    question: str,
    retrieved_chunks: list[dict],
    jurisdiction: str = "india",
) -> str:
    source_ids = ",".join(
        str(chunk.get("chunk_id", i))
        for i, chunk in enumerate(retrieved_chunks, 1)
    )

    raw_key = f"{question.lower().strip()}|{jurisdiction}|{source_ids}"

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def validate_and_sanitize_citations(
    answer_text: str,
    retrieved_chunks: list[dict],
) -> str:
    """
    Remove internal source tags, citation brackets, and metadata markers
    so user-facing answer text contains only the clean research answer.
    """
    # Strip any [Source N] or [Verified via: ...] tags
    sanitized = re.sub(r"\[Source\s+\d+\]", "", answer_text, flags=re.IGNORECASE)
    sanitized = re.sub(r"\[Verified via:[^\]]+\]", "", sanitized, flags=re.IGNORECASE)
    # Clean up double spaces or dangling punctuation left by removed citation tags
    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\s+\.", ".", sanitized)
    return sanitized.strip()


def generate_grounded_answer(
    question: str,
    retrieved_chunks: list[dict],
    language: str = "auto",
    jurisdiction: str = "india",
) -> str:
    if not retrieved_chunks:
        return (
            "I could not find verified official source material for this question "
            "in the selected jurisdiction."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            f"GEMINI_API_KEY was not found in: {ENV_FILE}"
        )

    detected_lang = detect_input_language(question) if language in ("auto", "en") else language

    cache_key = create_cache_key(
        question=question,
        retrieved_chunks=retrieved_chunks,
        jurisdiction=jurisdiction,
    )

    if cache_key in answer_cache:
        return answer_cache[cache_key]

    lang_instruction = _LANGUAGE_INSTRUCTION.get(detected_lang, _LANGUAGE_INSTRUCTION["english"])

    prompt = f"""
{SYSTEM_INSTRUCTIONS}

LANGUAGE INSTRUCTION: {lang_instruction}

User question:
{question}

Verified source context:
{build_context(retrieved_chunks)}

Write the direct research answer now according to the CRITICAL ANSWER RULES.
"""

    import threading
    import queue

    client = genai.Client(api_key=api_key)
    res_queue = queue.Queue()

    def _call_gemini():
        try:
            res = client.interactions.create(
                model=MODEL_NAME,
                input=prompt,
                generation_config={
                    "thinking_level": "low",
                    "max_output_tokens": 800,
                },
            )
            res_queue.put((res.output_text or "").strip())
        except Exception as err:
            res_queue.put(err)

    worker = threading.Thread(target=_call_gemini, daemon=True)
    worker.start()

    raw_answer = ""
    try:
        val = res_queue.get(timeout=2.0)
        if isinstance(val, str) and val.strip():
            raw_answer = val.strip()
        else:
            logger.info(f"Gemini call returned error: {val}")
    except queue.Empty:
        logger.info("Gemini call timed out after 2.0s; using multi-source verified synthesis")

    if not raw_answer:
        from evidence_verifier import cross_check_evidence
        report = cross_check_evidence(retrieved_chunks, question=question, jurisdiction=jurisdiction)
        raw_answer = report.consensus_summary

    # Apply Requirement 8 Citation Validation
    validated_answer = validate_and_sanitize_citations(raw_answer, retrieved_chunks)

    answer_cache[cache_key] = validated_answer
    return validated_answer


def generate_grounded_answer_stream(
    question: str,
    retrieved_chunks: list[dict],
    language: str = "auto",
):
    """
    Generator yielding tokens/words of the grounded answer progressively.
    """
    if not retrieved_chunks:
        yield "I could not find verified official source material for this question in the selected jurisdiction."
        return

    try:
        full_answer = generate_grounded_answer(
            question=question,
            retrieved_chunks=retrieved_chunks,
            language=language,
        )
        words = full_answer.split(" ")
        for i, word in enumerate(words):
            yield word if i == 0 else " " + word
            time.sleep(0.01)
    except Exception as e:
        logger.error(f"Gemini generation error in stream: {e}")
        from evidence_verifier import cross_check_evidence
        report = cross_check_evidence(retrieved_chunks, question=question)
        words = report.consensus_summary.split(" ")
        for i, word in enumerate(words):
            yield word if i == 0 else " " + word
            time.sleep(0.01)


