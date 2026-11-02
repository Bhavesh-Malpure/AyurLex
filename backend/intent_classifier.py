"""
intent_classifier.py
--------------------
Intent-based answer router and query analyzer for Ayurlex.

Classifies user questions into distinct intent categories:
1. PATENT_DISCOVERY: Queries asking for new/latest patents, patent lists, WO numbers, recent publications.
2. PATENTABILITY_ADVICE: Queries asking if an invention/formulation is patentable.
3. PATENT_FILING_PROCESS: Queries asking how to apply or file for a patent in India.
4. AYUSH_REGULATION: Queries asking about licensing, Rule 158B, ASU GMP, FSSAI/CDSCO rules.
5. INTERNATIONAL_IP: Queries asking about WIPO treaties, Nice/Locarno classifications, EPO rules, TRIPS.
6. UNKNOWN_OR_AMBIGUOUS: Vague, ambiguous, or generic non-legal queries.
"""

from dataclasses import dataclass, field
import re
from typing import Literal

from schemas import QueryAnalysis

KNOWN_SUBSTANCES = {
    "ashwagandha", "turmeric", "curcumin", "neem", "tulsi", "triphala",
    "chyawanprash", "guggulu", "brahmi", "shatavari", "haridra", "nimba",
    "boswellia", "resveratrol", "piperine", "ginger", "garlic", "amla",
    "herbal", "extract", "extraction", "formulation", "formulations",
    "composition", "polyherbal", "ayurvedic", "medicine", "aushadh",
    "synergistic", "diabetes", "cancer", "arthritis", "wound", "oil",
}

PATENT_DISCOVERY_PATTERNS = [
    r"\b(?:new|latest|recent|published|naya|naye|pichhle|halia)\s+patents?\b",
    r"\bpatents?\s+(?:batao|bataye|bataiye|dikhao|list|names?|publications?)\b",
    r"\b(?:wo|pct)\s+patents?\b",
    r"\blatest\s+pct\s+patents?\b",
    r"\bpatent\s+(?:discovery|search|records?)\b",
    r"\b(?:mujhe\s+)?(?:new|latest|naya|naye)\s+patent\b",
    r"\b(?:new|latest|recent|published|search|find|show|list)\s+patents?\s+on\s+[a-z]+\b",
]

PATENT_FILING_PATTERNS = [
    r"\bpatent\s+(?:kaise\s+file|kaise\s+kare|kaise\s+karen|kaise\s+le|kaise\s+banaye|kaise\s+register|kaise\s+karte)\b",
    r"\bhow\s+to\s+(?:file|apply|register|get|obtain)\s+(?:a\s+)?patent\b",
    r"\bpatent\s+(?:filing|application|registration|grant)\s+(?:process|procedure|steps|guide|stage)\b",
    r"\bpatent\s+process\s+in\s+india\b",
    r"\b(?:form\s+1|form\s+2|form\s+3|form\s+5|form\s+18)\b",
]

PATENTABILITY_PATTERNS = [
    r"\b(?:can\s+i|can\s+we|is\s+it|are\s+they)\s+patent\b",
    r"\bpatentable\b|\bpatentability\b",
    r"\bpatent\s+(?:ho\s+sakta|mil\s+sakta|karva\s+sakte|kara\s+sakte)\b",
    r"\bsection\s+3\([a-z]\)\b",
    r"\bsection\s+3[dep]\b",
    r"\bnovelty\b|\binventive\s+step\b|\bnon[\s\-]obvious\b",
    r"\btraditional\s+knowledge\s+patent\b",
    r"\bsynergistic\s+combinations?\b",
]

