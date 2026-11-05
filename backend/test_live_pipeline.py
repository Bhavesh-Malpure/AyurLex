import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

base_url = "http://127.0.0.1:8000"

test_cases = [
    {
        "title": "1. Ashwagandha Extract Section 3(p)",
        "endpoint": "/query/stream",
        "payload": {
            "question": "Is Ashwagandha extract patentable under Indian Patent Act Section 3(p)?",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["excluded", "section 3(p)", "national biodiversity authority", "prior-art"],
    },
    {
        "title": "2. Student Patent Eligibility",
        "endpoint": "/query/stream",
        "payload": {
            "question": "am student can patent",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["student", "first inventor", "college"],
    },
    {
        "title": "3. Patent Filing Process (Hindi / Hinglish)",
        "endpoint": "/query/stream",
        "payload": {
            "question": "patent kaise karte hai?",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["specification", "application", "examination"],
    },
    {
        "title": "4. Patent Discovery Guidance",
        "endpoint": "/query/stream",
        "payload": {
            "question": "mujhe new patent batao",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["technology", "ashwagandha"],
    },
    {
        "title": "5. Rule 158B Classical vs Proprietary",
        "endpoint": "/query/stream",
        "payload": {
            "question": "What is the licensing requirement under Rule 158B for Ayurveda?",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["158b", "license"],
    },
    {
        "title": "6. International WIPO Classifications",
        "endpoint": "/query/stream",
        "payload": {
            "question": "What are the Nice and Locarno classifications administered by WIPO?",
            "jurisdiction": "international",
            "response_mode": "ai",
        },
        "expected_kw": ["locarno", "classification"],
    },
    {
        "title": "7. Live Research Multi-Browser Pipeline (Curcumin / Piperine)",
        "endpoint": "/research/live/stream",
        "payload": {
            "question": "Can a synergistic Curcumin formulation be patented in India?",
            "jurisdiction": "india",
            "response_mode": "ai",
        },
        "expected_kw": ["turmeric", "curcuma", "section 3(p)"],
    },
]

print("====================================================")
print("AYURLEX MULTI-SOURCE & BROWSER RESEARCH PIPELINE TEST")
print("====================================================\n")

all_passed = True

for case in test_cases:
    case_name = case["title"]
    print(f"--> Testing: {case_name}")
    req = urllib.request.Request(
        f"{base_url}{case['endpoint']}",
        data=json.dumps(case["payload"]).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        res = urllib.request.urlopen(req, timeout=15)
        raw_sse = res.read().decode("utf-8")
        elapsed = round((time.time() - t0) * 1000, 2)

        lines = raw_sse.split("\n")
        events = [l[7:].strip() for l in lines if l.startswith("event:")]
        data_lines = [json.loads(l[6:].strip()) for l in lines if l.startswith("data: {")]

        final_answer = ""
        for d in data_lines:
            if "answer" in d:
                final_answer = d["answer"]
            elif "summary" in d and not final_answer:
                final_answer = d["summary"]

        sources_count = len(data_lines[-1].get("sources", [])) if data_lines else 0

        ans_lower = final_answer.lower()
        missing = [kw for kw in case["expected_kw"] if kw not in ans_lower]
        passed = (len(missing) == 0) and (len(final_answer) > 30)

        if not passed:
            all_passed = False
            print(f"    STATUS: FAILED (Missing keywords: {missing})")
            print(f"    Answer: {final_answer[:120]}")
        else:
            print(f"    STATUS: PASSED in {elapsed}ms (Sources: {sources_count})")
            print(f"    Events: {events}")
            print(f"    Answer snippet: {final_answer[:140]}...\n")

    except Exception as e:
        all_passed = False
        print(f"    STATUS: ERROR -> {e}\n")

print("====================================================")
print("OVERALL TEST RESULT:", "ALL PASSED" if all_passed else "SOME FAILED")
print("====================================================")

if not all_passed:
    sys.exit(1)
