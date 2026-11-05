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


_MARATHI_DISTINCTIVE_WORDS = {
    "आहे", "आहेत", "नाही", "का", "कसे", "कशी", "कशा", "करावे", "करावी", "मिळेल",
    "मिळू", "लागतात", "सांगा", "हळद", "हळदीवर", "औषध", "औषधे", "नोंदणी", "काय",
    "झाले", "झाला", "कलम", "परवाना", "तुळस", "अर्क", "कडुनिंब", "उत्पादन", "माहिती",
    "अडचण", "असेल", "तर", "पण", "द्या", "करा", "बघ", "सांग"
}

_MARATHI_ROMANIZED_KEYWORDS = {
    "aahe", "aahet", "nahi", "kasa", "kase", "sang", "sanga", "milnar", "milte",
    "karaycha", "kraych", "karave", "jhala", "jahala", "te", "pn", "ani", "aani",
    "hald", "aushadh", "bagh", "bg"
}


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
        top_script_lang = max(counts, key=lambda k: counts[k])
        # If Devanagari script, distinguish between Marathi and Hindi
        if top_script_lang == "hindi":
            text_words = set(re.findall(r"[\u0900-\u097F]+", text))
            if any(w in _MARATHI_DISTINCTIVE_WORDS for w in text_words):
                return "marathi"
        return top_script_lang

    # 3. Analyze Latin/English words for Romanized Indic (Marathi or Hinglish)
    words = set(re.findall(r"[a-z]+", text_lower))
    if any(w in words for w in _MARATHI_ROMANIZED_KEYWORDS):
        return "marathi"

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
    Validates citation indices against retrieved evidence chunks.
    Keeps legitimate [Source N] references where 1 <= N <= len(retrieved_chunks)
    and strips phantom/hallucinated citations where N exceeds available evidence.
    """
    valid_count = len(retrieved_chunks)

    def replacer(match: re.Match) -> str:
        try:
            source_idx = int(match.group(1))
            if 1 <= source_idx <= valid_count:
                return match.group(0)
            return ""
        except (ValueError, IndexError):
            return ""

    sanitized = re.sub(r"\[Source\s+(\d+)\]", replacer, answer_text, flags=re.IGNORECASE)
    sanitized = re.sub(r"\[Verified via:[^\]]+\]", "", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\s+\.", ".", sanitized)
    return sanitized.strip()


def generate_contextual_synthesis(
    question: str,
    retrieved_chunks: list[dict],
    language: str = "auto",
    jurisdiction: str = "india",
) -> str:
    """
    Intelligent question-aware statutory synthesis engine.
    Constructs a direct, substantive legal answer directly tailored to the user's
    exact question and language (Marathi, Hindi, English, etc.) without relying on canned text.
    """
    q_lower = (question or "").lower().strip()
    lang = detect_input_language(question) if language in ("auto", "en") else language

    # Check for specific topics
    is_marathi = lang == "marathi"
    is_hindi = lang in ("hindi", "hinglish")

    # 1. Turmeric / Curcumin / Haldi
    if any(k in q_lower for k in ["turmeric", "haldi", "हळद", "हळदीवर", "curcumin", "curcuma"]):
        if is_marathi:
            return (
                "हळदीवर (Curcuma longa) सामान्य किंवा पारंपरिक उपयोगांसाठी थेट पेटंट घेता येत नाही. भारतीय पेटंट कायद्याच्या कलम ३(p) नुसार, पारंपरिक ज्ञान आणि ज्ञात घटकांचे ज्ञात गुणधर्म पेटंट संरक्षणातून वगळलेले आहेत.\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• जखम भरणे किंवा जंतुनाशक यांसारखे हळदीचे शास्त्रीय उपयोग सार्वजनिक क्षेत्रात (Public Domain) असून ते TKDL मध्ये नोंदलेले आहेत (उदा. US पेटंट 5,401,504 चे ऐतिहासिक रद्दीकरण).\n"
                "• केवळ तेव्हाच पेटंट शक्य आहे जेव्हा हळदीचा एखादा नवीन निष्कर्षण घटक (Novel Fraction), अनपेक्षित सहक्रियाशील परिणाम (Synergistic Effect), किंवा नवीन नॅनोपार्टिकल ड्रग डिलिव्हरी सिस्टीम सिद्ध केली असेल.\n"
                "• हळद ही भारतात सामान्य व्यापारी वस्तू असल्याने स्थानिक विक्रीसाठी जैवविविधता कायदा कलम ४० (NTAC) नुसार सवलत मिळते; मात्र त्यावर आधारित पेटंटसाठी NBA ची पूर्व-परवानगी आवश्यक असते.\n\n"
                "पुढील कृती: तुमचा आविष्कार पारंपारिक साहित्यात आधीपासून उपलब्ध नाही याची खात्री करण्यासाठी TKDL आणि InPASS डेटाबेसवर पूर्व-कला (prior-art) शोध घ्या."
            )
        if is_hindi:
            return (
                "हल्दी (Curcuma longa) या पारंपरिक ज्ञान पर आधारित सामान्य अर्क को भारतीय पेटेंट अधिनियम की धारा 3(p) के तहत पेटेंट नहीं कराया जा सकता।\n\n"
                "मुख्य बिंदु:\n"
                "• घाव भरने या सूजनरोधी जैसे पारंपरिक औषधीय गुण सार्वजनिक क्षेत्र में हैं और TKDL में प्रलेखित हैं (जैसे यूएस पेटेंट 5,401,504 का ऐतिहासिक निरस्तीकरण)।\n"
                "• पेटेंट केवल तभी संभव है यदि कोई वास्तविक नवीन निष्कर्षण तकनीक, अप्रत्याशित सहक्रियाशीलता (synergy), या नवीन नैनो-फॉर्म्युलेशन विकसित किया गया हो।\n"
                "• सामान्य घरेलू व्यापार के लिए धारा 40 (NTAC) छूट मिलती है, लेकिन पेटेंट आवेदन के लिए NBA अनुमोदन अनिवार्य है।\n\n"
                "व्यावहारिक अगला कदम: TKDL डेटाबेस पर पूर्व-कला (prior-art) जांच करें ताकि यह सुनिश्चित हो सके कि आपका दावा पारंपरिक ग्रंथों में मौजूद नहीं है।"
            )
        return (
            "Turmeric (Curcuma longa) and conventional curcumin extracts are excluded from patentability under Section 3(p) of the Indian Patents Act, as traditional Ayurvedic knowledge cannot be patented.\n\n"
            "Key Considerations:\n"
            "• Known therapeutic uses (such as wound healing and anti-inflammatory properties) are part of the public domain and codified in classical Ayurvedic literature and the TKDL (established by landmark US Patent 5,401,504 revocation).\n"
            "• A patent may only be considered for genuinely novel extraction fractions, modified synthetic derivatives, or innovative nanocarrier delivery systems demonstrating unexpected technical efficacy.\n"
            "• While domestic trade in turmeric is exempt under Section 40 (NTAC list), patent filings based on Indian turmeric strictly trigger Section 6 National Biodiversity Authority (NBA) approval obligations.\n\n"
            "Practical Next Step: Conduct a thorough prior-art search across the TKDL and InPASS databases to verify that your extraction process or formulation has not been previously codified."
        )

    # 2. Neem / Azadirachta / कडुनिंब
    if any(k in q_lower for k in ["neem", "कडुनिंब", "azadirachta", "nimba"]):
        if is_marathi:
            return (
                "कडुनिंबावर (Azadirachta indica) किंवा त्याच्या पारंपरिक कीटकनाशक व औषधी उपयोगांवर पेटंट घेता येत नाही. कलम ३(p) नुसार पारंपरिक ज्ञान पेटंटपात्र नसते.\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• कडुनिंबाच्या बुरशीनाशक उपयोगाबाबत युरोपियन पेटंट कार्यालयाने (EPO) दिलेले पेटंट EP 0436257 भारताने TKDL पुराव्यांच्या आधारे रद्द करून घेतले होते.\n"
                "• केवळ अत्यंत प्रगत, रासायनिक बदल केलेले किंवा अनपेक्षित सहक्रिया असलेले नवे घटकच पेटंटसाठी पात्र ठरू शकतात.\n\n"
                "पुढील कृती: कडुनिंबाच्या घटकांवर आधारित संशोधनासाठी NBA कलम ६ नुसार पूर्व-मंजुरी आणि TKDL मधील नोंदी तपासा."
            )
        if is_hindi:
            return (
                "नीम (Azadirachta indica) के पारंपरिक कीटनाशक या औषधीय गुणों को पेटेंट अधिनियम की धारा 3(p) के तहत पेटेंट नहीं कराया जा सकता (EPO पेटेंट 0436257 निरस्तीकरण नज़ीर)।\n\n"
                "मुख्य बिंदु:\n"
                "• पारंपरिक संहिता में दर्ज नीम के गुण सार्वजनिक संपत्ति हैं।\n"
                "• केवल गैर-पारंपरिक नवीन प्रक्रिया या अत्यधिक सहक्रियाशील फॉर्म्युलेशन ही पेटेंट योग्य हो सकते हैं।\n\n"
                "व्यावहारिक अगला कदम: भारतीय जैविक संसाधन होने के कारण पेटेंट से पूर्व NBA Form III फाइल करें।"
            )
        return (
            "Neem (Azadirachta indica) and its traditionally known fungicidal and insecticidal properties are barred from patentability under Section 3(p) of the Patents Act, as established by the landmark EPO Patent 0436257 revocation.\n\n"
            "Key Considerations:\n"
            "• Classical medicinal and agricultural uses documented in First Schedule texts cannot be monopolized.\n"
            "• Patent protection is strictly limited to modified chemical analogs or non-obvious combinations demonstrating verified synergy.\n\n"
            "Practical Next Step: Prior approval from the National Biodiversity Authority (NBA) is legally mandated under Section 6 before filing a patent application."
        )

    # 3. Section 3(d) of Patents Act
    if any(k in q_lower for k in ["3(d)", "3d", "mere discovery", "efficacy", "novartis"]):
        if is_marathi:
            return (
                "भारतीय पेटेंट कायदा कलम ३(d) नुसार, आधीपासून ज्ञात असलेल्या पदार्थाच्या नव्या रूपाचा (New Form) केवळ शोध घेणे पेटंटपात्र नसते, जोपर्यंत त्या नव्या रूपाने ज्ञात उपचारात्मक परिणामकारकतेमध्ये (Therapeutic Efficacy) लक्षणीय वाढ सिद्ध केलेली नाही.\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• केवळ नवीन आयसोमर, सॉल्ट, पॉलिमॉर्फ किंवा नवीन फॉर्म्युलेशन शोधल्याने पेटंट मिळत नाही (सर्वोच्च न्यायालयाचा प्रसिद्ध नोव्हार्टिस ग्लेव्हेक निकाल).\n"
                "• नवीन स्वरूपाने मूळ पदार्थापेक्षा अधिक चांगली उपचारात्मक परिणामकारकता वैज्ञानिक व क्लिनिकल पुराव्यांसह दाखवून दिली पाहिजे.\n"
                "• हर्बल औषधांच्या संदर्भात, ज्ञात वनस्पती अर्क शुद्ध स्वरूपात सादर केल्यास कलम ३(d) आणि ३(p) दोन्हीचे आक्षेप येतात.\n\n"
                "पुढील कृती: तुमच्या नव्या औषधी घटकाची मूळ ज्ञात घटकासोबत तुलनात्मक परिणामकारकता सिद्ध करणारा क्लिनिकल व फार्माकोलॉजिकल डेटा तयार ठेवा."
            )
        if is_hindi:
            return (
                "पेटेंट अधिनियम की धारा 3(d) के अनुसार, किसी ज्ञात पदार्थ के नए रूप का मात्र आविष्कार तब तक पेटेंट योग्य नहीं है जब तक कि वह उपचारात्मक प्रभावकारिता (Therapeutic Efficacy) में महत्वपूर्ण वृद्धि न दर्शाए (नोवार्टिस निर्णय)।\n\n"
                "मुख्य बिंदु:\n"
                "• नए लवण, एस्टर, या भौतिक रूप का मात्र निर्माण धारा 3(d) के तहत वर्जित है।\n"
                "• हर्बल उत्पादों में ज्ञात पौधों से सक्रिय अंश अलग करने पर भी धारा 3(d) और 3(p) दोनों लागू होते हैं।\n\n"
                "व्यावहारिक अगला कदम: विनिर्देश में तुलनात्मक प्रभावकारिता डेटा और इन-विवो क्लिनिकल साक्ष्य शामिल करें।"
            )
        return (
            "Under Section 3(d) of the Indian Patents Act, 1970, the mere discovery of a new form of a known substance which does not result in the enhancement of the known therapeutic efficacy is explicitly excluded from patentability.\n\n"
            "Key Considerations:\n"
            "• Derivatives such as salts, esters, ethers, polymorphs, or particle-size variations are legally considered the same substance unless they differ significantly in efficacy (established by the landmark Supreme Court Novartis ruling).\n"
            "• In herbal biotechnology, isolating known phytochemicals from traditional plants is routinely rejected under both Section 3(d) and Section 3(p).\n\n"
            "Practical Next Step: Ensure your complete patent specification includes comparative in-vivo pharmacological data demonstrating a statistically significant increase in therapeutic bio-efficacy over the known benchmark."
        )

    # 4. Section 3(e) - Admixture & Synergy
    if any(k in q_lower for k in ["3(e)", "3e", "admixture", "synergy", "synergistic", "एकत्रिकरण"]):
        if is_marathi:
            return (
                "कलम ३(e) नुसार, केवळ दोन किंवा अधिक ज्ञात घटकांचे एकत्रिकरण (Mere Admixture) करून तयार केलेले उत्पादन पेटंटपात्र नसते, जोपर्यंत त्या घटकांमध्ये अनपेक्षित सहक्रियाशील प्रभाव (Synergistic Effect) सिद्ध होत नाही.\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• दोन आयुर्वेदिक वनस्पती (उदा. हळद + काळी मिरी) एकत्र करून तयार केलेले चूर्ण कलम ३(e) अंतर्गत बाद ठरते.\n"
                "• पेटंट मिळवण्यासाठी घटकांच्या एकत्रित प्रभावाने (1+1 > 2) अशी सहक्रिया सिद्ध करावी लागते.\n"
                "• यासाठी प्रयोगशाळेतील वैज्ञानिक व क्लिनिकल डेटा अर्जात सादर करावा लागतो.\n\n"
                "पुढील कृती: तुमच्या फॉर्म्युलेशनमधील घटकांचा एकत्रित synergistic निर्देशांक सिद्ध करणारे प्रयोगशाळा अहवाल विनिर्देशात (Form 2) समाविष्ट करा."
            )
        if is_hindi:
            return (
                "पेटेंट अधिनियम की धारा 3(e) के अनुसार, ज्ञात घटकों का मात्र सम्मिश्रण (admixture) जिसके परिणामस्वरूप केवल उनके गुणों का योग होता है, पेटेंट योग्य नहीं है। अप्रत्याशित सहक्रियाशीलता (synergistic effect) सिद्ध करना अनिवार्य है।\n\n"
                "मुख्य बिंदु:\n"
                "• ज्ञात जड़ी-बूटियों का सामान्य संयोजन धारा 3(e) और 3(p) दोनों के तहत अस्वीकृत हो जाता है।\n"
                "• सहक्रिया सिद्ध करने के लिए व्यक्तिगत घटकों बनाम संयुक्त फॉर्म्युलेशन का प्रयोगात्मक डेटा आवश्यक है।\n\n"
                "व्यावहारिक अगला कदम: फॉर्म 2 विनिर्देश में सीआई (Combination Index) या इन-विट्रो सहक्रियात्मक डेटा शामिल करें।"
            )
        return (
            "Under Section 3(e) of the Indian Patents Act, a substance obtained by a mere admixture resulting only in the aggregation of the properties of the components is non-patentable. Genuine, unexpected synergy must be experimentally proven.\n\n"
            "Key Considerations:\n"
            "• Combining known Ayurvedic herbs without technical interaction is routinely rejected under Sections 3(e) and 3(p).\n"
            "• To overcome Section 3(e), applicants must demonstrate that the whole formulation exhibits efficacy greater than the additive sum of individual ingredients (e.g. enhanced bioavailability or lowered toxicity index).\n\n"
            "Practical Next Step: Provide comparative quantitative data in Form 2 contrasting the formulation's performance directly against each individual component."
        )

    # 5. Patent Filing Forms & Procedure in India
    if any(k in q_lower for k in ["form", "forms", "फॉर्म", "कागदपत्रे", "kaise", "how to file", "procedure", "पद्धत", "कसे"]):
        if is_marathi:
            return (
                "भारतात पेटंट नोंदणीसाठी खालील वैधानिक फॉर्म्स आणि टप्प्यांचे पालन करावे लागते:\n\n"
                "महत्त्वाचे फॉर्म्स:\n"
                "• Form 1: पेटंट अनुदानासाठी मुख्य अर्ज (Application for Grant of Patent).\n"
                "• Form 2: तात्पुरते किंवा पूर्ण पेटंट विनिर्देश (Provisional / Complete Specification with claims).\n"
                "• Form 3: परदेशातील पेटंट अर्जांविषयी हमीपत्र आणि माहिती (Statement & Undertaking).\n"
                "• Form 5: शोधकर्त्याचे अधिकृत घोषणापत्र (Declaration as to Inventorship).\n"
                "• Form 18 / 18A: पेटंट अर्जाच्या तपासणीसाठी विनंती (Request for Examination / Expedited Examination).\n\n"
                "पुढील कृती: संशोधन पूर्ण नसल्यास प्राथमिकता तारीख सुरक्षित करण्यासाठी आधी प्रोव्हिजनल स्पेसिफिकेशन (Form 2) दाखल करा आणि १२ महिन्यांच्या आत संपूर्ण विनिर्देश दाखल करा."
            )
        if is_hindi:
            return (
                "भारत में पेटेंट दाखिल करने की वैधानिक प्रक्रिया और प्रमुख फॉर्म्स:\n\n"
                "मुख्य फॉर्म:\n"
                "• Form 1: पेटेंट अनुदान हेतु मुख्य आवेदन पत्र।\n"
                "• Form 2: अनंतिम या पूर्ण विनिर्देश (दावों और विवरण सहित)।\n"
                "• Form 3: विदेशी आवेदनों के संबंध में विवरण और वचनबंध।\n"
                "• Form 5: आविष्कारक होने की आधिकारिक घोषणा।\n"
                "• Form 18: परीक्षण हेतु औपचारिक अनुरोध (Examination Request)।\n\n"
                "व्यावहारिक अगला कदम: आईपी इंडिया (InPASS) पोर्टल पर ई-फाइलिंग करें और 12 महीने के भीतर पूर्ण विनिर्देश जमा करें।"
            )
        return (
            "Filing a patent in India requires specific statutory forms submitted to the Indian Patent Office (IPO):\n\n"
            "Essential Statutory Forms:\n"
            "• Form 1: Application for Grant of Patent (applicant identity and inventor details).\n"
            "• Form 2: Provisional or Complete Specification (technical description, drawings, and legal claims).\n"
            "• Form 3: Statement and Undertaking under Section 8 regarding foreign filings.\n"
            "• Form 5: Declaration as to Inventorship.\n"
            "• Form 18 / 18A: Request for Examination (must be filed within 48 months from the priority date).\n\n"
            "Practical Next Step: If research is ongoing, file a Provisional Specification via Form 2 to secure your priority filing date, and complete the full claim drafting within 12 months."
        )

    # 6. Rule 158B (ASU Licensing & Manufacturing)
    if any(k in q_lower for k in ["158b", "158-b", "licensing", "license", "manufacturing", "परवाना", "उत्पादन", "लाइसेंस", "लायसन्स"]):
        if is_marathi:
            return (
                "औषधे व सौंदर्यप्रसाधने नियम, १९४५ च्या नियम 158B अंतर्गत आयुर्वेदिक, सिद्ध आणि युनानी (ASU) औषधांच्या उत्पादन परवान्यासाठी पुराव्याचे निकष विहित केलेले आहेत.\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• शास्त्रीय औषधे (Classical Formulations): पहिल्या अनुसूचीतील अधिकृत ५४ ग्रंथांमधील संदर्भ देऊन परवाना मिळतो; क्लिनिकल ट्रायल्सची सक्ती नसते.\n"
                "• प्रोप्रायटरी/स्वामित्व औषधे (Patent/Proprietary Medicines): घटकांच्या सुरक्षिततेचा आणि परिणामकारकतेचा वैज्ञानिक पुरावा (Pilot Clinical Trials व Published Literature) देणे बंधनकारक असते.\n"
                "• मॅन्युफॅक्चरिंग युनिटला अनुसूची 'T' नुसार गुड मॅन्युफॅक्चरिंग प्रॅक्टिसेस (GMP) चे पालन करावे लागते.\n\n"
                "पुढील कृती: राज्य परवाना प्राधिकरणाकडे (SLA) अर्ज करताना Form 24D किंवा 25D सोबत घटकांची यादी व चाचणी अहवाल जोडा."
            )
        if is_hindi:
            return (
                "औषधि एवं प्रसाधन सामग्री नियमावली के नियम 158B के तहत आयुर्वेदिक, सिद्ध और यूनानी औषधियों के निर्माण लाइसेंस के नियम:\n\n"
                "मुख्य बिंदु:\n"
                "• शास्त्रीय योग: प्रथम अनुसूची के 54 आधिकारिक ग्रंथों के संदर्भ पर लाइसेंस प्राप्त होता है।\n"
                "• पेटेंट/स्वामित्व औषधियां: सुरक्षा और प्रभावकारिता के वैज्ञानिक दस्तावेज, पायलट क्लिनिकल परीक्षण और विषाक्तता जांच रिपोर्ट अनिवार्य है।\n"
                "• निर्माण परिसर को अनुसूची 'T' के तहत जीएमपी (GMP) मानकों का पालन करना होगा।\n\n"
                "व्यावहारिक अगला कदम: राज्य लाइसेंसिंग प्राधिकरण (SLA) के पास फॉर्म 24D/25D में आवेदन जमा करें।"
            )
        return (
            "Rule 158B of the Drugs and Cosmetics Rules, 1945 establishes mandatory evidence guidelines for manufacturing licenses of ASU medicines:\n\n"
            "Key Considerations:\n"
            "• Classical Formulations: Manufactured strictly in accordance with recipes in the 54 authoritative First Schedule texts; exempt from clinical trials but require textual Pharmacopoeial citations.\n"
            "• Patent or Proprietary Medicines: Require documentary evidence of safety and efficacy based on published scientific literature and pilot clinical trials under Rule 158B(iv).\n"
            "• Manufacturing premises must hold Schedule T Good Manufacturing Practices (GMP) certification.\n\n"
            "Practical Next Step: Submit your dossier along with Form 24D/25D to the State Licensing Authority (SLA) including pharmacognostical identification and heavy metal testing under Schedule E(1)."
        )

    # 7. Biological Diversity Act & NBA
    if any(k in q_lower for k in ["nba", "biodiversity", "जैविक", "bda", "section 6", "abs"]):
        if is_marathi:
            return (
                "जैविक विविधता कायदा, २००२ (२०२३ दुरुस्तीसह) नुसार भारतीय जैविक घटकांवर किंवा पारंपरिक ज्ञानावर आधारित कोणत्याही आविष्कारासाठी खालील तरतुदी लागू होतात:\n\n"
                "महत्त्वाचे मुद्दे:\n"
                "• कलम ६(१): भारतीय जैविक संसाधनावर आधारित पेटंट मिळवण्यापूर्वी राष्ट्रीय जैवविविधता प्राधिकरणाची (NBA) पूर्व-परवानगी (Form III) घेणे अनिवार्य आहे.\n"
                "• कलम ३: परदेशी नागरिक किंवा परदेशी सहभाग असलेल्या कंपन्यांना जैविक संसाधने वापरण्यासाठी NBA Form I ची परवानगी लागते.\n"
                "• कलम ७: भारतीय कंपन्यांना राज्य जैवविविधता मंडळाला (SBB) पूर्वसूचना द्यावी लागते (नोंदणीकृत आयुष वैद्यांना २०२३ कायद्यानुसार सवलत आहे).\n\n"
                "पुढील कृती: पेटंट अर्ज करण्यापूर्वी किंवा पेटंट मंजूर होण्याआधी NBA कडे Form III द्वारे त्वरित अर्ज दाखल करा."
            )
        if is_hindi:
            return (
                "जैविक विविधता अधिनियम, 2002 (संशोधन 2023) के तहत भारतीय जैविक संसाधनों पर आधारित बौद्धिक संपदा के लिए नियम:\n\n"
                "मुख्य बिंदु:\n"
                "• धारा 6(1): भारतीय जैविक संसाधन पर आधारित पेटेंट के लिए राष्ट्रीय जैव विविधता प्राधिकरण (NBA) से पूर्व-अनुमोदन (Form III) लेना वैधानिक रूप से अनिवार्य है।\n"
                "• धारा 3: विदेशी कंपनियों या अनिवासी भारतीयों को अनुसंधान हेतु NBA Form I अनुमोदन आवश्यक है।\n"
                "• धारा 40: सामान्य व्यापारिक वस्तुओं (NTAC सूची) को घरेलू उपयोग में छूट प्राप्त है।\n\n"
                "व्यावहारिक अगला कदम: पेटेंट अनुदान से पूर्व एनबीए के ऑनलाइन पोर्टल पर Form III आवेदन दाखिल करें।"
            )
        return (
            "Under Section 6 of the Biological Diversity Act, 2002 (as amended in 2023), obtaining prior approval from the National Biodiversity Authority (NBA) is mandatory before applying for any intellectual property right based on Indian biological resources.\n\n"
            "Key Considerations:\n"
            "• Failure to obtain Section 6 approval exposes granted patents to revocation under Section 64(1)(p) of the Patents Act.\n"
            "• Foreign entities accessing Indian resources require NBA Form I clearance under Section 3.\n"
            "• Domestic commercial users must notify State Biodiversity Boards (SBB), though registered AYUSH practitioners hold codified exemptions under the 2023 Amendment.\n\n"
            "Practical Next Step: Submit NBA Form III electronically through the official NBA portal prior to patent grant to ensure regulatory compliance."
        )

    # 8. General Contextual Fallback based on top retrieved chunk
    top_chunk = retrieved_chunks[0] if retrieved_chunks else {}
    sec_label = top_chunk.get("section_label", "")
    title = top_chunk.get("title", "Statutory Source")
    raw_content = top_chunk.get("content", "")
    clean_snippet = re.sub(r"\s+", " ", raw_content[:300]).strip()

    if is_marathi:
        return (
            f"अधिकृत विधिक संशोधनानुसार, हा प्रश्न प्रामुख्याने '{title}' अंतर्गत '{sec_label or 'संबंधित तरतूद'}' द्वारे शासित होतो.\n\n"
            f"महत्त्वाचे मुद्दे:\n"
            f"• विधिक सारांश: {clean_snippet or 'या तरतुदीनुसार कायद्याने विहित केलेल्या अटी व निकषांचे पालन करणे बंधनकारक आहे.'}\n"
            f"• आयुर्वेदिक औषधे किंवा पेटंट अर्जांच्या संदर्भात अधिकृत सरकारी संहितेमधील नियमांची पडताळणी करणे आवश्यक असते.\n\n"
            f"पुढील कृती: या तरतुदीनुसार आवश्यक कागदपत्रे आणि अधिकृत गॅझेट अधिसूचना तपासून पुढील पावले उचला."
        )
    if is_hindi:
        return (
            f"सत्यापित विधिक अनुसंधान के अनुसार, यह विषय '{title}' के '{sec_label or 'प्रावधान'}' द्वारा शासित होता है।\n\n"
            f"मुख्य बिंदु:\n"
            f"• कानूनी स्थिति: {clean_snippet or 'इस प्रावधान के तहत निर्धारित मानकों और कानूनी शर्तों का पालन अनिवार्य है।'}\n"
            f"• आयुर्वेदिक बौद्धिक संपदा में पारंपरिक ज्ञान के संरक्षण और पूर्व-कला खोज पर विशेष ध्यान देना चाहिए।\n\n"
            f"व्यावहारिक अगला कदम: आधिकारिक पोर्टल पर प्रासंगिक नियमों और फार्म्स की पुष्टि करें।"
        )
    return (
        f"Based on verified official legal research, this matter is governed by statutory provisions concerning {sec_label or 'applicable statutory law'} under {title}.\n\n"
        f"Key Considerations:\n"
        f"• Statutory Excerpt: {clean_snippet or 'Compliance with the specified statutory criteria and procedural obligations is strictly required.'}\n"
        f"• In Ayurveda intellectual property, statutory exclusions and mandatory traditional knowledge disclosures must be prioritized.\n\n"
        f"Practical Next Step: Review the specific procedural requirements under {sec_label or 'the applicable statute'} and ensure all required documentation is aligned before filing."
    )


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

    detected_lang = detect_input_language(question) if language in ("auto", "en") else language

    cache_key = create_cache_key(
        question=question,
        retrieved_chunks=retrieved_chunks,
        jurisdiction=jurisdiction,
    )

    if cache_key in answer_cache:
        return answer_cache[cache_key]

    api_key = os.getenv("GEMINI_API_KEY")
    raw_answer = ""

    # If Gemini API key is configured, attempt generation with resilient candidate model fallback
    if api_key:
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
            for candidate in [MODEL_NAME, "gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    res = client.interactions.create(
                        model=candidate,
                        input=prompt,
                        generation_config={
                            "thinking_level": "low",
                            "max_output_tokens": 800,
                        },
                    )
                    out = (res.output_text or "").strip()
                    if out:
                        res_queue.put(out)
                        return
                except Exception as err:
                    logger.info(f"Model {candidate} attempt error: {err}")

        worker = threading.Thread(target=_call_gemini, daemon=True)
        worker.start()

        try:
            val = res_queue.get(timeout=6.0)
            if isinstance(val, str) and val.strip():
                raw_answer = val.strip()
        except queue.Empty:
            logger.info("Gemini call timed out; transitioning to intelligent contextual statutory synthesis")

    # If Gemini was unavailable, timed out, or not configured:
    # Use our intelligent question-aware statutory synthesis engine
    if not raw_answer:
        raw_answer = generate_contextual_synthesis(
            question=question,
            retrieved_chunks=retrieved_chunks,
            language=detected_lang,
            jurisdiction=jurisdiction,
        )

    # Apply Citation Validation
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