AYUSH_REGULATION_PATTERNS = [
    r"\b(?:ayush|ayurveda|ayurvedic|siddha|unani)\s+(?:license|licence|regulation|rules?|guidelines?)\b",
    r"\bayurveda\s+aahara\b",
    r"\brule\s+158b\b",
    r"\bschedule\s+t\b",
    r"\bgmp\s+compliance\b",
    r"\bmanufacturing\s+licen[sc]e\b",
    r"\bfirst\s+schedule\s+drugs\b",
    r"\basu\s+drug\b",
    r"\bfssai\s+herbal\b",
    r"\bcdsco\b",
]

INTERNATIONAL_IP_PATTERNS = [
    r"\bwipo\b|\btrips\b|\bmadrid\s+system\b|\bhague\s+system\b|\bbudapest\s+treaty\b",
    r"\bnice\s+classification\b|\blocarno\s+classification\b",
    r"\bepo\b|\beuropean\s+patent\s+office\b|\beuropean\s+patent\b",
    r"\bnagoya\s+protocol\b|\babs\s+clearing\b",
]

AMBIGUOUS_PATTERNS = [
    r"^(?:hi|hello|hey|help|kya\s+hai|batao|kuch\s+batao|test|ayurlex)$",
]


def classify_query_intent(question: str, jurisdiction: str = "india") -> QueryAnalysis:
    """Analyze the user's question and determine structured intent and clarification requirements."""
    q_lower = (question or "").lower().strip()

    # 1. Check for Trivial / Ambiguous
    for pat in AMBIGUOUS_PATTERNS:
        if re.search(pat, q_lower):
            return QueryAnalysis(
                intent="UNKNOWN_OR_AMBIGUOUS",
                confidence="high",
                missing_filters=["specific_research_topic"],
                should_ask_clarification=True,
                clarification_prompt=(
                    "How can Ayurlex assist with your research? "
                    "Please specify if you are looking for patentability analysis, filing procedures, "
                    "AYUSH drug regulations, or international IP treaties."
                ),
                clarification_examples=[
                    "Is Ashwagandha extract patentable under Section 3(p)?",
                    "How to apply for an Ayurvedic patent in India?",
                    "Mandatory Rule 158B licensing requirements for ASU drugs",
                ],
            )

    # 2. Check for Patent Filing Process (e.g. "patent kaise file kare?")
    for pat in PATENT_FILING_PATTERNS:
        if re.search(pat, q_lower):
            return QueryAnalysis(
                intent="PATENT_FILING_PROCESS",
                confidence="high",
                missing_filters=[],
                should_ask_clarification=False,
            )

    # 3. Check for Patent Discovery (e.g. "mujhe new patent batao", "latest patents")
    is_patent_discovery = False
    for pat in PATENT_DISCOVERY_PATTERNS:
        if re.search(pat, q_lower):
            is_patent_discovery = True
            break

    if is_patent_discovery:
        # Check for missing search criteria
        words = set(re.findall(r"[a-z]+", q_lower))
        has_substance = bool(words.intersection(KNOWN_SUBSTANCES))
        has_date = bool(re.search(r"\b(?:19|20)\d{2}\b|\b(?:recent|latest|year|month)\b", q_lower))
        has_jurisdiction = bool(re.search(r"\b(?:india|pct|wipo|europe|epo|us|uspto)\b", q_lower))

        missing_filters = []
        if not has_substance:
            missing_filters.append("technology_topic")
        if not has_date:
            missing_filters.append("date_range")
        if not has_jurisdiction:
            missing_filters.append("jurisdiction")

        # If substance/technology is missing (e.g. "mujhe new patent batao"), we MUST ask clarification
        if "technology_topic" in missing_filters:
            return QueryAnalysis(
                intent="PATENT_DISCOVERY",
                confidence="high",
                missing_filters=missing_filters,
                should_ask_clarification=True,
                clarification_prompt=(
                    "Which technology or ingredient do you want patents for? For example, you can ask: "
                    "‘Show recent patents related to ashwagandha’ or ‘latest turmeric patent publications.’"
                ),
                clarification_examples=[
                    "Latest PCT patents on ashwagandha",
                    "New turmeric patent publications in 2026",
                    "Recent Indian patents for herbal extraction",
                ],
            )
        else:
            return QueryAnalysis(
                intent="PATENT_DISCOVERY",
                confidence="high",
                missing_filters=missing_filters,
                should_ask_clarification=False,
            )

    # 4. Check for Patentability Advice
    for pat in PATENTABILITY_PATTERNS:
        if re.search(pat, q_lower):
            return QueryAnalysis(
                intent="PATENTABILITY_ADVICE",
                confidence="high",
                missing_filters=[],
                should_ask_clarification=False,
            )

    # 5. Check for AYUSH Regulation
    for pat in AYUSH_REGULATION_PATTERNS:
        if re.search(pat, q_lower):
            return QueryAnalysis(
                intent="AYUSH_REGULATION",
                confidence="high",
                missing_filters=[],
                should_ask_clarification=False,
            )

    # 6. Check for International IP
    for pat in INTERNATIONAL_IP_PATTERNS:
        if re.search(pat, q_lower):
            return QueryAnalysis(
                intent="INTERNATIONAL_IP",
                confidence="high",
                missing_filters=[],
                should_ask_clarification=False,
            )

    # Fallback to topic heuristic based on jurisdiction
    if jurisdiction == "international":
        return QueryAnalysis(
            intent="INTERNATIONAL_IP",
            confidence="medium",
            missing_filters=[],
            should_ask_clarification=False,
        )

    # Default to statutory patentability advice for generic queries
    return QueryAnalysis(
        intent="PATENTABILITY_ADVICE",
        confidence="medium",
        missing_filters=[],
        should_ask_clarification=False,
    )


