"""
corpus_seeder.py
----------------
Seeds the Ayurlex database with offline corpus content so queries always
return meaningful results even when government portals are unreachable.

What it seeds
~~~~~~~~~~~~~
1. The Patents Act, 1970 PDF (if present in data/)
2. Embedded essential legal knowledge chunks covering:
   - Key patent sections (3(d), 3(p), 3(e), etc.)
   - Ayurveda IP protection concepts
   - TKDL and prior-art defence
   - TRIPS obligations
   - Biological Diversity Act / Nagoya Protocol
   - Drug regulation for ASU&H
"""

import logging
from pathlib import Path

from database import get_connection, rebuild_fts_index

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
PDF_PATH = DATA_DIR / "patents_act_1970_2024.pdf"

# ---------------------------------------------------------------------------
# Embedded knowledge chunks — sourced from official statutory text
# ---------------------------------------------------------------------------
# These are faithful excerpts and summaries from publicly available
# legislation and treaty texts.  They serve as the fallback corpus when
# live government portals return 403/404.

EMBEDDED_CORPUS: list[dict] = [
    # ── Patents Act, 1970 — Key Sections ────────────────────────────────
    {
        "title": "The Patents Act, 1970 — Section 3(d)",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Section 3(d) — Non-patentable inventions",
        "content": (
            "Section 3(d) of the Patents Act, 1970 states that the mere discovery of a new form of a "
            "known substance which does not result in the enhancement of the known efficacy of that "
            "substance is not patentable. For the purposes of this clause, salts, esters, ethers, "
            "polymorphs, metabolites, pure form, particle size, isomers, mixtures of isomers, complexes, "
            "combinations and other derivatives of known substance shall be considered to be the same "
            "substance, unless they differ significantly in properties with regard to efficacy. "
            "This provision is particularly significant for pharmaceutical patents and prevents "
            "'evergreening' — the practice of obtaining new patents on minor modifications of existing "
            "drugs to extend monopoly protection. The Supreme Court of India upheld this provision in "
            "the landmark Novartis v. Union of India (2013) case, where the patent application for "
            "the beta-crystalline form of imatinib mesylate (Gleevec) was rejected under Section 3(d). "
            "This section is critical in the context of Ayurvedic formulations because traditional "
            "knowledge-based modifications of known substances must demonstrate enhanced therapeutic "
            "efficacy to qualify for patent protection."
        ),
    },
    {
        "title": "The Patents Act, 1970 — Section 3(p)",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Section 3(p) — Traditional knowledge exclusion",
        "content": (
            "Section 3(p) of the Patents Act, 1970 provides that an invention which, in effect, "
            "is traditional knowledge or which is an aggregation or duplication of known properties "
            "of traditionally known component or components is not patentable. This section was "
            "inserted by the Patents (Amendment) Act, 2005 and is one of the most important "
            "provisions protecting India's traditional knowledge heritage, including Ayurveda, "
            "Siddha, Unani, and Yoga practices. Section 3(p) works in conjunction with the "
            "Traditional Knowledge Digital Library (TKDL) database, which documents traditional "
            "formulations from classical Ayurvedic texts like Charaka Samhita, Sushruta Samhita, "
            "and Ashtanga Hridaya. When a patent application claims an invention that is essentially "
            "traditional knowledge documented in the TKDL or other classical texts, the patent "
            "examiner can reject it under Section 3(p). This provision has been instrumental in "
            "defeating several biopiracy attempts, including the revocation of turmeric and neem "
            "patents at international patent offices."
        ),
    },
    {
        "title": "The Patents Act, 1970 — Section 3(e)",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Section 3(e) — Admixtures and known processes",
        "content": (
            "Section 3(e) of the Patents Act, 1970 excludes from patentability a substance obtained "
            "by a mere admixture resulting only in the aggregation of the properties of the components "
            "thereof or a process for producing such substance. This provision is relevant to Ayurvedic "
            "and herbal formulations because many traditional polyherbal compositions are combinations "
            "of known plant-based ingredients. A new polyherbal formulation that merely combines known "
            "herbs without producing a synergistic effect beyond the sum of individual properties would "
            "be excluded under Section 3(e). However, if scientific evidence demonstrates unexpected "
            "synergistic pharmacological activity — such as enhanced bioavailability, novel mechanism "
            "of action, or significantly improved therapeutic outcomes — the formulation may overcome "
            "the Section 3(e) bar. The burden of proof lies on the applicant to demonstrate the "
            "synergistic or unexpected result through clinical or pre-clinical data."
        ),
    },
    {
        "title": "The Patents Act, 1970 — Section 2(1)(j) Definition of Invention",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Section 2(1)(j) — Definition of Invention",
        "content": (
            "Section 2(1)(j) of the Patents Act, 1970 defines 'invention' as a new product or "
            "process involving an inventive step and capable of industrial application. 'Inventive "
            "step' is defined under Section 2(1)(ja) as a feature of an invention that involves "
            "technical advance as compared to existing knowledge or having economic significance or "
            "both, and that makes the invention not obvious to a person skilled in the art. 'New "
            "invention' under Section 2(1)(l) means any invention or technology which has not been "
            "anticipated by publication in any document or used in the country or elsewhere in the "
            "world before the date of filing of patent application with complete specification. For "
            "Ayurvedic innovations, this means the invention must demonstrate novelty over existing "
            "traditional knowledge, an inventive step that advances beyond common knowledge in the "
            "field, and capability for industrial-scale manufacture."
        ),
    },
    {
        "title": "The Patents Act, 1970 — Section 25 Opposition",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Section 25 — Opposition to patent",
        "content": (
            "Section 25 of the Patents Act, 1970 provides for opposition to the grant of a patent. "
            "Section 25(1) allows pre-grant opposition by 'any person' who can file a representation "
            "to the Controller before the grant. Section 25(2) allows post-grant opposition by 'any "
            "person interested' within one year of the date of publication of grant. Grounds for "
            "opposition include: (a) wrongful obtaining of the invention; (b) prior publication; "
            "(c) prior claim in an Indian application; (d) prior public knowledge or use in India; "
            "(e) obviousness / lack of inventive step; (f) non-patentable subject matter under "
            "Section 3; (g) insufficient description; (h) non-disclosure of information under "
            "Section 8; (i) non-filing of application in convention country; (j) non-compliance "
            "with Biological Diversity Act, 2002; (k) that the invention is traditional knowledge "
            "(Section 3(p)). This is crucial for challenging biopiracy patents on Ayurvedic "
            "formulations and traditional knowledge."
        ),
    },
    {
        "title": "The Patents Act, 1970 — Compulsory Licensing (Sections 84-92)",
        "source_url": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf",
        "jurisdiction": "india",
        "section_label": "Sections 84-92 — Compulsory Licensing",
        "content": (
            "Sections 84 to 92 of the Patents Act, 1970 provide for compulsory licensing. Under "
            "Section 84, any person interested can apply for a compulsory licence after three years "
            "from the date of grant if: (a) the reasonable requirements of the public with respect "
            "to the patented invention have not been satisfied; (b) the patented invention is not "
            "available to the public at a reasonably affordable price; or (c) the patented invention "
            "is not worked in the territory of India. Section 92 provides for compulsory licensing "
            "in circumstances of national emergency, extreme urgency, or public non-commercial use. "
            "India granted its first compulsory licence in 2012 (Natco Pharma v. Bayer) for the "
            "cancer drug sorafenib tosylate (Nexavar). These provisions are significant for ensuring "
            "access to patented pharmaceutical and traditional medicine-based products at affordable "
            "prices in India."
        ),
    },

    # ── TKDL & Prior Art Defence ───────────────────────────────────────
    {
        "title": "Traditional Knowledge Digital Library (TKDL)",
        "source_url": "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
        "jurisdiction": "india",
        "section_label": "TKDL — Overview and Legal Framework",
        "content": (
            "The Traditional Knowledge Digital Library (TKDL) is a collaborative project between "
            "the Council of Scientific and Industrial Research (CSIR) and the Ministry of Ayush, "
            "Government of India. Established in 2001, the TKDL digitises and classifies traditional "
            "knowledge from Indian systems of medicine — Ayurveda, Siddha, Unani, and Yoga — into "
            "a structured, searchable database accessible to patent examiners worldwide. The TKDL "
            "contains over 4.5 lakh (450,000) formulations derived from classical texts including "
            "Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, Bhavaprakash Nighantu, Sharangdhara "
            "Samhita, and Rasatarangini among others. Formulations are classified using the "
            "Traditional Knowledge Resource Classification (TKRC) system, which maps Ayurvedic "
            "concepts to the International Patent Classification (IPC). The TKDL has been "
            "instrumental in defeating over 250 patent applications at international patent offices "
            "(EPO, USPTO, JPO) by providing prior art evidence. Access agreements have been signed "
            "with the EPO, USPTO, JPO, IP Australia, UKIPO, CIPO (Canada), DPMA (Germany), and "
            "other patent offices. The database is available in English, French, German, Spanish, "
            "and Japanese, enabling patent examiners to identify prior art from Indian traditional "
            "knowledge during patent examination."
        ),
    },
    {
        "title": "TKDL — Biopiracy Cases and Prior Art Defence",
        "source_url": "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
        "jurisdiction": "india",
        "section_label": "TKDL — Landmark Biopiracy Cases",
        "content": (
            "The TKDL has been crucial in challenging biopiracy — the misappropriation of traditional "
            "knowledge through patents. Key cases include: (1) Turmeric Patent (US 5,401,504, 1995): "
            "The University of Mississippi Medical Center obtained a US patent on the wound-healing "
            "properties of turmeric (Curcuma longa). CSIR challenged this at the USPTO, providing "
            "evidence from ancient Sanskrit texts documenting turmeric's medicinal use for centuries. "
            "The patent was revoked in 1997 — the first time a traditional knowledge-based patent was "
            "successfully challenged. (2) Neem Patent (EP 0436257, 1994): W.R. Grace Company and "
            "USDA obtained a European patent on the fungicidal properties of neem (Azadirachta indica). "
            "India, with support from international NGOs, challenged the patent at the EPO. The patent "
            "was revoked in 2005 after demonstrating prior art from Indian traditional practices. "
            "(3) Basmati Rice (US patent by RiceTec): RiceTec Inc. obtained patents on Basmati rice "
            "lines. India challenged the claims, and most were either withdrawn or narrowed. "
            "(4) Ashwagandha, Jamun, and Karela patents have also been challenged using TKDL evidence. "
            "These cases demonstrate the importance of documenting traditional knowledge as prior art "
            "to prevent its misappropriation through the patent system."
        ),
    },

    # ── Ayurveda & IP Protection ───────────────────────────────────────
    {
        "title": "Ayurveda Intellectual Property — Patentability Framework",
        "source_url": "https://ayush.gov.in/",
        "jurisdiction": "india",
        "section_label": "Ayurveda IP — Patentability Analysis",
        "content": (
            "Patenting Ayurvedic innovations in India requires navigating several legal provisions: "
            "(1) Section 3(p) — bars patents on traditional knowledge or aggregation of known properties "
            "of traditionally known components. An Ayurvedic invention must go BEYOND mere traditional "
            "knowledge to be patentable. (2) Section 3(d) — bars patents on new forms of known "
            "substances unless enhanced efficacy is demonstrated. Ayurvedic reformulations must show "
            "measurably improved therapeutic outcomes. (3) Section 3(e) — bars patents on mere "
            "admixtures. Polyherbal combinations must demonstrate synergistic effects. "
            "PATENTABLE Ayurvedic innovations include: (a) Novel extraction processes yielding "
            "standardised active compounds with improved bioavailability; (b) Novel drug delivery "
            "systems (nanoparticles, liposomes) for traditional compounds; (c) Synergistic polyherbal "
            "compositions with demonstrated unexpected pharmacological effects; (d) Novel quality "
            "control methods, biomarker identification, and standardisation techniques; "
            "(e) New therapeutic applications of known Ayurvedic compounds backed by clinical evidence. "
            "NON-PATENTABLE: Classical formulations documented in Ayurvedic Pharmacopoeia of India "
            "(API), known herb combinations without synergistic evidence, and mere isolation of "
            "active ingredients from well-known medicinal plants."
        ),
    },
    {
        "title": "Ayurvedic Pharmacopoeia of India (API)",
        "source_url": "https://echarak.ayush.gov.in/knowledge_resources",
        "jurisdiction": "india",
        "section_label": "Ayurvedic Pharmacopoeia of India",
        "content": (
            "The Ayurvedic Pharmacopoeia of India (API) is an official document published by the "
            "Government of India (Ministry of Ayush) containing monographs of single drugs and "
            "compound formulations used in Ayurveda. It is published in multiple parts and volumes. "
            "Part I covers single drugs (plant-origin, animal-origin, and mineral-origin drugs) with "
            "monographs detailing: botanical/zoological name, Sanskrit synonyms, therapeutic properties "
            "(Rasa, Guna, Virya, Vipaka, Prabhava), therapeutic indications, dosage, and quality "
            "standards (identity tests, purity, assay, physicochemical constants). Part II covers "
            "compound formulations (Yoga) with details of ingredients, method of preparation, "
            "therapeutic indications, and quality standards. The API serves as the legal standard for "
            "quality and identity of Ayurvedic drugs under the Drugs and Cosmetics Act, 1940 (Schedule "
            "T and First Schedule). The API is crucial prior art documentation — formulations listed "
            "in the API cannot be patented as they constitute published traditional knowledge. "
            "E-Charak (echarak.ayush.gov.in) provides digital access to API monographs and classical "
            "Ayurvedic formulations."
        ),
    },

    # ── Biological Diversity Act ───────────────────────────────────────
    {
        "title": "Biological Diversity Act, 2002",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1937",
        "jurisdiction": "india",
        "section_label": "Biological Diversity Act — Key Provisions",
        "content": (
            "The Biological Diversity Act, 2002 (BDA) implements India's obligations under the "
            "Convention on Biological Diversity (CBD) and the Nagoya Protocol. Key provisions: "
            "Section 3 requires prior approval of the National Biodiversity Authority (NBA) for "
            "foreign nationals and foreign-controlled companies to obtain biological resources "
            "occurring in India for research, commercial utilisation, bio-survey, or bio-utilisation. "
            "Section 6 requires prior approval of the NBA before applying for any intellectual "
            "property right (including patents) based on research or information on a biological "
            "resource obtained from India. Section 7 requires Indian citizens and companies to give "
            "prior intimation to the State Biodiversity Board before obtaining biological resources "
            "for commercial utilisation. Section 18 mandates equitable benefit-sharing with local "
            "communities. Section 21 requires the NBA to determine benefit-sharing including: "
            "monetary payments, royalties, joint ventures, technology transfer, and contribution "
            "to a common fund. Non-compliance attracts penalties under Section 55 (imprisonment up "
            "to 5 years and/or fine up to Rs. 10 lakhs). This Act is critical for Ayurvedic "
            "innovations using Indian medicinal plants — patent applicants must demonstrate NBA "
            "compliance, and non-compliance is a ground for pre/post-grant opposition under "
            "Section 25(1)(k) / 25(2)(k) of the Patents Act."
        ),
    },

    # ── TRIPS Agreement ────────────────────────────────────────────────
    {
        "title": "WTO TRIPS Agreement — Patent Obligations",
        "source_url": "https://www.wto.org/english/tratop_e/trips_e/trips_e.htm",
        "jurisdiction": "international",
        "section_label": "TRIPS — Patent Standards and Flexibilities",
        "content": (
            "The Agreement on Trade-Related Aspects of Intellectual Property Rights (TRIPS) is "
            "administered by the WTO and sets minimum standards for IP protection. Key patent "
            "provisions: Article 27.1 requires patents to be available for any inventions (products "
            "or processes) in all fields of technology, provided they are new, involve an inventive "
            "step, and are capable of industrial application. Article 27.2 allows members to exclude "
            "inventions from patentability to protect public order, morality, or to protect human, "
            "animal, or plant life or health. Article 27.3(b) allows members to exclude plants and "
            "animals (other than micro-organisms) and essentially biological processes from "
            "patentability. Article 28 defines the rights conferred by a patent. Article 31 provides "
            "for compulsory licensing under certain conditions. Article 33 sets minimum patent term "
            "at 20 years from filing date. The Doha Declaration on TRIPS and Public Health (2001) "
            "affirmed that TRIPS should be interpreted to support WTO Members' right to protect "
            "public health and promote access to medicines. India's Patents Act provisions (like "
            "Section 3(d)) are considered TRIPS-compliant as TRIPS allows exclusions and flexibilities."
        ),
    },
    {
        "title": "TRIPS Article 27.3(b) — Traditional Knowledge and Biodiversity",
        "source_url": "https://www.wto.org/english/tratop_e/trips_e/art27_3b_undo_e.htm",
        "jurisdiction": "international",
        "section_label": "TRIPS Art. 27.3(b) — TK/Biodiversity Review",
        "content": (
            "Article 27.3(b) of TRIPS allows WTO members to exclude plants, animals, and essentially "
            "biological processes from patentability. It requires members to provide protection for "
            "plant varieties either by patents, a sui generis system, or a combination. India has "
            "implemented this through the Protection of Plant Varieties and Farmers' Rights Act, 2001. "
            "The TRIPS Council has been reviewing Art. 27.3(b) in relation to: (a) the relationship "
            "between TRIPS and the Convention on Biological Diversity (CBD); (b) protection of "
            "traditional knowledge and folklore; and (c) disclosure of origin of biological resources "
            "and traditional knowledge in patent applications. India and other developing countries "
            "have proposed amending TRIPS to require: (i) mandatory disclosure of source/origin of "
            "biological resources and TK used in inventions; (ii) evidence of prior informed consent "
            "(PIC) from the country of origin; (iii) evidence of fair and equitable benefit-sharing. "
            "These proposals aim to prevent biopiracy and ensure that patent systems do not facilitate "
            "misappropriation of traditional knowledge and genetic resources."
        ),
    },

    # ── Nagoya Protocol ────────────────────────────────────────────────
    {
        "title": "CBD — Nagoya Protocol on Access and Benefit-Sharing",
        "source_url": "https://www.cbd.int/abs/text/",
        "jurisdiction": "international",
        "section_label": "Nagoya Protocol — ABS Framework",
        "content": (
            "The Nagoya Protocol on Access to Genetic Resources and the Fair and Equitable Sharing "
            "of Benefits Arising from their Utilization (2010) is a supplementary agreement to the "
            "Convention on Biological Diversity. It provides a transparent legal framework for the "
            "effective implementation of the CBD's third objective: fair and equitable benefit-sharing. "
            "Key provisions: Article 5 requires benefits arising from utilisation of genetic resources "
            "and traditional knowledge to be shared fairly and equitably with the provider country. "
            "Article 6 requires that access to genetic resources is subject to Prior Informed Consent "
            "(PIC) of the providing country. Article 7 requires access to traditional knowledge "
            "associated with genetic resources held by indigenous and local communities to be subject "
            "to their PIC or approval. Article 12 recognises community protocols and customary laws. "
            "India ratified the Nagoya Protocol in 2012 and implements it through the Biological "
            "Diversity Act, 2002 and the NBA. Any researcher or company seeking to use Indian "
            "biological resources or associated traditional knowledge (including Ayurvedic knowledge) "
            "must comply with ABS requirements."
        ),
    },

    # ── Drug Regulation for ASU&H ──────────────────────────────────────
    {
        "title": "Drugs and Cosmetics Act, 1940 — ASU&H Drug Regulation",
        "source_url": "https://www.cdsco.gov.in/opencms/opencms/en/Consumer/Drugs/",
        "jurisdiction": "india",
        "section_label": "ASU&H Drug Regulation Framework",
        "content": (
            "Ayurveda, Siddha, Unani, and Homoeopathy (ASU&H) drugs are regulated under the "
            "Drugs and Cosmetics Act, 1940 and Rules thereunder. Key regulatory provisions: "
            "Section 3(a) defines 'Ayurvedic, Siddha or Unani drug' to include all medicines "
            "intended for internal/external use for diagnosis, treatment, mitigation, or prevention "
            "of disease in human beings/animals, and mentioned in authoritative classical texts "
            "(First Schedule). Rule 158B and Schedule T prescribe Good Manufacturing Practices "
            "(GMP) for ASU&H drugs. Manufacturing requires a licence from the State Licensing "
            "Authority. Proprietary Ayurvedic medicines (not in classical texts) require additional "
            "documentation. The Ayurvedic Pharmacopoeia of India (API) provides official quality "
            "standards. Classical formulations from approved texts can be manufactured without "
            "clinical trials, but proprietary formulations need approval. Schedule E-1 lists "
            "poisonous/potent Ayurvedic substances requiring cautionary labelling. The CDSCO's "
            "ASU&H Division oversees regulatory approvals, clinical trials, and quality standards. "
            "AYUSH Mark certification scheme ensures quality of ASU&H products."
        ),
    },

    # ── WIPO Traditional Knowledge ─────────────────────────────────────
    {
        "title": "WIPO — Traditional Knowledge Protection Framework",
        "source_url": "https://www.wipo.int/tk/en/",
        "jurisdiction": "international",
        "section_label": "WIPO IGC — TK Protection",
        "content": (
            "WIPO's Intergovernmental Committee on Intellectual Property and Genetic Resources, "
            "Traditional Knowledge and Folklore (IGC) has been negotiating international legal "
            "instruments for the protection of TK, genetic resources (GRs), and traditional cultural "
            "expressions (TCEs) since 2000. Two approaches to TK protection exist: (1) Defensive "
            "protection — preventing the grant of invalid IP rights over TK. This includes databases "
            "like India's TKDL, disclosure requirements in patent applications, and amendments to "
            "patent examination guidelines to consider TK as prior art. (2) Positive protection — "
            "providing rights to TK holders to control the use of their knowledge. This includes "
            "sui generis legislation (like India's BDA, 2002), contractual arrangements (ABS "
            "agreements), and customary laws. In May 2024, WIPO member states adopted a landmark "
            "treaty (WIPO Treaty on Intellectual Property, Genetic Resources and Associated "
            "Traditional Knowledge) requiring patent applicants to disclose the country of origin "
            "or source of genetic resources and associated traditional knowledge used in claimed "
            "inventions. India has been a leading advocate for this treaty."
        ),
    },

    # ── WIPO Classifications (Nice and Locarno) ────────────────────────
    {
        "title": "WIPO — Nice Classification (Goods and Services)",
        "source_url": "https://www.wipo.int/classifications/nice/en/",
        "jurisdiction": "international",
        "section_label": "Nice Agreement — Classification of Goods and Services",
        "content": (
            "The Nice Classification (NCL), established by the Nice Agreement (1957) and administered "
            "by the World Intellectual Property Organization (WIPO), is an international system used to "
            "classify goods and services for the purposes of the registration of marks. The classification "
            "consists of 45 classes in total: Classes 1 to 34 cover goods (including pharmaceuticals, "
            "herbal preparations, dietary supplements, and Ayurvedic medicinal products under Class 5), "
            "and Classes 35 to 45 cover services (such as medical, hygiene, beauty care, and Ayurvedic therapy "
            "services under Class 44). WIPO continuously publishes updated editions and versions of the Nice "
            "Classification."
        ),
    },
    {
        "title": "WIPO — Locarno Classification (Industrial Designs)",
        "source_url": "https://www.wipo.int/classifications/locarno/en/",
        "jurisdiction": "international",
        "section_label": "Locarno Agreement — Classification for Industrial Designs",
        "content": (
            "The Locarno Classification, established by the Locarno Agreement (1968) and administered "
            "by the World Intellectual Property Organization (WIPO), is an international classification "
            "system for goods for the purposes of the registration of industrial designs. The Locarno "
            "Classification comprises 32 classes and 219 subclasses, accompanied by explanatory notes "
            "and an alphabetical list of goods. Administered by WIPO, it provides a structured framework "
            "for categorising and searching industrial designs worldwide, including packaging, bottles, "
            "and dispensers commonly used for traditional medicine and pharmaceutical products."
        ),
    },

    # ── IP India — Patent Filing Procedure ─────────────────────────────
    {
        "title": "IP India — Patent Application and Filing Procedure",
        "source_url": "https://ipindiaonline.gov.in/epatentfiling/go4ip/login.do",
        "jurisdiction": "india",
        "section_label": "Patent Filing Procedure — Forms and Stages",
        "content": (
            "The official patent filing process in India under the Patents Act, 1970 and Patent Rules, 2003 "
            "comprises several key procedural steps: (1) Prior-Art Search: Conduct a comprehensive prior-art "
            "search on InPASS (search.ipindia.gov.in) and TKDL to ensure novelty and non-obviousness before filing. "
            "(2) Drafting Specification: Prepare a provisional or complete specification (Form 2) detailing the title, "
            "description, abstract, and claims. If a provisional specification is filed, the complete specification "
            "must follow within 12 months. (3) Application Filing: Submit Form 1 (Application for Grant of Patent), "
            "Form 2 (Specification), Form 3 (Statement and undertaking regarding foreign filings), and Form 5 (Declaration "
            "as to inventorship) via the official IP India e-filing portal (ipindiaonline.gov.in) or patent office counters. "
            "(4) Publication: The application is published in the official Patent Office Journal after 18 months from filing "
            "(or expedited early publication via Form 9). (5) Examination: File a Request for Examination (Form 18) within "
            "48 months from the priority or filing date. An examiner issues the First Examination Report (FER). "
            "(6) Response and Hearing: The applicant must overcome any statutory objections within 6 months (extendable by 3 months). "
            "(7) Grant: Upon satisfying statutory requirements, the patent is granted under Section 43 and published in the Journal."
        ),
    },

    # ── Geographical Indications ───────────────────────────────────────
    {
        "title": "Geographical Indications of Goods Act, 1999",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1944",
        "jurisdiction": "india",
        "section_label": "GI Act — Key Provisions for Ayurveda Products",
        "content": (
            "The Geographical Indications of Goods (Registration and Protection) Act, 1999 protects "
            "goods identified as originating from a specific geographical territory where quality, "
            "reputation, or other characteristics are essentially attributable to that origin. Key "
            "provisions: Section 2(1)(e) defines 'geographical indication' broadly to cover natural "
            "goods, agricultural goods, manufactured goods, and handicrafts. Section 11 allows any "
            "association of producers, any organization, or any authority established by law to apply "
            "for GI registration. Section 21 provides protection against unauthorized use. Section 22 "
            "lists permitted GIs (e.g., Darjeeling Tea, Basmati Rice, Kashmir Saffron). GI protection "
            "is relevant to Ayurveda in several ways: (a) Ayurvedic products associated with specific "
            "regions (e.g., Kerala Ayurveda) may qualify for GI protection; (b) Medicinal plants "
            "from specific regions (e.g., Manipuri Black Rice, Assam Lemon) have received GI tags; "
            "(c) GI registration provides collective rights that prevent misuse of regional branding. "
            "India has over 500 registered GIs as of 2024."
        ),
    },
]


