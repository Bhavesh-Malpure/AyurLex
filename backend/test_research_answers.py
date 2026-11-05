import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from main import app, query
from schemas import QueryRequest

queries = [
    "am student can patent",
    "patent kaise karte hai?",
    "mujhe new patent batao",
    "Can I patent an Ayurvedic formulation?",
    "xyz random unrelated invalid query",
]

for q in queries:
    req = QueryRequest(question=q, jurisdiction="india", response_mode="fast")
    res = query(req)
    print(f"\n=== QUESTION: {q} ===")
    print(f"Confidence: {res.confidence}")
    print(f"Is Abstained: {res.is_abstained}")
    print(f"Summary: {res.summary}")
    print(f"Sources Count: {len(res.retrieval.get('sources', []))}")
