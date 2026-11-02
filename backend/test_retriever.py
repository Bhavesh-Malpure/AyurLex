"""Quick test of the FTS5 retriever."""
from retriever import search_chunks

queries = [
    ("What is Section 3(p) patent ayurveda traditional knowledge", "india"),
    ("TKDL biopiracy turmeric neem prior art", "india"),
    ("compulsory licensing patents India", "india"),
    ("Nagoya Protocol benefit sharing genetic resources", "international"),
    ("ayurvedic formulation patentability requirements", "india"),
    ("TRIPS article 27 traditional knowledge biodiversity", "international"),
]

for question, juris in queries:
    results = search_chunks(question, juris)
    print(f"\n{'='*70}")
    print(f"Q: {question}")
    print(f"Jurisdiction: {juris} | Results: {len(results)}")
    for r in results[:3]:
        score = r["score"]
        label = r["section_label"]
        snippet = r["content"][:120].replace("\n", " ")
        print(f"  [{score:.2f}] {label}")
        print(f"         {snippet}...")