def _get_or_create_document(
    conn,
    title: str,
    source_url: str,
    jurisdiction: str,
) -> int:
    """Return the document ID, creating the row if needed."""
    row = conn.execute(
        "SELECT id FROM documents WHERE source_url = ?",
        (source_url,),
    ).fetchone()

    if row:
        return row["id"]

    conn.execute(
        """
        INSERT INTO documents (title, source_url, jurisdiction)
        VALUES (?, ?, ?)
        """,
        (title, source_url, jurisdiction),
    )
    conn.commit()

    return conn.execute(
        "SELECT id FROM documents WHERE source_url = ?",
        (source_url,),
    ).fetchone()["id"]


def _chunk_exists(conn, doc_id: int, section_label: str) -> bool:
    """Check if a chunk with this section_label already exists for the document."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM chunks WHERE document_id = ? AND section_label = ?",
        (doc_id, section_label),
    ).fetchone()
    return row["cnt"] > 0


def _document_has_chunks(conn, doc_id: int) -> bool:
    """Check if a document already has chunks indexed."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM chunks WHERE document_id = ?",
        (doc_id,),
    ).fetchone()
    return row["cnt"] > 0


def seed_embedded_corpus():
    """Insert embedded knowledge chunks into the database."""
    inserted = 0

    with get_connection() as conn:
        for entry in EMBEDDED_CORPUS:
            doc_id = _get_or_create_document(
                conn,
                title=entry["title"],
                source_url=entry["source_url"],
                jurisdiction=entry["jurisdiction"],
            )

            if _chunk_exists(conn, doc_id, entry["section_label"]):
                continue

            conn.execute(
                """
                INSERT INTO chunks (document_id, section_label, content)
                VALUES (?, ?, ?)
                """,
                (doc_id, entry["section_label"], entry["content"]),
            )
            inserted += 1

        conn.commit()

    if inserted:
        logger.info("Seeded %d embedded knowledge chunks", inserted)

    return inserted