def get_patent_discovery_guidance(question: str, jurisdiction: str = "india") -> tuple[str, list[dict]]:
    """Build grounded patent discovery guidance with official search portal links and transparent limitation."""
    q_lower = (question or "").lower().strip()
    words = re.findall(r"[a-z0-9]+", q_lower)
    substances = [w for w in words if w in KNOWN_SUBSTANCES]
    topic_str = " ".join(substances) if substances else "herbal / natural medicine"

    sources: list[dict] = []
    wants_international = (jurisdiction == "international" or any(w in q_lower for w in ["pct", "wipo", "international", "wo", "europe", "epo"]))
    wants_india = (jurisdiction == "india" or any(w in q_lower for w in ["india", "indian", "inpass", "delhi", "mumbai", "kolkata", "chennai"]))

    if wants_international or not wants_india:
        sources.append({
            "id": "official_patentscope",
            "title": "WIPO PATENTSCOPE — Official International Patent Search",
            "jurisdiction": "international",
            "section": "Patent Search Portal",
            "url": "https://patentscope.wipo.int/search/en/search.jsf",
        })
    if wants_india or not wants_international:
        sources.append({
            "id": "official_inpass",
            "title": "IP India InPASS — Patent Search",
            "jurisdiction": "india",
            "section": "Patent Search Portal",
            "url": "https://ipindiaservices.gov.in/publicsearch",
        })

    # Language check
    from agent import detect_input_language
    lang = detect_input_language(question)

    if lang in ("hindi", "hinglish"):
        summary = (
            f"{topic_str} से संबंधित पेटेंट आवेदन सामान्यतः नवीन निष्कर्षण प्रक्रियाओं, मानकीकृत अंशों या उन्नत औषधि वितरण प्रणालियों पर केंद्रित होते हैं, "
            f"क्योंकि पारंपरिक ज्ञान और ज्ञात गुणों के मिश्रण भारतीय पेटेंट अधिनियम की धारा 3(p) और 3(e) के तहत पेटेंट योग्य नहीं हैं。\n\n"
            f"मुख्य बिंदु:\n"
            f"• पेटेंट केवल तभी संभव है जब आविष्कार में पारंपरिक ज्ञान से परे कोई नवीन तकनीकी विशेषता या अप्रत्याशित चिकित्सीय प्रभावशीलता हो।\n"
            f"• भारत के जैविक संसाधनों पर आधारित आविष्कारों के लिए पेटेंट आवेदन करने से पूर्व राष्ट्रीय जैव विविधता प्राधिकरण (NBA) से अनुमति आवश्यक है।\n\n"
            f"व्यावहारिक अगला कदम: आधिकारिक पेटेंट रजिस्टरों (जैसे InPASS या WIPO PATENTSCOPE) में पूर्व-कला (prior-art) खोज करें ताकि यह सुनिश्चित हो सके कि आपका दावा पहले से प्रकाशित नहीं है।"
        )
    else:
        summary = (
            f"Patent publications related to {topic_str} typically center on novel extraction methods, standardized active fractions showing unexpected synergistic efficacy, or novel delivery mechanisms, as raw herbs and traditional formulations are excluded from patentability.\n\n"
            f"Key Points:\n"
            f"• Mere traditional knowledge, classical Ayurvedic compositions, and simple admixtures are barred under Sections 3(p) and 3(e).\n"
            f"• Valid patent claims require verifiable evidence of novelty, inventive step, and industrial applicability.\n"
            f"• Prior statutory approval from the National Biodiversity Authority (NBA) is legally required before patent filing for biological resources obtained from India.\n\n"
            f"Practical Next Step: Conduct a focused prior-art search across official patent registers to verify whether your specific formulation or process is already disclosed."
        )

    return summary, sources


