"""Statutory Calculator & Code Interpreter for Indian Patent Rules and Timelines.
Calculates official deadlines, Form filing periods, and Indian Patent Office fees.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

def calculate_patent_deadlines(priority_or_filing_date_str: str) -> Dict[str, Any]:
    """Calculate critical statutory deadlines under the Indian Patents Act, 1970 and Patent Rules, 2003 (as amended).
    Input format: YYYY-MM-DD
    """
    try:
        base_date = datetime.strptime(priority_or_filing_date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return {
            "error": "Invalid date format. Please provide date in YYYY-MM-DD format (e.g. 2024-01-15)."
        }

    # Statutory calculations
    # 1. Complete Specification (Form 2) after Provisional: 12 months (Section 9(1))
    # Approximate 12 months as 365 days / 1 year
    complete_spec_deadline = base_date + timedelta(days=365)
    
    # 2. Publication (Section 11A): Normally 18 months from priority
    publication_expected = base_date + timedelta(days=int(18 * 30.4375))
    
    # 3. Request for Examination (Form 18):
    # Under Patent (Amendment) Rules, 2024: 31 months from priority (earlier 48 months)
    rfe_deadline_2024_rule = base_date + timedelta(days=int(31 * 30.4375))
    rfe_legacy_deadline = base_date + timedelta(days=int(48 * 30.4375))
    
    # 4. PCT National Phase into India (Chapter XXII): 31 months from priority
    pct_national_phase_deadline = base_date + timedelta(days=int(31 * 30.4375))
    
    # 5. International Application submission (Paris Convention): 12 months
    paris_convention_deadline = base_date + timedelta(days=365)

    deadlines: List[Dict[str, str]] = [
        {
            "event": "Complete Specification (Form 2)",
            "deadline": complete_spec_deadline.strftime("%Y-%m-%d"),
            "section_rule": "Section 9(1), Rule 13",
            "description": "Deadline to submit complete specification if provisional application was filed on priority date."
        },
        {
            "event": "International Convention Filing (Paris Convention)",
            "deadline": paris_convention_deadline.strftime("%Y-%m-%d"),
            "section_rule": "Section 135, Paris Convention",
            "description": "Deadline to file convention applications in other Paris Convention member countries claiming Indian priority."
        },
        {
            "event": "Expected Automatic Publication (18 Months)",
            "deadline": publication_expected.strftime("%Y-%m-%d"),
            "section_rule": "Section 11A, Rule 24",
            "description": "Patent application is officially published in Indian Patent Office Journal unless early publication (Form 9) is filed."
        },
        {
            "event": "Request for Examination (Form 18) - 2024 Rules",
            "deadline": rfe_deadline_2024_rule.strftime("%Y-%m-%d"),
            "section_rule": "Section 11B, Rule 24B (Amended 2024)",
            "description": "Mandatory deadline to file Form 18 for applications filed on or after 15th March 2024 (31 months)."
        },
        {
            "event": "Request for Examination (Form 18) - Pre-2024 Rule Reference",
            "deadline": rfe_legacy_deadline.strftime("%Y-%m-%d"),
            "section_rule": "Rule 24B (Historical 48 months)",
            "description": "Applicable for applications filed prior to 15th March 2024 (48 months from priority)."
        },
        {
            "event": "PCT National Phase Entry into India",
            "deadline": pct_national_phase_deadline.strftime("%Y-%m-%d"),
            "section_rule": "Rule 20(4)(i)",
            "description": "Deadline for foreign PCT applications to enter Indian National Phase."
        }
    ]

    return {
        "priority_date": priority_or_filing_date_str,
        "deadlines": deadlines,
        "disclaimer": "Ayurlex provides statutory deadline estimates for research purposes and does not provide legal advice."
    }


def calculate_patent_fees(
    applicant_type: str = "natural_person", # natural_person, startup, small_entity, large_entity
    pages_count: int = 30,
    claims_count: int = 10,
    is_e_filing: bool = True,
    include_early_publication: bool = False,
    include_expedited_exam: bool = False
) -> Dict[str, Any]:
    """Calculate official statutory fees according to First Schedule, Indian Patent Rules (as amended).
    """
    applicant_type = applicant_type.lower().strip()
    is_small_or_startup_or_individual = applicant_type in ["natural_person", "startup", "small_entity", "educational_institution"]

    # Base Application Fee (Form 1)
    if is_small_or_startup_or_individual:
        base_f1 = 1600 if is_e_filing else 1750
        extra_page_fee_per = 160 if is_e_filing else 180
        extra_claim_fee_per = 320 if is_e_filing else 350
        form_9_fee = 2500 if is_e_filing else 2750
        form_18_fee = 4000 if is_e_filing else 4400
        form_18a_fee = 8000 if is_e_filing else 8800
    else: # large entity / others
        base_f1 = 8000 if is_e_filing else 8800
        extra_page_fee_per = 800 if is_e_filing else 880
        extra_claim_fee_per = 1600 if is_e_filing else 1750
        form_9_fee = 12500 if is_e_filing else 13750
        form_18_fee = 20000 if is_e_filing else 22000
        form_18a_fee = 60000 if is_e_filing else 66000

    excess_pages = max(0, pages_count - 30)
    excess_claims = max(0, claims_count - 10)

    fee_excess_pages = excess_pages * extra_page_fee_per
    fee_excess_claims = excess_claims * extra_claim_fee_per

    total_f1_cost = base_f1 + fee_excess_pages + fee_excess_claims

    # Examination
    exam_cost = form_18a_fee if include_expedited_exam else form_18_fee
    early_pub_cost = form_9_fee if include_early_publication else 0

    total_cost = total_f1_cost + exam_cost + early_pub_cost

    breakdown = [
        {"item": "Form 1 (Application Filing Base Fee)", "amount_inr": base_f1},
        {"item": f"Form 2 Extra Pages ({excess_pages} beyond 30)", "amount_inr": fee_excess_pages},
        {"item": f"Form 2 Extra Claims ({excess_claims} beyond 10)", "amount_inr": fee_excess_claims},
        {"item": "Form 18 / 18A (Examination Request)", "amount_inr": exam_cost},
    ]
    if include_early_publication:
        breakdown.append({"item": "Form 9 (Optional Early Publication)", "amount_inr": early_pub_cost})

    return {
        "applicant_type": applicant_type,
        "is_e_filing": is_e_filing,
        "pages_count": pages_count,
        "claims_count": claims_count,
        "total_official_fee_inr": total_cost,
        "fee_breakdown": breakdown,
        "schedule_reference": "First Schedule (Fees), Indian Patent Rules 2003 (amended)",
        "disclaimer": "Ayurlex provides statutory estimates for research purposes and does not provide legal advice."
    }