def seed_patents_act_pdf():
    """Extract and index the Patents Act PDF if present and not yet indexed."""
    if not PDF_PATH.exists():
        logger.info("Patents Act PDF not found at %s — skipping", PDF_PATH)
        return 0

    try:
        from pdf_chunker import chunk_pdf_file
    except ImportError:
        logger.warning("pdf_chunker not available (pymupdf missing?)")
        return 0

    source_url = (
        "https://ipindia.gov.in/writereaddata/Portal/IPOAct/"
        "1_113_1_The_Patents_Act__1970___incorporating_all_amendments_"
        "till_1-08-2024.pdf"
    )

    with get_connection() as conn:
        doc_id = _get_or_create_document(
            conn,
            title="The Patents Act, 1970 (Full Text — PDF)",
            source_url=f"local://patents_act_pdf#{PDF_PATH.name}",
            jurisdiction="india",
        )

        if _document_has_chunks(conn, doc_id):
            logger.info("Patents Act PDF already indexed")
            return 0

    try:
        chunks = chunk_pdf_file(PDF_PATH)
    except Exception as exc:
        logger.error("Failed to extract Patents Act PDF: %s", exc)
        return 0

    with get_connection() as conn:
        for chunk in chunks:
            conn.execute(
                """
                INSERT INTO chunks (document_id, section_label, content)
                VALUES (?, ?, ?)
                """,
                (doc_id, chunk["section_label"], chunk["content"]),
            )
        conn.commit()

    logger.info(
        "Indexed Patents Act PDF: %d chunks from %s",
        len(chunks), PDF_PATH.name,
    )
    return len(chunks)


def seed_all():
    """Run all corpus seeders and rebuild the FTS5 index."""
    total = 0
    total += seed_embedded_corpus()
    total += seed_patents_act_pdf()

    if total > 0:
        rebuild_fts_index()
        logger.info("FTS5 index rebuilt after seeding %d new chunks", total)

    return total