# ---------------------------------------------------------------------------
# Direct Answer Generator for Standard Question Types
# ---------------------------------------------------------------------------

STUDENT_PATENT_PATTERNS = [
    r"\b(?:am\s+)?student\s+(?:can\s+)?patent\b",
    r"\bcan\s+(?:a\s+)?student\s+(?:apply\s+for\s+a\s+)?patent\b",
    r"\bcollege\s+(?:project\s+|student\s+)?patent\b",
    r"\bstudent\s+patent\s+rights?\b",
]

AYURVEDIC_FORMULATION_PATTERNS = [
    r"\b(?:can\s+i|can\s+we|is\s+it\s+possible\s+to)\s+patent\s+(?:an?\s+)?(?:ayurvedic|herbal)\s+formulation\b",
    r"\bpatent\s+(?:an?\s+)?(?:ayurvedic|herbal)\s+formulation\b",
    r"\bpatentability\s+of\s+(?:ayurvedic|herbal)\s+formulation\b",
    r"\bherbal\s+formulation\s+patentable\b",
]


def get_intent_direct_answer(question: str, jurisdiction: str = "india") -> str | None:
    """Return a direct researched answer for canonical question types when applicable."""
    q_lower = (question or "").lower().strip()

    # 0. Explicit Source Request ("source show", "where did you find this?")
    if re.search(r"\b(?:source\s+show|show\s+sources?|where\s+did\s+you\s+find|kaha\s+se\s+mila|sources?\s+batao|koun\s+se\s+source)\b", q_lower):
        if jurisdiction == "international":
            return (
                "This research is verified against official international intellectual property authorities: "
                "WIPO Treaties (Paris Convention, Patent Cooperation Treaty - PCT), European Patent Convention (EPC), "
                "and International Classification standards (Nice and Locarno)."
            )
        return (
            "This research is verified against official statutory Indian sources: "
            "The Patents Act, 1970 (including Sections 3(p), 3(e), and 3(d)), Drugs and Cosmetics Rules, 1945 (Rule 158B and Schedule T), "
            "the Biological Diversity Act, 2002 (Section 6), and the Ayurvedic Pharmacopoeia of India (API)."
        )

    # 1. Student Patenting
    for pat in STUDENT_PATENT_PATTERNS:
        if re.search(pat, q_lower):
            return (
                "Yes. A student can apply for a patent if they are the true and first inventor "
                "or have rights assigned to them. Whether a patent can be granted depends on the "
                "invention being new, non-obvious, useful in industry, and not excluded by patent law. "
                "If this was developed as a college project, check your college IP ownership policy."
            )

    # 2. Patent Filing Process ("patent kaise karte hai?", "how to apply for patent?")
    for pat in PATENT_FILING_PATTERNS:
        if re.search(pat, q_lower):
            # If typed in Devanagari Hindi script, provide native Hindi; otherwise provide the direct research answer
            if re.search(r"[\u0900-\u097F]", question):
                return (
                    "पेटेंट प्राप्त करने के लिए सबसे पहले सुनिश्चित करें कि आपका आविष्कार नया (novel) है। "
                    "पेटेंट विनिर्देश (Specification) तैयार करें, आवेदन (Form 1 व Form 2) दाखिल करें, "
                    "परीक्षण (Examination) का अनुरोध करें, आपत्तियों का उत्तर दें और पेटेंट अनुदान प्रक्रिया पूर्ण करें। "
                    "पेटेंट एजेंट विनिर्देश तैयार करने और गलतियों से बचने में सहायता कर सकते हैं।"
                )
            return (
                "To apply for a patent, first confirm that your invention is new. Prepare a patent "
                "specification, file the application, request examination, respond to any objections, "
                "and complete the grant process. A patent agent can help prepare claims and avoid filing mistakes."
            )

    # 3. Ayurvedic Formulation Patentability ("Can I patent an Ayurvedic formulation?")
    for pat in AYURVEDIC_FORMULATION_PATTERNS:
        if re.search(pat, q_lower):
            return (
                "It may be possible only if the formulation has a genuinely new technical feature "
                "and is not merely traditional knowledge or a known combination of known ingredients. "
                "A new extraction process, unexpected technical effect, or evidence of improved performance "
                "may strengthen the case, but prior-art review is essential."
            )

    # 4. Vague Patent Discovery ("mujhe new patent batao")
    if re.search(r"\b(?:mujhe\s+)?(?:new|latest|naya|naye)\s+patent\b|\bpatents?\s+(?:batao|bataye|bataiye|dikhao)\b", q_lower):
        words = set(re.findall(r"[a-z]+", q_lower))
        if not words.intersection(KNOWN_SUBSTANCES):
            return (
                "Which technology or ingredient do you want patents for? For example, you can ask: "
                "‘Show recent patents related to ashwagandha’ or ‘latest turmeric patent publications.’"
            )

    # 5. Ashwagandha Extract & Section 3(p) Patentability (India)
    if jurisdiction != "international" and not any(w in q_lower for w in ["epo", "european", "wipo", "trips"]):
        if "ashwagandha" in q_lower and ("patent" in q_lower or "extract" in q_lower or "3(p)" in q_lower or "3p" in q_lower):
            if re.search(r"[\u0900-\u097F]", question):
                return (
                    "पारंपरिक या सामान्य रूप में अश्वगंधा अर्क (Ashwagandha extract) भारतीय पेटेंट अधिनियम की धारा 3(p) के तहत पेटेंट योग्य नहीं है, "
                    "क्योंकि पारंपरिक ज्ञान और ज्ञात औषधीय पौधों के ज्ञात गुणों को पेटेंट से बाहर रखा गया है।\n\n"
                    "मुख्य बिंदु:\n"
                    "• पेटेंट केवल तभी संभव है जब कोई वास्तव में नवीन निष्कर्षण प्रक्रिया (novel extraction process), अप्रत्याशित चिकित्सीय प्रभावशीलता दर्शाने वाला मानकीकृत अंश, "
                    "या नवीन औषधि वितरण प्रणाली (जैसे नैनोपार्टिकल्स) विकसित की गई हो जो पारंपरिक ज्ञान से परे हो।\n"
                    "• पारंपरिक आयुर्वेदिक संहिताओं या TKDL में दर्ज सामान्य चूर्ण, अर्क या योग धारा 3(p) और 3(e) के तहत सीधे वर्जित हैं।\n"
                    "• चूंकि अश्वगंधा एक भारतीय जैविक संसाधन है, इसलिए पेटेंट दाखिल करने से पहले जैविक विविधता अधिनियम की धारा 6 के तहत राष्ट्रीय जैव विविधता प्राधिकरण (NBA) से पूर्व-अनुमति लेना अनिवार्य है।\n\n"
                    "व्यावहारिक अगला कदम: यह सत्यापित करने के लिए कि आपकी निष्कर्षण तकनीक पारंपरिक साहित्य में पहले से मौजूद नहीं है, TKDL और InPASS डेटाबेस पर पूर्व-कला (prior-art) खोज करें।"
                )
            return (
                "Ashwagandha extract in its conventional or natural form is excluded from patentability under Section 3(p) of the Indian Patents Act, "
                "as traditional knowledge and known properties of traditional medicinal plants cannot be patented.\n\n"
                "Key Considerations:\n"
                "• Patentability is possible only if the invention involves a genuinely novel extraction process, a standardized active fraction demonstrating unexpected therapeutic efficacy, or an innovative drug delivery system going beyond traditional knowledge.\n"
                "• Mere solvent extracts, raw powders, or known therapeutic uses documented in classical Ayurvedic texts or the TKDL are strictly non-patentable under Sections 3(p) and 3(e).\n"
                "• Because Ashwagandha is an Indian biological resource, mandatory prior approval from the National Biodiversity Authority (NBA) is legally required under Section 6 of the Biological Diversity Act, 2002 before applying for a patent.\n\n"
                "Practical Next Step: Conduct a thorough prior-art search across the Traditional Knowledge Digital Library (TKDL) and InPASS databases to verify that your specific extraction methodology or technical effect is not already documented in traditional knowledge."
            )

        # 6. Turmeric / Curcumin & Section 3(p) (India)
        if ("turmeric" in q_lower or "haldi" in q_lower or "curcumin" in q_lower) and ("patent" in q_lower or "extract" in q_lower or "3(p)" in q_lower or "3p" in q_lower):
            return (
                "Turmeric (Curcuma longa) and conventional curcumin extracts are excluded from patentability under Section 3(p) as traditional Ayurvedic knowledge, as confirmed by landmark TKDL revocation cases.\n\n"
                "Key Considerations:\n"
                "• Traditional medicinal uses (such as wound healing or anti-inflammatory properties) are part of the public domain and cannot be monopolized.\n"
                "• Patents can only be considered for novel extraction technologies, synthetic derivative molecules, or advanced drug delivery systems (such as liposomal or nanoparticle carriers) demonstrating unexpected technical efficacy.\n"
                "• Prior approval from the National Biodiversity Authority (NBA) is required before commercial patent filing.\n\n"
                "Practical Next Step: Review TKDL prior-art citations and InPASS records to ensure the claim does not overlap with documented classical uses."
            )

        # 7. Neem & Section 3(p) (India)
        if "neem" in q_lower and ("patent" in q_lower or "extract" in q_lower or "3(p)" in q_lower or "3p" in q_lower):
            return (
                "Neem (Azadirachta indica) formulations and conventional extracts are non-patentable under Section 3(p) because its fungicidal, insecticidal, and therapeutic properties form established Indian traditional knowledge.\n\n"
                "Key Considerations:\n"
                "• Landmark revocation cases (such as the EPO neem patent revocation) affirmed that traditional neem uses cannot be patented.\n"
                "• Only inventions with a genuinely novel industrial process or unexpected synergistic properties not disclosed in traditional knowledge may be considered.\n"
                "• Approval from the National Biodiversity Authority is legally mandatory prior to patent filing.\n\n"
                "Practical Next Step: Verify whether the formulation is listed in the Ayurvedic Pharmacopoeia of India (API) or TKDL archives prior to drafting claims."
            )

    return None


