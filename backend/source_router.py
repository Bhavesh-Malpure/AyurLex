"""
source_router.py
----------------
Routes an Ayurlex research question to the most relevant official sources.

Full source catalogue
~~~~~~~~~~~~~~~~~~~~~
India
  • India Code                — Acts, Rules, Ordinances
  • IP India (Patents)        — Patent Act, InPASS search, patent guidelines
  • IP India (TM)             — Trade Marks Act, TM search
  • IP India (Designs)        — Designs Act, Design registry
  • IP India (GI Registry)    — GI Act, registered GIs list
  • TKDL                      — Traditional Knowledge Digital Library
  • Ministry of Ayush         — AYUSH policy, E-Charak
  • NMPB                      — Medicinal plant cultivation & trade
  • NBA / ABS portal          — Biological Diversity Act, ABS approvals
  • CDSCO / CDSCO-ASU        — Drug regulation, Rule 158B, Schedule ASU
  • FSSAI                     — Food / nutraceutical standards

International
  • WIPO — PATENTSCOPE        — Published PCT applications
  • WIPO — PCT System         — PCT procedural texts
  • WIPO — Madrid System      — International trademark registration
  • WIPO — Hague System       — International design registration
  • WIPO — Budapest Treaty    — Deposit of microorganisms
  • WIPO — TK/GRs/TCEs        — Traditional knowledge protection
  • WIPO — GI                 — Lisbon Agreement / GI texts
  • WIPO — Treaties overview  — Paris Convention, Berne etc.
  • WTO — TRIPS               — TRIPS Agreement + Doha Declaration
  • CBD — Nagoya Protocol      — ABS obligations text
  • CBD — Homepage             — Broad biodiversity law

Routing logic
~~~~~~~~~~~~~
* Keyword groups are checked independently; a question may match several
  groups and will receive sources from all of them.
* Sources carry a priority (1 = most targeted, 9 = broad fallback).
* Both India and international branches are always evaluated; the order
  in the returned list is jurisdiction-preference-first.
* The list is de-duplicated by URL before return.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Source catalogue
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OfficialSource:
    title: str
    source_url: str
    jurisdiction: str   # "india" | "international"
    purpose: str
    priority: int = 5   # 1 (most targeted) → 9 (broad fallback)


# ============================================================
# INDIA SOURCES
# ============================================================

# ── India Code (legislation texts) ────────────────────────
INDIA_CODE = OfficialSource(
    title="India Code — Central Legislation Repository",
    source_url="https://www.indiacode.nic.in/",
    jurisdiction="india",
    purpose="Full text of all central Indian Acts and Rules",
    priority=2,
)
INDIA_PATENTS_ACT = OfficialSource(
    title="The Patents Act, 1970 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1392",
    jurisdiction="india",
    purpose="Patent eligibility, Section 3(p)/3(d)/3(e), compulsory licensing",
    priority=1,
)
INDIA_TRADEMARKS_ACT = OfficialSource(
    title="The Trade Marks Act, 1999 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1993",
    jurisdiction="india",
    purpose="Trademark registration, protection, infringement provisions",
    priority=1,
)
INDIA_DESIGNS_ACT = OfficialSource(
    title="The Designs Act, 2000 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1576",
    jurisdiction="india",
    purpose="Design registration, protection period, piracy provisions",
    priority=1,
)
INDIA_GI_ACT = OfficialSource(
    title="The Geographical Indications of Goods Act, 1999 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1944",
    jurisdiction="india",
    purpose="GI registration criteria, producer rights, infringement",
    priority=1,
)
INDIA_BIODIVERSITY_ACT = OfficialSource(
    title="The Biological Diversity Act, 2002 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1937",
    jurisdiction="india",
    purpose="National Biodiversity Authority mandate, ABS obligations, Section 3/6",
    priority=1,
)
INDIA_DRUGS_ACT = OfficialSource(
    title="The Drugs and Cosmetics Act, 1940 — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/1456",
    jurisdiction="india",
    purpose="ASU&H drug schedules, manufacturing standards, market authorisation",
    priority=1,
)
INDIA_PLANTS_ACT = OfficialSource(
    title="The Protection of Plant Varieties and Farmers' Rights Act — India Code",
    source_url="https://www.indiacode.nic.in/handle/123456789/2009",
    jurisdiction="india",
    purpose="Plant variety protection, breeders' rights, farmers' rights",
    priority=2,
)

# ── IP India — Patents / InPASS ────────────────────────────
IP_INDIA = OfficialSource(
    title="IP India — Intellectual Property India",
    source_url="https://ipindia.gov.in/",
    jurisdiction="india",
    purpose="IP India portal: patents, trademarks, designs, GI",
    priority=2,
)
IP_INDIA_PATENTS = OfficialSource(
    title="IP India — Patents Section",
    source_url="https://ipindia.gov.in/patents.htm",
    jurisdiction="india",
    purpose="Patent examination guidelines, Manual of Patent Office Practice",
    priority=2,
)
IP_INDIA_INPASS = OfficialSource(
    title="IP India — InPASS Patent Application Search",
    source_url="https://ipindiaonline.gov.in/epatentfiling/goForLogin/doLogin",
    jurisdiction="india",
    purpose="Search published Indian patent applications and granted patents",
    priority=2,
)
IP_INDIA_PATENT_SEARCH = OfficialSource(
    title="IP India — Patent Search Portal",
    source_url="https://search.ipindia.gov.in/PatentSearch/",
    jurisdiction="india",
    purpose="Bibliographic and full-text search of Indian patent documents",
    priority=2,
)
IP_INDIA_JOURNAL = OfficialSource(
    title="IP India — Official Patent Journal",
    source_url="https://search.ipindia.gov.in/IPOJournal/Journal/Patent",
    jurisdiction="india",
    purpose="Weekly published patent applications and granted patents",
    priority=3,
)

# ── IP India — Trademarks ──────────────────────────────────
IP_INDIA_TM = OfficialSource(
    title="IP India — Trade Marks Registry",
    source_url="https://ipindia.gov.in/trade-marks.htm",
    jurisdiction="india",
    purpose="TM registration process, fees, classification, hearings",
    priority=2,
)
IP_INDIA_TM_SEARCH = OfficialSource(
    title="IP India — TM Public Search",
    source_url="https://search.ipindia.gov.in/IPTS/",
    jurisdiction="india",
    purpose="Search registered and pending Indian trademarks",
    priority=2,
)

# ── IP India — Designs ─────────────────────────────────────
IP_INDIA_DESIGNS = OfficialSource(
    title="IP India — Designs Registry",
    source_url="https://ipindia.gov.in/designs.htm",
    jurisdiction="india",
    purpose="Design registration, classification (Locarno), novelty rules",
    priority=2,
)
IP_INDIA_DESIGN_SEARCH = OfficialSource(
    title="IP India — Design Search Portal",
    source_url="https://ipindiaonline.gov.in/designsearch/",
    jurisdiction="india",
    purpose="Search registered Indian industrial designs",
    priority=2,
)

# ── IP India — GI Registry ────────────────────────────────
IP_INDIA_GI = OfficialSource(
    title="IP India — GI Registry",
    source_url="https://ipindia.gov.in/gi.htm",
    jurisdiction="india",
    purpose="Registered Geographical Indications list, GI Act guidance",
    priority=1,
)

# ── TKDL ──────────────────────────────────────────────────
TKDL = OfficialSource(
    title="Traditional Knowledge Digital Library (TKDL)",
    source_url="https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
    jurisdiction="india",
    purpose="Digitised traditional Ayurveda/Siddha/Unani/Yoga formulations, prior-art defence",
    priority=1,
)
TKDL_SEARCH = OfficialSource(
    title="TKDL — Traditional Formulations Search",
    source_url="https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp",
    jurisdiction="india",
    purpose="Searchable TKDL formulations database (Ayurveda, Unani, Siddha, Yoga)",
    priority=1,
)

# ── Ministry of Ayush / E-Charak ──────────────────────────
MINISTRY_OF_AYUSH = OfficialSource(
    title="Ministry of Ayush — Official Portal",
    source_url="https://ayush.gov.in/",
    jurisdiction="india",
    purpose="AYUSH policy, official guidelines, schemes, regulations",
    priority=2,
)
E_CHARAK_KNOWLEDGE = OfficialSource(
    title="E-Charak — AYUSH Knowledge Resources",
    source_url="https://echarak.ayush.gov.in/knowledge_resources",
    jurisdiction="india",
    purpose="Ayurveda pharmacopoeia, classical formulations, traditional texts",
    priority=1,
)
E_CHARAK_HOME = OfficialSource(
    title="E-Charak Portal — Digital Ayurveda Knowledge Base",
    source_url="https://echarak.ayush.gov.in/",
    jurisdiction="india",
    purpose="Searchable Ayurveda herb profiles, formulas, monographs",
    priority=2,
)
NMPB = OfficialSource(
    title="National Medicinal Plants Board (NMPB)",
    source_url="https://nmpb.nic.in/",
    jurisdiction="india",
    purpose="Medicinal plant cultivation, regulation, trade, sustainability rules",
    priority=3,
)

# ── NBA / ABS Portal ──────────────────────────────────────
NBA_INDIA = OfficialSource(
    title="National Biodiversity Authority (NBA) — ABS Portal",
    source_url="https://nbaindia.org/",
    jurisdiction="india",
    purpose="ABS approvals, Section 3/6 notifications, NBA decisions, BDA compliance",
    priority=1,
)
NBA_ABS = OfficialSource(
    title="NBA — Access and Benefit-Sharing Guidelines",
    source_url="https://nbaindia.org/content/abs-guidlines-protocols",
    jurisdiction="india",
    purpose="NBA ABS guidelines, approval forms, compliance protocols",
    priority=1,
)

# ── CDSCO ─────────────────────────────────────────────────
CDSCO = OfficialSource(
    title="Central Drugs Standard Control Organisation (CDSCO)",
    source_url="https://www.cdsco.gov.in/",
    jurisdiction="india",
    purpose="Drug regulation, clinical trials, market authorisation",
    priority=1,
)
CDSCO_ASU = OfficialSource(
    title="CDSCO — ASU&H Drugs Division",
    source_url="https://www.cdsco.gov.in/opencms/opencms/en/Consumer/Drugs/",
    jurisdiction="india",
    purpose="Ayurveda/Siddha/Unani drug licensing, Rule 158B, GMP, schedules",
    priority=1,
)

# ── FSSAI ─────────────────────────────────────────────────
FSSAI = OfficialSource(
    title="Food Safety and Standards Authority of India (FSSAI)",
    source_url="https://www.fssai.gov.in/",
    jurisdiction="india",
    purpose="Food / nutraceutical regulations, herbal food products",
    priority=1,
)
FSSAI_REGULATIONS = OfficialSource(
    title="FSSAI — Regulations and Standards",
    source_url="https://www.fssai.gov.in/home/fss-legislation/fss-regulations.html",
    jurisdiction="india",
    purpose="Herbal/botanical food standards, health claims, labelling rules",
    priority=2,
)


# ============================================================
# INTERNATIONAL SOURCES
# ============================================================

# ── WIPO — Core ───────────────────────────────────────────
WIPO_TREATIES = OfficialSource(
    title="WIPO — Treaties Portal",
    source_url="https://www.wipo.int/treaties/en/",
    jurisdiction="international",
    purpose="Paris Convention, PCT, Madrid, Hague, Lisbon, Budapest treaty texts",
    priority=1,
)

# ── WIPO — PCT ────────────────────────────────────────────
WIPO_PCT = OfficialSource(
    title="WIPO — PCT (Patent Cooperation Treaty) System",
    source_url="https://www.wipo.int/pct/en/",
    jurisdiction="international",
    purpose="PCT filing procedures, international search, Chapter II examination",
    priority=1,
)
WIPO_PATENTSCOPE = OfficialSource(
    title="WIPO PATENTSCOPE — PCT Application Search",
    source_url="https://www.wipo.int/en/web/patentscope",
    jurisdiction="international",
    purpose="Search published PCT international patent applications",
    priority=1,
)

# ── WIPO — Madrid (TM) ────────────────────────────────────
WIPO_MADRID = OfficialSource(
    title="WIPO — Madrid System (International Trademark Registration)",
    source_url="https://www.wipo.int/madrid/en/",
    jurisdiction="international",
    purpose="International trademark registration under the Madrid System",
    priority=1,
)
WIPO_MADRID_BRAND_DB = OfficialSource(
    title="WIPO — Madrid Monitor (Brand Database)",
    source_url="https://www.wipo.int/branddb/en/",
    jurisdiction="international",
    purpose="Search internationally registered trademarks under Madrid System",
    priority=2,
)

# ── WIPO — Hague (Designs) ────────────────────────────────
WIPO_HAGUE = OfficialSource(
    title="WIPO — Hague System (International Design Registration)",
    source_url="https://www.wipo.int/hague/en/",
    jurisdiction="international",
    purpose="International design registration under the Hague Agreement",
    priority=1,
)

# ── WIPO — Budapest (Microorganisms) ──────────────────────
WIPO_BUDAPEST = OfficialSource(
    title="WIPO — Budapest Treaty (Microorganism Deposit)",
    source_url="https://www.wipo.int/budapest/en/",
    jurisdiction="international",
    purpose="Deposit of microorganisms for patent purposes; IDA list",
    priority=1,
)

# ── WIPO — Traditional Knowledge / GRs / GI ──────────────
WIPO_TK = OfficialSource(
    title="WIPO — Traditional Knowledge & Genetic Resources",
    source_url="https://www.wipo.int/tk/en/",
    jurisdiction="international",
    purpose="WIPO IGC negotiations, defensive TK protection, GRTKF",
    priority=1,
)
WIPO_GI = OfficialSource(
    title="WIPO — Geographical Indications",
    source_url="https://www.wipo.int/geo_indications/en/",
    jurisdiction="international",
    purpose="Lisbon Agreement, GI protection approaches, WIPO GI database",
    priority=2,
)

# ── WTO — TRIPS ───────────────────────────────────────────
WTO_TRIPS = OfficialSource(
    title="WTO — TRIPS Agreement",
    source_url="https://www.wto.org/english/tratop_e/trips_e/trips_e.htm",
    jurisdiction="international",
    purpose="TRIPS patent obligations, Art. 27.3(b), Doha Declaration",
    priority=1,
)
WTO_TRIPS_TK = OfficialSource(
    title="WTO — TRIPS and Traditional Knowledge / Biodiversity",
    source_url="https://www.wto.org/english/tratop_e/trips_e/art27_3b_undo_e.htm",
    jurisdiction="international",
    purpose="TRIPS Art. 27.3(b) — patentability exceptions for plants and TK",
    priority=1,
)

# ── International: EPO ────────────────────────────────────
EPO = OfficialSource(
    title="European Patent Office",
    source_url="https://www.epo.org/en",
    jurisdiction="international",
    purpose="European patent law, patentability guidance and EPO procedures",
    priority=1,
)

# ── CBD / Nagoya Protocol ─────────────────────────────────
CBD_ABS = OfficialSource(
    title="CBD — Nagoya Protocol on ABS",
    source_url="https://www.cbd.int/abs/",
    jurisdiction="international",
    purpose="Nagoya Protocol obligations, ABS Clearing-House, compliance",
    priority=1,
)
CBD_NAGOYA_TEXT = OfficialSource(
    title="CBD — Nagoya Protocol Full Text",
    source_url="https://www.cbd.int/abs/text/",
    jurisdiction="international",
    purpose="Official text of the Nagoya Protocol on ABS (2010)",
    priority=1,
)
CBD_HOME = OfficialSource(
    title="Convention on Biological Diversity — Main Portal",
    source_url="https://www.cbd.int/",
    jurisdiction="international",
    purpose="CBD obligations, biodiversity law, GRs, digital sequence information",
    priority=2,
)


# ---------------------------------------------------------------------------
# Keyword groups
# ---------------------------------------------------------------------------

PATENT_KEYWORDS = [
    "patent", "patentable", "patentability", "invention", "novelty",
    "inventive step", "prior art", "section 3", "3(p)", "3(d)", "3(e)",
    "non-obvious", "utility", "claim", "specification", "filing",
    "examiner", "grant", "opposition", "revocation", "inpass",
    "patent application", "patent search", "granted patent",
]

PCT_KEYWORDS = [
    "pct", "patent cooperation treaty", "international application",
    "chapter ii", "international search", "isa", "international preliminary",
    "wo number", "pct filing", "national phase",
]

FORMULATION_KEYWORDS = [
    "formulation", "proprietary medicine", "classical", "polyherbal",
    "compound", "dosage", "tablet", "capsule", "churna", "kalpa",
    "vati", "asava", "aristha", "ghrita", "tailam", "bhasma",
    "chyavanprash", "rasayana",
]

AYURVEDA_KEYWORDS = [
    "ayurveda", "ayurvedic", "ayush", "herbal", "herb", "botanical",
    "traditional medicine", "traditional knowledge", "indigenous",
    "turmeric", "ashwagandha", "neem", "tulsi", "brahmi", "shatavari",
    "triphala", "panchakarma", "charak", "sushrut", "charaka", "sushruta",
    "pharmacopoeia", "api", "siddha", "unani", "homeopathy",
    "rasayana", "panchakarma", "ashtanga",
]

TKDL_KEYWORDS = [
    "tkdl", "traditional knowledge digital library", "prior art ayurveda",
    "siddha prior art", "unani prior art", "yoga prior art",
    "biopiracy", "bio piracy", "traditional formulation prior art",
    "traditional knowledge defense", "prior art traditional",
]

DRUG_MANUFACTURING_KEYWORDS = [
    "drug", "medicine", "clinical trial", "manufacturing", "quality",
    "approval", "license", "rule 158", "gmp", "good manufacturing",
    "cdsco", "central drugs", "pharmacopoeial", "standard",
    "asu", "asu&h", "schedule h", "schedule m", "market authorisation",
    "drug controller", "dcgi",
]

FOOD_KEYWORDS = [
    "food", "aahara", "label", "supplement", "nutraceutical",
    "functional food", "dietary supplement", "fssai", "food safety",
    "health claim", "nutrition", "food standard",
]

TRADEMARK_KEYWORDS = [
    "trademark", "trade mark", "brand", "logo", "mark", "passing off",
    "infringement", "well-known mark", "service mark", "collective mark",
    "certification mark", "tm registration", "tm search",
]

MADRID_KEYWORDS = [
    "madrid", "madrid system", "international trademark", "madrid protocol",
    "madrid agreement", "international registration trademark",
    "wipo trademark", "brand database", "madrid monitor",
]

DESIGN_KEYWORDS = [
    "design", "industrial design", "product design", "ornamental",
    "aesthetic", "locarno", "design registration", "design search",
    "hague", "design piracy", "design patent",
]

HAGUE_KEYWORDS = [
    "hague", "hague system", "international design", "hague agreement",
    "hague registration", "international design registration",
]

GI_KEYWORDS = [
    "geographical indication", "gi tag", "gi registration", "gi act",
    "place of origin", "origin", "darjeeling", "basmati",
    "lisbon", "lisbon agreement",
]

BUDAPEST_KEYWORDS = [
    "budapest", "budapest treaty", "microorganism", "microbial deposit",
    "depositary authority", "ida", "biological deposit", "culture deposit",
]

BIODIVERSITY_KEYWORDS = [
    "biodiversity", "biological resource", "traditional knowledge",
    "benefit sharing", "access and benefit", "nagoya", "abs",
    "nba", "national biodiversity", "biological diversity act",
    "genetic resource", "bioprospecting", "biopiracy",
    "prior informed consent", "pic", "mutually agreed terms", "mat",
]

MEDICINAL_PLANT_KEYWORDS = [
    "medicinal plant", "plant cultivation", "nmpb", "national medicinal plants",
    "wild collection", "cultivation", "sustainable harvest",
    "plant variety", "farmers rights", "breeder", "ppvfr",
]

TRIPS_KEYWORDS = [
    "trips", "wto", "trade related", "compulsory license",
    "doha declaration", "public health", "art 27", "article 27",
    "evergreening", "bolar exemption",
]

WIPO_TK_KEYWORDS = [
    "wipo", "igc", "traditional knowledge protection",
    "genetic resources protection", "defensive protection",
    "traditional cultural expression", "tce", "grtkf",
    "wipo committee", "igs",
]

LATEST_PATENT_KEYWORDS = [
    "latest patent", "new patent", "published patent", "patent publication",
    "patentscope", "pct application", "wo number",
]

EPO_KEYWORDS = [
    "european patent office", "epo", "european patent", "european patents",
    "ep application", "ep patent", "ep convention",
]


# ---------------------------------------------------------------------------
# Routing helpers
# ---------------------------------------------------------------------------

def _has_any_keyword(question: str, keywords: list[str]) -> bool:
    normalised = question.lower()
    return any(kw in normalised for kw in keywords)


def _deduplicate_by_url(
    sources: list[OfficialSource],
) -> list[OfficialSource]:
    seen_urls: set[str] = set()
    result: list[OfficialSource] = []
    for source in sources:
        if source.source_url not in seen_urls:
            result.append(source)
            seen_urls.add(source.source_url)
    return result


# ---------------------------------------------------------------------------
# Public router
# ---------------------------------------------------------------------------

def route_question_to_sources(
    question: str,
    jurisdiction: str,
) -> list[OfficialSource]:
    """
    Return an ordered, de-duplicated list of ``OfficialSource`` objects
    relevant to *question* and *jurisdiction*.

    Sources are sorted by ``priority`` (lower = most targeted) so
    callers can confidently slice from the front.

    Both India and international branches are always evaluated; the
    requested jurisdiction appears first in the returned list.
    """
    india_sources: list[OfficialSource] = []
    intl_sources: list[OfficialSource] = []

    # ── India: Patents ─────────────────────────────────────────────────────
    if _has_any_keyword(question, PATENT_KEYWORDS + FORMULATION_KEYWORDS):
        india_sources.extend([
            INDIA_PATENTS_ACT,
            IP_INDIA_PATENTS,
            IP_INDIA,
            IP_INDIA_PATENT_SEARCH,
        ])

    if _has_any_keyword(question, LATEST_PATENT_KEYWORDS):
        india_sources.extend([IP_INDIA_JOURNAL, IP_INDIA_INPASS])

    # ── India: Trademarks ──────────────────────────────────────────────────
    if _has_any_keyword(question, TRADEMARK_KEYWORDS):
        india_sources.extend([
            INDIA_TRADEMARKS_ACT,
            IP_INDIA_TM,
            IP_INDIA_TM_SEARCH,
        ])

    # ── India: Designs ─────────────────────────────────────────────────────
    if _has_any_keyword(question, DESIGN_KEYWORDS):
        india_sources.extend([
            INDIA_DESIGNS_ACT,
            IP_INDIA_DESIGNS,
            IP_INDIA_DESIGN_SEARCH,
        ])

    # ── India: GI ─────────────────────────────────────────────────────────
    if _has_any_keyword(question, GI_KEYWORDS):
        india_sources.extend([
            INDIA_GI_ACT,
            IP_INDIA_GI,
        ])

    # ── India: TKDL ────────────────────────────────────────────────────────
    if _has_any_keyword(question, TKDL_KEYWORDS + AYURVEDA_KEYWORDS):
        india_sources.extend([TKDL, TKDL_SEARCH])

    # ── India: Ayurveda / AYUSH ────────────────────────────────────────────
    if _has_any_keyword(question, AYURVEDA_KEYWORDS + FORMULATION_KEYWORDS):
        india_sources.extend([
            E_CHARAK_KNOWLEDGE,
            E_CHARAK_HOME,
            MINISTRY_OF_AYUSH,
        ])

    # ── India: Drugs / Manufacturing ───────────────────────────────────────
    if _has_any_keyword(question, DRUG_MANUFACTURING_KEYWORDS):
        india_sources.extend([CDSCO, CDSCO_ASU, INDIA_DRUGS_ACT])

    # ── India: Food ────────────────────────────────────────────────────────
    if _has_any_keyword(question, FOOD_KEYWORDS):
        india_sources.extend([FSSAI, FSSAI_REGULATIONS])

    # ── India: Biodiversity / ABS / NBA ────────────────────────────────────
    if _has_any_keyword(question, BIODIVERSITY_KEYWORDS):
        india_sources.extend([
            NBA_INDIA,
            NBA_ABS,
            INDIA_BIODIVERSITY_ACT,
        ])

    # ── India: Medicinal Plants / PPVFR ────────────────────────────────────
    if _has_any_keyword(question, MEDICINAL_PLANT_KEYWORDS):
        india_sources.extend([NMPB, INDIA_PLANTS_ACT])

    # ── India: General IP / India Code ─────────────────────────────────────
    if _has_any_keyword(
        question,
        PATENT_KEYWORDS + TRADEMARK_KEYWORDS + DESIGN_KEYWORDS + GI_KEYWORDS,
    ):
        india_sources.append(IP_INDIA)
        india_sources.append(INDIA_CODE)

    # ── International: EPO ────────────────────────────────────────────────
    if _has_any_keyword(question, EPO_KEYWORDS):
        intl_sources.insert(0, EPO)

    # ── International: PCT ─────────────────────────────────────────────────
    if _has_any_keyword(question, PCT_KEYWORDS + LATEST_PATENT_KEYWORDS):
        intl_sources.extend([WIPO_PCT, WIPO_PATENTSCOPE])

    if _has_any_keyword(question, PATENT_KEYWORDS + FORMULATION_KEYWORDS):
        intl_sources.extend([WIPO_TREATIES, WTO_TRIPS])

    # ── International: Madrid (TM) ─────────────────────────────────────────
    if _has_any_keyword(question, TRADEMARK_KEYWORDS + MADRID_KEYWORDS):
        intl_sources.extend([WIPO_MADRID, WIPO_MADRID_BRAND_DB])

    # ── International: Hague (Designs) ────────────────────────────────────
    if _has_any_keyword(question, DESIGN_KEYWORDS + HAGUE_KEYWORDS):
        intl_sources.extend([WIPO_HAGUE])

    # ── International: Budapest (Microorganisms) ───────────────────────────
    if _has_any_keyword(question, BUDAPEST_KEYWORDS):
        intl_sources.append(WIPO_BUDAPEST)

    # ── International: GI ─────────────────────────────────────────────────
    if _has_any_keyword(question, GI_KEYWORDS):
        intl_sources.extend([WIPO_GI, WIPO_TREATIES])

    # ── International: TK / GRs ────────────────────────────────────────────
    if _has_any_keyword(
        question,
        WIPO_TK_KEYWORDS + TKDL_KEYWORDS + BIODIVERSITY_KEYWORDS,
    ):
        intl_sources.append(WIPO_TK)

    # ── International: TRIPS ───────────────────────────────────────────────
    if _has_any_keyword(question, TRIPS_KEYWORDS):
        intl_sources.extend([WTO_TRIPS, WTO_TRIPS_TK, WIPO_TREATIES])

    # ── International: Nagoya / CBD ────────────────────────────────────────
    if _has_any_keyword(question, BIODIVERSITY_KEYWORDS):
        intl_sources.extend([CBD_ABS, CBD_NAGOYA_TEXT, CBD_HOME])

    # ── International: Ayurveda (international treaties) ──────────────────
    if _has_any_keyword(question, AYURVEDA_KEYWORDS):
        intl_sources.extend([WIPO_TK, CBD_ABS])

    # ── Compose based on strict jurisdiction separation (Rule 2) ───────────
    if jurisdiction == "india":
        combined = [s for s in india_sources if s.jurisdiction == "india"]
    elif jurisdiction == "international":
        combined = [s for s in intl_sources if s.jurisdiction == "international"]
    else:
        combined = india_sources + intl_sources

    # ── Fallback: nothing matched ─────────────────────────────────────────
    if not combined:
        if jurisdiction == "india":
            combined = [
                E_CHARAK_KNOWLEDGE,
                MINISTRY_OF_AYUSH,
                INDIA_PATENTS_ACT,
                INDIA_CODE,
            ]
        else:
            combined = [WIPO_TREATIES, WTO_TRIPS, CBD_ABS]

    deduped = _deduplicate_by_url(combined)
    deduped.sort(key=lambda s: s.priority)
    return deduped