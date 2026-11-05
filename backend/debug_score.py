"""Debug the smart research score logic."""
from retriever import search_chunks

question = "What is Section 3(p) of the Patents Act?"
results = search_chunks(question, "india")
total = sum(r["score"] for r in results)
print(f"Total relevance score: {total:.2f}")
print(f"Chunks found: {len(results)}")
print(f"Threshold: 1.0")
print(f"Would use corpus: {total >= 1.0}")
print()
for r in results[:5]:
    print(f"  score={r['score']:.2f}  label={r['section_label']}")
