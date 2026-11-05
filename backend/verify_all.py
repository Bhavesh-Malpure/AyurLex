import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from main import app, query, stream_query_events
from schemas import QueryRequest

print("=" * 60)
print("AYURLEX END-TO-END RESEARCH-ANSWER AGENT VERIFICATION")
print("=" * 60)

test_cases = [
    {
        "name": "Canonical Example 1: Student Patenting",
        "question": "am student can patent",
        "jurisdiction": "india",
        "expected_substring": "A student can apply for a patent",
    },
    {
        "name": "Canonical Example 2: Patent Filing Process",
        "question": "patent kaise karte hai?",
        "jurisdiction": "india",
        "expected_substring": "first confirm that your invention is new",
    },
    {
        "name": "Canonical Example 3: Vague Patent Discovery",
        "question": "mujhe new patent batao",
        "jurisdiction": "india",
        "expected_substring": "Which technology or ingredient",
    },
    {
        "name": "Canonical Example 4: Ayurvedic Formulation Patentability",
        "question": "Can I patent an Ayurvedic formulation?",
        "jurisdiction": "india",
        "expected_substring": "genuinely new technical feature",
    },
    {
        "name": "Statutory Question: Section 3(p) Traditional Knowledge",
        "question": "Is Ashwagandha extract patentable under Indian Patent Act Section 3(p)?",
        "jurisdiction": "india",
        "expected_substring": "traditional knowledge",
    },
    {
        "name": "International IP: WIPO Nice & Locarno Classifications",
        "question": "What are the Nice and Locarno classifications administered by WIPO?",
        "jurisdiction": "international",
        "expected_substring": "Classification",
    },
    {
        "name": "Unverified / Non-Domain Query: Graceful Abstention",
        "question": "cryptocurrency blockchain mining hash rate algorithms",
        "jurisdiction": "india",
        "expected_substring": "I could not verify a reliable answer from the available official research sources.",
    },
]

passed_count = 0

for idx, tc in enumerate(test_cases, 1):
    print(f"\n[{idx}/{len(test_cases)}] Testing: {tc['name']}")
    print(f"Question: \"{tc['question']}\" ({tc['jurisdiction']})")
    
    req = QueryRequest(
        question=tc["question"],
        jurisdiction=tc["jurisdiction"],
        response_mode="fast",
    )
    res = query(req)
    
    answer_text = res.summary
    is_abstained = res.is_abstained
    sources_count = len(res.retrieval.get("sources", []))
    
    print(f"-> Abstained: {is_abstained}")
    print(f"-> Internal Sources Cached: {sources_count}")
    print(f"-> Answer: {answer_text[:140]}...")
    
    assert tc["expected_substring"].lower() in answer_text.lower(), f"Expected substring '{tc['expected_substring']}' not found in answer!"
    print("-> Result: PASS [OK]")
    passed_count += 1

print("\n" + "=" * 60)
print("TESTING SERVER-SENT EVENTS (SSE) STREAMING")
print("=" * 60)

stream_req = QueryRequest(
    question="am student can patent",
    jurisdiction="india",
    response_mode="ai",
)

events = list(stream_query_events(stream_req))
print(f"Emitted {len(events)} SSE chunks.")
event_types = []
for ev in events:
    for line in ev.split("\n"):
        if line.startswith("event:"):
            event_types.append(line.replace("event:", "").strip())

print(f"Event Types: {event_types}")
assert "status" in event_types, "Missing status event"
assert "fast_answer" in event_types, "Missing fast_answer event"
assert "complete" in event_types, "Missing complete event"
print("Streaming Check: PASS [OK]")

print("\n" + "=" * 60)
print(f"ALL {passed_count} QUERY TESTS & STREAMING CHECKS PASSED SUCCESSFULLY!")
print("=" * 60)

